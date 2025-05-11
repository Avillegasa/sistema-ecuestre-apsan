/* eslint-disable no-restricted-globals */

// Nombre de la caché
const CACHE_NAME = 'ecuestre-cache-v1';

// Recursos estáticos para almacenar en caché
const STATIC_RESOURCES = [
  '/', 
  '/index.html', 
  '/static/js/main.bundle.js', 
  '/static/css/main.chunk.css',
  '/manifest.json',
  '/favicon.ico',
];

// Instalar service worker
self.addEventListener('install', (event) => {
  console.log('Service Worker instalado');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Caché abierta');
        return cache.addAll(STATIC_RESOURCES);
      })
      .then(() => self.skipWaiting())
  );
});

// Activar service worker
self.addEventListener('activate', (event) => {
  console.log('Service Worker activado');
  // Limpiar cachés antiguas
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Eliminando caché antigua:', cacheName);
            return caches.delete(cacheName);
          }
          return null;
        })
      );
    })
  );
  // Tomar control de clientes sin recargar
  return self.clients.claim();
});

// Interceptar solicitudes de red
self.addEventListener('fetch', (event) => {
  // Omitir solicitudes de API o Firebase
  if (event.request.url.includes('/api/') || 
      event.request.url.includes('firebaseio.com')) {
    return;
  }

  // Estrategia: Stale-while-revalidate
  event.respondWith(
    caches.match(event.request)
      .then((cachedResponse) => {
        // Usar caché mientras se busca en la red
        const fetchPromise = fetch(event.request)
          .then((networkResponse) => {
            // Si la respuesta es válida, actualizar caché
            if (networkResponse && networkResponse.status === 200) {
              const responseToCache = networkResponse.clone();
              caches.open(CACHE_NAME)
                .then((cache) => {
                  cache.put(event.request, responseToCache);
                });
            }
            return networkResponse;
          })
          .catch(() => {
            console.log('Fallback a respuesta de caché para:', event.request.url);
            return cachedResponse;
          });

        return cachedResponse || fetchPromise;
      })
  );
});

// Sincronizar datos cuando vuelve la conexión
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-scores') {
    console.log('Sincronizando calificaciones pendientes');
    // La sincronización real se maneja en el código de la aplicación
    // usando IndexedDB y el hook useOffline
  }
});

// Manejo de notificaciones push (para futura implementación)
self.addEventListener('push', (event) => {
  if (!event.data) return;

  const data = event.data.json();
  const options = {
    body: data.body,
    icon: '/icon-192x192.png',
    badge: '/icon-badge.png',
    vibrate: [100, 50, 100],
    data: {
      url: data.url || '/'
    }
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Abrir URL al hacer clic en notificación
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  event.waitUntil(
    clients.matchAll({ type: 'window' })
      .then((clientList) => {
        const url = event.notification.data.url;
        
        // Si ya hay una ventana abierta, enfocarla
        for (const client of clientList) {
          if (client.url === url && 'focus' in client) {
            return client.focus();
          }
        }
        
        // Si no hay ventana abierta, abrir una nueva
        if (clients.openWindow) {
          return clients.openWindow(url);
        }
      })
  );
});