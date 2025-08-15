const MAX_RECENT = 10;

function saveRecent() {
  try {
    const title = (document.querySelector('title')?.textContent || '').trim() || location.pathname;
    const path = location.pathname + location.search;
    const item = { title, path, ts: Date.now() };

    let list = [];
    try { list = JSON.parse(localStorage.getItem('recentPages') || '[]'); } catch (e) {}

    // 중복 제거 후 맨 앞에 삽입
    list = list.filter(x => x.path !== item.path);
    list.unshift(item);
    if (list.length > MAX_RECENT) list = list.slice(0, MAX_RECENT);

    localStorage.setItem('recentPages', JSON.stringify(list));
  } catch (e) {
    console.warn('saveRecent failed:', e);
  }
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
}

function renderRecent(containerId = 'recent-list', emptyText = '최근 본 페이지가 없어요') {
  const el = document.getElementById(containerId);
  if (!el) return;

  let list = [];
  try { list = JSON.parse(localStorage.getItem('recentPages') || '[]'); } catch (e) {}

  if (!list.length) {
    el.innerHTML = `<li class="empty">${emptyText}</li>`;
    return;
  }

  el.innerHTML = list
    .map(i => `<li><a href="${i.path}">${escapeHtml(i.title)}</a></li>`)
    .join('');
}

function clearRecent() {
  localStorage.removeItem('recentPages');
  renderRecent();
}

function saveRecentBenefit(partner) {
  try {
    // 필요한 필드만 추려 저장 (용량↓)
    const item = {
      partner_id: partner.partner_id,
      name: partner.name,
      content: partner.content || '',
      scope: partner.scope || '',
      category_id: partner.category_id || null,
      start_date: partner.start_date || null,
      end_date: partner.end_date || null,
      ts: Date.now()
    };

    let list = JSON.parse(localStorage.getItem('recentBenefits') || '[]');
    list = list.filter(x => x.partner_id !== item.partner_id);
    list.unshift(item);
    if (list.length > MAX_RECENT) list = list.slice(0, MAX_RECENT);
    localStorage.setItem('recentBenefits', JSON.stringify(list));
  } catch(e) { console.warn(e); }
}

function renderRecentBenefits(containerId = 'partnerBox', limit = 5) {
  const box = document.getElementById(containerId);
  if (!box) return;

  let list = [];
  try { list = JSON.parse(localStorage.getItem('recentBenefits') || '[]'); } catch(e) {}
  list = list.slice(0, limit);

  const fmt = (s) => (typeof formatDate === 'function' ? formatDate(s) : s || '');
  if (!list.length) {
    box.innerHTML = '<p>최근 본 혜택이 없습니다.</p>';
    return;
  }

  box.innerHTML = '';
  list.forEach(p => {
    const div = document.createElement('div');
    div.className = 'benefit-item';
    div.innerHTML = `
      <h4>${p.name}</h4>
      <p><strong>내용:</strong> ${p.content.length > 50 ? p.content.slice(0,50) + '...' : p.content}</p>
      <p><strong>범위:</strong> ${p.scope || '—'}</p>
      <p><strong>카테고리:</strong> ${p.category_id ?? '—'}</p>
      <p><strong>기간:</strong> ${fmt(p.start_date)} ~ ${fmt(p.end_date)}</p>
      <button onclick="location.href='/benefit/${p.partner_id}'">상세보기</button>
    `;
    box.appendChild(div);
  });
}

function clearRecentBenefits(){
  localStorage.removeItem('recentBenefits');
  renderRecentBenefits();
}