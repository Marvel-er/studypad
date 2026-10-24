"""
大模型适配层：所有供应商统一走 OpenAI 兼容协议。

对比开源项目：ai-dokkai / shiyu / read-bridge 都是 OpenAI 兼容可配，
本项目沿用同一约定，因此 DeepSeek、通义、智谱、Groq、Ollama、vLLM
以及任何自建网关都能直接接入，无需改代码。

未配置 API Key 时，整条链路自动退化为纯规则标注。
"""
from __future__ import annotations

import json
import os
import re
import sys
import threading
from dataclasses import dataclass

import httpx

PRESETS: dict[str, dict] = {
    "deepseek":  {"base_url": "https://api.deepseek.com/v1",                    "model": "deepseek-chat",       "label": "DeepSeek"},
    "openai":    {"base_url": "https://api.openai.com/v1",                      "model": "gpt-4o-mini",         "label": "OpenAI"},
    "qwen":      {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "model": "qwen-plus",        "label": "通义千问"},
    "zhipu":     {"base_url": "https://open.bigmodel.cn/api/paas/v4",           "model": "glm-4-flash",         "label": "智谱 GLM"},
    "moonshot":  {"base_url": "https://api.moonshot.cn/v1",                     "model": "moonshot-v1-8k",      "label": "Kimi"},
    "groq":      {"base_url": "https://api.groq.com/openai/v1",                 "model": "llama-3.3-70b-versatile", "label": "Groq"},
    "ollama":    {"base_url": "http://localhost:11434/v1",                      "model": "qwen2.5:7b",          "label": "本地 Ollama"},
    "custom":    {"base_url": "",                                               "model": "",                    "label": "自定义"},
}


# =====================================================================
# 翻译专用模型（MT）
# =====================================================================
# 为什么和上面的 PRESETS 分开：这两件事对模型的要求完全不同。
#
#   · **翻译**是逐句转写：一篇 20 页的 PDF 要翻几百句，全部丢给云端大模型等于
#     把最贵的那部分额度花在「不需要智能」的活上，而且逐句生成的延迟是总耗时的主体。
#   · **手账讲解**（语法重写、考点 brief）需要真正的语言理解 + 考纲上下文，小模型干不了。
#
# 所以默认把翻译甩给本机的翻译小模型（Apache-2.0，1.8B，Q4 约 1.1GB，常驻显存约 1.7GB），
# 云端额度只留给讲解。实测同一篇 23 句文章：本地 3.3 秒翻完，云端 token 消耗降为 0。
MT_PRESETS: dict[str, dict] = {
    "mt_local":  {"base_url": "http://localhost:11434/v1", "model": "hy-mt2:1.8b",
                  "label": "本地翻译模型（Hy-MT2-1.8B）"},
    "mt_own":    {"base_url": "http://localhost:11434/v1", "model": "hy-mt2:7b",
                  "label": "本地翻译模型（Hy-MT2-7B · 更高文风）"},
    "ollama":    {"base_url": "http://localhost:11434/v1", "model": "hy-mt2:1.8b",
                  "label": "本地 Ollama（自己填模型名）"},
    "custom":    {"base_url": "", "model": "", "label": "自定义 / 复用主模型"},
}

# 翻译模型没配时用的默认值 —— 与 MT_PRESETS["mt_local"] 一致。
# 单独拿出来是因为 main._resolve_mt_cfg 要在「已保存配置为空」时也要能拿到它：
# 用户装好模型后不该还被迫先去设置页填一遍端点。
MT_DEFAULT: dict = MT_PRESETS["mt_local"]


# =====================================================================
# 关掉「思考」
# =====================================================================
# 为什么必须有这一段：推理模型（deepseek-v4-pro / o 系列 / qwq 等）默认会先写一大段
# 思考再给正文，而**翻译和改写讲解根本不需要推理**。实测 deepseek-v4-pro 翻 18 句：
#
#     completion_tokens = 2710，其中 reasoning_tokens = 2439（90%）
#     耗时 36 秒，真正产出译文只用了 271 个 token
#
# 更糟的是：思考一旦把 max_tokens 吃满，message.content 就是**空字符串**。
# 下游只能判成「译文条数对不上」→ 重试 → 再二分，一串连锁浪费 ——
# 实测一篇 23 句的文章因此发了 6 次请求、94 秒里有 57 秒是白等的。
#
# 各家关法不统一，这里用实测有效的 DeepSeek/Anthropic 风格写法；
# 遇到不认这个字段的网关（400）会自动退回不带该字段重试，并记住这家不吃这套，
# 所以不会因为「有的服务不认」而每次白挨一次错误。
NO_THINK_PAYLOAD: dict = {"thinking": {"type": "disabled"}}

_NO_THINK_UNSUPPORTED: set[str] = set()
_LOCK = threading.Lock()


def no_think_default() -> bool:
    """默认关掉思考（快 5–10 倍）；想要最高质量可设 `STUDYPAD_LLM_THINK=1`。"""
    return os.environ.get("STUDYPAD_LLM_THINK", "").strip().lower() not in ("1", "true", "yes", "on")


@dataclass
class LLMConfig:
    provider: str = "deepseek"
    api_key: str = ""
    base_url: str = ""
    model: str = ""
    timeout: float = 90.0
    no_think: bool = True

    def resolved(self) -> "LLMConfig":
        p = PRESETS.get(self.provider, PRESETS["custom"])
        return LLMConfig(
            provider=self.provider,
            api_key=self.api_key or os.environ.get(f"{self.provider.upper()}_API_KEY", ""),
            base_url=self.base_url or p["base_url"],
            model=self.model or p["model"],
            timeout=self.timeout,
            no_think=self.no_think,
        )

    @property
    def ready(self) -> bool:
        r = self.resolved()
        return bool(r.base_url and (r.api_key or "localhost" in r.base_url or "127.0.0.1" in r.base_url))


class LLMError(RuntimeError):
    pass


# 共用一个连接池。每次调用都新建 `httpx.Client` 意味着重做一遍 TCP + TLS 握手，
# 并发翻译时这笔开销要乘上批次数；而且 keep-alive 用不上。
# httpx.Client 官方说明是线程安全的，可以跨线程共享。
_CLIENT: httpx.Client | None = None


def _client() -> httpx.Client:
    global _CLIENT
    if _CLIENT is None:
        with _LOCK:
            if _CLIENT is None:
                _CLIENT = httpx.Client(
                    timeout=httpx.Timeout(90.0, connect=15.0),
                    limits=httpx.Limits(max_connections=32, max_keepalive_connections=16),
                )
    return _CLIENT


def _log_usage(data: dict, model: str) -> None:
    """`STUDYPAD_LLM_DEBUG=1` 时把 token 用量写到 stderr（排查「为什么慢」用）。"""
    if os.environ.get("STUDYPAD_LLM_DEBUG", "").strip().lower() not in ("1", "true", "yes", "on"):
        return
    u = data.get("usage") or {}
    det = u.get("completion_tokens_details") or {}
    try:
        sys.stderr.write(
            f"[llm] {model}  prompt={u.get('prompt_tokens')}"
            f"(cache_hit {u.get('prompt_cache_hit_tokens')})"
            f"  completion={u.get('completion_tokens')}"
            f"  reasoning={det.get('reasoning_tokens')}\n")
        sys.stderr.flush()
    except Exception:  # noqa: BLE001 — 调试输出绝不能影响主流程
        pass


def chat(cfg: LLMConfig, messages: list[dict], *, temperature: float = 0.2,
         max_tokens: int = 3000, json_mode: bool = True,
         no_think: bool | None = None) -> str:
    r = cfg.resolved()
    if not r.ready:
        raise LLMError("未配置可用的模型服务")

    payload: dict = {
        "model": r.model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    headers = {"Content-Type": "application/json"}
    if r.api_key:
        headers["Authorization"] = f"Bearer {r.api_key}"
    url = f"{r.base_url.rstrip('/')}/chat/completions"

    want_off = r.no_think if no_think is None else bool(no_think)
    host = r.base_url.rstrip("/")
    if want_off and host not in _NO_THINK_UNSUPPORTED:
        payload.update(NO_THINK_PAYLOAD)

    client = _client()
    resp = client.post(url, json=payload, headers=headers, timeout=r.timeout)
    if resp.status_code >= 400 and "thinking" in payload:
        # 有的 OpenAI 兼容网关不认这个字段，直接 400。退回不带它再发一次，
        # 并记住这家不吃这套 —— 只挨一次，不是每次调用都白挨。
        with _LOCK:
            _NO_THINK_UNSUPPORTED.add(host)
        payload.pop("thinking", None)
        resp = client.post(url, json=payload, headers=headers, timeout=r.timeout)
    if resp.status_code >= 400:
        raise LLMError(f"HTTP {resp.status_code}: {resp.text[:300]}")

    try:
        data = resp.json()
        choice = data["choices"][0]
        msg = choice["message"] or {}
    except (KeyError, IndexError, ValueError) as e:
        raise LLMError(f"响应格式异常: {str(resp.text)[:300]}") from e

    _log_usage(data, r.model)

    text = msg.get("content") or ""
    finish = choice.get("finish_reason")
    det = (data.get("usage") or {}).get("completion_tokens_details") or {}
    reasoning_tokens = det.get("reasoning_tokens") or 0
    thinking_chars = len(msg.get("reasoning_content") or "")

    if not text.strip():
        # 空正文的两种成因必须分开报。混成一句「未返回可解析的 JSON」，
        # 会让人以为是提示词写错了，实际是输出预算被推理吃掉了。
        if reasoning_tokens or thinking_chars:
            raise LLMError(
                f"模型把输出预算都花在推理上了（reasoning_tokens={reasoning_tokens}，"
                f"思考 {thinking_chars} 字，finish_reason={finish}），没有产出正文。"
                f"该模型可能关不掉推理，需要提高 max_tokens 或换成非推理模型。")
        if finish == "length":
            raise LLMError(f"输出被 max_tokens={max_tokens} 截断，正文为空。")
        raise LLMError(f"模型返回了空内容（finish_reason={finish!r}）")

    if finish == "length":
        # 正文非空但被截断：JSON 多半已经是残的，早点说清楚，
        # 别让下游拿半截 JSON 去猜「条数对不上」。
        raise LLMError(f"输出被 max_tokens={max_tokens} 截断（只拿到 {len(text)} 字）")

    return text


def parse_json(text: str) -> dict | list:
    """从模型输出里稳健地取出 JSON（容忍 ```json 围栏与前后废话）。"""
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*", "", t)
    t = re.sub(r"\s*```$", "", t)
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        pass
    for m in re.finditer(r"[\[{]", t):
        for closer in ("}", "]"):
            depth = 0
            for i in range(m.start(), len(t)):
                if t[i] in "{[":
                    depth += 1
                elif t[i] in "}]":
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(t[m.start():i + 1])
                        except json.JSONDecodeError:
                            break
    raise LLMError("模型未返回可解析的 JSON")


def test_connection(cfg: LLMConfig) -> tuple[bool, str]:
    try:
        out = chat(cfg, [{"role": "user", "content": "reply with exactly: ok"}],
                   max_tokens=10, json_mode=False)
        return True, out.strip()[:60]
    except Exception as e:  # noqa: BLE001
        return False, str(e)[:200]
