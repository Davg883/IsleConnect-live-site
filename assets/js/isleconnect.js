/* IsleConnect — V1 behaviour. No framework, no dependencies. */
(function () {
  'use strict';

  var reduced = window.matchMedia &&
                window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------------------------------------------------------------- header */

  var header = document.querySelector('.site-header');
  if (header && header.classList.contains('site-header--over')) {
    var onScroll = function () {
      header.classList.toggle('is-stuck', window.scrollY > 40);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ------------------------------------------------------------ mobile nav */

  var toggle = document.querySelector('.nav-toggle');
  var panel = document.querySelector('.mobile-nav');
  if (toggle && panel) {
    toggle.addEventListener('click', function () {
      var open = panel.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', String(open));
    });
    panel.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') {
        panel.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && panel.classList.contains('is-open')) {
        panel.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.focus();
      }
    });
  }

  /* ------------------------------------------------------------- Then/Now
     Press and hold to reveal the historic plate. Release returns to today.
     The control is a real <button>, so keyboard and screen-reader users get
     the same thing: hold space/enter, or tap it to latch on touch devices. */

  document.querySelectorAll('.thennow').forEach(function (unit) {
    var btn = unit.querySelector('.thennow__hold');
    if (!btn) return;

    var labelHold = btn.getAttribute('data-hold') || 'Hold to see the past';
    var labelBack = btn.getAttribute('data-back') || 'Release for today';
    var pointerGesture = false;   // a press-and-hold is in progress
    var latched = false;          // keyboard/assistive toggle state

    function show() {
      unit.classList.add('is-revealed');
      btn.setAttribute('aria-pressed', 'true');
      btn.querySelector('span').textContent = labelBack;
    }
    function hide() {
      unit.classList.remove('is-revealed');
      btn.setAttribute('aria-pressed', 'false');
      btn.querySelector('span').textContent = labelHold;
    }

    // Mouse and touch: press and hold.
    btn.addEventListener('pointerdown', function (e) {
      e.preventDefault();
      pointerGesture = true;
      latched = false;
      show();
      if (btn.setPointerCapture && e.pointerId != null) {
        try { btn.setPointerCapture(e.pointerId); } catch (err) {}
      }
    });
    ['pointerup', 'pointercancel', 'pointerleave'].forEach(function (evt) {
      btn.addEventListener(evt, function () {
        if (pointerGesture) hide();
      });
    });

    // Keyboard and assistive tech: click toggles, since you cannot "hold" a
    // button with a screen reader. A click that merely follows a pointer
    // press-and-hold is swallowed so the two models never fight.
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      if (pointerGesture) { pointerGesture = false; return; }
      latched = !latched;
      if (latched) show(); else hide();
    });
  });

  /* --------------------------------------------------------- story thread
     Each thread draws itself once, when it scrolls into view. */

  var threads = document.querySelectorAll('.thread');
  if (threads.length) {
    threads.forEach(function (svg) {
      var path = svg.querySelector('path');
      if (path && path.getTotalLength) {
        svg.style.setProperty('--len', Math.ceil(path.getTotalLength()));
      }
    });

    if (reduced || !('IntersectionObserver' in window)) {
      threads.forEach(function (t) { t.classList.add('is-drawn'); });
    } else {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-drawn');
            io.unobserve(entry.target);
          }
        });
      }, { rootMargin: '0px 0px -12% 0px', threshold: 0.2 });
      threads.forEach(function (t) { io.observe(t); });
    }
  }
})();
