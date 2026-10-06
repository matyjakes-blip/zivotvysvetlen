/* Život vysvětlen · drobnosti, které potřebují JavaScript.
   Bez JavaScriptu všechno funguje taky (video se otevře na YouTube, menu je <details>). */
(function () {
  // video: iframe z YouTube se vloží až po kliknutí, do té doby se nic nenačítá
  document.querySelectorAll('.video-spust').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var src = a.getAttribute('data-video');
      if (!src) return;
      e.preventDefault();
      var f = document.createElement('iframe');
      f.src = src;
      f.title = 'Život vysvětlen · video';
      f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      f.allowFullscreen = true;
      a.parentNode.replaceChild(f, a);
    });
  });

  // proměna: posuvník před / po (tah myší nebo prstem do stran, šipky na klávesnici)
  document.querySelectorAll('.posuvnik').forEach(function (box) {
    var vstup = box.querySelector('.posuvnik-ovladac');
    var tahne = false;
    function nastav(pct) {
      pct = Math.max(0, Math.min(100, pct));
      box.style.setProperty('--pozice', pct + '%');
      if (vstup) vstup.value = Math.round(pct);
    }
    function zBodu(x) {
      var r = box.getBoundingClientRect();
      nastav((x - r.left) / r.width * 100);
    }
    box.addEventListener('pointerdown', function (e) {
      tahne = true; zBodu(e.clientX);
      if (box.setPointerCapture) box.setPointerCapture(e.pointerId);
    });
    box.addEventListener('pointermove', function (e) { if (tahne) zBodu(e.clientX); });
    ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(function (t) {
      box.addEventListener(t, function () { tahne = false; });
    });
    if (vstup) vstup.addEventListener('input', function () { nastav(+vstup.value); });
  });

  // proměna: přepínač Pleť / Postava (bez JavaScriptu jsou vidět oba posuvníky pod sebou)
  var tlacitka = document.querySelectorAll('.prepinac-tl');
  function ukazPar(klic) {
    document.querySelectorAll('.promena .posuvnik').forEach(function (p) { p.hidden = p.getAttribute('data-par') !== klic; });
    tlacitka.forEach(function (t) { t.setAttribute('aria-pressed', t.getAttribute('data-par') === klic ? 'true' : 'false'); });
  }
  if (tlacitka.length) {
    tlacitka.forEach(function (t) { t.addEventListener('click', function () { ukazPar(t.getAttribute('data-par')); }); });
    ukazPar(tlacitka[0].getAttribute('data-par'));
  }

  // okno „Co se změnilo a proč": záložky (bez JavaScriptu jsou všechny texty pod sebou)
  var zalozky = document.querySelectorAll('.zalozka');
  function ukazPanel(klic) {
    document.querySelectorAll('.panel').forEach(function (p) { p.hidden = p.getAttribute('data-panel') !== klic; });
    zalozky.forEach(function (z) { z.setAttribute('aria-selected', z.getAttribute('data-zalozka') === klic ? 'true' : 'false'); });
  }
  if (zalozky.length) {
    document.documentElement.classList.add('js');
    zalozky.forEach(function (z) { z.addEventListener('click', function () { ukazPanel(z.getAttribute('data-zalozka')); }); });
    ukazPanel(zalozky[0].getAttribute('data-zalozka'));
  }

  // okna přes #odkaz (Respekt, Co se změnilo a proč): zavřít klávesou Esc
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var okno = document.querySelector('.clanek:target');
    var zpet = okno && okno.querySelector('.clanek-zavrit');
    if (zpet) location.hash = zpet.getAttribute('href');
  });

  // menu na telefonu: zavřít klepnutím vedle nebo klávesou Esc
  var menu = document.querySelector('.menu');
  if (menu) {
    document.addEventListener('click', function (e) {
      if (menu.open && !menu.contains(e.target)) menu.open = false;
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') menu.open = false;
    });
  }
})();
