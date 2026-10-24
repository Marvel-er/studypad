'use client'

import { useEffect } from 'react'

/**
 * Registers the service worker for PWA offline support.
 * Only runs in production to avoid caching issues during dev.
 */
export function ServiceWorkerRegister() {
  useEffect(() => {
    if (typeof window === 'undefined') return
    if (!('serviceWorker' in navigator)) return
    // Only register in production (dev has HMR which conflicts with SW caching)
    if (process.env.NODE_ENV !== 'production') return

    const register = () => {
      navigator.serviceWorker
        .register('/sw.js')
        .then((reg) => {
          console.log('[PWA] Service Worker registered:', reg.scope)
        })
        .catch((err) => {
          console.warn('[PWA] Service Worker registration failed:', err)
        })
    }

    // Register after page load to not block initial render
    if (document.readyState === 'complete') {
      register()
    } else {
      window.addEventListener('load', register)
      return () => window.removeEventListener('load', register)
    }
  }, [])

  return null
}
