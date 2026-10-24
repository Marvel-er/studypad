"""
FastAPI 入口：把解析 → 分析 → 编排 → 渲染串成一条链路。

刻意做成单体 + 同步返回：纯规则链路单篇 2000 词耗时 < 1 秒，
不需要 Celery 那一套。等接入 OCR 与批量 LLM 时再拆异步（见开发文档 4.1）。
"""
from __future__ import annotations

import threading
import time
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from . import (annotator, cards_render, exam_points, library, llm, markup,
               parsers, progress, render, settings, translate, wordlist)
from .levels import LEVELS

ROOT = Path(__file__).resolve().parents[2]
STATIC = Path(__file__).resolve().parents[1] / "static"
SAMPLES = ROOT / "samples"

app = FastAPI(title="英语手账 · StudyPad", version="0.1.0")


# ---------------------------------------------------------------- 元信息

@app.get("/api/levels")
def get_levels() -> dict:
    from . import ocr

    return {
        "levels": [
            {
                "id": lv["id"], "name": lv["name"], "en": lv["en"],
                "vocab_note": lv["vocab_note"], "tagline": lv["tagline"],
                "highlight_per_1000": lv["highlight_per_1000"],
                "circle_per_1000": lv["circle_per_1000"],
                "deep_per_1000": lv["deep_per_1000"],
                # 等级自带的「默认是否显示译文」——前端据此决定勾选框初始状态
                "show_translation": lv["show_translation"],
            }
            for lv in LEVELS
        ],
        "wordlist": {**wordlist.stats(),
                     "general_dict": wordlist.has_general_dict(),
                     "extra_dict": wordlist.has_extra_dict(),
                     "ecdict_dict": wordlist.has_ecdict_dict()},
        "formats": parsers.supported_extensions(),
        "ocr": ocr.engine_info(),
        "exam_points": exam_points.stats(),
    }


@app.get("/api/ocr/status")
def ocr_status() -> dict:
    from . import ocr

    return ocr.engine_info()


@app.get("/api/progress")
def progress_stats() -> dict:
    """进度任务表的状态（排查用：有几个任务在跑、TTL 与容量上限）。"""
    return progress.stats()


@app.get("/api/progress/{job_id}")
def get_progress(job_id: str) -> dict:
    """
    查询一次生成任务的进度。

    前端在发起生成请求的同时带上 `job_id`，并轮询这里；
    主请求照旧一次性返回完整手账，所以**进度是旁路**，不影响原有契约
    （不带 `job_id` 的老请求完全不受影响）。

    未知任务返回 `found=False` 而不是 404：轮询天然存在竞态
    （前端可能在请求线程登记任务之前就打过来，也可能在结束后多打一次），
    用 404 会让浏览器控制台刷满无意义的错误，掩盖真正的问题。
    """
    return progress.snapshot(job_id)


@app.get("/api/translate/status")
def translate_status() -> dict:
    """
    翻译能力状态。

    刻意把「不可用」说得直白：翻译没有规则兜底，如果这里报不可用，
    生成手账时就不会有译文 —— 与其糊一份词对对的假译文，不如明确告知。

    ⚠ 这里报的是**翻译专用模型**（mt_*）的状态，不是手账讲解那个模型。
    两者从 2026-10-15 起分开配置：翻译默认走本机 Ollama 上的 Hy-MT2-1.8B，
    云端 API 只负责生成讲解。用户最常犯的错是「手账讲解通了就以为翻译也通」，
    所以这两个状态必须各自如实汇报。
    """
    saved = settings.load()
    mt_cfg = _resolve_mt_cfg()
    # 讲解模型（手账内容那个）也要解析出来：本地翻译关掉时翻译会退回它，
    # 那种情况下「有没有译文」取决于它 —— 状态里必须算进去。
    main_cfg = _resolve_cfg(saved.get("provider", ""), saved.get("api_key", ""),
                            saved.get("base_url", ""), saved.get("model", ""))
    st = translate.stats()
    enabled = settings._truthy(saved.get("mt_enabled", True))
    st["enabled"] = enabled
    st["fallback"] = settings._truthy(saved.get("mt_fallback", True))
    st["main_model"] = (
        f'{saved.get("provider", "")} / {saved.get("model", "")}'.strip(" /") or ""
    )
    use_mt = enabled and mt_cfg.ready
    if use_mt:
        st["available"] = True
        st["provider"] = mt_cfg.resolved().provider
        st["model"] = mt_cfg.resolved().model
        st["base_url"] = mt_cfg.resolved().base_url
    elif main_cfg.ready:
        # 本地翻译关掉了，但讲解模型还能翻 —— 仍然算「可用」，只是报的是讲解模型。
        # ⚠ 这里以前只看 `mt_cfg.ready`，而它对 localhost 一律 True，
        # 于是关掉本地翻译后状态还在报「已接入 mt_local / hy-mt2:1.8b」，
        # 与同一份响应里的 message（说「已关闭」）自相矛盾。
        st["available"] = True
        st["provider"] = saved.get("provider", "")
        st["model"] = saved.get("model", "")
        st["base_url"] = saved.get("base_url", "")
    else:
        st["available"] = False
        st["provider"] = st["model"] = st["base_url"] = ""
    st["local"] = _is_local(st["base_url"])
    if not enabled:
        st["message"] = (
            "「翻译交给这个模型」已关闭：翻译改用上面的讲解模型 %s（更慢，且按 token 计费）"
            % st["main_model"]
            if main_cfg.ready else
            "翻译不可用：本地翻译模型已关闭，且讲解模型未配置。翻译没有规则兜底，"
            "所以不会有译文 —— 请打开「翻译交给这个模型」，或配上云端 API Key。"
        )
    elif not mt_cfg.ready:
        st["message"] = (
            "翻译模型未就绪：默认用的是本机 Ollama 上的 hy-mt2:1.8b，"
            "请确认 Ollama 正在运行且已装该模型，"
            "或在设置页把「翻译模型」指向别的 OpenAI 兼容端点。"
            + ("（讲解模型可用，翻译会退回它）" if main_cfg.ready else "")
        )
    elif st["local"]:
        st["message"] = ("已接入 %s / %s，翻译由它完成（本地模型，不消耗云端额度）"
                         % (st["provider"], st["model"]))
    else:
        st["message"] = "已接入 %s / %s，翻译由它完成" % (st["provider"], st["model"])
    return st


@app.delete("/api/translate/cache")
def translate_cache_clear() -> dict:
    """清空译文缓存（译文按原文哈希缓存，换等级重标注时会自动复用）。"""
    n = translate.clear_cache()
    return {"removed": n, **translate.stats()}


@app.get("/api/llm/presets")
def llm_presets() -> dict:
    """
    两套预设一起给前端：`presets` = 手账讲解模型，`mt_presets` = 翻译专用模型。

    分成两个列表而不是一个，是因为它们的作用不可互换 ——
    把手账讲解模型填成 1.8B 的翻译模型会得到满篇机翻味的讲解，
    反过来把翻译填成 deepseek-chat 则等于这次的优化白做了。
    """
    return {
        "presets": [
            {"id": k, "label": v["label"], "base_url": v["base_url"], "model": v["model"],
             "need_key": k not in ("ollama",)}
            for k, v in llm.PRESETS.items()
        ],
        "mt_presets": [
            {"id": k, "label": v["label"], "base_url": v["base_url"], "model": v["model"],
             "need_key": k not in ("ollama", "mt_local", "mt_own")}
            for k, v in llm.MT_PRESETS.items()
        ],
        "mt_default": {"id": "mt_local", **llm.MT_DEFAULT},
    }


def _is_local(base_url: str) -> bool:
    """端点是不是本机（本机端点不需要 Key，且「翻译成本」按 0 算）。"""
    b = (base_url or "").lower()
    return "localhost" in b or "127.0.0.1" in b or "0.0.0.0" in b or "[::1]" in b


# 翻译模型探活的结果缓存（见 _probe_mt 的说明）。
_MT_PROBE_LOCK = threading.Lock()
_MT_PROBE_TTL_OK = 60.0
_MT_PROBE_TTL_FAIL = 10.0
_mt_probe: dict[tuple[str, str], tuple[float, bool, str]] = {}


def _resolve_mt_cfg(provider: str = "", api_key: str = "", base_url: str = "",
                    model: str = "") -> llm.LLMConfig:
    """
    解析**翻译专用**模型的配置。

    优先级：请求里显式带的 mt_* 字段 → 本机已保存的 mt_* → `llm.MT_DEFAULT`
    （即本机 Ollama 上的 `hy-mt2:1.8b`）。

    与 `_resolve_cfg` 的关键差别：**这里不偷偷回退到主模型**。
    翻译要不要退回云端是一个有代价的决定（会把好不容易省下来的额度又花回去），
    所以它由 `_translation_cfg` 按 `mt_enabled` / `mt_fallback` 显式做，并写进给用户看的说明里；
    藏在配置解析里做的话，用户会以为翻译还是本地的。
    """
    provider = (provider or "").strip()
    api_key = (api_key or "").strip()
    base_url = (base_url or "").strip()
    model = (model or "").strip()

    saved = settings.load()
    d = llm.MT_DEFAULT
    # 优先级：请求字段（= 界面上你此刻看到的值）→ 已保存配置 → 预设 → 默认值。
    # 「界面上看到什么就用什么」这条最重要：两套模型的作用不可互换，
    # 悄悄用另一套会让人完全摸不着头脑（表现为「明明填了 7B，跑的还是 1.8B」）。
    # 前端在切换服务商下拉时会自动把该预设的 Base URL / 模型名填进输入框，
    # 所以这里不需要再猜用户换服务商之后想要哪个模型名。
    provider = provider or saved.get("mt_provider") or "mt_local"
    p = llm.MT_PRESETS.get(provider) or {}
    base_url = base_url or saved.get("mt_base_url") or p.get("base_url") or d["base_url"]
    model = model or saved.get("mt_model") or p.get("model") or d["model"]
    # Key：**用户显式存过就照发**，不因为端点是本机就悄悄丢掉。
    # 原来这里有个 `and not _is_local(base_url)` 的门，本意是「本机 Ollama 不需要 Key」，
    # 但它把「用户明确填了一个 Key」也一起吞了 —— llama.cpp / LM Studio / vLLM
    # 都能配成要求 token 的本机服务，配了却不发就是「填了没反应」。
    # 注意方向：只有**空** Key 才不发，那是默认状态（本机端点留空即可）。
    api_key = api_key or saved.get("mt_api_key") or ""
    return llm.LLMConfig(provider=provider, api_key=api_key,
                         base_url=base_url, model=model)


def _probe_mt(mt_cfg: llm.LLMConfig) -> tuple[bool, str]:
    """
    探一次翻译模型能不能用，**结果带 TTL 缓存**。

    为什么要缓存：探活是给每次生成多加一个 1 token 请求。本机模型一次几十毫秒不算什么，
    但在「连续生成几篇」时这笔开销会重复付；而「模型在不在」这件事在这几十秒内不会变。
    成功结果缓存 60 秒；**失败只缓存 10 秒** —— Ollama 刚起来就得能马上被发现，
    不能让用户对着「翻译不可用」等满一分钟。

    缓存键带上 base_url + model：用户换了模型/端点必须立刻重探，不能吃旧结果。
    """
    key = (mt_cfg.resolved().base_url, mt_cfg.resolved().model)
    now = time.time()
    with _MT_PROBE_LOCK:
        hit = _mt_probe.get(key)
        if hit:
            ts, ok, msg = hit
            if now - ts < (_MT_PROBE_TTL_OK if ok else _MT_PROBE_TTL_FAIL):
                return ok, msg
    ok, msg = llm.test_connection(mt_cfg)
    with _MT_PROBE_LOCK:
        _mt_probe[key] = (now, ok, msg)
    return ok, msg


def _translation_cfg(mt_cfg: llm.LLMConfig, main_cfg: llm.LLMConfig | None,
                     enabled: bool, fallback: bool) -> tuple[llm.LLMConfig | None, str]:
    """
    决定本次翻译真正用哪个模型，返回 `(配置, 给用户看的说明)`。

    为什么这里要**真的探一次连接**而不只看 `cfg.ready`：
    `ready` 对 localhost 端点一律放行（本地端点不需要 Key），所以
    **Ollama 没启动时它照样是 ready**。若不探测，整篇翻译会先按 4 路并发发出去、
    每路各自等到超时（90 秒）才失败，用户看到的是「手账卡住两分钟、最后没有译文」——
    这是本项目最不该有的体验。一次 1 token 的探活只要几十毫秒，换掉这个坑很值。

    说明文案分四种，都要说清「为什么」：
      · 本地模型正常        → 空串（不打扰用户）
      · 关掉了本地翻译      → 明说本次用主模型，费用算在主模型上
      · 本地不可用、已回退  → 明说退回了主模型（意思是：这次没省到钱，且更慢）
      · 两边都不可用        → 翻译直接不可用（不做规则兜底）
    """
    if not enabled:
        if main_cfg and main_cfg.ready:
            return main_cfg, "翻译走主模型（设置里已关闭本地翻译模型，本次翻译会消耗主模型额度）"
        return None, ("翻译不可用：本地翻译模型已关闭，且讲解模型未配置"
                      "（翻译没有规则兜底，不糊假译文 —— 请打开「翻译交给这个模型」"
                      "或配上云端 API Key）")

    if not (mt_cfg and mt_cfg.ready):
        if fallback and main_cfg and main_cfg.ready:
            return main_cfg, "本地翻译模型未配置，本次退回主模型翻译（更慢、且消耗额度）"
        return None, ("翻译不可用：翻译模型未配置。默认用本机 Ollama 的 hy-mt2:1.8b，"
                      "请确认 Ollama 在运行且已装该模型")

    ok, msg = _probe_mt(mt_cfg)
    if ok:
        return mt_cfg, ""
    if fallback and main_cfg and main_cfg.ready:
        return main_cfg, (f"本地翻译模型连不上（{msg[:60]}），本次已退回主模型翻译 —— "
                          "本地模型不消耗额度，建议确认 Ollama 是否在运行")
    return None, f"翻译不可用：连不上翻译模型（{msg[:80]}）"


def _needs_saved_key(provider: str, api_key: str, base_url: str) -> bool:
    """
    本次调用是否应该改用「本机已保存的 Key」。

    三种情况不该用：请求里本来带了 Key、本地模型（Ollama）不需要 Key、
    Base URL 指向本机。少判一条都会踩坑 ——
    比如用户切到 Ollama 却被回退成已保存的 DeepSeek 配置。
    """
    if api_key:
        return False
    if (provider or "").strip() == "ollama":
        return False
    if "localhost" in (base_url or "") or "127.0.0.1" in (base_url or ""):
        return False
    return True


def _resolve_cfg(provider: str, api_key: str, base_url: str, model: str) -> llm.LLMConfig:
    """
    解析出本次调用要用的模型配置。

    **「配一次就好」的关键在这里**：请求里没带 Key 时，回退到本地已保存的配置。
    前端因此不必把 Key 存进 localStorage，也不必在每次生成时回传它 ——
    浏览器全程只拿到 `sk-******3f9a` 这样的掩码。
    """
    provider = (provider or "deepseek").strip()
    api_key = (api_key or "").strip()
    base_url = (base_url or "").strip()
    model = (model or "").strip()

    saved = settings.load()
    if _needs_saved_key(provider, api_key, base_url) and saved.get("api_key"):
        return llm.LLMConfig(
            provider=saved.get("provider") or provider,
            api_key=saved["api_key"],
            base_url=saved.get("base_url") or base_url,
            model=saved.get("model") or model,
        )
    return llm.LLMConfig(provider=provider, api_key=api_key,
                         base_url=base_url, model=model)


@app.get("/api/llm/config")
def llm_config_get() -> dict:
    """读取已保存的模型配置（脱敏，不含完整 Key）。"""
    return settings.public()


@app.post("/api/llm/config")
def llm_config_save(payload: dict) -> dict:
    """
    保存模型配置。`api_key` 传空表示「保持原样」——
    前端拿不到已存的 Key，无法回传原值，所以不能把空值当清空。
    这条规则对 `mt_api_key` 同样成立。

    一次可以只改一套配置：`payload` 里没出现的键不会被碰
    （settings.save 只处理 ALLOWED 里**实际存在**的键）。
    """
    try:
        settings.save({
            k: payload[k] for k in ALLOWED_PAYLOAD_KEYS if k in payload
        })
    except RuntimeError as e:
        raise HTTPException(500, str(e)) from e
    return settings.public()


# 允许从前端保存的键 —— 与 settings.ALLOWED 完全一致。
# 用白名单逐键取值而不是逐个手写，是为了避免「加了新配置项但忘了在这里接上」：
# 那种漏接不会报错，只会表现为「保存成功、刷新后又变回去了」，极难定位。
ALLOWED_PAYLOAD_KEYS = settings.ALLOWED


@app.delete("/api/llm/config")
def llm_config_clear() -> dict:
    try:
        settings.clear()
    except RuntimeError as e:
        raise HTTPException(500, str(e)) from e
    return settings.public()


@app.post("/api/llm/test")
def llm_test(payload: dict) -> dict:
    """
    测试连通性。

    刻意用同步 `def` 而不是 `async def`：`llm.test_connection` 是**同步阻塞**的
    httpx 调用，最长会等 90 秒。写成 `async def` 的话 FastAPI 会把它直接跑在事件循环上，
    这 90 秒里**整个服务一个请求都处理不了**（连首页都打不开）——
    用户在自己的页面上点一次「测试连接」就能把服务冻住，而日志上看不出任何异常。
    改成 `def` 后 Starlette 会把它丢进线程池，事件循环保持可用。

    `target="mt"` 时测的是**翻译专用模型**（默认本机 Ollama 的 hy-mt2:1.8b）：
    两套配置各有各的「测试连接」按钮，混用会让人以为翻译也通了。

    ⚠ 翻译那一支读的是 **`mt_` 前缀**的字段（`mt_base_url` 等）——
    前端「测试翻译模型」按钮就是把 `collectMt()` 原样发过来的。
    早先这里错读了无前缀的 `base_url`：用户填了一个错的翻译端点、点测试，
    后端却拿「已保存的默认端点」去测并回「连接成功」，
    于是这个按钮永远说通 —— 比不提供按钮更糟。
    """
    if (payload.get("target") or "") == "mt":
        # 前缀字段优先，同时容忍无前缀写法（自检脚本/手写 curl 更顺手）
        cfg = _resolve_mt_cfg(
            payload.get("mt_provider") or payload.get("provider", ""),
            payload.get("mt_api_key") or payload.get("api_key", ""),
            payload.get("mt_base_url") or payload.get("base_url", ""),
            payload.get("mt_model") or payload.get("model", ""))
    else:
        cfg = _resolve_cfg(
            payload.get("provider", ""),
            payload.get("api_key", ""),
            payload.get("base_url", ""),
            payload.get("model", ""),
        )
    ok, msg = llm.test_connection(cfg)
    return {
        "ok": ok, "message": msg,
        "target": payload.get("target") or "main",
        "provider": cfg.resolved().provider,
        "model": cfg.resolved().model,
        "base_url": cfg.resolved().base_url,
        "local": _is_local(cfg.resolved().base_url),
    }


# ---------------------------------------------------------------- 考点知识库

@app.get("/api/exam-points")
def exam_points_index() -> dict:
    """六档考点的索引（不含正文）+ 来源总表。"""
    return {
        "levels": exam_points.summary(),
        "stats": exam_points.stats(),
        "sources": exam_points.SOURCES,
        "oss": exam_points.OSS_SOURCES,
    }


@app.get("/api/exam-points/{level_id}")
def exam_points_detail(level_id: str) -> dict:
    """
    某档的完整考点：词汇 / 语法 / 题型 / 高频考点 / 考查重点。

    `sources` 是展开后的完整来源条目（带 tier 与链接）——
    前端要能把「依据」直接摆给用户看，这是这一层存在的意义。
    """
    point = exam_points.get(level_id)
    if not point:
        raise HTTPException(404, f"未知阶段：{level_id}，可选 {exam_points.ORDER}")
    return {
        "point": point,
        "sources": exam_points.sources_of(level_id),
        "sections": ["profile", "vocabulary", "grammar",
                     "question_types", "high_frequency", "focus"],
    }


@app.get("/api/exam-points/{level_id}/{section}")
def exam_points_section(level_id: str, section: str) -> dict:
    """只取某一维度，前端分 Tab 拉取时用。"""
    data = exam_points.section(level_id, section)
    if data is None:
        raise HTTPException(404, f"{level_id} 没有 {section} 维度")
    return {
        "level_id": level_id,
        "section": section,
        "data": data,
        "sources": exam_points.sources_of(level_id),
    }


_BRIEF_SYS = """You are a senior English exam coach writing a SHORT briefing for a Chinese
student about what the exam at their target level actually tests.

You will receive a structured exam-point digest that has already been verified against
official sources. Rules:
1. Ground EVERY claim in the digest. If the digest does not say it, do not write it.
2. Never invent numbers (question counts, scores, durations, word counts).
3. When you cite a figure, keep the digest's wording/scope (e.g. "约 4500 词").
4. Output Chinese, 4-6 short bullet-style paragraphs, each starting with a bold topic.
5. End with a one-line "依据" note naming the source publishers given in the digest.

Return STRICT JSON: {"brief":"<markdown text>"}
"""


def _rule_brief(level_id: str) -> str:
    """没配大模型时的确定性兜底 —— 内容直接来自知识库，绝不编造。"""
    p = exam_points.require(level_id)
    lines = [f"**{p['label']}**  \n"]
    prof = p.get("profile", {})
    if prof:
        lines.append(f"- **卷面**：{prof.get('score_scale', '')}"
                     f"｜{prof.get('duration', '')}｜{prof.get('paper_count', '')}")
    v = p.get("vocabulary", {})
    if v:
        lines.append(f"- **词汇**：目标约 {v.get('target')} 词。{v.get('basis', '')}")
    if p.get("grammar", {}).get("items"):
        names = "、".join(g["name"] for g in p["grammar"]["items"][:8])
        lines.append(f"- **重点语法**：{names}")
    if p.get("question_types", {}).get("items"):
        cur = [q for q in p["question_types"]["items"] if not q.get("effective_until")]
        seg = "；".join(f"{q['section']} {q.get('items', '')}（{q.get('score', '')}）"
                        for q in cur[:6])
        lines.append(f"- **题型分布**：{seg}")
    for t in p.get("high_frequency", [])[:3]:
        lines.append(f"- **高频考点·{t['topic']}**：{'、'.join(t['points'][:5])}")
    for f in p.get("focus", [])[:3]:
        lines.append(f"- **考查重点**：{f['title']} —— {f['detail']}")
    pubs = "、".join(sorted({s["publisher"] for s in exam_points.sources_of(level_id)}))
    lines.append(f"\n**依据**：{pubs}")
    return "\n".join(lines)


@app.post("/api/exam-points/{level_id}/brief")
def exam_points_brief(level_id: str, payload: dict | None = None) -> dict:
    """
    生成一段「这个阶段到底考什么」的简报。

    关键设计：**知识库是事实来源，大模型只是转述者**。
    未配模型或调用失败时退回 `_rule_brief()`，输出内容仍完全来自知识库 ——
    这样「有据可查」这件事不依赖模型运气。
    """
    point = exam_points.get(level_id)
    if not point:
        raise HTTPException(404, f"未知阶段：{level_id}")
    payload = payload or {}

    cfg = _resolve_cfg(payload.get("llm_provider", ""), payload.get("llm_api_key", ""),
                       payload.get("llm_base_url", ""), payload.get("llm_model", ""))
    if not (payload.get("use_llm", True) and cfg.ready):
        return {"brief": _rule_brief(level_id), "mode": "rule",
                "sources": exam_points.sources_of(level_id)}

    digest = exam_points.prompt_context(level_id)
    try:
        out = llm.chat(cfg, [
            {"role": "system", "content": _BRIEF_SYS},
            {"role": "user", "content": digest},
        ], max_tokens=1200)
        brief = (llm.parse_json(out) or {}).get("brief", "")
        if not brief.strip():
            raise llm.LLMError("模型返回空内容")
        return {"brief": brief, "mode": "llm",
                "model": cfg.resolved().model,
                "sources": exam_points.sources_of(level_id)}
    except Exception as e:  # noqa: BLE001
        return {"brief": _rule_brief(level_id), "mode": "rule",
                "note": f"大模型不可用，已退回知识库直出（{str(e)[:80]}）",
                "sources": exam_points.sources_of(level_id)}


# ---------------------------------------------------------------- 核心链路

def _autosave_cfg(provider: str, api_key: str, base_url: str, model: str,
                  enabled: bool) -> None:
    """
    用户一旦**真的把模型跑起来**（而不是只点开面板看看），就把配置落盘。

    这里有个容易写错的点：如果本次用的是「已保存的配置」（请求没带 Key），
    那请求里的 provider/base_url/model 未必反映用户意图
    （`analyze` 的表单字段有 `deepseek` 这种默认值），
    直接写回会把用户存的 `qwen` 覆盖成 `deepseek`。所以这种情况下只更新开关。

    只管**手账讲解模型**。翻译模型的回写走 `_autosave_mt_cfg`，理由见那个函数。
    """
    api_key = (api_key or "").strip()
    if _needs_saved_key(provider, api_key, base_url) and settings.load().get("api_key"):
        # 本次用的就是已存配置，请求里的 provider/base_url/model 未必反映用户意图
        # （`analyze` 的表单字段带 `deepseek` 这种默认值），写回去会把用户的配置改坏
        patch: dict = {"enabled": bool(enabled)}
    else:
        patch = {"provider": provider, "base_url": base_url,
                 "model": model, "api_key": api_key, "enabled": bool(enabled)}
    try:
        settings.save(patch)
    except RuntimeError:
        pass          # 配置存不下不该让本次生成失败


def _autosave_mt_cfg(mt: dict | None) -> None:
    """
    把**翻译模型**的配置落盘。

    为什么不复用 `_autosave_cfg` 的守卫（它要求 `cfg.ready`，即云端模型可用）：
    翻译默认走本机 Ollama，**根本不需要云端 Key**。
    挂在那个守卫上，等于「只开翻译、没配云端模型」的用户每次填完都被丢掉 ——
    表现是「保存成功，刷新后又变回默认」，而且完全不会报错。

    写入规则与 settings 一致：只有请求里**真的带了值**才写。
    没填=空串只代表「沿用已存配置/默认值」，不代表用户想清空。
    """
    if not mt:
        return
    patch: dict = {}
    for k in ("mt_provider", "mt_base_url", "mt_model", "mt_api_key",
              "mt_enabled", "mt_fallback"):
        if k not in mt:
            continue
        v = mt[k]
        if k == "mt_api_key":
            if str(v or "").strip():          # 空 = 保持原样
                patch[k] = str(v).strip()
        elif k in ("mt_enabled", "mt_fallback"):
            patch[k] = v                       # 真假值交给 settings.save 统一解析
        elif str(v or "").strip():
            patch[k] = str(v).strip()
    if not patch:
        return
    try:
        settings.save(patch)
    except RuntimeError:
        pass


def _run_pipeline(blocks: list[dict], level_id: str, title: str,
                  cfg: llm.LLMConfig | None, use_llm: bool,
                  want_translate: bool = False,
                  trans_mode: str = "sentence",
                  job: str = "",
                  save: bool = True,
                  tcfg: llm.LLMConfig | None = None,
                  tnote: str = "") -> dict:
    """
    标注 →（可选）大模型增强 →（可选）中文译文 → 排版。

    两个模型配置是**刻意分开**的：
      · `cfg`  —— 生成手账内容（语法讲解重写、考点 brief），走云端 API；
      · `tcfg` —— **只做翻译**，默认是本机 Ollama 上的 Hy-MT2-1.8B。
    翻译是逐句转写，一篇 20 页的 PDF 就是几百句，用它去占云端模型的输出预算
    既慢又贵（云端额度要留给真正需要语言能力的讲解）。所以这里把两件事彻底拆开：
    **翻译只认 `tcfg`，讲解只认 `cfg`，互不兜底。**

    `tcfg` 由接口层用 `_translation_cfg` 一次性解析好再传进来 ——
    不在本函数里解析是为了**只探一次活**：`_begin_job` 排进度计划时也需要知道
    翻译到底会不会跑、跑的是本地还是云端，两处各探一次等于每次生成多花一次往返。

    `tnote` 是「本次翻译为什么用这个模型」的说明（换过模型 / 不可用）；
    为空表示按默认走本地模型、无需提示。

    `job` 是进度任务号：给了就把每个阶段的进展上报，前端据此画进度条。
    上报全部是内存操作，且内部吞异常，不会影响出稿。
    """
    progress.at(job, "annotate")
    parsed = annotator.analyze_document(
        blocks, level_id,
        on_progress=lambda d, t: progress.sub(job, d, t,
                                              f"已处理 {d}/{t} 个区块"))

    notes: list[str] = []
    llm_note = "未启用大模型，全部由本地规则引擎标注"
    if use_llm and cfg and cfg.ready:
        try:
            progress.at(job, "enrich")
            n = _enrich_with_llm(parsed, level_id, cfg)
            llm_note = f"已接入 {cfg.resolved().provider} / {cfg.resolved().model}，增强 {n} 处讲解"
        except Exception as e:  # noqa: BLE001
            llm_note = f"大模型调用失败，已自动降级为纯规则标注（{str(e)[:80]}）"

    # --- 中文译文：必须走模型，没有规则兜底 ---
    #
    # ⚠ 这里用的是 `mt_cfg`（翻译专用模型），**不是** `cfg`（手账讲解模型）。
    # 上一次改造（2026-10-15）的核心就是把这两件事拆开：
    # 翻译逐句转写、量大且不需要智能，交给本机 Hy-MT2-1.8B；
    # 云端额度只花在真正需要语言能力的讲解重写上。
    translations: dict = {}
    mode = "off"
    mt_used = ""
    if want_translate:
        if tnote:
            notes.append(tnote)
        if tcfg is not None:
            try:
                progress.at(job, "translate")
                tr = translate.translate_blocks(
                    blocks, tcfg,
                    on_progress=lambda d, t, note: progress.sub(job, d, t, note))
                translations = tr["blocks"]
                mt_used = f"{tcfg.resolved().provider} / {tcfg.resolved().model}"
                if translations:
                    mode = "paragraph" if trans_mode == "paragraph" else "sentence"
                    bits = [f"中文译文 {tr['done']}/{tr['total']} 段"]
                    if not tnote:      # 已经说明过换过模型的话就不再重复报模型名
                        bits.append(f"由 {tcfg.resolved().model} 翻译")
                    if tr["cache_hits"]:
                        bits.append(f"复用缓存 {tr['cache_hits']} 句")
                    if tr["skipped"]:
                        bits.append(f"{tr['skipped']} 段未译")
                    if tr["truncated"]:
                        bits.append(f"原文超长，仅翻译前约 {translate.MAX_CHARS} 字符")
                    if tr["errors"]:
                        bits.append(f"{len(tr['errors'])} 处对齐失败已跳过")
                    notes.append("，".join(bits))
                else:
                    # 一段都没成也要说清是哪一种「没有」：
                    # 「无可用段落」和「模型对不齐」对用户是两件完全不同的事。
                    if tr["errors"]:
                        notes.append(f"未能生成中文译文：{len(tr['errors'])} 处对齐失败，"
                                     "为避免译文挂错句子已整段跳过")
                    elif tr["truncated"]:
                        notes.append("未能生成中文译文：原文超出翻译长度上限")
                    else:
                        notes.append("未能生成中文译文（无可用段落）")
            except Exception as e:  # noqa: BLE001
                notes.append(f"中文译文生成失败，已跳过：{str(e)[:80]}")
        # tcfg is None 时不做任何兜底：翻译没有规则版本，
        # 词对词拼接读起来是乱码，比不给译文更糟（原因已由 tnote 说明）。

    progress.at(job, "render")
    hb = markup.build(parsed, level_id)
    hb["title"] = title
    hb["llm_note"] = llm_note
    hb["translations"] = translations
    hb["trans_mode"] = mode
    hb["trans_note"] = " · ".join(notes)
    # 机器可读的「谁干了什么」：手账讲解模型 vs 翻译模型。
    # 有了这两个字段，自检与前端都不必再去解析中文说明文案，
    # 也能直接断言「翻译确实没走云端」——这正是本次改造要保证的事。
    hb["llm_model"] = (f"{cfg.resolved().provider} / {cfg.resolved().model}"
                       if (use_llm and cfg and cfg.ready and not llm_note.startswith("大模型调用失败"))
                       else "")
    hb["mt_model"] = mt_used
    hb["html"] = render.render_handbook(hb, title)

    # --- 自动存进知识库 ---
    # 放在最后：手账已经渲染好了，存不进去也**不该让这一篇出不来**。
    # 但也不能静默吞掉 —— 用户以为存上了、结果重启就没了，
    # 下次要找「上周那篇」时才会发现。所以失败要写进 note 一并显示。
    #
    # `save=False` 用于自检：写盘位置是**服务端进程**的 `~/.studypad/library`，
    # 子进程改自己的环境变量毫无用处 —— 于是每个跑生成链路的自检
    # 都会往用户真实知识库里灌一篇 `api-check`/`live-check` 垃圾手账
    # （实测一次全量回归就灌了 9 篇）。关掉它是唯一干净的做法。
    if not save:
        return hb
    try:
        saved = library.save_handbook(hb)
        hb["library"] = saved
        c = saved.get("cards") or {}
        hb["trans_note"] = (
            hb["trans_note"] + " · " if hb["trans_note"] else ""
        ) + (f"已存入知识库（生词本 {c.get('words', 0)} · "
             f"句型本 {c.get('patterns', 0)} · 语法本 {c.get('grammar', 0)}）")
    except (RuntimeError, ValueError) as e:
        hb["library"] = {"error": str(e)}
        hb["trans_note"] = (
            hb["trans_note"] + " · " if hb["trans_note"] else ""
        ) + f"未能存入知识库：{str(e)[:120]}（手账本身不受影响，可手动下载）"
    return hb


# 这些格式有可能走 OCR —— OCR 是秒级/页的重活，进度计划要据此给解析阶段加权
_OCR_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff", ".pdf"}


def _begin_job(job_id: str, use_llm: bool, want_translate: bool,
               cfg: llm.LLMConfig | None, ocr_hint: bool,
               tcfg: llm.LLMConfig | None = None) -> None:
    """
    登记进度任务并排好阶段计划。

    只把**真的会跑**的阶段算进去（模型没配好就不该有「等模型」那一段），
    否则进度条会为一段根本不存在的工作空转，反而更像卡住。

    ⚠ 「翻译会不会跑」看的是 `tcfg`（翻译模型），不是 `cfg`（讲解模型）——
    这两个自 2026-10-15 起是分开配的，用 `cfg.ready` 判断翻译阶段
    会出现「进度条等着翻译、但翻译根本不会跑」的错位。
    """
    progress.begin(job_id, progress.plan(
        use_llm=bool(use_llm and cfg and cfg.ready),
        translate=bool(want_translate and tcfg is not None),
        ocr_hint=ocr_hint,
        translate_local=bool(tcfg is not None and _is_local(tcfg.resolved().base_url)),
    ))
    progress.at(job_id, "parse")


@app.post("/api/analyze")
def analyze(
    file: UploadFile = File(...),
    level_id: str = Form("cet4"),
    use_llm: bool = Form(False),
    # 注意：这个参数名会遮蔽同名的 translate 模块 —— 本函数内不要再用 translate.xxx
    translate: bool = Form(False),
    trans_mode: str = Form("sentence"),
    llm_provider: str = Form("deepseek"),
    llm_api_key: str = Form(""),
    llm_base_url: str = Form(""),
    llm_model: str = Form(""),
    # 翻译专用模型（与上面的手账讲解模型是两套配置）。
    # 留空 = 沿用已保存的配置 / 默认值（本机 Ollama 的 hy-mt2:1.8b）。
    mt_provider: str = Form(""),
    mt_api_key: str = Form(""),
    mt_base_url: str = Form(""),
    mt_model: str = Form(""),
    job_id: str = Form(""),
    # 自检专用：关掉「自动存进知识库」。
    # **必须显式声明**，不能靠子进程设环境变量 —— 库目录是服务端进程
    # 读 `STUDYPAD_HOME` 决定的，自检子进程改了对自己没影响，
    # 于是每跑一次生成链路的自检就往用户真实知识库灌一篇垃圾手账。
    no_save: bool = Form(False),
) -> JSONResponse:
    """
    上传文件 → 解析 → 标注 →（可选）译文 → 渲染手账。

    同步 `def`（不是 `async def`）：这条链路里全是阻塞操作 ——
    解析、OCR 推理、词法分析都是 CPU 密集；若开了大模型还要等最长 90 秒的网络往返。
    写成 `async def` 会把这些直接压到事件循环上，一次上传就能让整个服务失去响应。
    交给线程池后，慢请求只占用它自己那一个线程。

    `job_id` 可选：带了就上报进度供前端轮询，接口的返回内容不变。
    """
    # 同步端点里不能 await；UploadFile.file 就是底层的 SpooledTemporaryFile
    data = file.file.read()
    filename = file.filename or "untitled.txt"
    ext = Path(filename).suffix.lower()
    # 配置解析提前到这里：进度计划要先知道「会不会真的去等模型」
    cfg = _resolve_cfg(llm_provider, llm_api_key, llm_base_url, llm_model)
    mt_cfg = _resolve_mt_cfg(mt_provider, mt_api_key, mt_base_url, mt_model)
    # 翻译用的配置只解析一次（内部含一次 1 token 探活），
    # 进度计划与真正的翻译共用它，避免每次生成多花一次往返。
    saved_mt = settings.load()
    tcfg, tnote = (_translation_cfg(
        mt_cfg, cfg,
        bool(saved_mt.get("mt_enabled", True)),
        bool(saved_mt.get("mt_fallback", True))) if translate else (None, ""))
    _begin_job(job_id, use_llm, translate, cfg, ocr_hint=(ext in _OCR_EXTS), tcfg=tcfg)

    try:
        if not data:
            raise HTTPException(400, "文件为空")
        allowed = set(parsers.supported_extensions())
        if ext not in allowed:
            raise HTTPException(400, f"暂不支持 {ext}，可用格式：{' / '.join(sorted(allowed))}")

        try:
            blocks, info = parsers.parse(
                filename, data,
                on_progress=lambda d, t, note: progress.sub(job_id, d, t, note))
        except Exception as e:  # noqa: BLE001
            raise HTTPException(422, f"解析失败：{e}") from e

        if not blocks:
            raise HTTPException(422, "没有解析出任何文本内容（可能是扫描件，需要 OCR）")

        if (use_llm or translate) and cfg.ready:
            # `enabled` 只跟「LLM 讲解增强」走：用户可能只是想翻译，
            # 顺手把 enabled 也置真的话，下次打开会发现讲解增强被悄悄打开了。
            _autosave_cfg(llm_provider, llm_api_key, llm_base_url, llm_model, use_llm)
        # 翻译模型的配置**独立回写**（不受上面 cfg.ready 的守卫约束）：
        # 翻译走本机模型、不需要云端 Key，用讲解模型的守卫会把只翻译不讲解的配置丢掉。
        _autosave_mt_cfg({"mt_provider": mt_provider, "mt_base_url": mt_base_url,
                          "mt_model": mt_model, "mt_api_key": mt_api_key})
        title = Path(filename).stem
        hb = _run_pipeline([b.as_dict() for b in blocks], level_id, title, cfg,
                           use_llm, translate, trans_mode, job_id,
                           save=not no_save, tcfg=tcfg, tnote=tnote)
        hb["parse_info"] = info
        progress.done(job_id, "手账已生成")
        return JSONResponse(hb)
    except HTTPException as e:
        # 让前端立刻停止等待，并把真正的原因显示出来（而不是让进度条空转到超时）
        progress.fail(job_id, str(e.detail))
        raise
    except Exception as e:  # noqa: BLE001
        progress.fail(job_id, f"{type(e).__name__}: {str(e)[:160]}")
        raise


@app.post("/api/analyze-text")
def analyze_text(payload: dict) -> JSONResponse:
    """
    直接粘贴文本分析，前端「示例文章」走这条。

    与 `/api/analyze` 一样区分两套模型：`llm_*` 出讲解，`mt_*` 只出译文。
    """
    payload = payload or {}
    level_id = payload.get("level_id", "cet4")
    title = payload.get("title", "未命名文本")
    use_llm = bool(payload.get("use_llm"))
    want_translate = bool(payload.get("translate"))
    trans_mode = payload.get("trans_mode", "sentence")
    job_id = payload.get("job_id", "")
    # 与 /api/analyze 的 no_save 同义：自检跑这条链路时别往用户库里灌数据
    save = not bool(payload.get("no_save"))
    cfg = _resolve_cfg(payload.get("llm_provider", ""),
                       payload.get("llm_api_key", ""),
                       payload.get("llm_base_url", ""),
                       payload.get("llm_model", ""))
    mt_cfg = _resolve_mt_cfg(payload.get("mt_provider", ""),
                             payload.get("mt_api_key", ""),
                             payload.get("mt_base_url", ""),
                             payload.get("mt_model", ""))
    saved_mt = settings.load()
    tcfg, tnote = (_translation_cfg(
        mt_cfg, cfg,
        bool(saved_mt.get("mt_enabled", True)),
        bool(saved_mt.get("mt_fallback", True))) if want_translate else (None, ""))
    # 纯文本不经过 OCR
    _begin_job(job_id, use_llm, want_translate, cfg, ocr_hint=False, tcfg=tcfg)

    try:
        text = (payload.get("text") or "").strip()
        if not text:
            raise HTTPException(400, "文本为空")
        blocks = [b.as_dict() for b in parsers.parse_text(text)]
        if (use_llm or want_translate) and cfg.ready:
            # 同上：`enabled` 只反映「LLM 讲解增强」，不要被翻译带成 true
            _autosave_cfg(payload.get("llm_provider", ""), payload.get("llm_api_key", ""),
                          payload.get("llm_base_url", ""), payload.get("llm_model", ""),
                          use_llm)
        # 翻译模型配置独立回写（同 /api/analyze）
        _autosave_mt_cfg({"mt_provider": payload.get("mt_provider", ""),
                          "mt_base_url": payload.get("mt_base_url", ""),
                          "mt_model": payload.get("mt_model", ""),
                          "mt_api_key": payload.get("mt_api_key", "")})
        hb = _run_pipeline(blocks, level_id, title, cfg, use_llm,
                           want_translate, trans_mode, job_id, save=save,
                           tcfg=tcfg, tnote=tnote)
        hb["parse_info"] = {"engine": "plain-text"}
        progress.done(job_id, "手账已生成")
        return JSONResponse(hb)
    except HTTPException as e:
        progress.fail(job_id, str(e.detail))
        raise
    except Exception as e:  # noqa: BLE001
        progress.fail(job_id, f"{type(e).__name__}: {str(e)[:160]}")
        raise


@app.post("/api/render-only")
def render_only(payload: dict) -> JSONResponse:
    """只换版式重渲染（不重跑分析）。"""
    hb = payload.get("handbook") or {}
    html = render.render_handbook(hb, hb.get("title", "英语精读手账"))
    return JSONResponse({"html": html})


# ---------------------------------------------------------------- 知识库

@app.get("/api/library")
def library_index() -> dict:
    """知识库总览：手账列表 + 三本卡片本的统计 + 库目录路径。"""
    return {"stats": library.stats(), "docs": library.list_handbooks()}


@app.get("/api/library/audit")
def library_audit() -> dict:
    """
    找不一致：卡片指向了已不存在的手账（用户手工删过 json 时会出现）。

    正常情况下永远是空数组 —— 这条接口存在的意义是**让这种异常可见**，
    否则用户的生词本里会有一批删不掉的僵尸条目却查不出原因。

    ⚠ **必须声明在 `@app.get("/api/library/{doc_id}")` 之前**。
    两条都是两段路径，FastAPI 按声明顺序匹配：`/api/library/audit`
    会被 `{doc_id}` 抢先接走，于是这个接口永远返回
    「找不到这篇手账（可能已被删除）」。同理 `/api/library/cards/...`
    是三段、与 `{doc_id}` 不冲突，但**将来若加两段子路径也要注意**。
    """
    try:
        return {"problems": library.audit()}
    except RuntimeError as e:
        raise HTTPException(500, str(e)) from e


@app.post("/api/library/repair")
def library_repair() -> dict:
    """按 audit 的结论清掉僵尸卡片。"""
    try:
        return {**library.repair(), "problems": library.audit()}
    except RuntimeError as e:
        raise HTTPException(500, str(e)) from e


@app.post("/api/library")
def library_save(payload: dict) -> dict:
    """
    手动把一份手账存进知识库（自动保存之外的补充入口）。

    `handbook` 就是 `/api/analyze` 的返回体。`doc_id` 给了就覆盖那一篇，
    否则新建 —— 靠 `library.save_handbook` 内部的 reindex 保证幂等。
    """
    hb = payload.get("handbook") or {}
    if not hb.get("blocks"):
        raise HTTPException(400, "没有可保存的手账数据")
    try:
        return library.save_handbook(hb, payload.get("doc_id") or None)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except RuntimeError as e:
        raise HTTPException(500, f"保存失败：{e}") from e


@app.get("/api/library/{doc_id}")
def library_doc(doc_id: str) -> dict:
    """取回一篇手账的结构化数据（前端「打开」用）。"""
    try:
        hb = library.get_handbook(doc_id)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except RuntimeError as e:
        raise HTTPException(500, str(e)) from e
    if not hb:
        raise HTTPException(404, "找不到这篇手账（可能已被删除）")
    return hb


@app.get("/api/library/{doc_id}/html", response_class=HTMLResponse)
def library_doc_html(doc_id: str) -> HTMLResponse:
    """
    把历史手账**重新渲染**成 HTML（预览 / 下载 / 打印 PDF 共用这一条）。

    这是「存结构化 JSON 而不存 HTML 快照」换来的好处：
    以后改了版式，旧手账点导出就是新样式，不用重新上传原文、
    也不用再付一次大模型的钱。
    """
    try:
        hb = library.get_handbook(doc_id)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except RuntimeError as e:
        raise HTTPException(500, str(e)) from e
    if not hb:
        raise HTTPException(404, "找不到这篇手账（可能已被删除）")
    return HTMLResponse(render.render_handbook(hb, hb.get("title") or "英语精读手账"))


@app.delete("/api/library/{doc_id}")
def library_delete(doc_id: str) -> dict:
    """
    删除一篇手账。

    会连带把它对三本卡片本的贡献**回滚掉** —— 只删 json 而不回滚，
    用户删掉一篇 PDF 之后生词本里会永久留下一批查不到出处的僵尸条目，
    而且他根本删不掉（页面上找不到出处）。这是 `library.delete_handbook`
    内部做的，这里不需要额外操作。
    """
    try:
        existed = library.delete_handbook(doc_id)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except RuntimeError as e:
        raise HTTPException(500, f"删除失败：{e}") from e
    return {"deleted": existed, "stats": library.stats()}


@app.get("/api/library/cards/{kind}")
def library_cards(kind: str, q: str = "", status: str = "",
                  level: str = "", sort: str = "recent") -> dict:
    """读一本卡片（words / patterns / grammar）。"""
    if kind not in library.CARDS:
        raise HTTPException(404, f"没有这一本卡片（只有 {'/'.join(library.CARDS)}）")
    try:
        return library.list_cards(kind, q=q, status=status,
                                  level=level, sort=sort)
    except RuntimeError as e:
        raise HTTPException(500, str(e)) from e


@app.post("/api/library/cards/{kind}/{key}/status")
def library_card_status(kind: str, key: str, payload: dict) -> dict:
    """标记掌握度 / 写备注。`key` 里的斜杠已被前端 encodeURIComponent 处理。"""
    if kind not in library.CARDS:
        raise HTTPException(404, "没有这一本卡片")
    status = (payload or {}).get("status")
    note = (payload or {}).get("note")
    try:
        return library.set_status(kind, key, status, note)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except KeyError:
        raise HTTPException(404, "卡片不存在（可能已删）") from None
    except RuntimeError as e:
        raise HTTPException(500, str(e)) from e


@app.delete("/api/library/cards/{kind}/{key}")
def library_card_delete(kind: str, key: str) -> dict:
    if kind not in library.CARDS:
        raise HTTPException(404, "没有这一本卡片")
    try:
        ok = library.delete_card(kind, key)
    except RuntimeError as e:
        raise HTTPException(500, str(e)) from e
    return {"deleted": ok}


@app.get("/api/library/cards/{kind}/export.html", response_class=HTMLResponse)
def library_cards_html(kind: str, q: str = "", status: str = "",
                       level: str = "", sort: str = "alpha") -> HTMLResponse:
    """导出卡片本为可打印 HTML（浏览器 Ctrl+P 即 PDF）。"""
    if kind not in library.CARDS:
        raise HTTPException(404, "没有这一本卡片")
    try:
        data = library.list_cards(kind, q=q, status=status, level=level, sort=sort)
    except RuntimeError as e:
        raise HTTPException(500, str(e)) from e
    return HTMLResponse(cards_render.render_cards(kind, data, library.root()))


@app.get("/api/library/cards/{kind}/export.csv")
def library_cards_csv(kind: str, q: str = "", status: str = "",
                      level: str = "", sort: str = "alpha"):
    """
    导出纯文本 CSV（UTF-8 BOM，Excel 双击能正确认出中文）。

    不是用户点名要的格式，但**数据需要一个非 HTML 的出口** ——
    只给 HTML 的话，想备份、想搬到别的软件、想在项目目录出问题时留个底，
    都只能去翻 json。加它成本极低。
    """
    if kind not in library.CARDS:
        raise HTTPException(404, "没有这一本卡片")
    try:
        data = library.list_cards(kind, q=q, status=status, level=level, sort=sort)
    except RuntimeError as e:
        raise HTTPException(500, str(e)) from e
    body = cards_render.render_csv(kind, data)
    fname = f"studypad-{kind}.csv"
    return Response(
        content=body.encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{fname}"'},
    )


@app.get("/api/library/audit")
def library_audit() -> dict:
    """
    找不一致：卡片指向了已不存在的手账（用户手工删过 json 时会出现）。

    正常情况下永远是空数组 —— 这条接口存在的意义是**让这种异常可见**，
    否则用户的生词本里会有一批删不掉的僵尸条目却查不出原因。
    """
    try:
        return {"problems": library.audit()}
    except RuntimeError as e:
        raise HTTPException(500, str(e)) from e


@app.post("/api/library/repair")
def library_repair() -> dict:
    """按 audit 的结论清掉僵尸卡片。"""
    try:
        return {**library.repair(), "problems": library.audit()}
    except RuntimeError as e:
        raise HTTPException(500, str(e)) from e


@app.get("/api/sample")
def sample() -> dict:
    p = SAMPLES / "sample_article.md"
    if not p.exists():
        raise HTTPException(404, "示例文章不存在")
    return {"title": "Example: The Cost of Convenience",
            "text": p.read_text(encoding="utf-8")}


# ---------------------------------------------------------------- LLM 增强

_ENRICH_SYS = """You are a senior English teacher writing margin notes for a Chinese
student. You will receive English sentences together with grammar structures that
have already been detected by a rule engine.

The user message may also contain a 【考试阶段】block: a verified digest of what the
student's target exam actually tests. Use it as REFERENCE for emphasis only —
explain the grammar points that this exam really weights more concretely
(e.g. for 考研 stress clause splitting; for 高中 stress 语法填空 的六类考点).
Never treat the digest as a checklist of things to annotate, and never copy its
wording into an explanation.

Your task: for each item, write a BETTER, more natural Chinese explanation of the
grammar point IN CONTEXT. Keep each explanation under 80 Chinese characters.
Do NOT invent grammar points that were not listed. Do NOT mark vocabulary.

Return STRICT JSON: {"items":[{"id":"<given id>","explain":"<Chinese explanation>"}]}
"""


def _enrich_with_llm(parsed: dict, level_id: str, cfg: llm.LLMConfig) -> int:
    """把语法讲解交给模型重写得更像真人老师。批量提交，控制成本。"""
    items = []
    for b in parsed["blocks"]:
        for c in b.get("candidates", []):
            if c["type"] != "grammar_underline":
                continue
            items.append({
                "id": f'{b["id"]}:{c["start"]}',
                "sentence": (b.get("text") or "")[:600],
                "grammar": c["payload"].get("label", ""),
            })
    if not items:
        return 0

    items = items[:24]
    payload = "\n".join(
        f'{i["id"]} | {i["grammar"]} | {i["sentence"]}' for i in items
    )
    # 把该阶段的考点摘要注入进去：模型因此知道「这个阶段真正在意哪些语法」，
    # 讲解会有侧重，而不是对每个点平均用力。
    ctx = exam_points.prompt_context(
        level_id, sections=("grammar", "high_frequency", "focus"))
    label = exam_points.require(level_id)["label"]
    out = llm.chat(cfg, [
        {"role": "system", "content": _ENRICH_SYS},
        {"role": "user", "content":
            f"Target level: {level_id}（{label}）\n\n{ctx}\n\n{payload}"},
    ], max_tokens=2200)
    data = llm.parse_json(out)
    mapping = {d["id"]: d.get("explain", "") for d in data.get("items", []) if d.get("id")}

    n = 0
    for b in parsed["blocks"]:
        for c in b.get("candidates", []):
            if c["type"] != "grammar_underline":
                continue
            key = f'{b["id"]}:{c["start"]}'
            txt = mapping.get(key)
            if txt:
                c["payload"]["explain"] = txt
                c["source"] = "llm"
                n += 1
    return n


# ---------------------------------------------------------------- 静态页

app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")


def _page(name: str) -> HTMLResponse:
    p = STATIC / name
    if not p.exists():
        raise HTTPException(404, f"页面 {name} 不存在")
    return HTMLResponse(p.read_text(encoding="utf-8"))


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    """制作页：上传材料 → 选等级 → 生成手账。"""
    return _page("index.html")


@app.get("/library", response_class=HTMLResponse)
@app.get("/library/", response_class=HTMLResponse)
def library_page() -> HTMLResponse:
    """
    知识库独立页：历史手账 + 生词本 / 句型本 / 语法本。

    2026-10-15 从 index.html 拆出。此前两者挤在一页里，
    首屏要同时看等级选择、上传区、模型设置、考点面板、手账预览，
    外加一整套知识库 —— 层级混乱且信息密度过高。
    """
    return _page("library.html")
