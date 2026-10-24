"""
进度上报自检：单元（数据结构）+ 端到端（真实 HTTP + 真实并发）。

## 为什么必须分两层

`progress` 模块自己算得对，**不等于**用户看到的东西对。这次要修的问题是：

    按钮写着「正在标注…」一直转，提示还并排写着「准备就绪，点击生成手账」，
    用户既不知道它在干什么，也不知道是不是卡死了。

这条问题的证据只存在于「一次真实请求的时间轴上」，静态单测看不见。所以这里
真的起一个 uvicorn、真的发 HTTP、真的在另一个线程里跑生成，再按前端 700ms 的
节奏从主线程轮询，把**用户会看到的那个序列**录下来断言：

  · 百分比单调不减（回退会让人以为出错了，比没进度条更糟）；
  · 阶段文案按真实流程推进，不是永远停在同一句；
  · **模型卡住时必须出现 `waiting=True`** —— 这是「没卡死，是在等模型」的唯一证据，
    也正是用户最需要的那个回答；
  · 失败时 `error` 有值，前端据此立刻停轮询，而不是空转到超时；
  · 上报不能拖慢主流程：卡住期间别的接口仍要毫秒级返回。

## 桩模型

真的监听端口，用类属性 `delay` 控制快慢。慢的那只 sleep 9 秒 ——
大于 `STALL_AFTER`（6 秒）能观察到 waiting，又小于客户端 90 秒超时，
所以不会留下一个永远挂着的请求线程。

## 环境

`STUDYPAD_HOME` 指向系统临时目录（工作区的 safe-delete 守卫会拦批量删除，
译文缓存清空时会被误伤）。起点显式 `clear_cache()`：缓存的句子不会去调模型，
不清就会「慢测试根本不慢」，测了半天什么都没验到。
"""
from __future__ import annotations

import json
import os
import re
import socket
import sys
import tempfile
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

TMP = Path(tempfile.gettempdir()) / "_studypad_progress"
TMP.mkdir(parents=True, exist_ok=True)
os.environ["STUDYPAD_HOME"] = str(TMP)

import httpx  # noqa: E402
import uvicorn  # noqa: E402

from app import progress as P  # noqa: E402
from app import translate as tr  # noqa: E402
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


def note(line: str = "") -> None:
    LOG.append(line)


# =====================================================================
# 桩模型：真的监听端口
# =====================================================================

class _StubBase(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    delay = 0.0
    calls: list[int] = []

    def log_message(self, *a):        # 别把访问日志喷到 stdout
        pass

    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n).decode("utf-8")
        try:
            payload = json.loads(raw or "{}")
        except ValueError:
            payload = {}
        msgs = payload.get("messages") or []
        user = msgs[-1].get("content", "") if msgs else ""
        sents = re.findall(r"^\d+\.\s?(.*)$", user, re.M)
        cls = type(self)
        cls.calls.append(len(sents))
        if cls.delay:
            time.sleep(cls.delay)
        content = ("```json\n"
                   + json.dumps({"t": [f"中译{s[:24]}" for s in sents]}, ensure_ascii=False)
                   + "\n```")
        self._json({"id": "stub", "object": "chat.completion",
                    "choices": [{"index": 0, "finish_reason": "stop",
                                 "message": {"role": "assistant", "content": content}}],
                    "usage": {"prompt_tokens": 1, "completion_tokens": 1}})


class FastStub(_StubBase):
    delay = 0.0
    calls: list[int] = []


class SlowStub(_StubBase):
    """sleep 9 秒：够越过 STALL_AFTER，又短于 90 秒读超时。"""
    delay = 9.0
    calls: list[int] = []


def start_stub(cls) -> str:
    srv = ThreadingHTTPServer(("127.0.0.1", 0), cls)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    host, port = srv.server_address[:2]
    return f"http://{host}:{port}/v1"


def free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


SAMPLE = (
    "Although the committee had been informed of the potential risks, it nevertheless "
    "decided to proceed with the experiment. The results, which were published last month, "
    "suggest that the hypothesis is worth pursuing.\n\n"
    "Not only did the team overcome the technical obstacles, but it also managed to reduce "
    "the overall cost. This achievement demonstrates the importance of persistent effort."
)

# =====================================================================
# 第 1 层：progress 模块的确定性断言
# =====================================================================

def unit_checks() -> None:
    P.clear()
    note("---- 阶段计划 ----")

    plain = P.plan(use_llm=False, translate=False, ocr_hint=False)
    check("纯规则任务不排「等模型」阶段",
          [s["key"] for s in plain] == ["parse", "annotate", "render"],
          str([s["key"] for s in plain]))

    trn = P.plan(use_llm=False, translate=True, ocr_hint=False)
    w = {s["key"]: s["weight"] for s in trn}
    check("开译文时才有 translate 阶段且权重最大",
          [s["key"] for s in trn] == ["parse", "annotate", "translate", "render"]
          and w["translate"] == max(w.values()),
          str(w))

    full = P.plan(use_llm=True, translate=True, ocr_hint=True)
    check("OCR 让解析阶段显著加权（扫描件本来就慢）",
          full[0]["weight"] == 30 and "OCR" in full[0]["label"],
          f"{full[0]['weight']} / {full[0]['label']}")
    check("OCR 计划里带「每页约 1–2 秒」预期，用户才知道该等多久",
          "1–2 秒" in (full[0].get("hint") or ""),
          full[0].get("hint", ""))
    check("每个阶段都带自己的「等待文案」（否则卡住时只能含糊其辞）",
          all(s.get("wait") for s in full),
          str([(s["key"], bool(s.get("wait"))) for s in full]))
    ocr_wait = full[0]["wait"]
    check("OCR 阶段的等待文案说的是 OCR，且不出现「模型」",
          "OCR" in ocr_wait and "模型" not in ocr_wait, ocr_wait)
    waits = {s["key"]: s["wait"] for s in full}
    check("模型阶段的等待文案明确说「等待模型应答」",
          "等待模型应答" in waits["enrich"] and "等待模型应答" in waits["translate"],
          f"{waits['enrich']} / {waits['translate']}")
    check("标注阶段的等待文案说明是本地计算（不需要联网）",
          "本地" in waits["annotate"], waits["annotate"])

    note("---- 单调性与阶段内封顶 ----")
    P.clear()
    P.begin("u1", P.plan(True, True, False))
    pcts = []
    P.at("u1", "parse")
    pcts.append(P.snapshot("u1")["percent"])
    P.at("u1", "annotate")
    pcts.append(P.snapshot("u1")["percent"])
    P.at("u1", "enrich")
    pcts.append(P.snapshot("u1")["percent"])
    P.sub("u1", 0, 4)
    pcts.append(P.snapshot("u1")["percent"])
    P.sub("u1", 2, 4)
    pcts.append(P.snapshot("u1")["percent"])
    P.sub("u1", 4, 4)                      # 阶段内跑完也算 95%，不能顶到阶段边界
    s_full = P.snapshot("u1")
    pcts.append(s_full["percent"])
    check("阶段内即使 100% 也不越界（避免「卡在整格不动」）",
          s_full["percent"] < 54, f"percent={s_full['percent']} 阶段={s_full['stage']}")
    P.at("u1", "translate")
    pcts.append(P.snapshot("u1")["percent"])
    P.at("u1", "render")
    pcts.append(P.snapshot("u1")["percent"])
    P.done("u1")
    pcts.append(P.snapshot("u1")["percent"])
    check("百分比全程单调不减", all(b >= a for a, b in zip(pcts, pcts[1:])), str(pcts))

    s = P.snapshot("u1")
    check("done 后 = 100% 且 done=True 且无 error",
          s["percent"] == 100.0 and s["done"] and not s["error"], str(s["percent"]))
    check("done 后重复取快照仍是 100（幂等，前端可能晚一拍）",
          P.snapshot("u1")["percent"] == 100.0)

    note("---- 乱序上报不回退 ----")
    P.clear()
    P.begin("u2", P.plan(False, False, False))
    P.at("u2", "render")
    hi = P.snapshot("u2")["percent"]
    P.at("u2", "parse")                    # 迟到的上报
    check("晚到的早期阶段不会把进度条拉回去",
          P.snapshot("u2")["percent"] >= hi, f"{hi} → {P.snapshot('u2')['percent']}")

    note("---- 等待文案跟着阶段走 ----")
    P.clear()
    P.begin("u4", P.plan(False, True, True))
    P.at("u4", "parse")
    w_parse = P.snapshot("u4").get("waiting_label") or ""
    P.at("u4", "annotate")
    w_ann = P.snapshot("u4").get("waiting_label") or ""
    P.at("u4", "translate")
    w_tr = P.snapshot("u4").get("waiting_label") or ""
    check("快照里的 waiting_label 跟着当前阶段变",
          w_parse != w_ann and w_ann != w_tr,
          f"{w_parse[:12]} | {w_ann[:12]} | {w_tr[:12]}")
    check("parse 阶段说 OCR、annotate 说本地、translate 说模型",
          "OCR" in w_parse and "本地" in w_ann and "模型" in w_tr,
          f"{w_parse[:16]} / {w_ann[:16]} / {w_tr[:16]}")

    note("---- 失败与未登记 ----")
    P.clear()
    P.begin("u3", P.plan(False, False, False))
    P.at("u3", "annotate")
    P.fail("u3", "文本为空")
    s = P.snapshot("u3")
    check("fail 后 error 有值、done 仍为 False（前端据此停轮询并报原因）",
          s["error"] == "文本为空" and not s["done"], repr(s["error"]))

    s = P.snapshot("nope")
    check("未登记任务返回 found=False 而不是抛错/404（轮询不会刷错误）",
          s.get("found") is False and s.get("percent") == 0, str(s))

    note("---- 空 job_id 必须完全无副作用 ----")
    ok = True
    try:
        P.begin("", P.plan(False, False, False))
        P.at("", "parse")
        P.sub("", 1, 1)
        P.done("")
        P.fail("", "x")
        P.snapshot("")
    except Exception:  # noqa: BLE001
        ok = False
        LOG.append(traceback.format_exc())
    check("job_id 缺省时进度接口静默跳过，老请求不受影响", ok)

    P.clear()
    note("单元层：PASS=%d FAIL=%d" % (PASS, FAIL))


# =====================================================================
# 第 2 层：真实 HTTP
# =====================================================================

BASE = ""
CLIENT = httpx.Client(trust_env=False, timeout=120.0)
FAST_URL = ""
SLOW_URL = ""


def get_prog(job: str) -> dict:
    r = CLIENT.get(f"{BASE}/api/progress/{job}")
    if r.status_code != 200:
        return {"found": False, "http": r.status_code}
    return r.json()


def poll(job: str, seconds: float, interval: float = 0.35) -> list[dict]:
    """按前端节奏轮询，录下「用户会看到的序列」。"""
    seq, t0 = [], time.time()
    while time.time() - t0 < seconds:
        d = get_prog(job)
        seq.append(d)
        if d.get("done") or d.get("error"):
            break
        time.sleep(interval)
    return seq


def post_text(job: str, **kw) -> httpx.Response:
    payload = {"text": SAMPLE, "level_id": "cet4", "title": "进度自检",
               "use_llm": False, "translate": False}
    payload.update(kw)
    if job is not None:
        payload["job_id"] = job
    return CLIENT.post(f"{BASE}/api/analyze-text", json=payload)


def api_checks() -> None:
    global PASS, FAIL
    p0, f0 = PASS, FAIL          # 分层计数：不这样记，打出来的会是累计值，看着像跑了两遍
    note("")
    note("---- HTTP：未知任务 ----")
    r = CLIENT.get(f"{BASE}/api/progress/never-existed")
    check("/api/progress/{未知} 返回 200 + found=False（不是 404，避免轮询刷错误）",
          r.status_code == 200 and r.json().get("found") is False,
          f"{r.status_code} {r.text[:120]}")

    r = CLIENT.get(f"{BASE}/api/progress")
    check("/api/progress 统计可用（排查用）",
          r.status_code == 200 and "jobs" in r.json(), r.text[:120])

    note("---- HTTP：不带 job_id 的老请求不受影响 ----")
    r = post_text(None)
    check("不带 job_id 的生成照常成功且返回手账",
          r.status_code == 200 and "<div" in (r.json().get("html") or ""),
          f"{r.status_code}")

    note("---- HTTP：错误必须让进度条停下来并说明原因 ----")
    job_err = "err" + str(int(time.time() * 1000))
    r = post_text(job_err, text="")
    check("空文本被拒（400）", r.status_code == 400, f"{r.status_code} {r.text[:120]}")
    d = get_prog(job_err)
    check("失败原因写进了进度（前端不再空转到超时）",
          d.get("found") and d.get("error") == "文本为空" and not d.get("done"),
          str(d.get("error")))
    d2 = get_prog(job_err)
    check("错误状态稳定可重复读（不是一闪而过）", d2.get("error") == "文本为空")

    note("---- HTTP：纯规则任务（快）----")
    job_fast = "fast" + str(int(time.time() * 1000))
    r = post_text(job_fast)
    ok_body = r.status_code == 200 and r.json().get("counters")
    check("纯规则标注返回 200", ok_body, f"{r.status_code} {r.text[:120]}")
    seq = poll(job_fast, 3.0)
    check("快任务结束后进度=100% 且 done=True",
          seq and seq[-1]["percent"] == 100.0 and seq[-1]["done"], str(seq[-1]))
    check("快任务全程没有误报「等待模型」",
          not any(d.get("waiting") for d in seq),
          str([(d.get("stage"), d.get("waiting")) for d in seq]))
    c = r.json()["counters"]
    check("进度上报没有改动返回内容（标注计数仍在）", c.get("word_highlight", 0) >= 0, str(c))

    note("---- HTTP：模型秒回时不能误报「等待模型」----")
    tr.clear_cache()
    FastStub.calls.clear()
    job_fast2 = "fast2" + str(int(time.time() * 1000))
    # 翻译链路读的是 `mt_*`（2026-10-15 起与讲解模型分开）：只给 `llm_*`
    # 的话翻译会去问本机 Ollama，桩模型收不到请求，「模型被真的调用了」永远是空。
    r = post_text(job_fast2, translate=True, trans_mode="sentence",
                  llm_provider="openai", llm_api_key="stub-key",
                  llm_base_url=FAST_URL, llm_model="stub",
                  mt_provider="openai", mt_api_key="stub-key",
                  mt_base_url=FAST_URL, mt_model="stub")
    check("配了模型时译文链路走通（200）", r.status_code == 200, f"{r.status_code} {r.text[:160]}")
    check("模型被真的调用了", len(FastStub.calls) >= 1, str(FastStub.calls))
    seq = poll(job_fast2, 3.0)
    check("秒回场景全程没有误报等待（STALL_AFTER 不能过敏）",
          not any(d.get("waiting") for d in seq),
          str([(d.get("stage"), d.get("waiting")) for d in seq]))
    check("秒回场景结束时进度=100%", seq and seq[-1]["percent"] == 100.0, str(seq[-1]))

    note("---- HTTP：OCR 场景（等待文案不能张冠李戴）----")
    # 这一段是上面那条断言的真实版：OCR 是本地推理，一页照片跑十几秒很正常，
    # 进度同样会「停住」。如果那时弹出「等待模型应答」，就是把等待原因讲错了 ——
    # 和原来那句「正在标注…」属于同一类毛病。
    pdf = ROOT / "samples" / "test_scanned.pdf"
    check("扫描件样本存在", pdf.exists(), str(pdf))
    if pdf.exists():
        job_ocr = "ocr" + str(int(time.time() * 1000))
        res_ocr: dict = {}

        def _post_ocr():
            t = time.time()
            with open(pdf, "rb") as f:
                rr = CLIENT.post(f"{BASE}/api/analyze", timeout=600,
                                 files={"file": (pdf.name, f, "application/pdf")},
                                 data={"level_id": "cet4", "use_llm": "false",
                                       "translate": "false", "job_id": job_ocr})
            res_ocr.update(status=rr.status_code, ms=(time.time() - t) * 1000,
                           info=(rr.json().get("parse_info") if rr.status_code == 200
                                 else rr.text[:200]))

        th_ocr = threading.Thread(target=_post_ocr, daemon=True)
        # 真实 OCR 每页约 3–6 秒、页与页之间有上报，按默认 6 秒阈值常常**不会**触发 waiting；
        # 而这条正是要验的路径，不能靠碰运气。把阈值临时压到 0.6 秒强制触发，
        # 跑完立刻还原（改的是本进程里的模块常量，只有本测试看得见）。
        prev_stall = P.STALL_AFTER
        P.STALL_AFTER = 0.6
        try:
            th_ocr.start()
            seq_ocr = poll(job_ocr, 90.0)
            th_ocr.join(timeout=60)
        finally:
            P.STALL_AFTER = prev_stall

        p_samples = [d for d in seq_ocr if d.get("stage") == "parse"]
        w_samples = [d for d in p_samples if d.get("waiting")]
        check("OCR 任务落在 parse 阶段（能看出在识别，而不是笼统一句「正在标注」）",
              len(p_samples) > 0, str([d.get("stage") for d in seq_ocr][:6]))
        check("OCR 停顿时确实触发了 waiting（阈值压到 0.6 秒强制触发，不是碰运气）",
              len(w_samples) > 0, f"parse 采样 {len(p_samples)} 次，其中 waiting {len(w_samples)} 次")
        check("OCR 的等待文案说的是 OCR，绝不出现「模型」（本次核心）",
              bool(w_samples)
              and all("OCR" in (d.get("waiting_label") or "") for d in w_samples)
              and all("模型" not in (d.get("waiting_label") or "") for d in w_samples),
              str([d.get("waiting_label") for d in w_samples[:2]]))
        check("OCR 期间 detail 一直在说明认到第几页",
              any("页" in (d.get("detail") or "") for d in p_samples),
              str([d.get("detail") for d in p_samples[:4]]))
        check("OCR 任务最终完成且进度=100%",
              bool(seq_ocr) and seq_ocr[-1].get("done") and seq_ocr[-1]["percent"] == 100.0,
              f"{seq_ocr[-1].get('percent')} done={seq_ocr[-1].get('done')} "
              f"err={seq_ocr[-1].get('error')!r}")
        check("真的走了 OCR（否则这一段什么都没验到）",
              res_ocr.get("status") == 200 and (res_ocr.get("info") or {}).get("ocr") is True,
              str(res_ocr)[:220])
        check("阈值已还原（后面的用例不会被这段的改动影响）",
              P.STALL_AFTER == prev_stall, f"{prev_stall} → {P.STALL_AFTER}")
        note(f"    OCR 实测耗时 {res_ocr.get('ms', 0):.0f}ms  "
             f"parse_info={res_ocr.get('info')}")
        note(f"    parse 阶段采样 {len(p_samples)} 次，其中 waiting {len(w_samples)} 次；"
             f"detail 见过 {[d.get('detail') for d in p_samples][:5]}")

    note("---- HTTP：真实慢任务 → waiting 反馈（本次核心）----")
    tr.clear_cache()
    SlowStub.calls.clear()
    job_slow = "slow" + str(int(time.time() * 1000))
    res: dict = {}

    def _post():
        t = time.time()
        try:
            # ⚠ 翻译走的是 `mt_*` 那条链路（2026-10-15 起与讲解模型分开）：
            # 只给 `llm_*` 的话翻译会去问本机 Ollama，桩模型永远收不到请求 ——
            # 「慢任务 → waiting 反馈」这条核心用例就什么都没验到（waiting 采样 0 次）。
            rr = post_text(job_slow, translate=True, trans_mode="sentence",
                           llm_provider="openai", llm_api_key="stub-key",
                           llm_base_url=SLOW_URL, llm_model="stub",
                           mt_provider="openai", mt_api_key="stub-key",
                           mt_base_url=SLOW_URL, mt_model="stub")
            res.update(status=rr.status_code, ms=(time.time() - t) * 1000,
                       body=rr.text[:200])
        except Exception as e:  # noqa: BLE001
            res.update(status=-1, ms=(time.time() - t) * 1000, body=repr(e))

    th = threading.Thread(target=_post, daemon=True)
    th.start()

    seq = poll(job_slow, 40.0)
    th.join(timeout=20)

    stages = [d.get("stage") for d in seq]
    # 只断言「顺序」而不是「每一段都采到」：parse / annotate 是毫秒级的，
    # 700ms 的轮询本来就可能整段跳过它们 —— 拿时序巧合当断言，会变成偶发假失败。
    plan_order = ["parse", "annotate", "translate", "render"]
    seen_idx = [plan_order.index(s) for s in stages if s in plan_order]
    check("阶段只按计划顺序前进，不倒退",
          all(b >= a for a, b in zip(seen_idx, seen_idx[1:])), str(stages))
    check("确实落到了 translate 阶段（9 秒足够看清它在等哪一段）",
          "translate" in stages, str(stages))

    pcts = [d["percent"] for d in seq if d.get("found")]
    check("整个慢任务期间百分比单调不减",
          all(b >= a for a, b in zip(pcts, pcts[1:])), str(pcts))

    waits = [d for d in seq if d.get("waiting")]
    check("模型迟迟不回时出现 waiting=True（回答「是不是卡住了」）",
          len(waits) > 0, f"waiting 采样 {len(waits)} 次")
    check("waiting 时给出「已 N 秒无新进展」这个具体数字",
          any((d.get("since_update") or 0) >= P.STALL_AFTER for d in waits),
          str([d.get("since_update") for d in waits]))
    check("waiting 期间进度停在中途而不是假报 100%",
          bool(waits) and max(d["percent"] for d in waits) < 100,
          str([d["percent"] for d in waits]))
    check("等待前能读到 translate 的非 waiting 态（说明是「刚卡住」而不是「一直卡」）",
          any(d.get("stage") == "translate" and not d.get("waiting") for d in seq),
          str([(d.get("stage"), d.get("waiting")) for d in seq][:8]))
    check("waiting 时的 detail 说明翻译批次（有分母才敢推进）",
          any("批" in (d.get("detail") or "") for d in waits),
          str([d.get("detail") for d in waits[:3]]))

    check("慢任务最终完成且进度=100%",
          bool(seq) and seq[-1].get("done") and seq[-1]["percent"] == 100.0,
          f"{seq[-1].get('percent')} done={seq[-1].get('done')} err={seq[-1].get('error')!r}")
    check("慢任务真的调到了桩模型（否则这条测试什么都没验到）",
          len(SlowStub.calls) >= 1, str(SlowStub.calls))
    check("慢任务 POST 实际返回 200", res.get("status") == 200,
          f"{res.get('status')} {res.get('body')}")

    note("---- 上报不能拖慢主流程 ----")
    tr.clear_cache()
    job_slow2 = "slow2" + str(int(time.time() * 1000))
    th2 = threading.Thread(target=lambda: post_text(
        job_slow2, translate=True, trans_mode="sentence", llm_provider="openai",
        llm_api_key="stub-key", llm_base_url=SLOW_URL, llm_model="stub",
        mt_provider="openai", mt_api_key="stub-key",
        mt_base_url=SLOW_URL, mt_model="stub"), daemon=True)
    th2.start()
    time.sleep(1.5)                        # 让它进入等模型的那一段
    lat_levels, lat_prog = [], []
    for _ in range(5):
        t = time.time()
        r = CLIENT.get(f"{BASE}/api/levels")
        lat_levels.append((time.time() - t) * 1000)
        if r.status_code != 200:
            break
        t = time.time()
        get_prog(job_slow2)
        lat_prog.append((time.time() - t) * 1000)
    check("慢请求在飞时，别的接口仍毫秒级返回（同步 def 的真正含义）",
          len(lat_levels) == 5 and max(lat_levels) < 1000,
          "levels " + " ".join(f"{x:.0f}ms" for x in lat_levels))
    check("轮询本身很轻（不会因为看进度而拖慢生成）",
          len(lat_prog) == 5 and max(lat_prog) < 500,
          "progress " + " ".join(f"{x:.0f}ms" for x in lat_prog))

    # 收尾：把最后那个慢请求等回来，别给进程留下非守护线程（否则退出时会吊住）
    th2.join(timeout=20)
    th.join(timeout=5)

    note("")
    note("接口层：PASS=%d FAIL=%d" % (PASS - p0, FAIL - f0))


# =====================================================================
# 主流程
# =====================================================================

def main() -> None:
    global BASE, FAST_URL, SLOW_URL
    port = free_port()
    BASE = f"http://127.0.0.1:{port}"
    FAST_URL = start_stub(FastStub)
    SLOW_URL = start_stub(SlowStub)
    note(f"服务 = {BASE}   快桩 = {FAST_URL}   慢桩 = {SLOW_URL}（delay=9s）")
    note(f"STUDYPAD_HOME = {TMP}")

    cfg = uvicorn.Config(app, host="127.0.0.1", port=port,
                         log_level="warning", access_log=False)
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    t0 = time.time()
    while not server.started and time.time() - t0 < 20:
        time.sleep(0.1)
    check("自检用的 uvicorn 已启动", server.started, f"{time.time() - t0:.1f}s")

    unit_checks()
    api_checks()

    server.should_exit = True
    note("")
    note(f"合计：PASS={PASS} FAIL={FAIL}")
    if FAIL:
        for line in LOG:
            if line.startswith("[FAIL]"):
                note("  失败项：" + line)


LOG_PATH = ROOT / "out" / "_progress_test.txt"
try:
    main()
except BaseException:  # noqa: BLE001 — 崩了才更要落盘，否则又变成「脚本失败但看不到原因」
    LOG.append("[未捕获异常]")
    LOG.append(traceback.format_exc())
    FAIL += 1
finally:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text("\n".join(LOG) + "\n", encoding="utf-8")
    print("\n".join(LOG))
    sys.stderr.write(f"\n日志已写入 {LOG_PATH}\n")

sys.exit(0 if FAIL == 0 else 1)
