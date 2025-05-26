const CACHE_NAME = 'registro-compras-cache-v1';
const urlsToCache = [
  '/',
  '/registrar',
  '/ver',
  '/static/styles.css',  // si tienes CSS separado
  // Añade aquí todos los archivos estáticos importantes que uses
];

// Instalación: cachear recursos esenciales
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

// Activación: limpiar caches antiguas
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => 
      Promise.all(keys.filter(key => key !== CACHE_NAME)
                     .map(key => caches.delete(key)))
    )
  );
});

// Fetch: responder con cache o hacer fetch normal
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
