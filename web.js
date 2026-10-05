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
