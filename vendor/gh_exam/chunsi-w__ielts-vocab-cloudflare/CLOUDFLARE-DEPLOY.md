# Cloudflare Pages 部署指南

## 概述

本项目已适配 Cloudflare Pages 静态部署。数据以 JSON 文件形式预构建到 `/data/` 目录，无需后端服务器。

## 部署步骤

### 方法 1: 通过 Cloudflare Dashboard 部署

1. 登录 Cloudflare Dashboard → Pages → Create a project → Connect to Git
2. 选择项目仓库
3. 配置构建:
   - **Framework preset**: Next.js
   - **Build command**: `bash scripts/build-cloudflare.sh`
   - **Build output directory**: `out`
   - **Environment variables**:
     - `NEXT_PUBLIC_STATIC_DATA` = `true`
4. 点击 Deploy

### 方法 2: 通过 Wrangler CLI 部署

```bash
# 安装 wrangler
npm install -g wrangler

# 登录 Cloudflare
wrangler login

# 构建
bash scripts/build-cloudflare.sh

# 部署
wrangler pages deploy out --project-name ielts-vocab
```

## 架构说明

- **静态数据**: 数据库导出为 JSON 文件 (`public/data/`)
  - `stats.json` - 平台统计
  - `groups.json` - 词频分组
  - `words-{A-Z}.json` - 按首字母分块的单词 (26 个文件)
  - `sentences-{0-34}.json` - 按 wordId 范围分块的例句 (35 个文件)
- **客户端数据层** (`src/lib/static-api.ts`): 模拟 API，从 JSON 文件读取数据
- **环境变量** `NEXT_PUBLIC_STATIC_DATA=true`: 启用静态模式，使用 staticApi 替代 API 路由

## 功能特性

- ✅ 34,212 个单词 + 76,332 条真题例句
- ✅ 8 大模块: 首页/浏览/学习(翻卡)/测验/拼写/填空/复习/收藏/设置
- ✅ 深色模式 + PWA 离线支持
- ✅ 艾宾浩斯复习算法
- ✅ 发音跟读 (Web Speech API)
- ✅ 学习成就系统
- ✅ 单词联想图
- ✅ 测验统计仪表盘 + 排行榜
- ✅ 每日目标 + confetti 庆祝
- ✅ 生词本标签 + 导出/导入
- ✅ 移动端底部 tab bar
- ✅ URL hash 路由 (浏览器后退支持)

## 限制

- 静态模式下所有数据在客户端加载 (首屏需加载 ~30MB JSON，分块按需加载)
- 学习进度仅存浏览器 localStorage (不跨设备同步)
- 发音跟读需 Chrome/Edge/Safari
- PWA Service Worker 仅 production 环境注册

## 本地测试静态模式

```bash
# 设置环境变量
export NEXT_PUBLIC_STATIC_DATA=true

# 构建
bash scripts/build-cloudflare.sh

# 本地预览
npx serve out
```
