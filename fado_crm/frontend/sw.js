// 🛡️ Simple Service Worker for FADO CRM
// Caches static assets for offline support

const CACHE_NAME = 'fado-crm-cache-v1';
const ASSETS = [
  './index.html',
  './style.css',
  './script.js',
  './auth.js',
  './advanced-dashboard.html',
  './analytics-dashboard.html',
  './export-import.html',
  './file-upload.html',
  './login.html',
  './login-test.html'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
    ))
  );
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  // Only cache GET requests
  if (request.method !== 'GET') return;

  event.respondWith(
    caches.match(request).then((cached) => {
      if (cached) return cached;
      return fetch(request).then((response) => {
        const copy = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
        return response;
      }).catch(() => {
        // Offline fallback: return cached index if available
        return caches.match('./index.html');
      });
    })
  );
});
