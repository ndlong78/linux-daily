(() => {
  const input = document.querySelector('#archive-search');
  const status = document.querySelector('#search-status');
  const results = document.querySelector('#search-results');
  const groups = document.querySelector('#archive-groups');
  if (!input || !status || !results || !groups) return;

  let posts = [];
  const normalize = (value) => value.toLocaleLowerCase('vi').normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  const haystack = (post) => normalize([post.title, post.lede, post.axis_label, ...(post.tags || [])].join(' '));

  const render = (matches, query) => {
    results.replaceChildren();
    if (!query) {
      results.hidden = true;
      groups.hidden = false;
      status.textContent = `Nhập từ khóa để lọc ${posts.length} bài.`;
      return;
    }
    groups.hidden = true;
    results.hidden = false;
    status.textContent = `${matches.length} kết quả cho “${query}”.`;
    if (!matches.length) {
      const p = document.createElement('p');
      p.className = 'empty';
      p.textContent = 'Không tìm thấy bài phù hợp.';
      results.append(p);
      return;
    }
    const list = document.createElement('div');
    list.className = 'archive-list';
    for (const post of matches) {
      const a = document.createElement('a');
      a.className = 'archive-item';
      a.href = post.href;
      const meta = document.createElement('span');
      meta.className = 'archive-meta';
      meta.textContent = `#${String(post.issue).padStart(3, '0')} · ${post.axis_label} · ${post.date}`;
      const strong = document.createElement('strong');
      strong.textContent = post.title;
      const lede = document.createElement('span');
      lede.textContent = post.lede;
      a.append(meta, strong, lede);
      list.append(a);
    }
    results.append(list);
  };

  fetch('search-index.json', {cache: 'no-store'})
    .then((response) => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    })
    .then((payload) => {
      posts = Array.isArray(payload.posts) ? payload.posts : [];
      status.textContent = `Nhập từ khóa để lọc ${posts.length} bài.`;
      input.addEventListener('input', () => {
        const raw = input.value.trim();
        const terms = normalize(raw).split(/\s+/).filter(Boolean);
        const matches = terms.length ? posts.filter((post) => terms.every((term) => haystack(post).includes(term))) : posts;
        render(matches, raw);
      });
    })
    .catch(() => {
      input.disabled = true;
      status.textContent = 'Không tải được chỉ mục tìm kiếm; bạn vẫn có thể duyệt archive bên dưới.';
    });
})();
