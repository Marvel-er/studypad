import { useEffect, useState } from 'react'
import { getTodayReading } from '../data/readings'
import type { ReadingArticle } from '../types'

let cachedArticle: ReadingArticle | null = null
let pendingRequest: Promise<ReadingArticle> | null = null

function chicagoDate() {
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'America/Chicago',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).formatToParts(new Date())
  const values = Object.fromEntries(parts.map((part) => [part.type, part.value]))
  return `${values.year}-${values.month}-${values.day}`
}

function requestDailyReading() {
  if (cachedArticle?.publishedDate === chicagoDate()) return Promise.resolve(cachedArticle)
  cachedArticle = null
  if (!pendingRequest) {
    pendingRequest = fetch(`/api/daily-reading?date=${chicagoDate()}`)
      .then((response) => {
        if (!response.ok) throw new Error(`Daily reading returned ${response.status}`)
        return response.json() as Promise<ReadingArticle>
      })
      .then((article) => {
        cachedArticle = article
        return article
      })
      .finally(() => {
        pendingRequest = null
      })
  }
  return pendingRequest
}

export function useDailyReading() {
  const fallback = getTodayReading()
  const cachedForToday = cachedArticle?.publishedDate === chicagoDate() ? cachedArticle : null
  const [article, setArticle] = useState<ReadingArticle>(() => cachedForToday ?? fallback)
  const [status, setStatus] = useState<'loading' | 'live' | 'fallback'>(() => cachedForToday ? 'live' : 'loading')

  useEffect(() => {
    let active = true
    const load = () => {
      requestDailyReading()
        .then((dailyArticle) => {
          if (!active) return
          setArticle(dailyArticle)
          setStatus('live')
        })
        .catch(() => {
          if (!active) return
          setStatus('fallback')
        })
    }
    load()
    const timer = window.setInterval(() => {
      if (cachedArticle?.publishedDate !== chicagoDate()) {
        setStatus('loading')
        load()
      }
    }, 60_000)
    return () => {
      active = false
      window.clearInterval(timer)
    }
  }, [])

  return { article, status }
}
