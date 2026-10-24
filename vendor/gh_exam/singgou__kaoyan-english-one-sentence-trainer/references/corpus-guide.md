# 本地真题语料库指南

## 原则

公开仓库不提供真题、答案或派生语料。使用者需要自行准备合法获取的 PDF、DOC、DOCX、TXT 或 Markdown 文件，所有解析结果只保存在本地。

构建目标是 Reading Part A 正文句子。问题、选项、答案、中文译文、解析、页眉页脚和重复来源不得进入每日长难句句库。

## 准备

1. 把真题资料集中到一个独立目录，不要放进 Skill 或 Git 仓库。
2. 通过 Codex 工作区依赖加载器取得 bundled Python，并进入 `SKILL_ROOT`。
3. 保持 `data/config.json` 的 `source_root` 为 `null`，每次通过命令显式指定资料目录。

## 构建

```powershell
& $PY scripts/build_corpus.py `
  --source-root "<用户真题目录>" `
  --year-start 2001 `
  --year-end 2026 `
  --allow-incomplete
```

`--allow-incomplete` 允许资料缺少某些年份，但不会绕过单篇来源安全检查，也不会补写缺失文本。若希望强制年份完整，省略该参数。

完成后运行：

```powershell
& $PY scripts/validate_corpus.py
```

验证失败时不得继续每日真题训练。先检查选错文件、不可机读扫描件、OCR 乱码、题目尾串、来源缺失或语料回退。

## OCR

扫描 PDF 没有文本层时，先生成单独的 OCR 派生副本，并标记为未复核。OCR 文本需要逐页核对后才能进入安全训练池；不得覆盖原始文件，也不得把模型补写当作 OCR 结果。

## 本地资产

构建过程会在 `data/` 下生成 `corpus.jsonl`、`source_manifest.json`、统计和验证报告。这些文件可能包含真题文字及本机路径，已被 `.gitignore` 排除，不应提交到公共仓库。

学习记录默认保存在 `%USERPROFILE%\.codex\user-data\kaoyan-english-one-sentence-trainer\`，与 Skill 安装目录分离。
