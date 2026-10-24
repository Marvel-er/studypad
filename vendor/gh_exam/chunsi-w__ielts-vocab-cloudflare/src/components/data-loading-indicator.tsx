'use client'

import { useEffect, useState } from 'react'
import { Database, CheckCircle2, Loader2 } from 'lucide-react'
import { isStaticMode, onWordLoadProgress, preloadHighFreqWords } from '@/lib/api'

interface LoadProgress {
  loaded: number
  total: number
  letters: string[]
}

export function DataLoadingIndicator() {
  const [progress, setProgress] = useState<LoadProgress | null>(null)
  const [done, setDone] = useState(false)

  useEffect(() => {
    if (!isStaticMode) return
    let unsubscribe: (() => void) | null = null
    let cancelled = false

    // Start preloading high-freq words
    preloadHighFreqWords().catch(() => {})

    // Subscribe to progress
    onWordLoadProgress((p) => {
      if (cancelled) return
      setProgress(p)
      if (p.loaded >= p.total) {
        setDone(true)
      }
    }).then((unsub) => {
      if (cancelled) {
        unsub()
      } else {
        unsubscribe = unsub
      }
    })

    return () => {
      cancelled = true
      if (unsubscribe) unsubscribe()
    }
  }, [])

  if (!isStaticMode || done) return null

  const pct = progress ? Math.round((progress.loaded / progress.total) * 100) : 0

  return (
    <div className="fixed bottom-4 right-4 z-50 pointer-events-none">
      <div className="bg-popover/95 backdrop-blur border border-border rounded-lg shadow-lg px-3 py-2 flex items-center gap-2 animate-fade-in-up">
        <div className="relative">
          {pct < 100 ? (
            <Loader2 className="h-4 w-4 text-primary animate-spin" />
          ) : (
            <CheckCircle2 className="h-4 w-4 text-emerald-500" />
          )}
        </div>
        <div className="text-xs">
          <div className="font-medium flex items-center gap-1">
            <Database className="h-3 w-3" />
            加载词库 {pct}%
          </div>
          <div className="text-[10px] text-muted-foreground">
            {progress?.loaded || 0} / {progress?.total || 26} 字母组
          </div>
        </div>
        <div className="w-16 h-1 bg-muted rounded-full overflow-hidden">
          <div
            className="h-full bg-primary transition-all duration-300"
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>
    </div>
  )
}
