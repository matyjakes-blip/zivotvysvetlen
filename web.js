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

  // proměna: přepínač (starý: data-par; nový: Obličej / Postava + věk). Bez JavaScriptu jsou vidět všechny posuvníky pod sebou.
  var tlacitka = document.querySelectorAll('.prepinac-tl[data-par]');
  function ukazPar(klic) {
    document.querySelectorAll('.promena .posuvnik').forEach(function (p) { p.hidden = p.getAttribute('data-par') !== klic; });
    tlacitka.forEach(function (t) { t.setAttribute('aria-pressed', t.getAttribute('data-par') === klic ? 'true' : 'false'); });
  }
  if (tlacitka.length) {
    tlacitka.forEach(function (t) { t.addEventListener('click', function () { ukazPar(t.getAttribute('data-par')); }); });
    ukazPar(tlacitka[0].getAttribute('data-par'));
  }
  var rezTl = document.querySelectorAll('.prepinac-tl[data-rezim]'), vekTl = document.querySelectorAll('.prepinac-tl[data-vek]');
  var pary = document.querySelectorAll('.promena .posuvnik[data-rezim]');
  if (rezTl.length && pary.length) {
    var stav = { rezim: rezTl[0].getAttribute('data-rezim'), vek: '18' };
    var existuje = function (r, v) {
      return [].some.call(pary, function (p) { return p.getAttribute('data-rezim') === r && p.getAttribute('data-vek') === v; });
    };
    var ukaz = function () {
      if (!existuje(stav.rezim, stav.vek)) {
        [].some.call(vekTl, function (t) { if (existuje(stav.rezim, t.getAttribute('data-vek'))) { stav.vek = t.getAttribute('data-vek'); return true; } });
      }
      pary.forEach(function (p) { p.hidden = !(p.getAttribute('data-rezim') === stav.rezim && p.getAttribute('data-vek') === stav.vek); });
      rezTl.forEach(function (t) { t.setAttribute('aria-pressed', t.getAttribute('data-rezim') === stav.rezim ? 'true' : 'false'); });
      vekTl.forEach(function (t) {
        t.hidden = !existuje(stav.rezim, t.getAttribute('data-vek'));
        t.setAttribute('aria-pressed', t.getAttribute('data-vek') === stav.vek ? 'true' : 'false');
      });
    };
    rezTl.forEach(function (t) { t.addEventListener('click', function () { stav.rezim = t.getAttribute('data-rezim'); ukaz(); }); });
    vekTl.forEach(function (t) { t.addEventListener('click', function () { stav.vek = t.getAttribute('data-vek'); ukaz(); }); });
    ukaz();
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

  // úvod: fotky k přetáčení (šipky, tečky, prst)
  document.querySelectorAll('.uvod-karusel').forEach(function (k) {
    var pas = k.querySelector('.uvod-pas'), tecky = k.querySelectorAll('.uvod-tecky button');
    function index() { return Math.round(pas.scrollLeft / pas.clientWidth); }
    function jdi(i) {
      var cil = i * pas.clientWidth;
      pas.scrollTo({ left: cil, behavior: document.hidden ? 'auto' : 'smooth' });
      setTimeout(function () { if (Math.abs(pas.scrollLeft - cil) > 4) pas.scrollLeft = cil; }, 700);
    }
    k.querySelector('.predchozi').addEventListener('click', function () { jdi(Math.max(0, index() - 1)); });
    k.querySelector('.dalsi').addEventListener('click', function () { jdi(Math.min(tecky.length - 1, index() + 1)); });
    tecky.forEach(function (t, i) { t.addEventListener('click', function () { jdi(i); }); });
    pas.addEventListener('scroll', function () {
      var i = index();
      tecky.forEach(function (t, j) { if (j === i) t.setAttribute('aria-current', 'true'); else t.removeAttribute('aria-current'); });
    }, { passive: true });
  });

  // recenze: zastavit pod prstem
  document.querySelectorAll('.recenze-okno').forEach(function (o) {
    o.addEventListener('touchstart', function () { o.classList.add('stuj'); }, { passive: true });
    o.addEventListener('touchend', function () { o.classList.remove('stuj'); });
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
