// Service Worker for 雅思词汇通
// Caches app shell for offline access
const CACHE_NAME = 'ielts-vocab-v1'
const APP_SHELL = [
  '/',
  '/manifest.json',
  '/icon-192.png',
  '/icon-512.png',
]

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(APP_SHELL).catch(() => {
        // ignore failures for individual assets
      })
    }),
  )
  self.skipWaiting()
})

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name)),
      )
    }),
  )
  self.clients.claim()
})

self.addEventListener('fetch', (event) => {
  const { request } = event
  // Only handle GET requests
  if (request.method !== 'GET') return

  const url = new URL(request.url)

  // Skip API requests (always network-first for fresh data)
  if (url.pathname.startsWith('/api/')) {
    return
  }

  // Skip external requests (audio OSS, fonts, etc.)
  if (url.origin !== self.location.origin) {
    return
  }

  // App shell: cache-first
  event.respondWith(
    caches.match(request).then((cached) => {
      if (cached) {
        return cached
      }
      return fetch(request)
        .then((response) => {
          // cache successful responses
          if (response && response.status === 200) {
            const responseClone = response.clone()
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, responseClone)
            })
          }
          return response
        })
        .catch(() => {
          // offline fallback
          if (request.mode === 'navigate') {
            return caches.match('/')
          }
        })
    }),
  )
})
