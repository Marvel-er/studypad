/* StudyPad · 两个页面共用的 JS 助手
   ------------------------------------------------------------------
   只有 api() / esc() / $() / toast 这几样是真共用的。
   刻意不共用业务逻辑：主页与知识库的交互模型本来就不同，
   硬凑成一个「组件库」反而会让两页互相牵制。

   加载方式：<script src="/static/common.js"></script>（放在页面 script 之前）。
   ⚠ 项目零 CDN 依赖，公共层也是同源本地文件，不引任何外部资源。
*/
'use strict';

var $ = function (id) { return document.getElementById(id); };

function esc(s) {
  return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
  });
}

// ⚠ 不能假设「非 2xx 就一定是 JSON」（2026-10-15 用户截图反馈过）：
// FastAPI 对**未捕获异常**返回的 500 是**纯文本** `Internal Server Error`，
// 这时 r.json() 会抛 `SyntaxError: Unexpected token 'I', "Internal S"...`，
// 用户看到的就是那句解析错误，而不是真正的原因 —— 等于把病因藏起来了。
// 所以：先拿文本，再尝试按 JSON 解；解不出来就原样显示，并带上状态码。
// 5xx 额外提示去看服务端日志（traceback 只在那里）。
function apiError(r, raw) {
  var msg = '';
  try { msg = (JSON.parse(raw) || {}).detail || ''; } catch (e) { /* 非 JSON，走文本分支 */ }
  if (!msg) msg = (raw || '').replace(/\s+/g, ' ').trim().slice(0, 300);
  var head = 'HTTP ' + r.status + (r.status >= 500 ? '（服务端内部错误）' : '');
  if (r.status >= 500) head += '，traceback 见服务端日志 out/_server.log';
  return msg ? head + '：' + msg : head;
}

function api(path, opts) {
  return fetch(path, opts).then(function (r) {
    if (!r.ok) {
      return r.text().then(function (raw) { throw new Error(apiError(r, raw)); });
    }
    return r.json();
  });
}

// 取**原始文本**响应（HTML / CSV 这类不是 JSON 的接口）。
//
// 存在的理由（2026-10-15 用户反馈「从知识库打开历史手账一片空白」）：
// 手账的 HTML 是**服务端现渲染**的（`library.save_handbook` 刻意不存 `hb["html"]`，
// 只存结构化 JSON），要拿它只能打 `/api/library/<id>/html`。
// 而 `api()` 固定走 `r.json()`，用它取 HTML 会直接抛解析错 —— 于是当时那段代码
// 退而求其次用了「不带 html 的 JSON 记录」，把 `undefined` 喂进了 iframe。
function apiText(path, opts) {
  return fetch(path, opts).then(function (r) {
    return r.text().then(function (raw) {
      if (!r.ok) throw new Error(apiError(r, raw));
      return raw;
    });
  });
}

function fmtDateTime(ts) {
  if (!ts) return '';
  var d = new Date(ts * 1000);
  function p(n) { return (n < 10 ? '0' : '') + n; }
  return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate())
    + ' ' + p(d.getHours()) + ':' + p(d.getMinutes());
}

// ---------------- 主题（白天 / 黑夜）
//
// 三种取值：
//   light  强制白天
//   dark   强制黑夜
//   auto   跟随系统（默认）。用户没表态时按系统走，
//          晚上开着深色系统的用户不该被一屋子白卡片晃眼。
var THEME_KEY = 'studypad.theme';

function themeSystemDark() {
  return !!(window.matchMedia
    && window.matchMedia('(prefers-color-scheme: dark)').matches);
}

function themeResolved() {
  var t = null;
  try { t = localStorage.getItem(THEME_KEY); } catch (e) { t = null; }
  if (t !== 'dark' && t !== 'light') t = 'auto';
  return t === 'auto' ? (themeSystemDark() ? 'dark' : 'light') : t;
}

function themeApply(t) {
  var eff = t === 'auto' ? (themeSystemDark() ? 'dark' : 'light') : t;
  // 只在**实际生效值**上写属性：auto + 白天时把 data-theme 设成 "light"，
  // 这样 CSS 里 `[data-theme="dark"]` 的覆盖块不会误命中。
  document.documentElement.setAttribute('data-theme', eff);
  var b = document.getElementById('btnTheme');
  if (b) {
    b.setAttribute('data-mode', t);
    b.title = { light: '当前：白天模式（点击切到黑夜）',
                dark: '当前：黑夜模式（点击切到白天）',
                auto: '当前：跟随系统（点击固定为白天）' }[t];
    b.setAttribute('aria-label', b.title);
  }
  // 同一份状态也写进 meta，导出的静态页能带上主题
  var m = document.querySelector('meta[name="theme-color"]');
  if (m) m.setAttribute('content', eff === 'dark' ? '#14161a' : '#f6f7f9');
  // 通知页面：预览里的 iframe / 已渲染的内容需要跟着重绘。
  // 用自定义事件而不是让 common.js 直接改 DOM —— 公共层不认识
  // 手账预览这种东西，耦合进去会让它变成垃圾桶。
  try {
    document.dispatchEvent(new CustomEvent('studypad:theme',
      { detail: { mode: t, eff: eff } }));
  } catch (e) { /* 老浏览器没有 CustomEvent 构造器，忽略 */ }
}

function themeCycle() {
  var cur = 'auto';
  try { cur = localStorage.getItem(THEME_KEY) || 'auto'; } catch (e) { /* 无痕模式 */ }
  // auto → light → dark → auto。只在 light/dark 之间循环也可以，
  // 但那样「跟随系统」这个默认态就再也回不去了。
  var next = cur === 'auto' ? 'light' : (cur === 'light' ? 'dark' : 'auto');
  try { localStorage.setItem(THEME_KEY, next); } catch (e) { /* 无痕模式：不记 */ }
  themeApply(next);
}

// 跟随系统时，系统主题变了要实时跟上（用户从「自动」切到夜间）
(function () {
  if (!window.matchMedia) return;
  var mq = window.matchMedia('(prefers-color-scheme: dark)');
  var onChange = function () {
    var t = null;
    try { t = localStorage.getItem(THEME_KEY); } catch (e) { /* 无痕模式 */ }
    if (t !== 'dark' && t !== 'light') themeApply('auto');
  };
  if (mq.addEventListener) mq.addEventListener('change', onChange);
  else if (mq.addListener) mq.addListener(onChange);   // 老 Safari
})();

document.addEventListener('DOMContentLoaded', function () {
  var b = document.getElementById('btnTheme');
  if (b) b.onclick = themeCycle;
  var t = 'auto';
  try { t = localStorage.getItem(THEME_KEY); } catch (e) { /* 无痕模式 */ }
  themeApply(t);
});

// 顶栏当前页高亮：按 <body data-page> 标记，避免两处各写一套判断
(function () {
  var page = document.body.getAttribute('data-page');
  if (!page) return;
  Array.prototype.forEach.call(document.querySelectorAll('.nav a[data-p]'), function (a) {
    if (a.getAttribute('data-p') === page) a.classList.add('on');
  });
})();

// 键盘可达性：Ctrl/Cmd+K 跳到本页搜索框。
// 复习时通常是「找那个词」，有搜索框却要先去点一下鼠标是多余的一步。
(function () {
  document.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')) {
      var s = document.querySelector('[data-search]');
      if (!s) return;
      e.preventDefault();
      s.focus();
      s.select();
    }
  });
})();