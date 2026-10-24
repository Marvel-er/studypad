"""
接口层自检：中文译文（/api/translate/*、/api/analyze*、/api/levels）。

模块自检验的是「翻译对不对」，这里验的是**整条链路怎么把译文交给用户**：

1. **没配模型时必须说清「为什么没有译文」**，而不是静默无译文、更不是 500。
   用户看到手账里没有译文，唯一能接受的解释是「要配模型」——
   「服务器错误」和「我也不知道为什么」都不合格。
2. **对齐必须穿过 HTTP 边界仍然成立**：接口返回的 `translations` 里
   第 k 句译文必须真的对应第 k 句原文，且渲染出的 HTML 里能查到这句中文。
3. **译文不许动标注**：同一个文件开/关译文，标注计数必须完全一致。
   翻译是旁路，一旦它改了 block 内容或顺序，标注就会跟着漂。
4. 配置落盘时 `enabled` 只跟「LLM 讲解增强」走，不能被「只是想翻译」带成 true。

假模型 monkeypatch 掉 `llm.chat`，全程零真实请求。
临时目录放系统临时目录（工作区的 safe-delete 守卫会拦批量删除）。
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

TMP = Path(tempfile.gettempdir()) / "_studypad_transapi"
os.environ["STUDYPAD_HOME"] = str(TMP)

from fastapi.testclient import TestClient  # noqa: E402

from app import llm, settings, translate  # noqa: E402
from app.main import app  # noqa: E402

LOG: list[str] = []
PASS = FAIL = 0


def check(name: str, cond: bool, extra: str = "") -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
    LOG.append(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f"  → {extra}" if extra else ""))


c = TestClient(app)

# 样例要「有东西可标」，否则「开/关译文标注一致」这条断言会退化成 0 == 0 的空转。
# 故意塞进让步状语从句、Not only...but also、非限定性定语从句这类考点结构。
SAMPLE = (
    "Although the committee had been informed of the potential risks, it nevertheless "
    "decided to proceed with the experiment. The results, which were published last month, "
    "suggest that the hypothesis is worth pursuing.\n\n"
    "Not only did the team overcome the technical obstacles, but it also managed to reduce "
    "the overall cost. This achievement demonstrates the importance of persistent effort."
)

CALLS: list[str] = []


def fake_chat(cfg, messages, **kw):
    """假翻译模型：按输入行数逐条返回，前缀「中译」以便校验是否错位。"""
    CALLS.append(messages[-1]["content"])
    sents = re.findall(r"^\d+\.\s?(.*)$", messages[-1]["content"], re.M)
    return json.dumps({"t": [f"中译{s[:24]}" for s in sents]}, ensure_ascii=False)


def post_text(**kw):
    payload = {"text": SAMPLE, "level_id": "cet4", "title": "样例", "use_llm": False}
    payload.update(kw)
    return c.post("/api/analyze-text", json=payload)


# 判断「译文块真的渲染了吗」必须匹配 class 属性本身。
# 直接写 `"tr-zh" in html` 是假绿：这两个类名本来就写在 HTML 内嵌的 <style> 里，
# 于是正向断言恒真、反向断言恒假 —— 等于什么都没验。
def has_zh(html: str) -> bool:
    return 'class="tr-zh"' in html or 'class="tr-zh partial"' in html


def has_pair(html: str) -> bool:
    return 'class="tr-pair"' in html


def no_translation_model() -> None:
    """
    把「没有任何可用翻译模型」这个前提**显式**搭出来。

    ⚠ 2026-10-15 起，这件事不再等于「清空配置」：翻译与讲解是两套模型，
    只清空配置的话翻译会默认走本机 Ollama 上的 `hy-mt2:1.8b`，而本机模型可用 ——
    于是「无 Key」也照样出译文。第 1、3、12 节验的是**真没有模型**时的表现，
    必须连本地翻译模型一起关掉，否则那几条断言什么都没验到。
    """
    try:
        settings.clear()
    except Exception:  # noqa: BLE001
        pass
    settings.save({"mt_enabled": False})


def main() -> None:
    # 干净的起点：不要读到上一个测试留下的配置
    TMP.mkdir(parents=True, exist_ok=True)
    # 有些模型的 Key 也会被 llm.resolved() 从环境变量里捡回来，
    # 不摘掉的话「未配置」这条分支根本走不到，整段自检会变成假绿。
    for k in list(os.environ):
        if k.endswith("_API_KEY"):
            os.environ.pop(k, None)
    no_translation_model()

    # ------------------------------------------------------- 1. 未配置模型时的状态
    r = c.get("/api/translate/status")
    check("GET /api/translate/status → 200", r.status_code == 200, str(r.status_code))
    st = r.json()
    check("status 声明翻译必须用大模型", st["required"] == "llm", str(st.get("required")))
    check("未配置时 available=False", st["available"] is False, str(st.get("available")))
    check("status 带成本护栏参数",
          st["max_chars"] == translate.MAX_CHARS and st["batch_sentences"] > 0)
    check("status 带缓存条目数", isinstance(st.get("cache_entries"), int))
    msg = st.get("message", "")
    # 「为什么没有译文」这件事必须直说。断言按**意图**写（说了原因、且理由是「没有可用的翻译模型」），
    # 不锁死具体措辞 —— 锁死措辞的断言会在文案正常迭代时假红，然后被人「顺手改绿」。
    check("★ 没有可用翻译模型时说清了原因",
          ("关闭" in msg or "未就绪" in msg) and "翻译" in msg, msg[:80])
    check("status 不谎报可用的 provider/model",
          st["provider"] == "" and st["model"] == "",
          f'{st["provider"]} / {st["model"]}')

    # ------------------------------------------------------- 2. /api/levels 带 show_translation
    r = c.get("/api/levels")
    check("GET /api/levels → 200", r.status_code == 200, str(r.status_code))
    lv = r.json()["levels"]
    check("每档都带 show_translation（布尔）",
          all(isinstance(x.get("show_translation"), bool) for x in lv))
    check("低阶段默认给译文、高阶段默认不给（教学取向）",
          lv[0]["show_translation"] is True and lv[-1]["show_translation"] is False,
          str([(x["id"], x["show_translation"]) for x in lv]))

    # ------------------------------------------------------- 3. 无 Key 时请求翻译
    r = post_text(translate=True)
    check("无 Key 时请求翻译 → 200（不是 500）", r.status_code == 200, str(r.status_code))
    hb = r.json()
    check("无 Key 时 trans_mode 归为 off", hb["trans_mode"] == "off", hb["trans_mode"])
    check("无 Key 时不产出任何译文", hb["translations"] == {})
    note = hb.get("trans_note", "")
    # 断言按**意图**写：说明里必须讲清「为什么没有译文」（没有可用的翻译模型），
    # 且要点出翻译**不是规则引擎能兜的** —— 那正是当初拒绝糊一份假译文的理由。
    # 不锁死具体措辞：文案一迭代就假红，然后被人顺手改绿。
    check("★ 无 Key 时说明白为什么没有译文",
          ("不可用" in note or "未配置" in note or "关闭" in note)
          and "模型" in note and "规则" in note, note[:70])
    check("无 Key 时手账正文照常渲染", "hb-head" in hb["html"])
    check("无 Key 时 HTML 里没有译文块（只看 class，别被 CSS 骗了）",
          not has_zh(hb["html"]) and not has_pair(hb["html"]))
    check("无 Key 时不会凭空写入配置", not settings.load().get("api_key"))

    # ------------------------------------------------------- 4. 译文缓存接口
    translate.cache_put("a probe sentence.", "一个探针句子。")
    r = c.get("/api/translate/status")
    check("缓存写入后 status 能反映出来", r.json()["cache_entries"] >= 1,
          str(r.json()["cache_entries"]))
    r = c.delete("/api/translate/cache")
    check("DELETE /api/translate/cache → 200", r.status_code == 200, str(r.status_code))
    check("清缓存返回删除条数", r.json()["removed"] >= 1, str(r.json().get("removed")))
    check("清空后 cache_entries=0", r.json()["cache_entries"] == 0)
    check("重复清空不报错", c.delete("/api/translate/cache").status_code == 200)

    # ------------------------------------------------------- 5. 配上 Key（假模型）
    settings.save({"provider": "deepseek", "api_key": "sk-fake-for-test",
                   "base_url": "http://fake.local/v1", "model": "fake", "enabled": False})
    orig = llm.chat
    llm.chat = fake_chat
    try:
        CALLS.clear()
        r = post_text(translate=True, trans_mode="sentence")
        check("配置 Key 后请求翻译 → 200", r.status_code == 200, str(r.status_code))
        hb = r.json()
        check("trans_mode 落为 sentence", hb["trans_mode"] == "sentence", hb["trans_mode"])
        check("translations 非空", bool(hb["translations"]),
              str(list(hb["translations"].keys())))

        # ★ 对齐必须穿过 HTTP 边界仍然成立。
        # 比较前要 strip：假模型的译文里 s[:24] 可能把第 24 位的空格一起带上，
        # 而服务端的 _clean 会去掉尾随空白 —— 这是格式差异，不是对齐错误。
        bad = []
        for bid, tr in hb["translations"].items():
            for s in tr["sentences"]:
                if s["zh"] != ("中译" + s["en"][:24]).strip():
                    bad.append((bid, s["en"], s["zh"]))
        check("★ 接口返回的译文逐句对齐正确（没有错位）", not bad, str(bad[:2]))
        # 前缀若有重复，上面这条就分辨不出「两句译文对调」了 —— 断言本身要先站得住
        prefs = [s["en"][:24] for tr in hb["translations"].values()
                 for s in tr["sentences"]]
        check("样例的句子前缀互不相同（否则对齐检查形同虚设）",
              len(set(prefs)) == len(prefs) and len(prefs) >= 4, str(prefs))
        check("每段译文条数与原文句数一致", all(
            len(tr["sentences"]) == len(translate.split_spans(
                next(b["text"] for b in hb["blocks"] if b["id"] == bid)))
            for bid, tr in hb["translations"].items()))
        check("★ 译文真的渲染进了 HTML",
              "中译" in hb["html"] and has_pair(hb["html"]))
        check("HTML 标注了译文版式（逐句对照）", "逐句对照" in hb["html"])
        check("trans_note 报告译文段数", "中文译文" in hb.get("trans_note", ""),
              hb.get("trans_note", "")[:60])
        check("HTML 有译文免责说明", "中文译文由大模型生成" in hb["html"])

        # ---- 配置落盘：enabled 不能被「只是想翻译」带成 true（回归护栏）
        check("★ 只勾译文不会顺手打开「LLM 讲解增强」",
              settings.public()["enabled"] is False,
              f"enabled={settings.public()['enabled']}")
        check("Key 已按预期落盘", settings.public()["has_key"] is True)
        pub = json.dumps(settings.public(), ensure_ascii=False)
        check("★ 完整 Key 不会回到浏览器（只给掩码）",
              "sk-fake-for-test" not in pub and "*" in settings.public()["key_hint"],
              settings.public()["key_hint"])

        # --------------------------------------------------- 6. 缓存复用（接口层）
        n1 = len(CALLS)
        r = post_text(translate=True, trans_mode="sentence")
        check("同文重发仍能出译文", r.status_code == 200 and bool(r.json()["translations"]))
        check("★ 同文重发不再打模型（缓存命中）", len(CALLS) == n1,
              f"{n1} → {len(CALLS)}")
        check("重发时提示复用了缓存", "复用缓存" in r.json().get("trans_note", ""),
              r.json().get("trans_note", "")[:70])

        # --------------------------------------------------- 7. 整段附译版式
        r = post_text(translate=True, trans_mode="paragraph")
        hb2 = r.json()
        check("段落版式 trans_mode 落为 paragraph",
              hb2["trans_mode"] == "paragraph", hb2["trans_mode"])
        check("段落版式用 tr-zh 而不是 tr-pair",
              has_zh(hb2["html"]) and not has_pair(hb2["html"]))
        check("段落版式标注为「整段附译」", "整段附译" in hb2["html"])

        # --------------------------------------------------- 8. 关掉译文
        r = post_text(translate=False)
        hb3 = r.json()
        check("不请求翻译时 trans_mode=off", hb3["trans_mode"] == "off")
        check("不请求翻译时不产出译文", hb3["translations"] == {})
        check("不请求翻译时 HTML 无译文块",
              not has_zh(hb3["html"]) and not has_pair(hb3["html"]))
        check("不请求翻译时不给翻译提示", "中文译文" not in hb3.get("trans_note", ""))

        # --------------------------------------------------- 9. ★ 译文不许动标注
        check("样例确实产生了标注（否则下面这条断言是空转）",
              sum(hb3["counters"].values()) > 0, str(hb3["counters"]))
        check("★ 开/关译文，标注计数完全一致",
              hb3["counters"] == hb["counters"],
              f'{hb3["counters"]} vs {hb["counters"]}')
        check("★ 开/关译文，分块内容与顺序一致",
              [b["id"] for b in hb3["blocks"]] == [b["id"] for b in hb["blocks"]]
              and [b["text"] for b in hb3["blocks"]] == [b["text"] for b in hb["blocks"]])

        # --------------------------------------------------- 10. 文件上传入口
        r = c.post("/api/analyze",
                   files={"file": ("sample.txt", SAMPLE.encode(), "text/plain")},
                   data={"level_id": "cet4", "use_llm": "false",
                         "translate": "true", "trans_mode": "sentence"})
        check("POST /api/analyze + translate → 200", r.status_code == 200, str(r.status_code))
        hbf = r.json()
        check("上传入口也能出译文", bool(hbf["translations"]), hbf["trans_mode"])
        check("上传入口 HTML 带译文", "中译" in hbf["html"])
        check("上传入口 trans_note 报告译文", "中文译文" in hbf.get("trans_note", ""))

        # --------------------------------------------------- 11. 始终对不齐 → 明说原因
        # 必须先清缓存：SAMPLE 在第 5 步已经翻过并落盘，
        # 不清的话这里会全部命中缓存，坏模型根本不会被调用 ——
        # 那这条用例就从「验对齐失败」退化成「验缓存命中」了。
        translate.clear_cache()

        def stubborn(cfg, messages, **kw):
            CALLS.append(messages[-1]["content"])
            sents = re.findall(r"^\d+\.\s?(.*)$", messages[-1]["content"], re.M)
            return json.dumps({"t": ["永远多一条"] * (len(sents) + 1)}, ensure_ascii=False)

        llm.chat = stubborn
        before = len(CALLS)
        r = post_text(translate=True)
        check("模型始终对不齐 → 200（不 500）", r.status_code == 200, str(r.status_code))
        check("对不齐时确实调了模型（不是靠缓存蒙过去）",
              len(CALLS) > before, f"{before} → {len(CALLS)}")
        hb4 = r.json()
        check("对不齐时不产出译文", hb4["translations"] == {})
        check("对不齐时 trans_mode 归 off", hb4["trans_mode"] == "off")
        check("★ 对不齐时把真实原因说出来（不是「无可用段落」）",
              "对齐失败" in hb4.get("trans_note", ""), hb4.get("trans_note", "")[:70])
        check("对不齐时手账仍然完整可用", "hb-head" in hb4["html"])
    finally:
        llm.chat = orig

    # ------------------------------------------------------- 12. 无 Key 的上传入口
    no_translation_model()
    r = c.post("/api/analyze",
               files={"file": ("sample.txt", SAMPLE.encode(), "text/plain")},
               data={"level_id": "cet4", "use_llm": "false", "translate": "true"})
    check("上传入口无 Key 请求翻译 → 200", r.status_code == 200, str(r.status_code))
    note_up = r.json().get("trans_note", "")
    check("上传入口无 Key 时明确说明原因",
          ("不可用" in note_up or "未配置" in note_up or "关闭" in note_up)
          and "翻译" in note_up, note_up[:70])


def _report(tb: str = "") -> None:
    if tb:
        LOG.append("*** 自检中途异常终止 ***")
        LOG.append(tb)
    LOG.append("")
    LOG.append(f"结果：{PASS} 通过 / {FAIL} 失败")
    (ROOT / "out" / "_transapi_test.txt").write_text("\n".join(LOG), encoding="utf-8")
    print(f"PASS={PASS} FAIL={FAIL}")


def _cleanup() -> None:
    try:
        settings.clear()
    except Exception:  # noqa: BLE001
        pass
    if TMP.exists():
        for f in list(TMP.rglob("*")):
            if f.is_file():
                f.unlink()
        for d in sorted([p for p in TMP.rglob("*") if p.is_dir()],
                        key=lambda p: -len(p.parts)):
            try:
                d.rmdir()
            except OSError:
                pass
        try:
            TMP.rmdir()
        except OSError:
            pass


if __name__ == "__main__":
    tb = ""
    try:
        main()
    except BaseException:  # noqa: BLE001
        import traceback
        tb = traceback.format_exc()
    try:
        _report(tb)
    finally:
        _cleanup()
    sys.exit(1 if (FAIL or tb) else 0)
