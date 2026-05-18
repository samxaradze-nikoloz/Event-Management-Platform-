// ══════════════════════════════
//  MOBILE NAV
// ══════════════════════════════
const navToggle = document.getElementById('nav-toggle');
const navLinks  = document.getElementById('nav-links');

if (navToggle && navLinks) {
  navToggle.addEventListener('click', function () {
    navLinks.classList.toggle('open');
  });
  document.addEventListener('click', function (e) {
    if (!navToggle.contains(e.target) && !navLinks.contains(e.target)) {
      navLinks.classList.remove('open');
    }
  });
}

// ── Active nav link ──
const currentPath = window.location.pathname;
document.querySelectorAll('.nav-link').forEach(function (link) {
  const href = link.getAttribute('href');
  if (href && href !== '/' && currentPath.startsWith(href)) {
    link.classList.add('active');
  }
});

// ── Auto-dismiss toasts ──
document.querySelectorAll('.toast').forEach(function (toast) {
  setTimeout(function () {
    toast.style.transition = 'opacity 0.3s, transform 0.3s';
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-6px)';
    setTimeout(function () { toast.remove(); }, 300);
  }, 4000);
});


// ══════════════════════════════
//  GLOBAL LIVE SEARCH
// ══════════════════════════════
(function () {
  const input      = document.getElementById('global-search-input');
  const clearBtn   = document.getElementById('gsearch-clear');
  const resultsBox = document.getElementById('gsearch-results');
  const chipsWrap  = document.getElementById('gsearch-chips');

  if (!input) return;

  let allEvents    = [];   // cached from API
  let allCategories = [];
  let activeType   = '';
  let activeCat    = '';
  let debounceTimer;

  // ── 1. Load categories from API ──
  fetch('/api/categories/')
    .then(function (r) { return r.json(); })
    .then(function (data) {
      const cats = data.results || data;
      allCategories = cats;
      cats.forEach(function (cat) {
        const btn = document.createElement('button');
        btn.className = 'gchip';
        btn.dataset.cat = cat.id;
        btn.textContent = cat.name;
        btn.addEventListener('click', function () {
          document.querySelectorAll('.gchip').forEach(c => c.classList.remove('active'));
          this.classList.add('active');
          activeCat = this.dataset.cat;
          runSearch();
        });
        chipsWrap.appendChild(btn);
      });
    })
    .catch(function () {});

  // ── 2. Load all events once (published only) ──
  fetch('/api/events/?status=published&page_size=200')
    .then(function (r) { return r.json(); })
    .then(function (data) {
      allEvents = data.results || data;
    })
    .catch(function () {});

  // ── 3. Type pills ──
  document.querySelectorAll('.gpill').forEach(function (pill) {
    pill.addEventListener('click', function () {
      document.querySelectorAll('.gpill').forEach(p => p.classList.remove('active'));
      this.classList.add('active');
      activeType = this.dataset.type;
      runSearch();
    });
  });

  // ── 4. Input events ──
  input.addEventListener('input', function () {
    const q = this.value.trim();
    clearBtn.classList.toggle('visible', q.length > 0);
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(runSearch, 200);
  });

  input.addEventListener('focus', function () {
    if (this.value.trim().length > 0) runSearch();
  });

  clearBtn.addEventListener('click', function () {
    input.value = '';
    clearBtn.classList.remove('visible');
    closeResults();
    input.focus();
  });

  // close on outside click
  document.addEventListener('click', function (e) {
    const wrap = document.getElementById('global-search-wrap');
    if (wrap && !wrap.contains(e.target)) closeResults();
  });

  // keyboard nav
  input.addEventListener('keydown', function (e) {
    const items = resultsBox.querySelectorAll('.gsearch-result-item');
    const focused = resultsBox.querySelector('.gsearch-result-item.focused');
    let idx = Array.from(items).indexOf(focused);

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      idx = Math.min(idx + 1, items.length - 1);
      items.forEach(i => i.classList.remove('focused'));
      if (items[idx]) items[idx].classList.add('focused');
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      idx = Math.max(idx - 1, 0);
      items.forEach(i => i.classList.remove('focused'));
      if (items[idx]) items[idx].classList.add('focused');
    } else if (e.key === 'Enter') {
      if (focused) {
        e.preventDefault();
        window.location.href = focused.getAttribute('href');
      } else {
        // fallback: go to events list with search param
        window.location.href = '/events/?search=' + encodeURIComponent(input.value.trim());
      }
    } else if (e.key === 'Escape') {
      closeResults();
    }
  });

  // ── 5. Core search function ──
  function runSearch() {
    const q = input.value.trim().toLowerCase();
    const words = q.split(/\s+/).filter(Boolean);

    if (!q && !activeType && !activeCat) {
      closeResults();
      return;
    }

    let results = allEvents.filter(function (ev) {
      const title = (ev.title || '').toLowerCase();
      const desc  = (ev.description || '').toLowerCase();
      const type  = ev.event_type || '';
      const catId = String(ev.category || '');

      if (words.length && !words.every(w => (title + ' ' + desc).includes(w))) return false;
      if (activeType && type !== activeType) return false;
      if (activeCat && catId !== activeCat) return false;
      return true;
    });

    renderResults(results, words);
  }

  // ── 6. Render dropdown ──
  function renderResults(results, words) {
    resultsBox.innerHTML = '';

    if (results.length === 0) {
      resultsBox.innerHTML = '<div class="gsearch-no-results">No events found. <a href="/events/">Browse all</a></div>';
      resultsBox.classList.add('open');
      return;
    }

    // count row
    const countRow = document.createElement('div');
    countRow.className = 'gsearch-result-count';
    countRow.textContent = results.length + ' result' + (results.length !== 1 ? 's' : '');
    resultsBox.appendChild(countRow);

    // top 8 results
    results.slice(0, 8).forEach(function (ev) {
      const a = document.createElement('a');
      a.className = 'gsearch-result-item';
      a.href = '/events/' + ev.id + '/';

      const emoji = ev.event_type === 'online' ? '🖥️' : '📍';
      const date  = ev.start_date ? new Date(ev.start_date).toLocaleDateString('en-GB', { day:'numeric', month:'short', year:'numeric' }) : '';
      const spots = ev.available_spots > 0 ? ev.available_spots + ' spots left' : 'Full';

      a.innerHTML =
        '<div class="gsearch-result-emoji">' + emoji + '</div>' +
        '<div class="gsearch-result-info">' +
          '<div class="gsearch-result-title">' + highlightText(escHtml(ev.title), words) + '</div>' +
          '<div class="gsearch-result-meta">' +
            '<span>📅 ' + date + '</span>' +
            '<span>' + spots + '</span>' +
            (ev.category_detail ? '<span>' + escHtml(ev.category_detail.name) + '</span>' : '') +
          '</div>' +
        '</div>' +
        '<span class="badge badge-' + ev.event_type + '">' + ev.event_type + '</span>';

      resultsBox.appendChild(a);
    });

    // "see all results" link
    if (results.length > 8) {
      const more = document.createElement('a');
      more.className = 'gsearch-result-item';
      more.href = '/events/?search=' + encodeURIComponent(input.value.trim());
      more.style.justifyContent = 'center';
      more.style.color = 'var(--accent)';
      more.style.fontWeight = '500';
      more.style.fontSize = '13px';
      more.textContent = 'See all ' + results.length + ' results →';
      resultsBox.appendChild(more);
    }

    resultsBox.classList.add('open');
  }

  function closeResults() {
    resultsBox.classList.remove('open');
    resultsBox.innerHTML = '';
  }

  function highlightText(text, words) {
    if (!words.length) return text;
    let result = text;
    words.forEach(function (w) {
      const re = new RegExp('(' + escRe(w) + ')', 'gi');
      result = result.replace(re, '<mark>$1</mark>');
    });
    return result;
  }

  function escHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  function escRe(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

})();