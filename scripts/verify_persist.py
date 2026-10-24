"""
真实服务的持久化验证（跑在 8300 上，会写用户真实配置，最后会清理）。

  python scripts/verify_persist.py save    # 写入配置（假 Key）
  <重启服务>
  python scripts/verify_persist.py check   # 验证重启后仍在，然后清理

用户当前没有配置时最安全：check 阶段的 DELETE 会把状态还原成「无配置」。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx

BASE = "http://127.0.0.1:8300"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out" / "_persist.txt"
CFG = Path.home() / ".studypad" / "settings.json"
SECRET = "sk-persistcheck-aaaaBBBB1234"

mode = sys.argv[1] if len(sys.argv) > 1 else "save"
log: list[str] = []
c = httpx.Client(timeout=30)

if mode == "save":
    before = c.get(f"{BASE}/api/llm/config").json()
    log.append(f"[写入前] has_key={before['has_key']}  provider={before['provider']!r}")
    log.append(f"         配置文件路径 = {before['path']}")

    r = c.post(f"{BASE}/api/llm/config", json={
        "provider": "deepseek", "base_url": "", "model": "deepseek-chat",
        "api_key": SECRET, "enabled": True,
    })
    d = r.json()
    log.append(f"[POST] {r.status_code}  has_key={d['has_key']}  key_hint={d['key_hint']!r}")
    log.append(f"       响应体里含明文 Key = {SECRET in r.text}   （应为 False）")

    log.append(f"[磁盘] {CFG}")
    log.append(f"       文件存在 = {CFG.exists()}")
    if CFG.exists():
        raw_text = CFG.read_text(encoding="utf-8")
        raw = json.loads(raw_text)
        log.append(f"       provider={raw.get('provider')}  model={raw.get('model')}  "
                   f"enabled={raw.get('enabled')}")
        log.append(f"       Key 完整落盘 = {raw.get('api_key') == SECRET}")
        log.append(f"       （本地文件里是明文，属预期：单机应用无法真正藏住本地密钥）")
else:
    d = c.get(f"{BASE}/api/llm/config").json()
    ok = bool(d["has_key"]) and d["provider"] == "deepseek" and d["model"] == "deepseek-chat"
    log.append(f"[重启后 GET] has_key={d['has_key']}  provider={d['provider']!r}  "
               f"model={d['model']!r}  enabled={d['enabled']}  key_hint={d['key_hint']!r}")
    log.append(f"[结论] 重启后无需重新配置 = {ok}   （应为 True）")

    r = c.delete(f"{BASE}/api/llm/config")
    log.append(f"[DELETE] {r.status_code}  has_key={r.json()['has_key']}")
    log.append(f"[清理] 配置文件仍存在 = {CFG.exists()}   （应为 False）")

OUT.write_text("\n".join(log), encoding="utf-8")
print("\n".join(log))
