const CACHE_NAME = 'avelar-system-v1';
const urlsToCache = [
  '/',
  '/static/style.css',
  '/static/script.js',
  '/offline'
];

// Instalação do SW
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        return cache.addAll(urlsToCache);
      })
  );
});

// Estratégia: Network First (Tenta internet, se falhar, tenta cache)
self.addEventListener('fetch', (event) => {
  event.respondWith(
    fetch(event.request)
      .catch(() => {
        return caches.match(event.request);
      })
  );
});