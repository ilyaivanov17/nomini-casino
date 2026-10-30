(function () {
  'use strict';

  var menuBtn = document.getElementById('mobile-menu-btn');
  var mobileMenu = document.getElementById('mobile-menu');
  if (menuBtn && mobileMenu) {
    menuBtn.addEventListener('click', function () {
      var open = mobileMenu.classList.toggle('hidden') === false;
      menuBtn.setAttribute('aria-expanded', String(open));
    });
    mobileMenu.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        mobileMenu.classList.add('hidden');
        menuBtn.setAttribute('aria-expanded', 'false');
      });
    });
  }

  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      var href = this.getAttribute('href');
      if (!href || href === '#') return;
      var target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  /* Horizontal lobby rails */
  document.querySelectorAll('[data-scroll]').forEach(function (button) {
    button.addEventListener('click', function () {
      var track = document.getElementById(button.getAttribute('data-scroll'));
      if (!track) return;
      var direction = Number(button.getAttribute('data-dir') || 1);
      var step = Math.min(Math.max(220, track.clientWidth * 0.72), 520);
      track.scrollBy({ left: direction * step, behavior: 'smooth' });
    });
  });

  /* Small interactive favorite buttons — visual only */
  document.querySelectorAll('.game-fav').forEach(function (button) {
    button.addEventListener('click', function () {
      var active = button.classList.toggle('is-saved');
      button.textContent = active ? '★' : '☆';
      button.setAttribute('aria-pressed', String(active));
      button.style.color = active ? '#ffd22b' : '';
    });
  });

  /* Local game search */
  var search = document.getElementById('lobby-search');
  var cards = Array.prototype.slice.call(document.querySelectorAll('.lobby-game-card[data-search]'));
  if (search && cards.length) {
    var noResults = document.createElement('div');
    noResults.className = 'lobby-no-results';
    noResults.textContent = 'Keine passenden Spiele in dieser Auswahl gefunden.';
    noResults.hidden = true;

    var track = cards[0].closest('.lobby-track');
    if (track) track.parentNode.insertBefore(noResults, track.nextSibling);
    var lang = (document.documentElement.getAttribute('lang') || 'de').slice(0,2);
    var noResultText = { de: 'Keine passenden Spiele in dieser Auswahl gefunden.', en: 'No matching games were found in this selection.', fr: 'Aucun jeu correspondant dans cette sélection.', es: 'No hay juegos que coincidan en esta selección.' };
    noResults.textContent = noResultText[lang] || noResultText.en;

    search.addEventListener('input', function () {
      var query = search.value.trim().toLowerCase();
      var visible = 0;
      cards.forEach(function (card) {
        var matches = !query || card.getAttribute('data-search').indexOf(query) !== -1;
        card.classList.toggle('search-hidden', !matches);
        if (matches) visible += 1;
      });
      noResults.hidden = visible !== 0 || !query;
    });
  }

  /* Random game button */
  var randomBtn = document.getElementById('random-game');
  if (randomBtn && cards.length) {
    randomBtn.addEventListener('click', function () {
      var visibleCards = cards.filter(function (card) {
        return !card.classList.contains('search-hidden');
      });
      var pool = visibleCards.length ? visibleCards : cards;
      var chosen = pool[Math.floor(Math.random() * pool.length)];
      var track = chosen.closest('.lobby-track');

      if (track) {
        track.scrollTo({ left: Math.max(0, chosen.offsetLeft - track.offsetLeft - 20), behavior: 'smooth' });
      }
      chosen.animate([
        { transform: 'translateY(0)' },
        { transform: 'translateY(-6px)' },
        { transform: 'translateY(0)' }
      ], { duration: 420, easing: 'ease-out' });
    });
  }

  /* Category chips */
  document.querySelectorAll('.lobby-category-chip[href^="#"]').forEach(function (chip) {
    chip.addEventListener('click', function () {
      document.querySelectorAll('.lobby-category-chip').forEach(function (item) {
        item.classList.remove('is-active');
      });
      chip.classList.add('is-active');
    });
  });

  /* Promo-code copy buttons */
  document.querySelectorAll('[data-copy-code]').forEach(function (button) {
    button.addEventListener('click', function () {
      var code = button.getAttribute('data-copy-code') || '';
      var status = button.parentElement.querySelector('.promo-code-status');
      var copyLabel = button.getAttribute('data-copy-label') || 'Copy code';
      var copiedLabel = button.getAttribute('data-copied-label') || 'Copied';
      var failLabel = button.getAttribute('data-copy-fail-label') || 'Copy manually';

      function showResult(success) {
        if (status) status.textContent = success ? copiedLabel : failLabel + ': ' + code;
        button.textContent = success ? copiedLabel : failLabel;
        button.setAttribute('aria-label', (success ? copiedLabel : failLabel) + ': ' + code);
        window.setTimeout(function () {
          button.textContent = copyLabel;
          button.setAttribute('aria-label', copyLabel + ': ' + code);
          if (status) status.textContent = '';
        }, 2200);
      }

      if (navigator.clipboard && window.isSecureContext && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(code).then(function () { showResult(true); }).catch(function () { fallbackCopy(); });
      } else {
        fallbackCopy();
      }

      function fallbackCopy() {
        var field = document.createElement('textarea');
        field.value = code;
        field.setAttribute('readonly', '');
        field.style.position = 'absolute';
        field.style.left = '-9999px';
        document.body.appendChild(field);
        field.select();
        var success = false;
        try { success = document.execCommand('copy'); } catch (e) { success = false; }
        document.body.removeChild(field);
        showResult(success);
      }
    });
  });

  /* Cookie consent */
  var banner = document.getElementById('cookie-banner');
  var accept = document.getElementById('cookie-accept');
  var decline = document.getElementById('cookie-decline');
  var settings = document.getElementById('cookie-settings');
  var panel = document.getElementById('cookie-settings-panel');
  var saveSettings = document.getElementById('cookie-save-settings');
  var analytics = document.getElementById('cookie-analytics');
  var marketing = document.getElementById('cookie-marketing');

  function readPrefs() {
    try {
      var raw = localStorage.getItem('cookie_preferences');
      return raw ? JSON.parse(raw) : null;
    } catch (e) { return null; }
  }

  function savePrefs(prefs) {
    try { localStorage.setItem('cookie_preferences', JSON.stringify(prefs)); } catch (e) {}
    if (banner) banner.classList.add('hidden');
    if (panel) panel.classList.add('hidden');
    if (settings) settings.setAttribute('aria-expanded', 'false');
  }

  if (banner) {
    var prefs = readPrefs();
    if (!prefs) {
      banner.classList.remove('hidden');
    } else {
      if (analytics) analytics.checked = prefs.analytics === true;
      if (marketing) marketing.checked = prefs.marketing === true;
    }
    if (accept) accept.addEventListener('click', function () { savePrefs({ necessary: true, analytics: true, marketing: true }); });
    if (decline) decline.addEventListener('click', function () { savePrefs({ necessary: true, analytics: false, marketing: false }); });
    if (settings) settings.addEventListener('click', function () {
      var isHidden = panel.classList.toggle('hidden');
      settings.setAttribute('aria-expanded', String(!isHidden));
    });
    if (saveSettings) saveSettings.addEventListener('click', function () {
      savePrefs({ necessary: true, analytics: !!(analytics && analytics.checked), marketing: !!(marketing && marketing.checked) });
    });
  }
})();
