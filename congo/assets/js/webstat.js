// webstat beacon for www.kiils.dk, after the one on klimaleksikon.dk
// (klimaleksikon repo, tools/drupal/klimaleksikon_webstat/js/webstat.js).
// GitHub Pages runs no code, so there is no first-party collector here: the
// beacons go straight to webstat as text/plain (no CORS preflight). Ad
// blockers may stop some of them, and webstat cannot see the reader's IP
// through cross.stream's proxy, so views are counted but visitors are not.
// No cookies; nothing is stored on the reader's device.
//
// Reports: the page view; reading 50 and 100 percent of an article; the
// seconds the page was visible; contact clicks (/kontakt/, mail, phone).
(function () {
  if (!navigator.sendBeacon || navigator.webdriver || document.visibilityState === 'prerender') { return; }
  var collector = 'https://webstat.kiil.cross.stream/hit';
  var view = Math.random().toString(36).slice(2, 10);
  var path = location.pathname;
  try { path = decodeURIComponent(path); } catch (e) {}

  function send(kind, extra) {
    var data = {kind: kind, view: view, path: path};
    for (var k in extra) { data[k] = extra[k]; }
    navigator.sendBeacon(collector, new Blob([JSON.stringify(data)], {type: 'text/plain'}));
  }

  function hostOf(url) {
    try { return new URL(url).hostname.replace(/^www\./, ''); } catch (e) { return ''; }
  }

  function start() {
    var heading = document.querySelector('h1');
    var here = location.hostname.replace(/^www\./, '');
    var refHost = hostOf(document.referrer);
    var from = null;
    if (refHost === here) {
      try { from = decodeURIComponent(new URL(document.referrer).pathname); } catch (e) {}
    }
    var section = path.split('/')[1] || '';
    var width = window.innerWidth;
    send('view', {
      type: /^[a-z_-]{1,40}$/.test(section) ? section : null,
      title: heading ? heading.textContent.trim() : null,
      ref: refHost && refHost !== here ? refHost : null,
      from: from,
      device: width < 768 ? 'mobile' : width < 1200 ? 'tablet' : 'desktop',
      lang: document.documentElement.lang || null
    });

    // Reading depth through an article: halfway and the end.
    var body = document.querySelector('.article-content');
    if (body) {
      var reached = {};
      var waiting = false;
      var depth = function () {
        var box = body.getBoundingClientRect();
        var seen = (window.innerHeight - box.top) / Math.max(box.height, 1);
        [50, 100].forEach(function (d) {
          if (!reached[d] && seen >= (d === 100 ? 0.95 : 0.5)) { reached[d] = true; send('read', {depth: d}); }
        });
        if (reached[100]) { window.removeEventListener('scroll', onScroll); }
      };
      var onScroll = function () {
        if (waiting) { return; }
        waiting = true;
        setTimeout(function () { waiting = false; depth(); }, 250);
      };
      window.addEventListener('scroll', onScroll, {passive: true});
      depth();
    }

    // Contact clicks: the contact page, mail and phone. The target is the
    // path, or "mail" or "phone" (never the address itself).
    document.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a[href]');
      if (!a) { return; }
      var url;
      try { url = new URL(a.href); } catch (err) { return; }
      var target = null;
      if (url.protocol === 'mailto:') {
        target = 'mail';
      } else if (url.protocol === 'tel:') {
        target = 'phone';
      } else if (url.hostname.replace(/^www\./, '') === here && /^(\/en)?\/(kontakt|contact)/.test(url.pathname)) {
        target = url.pathname;
      }
      if (target) { send('click', {target: target}); }
    }, true);
  }

  // Seconds the page was visible, sent each time it is hidden (the latest
  // report per view counts).
  var visibleSince = document.visibilityState === 'visible' ? Date.now() : null;
  var visible = 0;
  document.addEventListener('visibilitychange', function () {
    if (document.visibilityState === 'hidden') {
      if (visibleSince) { visible += Date.now() - visibleSince; visibleSince = null; }
      var seconds = Math.round(visible / 1000);
      if (seconds >= 1) { send('leave', {seconds: Math.min(seconds, 7200)}); }
    } else {
      visibleSince = Date.now();
    }
  });

  if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', start); } else { start(); }
})();
