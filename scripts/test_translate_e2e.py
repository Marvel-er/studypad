"""
端到端（真实 HTTP）验证中文译文：桩模型 + 真实网络请求。

为什么还要单独做这一层 —— 前面两层都有盲区：
  · `test_translate.py` 用 monkeypatch 换掉 `llm.chat`，**HTTP 根本没发生**；
  · `test_translate_api.py` 同样 monkeypatch，只验了「应用内部怎么组织译文」。
于是这些只在真实请求里才暴露的问题，前两层一个都拦不住：
  · 请求体里 `response_format` / `temperature` / `max_tokens` 有没有带上；
  · `Authorization: Bearer <key>` 有没有带上；
  · 模型把 JSON 包在 ```json 围栏里（很常见）时能不能解析出来；
  · 缓存到底有没有真的省下一次网络往返。

所以这里起一个**真的监听端口**的 OpenAI 兼容桩服务，
让 httpx 真发一次请求过去，再断言桩那边收到了什么。

桩服务绑 127.0.0.1 上的随机空闲端口，配置写在临时 STUDYPAD_HOME 里，
不碰用户真实的 ~/.studypad/settings.json。
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

TMP = Path(tempfile.gettempdir()) / "_studypad_transe2e"
os.environ["STUDYPAD_HOME"] = str(TMP)

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
# 桩模型：真的监听端口，真的走 HTTP
# =====================================================================

SEEN: list[dict] = []


class Stub(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

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
            payload = json.loads(raw)
        except ValueError:
            payload = {}
        msgs = payload.get("messages") or []
        user = msgs[-1].get("content", "") if msgs else ""
        sents = re.findall(r"^\d+\.\s?(.*)$", user, re.M)

        SEEN.append({
            "path": self.path,
            "auth": self.headers.get("Authorization"),
            "response_format": payload.get("response_format"),
            "temperature": payload.get("temperature"),
            "max_tokens": payload.get("max_tokens"),
            "model": payload.get("model"),
            "n_sent": len(sents),
            "system": msgs[0].get("content", "")[:80] if msgs else "",
        })

        # 刻意包一层 ```json 围栏：这是真实模型很爱干的事，
        # 桩要复现它，否则解析容错这段代码永远没被真实请求检验过。
        content = ("```json\n"
                   + json.dumps({"t": [f"中译{s[:24]}" for s in sents]}, ensure_ascii=False)
                   + "\n```")
        self._json({"id": "stub", "object": "chat.completion",
                    "choices": [{"index": 0, "finish_reason": "stop",
                                 "message": {"role": "assistant", "content": content}}],
                    "usage": {"prompt_tokens": 1, "completion_tokens": 1}})


_SRV: ThreadingHTTPServer | None = None


def start_stub() -> tuple[ThreadingHTTPServer, str]:
    """绑 127.0.0.1 的随机空闲端口，避免和别的服务抢端口。"""
    global _SRV
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Stub)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    _SRV = srv
    host, port = srv.server_address[:2]
    return srv, f"http://{host}:{port}/v1"


SAMPLE = (
    "Although the committee had been informed of the potential risks, it nevertheless "
    "decided to proceed with the experiment. The results, which were published last month, "
    "suggest that the hypothesis is worth pursuing.\n\n"
    "Not only did the team overcome the technical obstacles, but it also managed to reduce "
    "the overall cost. This achievement demonstrates the importance of persistent effort."
)


def main() -> None:
    srv, base = start_stub()

    from fastapi.testclient import TestClient

    from app import settings, translate
    from app.main import app

    TMP.mkdir(parents=True, exist_ok=True)
    try:
        settings.clear()
    except Exception:  # noqa: BLE001
        pass

    c = TestClient(app)

    # ---- 配好桩模型（写临时目录，不碰真实配置） ----
    # ⚠ 2026-10-15 起翻译与讲解是**两套模型**：只配 `provider/base_url/model` 配的是
    # 讲解模型，翻译仍走本机 Ollama 的 hy-mt2:1.8b —— 桩服务器一个请求都收不到，
    # 这条测试就白跑了（表现是「桩模型真的收到了 HTTP 请求 → 0」）。
    # 翻译真正走的链路在 `mt_*` 上，所以桩模型必须配到那边。
    settings.save({"provider": "custom", "base_url": base, "model": "stub-model",
                   "api_key": "sk-stub-1234", "enabled": False,
                   "mt_enabled": True, "mt_provider": "custom", "mt_base_url": base,
                   "mt_model": "stub-model", "mt_api_key": "sk-stub-1234"})
    st = c.get("/api/translate/status").json()
    check("接通桩模型后 status.available=True", st["available"] is True, str(st["available"]))
    check("status 不泄漏 Key", "sk-stub-1234" not in json.dumps(st, ensure_ascii=False))
    check("status 报告 model 与 provider",
          st["model"] == "stub-model" and st["provider"] == "custom",
          f'{st["provider"]}/{st["model"]}')

    # ---- 真发一次翻译请求 ----
    SEEN.clear()
    translate.clear_cache()
    r = c.post("/api/analyze-text", json={
        "text": SAMPLE, "level_id": "cet4", "title": "真实链路", "use_llm": False,
        "translate": True, "trans_mode": "sentence"})
    check("端到端请求 → 200", r.status_code == 200, str(r.status_code))
    hb = r.json()

    check("★ 桩模型真的收到了 HTTP 请求", len(SEEN) >= 1, str(len(SEEN)))
    # 探活请求（「你还活着吗」那个 1-token 调用）和翻译请求打的是**同一个端点**，
    # 桩服务器两条都会收到 —— 取样与计数必须只认翻译那一条：
    # 否则 `SEEN[0]` 拿到的是探活（system 是「reply with exactly: ok」、n_sent=0），
    # 后面几条断言全歪（表现为「请求声明 JSON 模式 → None」「合批 → 0 句」）。
    TR = [s for s in SEEN if "translator" in (s.get("system") or "").lower()]
    check("★ 其中有一条是真正的翻译请求（不是探活）", len(TR) == 1,
          f"SEEN={len(SEEN)}，翻译={len(TR)}")
    if not TR:
        return
    got = TR[0]
    check("请求打到 /v1/chat/completions", got["path"] == "/v1/chat/completions", got["path"])
    check("★ 请求带 Authorization: Bearer <key>",
          got["auth"] == "Bearer sk-stub-1234", str(got["auth"]))
    check("★ 请求声明 JSON 模式（否则模型可能不回 JSON）",
          got["response_format"] == {"type": "json_object"}, str(got["response_format"]))
    check("请求带 temperature 且为低值", isinstance(got["temperature"], (int, float))
          and got["temperature"] <= 0.3, str(got["temperature"]))
    check("请求带 max_tokens", isinstance(got["max_tokens"], int) and got["max_tokens"] > 0,
          str(got["max_tokens"]))
    check("请求用的 model 来自配置", got["model"] == "stub-model", str(got["model"]))
    check("system 提示是翻译角色的提示词", "translator" in got["system"].lower(),
          got["system"])
    check("一次请求带上了全部 4 句（合批生效）", got["n_sent"] == 4, str(got["n_sent"]))

    # ---- 围栏 JSON 解析 + 逐句对齐 ----
    tr = hb.get("translations") or {}
    check("trans_mode=sentence", hb["trans_mode"] == "sentence", hb["trans_mode"])
    check("两段都拿到译文", len(tr) == 2, str(list(tr.keys())))
    pairs = [s for t in tr.values() for s in t["sentences"]]
    check("译文共 4 句", len(pairs) == 4, str(len(pairs)))
    bad = [s for s in pairs if s["zh"] != ("中译" + s["en"][:24]).strip()]
    check("★ ```json 围栏被正确解析，且逐句对齐无错位", not bad, str(bad[:2]))
    check("★ 译文渲染进了 HTML",
          "中译" in hb["html"] and 'class="tr-pair"' in hb["html"])

    # ---- 缓存省下真实往返 ----
    r2 = c.post("/api/analyze-text", json={
        "text": SAMPLE, "level_id": "cet4", "title": "真实链路", "use_llm": False,
        "translate": True, "trans_mode": "sentence"})
    # 只数翻译请求：探活是另一条（同端点，见上）
    check("★ 重发没有新的翻译请求（缓存生效）",
          len([s for s in SEEN if "translator" in (s.get("system") or "").lower()]) == 1,
          f"SEEN={len(SEEN)}")
    check("重发仍得到完整译文",
          len(r2.json().get("translations") or {}) == 2
          and "复用缓存" in r2.json().get("trans_note", ""),
          r2.json().get("trans_note", "")[:70])

    # ---- 换等级复用同一份译文（缓存按句子哈希，不含等级） ----
    r3 = c.post("/api/analyze-text", json={
        "text": SAMPLE, "level_id": "ielts", "title": "真实链路", "use_llm": False,
        "translate": True, "trans_mode": "paragraph"})
    check("★ 换等级 + 换版式仍是 0 次新翻译请求",
          len([s for s in SEEN if "translator" in (s.get("system") or "").lower()]) == 1,
          f"SEEN={len(SEEN)}")
    check("换版式后渲染成整段附译",
          r3.json()["trans_mode"] == "paragraph"
          and 'class="tr-zh"' in r3.json()["html"], r3.json()["trans_mode"])

    # ---- 标注不受影响 ----
    r4 = c.post("/api/analyze-text", json={
        "text": SAMPLE, "level_id": "cet4", "title": "真实链路", "use_llm": False,
        "translate": False})
    check("★ 开/关译文的标注计数一致",
          r4.json()["counters"] == hb["counters"],
          f'{r4.json()["counters"]} vs {hb["counters"]}')

    # ---- 缓存确实落盘 ----
    n_files = len(list(translate.cache_dir().glob("*.json")))
    check("译文缓存已落盘（4 句 → 4 个文件）", n_files == 4, str(n_files))


def _report(tb: str = "") -> None:
    if tb:
        LOG.append("*** 自检中途异常终止 ***")
        LOG.append(tb)
    LOG.append("")
    LOG.append(f"结果：{PASS} 通过 / {FAIL} 失败")
    (ROOT / "out" / "_transe2e_test.txt").write_text("\n".join(LOG), encoding="utf-8")
    print(f"PASS={PASS} FAIL={FAIL}")


def _cleanup() -> None:
    try:
        from app import settings, translate
        translate.clear_cache()
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
    finally:
        try:
            if _SRV is not None:
                _SRV.shutdown()
        except Exception:  # noqa: BLE001
            pass
        try:
            _report(tb)
        finally:
            _cleanup()
    sys.exit(1 if (FAIL or tb) else 0)
