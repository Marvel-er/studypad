"""
前端 api() 助手的错误路径自检（用 Node 跑，不依赖浏览器）。

背景（2026-10-15 用户截图反馈）：FastAPI 对**未捕获异常**返回的 500 是
**纯文本** `Internal Server Error`，而旧的 api() 在 `!r.ok` 时直接 `r.json()`，
于是抛 `SyntaxError: Unexpected token 'I', "Internal S"...` ——
用户看到的就是那句解析错误，真正的原因（服务端 500）被藏起来了。

做法：从 common.js 里把 `api` 函数定义抠出来，配一个假 fetch，
分别喂「200 JSON / 500 JSON / 500 纯文本」，断言抛出的 message 是人话。
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# ⚠ api() 现在住在**公共层** `common.js`（2026-10-15 拆页时挪过去的），
# 曾经指着 index.html —— 拆完之后那儿已经没有这个函数了，
# 探针会「没找到 api() 定义」直接退出 1（2026-10-15 踩过）。
COMMON = (ROOT / "backend" / "static" / "common.js").read_text(encoding="utf-8")
HTML = COMMON
NODE = Path(r"C:\Users\刘永键\.workbuddy\binaries\node\versions\22.22.2-5\node.exe")

out: list[str] = []
fails: list[str] = []


def check(cond: bool, label: str, detail: str = "") -> None:
    out.append(f"  [{'PASS' if cond else 'FAIL'}] {label}" + (f"  → {detail}" if detail else ""))
    if not cond:
        fails.append(label)


# 把函数定义整段抠出来。**不能用正则**：函数体里换行+缩进不固定，
# `.*?\n\}` 会把它拦腰截断，抠出来的片段直接 SyntaxError（第一版就踩了）。
# 改成从 `function <名字>(` 起做花括号配对，数到归零为止。
def extract(fn_name: str, src: str) -> str:
    i = src.find(f"function {fn_name}(")
    if i < 0:
        print(f"没找到 {fn_name}() 定义，common.js 结构变了？")
        sys.exit(1)
    depth = 0
    for j in range(i, len(src)):
        ch = src[j]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return src[i:j + 1]
    print(f"{fn_name}() 的花括号没配对，common.js 结构变了？")
    sys.exit(1)


api_src = extract("api", HTML)
# ⚠ api() 现在把「错误文案怎么拼」抽给了 `apiError()`（2026-10-15 加 apiText() 时要复用同一套说法），
# 所以抠 api() 时必须把被它依赖的函数一起带上：只抠 api() 的话，
# Node 里会报 `apiError is not defined` —— 那条报错看着像「common.js 写坏了」，
# 其实只是探针的抠取范围太窄，白追一轮。
dep_src = extract("apiError", HTML)
src_all = api_src + "\n" + dep_src
out.append(f"抠到的 api() {len(api_src)} 字符 + apiError() {len(dep_src)} 字符，收尾 = {api_src[-24:]!r}")
check(api_src.rstrip().endswith("}"), "抠出来的是完整函数（花括号已配对）")
check("r.text()" in src_all, "新实现先取文本再尝试解析（不再直接 r.json()）")
check("r.status >= 500" in src_all, "5xx 有单独的说法")
check("out/_server.log" in src_all, "5xx 指引用户去看服务端日志")

# ---- 交给 Node 实跑 ----
JS = r"""
var __cases = [];
function __fetch(status, body, ctype) {
  return function () {
    return Promise.resolve({
      ok: status >= 200 && status < 300,
      status: status,
      text: function () { return Promise.resolve(body); },
      json: function () { return Promise.resolve(JSON.parse(body)); }
    });
  };
}
__SRC__
function run() {
  var results = [];
  var cases = [
    { name: "200 正常 JSON", status: 200, body: '{"ok":1}' },
    { name: "500 + JSON detail", status: 500, body: '{"detail":"模型未配置"}' },
    { name: "500 + 纯文本（线上真实形态）", status: 500, body: 'Internal Server Error' },
    { name: "400 + JSON detail", status: 400, body: '{"detail":"文件为空"}' },
    { name: "502 + HTML", status: 502, body: '<html><body>Bad Gateway</body></html>' }
  ];
  var p = Promise.resolve();
  cases.forEach(function (c) {
    p = p.then(function () {
      global.fetch = __fetch(c.status, c.body);
      return api('/api/x').then(function (d) {
        results.push({ name: c.name, kind: "resolved", value: JSON.stringify(d) });
      }).catch(function (e) {
        results.push({ name: c.name, kind: "rejected", value: String(e.message || e) });
      });
    });
  });
  return p.then(function () { return results; });
}
run().then(function (r) { console.log(JSON.stringify(r)); });
"""
JS = JS.replace("__SRC__", src_all)

tmp = ROOT / "out" / "_api_err_test.js"
tmp.write_text(JS, encoding="utf-8")
res = subprocess.run([str(NODE), str(tmp)], capture_output=True, text=True, timeout=60)
if res.returncode != 0:
    out.append("Node 执行失败：")
    out.append(res.stderr[-1500:])
    print("\n".join(out))
    sys.exit(1)

try:
    results = json.loads(res.stdout.strip().splitlines()[-1])
except (ValueError, IndexError):
    out.append("Node 输出解析失败：" + res.stdout[-500:])
    print("\n".join(out))
    sys.exit(1)

by = {r["name"]: r for r in results}
out.append("")
out.append("Node 实跑结果：")
for r in results:
    out.append(f"  [{r['kind']:8s}] {r['name']} → {r['value'][:110]}")

out.append("")
# ① 正常路径不能坏
check(by["200 正常 JSON"]["kind"] == "resolved"
      and json.loads(by["200 正常 JSON"]["value"]) == {"ok": 1},
      "200 正常 JSON 照旧解析出数据")
# ② 500 + JSON detail：仍然显示 detail
check(by["500 + JSON detail"]["kind"] == "rejected"
      and "模型未配置" in by["500 + JSON detail"]["value"]
      and "HTTP 500" in by["500 + JSON detail"]["value"],
      "500 + JSON：既显示 detail 也显示状态码")
# ③ 500 + 纯文本：**用户截图反馈的那条**，必须变成人话
v = by["500 + 纯文本（线上真实形态）"]["value"]
check(by["500 + 纯文本（线上真实形态）"]["kind"] == "rejected", "500 纯文本：走了 rejected 分支")
check("Unexpected token" not in v, "500 纯文本：不再出现 JSON 解析错误",
      f"实际 message = {v[:120]}")
check("HTTP 500" in v and "服务端内部错误" in v,
      "500 纯文本：说清是服务端内部错误并带上状态码", f"实际 message = {v[:120]}")
check("out/_server.log" in v, "500 纯文本：指引去看服务端日志（traceback 只在那里）")
check("Internal Server Error" in v, "500 纯文本：原文也一并显示，不吞信息")
# ④ 4xx + JSON：老行为要保持
check(by["400 + JSON detail"]["kind"] == "rejected"
      and "文件为空" in by["400 + JSON detail"]["value"]
      and "HTTP 400" in by["400 + JSON detail"]["value"],
      "400 + JSON：detail 与状态码都显示")
check("out/_server.log" not in by["400 + JSON detail"]["value"],
      "400 不该提示去看服务端日志（那是 5xx 的事）")
# ⑤ 502 + HTML：不能崩，也不能露出解析错误
v5 = by["502 + HTML"]["value"]
check(by["502 + HTML"]["kind"] == "rejected" and "Unexpected token" not in v5,
      "502 + HTML：不崩、不露解析错误", f"实际 message = {v5[:120]}")
check("HTTP 502" in v5, "502 + HTML：带上了状态码")

out.append("")
out.append(f"结果：{'全部通过' if not fails else str(len(fails)) + ' 项失败 — ' + '、'.join(fails)}")
print("\n".join(out))
sys.exit(1 if fails else 0)
