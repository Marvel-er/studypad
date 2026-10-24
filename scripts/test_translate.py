"""
译文模块自检。

这份测试的重心不是「能不能翻出来」，而是**对齐是否可信**：
译文挂错句子会直接误导阅读理解，比不给译文更糟。
所以这里用假模型刻意制造「条数不对」「返回加序号」「返回围栏 JSON」等真实故障，
验证系统要么对齐、要么明确放弃，绝不猜。

全程用 monkeypatch 替换 llm.chat，不发任何真实请求。

**临时目录必须放在系统临时目录下，不能放 `out/`**：
工作区有 safe-delete 守卫，单轮删除超过 50 个文件会被直接拦下并中断进程
（曾因此让整份自检在半路死掉、结果文件都没写出来）。
而缓存的本质就是「一篇文章几百个句子文件」，测试又要反复清空它，
所以这里是刻意选在守卫作用域之外。
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

TMP = Path(tempfile.gettempdir()) / "_studypad_transtest"
os.environ["STUDYPAD_HOME"] = str(TMP)

from app import analyzer, llm, translate  # noqa: E402

LOG: list[str] = []
PASS = FAIL = 0


def check(name: str, cond: bool, extra: str = "") -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
    LOG.append(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f"  → {extra}" if extra else ""))


def reset_cache() -> None:
    translate.clear_cache()


CFG = llm.LLMConfig(provider="deepseek", api_key="sk-fake", base_url="http://fake/v1",
                    model="fake")


def make_chat(transform=None):
    """假模型：按输入行数返回等量译文。transform 可注入故障。"""
    calls: list[list[dict]] = []

    def fake(cfg, messages, **kw):
        calls.append(messages)
        user = messages[-1]["content"]
        sents = re.findall(r"^\d+\.\s?(.*)$", user, re.M)
        items = ["译_" + s[:14] for s in sents]
        if transform:
            items = transform(items, sents, len(calls))
        return json.dumps({"t": items}, ensure_ascii=False)

    return fake, calls


def run(blocks, transform=None, target="zh"):
    fake, calls = make_chat(transform)
    orig = llm.chat
    llm.chat = fake
    try:
        out = translate.translate_blocks(blocks, CFG, target=target)
    finally:
        llm.chat = orig
    return out, calls


def blk(bid, text, btype="paragraph", **meta):
    return {"id": bid, "type": btype, "order": 0, "text": text,
            "meta": meta, "annotations": []}


def main() -> None:
    reset_cache()

    # ---------------------------------------------------------------- 1. span
    text = "First sentence here. Second one! And a third? Yes."
    spans = analyzer.split_spans(text)
    check("split_spans 切出 4 句", len(spans) == 4, str(len(spans)))
    ok_exact = all(text[s:e] == sent for s, e, sent in spans)
    check("span 切片与原句完全一致", ok_exact,
          str([(s, e, text[s:e]) for s, e, sent in spans][:2]))
    mono = all(spans[i][0] < spans[i + 1][0] and spans[i][1] <= spans[i + 1][0]
               for i in range(len(spans) - 1))
    check("span 单调不重叠", mono)
    check("span 无前导/尾随空白",
          all(sent == sent.strip() for _s, _e, sent in spans))

    # 缩写不该被切碎
    ab = "Dr. Smith went home. He was tired."
    check("缩写不误切", len(analyzer.split_spans(ab)) == 2,
          str(len(analyzer.split_spans(ab))))

    # 空串 / 只有空白 / 单句
    check("空串切不出 span", analyzer.split_spans("") == [])
    check("纯空白切不出 span", analyzer.split_spans("   \n  ") == [])
    check("单句切出 1 个 span", len(analyzer.split_spans("Only one.")) == 1)
    check("无终止标点也能切出", len(analyzer.split_spans("No punctuation here")) == 1)

    # ---------------------------------------------------------------- 2. 清洗与解析
    check("去序号 1. ", translate._clean("1. 你好") == "你好")
    check("去序号 ①", translate._clean("① 你好") == "你好")
    check("去序号 3、", translate._clean("3、你好") == "你好")
    check("保留正常译文", translate._clean("这是一个测试。") == "这是一个测试。")
    check("剥掉包裹引号", translate._clean('"你好"') == "你好")

    check("解析 {t:[...]}", translate._extract_array({"t": ["a", "b"]}) == ["a", "b"])
    check("解析裸数组", translate._extract_array(["a"]) == ["a"])
    check("解析 translations 键",
          translate._extract_array({"translations": ["x"]}) == ["x"])
    check("解析 [{\"zh\":...}] 形态",
          translate._extract_array({"t": [{"zh": "甲"}]}) == ["甲"])
    check("单 list 值自动识别",
          translate._extract_array({"whatever": ["z"]}) == ["z"])
    check("无数组返回 None", translate._extract_array({"a": 1}) is None)

    # ---------------------------------------------------------------- 3. 正常翻译
    reset_cache()
    blocks = [
        blk("b0000", "The quick brown fox jumps. It is very fast.", "paragraph"),
        blk("b0001", "A second paragraph follows here. Done.", "paragraph"),
    ]
    out, calls = run(blocks)
    r = out["blocks"]
    check("两段都翻译成功", out["done"] == 2, f"done={out['done']} total={out['total']}")
    check("共发起 1 次批量请求（合并成批）", len(calls) == 1, str(len(calls)))

    s0 = r["b0000"]["sentences"]
    check("b0000 有 2 句译文", len(s0) == 2, str(len(s0)))
    # 关键：第 k 句译文必须对应第 k 句原文
    good = all(
        s0[i]["zh"].startswith("译_" + s0[i]["en"][:14])
        for i in range(len(s0))
    )
    check("★ 逐句对齐正确（译文没有错位）", good,
          str([(s["en"][:16], s["zh"]) for s in s0]))
    check("整段译文已拼接", r["b0000"]["zh"] == "".join(s["zh"] for s in s0))
    check("整段译文非 partial", r["b0000"]["partial"] is False)
    check("sentences 的 en 与原文 span 一致",
          all(s["en"] == blocks[0]["text"][s["start"]:s["end"]] for s in s0))
    check("mode 由 main 决定，此处只出数据", "trans_mode" not in out)

    # ---------------------------------------------------------------- 4. 缓存
    out2, calls2 = run(blocks)
    check("第二次全部命中缓存（0 次请求）", len(calls2) == 0, str(len(calls2)))
    check("缓存命中计数正确", out2["cache_hits"] == 4, str(out2["cache_hits"]))
    check("缓存结果与首次一致", out2["blocks"]["b0000"]["zh"] == r["b0000"]["zh"])

    # 换等级不影响翻译（缓存按句子哈希，不含等级）
    out3, calls3 = run(blocks)
    check("换等级复用同一份译文", len(calls3) == 0 and out3["done"] == 2)

    # --- 合批的收益：原文分段越碎，收益越大 -------------------------------
    # 这是「跨段落合批」存在的理由：手账原文常是一段一两句，
    # 若按段发请求，30 段就是 30 次往返，一份 20 页 PDF 要上百次。
    reset_cache()
    many_blocks = [blk(f"p{i:04d}", "One short sentence. And another one.")
                   for i in range(30)]
    out_mb, calls_mb = run(many_blocks)
    # 这里**不写死批数**，而是按护栏常数算出来。
    # 写死数字的话，每次调 BATCH_SENTENCES 都要来改测试，久而久之就变成
    # 「为了让测试变绿而改数字」—— 断言该钉的是「批数由护栏决定、与段数无关」。
    cap = math.ceil(60 / translate.BATCH_SENTENCES)
    check(f"30 段 × 2 句 → 批数由护栏决定（≤{cap} 批）",
          len(calls_mb) <= cap, f"实际 {len(calls_mb)} 批")
    check("合批收益仍在：远少于按段发（30 次）", len(calls_mb) < 30, str(len(calls_mb)))
    check("合批后每段都拿到自己的译文", out_mb["done"] == 30, str(out_mb["done"]))
    check("合批后逐段对齐仍然正确", all(
        all(s["zh"].strip() == ("译_" + s["en"][:14]).strip()
            for s in d["sentences"])
        for d in out_mb["blocks"].values()))
    check("合批后每段译文条数与原文句数一致", all(
        len(d["sentences"]) == 2 for d in out_mb["blocks"].values()))

    # --- 输出预算：必须盖得住「思考 + 正文」 -------------------------------
    # 这次的真凶。实测 deepseek-v4-pro 翻 18 句（1843 字符）时
    # completion=2710，其中思考 2439 —— 旧公式 300+1.5×1843=3064 看似够，
    # 但思考一超就把正文挤没，content 直接是空字符串。
    check("预算盖得住实测的「思考 2439 + 正文 271」",
          translate._budget_for(1843) >= 2710, str(translate._budget_for(1843)))
    check("预算比「只算正文」的旧公式更宽",
          translate._budget_for(1843) > 300 + int(1843 * 1.5),
          f"{translate._budget_for(1843)} vs {300 + int(1843 * 1.5)}")
    check("预算有上限（本地小上下文模型不能被撑爆）",
          translate._budget_for(999999) == 4000, str(translate._budget_for(999999)))
    check("短批不吃大预算", translate._budget_for(50) < 1000,
          str(translate._budget_for(50)))

    # --- 并发：整篇耗时从「各批求和」变成「取最慢那批」 ---------------------
    # 改动前批次是串行发的：实测 23 句的文档 94 秒里 57 秒是白等的
    # （见 out/_translate_speed.txt 的对比）。用「每次调用都 sleep」的假模型
    # 把并发放大：串行必然 ≈ N×sleep，并发只有 ≈ N/workers×sleep。
    reset_cache()
    many2 = [blk(f"q{i:04d}", "Alpha sentence one. Beta sentence two.")
             for i in range(16)]
    sleep_s = 0.25
    inner, calls_slow = make_chat()

    def slow_chat(cfg, messages, **kw):
        time.sleep(sleep_s)
        return inner(cfg, messages, **kw)

    orig_chat = llm.chat
    llm.chat = slow_chat
    ticks: list[tuple[int, int, str]] = []
    t0 = time.time()
    try:
        out_c = translate.translate_blocks(
            many2, CFG, on_progress=lambda d, t, n: ticks.append((d, t, n)))
    finally:
        llm.chat = orig_chat
    elapsed = time.time() - t0
    n_calls = len(calls_slow)
    serial = n_calls * sleep_s
    check(f"批次是并发发的（{n_calls} 次 × {sleep_s}s，串行需 {serial:.2f}s）",
          elapsed < serial * 0.8, f"实际 {elapsed:.2f}s")
    check("并发时每段仍拿到自己的译文", out_c["done"] == 16, str(out_c["done"]))
    check("并发时逐段对齐仍然正确", all(
        all(s["zh"].strip() == ("译_" + s["en"][:14]).strip()
            for s in d["sentences"])
        for d in out_c["blocks"].values()))
    check("进度分母是批数而不是段数",
          bool(ticks) and ticks[-1][1] == n_calls and ticks[-1][1] < 16,
          str(ticks[-1] if ticks else None))
    check("进度单调不减", all(b[0] >= a[0] for a, b in zip(ticks, ticks[1:])),
          str([t[0] for t in ticks]))
    check("进度跑满（最后一批完成即收尾）",
          bool(ticks) and ticks[-1][0] == ticks[-1][1], str(ticks[-1] if ticks else None))
    check("stats() 暴露并发度（排查时要知道当时发了几路）",
          translate.stats().get("workers") == translate.TRANSLATE_WORKERS,
          str(translate.stats().get("workers")))

    # ---------------------------------------------------------------- 5. 对齐失败
    reset_cache()
    # 第 1 次返回多一条（模型爱合并/多吐），第 2 次正常 → 重试应救回来
    state = {"seen": 0}

    def flaky(items, sents, n):
        state["seen"] += 1
        if state["seen"] == 1:
            return items + ["多余的一条"]
        return items

    out4, calls4 = run([blk("b0000", "One. Two. Three.")], transform=flaky)
    check("对齐失败后重试成功", out4["done"] == 1 and len(calls4) == 2,
          f"done={out4['done']} calls={len(calls4)}")
    check("重试时提示了期望条数",
          "expected exactly" in calls4[1][-1]["content"])

    # 永远对不上 → 必须整块放弃，且记录错误。
    # 假模型用「永远多吐一条」而不是「永远只吐一条」：
    # 后者在**单句批**里恰好条数相等（1 对 1），会被判为对齐成功，
    # 而这条用例要验的是「怎么都对不齐时不能硬猜」。
    reset_cache()
    out5, _c = run([blk("b0000", "One. Two. Three.")],
                   transform=lambda items, sents, n: items + ["多余的一条"])
    check("★ 始终对不齐时放弃该段（不猜）", out5["done"] == 0 and out5["skipped"] == 1,
          f"done={out5['done']} skipped={out5['skipped']}")
    check("放弃原因被记录", bool(out5["errors"]), str(out5["errors"][:1]))
    check("放弃时不产出任何译文", out5["blocks"] == {})

    # ------------------------------------------------- 5b. 二分救援（合批的安全网）
    # 合批把好几个段落的句子塞进一次请求，代价是「一坏坏一批」。
    # 二分救援要能把坏句子隔离出来，保住同批里本来能翻好的那部分。
    reset_cache()

    def poison(items, sents, n):
        if any("POISON" in s for s in sents):
            return items + ["多余的"]
        return items

    out_b, calls_b = run([blk("b0000", "Good one A. Good one B. Good one C. POISON here.")],
                         transform=poison)
    d = out_b["blocks"].get("b0000")
    check("★ 一半对不齐时，另一半仍被救回",
          out_b["done"] == 1 and bool(d) and len(d["sentences"]) == 2,
          f"done={out_b['done']} sentences={len(d['sentences']) if d else 0}")
    check("救回的正是好的那两句（顺序没被打乱）",
          bool(d) and [s["en"] for s in d["sentences"]] == ["Good one A.", "Good one B."],
          str([s["en"] for s in d["sentences"]] if d else []))
    check("缺句的段落标记为 partial", bool(d) and d["partial"] is True)
    check("缺句时整段译文留空（不能拿残句凑一段）", bool(d) and d["zh"] == "")
    check("放弃的那半批有错误记录", bool(out_b["errors"]), str(out_b["errors"][:1]))
    check("二分不会把请求数放大（最坏 6 次）", len(calls_b) <= 6, str(len(calls_b)))

    # ---------------------------------------------------------------- 6. 异常容错
    reset_cache()
    # 模型返回烂 JSON
    fake_bad = lambda cfg, messages, **kw: "对不起，我无法完成"
    orig = llm.chat
    llm.chat = fake_bad
    try:
        out6 = translate.translate_blocks([blk("b0000", "Hello there. Good day.")], CFG)
    finally:
        llm.chat = orig
    check("模型返非 JSON 时不崩、记错误",
          out6["done"] == 0 and bool(out6["errors"]), str(out6["errors"][:1]))

    # 模型直接抛异常
    def boom(cfg, messages, **kw):
        raise llm.LLMError("HTTP 401: unauthorized")

    llm.chat = boom
    try:
        out7 = translate.translate_blocks([blk("b0000", "Hello there. Good day.")], CFG)
    finally:
        llm.chat = orig
    check("模型报错时不崩、记错误",
          out7["done"] == 0 and "401" in (out7["errors"][0] if out7["errors"] else ""),
          str(out7["errors"][:1]))

    # ---------------------------------------------------------------- 7. 跳过规则
    reset_cache()
    blocks7 = [
        blk("b0000", "print('hello world')", "code"),
        blk("b0001", "A diagram caption.", "figure"),
        blk("b0002", "| a | b |", "table"),
        blk("b0003", "This paragraph should be translated.", "paragraph"),
        blk("b0004", "Skipped by meta.", "paragraph", skip=True),
        blk("b0005", " ", "paragraph"),
    ]
    out8, calls8 = run(blocks7)
    check("code/figure/table 不翻译", out8["total"] == 1, f"total={out8['total']}")
    check("meta.skip 不翻译", "b0004" not in out8["blocks"])
    check("空白块不翻译", "b0005" not in out8["blocks"])
    check("只翻正文段落", list(out8["blocks"].keys()) == ["b0003"],
          str(list(out8["blocks"].keys())))

    # ---------------------------------------------------------------- 8. 超长截断
    # 把上限临时调小来测截断，而不是真造 2.4 万字符的原文：
    # 那样会写出几百个缓存文件，既慢又没多测到任何东西。
    reset_cache()
    CAP = 260
    old_max = translate.MAX_CHARS
    translate.MAX_CHARS = CAP
    try:
        big = [blk(f"b{i:04d}", "Sentence number %d is here and it keeps going." % i)
               for i in range(30)]
        out9, _ = run(big)
    finally:
        translate.MAX_CHARS = old_max
    check("超长原文会截断并置标记", out9["truncated"] is True)
    check("截断时仍有产出", out9["done"] > 0, str(out9["done"]))
    check("截断时报告未译段数", out9["skipped"] > 0, str(out9["skipped"]))
    check("done + skipped 等于总数（没有段落被漏算）",
          out9["done"] + out9["skipped"] == out9["total"],
          f"{out9['done']}+{out9['skipped']} vs {out9['total']}")
    check("实际字符数不超上限", 0 < out9["chars"] <= CAP,
          f"{out9['chars']} vs {CAP}")
    check("截断时已译的段落都完整", all(
        d["partial"] is False for d in out9["blocks"].values()))

    # ---------------------------------------------------------------- 9. 分批
    reset_cache()
    many = blk("b0000", " ".join("Sentence number %d here." % i for i in range(50)))
    out10, calls10 = run([many])
    check("长段落会分批请求", len(calls10) >= 3, str(len(calls10)))
    check("每批不超过条数上限",
          all(len(re.findall(r"^\d+\.\s", m[-1]["content"], re.M))
              <= translate.BATCH_SENTENCES for m in calls10))
    check("分批后仍逐句对齐", out10["done"] == 1 and
          len(out10["blocks"]["b0000"]["sentences"]) == 50,
          str(len(out10["blocks"]["b0000"].get("sentences", []))))
    aligned = all(
        s["zh"].startswith("译_" + s["en"][:14])
        for s in out10["blocks"]["b0000"]["sentences"]
    )
    check("★ 分批后对齐依然正确", aligned)

    # ---------------------------------------------------------------- 10. flatten / stats
    flat = translate.flatten(out10["blocks"])
    check("flatten 产出非空", bool(flat.strip()))
    st = translate.stats()
    check("stats 声明必须用大模型", st["required"] == "llm")
    check("stats 带缓存目录", bool(st["cache_dir"]))
    check("stats 缓存条目数 > 0", st["cache_entries"] > 0, str(st["cache_entries"]))
    check("clear_cache 返回删除条数", translate.clear_cache() > 0)
    check("清空后缓存为 0", translate.stats()["cache_entries"] == 0)

    # ---------------------------------------------------------------- 11. 缓存隔离
    reset_cache()
    translate.cache_put("hello", "你好")
    check("缓存可写可读", translate.cache_get("hello") == "你好")
    check("不同 target 互不串味", translate.cache_get("hello", "ja") is None)
    translate.cache_put("hello", "你好啊")
    check("同 key 覆盖", translate.cache_get("hello") == "你好啊")

    LOG.append("")


def _report(tb: str = "") -> None:
    """结果落盘。放在 main 之外 —— 自检半路崩掉时也必须留下已经跑到哪儿了。"""
    if tb:
        LOG.append("*** 自检中途异常终止 ***")
        LOG.append(tb)
    LOG.append(f"结果：{PASS} 通过 / {FAIL} 失败")
    (ROOT / "out" / "_translate_test.txt").write_text("\n".join(LOG), encoding="utf-8")
    print(f"PASS={PASS} FAIL={FAIL}")


def _cleanup() -> None:
    reset_cache()
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
    except BaseException:  # noqa: BLE001 — 崩了也要落盘，否则等于没跑
        import traceback
        tb = traceback.format_exc()
    try:
        _report(tb)
    finally:
        _cleanup()
    # 失败时给出非零退出码，方便被 CI / 钩子当作红灯
    sys.exit(1 if (FAIL or tb) else 0)
