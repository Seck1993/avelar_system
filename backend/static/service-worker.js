const CACHE_NAME = 'avelar-system-v1';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/img/Logo.png',
  '/offline'
];

// Instalação do SW
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Cache aberto');
        return cache.addAll(urlsToCache);
      })
  );
});

// Estratégia: Network First (Tenta internet, se falhar, tenta cache)
self.addEventListener('fetch', (event) => {
  event.respondWith(
    fetch(event.request)
      .catch(() => {
        return caches.match(event.request)
          .then((response) => {
            if (response) {
              return response;
            }
            // Se a requisição for uma página (navegação), retorna a página offline
            if (event.request.mode === 'navigate') {
              return caches.match('/offline');
            }
          });
      })
  );
});

// Atualização do SW (Limpeza de caches antigos)
self.addEventListener('activate', (event) => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});