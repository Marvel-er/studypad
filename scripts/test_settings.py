"""
配置持久化自检：settings 模块 + main 里的 Key 回退逻辑。

用 STUDYPAD_HOME 指向 out/_cfgtest，不碰用户真实的 ~/.studypad。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

TMP = ROOT / "out" / "_cfgtest"
os.environ["STUDYPAD_HOME"] = str(TMP)

from app import main, settings  # noqa: E402

LOG = []
PASS = FAIL = 0


def check(name: str, cond: bool, extra: str = "") -> None:
    global PASS, FAIL
    mark = "PASS" if cond else "FAIL"
    if cond:
        PASS += 1
    else:
        FAIL += 1
    LOG.append(f"[{mark}] {name}" + (f"  → {extra}" if extra else ""))


def dump() -> str:
    p = settings.path()
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return "<不存在>"


# ---------------------------------------------------------------- 准备
if TMP.exists():
    for f in TMP.iterdir():
        f.unlink()
    TMP.rmdir()

LOG.append(f"配置目录 = {settings.home()}")
LOG.append(f"配置文件 = {settings.path()}")
LOG.append("")

# ---------------------------------------------------------------- 1. 空状态
check("初始 load() 为空", settings.load() == {})
check("初始 public().has_key 为 False", settings.public()["has_key"] is False)
check("初始 public() 返回 path", bool(settings.public()["path"]))

# ---------------------------------------------------------------- 2. 保存
settings.save({
    "provider": "qwen", "base_url": "https://example.test/v1",
    "model": "qwen-plus", "api_key": "sk-1234567890abcdef", "enabled": True,
})
d = settings.load()
check("保存后 provider 正确", d.get("provider") == "qwen", str(d.get("provider")))
check("保存后 api_key 完整落盘", d.get("api_key") == "sk-1234567890abcdef")
check("保存后 enabled=True", d.get("enabled") is True)
check("配置文件已创建", settings.path().exists())
check("落盘内容是合法 JSON", isinstance(json.loads(dump()), dict))

# ---------------------------------------------------------------- 3. 脱敏
pub = settings.public()
check("public() 不含完整 api_key 字段", "api_key" not in pub)
check("public() has_key=True", pub["has_key"] is True)
check("key_hint 已掩码", pub["key_hint"] == "sk-******cdef", pub["key_hint"])
check("key_hint 不含中间明文", "1234567890" not in json.dumps(pub, ensure_ascii=False))
check("mask 短串全遮", settings.mask("abc") == "***")
check("mask 空串返回空", settings.mask("") == "")

# ---------------------------------------------------------------- 4. 空 key = 保持原样
settings.save({"api_key": "", "model": "qwen-max"})
d = settings.load()
check("传空 api_key 不会清掉原 Key", d.get("api_key") == "sk-1234567890abcdef")
check("同一次请求里其它字段照常更新", d.get("model") == "qwen-max", str(d.get("model")))

# ---------------------------------------------------------------- 5. 只更新开关
settings.save({"enabled": False})
d = settings.load()
check("单独更新 enabled 不影响其它字段",
      d.get("enabled") is False and d.get("provider") == "qwen" and d.get("model") == "qwen-max")

# ---------------------------------------------------------------- 6. 白名单
settings.save({"provider": "deepseek", "恶意字段": "x", "__proto__": "y"})
d = settings.load()
check("非白名单字段被丢弃", "恶意字段" not in d and "__proto__" not in d)
check("白名单字段正常写入", d.get("provider") == "deepseek")

# ---------------------------------------------------------------- 7. 损坏文件容错
settings.path().write_text("{ this is not json", encoding="utf-8")
check("损坏的 JSON 不抛异常且返回空", settings.load() == {})
settings.path().write_text('["not", "a", "dict"]', encoding="utf-8")
check("非对象 JSON 返回空", settings.load() == {})

# ---------------------------------------------------------------- 8. _needs_saved_key
check("带 Key → 不用保存的", main._needs_saved_key("deepseek", "sk-x", "") is False)
check("ollama → 不用保存的", main._needs_saved_key("ollama", "", "") is False)
check("localhost → 不用保存的", main._needs_saved_key("custom", "", "http://localhost:11434/v1") is False)
check("127.0.0.1 → 不用保存的", main._needs_saved_key("custom", "", "http://127.0.0.1:8000/v1") is False)
check("云端 + 无 Key → 用保存的", main._needs_saved_key("deepseek", "", "") is True)

# ---------------------------------------------------------------- 9. _resolve_cfg 回退
settings.save({"provider": "qwen", "base_url": "", "model": "qwen-plus",
               "api_key": "sk-saved-key-9999"})

cfg = main._resolve_cfg("", "", "", "")
check("无 Key 时回退到已保存的 Key", cfg.api_key == "sk-saved-key-9999")
check("无 Key 时回退到已保存的 provider", cfg.provider == "qwen", cfg.provider)
r = cfg.resolved()
check("回退后 base_url 用预设默认",
      r.base_url == "https://dashscope.aliyuncs.com/compatible-mode/v1", r.base_url)
check("回退后 ready 为真", cfg.ready is True)

cfg = main._resolve_cfg("deepseek", "sk-request-key", "", "")
check("请求带 Key 时优先用请求的", cfg.api_key == "sk-request-key" and cfg.provider == "deepseek")

cfg = main._resolve_cfg("ollama", "", "", "")
check("ollama 不回退（不会误用云端 Key）", cfg.api_key == "" and cfg.provider == "ollama")
check("ollama 仍可用（本地免 Key）", cfg.ready is True, f"base_url={cfg.resolved().base_url}")

# ---------------------------------------------------------------- 10. 清除
settings.clear()
check("clear() 后文件不存在", not settings.path().exists())
check("clear() 后 load() 为空", settings.load() == {})
settings.clear()   # 重复清除不应抛异常
check("重复 clear() 不抛异常", True)

# ---------------------------------------------------------------- 收尾
LOG.append("")
LOG.append(f"结果：{PASS} 通过 / {FAIL} 失败")
(ROOT / "out" / "_settings_test.txt").write_text("\n".join(LOG), encoding="utf-8")
print(f"PASS={PASS} FAIL={FAIL}")

# 清理测试目录
if TMP.exists():
    for f in TMP.iterdir():
        f.unlink()
    TMP.rmdir()
