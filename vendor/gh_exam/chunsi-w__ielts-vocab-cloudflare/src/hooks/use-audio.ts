'use client'

import { useCallback, useRef } from 'react'
import { useProgressStore } from '@/store/progress'

/**
 * Audio player hook for word pronunciation.
 * Uses the audioUk / audioUs URLs from the data.
 */
export function useAudioPlayer() {
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const audioAccent = useProgressStore((s) => s.audioAccent)

  const play = useCallback(
    (url?: string | null, accent?: 'uk' | 'us') => {
      const a = accent ?? audioAccent
      if (!url) return
      // stop any current playback
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current.currentTime = 0
      }
      const audio = new Audio(url)
      audioRef.current = audio
      audio.play().catch((e) => {
        // silent fail — network/CORS issues
        console.warn('Audio playback failed:', e)
      })
      // mark accent for analytics if needed
      void a
    },
    [audioAccent],
  )

  return { play }
}
