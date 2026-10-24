'use client'

import { useState, useEffect, useCallback, useRef } from 'react'

// Web Speech API type augmentation
interface SpeechRecognitionResultLike {
  transcript: string
  confidence: number
}
interface SpeechRecognitionEventLike {
  resultIndex: number
  results: ArrayLike<{
    0: SpeechRecognitionResultLike
    isFinal: boolean
    length: number
  }>
}
interface SpeechRecognitionLike {
  lang: string
  continuous: boolean
  interimResults: boolean
  maxAlternatives: number
  start: () => void
  stop: () => void
  abort: () => void
  onresult: ((e: SpeechRecognitionEventLike) => void) | null
  onerror: ((e: any) => void) | null
  onend: (() => void) | null
  onstart: (() => void) | null
}
type SpeechRecognitionCtor = new () => SpeechRecognitionLike

function getRecognitionCtor(): SpeechRecognitionCtor | null {
  if (typeof window === 'undefined') return null
  return (
    (window as any).SpeechRecognition ||
    (window as any).webkitSpeechRecognition ||
    null
  )
}

interface UsePronunciationResult {
  supported: boolean
  listening: boolean
  transcript: string
  confidence: number
  error: string | null
  start: (expectedWord: string) => void
  stop: () => void
  reset: () => void
}

/**
 * Hook for pronunciation practice using Web Speech API.
 * - Uses SpeechRecognition (webkit prefix in Safari/Chrome) to capture user's pronunciation
 * - Returns transcript + confidence for comparison with the expected word
 */
export function usePronunciation(): UsePronunciationResult {
  const [supported, setSupported] = useState(false)
  const [listening, setListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [confidence, setConfidence] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null)
  const expectedRef = useRef<string>('')

  useEffect(() => {
    const ctor = getRecognitionCtor()
    // defer to avoid synchronous setState in effect
    Promise.resolve().then(() => setSupported(!!ctor))
  }, [])

  const start = useCallback((expectedWord: string) => {
    const ctor = getRecognitionCtor()
    if (!ctor) {
      setError('当前浏览器不支持语音识别，请使用 Chrome 浏览器')
      return
    }
    // stop any existing
    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort()
      } catch {}
    }
    expectedRef.current = expectedWord.toLowerCase()
    setError(null)
    setTranscript('')
    setConfidence(0)

    const rec = new ctor()
    rec.lang = 'en-US'
    rec.continuous = false
    rec.interimResults = false
    rec.maxAlternatives = 3

    rec.onstart = () => {
      setListening(true)
    }
    rec.onresult = (e: SpeechRecognitionEventLike) => {
      const result = e.results[0]
      if (result) {
        const text = result[0].transcript.trim()
        const conf = result[0].confidence
        setTranscript(text)
        setConfidence(conf)
      }
    }
    rec.onerror = (e: any) => {
      const errType = e?.error || 'unknown'
      if (errType === 'no-speech') {
        setError('未检测到语音，请再试一次')
      } else if (errType === 'not-allowed' || errType === 'service-not-allowed') {
        setError('麦克风权限被拒绝，请允许浏览器访问麦克风')
      } else if (errType === 'aborted') {
        // user aborted, no error
      } else {
        setError(`语音识别失败: ${errType}`)
      }
    }
    rec.onend = () => {
      setListening(false)
    }

    recognitionRef.current = rec
    try {
      rec.start()
    } catch (err) {
      setError('无法启动语音识别，请重试')
      setListening(false)
    }
  }, [])

  const stop = useCallback(() => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop()
      } catch {}
    }
    setListening(false)
  }, [])

  const reset = useCallback(() => {
    setTranscript('')
    setConfidence(0)
    setError(null)
  }, [])

  return { supported, listening, transcript, confidence, error, start, stop, reset }
}

/**
 * Compare expected word with recognized transcript.
 * Returns { match: boolean, score: 0-100, similarity: 0-1 }
 */
export function comparePronunciation(expected: string, transcript: string): {
  match: boolean
  score: number
  similarity: number
} {
  const a = expected.toLowerCase().trim()
  const b = transcript.toLowerCase().trim()
  if (!a || !b) return { match: false, score: 0, similarity: 0 }
  // exact match
  if (a === b) return { match: true, score: 100, similarity: 1 }
  // transcript may contain extra words; check if expected is contained
  if (b.includes(a)) return { match: true, score: 95, similarity: 0.95 }
  // Levenshtein-based similarity
  const dist = levenshtein(a, b)
  const maxLen = Math.max(a.length, b.length)
  const similarity = 1 - dist / maxLen
  const score = Math.round(similarity * 100)
  return { match: score >= 70, score, similarity }
}

function levenshtein(a: string, b: string): number {
  const m = a.length
  const n = b.length
  if (m === 0) return n
  if (n === 0) return m
  const dp: number[][] = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(0))
  for (let i = 0; i <= m; i++) dp[i][0] = i
  for (let j = 0; j <= n; j++) dp[0][j] = j
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1
      dp[i][j] = Math.min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    }
  }
  return dp[m][n]
}
