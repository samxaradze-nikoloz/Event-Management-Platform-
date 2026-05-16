// ── Live search with debounce ──
const searchInput = document.querySelector('.search-input');
if (searchInput) {
  let timer;
  searchInput.addEventListener('input', function () {
    clearTimeout(timer);
    timer = setTimeout(function () {
      document.getElementById('filter-form').submit();
    }, 500);
  });
}

// ── Star rating ──
const stars = document.querySelectorAll('.star-rating .star');
const ratingInput = document.getElementById('rating-input');

if (stars.length && ratingInput) {
  stars.forEach(function (star) {
    star.addEventListener('mouseenter', function () {
      const val = parseInt(this.dataset.val);
      stars.forEach(function (s, i) {
        s.classList.toggle('selected', i < val);
      });
    });

    star.addEventListener('click', function () {
      const val = this.dataset.val;
      ratingInput.value = val;
      stars.forEach(function (s, i) {
        s.classList.toggle('selected', i < parseInt(val));
      });
    });
  });

  document.querySelector('.star-rating').addEventListener('mouseleave', function () {
    const current = parseInt(ratingInput.value) || 0;
    stars.forEach(function (s, i) {
      s.classList.toggle('selected', i < current);
    });
  });
}

// ── Review form toggle ──
const reviewToggle = document.getElementById('review-toggle');
const reviewFormWrap = document.getElementById('review-form-wrap');
const reviewCancel = document.getElementById('review-cancel');

if (reviewToggle && reviewFormWrap) {
  reviewToggle.addEventListener('click', function () {
    const open = reviewFormWrap.style.display === 'block';
    reviewFormWrap.style.display = open ? 'none' : 'block';
    reviewToggle.textContent = open ? '+ Write review' : '✕ Cancel';
  });
}
if (reviewCancel && reviewFormWrap) {
  reviewCancel.addEventListener('click', function () {
    reviewFormWrap.style.display = 'none';
    if (reviewToggle) reviewToggle.textContent = '+ Write review';
  });
}

// ── Auto-dismiss toasts ──
document.querySelectorAll('.toast').forEach(function (toast) {
  setTimeout(function () {
    toast.style.transition = 'opacity 0.3s';
    toast.style.opacity = '0';
    setTimeout(function () { toast.remove(); }, 300);
  }, 4000);
});

// ── Confirm delete ──
document.querySelectorAll('[data-confirm]').forEach(function (btn) {
  btn.addEventListener('click', function (e) {
    if (!confirm(this.dataset.confirm)) e.preventDefault();
  });
});