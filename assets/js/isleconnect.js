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

  /* ----------------------------------------------------------- measurement
     Anonymous behavioural events. This is the commercial engine: a venue
     conversation is won with "94 people continued to another stop", not with
     a description of the idea.

     The vocabulary is fixed — thirteen event types, carried over from the
     Vectis ONE concept so the static site, the trail app and any future
     backend all report the same words. Adding a fourteenth is a deliberate
     decision, not a convenience.

     What it deliberately does NOT do:
       · no cookies, and no identifier that outlives the browser tab
       · no names, emails, addresses, IPs or fingerprints
       · nothing at all until an endpoint is configured (see below)
       · nothing at all if the visitor signals Do Not Track / GPC

     To switch it on, add to the page head:
       <meta name="ic-events" content="https://your-endpoint.example/events">
     Until then events accumulate in window.IsleConnect.events so the
     instrumentation can be verified in a browser console without sending
     a single byte anywhere. Add ?ic-debug=1 to log them as they fire. */

  var EVENTS = [
    'page_opened',
    'map_opened',
    'stop_selected',
    'story_started',
    'story_completed',
    'nearby_places_viewed',
    'worked_example_viewed',
    'offer_opened',
    'directions_clicked',
    'menu_clicked',
    'booking_clicked',
    'trail_selected',
    'sponsor_enquiry'
  ];

  var endpointMeta = document.querySelector('meta[name="ic-events"]');
  var ENDPOINT = endpointMeta ? (endpointMeta.getAttribute('content') || '').trim() : '';

  // Honour the visitor's stated preference before anything else.
  var nav = window.navigator || {};
  var optedOut = nav.doNotTrack === '1' || nav.doNotTrack === 'yes' ||
                 window.doNotTrack === '1' || nav.msDoNotTrack === '1' ||
                 nav.globalPrivacyControl === true;

  var debug = window.location.search.indexOf('ic-debug=1') > -1;
  var buffer = [];
  var sending = ENDPOINT !== '' && !optedOut;

  var body = document.body;
  var PAGE = body ? (body.getAttribute('data-ic-page') || 'page') : 'page';

  /* Session scope. A random value in sessionStorage, which the browser drops
     when the tab closes — enough to tell "one visitor opened three stories"
     from "three visitors opened one each", and useless for anything else.
     Only written when events are actually being sent, so a site with no
     endpoint configured writes no storage at all. */

  var SESSION_KEY = 'ic:session';
  var STORIES_KEY = 'ic:stories';

  function store() {
    try { return window.sessionStorage; } catch (err) { return null; }
  }

  function sessionId() {
    if (!sending) return null;
    var s = store();
    if (!s) return null;
    try {
      var id = s.getItem(SESSION_KEY);
      if (!id) {
        id = 's-' + Date.now().toString(36) + '-' +
             Math.floor(Math.random() * 1e9).toString(36);
        s.setItem(SESSION_KEY, id);
      }
      return id;
    } catch (err) { return null; }
  }

  /* Distinct stories opened this session. This is what turns story_started
     into the number that actually sells: "continued to a second story". */
  function noteStory(id) {
    if (!id) return null;
    var s = store();
    if (!s || !sending) return null;
    try {
      var seen = JSON.parse(s.getItem(STORIES_KEY) || '[]');
      if (seen.indexOf(id) === -1) {
        seen.push(id);
        s.setItem(STORIES_KEY, JSON.stringify(seen));
      }
      return seen.length;
    } catch (err) { return null; }
  }

  function context(el) {
    var out = {};
    var story = closestAttr(el, 'data-ic-story');
    var stop = closestAttr(el, 'data-ic-stop');
    var trail = closestAttr(el, 'data-ic-trail');
    if (story) out.storyId = story;
    if (stop) out.stopId = stop;
    if (trail) out.trailId = trail;
    return out;
  }

  function closestAttr(el, attr) {
    var node = el;
    while (node && node.nodeType === 1) {
      if (node.hasAttribute && node.hasAttribute(attr)) {
        return node.getAttribute(attr);
      }
      node = node.parentNode;
    }
    return body && body.getAttribute(attr) ? body.getAttribute(attr) : null;
  }

  function track(type, extra, el) {
    try {
      if (EVENTS.indexOf(type) === -1) return;   // fixed vocabulary, no drift
      var event = { type: type, page: PAGE, timestamp: new Date().toISOString() };
      var ctx = context(el || body);
      for (var k in ctx) { if (ctx.hasOwnProperty(k)) event[k] = ctx[k]; }
      if (extra) {
        for (var j in extra) { if (extra.hasOwnProperty(j)) event[j] = extra[j]; }
      }
      var sid = sessionId();
      if (sid) event.sessionId = sid;

      buffer.push(event);
      if (debug && window.console) window.console.log('[isleconnect:event]', event);
      if (!sending) return;

      var payload = JSON.stringify(event);
      if (nav.sendBeacon) {
        nav.sendBeacon(ENDPOINT, new Blob([payload], { type: 'application/json' }));
        return;
      }
      window.fetch(ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: payload,
        keepalive: true
      });
    } catch (err) {
      // Measurement must never interrupt the experience.
    }
  }

  /* -------------------------------------------------- automatic instrumentation
     Wired by selector so a new page inherits it, and overridable per element
     with data-ic-event="…" where the intent is not obvious from the markup. */

  track('page_opened');

  // Stories. Pressing play is the moment a visitor chose to experience it.
  document.querySelectorAll('.video video').forEach(function (video) {
    var scope = video.closest ? video.closest('[data-ic-story]') : null;
    var id = (scope && scope.getAttribute('data-ic-story')) ||
             (body && body.getAttribute('data-ic-story')) || null;
    var started = false;
    video.addEventListener('play', function () {
      if (started) return;
      started = true;
      var count = noteStory(id);
      track('story_started', count ? { sessionStoryCount: count } : null, video);
    });
    video.addEventListener('ended', function () {
      track('story_completed', null, video);
    });
  });

  // Explicit intent, declared in the markup.
  document.addEventListener('click', function (e) {
    var el = e.target && e.target.closest ? e.target.closest('[data-ic-event]') : null;
    if (!el) return;
    track(el.getAttribute('data-ic-event'), null, el);
  }, true);

  // Onward journeys. A trail stop or another story is the behaviour that
  // proves the network works rather than the single page.
  document.querySelectorAll('.route a, .onward a, .feature__stops a').forEach(function (a) {
    if (a.hasAttribute('data-ic-event')) return;
    a.addEventListener('click', function () { track('stop_selected', null, a); });
  });

  // Seen, not clicked. Two blocks are worth knowing were actually read.
  if ('IntersectionObserver' in window) {
    var seen = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        seen.unobserve(el);
        track(el.classList.contains('nearby') ? 'nearby_places_viewed'
                                              : 'worked_example_viewed', null, el);
      });
    }, { threshold: 0.4 });
    document.querySelectorAll('.nearby, .stats').forEach(function (el) {
      seen.observe(el);
    });
  }

  window.IsleConnect = {
    track: track,
    events: buffer,
    vocabulary: EVENTS,
    enabled: sending,
    reason: sending ? 'sending' : (optedOut ? 'visitor opted out' : 'no endpoint configured')
  };
})();
