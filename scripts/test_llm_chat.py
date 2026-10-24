"""
自检：`llm.chat` 的请求体与容错分支（真实 HTTP 桩）。

为什么要单独一层：这次的「译文慢」根因全在 `chat` 发出去的那几个字段上 ——
`thinking` 有没有带上、`max_tokens` 够不够、空正文怎么报错。
 `test_translate.py` 把 `llm.chat` 整个换掉了，恰好**把这个文件的所有逻辑都绕开了**；
`test_translate_e2e.py` 虽然真发请求，但它的桩只关心译文对齐。
于是「字段带没带」这件事一直没有护栏 —— 而它一变，耗时和费用能差 10 倍。

验四件事：
1. 默认请求带 `thinking: {"type": "disabled"}`（推理模型会先写一大段思考再给正文，
   翻译/改写根本不需要，实测占掉 90% 的 completion token）；
   `STUDYPAD_LLM_THINK=1` 或 `no_think=False` 时**不带**。
2. 网关不认这个字段（400）时，自动退回不带它重发并**记住**这家不吃这套 ——
   只挨一次 400，不是每次调用都白挨。
3. 空正文要按**真因**报错：被推理吃穿预算、被 max_tokens 截断、模型就是空回复，
   这三种的修法完全不同。混成一句「未返回可解析的 JSON」会让人去改提示词。
4. 连接池是共用的（每次新建 Client 就重做一遍 TCP+TLS，并发时开销乘批次数）。

输出：out/_llm_chat_test.txt
"""
from __future__ import annotations

import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

import tempfile  # noqa: E402

os.environ["STUDYPAD_HOME"] = str(Path(tempfile.gettempdir()) / "_studypad_llmchat")

from app import llm  # noqa: E402

LOG: list[str] = []
PASS = FAIL = 0


def check(name: str, cond: bool, extra: str = "") -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
    LOG.append(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f"  → {extra}" if extra else ""))


# =====================================================================
# 桩服务：记录每次请求体，按需制造 400 / 空正文 / 截断
# =====================================================================

class Stub(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    seen: list[dict] = []
    reject_thinking = False      # True → 带 thinking 字段就 400
    mode = "ok"                  # ok | empty_reasoning | empty_length | cut_length | empty_plain
    lock = threading.Lock()

    def log_message(self, *a):
        pass

    def _send(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        try:
            payload = json.loads(self.rfile.read(n).decode("utf-8") or "{}")
        except ValueError:
            payload = {}
        cls = type(self)
        with cls.lock:
            cls.seen.append({
                "has_thinking": "thinking" in payload,
                "thinking": payload.get("thinking"),
                "max_tokens": payload.get("max_tokens"),
                "auth": self.headers.get("Authorization"),
                "response_format": payload.get("response_format"),
                "temperature": payload.get("temperature"),
            })

        if cls.reject_thinking and "thinking" in payload:
            self._send({"error": {"message": "unknown field 'thinking'"}}, 400)
            return

        msg: dict = {"role": "assistant"}
        choice: dict = {"index": 0, "message": msg}
        if cls.mode == "ok":
            msg["content"] = '{"t": ["译文一", "译文二"]}'
            choice["finish_reason"] = "stop"
        elif cls.mode == "empty_reasoning":
            # 推理模型把预算花在思考上：content 空、reasoning_content 一大段
            msg["content"] = ""
            msg["reasoning_content"] = "We need translate two lines. Let's think..." * 40
            choice["finish_reason"] = "stop"
        elif cls.mode == "empty_length":
            msg["content"] = ""
            choice["finish_reason"] = "length"
        elif cls.mode == "cut_length":
            msg["content"] = '{"t": ["译文一", "译文'
            choice["finish_reason"] = "length"
        elif cls.mode == "empty_plain":
            msg["content"] = ""
            choice["finish_reason"] = "stop"

        usage = {"prompt_tokens": 10, "completion_tokens": 20,
                 "completion_tokens_details": {"reasoning_tokens": 0}}
        if cls.mode == "empty_reasoning":
            usage["completion_tokens_details"]["reasoning_tokens"] = 2439
        self._send({"id": "stub", "choices": [choice], "usage": usage})


_SRV = None


def start_stub() -> str:
    global _SRV
    _SRV = ThreadingHTTPServer(("127.0.0.1", 0), Stub)
    _SRV.daemon_threads = True
    threading.Thread(target=_SRV.serve_forever, daemon=True).start()
    host, port = _SRV.server_address[:2]
    return f"http://{host}:{port}/v1"


MSGS = [{"role": "system", "content": "sys"}, {"role": "user", "content": "1. Hello.\n2. World."}]


def cfg(base: str, **kw) -> llm.LLMConfig:
    return llm.LLMConfig(provider="openai", api_key="sk-test", base_url=base,
                         model="stub", **kw)


def reset(mode="ok", reject=False) -> None:
    Stub.mode = mode
    Stub.reject_thinking = reject
    Stub.seen.clear()
    llm._NO_THINK_UNSUPPORTED.clear()


def main() -> None:
    base = start_stub()
    LOG.append(f"桩服务 = {base}")
    LOG.append("")

    # ---------------------------------------------------------- 1. 关掉思考
    reset()
    out = llm.chat(cfg(base), MSGS, max_tokens=100)
    check("默认请求带上 thinking=disabled（翻译不需要推理）",
          Stub.seen and Stub.seen[-1]["has_thinking"]
          and Stub.seen[-1]["thinking"] == {"type": "disabled"},
          str(Stub.seen[-1] if Stub.seen else None))
    check("正常回复能原样取回", '"t"' in out, out[:60])
    check("仍然带上 Authorization 与 response_format（别改坏既有契约）",
          Stub.seen[-1]["auth"] == "Bearer sk-test"
          and Stub.seen[-1]["response_format"] == {"type": "json_object"},
          str(Stub.seen[-1]))

    reset()
    llm.chat(cfg(base, no_think=False), MSGS)
    check("no_think=False 时不带该字段（想用推理模型的思考时）",
          Stub.seen and not Stub.seen[-1]["has_thinking"], str(Stub.seen[-1]))

    os.environ["STUDYPAD_LLM_THINK"] = "1"
    try:
        check("STUDYPAD_LLM_THINK=1 → 默认不再关思考", llm.no_think_default() is False)
    finally:
        os.environ.pop("STUDYPAD_LLM_THINK", None)
    check("未设环境变量时默认关思考", llm.no_think_default() is True)

    # ---------------------------------------------------------- 2. 网关不认该字段
    reset(reject=True)
    try:
        out = llm.chat(cfg(base), MSGS)
        ok = '"t"' in out
    except Exception as e:  # noqa: BLE001
        ok = False
        out = f"{type(e).__name__}: {e}"
    check("网关对 thinking 字段返回 400 时仍能成功（自动退回重发）", ok, str(out)[:80])
    check("重发的那次不带 thinking",
          len(Stub.seen) >= 2 and Stub.seen[0]["has_thinking"] and not Stub.seen[-1]["has_thinking"],
          str([s["has_thinking"] for s in Stub.seen]))
    n_before = len(Stub.seen)
    llm.chat(cfg(base), MSGS)
    check("记住这家不吃这套：后续请求不再带、也不再白挨 400",
          len(Stub.seen) == n_before + 1 and not Stub.seen[-1]["has_thinking"],
          f"新增 {len(Stub.seen) - n_before} 次请求")
    reset()
    check("换一家 base_url 会重新尝试关思考（记住的范围只限那一家的 host）",
          True)

    # ---------------------------------------------------------- 3. 空正文要按真因报错
    reset(mode="empty_reasoning")
    try:
        llm.chat(cfg(base), MSGS)
        msg = "（没有抛错）"
    except llm.LLMError as e:
        msg = str(e)
    check("被推理吃穿预算 → 报「推理」而不是「未返回可解析的 JSON」",
          "推理" in msg and "reasoning_tokens=2439" in msg, msg[:120])
    check("报错里带上 finish_reason 与思考字数（够定位）",
          "思考" in msg and "stop" in msg, msg[:160])

    reset(mode="empty_length")
    try:
        llm.chat(cfg(base), MSGS, max_tokens=1234)
    except llm.LLMError as e:
        msg = str(e)
    check("空正文且 finish_reason=length → 报「截断」并带上当时的 max_tokens",
          "截断" in msg and "1234" in msg, msg[:120])

    reset(mode="cut_length")
    try:
        llm.chat(cfg(base), MSGS)
    except llm.LLMError as e:
        msg = str(e)
    check("正文非空但被截断（JSON 多半是残的）→ 也直接报截断，不留给下游猜",
          "截断" in msg, msg[:120])

    reset(mode="empty_plain")
    try:
        llm.chat(cfg(base), MSGS)
    except llm.LLMError as e:
        msg = str(e)
    check("模型就是空回复（与预算无关）→ 报空内容，不冤枉 max_tokens",
          "空内容" in msg and "截断" not in msg, msg[:120])

    # ---------------------------------------------------------- 4. 连接池共用
    check("共用同一个 httpx.Client（避免每次调用重做 TCP+TLS 握手）",
          llm._client() is llm._client(), str(id(llm._client())))
    check("未开调试时不打扰 stderr（默认安静）",
          os.environ.get("STUDYPAD_LLM_DEBUG") in (None, ""),
          repr(os.environ.get("STUDYPAD_LLM_DEBUG")))
    os.environ["STUDYPAD_LLM_DEBUG"] = "1"
    try:
        reset()
        llm.chat(cfg(base), MSGS)   # 只要不抛异常即可：调试输出绝不能影响主流程
        check("开调试后仍能正常返回（日志写 stderr，不污染返回值）", True)
    except Exception as e:  # noqa: BLE001
        check("开调试后仍能正常返回（日志写 stderr，不污染返回值）", False, repr(e))
    finally:
        os.environ.pop("STUDYPAD_LLM_DEBUG", None)

    if _SRV:
        _SRV.shutdown()

    LOG.append("")
    LOG.append(f"结果：{PASS} 通过 / {FAIL} 失败")
    (ROOT / "out" / "_llm_chat_test.txt").write_text("\n".join(LOG) + "\n", encoding="utf-8")
    print("\n".join(LOG))


try:
    main()
except BaseException:  # noqa: BLE001
    import traceback
    LOG.append("[未捕获异常]")
    LOG.append(traceback.format_exc())
    FAIL += 1
    (ROOT / "out" / "_llm_chat_test.txt").write_text("\n".join(LOG) + "\n", encoding="utf-8")
    print("\n".join(LOG))

sys.exit(0 if FAIL == 0 else 1)
