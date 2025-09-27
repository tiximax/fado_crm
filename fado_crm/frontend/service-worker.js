// 🚀 FADO CRM - Service Worker for PWA
// Advanced caching strategies and offline support

const CACHE_NAME = 'fado-crm-v6.0.0';
const STATIC_CACHE = 'fado-static-v6';
const API_CACHE = 'fado-api-v6';
const IMAGE_CACHE = 'fado-images-v6';

// Resources to cache immediately
const STATIC_RESOURCES = [
  '/',
  '/index.html',
  '/style.css',
  '/script.js',
  '/mobile-enhancements.css',
  '/pwa-enhanced.js',
  '/manifest.json',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
  'https://cdn.jsdelivr.net/npm/chart.js',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
];

// API endpoints to cache with network-first strategy
const API_ENDPOINTS = [
  '/api/dashboard/stats',
  '/api/customers',
  '/api/products',
  '/api/orders'
];

// Install Service Worker
self.addEventListener('install', (event) => {
  console.log('🔧 Service Worker installing...');

  event.waitUntil(
    Promise.all([
      // Cache static resources
      caches.open(STATIC_CACHE).then((cache) => {
        console.log('📦 Caching static resources');
        return cache.addAll(STATIC_RESOURCES.map(url => new Request(url, {
          credentials: 'same-origin'
        })));
      }),

      // Initialize API cache
      caches.open(API_CACHE),

      // Initialize image cache
      caches.open(IMAGE_CACHE)
    ]).then(() => {
      console.log('✅ Service Worker installed successfully');
      // Skip waiting to activate immediately
      return self.skipWaiting();
    }).catch((error) => {
      console.error('❌ Service Worker installation failed:', error);
    })
  );
});

// Activate Service Worker
self.addEventListener('activate', (event) => {
  console.log('🚀 Service Worker activating...');

  event.waitUntil(
    Promise.all([
      // Clean up old caches
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE &&
                cacheName !== API_CACHE &&
                cacheName !== IMAGE_CACHE) {
              console.log('🗑️ Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),

      // Take control of all clients immediately
      self.clients.claim()
    ]).then(() => {
      console.log('✅ Service Worker activated successfully');

      // Send message to all clients about the update
      self.clients.matchAll().then((clients) => {
        clients.forEach((client) => {
          client.postMessage({
            type: 'SW_ACTIVATED',
            message: 'Service Worker updated successfully!'
          });
        });
      });
    })
  );
});

// Fetch Event Handler - Advanced Caching Strategies
self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Skip chrome-extension and other non-http requests
  if (!url.protocol.startsWith('http')) {
    return;
  }

  // Different strategies for different types of resources
  if (url.pathname.startsWith('/api/')) {
    // API requests - Network First with fallback
    event.respondWith(networkFirstStrategy(request, API_CACHE));
  } else if (isImageRequest(request)) {
    // Images - Cache First
    event.respondWith(cacheFirstStrategy(request, IMAGE_CACHE));
  } else if (isStaticResource(request)) {
    // Static resources - Cache First with network fallback
    event.respondWith(cacheFirstStrategy(request, STATIC_CACHE));
  } else {
    // Default - Network First
    event.respondWith(networkFirstStrategy(request, STATIC_CACHE));
  }
});

// Network First Strategy - For API and dynamic content
async function networkFirstStrategy(request, cacheName) {
  try {
    // Try network first
    const networkResponse = await fetch(request.clone());

    // If successful, cache the response
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);

      // Clone response before caching (response can only be consumed once)
      const responseToCache = networkResponse.clone();

      // Cache API responses with TTL consideration
      if (request.url.includes('/api/')) {
        // Add timestamp to cached response for TTL
        const responseWithTimestamp = new Response(responseToCache.body, {
          status: responseToCache.status,
          statusText: responseToCache.statusText,
          headers: {
            ...Object.fromEntries(responseToCache.headers.entries()),
            'sw-cache-timestamp': Date.now().toString()
          }
        });

        cache.put(request, responseWithTimestamp);
      } else {
        cache.put(request, responseToCache);
      }
    }

    return networkResponse;
  } catch (error) {
    console.log('🌐 Network failed, trying cache:', request.url);

    // Network failed, try cache
    const cachedResponse = await caches.match(request);

    if (cachedResponse) {
      // Check if API response is stale (older than 5 minutes)
      if (request.url.includes('/api/')) {
        const cacheTimestamp = cachedResponse.headers.get('sw-cache-timestamp');
        if (cacheTimestamp) {
          const age = Date.now() - parseInt(cacheTimestamp);
          const maxAge = 5 * 60 * 1000; // 5 minutes

          if (age > maxAge) {
            console.log('📅 Cached API response is stale');
            // Return stale response but with a header indicating it's stale
            return new Response(cachedResponse.body, {
              status: cachedResponse.status,
              statusText: cachedResponse.statusText,
              headers: {
                ...Object.fromEntries(cachedResponse.headers.entries()),
                'sw-cache-stale': 'true'
              }
            });
          }
        }
      }

      return cachedResponse;
    }

    // If no cache available, return offline page for HTML requests
    if (request.headers.get('accept')?.includes('text/html')) {
      return caches.match('/offline.html') || new Response(
        getOfflineHTML(),
        {
          headers: { 'Content-Type': 'text/html' },
          status: 200
        }
      );
    }

    // For other requests, return a generic error response
    return new Response(
      JSON.stringify({
        error: 'Offline - Service temporarily unavailable',
        cached: false,
        timestamp: new Date().toISOString()
      }),
      {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Cache First Strategy - For static resources and images
async function cacheFirstStrategy(request, cacheName) {
  const cachedResponse = await caches.match(request);

  if (cachedResponse) {
    // Return cached version immediately

    // Optionally update cache in background for static resources
    if (!isImageRequest(request)) {
      updateCacheInBackground(request, cacheName);
    }

    return cachedResponse;
  }

  // Not in cache, fetch from network
  try {
    const networkResponse = await fetch(request);

    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    console.error('📡 Failed to fetch resource:', request.url, error);

    // Return a fallback response
    if (isImageRequest(request)) {
      return new Response(
        // Simple 1x1 transparent PNG
        Uint8Array.from(atob('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='), c => c.charCodeAt(0)),
        { headers: { 'Content-Type': 'image/png' } }
      );
    }

    return new Response('Resource not available offline', {
      status: 503,
      headers: { 'Content-Type': 'text/plain' }
    });
  }
}

// Update cache in background
function updateCacheInBackground(request, cacheName) {
  fetch(request.clone())
    .then(response => {
      if (response.ok) {
        caches.open(cacheName).then(cache => {
          cache.put(request, response);
        });
      }
    })
    .catch(error => {
      console.log('🔄 Background cache update failed:', error);
    });
}

// Helper functions
function isImageRequest(request) {
  return request.headers.get('accept')?.includes('image/') ||
         request.url.match(/\\.(jpg|jpeg|png|gif|webp|svg)$/i);
}

function isStaticResource(request) {
  return request.url.match(/\\.(css|js|html|json|ico|woff2?|ttf|eot)$/i) ||
         STATIC_RESOURCES.some(resource => request.url.endsWith(resource));
}

function getOfflineHTML() {
  return `
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FADO CRM - Offline</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
            }
            .offline-container {
                max-width: 400px;
                padding: 2rem;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }
            .offline-icon {
                font-size: 4rem;
                margin-bottom: 1rem;
            }
            .offline-title {
                font-size: 1.5rem;
                margin-bottom: 1rem;
                font-weight: 600;
            }
            .offline-message {
                margin-bottom: 2rem;
                opacity: 0.9;
            }
            .retry-button {
                background: #4A90E2;
                border: none;
                color: white;
                padding: 0.75rem 1.5rem;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1rem;
                transition: background 0.3s;
            }
            .retry-button:hover {
                background: #357ABD;
            }
            .features-list {
                text-align: left;
                margin: 1rem 0;
                padding-left: 1.5rem;
            }
            .features-list li {
                margin: 0.5rem 0;
                opacity: 0.8;
            }
        </style>
    </head>
    <body>
        <div class="offline-container">
            <div class="offline-icon">📶</div>
            <h1 class="offline-title">Bạn đang offline</h1>
            <p class="offline-message">
                FADO CRM đang hoạt động offline. Một số tính năng vẫn có thể sử dụng được:
            </p>
            <ul class="features-list">
                <li>Xem dữ liệu đã cache</li>
                <li>Tạo đơn hàng mới (sẽ sync khi online)</li>
                <li>Xem thông tin khách hàng</li>
                <li>Truy cập báo cáo đã lưu</li>
            </ul>
            <button class="retry-button" onclick="window.location.reload()">
                Thử lại kết nối
            </button>
        </div>

        <script>
            // Auto-retry when online
            window.addEventListener('online', () => {
                window.location.reload();
            });

            // Show online/offline status
            function updateOnlineStatus() {
                if (navigator.onLine) {
                    window.location.reload();
                }
            }

            window.addEventListener('online', updateOnlineStatus);
            window.addEventListener('offline', updateOnlineStatus);
        </script>
    </body>
    </html>
  `;
}

// Message handling
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    console.log('⏩ Skipping waiting phase');
    self.skipWaiting();
  }

  if (event.data && event.data.type === 'GET_CACHE_STATUS') {
    // Send cache status to client
    Promise.all([
      caches.open(STATIC_CACHE).then(cache => cache.keys()),
      caches.open(API_CACHE).then(cache => cache.keys()),
      caches.open(IMAGE_CACHE).then(cache => cache.keys())
    ]).then(([staticKeys, apiKeys, imageKeys]) => {
      event.ports[0].postMessage({
        type: 'CACHE_STATUS',
        static: staticKeys.length,
        api: apiKeys.length,
        images: imageKeys.length,
        total: staticKeys.length + apiKeys.length + imageKeys.length
      });
    });
  }

  if (event.data && event.data.type === 'CLEAR_CACHE') {
    // Clear specific cache or all caches
    const cacheType = event.data.cacheType || 'all';

    Promise.resolve().then(() => {
      if (cacheType === 'all' || cacheType === 'api') {
        return caches.delete(API_CACHE);
      }
    }).then(() => {
      if (cacheType === 'all' || cacheType === 'static') {
        return caches.delete(STATIC_CACHE);
      }
    }).then(() => {
      if (cacheType === 'all' || cacheType === 'images') {
        return caches.delete(IMAGE_CACHE);
      }
    }).then(() => {
      event.ports[0].postMessage({
        type: 'CACHE_CLEARED',
        cacheType: cacheType
      });
    });
  }
});

// Background Sync for offline actions
self.addEventListener('sync', (event) => {
  console.log('🔄 Background sync triggered:', event.tag);

  if (event.tag === 'sync-orders') {
    event.waitUntil(syncOfflineOrders());
  }

  if (event.tag === 'sync-customers') {
    event.waitUntil(syncOfflineCustomers());
  }
});

// Sync offline orders when connection is restored
async function syncOfflineOrders() {
  try {
    const offlineOrders = await getOfflineData('orders');

    for (const order of offlineOrders) {
      try {
        const response = await fetch('/api/orders', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(order.data)
        });

        if (response.ok) {
          await removeOfflineData('orders', order.id);
          console.log('✅ Synced offline order:', order.id);
        }
      } catch (error) {
        console.error('❌ Failed to sync order:', order.id, error);
      }
    }
  } catch (error) {
    console.error('❌ Background sync failed:', error);
  }
}

// Sync offline customers
async function syncOfflineCustomers() {
  try {
    const offlineCustomers = await getOfflineData('customers');

    for (const customer of offlineCustomers) {
      try {
        const response = await fetch('/api/customers', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(customer.data)
        });

        if (response.ok) {
          await removeOfflineData('customers', customer.id);
          console.log('✅ Synced offline customer:', customer.id);
        }
      } catch (error) {
        console.error('❌ Failed to sync customer:', customer.id, error);
      }
    }
  } catch (error) {
    console.error('❌ Background sync failed:', error);
  }
}

// Helper functions for offline data management
async function getOfflineData(type) {
  try {
    const cache = await caches.open('offline-data');
    const response = await cache.match(`/offline/${type}`);

    if (response) {
      return await response.json();
    }

    return [];
  } catch (error) {
    console.error('Error getting offline data:', error);
    return [];
  }
}

async function removeOfflineData(type, id) {
  try {
    const data = await getOfflineData(type);
    const filteredData = data.filter(item => item.id !== id);

    const cache = await caches.open('offline-data');
    await cache.put(`/offline/${type}`, new Response(
      JSON.stringify(filteredData),
      { headers: { 'Content-Type': 'application/json' } }
    ));
  } catch (error) {
    console.error('Error removing offline data:', error);
  }
}

// Push notifications handler
self.addEventListener('push', (event) => {
  console.log('🔔 Push notification received');

  let notificationData = {
    title: 'FADO CRM',
    body: 'Bạn có thông báo mới',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    tag: 'fado-crm-notification',
    requireInteraction: false,
    actions: [
      {
        action: 'view',
        title: 'Xem ngay',
        icon: '/icons/action-view.png'
      },
      {
        action: 'dismiss',
        title: 'Bỏ qua',
        icon: '/icons/action-dismiss.png'
      }
    ]
  };

  if (event.data) {
    try {
      const pushData = event.data.json();
      notificationData = { ...notificationData, ...pushData };
    } catch (e) {
      notificationData.body = event.data.text();
    }
  }

  event.waitUntil(
    self.registration.showNotification(notificationData.title, notificationData)
  );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  console.log('🔔 Notification clicked:', event.notification.tag);

  event.notification.close();

  if (event.action === 'view') {
    event.waitUntil(
      clients.openWindow('/')
    );
  } else if (event.action === 'dismiss') {
    // Just close the notification
    return;
  } else {
    // Default action - open the app
    event.waitUntil(
      clients.matchAll({ type: 'window' }).then((windowClients) => {
        // Check if app is already open
        for (let client of windowClients) {
          if (client.url.includes(self.registration.scope) && 'focus' in client) {
            return client.focus();
          }
        }

        // Open new window
        if (clients.openWindow) {
          return clients.openWindow('/');
        }
      })
    );
  }
});

console.log('🚀 FADO CRM Service Worker loaded successfully!');