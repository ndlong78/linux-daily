// Harness chạy assets/search.js trong Node với DOM giả, để đo số lần chuẩn hóa chuỗi.
//
// String.prototype.normalize là thao tác đắt nhất trong search.js (kèm toLocaleLowerCase
// + regex bỏ dấu). Đếm số lần gọi cho biết chỉ mục có được dựng sẵn một lần hay bị tính
// lại theo từng term × từng bài × từng keystroke.
//
// Dùng: node search_harness.mjs <đường-dẫn-search.js> <số-bài> <số-keystroke>
import {readFileSync} from 'node:fs';

const [scriptPath, postCountRaw, keystrokesRaw] = process.argv.slice(2);
const postCount = Number(postCountRaw);
const keystrokes = Number(keystrokesRaw);

let normalizeCalls = 0;
const nativeNormalize = String.prototype.normalize;
String.prototype.normalize = function (...args) {
  normalizeCalls += 1;
  return nativeNormalize.apply(this, args);
};

const makeNode = () => {
  const node = {
    children: [],
    hidden: false,
    disabled: false,
    textContent: '',
    className: '',
    href: '',
    value: '',
    listeners: {},
    append(...kids) { node.children.push(...kids); },
    replaceChildren(...kids) { node.children = kids; },
    addEventListener(type, fn) { (node.listeners[type] ||= []).push(fn); },
    dispatch(type) { (node.listeners[type] || []).forEach((fn) => fn()); },
  };
  return node;
};

const input = makeNode();
const status = makeNode();
const results = makeNode();
const groups = makeNode();

globalThis.document = {
  querySelector: (selector) => ({
    '#archive-search': input,
    '#search-status': status,
    '#search-results': results,
    '#archive-groups': groups,
  }[selector] ?? null),
  createElement: () => makeNode(),
};

const posts = Array.from({length: postCount}, (_, i) => ({
  issue: i + 1,
  href: `posts/post-${String(i + 1).padStart(3, '0')}-demo.html`,
  title: i === 0 ? 'Cấu hình tường lửa' : `Bài số ${i + 1}`,
  lede: 'Mô tả ngắn cho bài viết.',
  axis_label: 'Networking',
  date: '01·01·2026',
  tags: ['linux'],
}));

globalThis.fetch = () => Promise.resolve({ok: true, json: () => Promise.resolve({posts})});

// search.js là IIFE, không export gì; eval trong scope hiện tại là đủ.
(0, eval)(readFileSync(scriptPath, 'utf8'));

const settle = () => new Promise((resolve) => setTimeout(resolve, 250));

await settle();
const afterLoad = normalizeCalls;

// Gõ dần "tường" — mỗi keystroke là một sự kiện input.
const query = 'tường';
for (let i = 1; i <= keystrokes; i += 1) {
  input.value = query.slice(0, i);
  input.dispatch('input');
}
await settle();

const flat = (node) => node.children.flatMap((kid) => [kid, ...flat(kid)]);
const rendered = flat(results).filter((node) => node.className === 'archive-item').length;

console.log(JSON.stringify({
  afterLoad,
  total: normalizeCalls,
  rendered,
  statusText: status.textContent,
}));
