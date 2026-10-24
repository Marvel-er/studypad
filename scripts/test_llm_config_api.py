"""
接口层自检：/api/llm/config 的 GET / POST / DELETE。

用 FastAPI TestClient 在本进程内直接调用，不需要起服务；
STUDYPAD_HOME 指向 out/_cfgtest_api，不碰用户真实的 ~/.studypad。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

TMP = ROOT / "out" / "_cfgtest_api"
os.environ["STUDYPAD_HOME"] = str(TMP)

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app import settings  # noqa: E402

SECRET = "sk-testkey-abcdef123456"
LOG = []
PASS = FAIL = 0


def check(name: str, cond: bool, extra: str = "") -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
    LOG.append(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f"  → {extra}" if extra else ""))


if TMP.exists():
    for f in TMP.iterdir():
        f.unlink()
    TMP.rmdir()

c = TestClient(app)
LOG.append(f"配置文件 = {settings.path()}")
LOG.append("")

# ---------------------------------------------------------------- 1. 初始为空
r = c.get("/api/llm/config")
check("GET 初始返回 200", r.status_code == 200, str(r.status_code))
d = r.json()
check("初始 has_key=False", d.get("has_key") is False)
check("GET 响应含 path", bool(d.get("path")))
check("GET 响应不含 api_key 字段", "api_key" not in d)

# ---------------------------------------------------------------- 2. 保存
r = c.post("/api/llm/config", json={
    "provider": "deepseek", "base_url": "", "model": "deepseek-chat",
    "api_key": SECRET, "enabled": True,
})
check("POST 保存返回 200", r.status_code == 200, r.text[:200])
body = r.text
check("POST 响应不含明文 Key", SECRET not in body)
d = r.json()
check("POST 后 has_key=True", d.get("has_key") is True)
check("POST 后 key_hint 正确", d.get("key_hint") == "sk-******3456", d.get("key_hint"))
check("POST 后 enabled=True", d.get("enabled") is True)

# ---------------------------------------------------------------- 3. 真的落盘了吗
raw = settings.path().read_text(encoding="utf-8")
disk = json.loads(raw)
check("磁盘上确实存了完整 Key（该存的存下来）", disk.get("api_key") == SECRET)
check("磁盘文件是合法 JSON", isinstance(disk, dict))

# ---------------------------------------------------------------- 4. 重新读取（模拟"下次打开"）
r = c.get("/api/llm/config")
check("重新 GET 返回 200", r.status_code == 200)
check("重新 GET 仍不含明文 Key", SECRET not in r.text)
d = r.json()
check("重新 GET has_key=True（下次打开无需重配）", d.get("has_key") is True)
check("重新 GET provider 保持", d.get("provider") == "deepseek", d.get("provider"))
check("重新 GET model 保持", d.get("model") == "deepseek-chat", d.get("model"))
check("重新 GET enabled 保持", d.get("enabled") is True)

# ---------------------------------------------------------------- 5. 空 Key 不清空
r = c.post("/api/llm/config", json={
    "provider": "deepseek", "base_url": "", "model": "deepseek-reasoner",
    "api_key": "", "enabled": True,
})
d = r.json()
check("第二次 POST 传空 Key 后仍 has_key=True", d.get("has_key") is True)
check("第二次 POST 更新了 model", d.get("model") == "deepseek-reasoner", d.get("model"))
check("磁盘上的 Key 未被清掉",
      json.loads(settings.path().read_text(encoding="utf-8")).get("api_key") == SECRET)

# ---------------------------------------------------------------- 6. 清除
r = c.delete("/api/llm/config")
check("DELETE 返回 200", r.status_code == 200)
check("DELETE 后 has_key=False", r.json().get("has_key") is False)
check("DELETE 后文件被删除", not settings.path().exists())
r = c.get("/api/llm/config")
check("清除后再 GET 仍正常", r.status_code == 200 and r.json().get("has_key") is False)

# ---------------------------------------------------------------- 7. 预设接口仍正常
r = c.get("/api/llm/presets")
check("GET /api/llm/presets 正常", r.status_code == 200 and len(r.json()["presets"]) == 8)

LOG.append("")
LOG.append(f"结果：{PASS} 通过 / {FAIL} 失败")
(ROOT / "out" / "_cfgapi_test.txt").write_text("\n".join(LOG), encoding="utf-8")
print(f"PASS={PASS} FAIL={FAIL}")

if TMP.exists():
    for f in TMP.iterdir():
        f.unlink()
    TMP.rmdir()
