"""探针：沙箱守卫抛 SystemExit 时，缓存层绝不能影响翻译。

2026-10-15 用户截图反馈「Unexpected token 'I', "Internal S"... is not valid JSON」。
根因不是翻译失败，而是：本机 WorkBuddy 沙箱把 `pathlib.Path.unlink` 换成了带
safe-delete 守卫的版本，守卫不通过时抛 **`SystemExit(1)`** ——
它继承自 `BaseException`，`except OSError` 和 `except Exception` 都拦不住，
一路穿透 anyio 线程池和 FastAPI 把请求打成 500；前端再把 500 的纯文本
响应当 JSON 解析，于是用户看到那句莫名的解析错误。

线上真实触发条件：缓存条目涨到 `CACHE_MAX_FILES`(400) 之上，
`_prune` 开始淘汰旧文件 → 第一个 `unlink` 就炸。

⚠ 本探针第一版的教训：只写两三条缓存是**跑不到淘汰分支**的
（`files[: max(0, len(files) - 400)]` 是空切片），于是正向断言恒真。
所以这里把 `CACHE_MAX_FILES` 临时打成 0，强制每次 `cache_put` 都走淘汰。
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

TMP = Path(tempfile.gettempdir()) / "_studypad_cacheguard"
os.environ["STUDYPAD_HOME"] = str(TMP)

from app import settings as _settings, translate  # noqa: E402

import os as _os  # noqa: E402
ORIG_REPLACE = _os.replace

out: list[str] = []
fails: list[str] = []


def check(cond: bool, label: str, detail: str = "") -> None:
    out.append(f"  [{'PASS' if cond else 'FAIL'}] {label}" + (f"  → {detail}" if detail else ""))
    if not cond:
        fails.append(label)


translate.clear_cache()

ORIG_UNLINK = Path.unlink
ORIG_MKDIR = Path.mkdir
ORIG_TOUCH = Path.touch
ORIG_MAX = translate.CACHE_MAX_FILES
NEW_MAX = (OSError, ValueError, SystemExit)


def boom(self, *a, **kw):
    """模拟沙箱 safe-delete 守卫：抛的是 SystemExit，不是 OSError。"""
    raise SystemExit(1)


def restore():
    Path.unlink = ORIG_UNLINK
    Path.mkdir = ORIG_MKDIR
    Path.touch = ORIG_TOUCH
    translate.CACHE_MAX_FILES = ORIG_MAX
    translate._CACHE_ERRORS = NEW_MAX


# 关键：把上限打成 0，强制每次 cache_put 都触发淘汰（否则跑不到 unlink）
translate.CACHE_MAX_FILES = 0

out.append("--- 0. 夹具自检：淘汰分支真的会走到 ---")
translate.cache_put("warmup", "预热")
n_files = len(list(translate.cache_dir().glob("*.json")))
check(n_files == 0, "上限打成 0 后，缓存确实被淘汰光了（夹具有效）", f"剩 {n_files} 个")

out.append("")
out.append("--- 1. 淘汰旧缓存时 unlink 抛 SystemExit（线上真实出事点）---")
Path.unlink = boom
try:
    translate.cache_put("sentence one", "译文一")
    translate.cache_put("sentence two", "译文二")
    check(True, "cache_put 在 unlink 抛 SystemExit 时没有往外抛")
except BaseException as e:  # noqa: BLE001
    check(False, "cache_put 在 unlink 抛 SystemExit 时没有往外抛",
          f"抛出了 {type(e).__name__}")
finally:
    restore()
    translate.CACHE_MAX_FILES = 0        # 继续保持「强制淘汰」

out.append("")
out.append("--- 2. 建缓存目录时 mkdir 抛 SystemExit ---")
Path.mkdir = boom
try:
    translate.cache_put("sentence three", "译文三")
    check(True, "cache_put 在 mkdir 抛 SystemExit 时没有往外抛")
except BaseException as e:  # noqa: BLE001
    check(False, "cache_put 在 mkdir 抛 SystemExit 时没有往外抛",
          f"抛出了 {type(e).__name__}")
finally:
    restore()
    translate.CACHE_MAX_FILES = 0

out.append("")
out.append("--- 3. 读缓存时 touch 抛 SystemExit ---")
translate.CACHE_MAX_FILES = 10 ** 9      # 先正常写一条（别被淘汰掉）
translate.cache_put("sentence four", "译文四")
Path.touch = boom
try:
    got = translate.cache_get("sentence four")
    check(True, "cache_get 在 touch 抛 SystemExit 时没有往外抛")
    check(got == "译文四", "而且译文照样读出来了（touch 只是摸 mtime）", f"got={got!r}")
except BaseException as e:  # noqa: BLE001
    check(False, "cache_get 在 touch 抛 SystemExit 时没有往外抛",
          f"抛出了 {type(e).__name__}")
finally:
    restore()
    translate.CACHE_MAX_FILES = 0

out.append("")
out.append("--- 4. 清缓存时 unlink 抛 SystemExit ---")
Path.unlink = boom
try:
    n = translate.clear_cache()
    check(True, "clear_cache 在 unlink 抛 SystemExit 时没有往外抛", f"removed={n}")
except BaseException as e:  # noqa: BLE001
    check(False, "clear_cache 在 unlink 抛 SystemExit 时没有往外抛",
          f"抛出了 {type(e).__name__}")
finally:
    restore()
    translate.CACHE_MAX_FILES = 0

out.append("")
out.append("--- 5. 恢复正常后缓存仍然好用（不能把功能修没了）---")
translate.CACHE_MAX_FILES = 10 ** 9      # 先把上限恢复，否则刚写进去就被淘汰
translate.clear_cache()
translate.cache_put("sentence five", "译文五")
got = translate.cache_get("sentence five")
check(got == "译文五", "恢复正常后缓存读写照旧", f"got={got!r}")
check(translate.clear_cache() >= 1, "恢复正常后清缓存照旧")

out.append("")
out.append("--- 6. 反向验证：换回旧的异常元组，探针必须报警 ---")
# 否则前面 5 组就是恒真断言（这个项目已经被假绿断言咬过两次）。
# 旧代码只捕 (OSError, ValueError)，SystemExit 会直接穿透。
translate._CACHE_ERRORS = (OSError, ValueError)
translate.CACHE_MAX_FILES = 0            # 强制走淘汰分支
Path.unlink = boom
raised = None
try:
    translate.cache_put("sentence six", "译文六")     # 会触发 _prune → unlink → SystemExit
except BaseException as e:  # noqa: BLE001
    raised = type(e).__name__
finally:
    Path.unlink = ORIG_UNLINK
    translate._CACHE_ERRORS = NEW_MAX
    translate.CACHE_MAX_FILES = 10 ** 9
check(raised == "SystemExit",
      "反向：只捕 OSError/ValueError 时，unlink 的 SystemExit 确实会穿透",
      f"实际抛出 {raised}")
# 炸点的位置要和线上 traceback 对得上：文件已经写成了，炸在淘汰那一步
check((translate.cache_dir() / f"{translate._key('sentence six')}.json").exists(),
      "反向：穿透前文件已写成、炸在淘汰这一步（与线上 traceback 位置一致）")

restore()
translate.clear_cache()

out.append("")
out.append("--- 7. settings.py 的保存/删除：SystemExit 要转成 RuntimeError，不能甩 500 ---")
# 同一个雷的第三处（缓存层已修，settings 是另一处）。
# 与缓存不同：保存 API Key 失败必须如实告知，所以不吞异常，
# 而是转成 RuntimeError —— llm_config_save/clear 已会把它变成 JSON 错误。

ORIG_HOME = _settings.home
_settings_home = TMP / "_cfgprobe"
_settings.home = lambda: _settings_home

for fn_name, fn in (("save", lambda: _settings.save({"api_key": "sk-x", "enabled": True})),
                    ("clear", lambda: _settings.clear())):
    Path.unlink = boom
    Path.mkdir = boom
    _os.replace = boom
    kind = None
    try:
        fn()
        kind = "no-raise"
    except RuntimeError:
        kind = "RuntimeError"
    except BaseException as e:  # noqa: BLE001
        kind = type(e).__name__
    finally:
        Path.unlink = ORIG_UNLINK
        Path.mkdir = ORIG_MKDIR
        _os.replace = ORIG_REPLACE
    check(kind == "RuntimeError",
          f"settings.{fn_name} 遇到 SystemExit 时转成 RuntimeError（不甩裸 500）",
          f"实际 {kind}")

# 反向：确认这些 patch 真的拦到了东西，不是恒真。
# 注意 patch 的必须是 **os.replace**（settings.save 用的是它，不是 Path.replace）
_settings.home = lambda: _settings_home
_os.replace = boom
kind2 = None
try:
    _settings.save({"api_key": "sk-y"})
except RuntimeError:
    kind2 = "RuntimeError"
except BaseException as e:  # noqa: BLE001
    kind2 = type(e).__name__
finally:
    _os.replace = ORIG_REPLACE
    _settings.home = ORIG_HOME
check(kind2 == "RuntimeError",
      "反向：只 patch os.replace 也确实被拦（夹具有效，不是恒真断言）",
      f"实际 {kind2}")

out.append("")
out.append(f"结果：{'全部通过' if not fails else str(len(fails)) + ' 项失败 — ' + '、'.join(fails)}")
print("\n".join(out))
sys.exit(1 if fails else 0)
