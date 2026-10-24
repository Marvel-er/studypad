"""
任务进度上报：让前端显示**真实**进度，而不是一个永远转的圈。

## 为什么需要它

原来整个链路是一个同步 POST，服务端不对外暴露任何阶段信息，
前端只能把按钮变成「正在标注…」然后一直转。用户看到的是：
不知道在做什么、不知道还要多久、更不知道是不是卡死了。

标注本身其实**只占几毫秒**（纯规则），真正的耗时几乎都在等模型
（LLM 讲解重写、中文译文）和 OCR 上。所以那条「正在标注…」不只是没有进度，
而是**把等待的原因说错了** —— 用户以为在标注，实际在等模型。

## 三条设计原则

1. **不编进度。** 百分比只在有分母的地方推进：知道要翻几批就用批次做分母；
   不知道分母的阶段（等模型应答）就不动进度条，改为如实显示「正在等待模型」，
   并让「已用时长」继续走 —— 时长本身就是「没卡死」的证据。
2. **百分比单调不减。** 进度条回退会让人以为出错了，所以只允许前进。
3. **上报绝不能拖慢主流程。** 全部是内存字典操作 + 一把锁，
   任何异常都吞掉（进度丢了是小事，任务失败是大事）。

## 生命周期

    begin(job, plan)  → at(job, "parse") → …→ at(job, "render") → done(job)
    失败走 fail(job, msg)。前端拿到 done/error 后停止轮询。

任务表在内存里，按 TTL 清理（默认 10 分钟），进程重启即清空 —— 这是刻意的：
进度只在「一次生成」的时间尺度上有意义，没必要持久化。
"""
from __future__ import annotations

import threading
import time

# 任务保留时长与容量上限：只服务「正在进行」的请求，不做长期存储
TTL = 600.0
MAX_JOBS = 64

# 超过这么久没有新上报，就认为「在等某个东西」而不是「在算东西」
STALL_AFTER = 6.0

# 说不出具体原因时的兜底文案
DEFAULT_WAIT = "仍在处理中，请稍候"

_lock = threading.Lock()
_jobs: dict[str, dict] = {}
_seq = 0


# =====================================================================
# 阶段计划
# =====================================================================

def plan(use_llm: bool, translate: bool, ocr_hint: bool,
         translate_local: bool = False) -> list[dict]:
    """
    按本次请求实际会做的事，排出阶段与权重。

    权重是「预期耗时占比」，不是拍脑袋的平均分配：标注是纯规则、毫秒级，
    所以只给 5；等模型的两段给大头 —— 这样进度条的位置才和用户等待的感受一致。
    OCR 很慢（秒级/页），所以要单独抬高解析阶段的权重。

    每个阶段还带一条 `wait` 文案，用于「这一个阶段卡了 6 秒以上」时告诉用户
    卡在哪。**这条文案必须逐阶段写**，不能用一句通用的「等待模型应答」兜底：
    OCR 是本地推理，一页照片跑十几秒很正常，那时说「在等模型」就是把原因讲错了 ——
    而把原因讲错，正是这次要修的那类问题（原来那句「正在标注…」就把等待说成了标注）。
    """
    stages: list[dict] = [{
        "key": "parse", "label": "解析文档与 OCR 识别" if ocr_hint else "解析文档",
        "weight": 30 if ocr_hint else 5,
        "hint": "扫描件与图片需要跑 OCR，每页约 1–2 秒" if ocr_hint else "",
        "wait": ("正在 OCR 识别扫描件（每页约 1–2 秒，照片大或页数多时会更久）"
                 if ocr_hint else "正在解析文档"),
    }, {
        "key": "annotate", "label": "按所选水平标注单词与语法",
        "weight": 5,
        "hint": "由本地规则引擎完成，通常很快",
        "wait": "正在用本地规则引擎标注（纯本地计算，不需要联网）",
    }]
    if use_llm:
        stages.append({
            "key": "enrich", "label": "大模型重写语法讲解", "weight": 25,
            "hint": "正在等待模型应答，通常几秒到几十秒",
            "wait": "等待模型应答，正在重写语法讲解（大模型一般需要数秒到一分钟）",
        })
    if translate:
        # 翻译走本地小模型时权重从 35 降到 10：实测同一篇 23 句文章，
        # 本地 3.3 秒翻完，而云端要几十秒 —— 权重是「预期耗时占比」，
        # 不跟着改的话进度条会在最后一段凭空慢下来，看起来像卡住。
        stages.append({
            "key": "translate", "label": "生成中文译文",
            "weight": 10 if translate_local else 35,
            "hint": ("由本机翻译模型完成，通常几秒内翻完整篇；已翻译过的句子会直接复用缓存"
                     if translate_local else
                     "整篇逐句翻译，按批提交给模型；已翻译过的句子会直接复用缓存"),
            "wait": ("正在用本机翻译模型整批翻译（本地推理，通常几秒，不消耗云端额度）"
                     if translate_local else
                     "等待模型应答，正在整批翻译（大模型一般需要数秒到一分钟）"),
        })
    stages.append({
        "key": "render", "label": "排版手账", "weight": 5, "hint": "",
        "wait": "正在排版手账",
    })
    return stages


# =====================================================================
# 内部工具
# =====================================================================

def _prune_locked() -> None:
    """清掉过期任务；仍然超量就丢最老的（先丢已结束的）。"""
    global _seq
    now = time.monotonic()
    for k in [k for k, v in _jobs.items() if now - v["touched"] > TTL]:
        _jobs.pop(k, None)
    if len(_jobs) <= MAX_JOBS:
        return
    order = sorted(_jobs.items(),
                   key=lambda kv: (not kv[1]["done"], kv[1]["touched"]))
    for k, _v in order[: len(_jobs) - MAX_JOBS]:
        _jobs.pop(k, None)


def begin(job_id: str, stages: list[dict]) -> None:
    """登记一个任务。空 job_id 直接忽略（进度是可选的，不该让请求失败）。"""
    if not job_id:
        return
    global _seq
    try:
        with _lock:
            _prune_locked()
            _seq += 1
            _jobs[job_id] = {
                "job_id": job_id,
                "stages": stages,
                "total": sum(max(1, int(s.get("weight") or 1)) for s in stages) or 1,
                "idx": 0,
                "sub": (0, 0),
                "detail": "",
                "max_percent": 0.0,
                "t0": time.monotonic(),
                "touched": time.monotonic(),
                "done": False,
                "error": "",
                "seq": _seq,
            }
    except Exception:  # noqa: BLE001 — 上报失败绝不影响主流程
        pass


def at(job_id: str, key: str, detail: str = "") -> None:
    """进入某个阶段（按 key 定位，找不到就忽略）。"""
    if not job_id:
        return
    try:
        with _lock:
            j = _jobs.get(job_id)
            if not j or j["done"]:
                return
            for i, s in enumerate(j["stages"]):
                if s["key"] == key:
                    # 只前进不后退：乱序上报也不会让进度条倒退
                    j["idx"] = max(j["idx"], i)
                    break
            j["sub"] = (0, 0)
            j["detail"] = detail
            j["touched"] = time.monotonic()
    except Exception:  # noqa: BLE001
        pass


def sub(job_id: str, done: int, total: int, detail: str = "") -> None:
    """当前阶段的细粒度进度（例如「第 2/3 批」）。"""
    if not job_id:
        return
    try:
        with _lock:
            j = _jobs.get(job_id)
            if not j or j["done"]:
                return
            j["sub"] = (max(0, int(done)), max(0, int(total)))
            if detail:
                j["detail"] = detail
            j["touched"] = time.monotonic()
    except Exception:  # noqa: BLE001
        pass


def done(job_id: str, note: str = "") -> None:
    if not job_id:
        return
    try:
        with _lock:
            j = _jobs.get(job_id)
            if not j:
                return
            j["idx"] = len(j["stages"])          # 满格
            j["sub"] = (0, 0)
            j["done"] = True
            if note:
                j["detail"] = note
            j["touched"] = time.monotonic()
    except Exception:  # noqa: BLE001
        pass


def fail(job_id: str, message: str) -> None:
    if not job_id:
        return
    try:
        with _lock:
            j = _jobs.get(job_id)
            if not j:
                return
            j["error"] = str(message)[:300]
            j["touched"] = time.monotonic()
    except Exception:  # noqa: BLE001
        pass


def snapshot(job_id: str) -> dict:
    """给前端的进度快照。未知任务返回 found=False（不是 404，避免轮询刷错误）。"""
    now = time.monotonic()
    try:
        with _lock:
            j = _jobs.get(job_id)
            if not j:
                return {"found": False, "job_id": job_id,
                        "active": False, "percent": 0, "done": False}
            stages = j["stages"]
            idx = min(j["idx"], len(stages))
            base = sum(max(1, int(s.get("weight") or 1)) for s in stages[:idx])
            if idx < len(stages):
                w = max(1, int(stages[idx].get("weight") or 1))
                d, t = j["sub"]
                frac = (d / t) if t > 0 else 0.0
                # 阶段内的细粒度进度最多算到 95%：这一段跑完才算这个阶段结束，
                # 否则会在阶段切换时出现「卡在 100% 不动」的观感
                frac = max(0.0, min(0.95, frac))
                cur = stages[idx]
                stage_key, stage_label = cur["key"], cur["label"]
                hint = cur.get("hint", "")
                waiting_label = cur.get("wait") or DEFAULT_WAIT
            else:
                frac, w = 0.0, 0
                stage_key, stage_label, hint = "done", "完成", ""
                waiting_label = ""

            raw = (base + w * frac) / j["total"] * 100.0
            if j["done"]:
                raw = 100.0
            pct = max(j["max_percent"], raw)
            j["max_percent"] = pct                 # 记住最高点，保证单调

            since = now - j["touched"]
            return {
                "found": True,
                "job_id": job_id,
                "active": not j["done"],
                "done": j["done"],
                "error": j["error"],
                "percent": round(min(100.0, pct), 1),
                "stage": stage_key,
                "stage_label": stage_label,
                "detail": j["detail"],
                "hint": hint,
                "waiting_label": waiting_label,
                "elapsed": round(now - j["t0"], 1),
                "since_update": round(since, 1),
                "waiting": (not j["done"]) and since >= STALL_AFTER,
                "stage_index": idx,
                "stage_count": len(stages),
            }
    except Exception:  # noqa: BLE001
        return {"found": False, "job_id": job_id, "active": False,
                "percent": 0, "done": False}


def stats() -> dict:
    """给自检与排查用：当前登记了几个任务、有几个还在跑。"""
    try:
        with _lock:
            _prune_locked()
            return {
                "jobs": len(_jobs),
                "active": sum(1 for v in _jobs.values() if not v["done"]),
                "ttl": TTL, "max_jobs": MAX_JOBS, "stall_after": STALL_AFTER,
            }
    except Exception:  # noqa: BLE001
        return {"jobs": 0, "active": 0}


def clear() -> int:
    """清空任务表（自检用）。"""
    try:
        with _lock:
            n = len(_jobs)
            _jobs.clear()
            return n
    except Exception:  # noqa: BLE001
        return 0
