"""
本地配置持久化：把大模型接入信息存下来，下次打开自动生效。

存放位置（按优先级）：
  1. 环境变量 `STUDYPAD_HOME` 指定的目录
  2. 用户主目录下的 `~/.studypad/settings.json`
     Windows 上即 `C:\\Users\\<你>\\.studypad\\settings.json`

**为什么不放在项目目录里**：API Key 是「这台机器、这个用户」的凭据，
不属于项目本身。放进项目目录会有两个本可避免的泄露面 ——
拷贝/打包项目时把 Key 一起带走，以及误提交进版本库。
放在用户目录后，项目目录可以随便复制、随便开源。

**对外一律脱敏**：`public()` 只返回 `has_key` 与 `key_hint`（形如 `sk-******3f9a`），
完整的 Key 永远不会回到浏览器。前端因此也不需要持有它 ——
生成请求里不带 Key，后端自己取，链路上少一次密钥传递。
"""
from __future__ import annotations

import json
import os
from pathlib import Path

ENV_HOME = "STUDYPAD_HOME"
FILENAME = "settings.json"

# 只允许持久化这几个键，避免把任意请求体写进配置文件
#
# 两套模型配置是刻意分开的：
#   · `provider/base_url/model/api_key`        —— 生成手账内容（讲解重写、考点 brief），走云端 API
#   · `mt_provider/mt_base_url/mt_model/mt_api_key` —— **翻译专用**，默认指向本机 Ollama 上的翻译小模型
# 分开的理由就是这次改造的目的：翻译是「逐句转写」，用它去占云端模型的输出预算又慢又贵；
# 而讲解重写需要真正的语言能力和考纲上下文，本地 1.8B 干不了。
ALLOWED = ("provider", "base_url", "model", "api_key", "enabled",
           "mt_provider", "mt_base_url", "mt_model", "mt_api_key",
           "mt_enabled", "mt_fallback")

# 布尔键：前端可能传 "true"/"false" 字符串（form 表单），统一按真值转换
_BOOL_KEYS = ("enabled", "mt_enabled", "mt_fallback")

# 空值语义为「保持原样」的键。
# 前端拿不到已存的 Key（public() 只给掩码），无法回传原值 ——
# 所以传空必须是「别动」，否则用户每点一次保存就会把自己的 Key 清掉。
_KEEP_ON_EMPTY = ("api_key", "mt_api_key")

# ⚠ 写配置文件时的异常元组，**不能只写 OSError**（2026-10-15 踩过，改动前必读）。
#
# 本机的 WorkBuddy 沙箱会把一批文件操作换成带守卫 / broker 的版本
# （`pathlib.Path.unlink` / `Path.mkdir` / `Path.touch`、`os.remove` /
# `os.replace` / `os.chmod` …），守卫不通过时抛的是 **`SystemExit(1)`** ——
# 它继承自 `BaseException`，`except OSError` 拦不住，会一路穿透 FastAPI
# 把请求打成 500，前端只拿到一句纯文本 `Internal Server Error`。
#
# 与 `translate` 的缓存层不同：**这里是保存 API Key，失败必须如实告知用户**，
# 所以不吞异常，而是把 SystemExit 转成 RuntimeError（`llm_config_save` /
# `llm_config_clear` 已经会把它变成前端能显示的 JSON 错误）。
_FS_ERRORS = (OSError, SystemExit)


def home() -> Path:
    """配置目录。"""
    custom = os.environ.get(ENV_HOME, "").strip()
    if custom:
        return Path(custom).expanduser()
    return Path.home() / ".studypad"


def path() -> Path:
    return home() / FILENAME


def load() -> dict:
    """读配置。文件不存在或损坏都返回空字典，绝不抛异常。"""
    p = path()
    try:
        raw = p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    return {k: data.get(k) for k in ALLOWED if data.get(k) is not None}


def save(patch: dict) -> dict:
    """
    合并保存。

    `api_key` 的语义要特别说明：**传空值表示「保持原样」，而不是「清空」**。
    因为前端拿不到已存的 Key（脱敏），它无法回传原值；
    要清空请走 `clear()` / DELETE 接口。
    """
    data = load()
    for k in ALLOWED:
        if k not in patch:
            continue
        v = patch[k]
        if k in _KEEP_ON_EMPTY and not str(v or "").strip():
            continue                      # 空 key = 保持原样
        if k in _BOOL_KEYS:
            data[k] = _truthy(v)
            continue
        data[k] = str(v).strip()

    p = path()
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        # 原子写：先落临时文件再 replace，避免中途崩溃留下半个 JSON
        tmp = p.with_name(p.name + ".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, p)
        try:
            os.chmod(p, 0o600)   # POSIX 生效；Windows 继承用户目录 ACL，基本是 no-op
        except OSError:
            pass
    except _FS_ERRORS as e:
        # SystemExit 是沙箱守卫抛的，对它说「无法写入」比甩一句 500 有用得多
        raise RuntimeError(f"无法写入配置文件 {p}：{e}") from e
    return data


def clear() -> None:
    """删掉配置文件（下次就是全新状态）。"""
    try:
        path().unlink()
    except FileNotFoundError:
        pass
    except _FS_ERRORS as e:
        raise RuntimeError(f"无法删除配置文件 {path()}：{e}") from e


def _truthy(v) -> bool:
    """
    表单/JSON 传进来的「真假」值统一解析。

    ⚠ 不能直接 `bool(v)`：form 表单传的一律是字符串，
    `bool("false")` 是 **True** —— 前端把「翻译走本地模型」的勾去掉、提交 "false"，
    后端会当成「开启」，而设置页上显示的又是关闭状态，两边说法不一致且极难排查。
    """
    if isinstance(v, bool):
        return v
    return str(v or "").strip().lower() in ("1", "true", "yes", "on")


def mask(key: str) -> str:
    """`sk-abcdef123456` → `sk-******3456`。太短的直接全遮。"""
    key = (key or "").strip()
    if not key:
        return ""
    if len(key) <= 8:
        return "*" * len(key)
    return f"{key[:3]}{'*' * 6}{key[-4:]}"


def public() -> dict:
    """
    给浏览器的脱敏视图 —— 永不包含完整 api_key。

    `mt_*` 是**翻译专用**模型的配置（见 ALLOWED 的注释）。
    两个布尔位的默认值都是 True，与前端勾选框的初始状态一致：
    翻译走本地模型是这个项目的默认姿势，用户不需要先去设置页把它打开。
    """
    d = load()
    key = d.get("api_key", "") or ""
    mt_key = d.get("mt_api_key", "") or ""
    return {
        "provider": d.get("provider", "") or "",
        "base_url": d.get("base_url", "") or "",
        "model": d.get("model", "") or "",
        "enabled": bool(d.get("enabled", False)),
        "has_key": bool(key),
        "key_hint": mask(key),
        "mt_provider": d.get("mt_provider", "") or "",
        "mt_base_url": d.get("mt_base_url", "") or "",
        "mt_model": d.get("mt_model", "") or "",
        "mt_enabled": bool(d.get("mt_enabled", True)),
        "mt_fallback": bool(d.get("mt_fallback", True)),
        "mt_has_key": bool(mt_key),
        "mt_key_hint": mask(mt_key),
        "path": str(path()),
    }
