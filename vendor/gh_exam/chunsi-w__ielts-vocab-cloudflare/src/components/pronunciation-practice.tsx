'use client'

import { useState, useEffect, useMemo } from 'react'
import { Mic, MicOff, Volume2, Check, X, AlertCircle, Loader2, RotateCcw, Sparkles } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { usePronunciation, comparePronunciation } from '@/hooks/use-pronunciation'
import { useAudioPlayer } from '@/hooks/use-audio'
import { cn } from '@/lib/utils'

interface PronunciationPracticeProps {
  word: string
  audioUk: string | null
  audioUs: string | null
}

export function PronunciationPractice({ word, audioUk, audioUs }: PronunciationPracticeProps) {
  const { supported, listening, transcript, confidence, error, start, stop, reset } = usePronunciation()
  const { play } = useAudioPlayer()
  const [hasResult, setHasResult] = useState(false)

  // Skip multi-word phrases (pronunciation practice is for single words)
  const isSingleWord = !word.includes(' ') && word.length <= 25

  const comparison = useMemo(() => {
    if (!transcript) return null
    return comparePronunciation(word, transcript)
  }, [transcript, word])

  // Reset when word changes (deferred to avoid synchronous setState in effect)
  useEffect(() => {
    Promise.resolve().then(() => {
      reset()
      setHasResult(false)
    })
  }, [word, reset])

  useEffect(() => {
    if (transcript) {
      Promise.resolve().then(() => setHasResult(true))
    }
  }, [transcript])

  if (!isSingleWord) {
    return null // skip for phrases
  }

  const handleMicClick = () => {
    if (listening) {
      stop()
    } else {
      reset()
      setHasResult(false)
      start(word)
    }
  }

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold flex items-center gap-2">
          <Mic className="h-4 w-4 text-primary" />
          发音练习
        </h3>
        <Badge variant="outline" className="text-[10px]">
          {supported ? 'Web Speech API' : '不支持'}
        </Badge>
      </div>

      {!supported ? (
        <div className="rounded-lg bg-amber-50 dark:bg-amber-950/30 p-3 text-xs text-amber-700 dark:text-amber-400 flex items-start gap-2">
          <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
          <div>
            <p>当前浏览器不支持语音识别功能。</p>
            <p className="mt-1">请使用 Chrome / Edge 浏览器，并允许麦克风权限。</p>
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          {/* Instructions */}
          <p className="text-xs text-muted-foreground">
            点击麦克风按钮，大声读出单词 <span className="font-mono font-semibold text-foreground">{word}</span>
          </p>

          {/* Mic button */}
          <div className="flex items-center justify-center gap-3 py-2">
            {audioUs && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => play(audioUs, 'us')}
                className="gap-1.5"
              >
                <Volume2 className="h-3.5 w-3.5" />
                听发音
              </Button>
            )}
            <button
              onClick={handleMicClick}
              disabled={!supported}
              className={cn(
                'relative flex h-14 w-14 items-center justify-center rounded-full transition-all',
                listening
                  ? 'bg-rose-500 text-white shadow-lg'
                  : 'bg-primary text-primary-foreground hover:scale-105 shadow-md',
              )}
              aria-label={listening ? '停止录音' : '开始录音'}
            >
              {listening ? (
                <>
                  <MicOff className="h-6 w-6" />
                  <span className="absolute inset-0 rounded-full bg-rose-500 animate-ping opacity-30" />
                </>
              ) : (
                <Mic className="h-6 w-6" />
              )}
            </button>
            <div className="text-xs text-muted-foreground min-w-[60px]">
              {listening ? (
                <span className="flex items-center gap-1 text-rose-600 dark:text-rose-400">
                  <Loader2 className="h-3 w-3 animate-spin" />
                  录音中...
                </span>
              ) : (
                <span>点击录音</span>
              )}
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="rounded-lg bg-rose-50 dark:bg-rose-950/30 p-2.5 text-xs text-rose-700 dark:text-rose-400 flex items-start gap-2 animate-fade-in-up">
              <AlertCircle className="h-3.5 w-3.5 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* Result */}
          {hasResult && transcript && comparison && (
            <div className="rounded-lg border-2 p-3 animate-fade-in-up">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  {comparison.match ? (
                    <Badge className="bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
                      <Check className="h-3 w-3 mr-1" /> 发音正确
                    </Badge>
                  ) : (
                    <Badge className="bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300">
                      <X className="h-3 w-3 mr-1" /> 需要练习
                    </Badge>
                  )}
                  <Badge variant="outline" className="text-[10px]">
                    相似度 {comparison.score}%
                  </Badge>
                  {confidence > 0 && (
                    <Badge variant="outline" className="text-[10px]">
                      识别置信度 {Math.round(confidence * 100)}%
                    </Badge>
                  )}
                </div>
                <Button variant="ghost" size="sm" className="h-6 px-2 text-xs" onClick={() => { reset(); setHasResult(false) }}>
                  <RotateCcw className="h-3 w-3 mr-1" />
                  重试
                </Button>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="rounded bg-muted/50 p-2">
                  <div className="text-[10px] text-muted-foreground mb-0.5">目标</div>
                  <div className="font-mono font-semibold">{word}</div>
                </div>
                <div className="rounded bg-muted/50 p-2">
                  <div className="text-[10px] text-muted-foreground mb-0.5">你的发音</div>
                  <div className="font-mono font-semibold">{transcript || '(空)'}</div>
                </div>
              </div>

              {/* Score bar */}
              <div className="mt-2">
                <div className="flex justify-between text-[10px] text-muted-foreground mb-1">
                  <span>发音相似度</span>
                  <span>{comparison.score}/100</span>
                </div>
                <div className="h-2 rounded-full bg-muted overflow-hidden">
                  <div
                    className={cn(
                      'h-full transition-all duration-500 rounded-full',
                      comparison.score >= 80
                        ? 'bg-emerald-500'
                        : comparison.score >= 60
                          ? 'bg-amber-500'
                          : 'bg-rose-500',
                    )}
                    style={{ width: `${comparison.score}%` }}
                  />
                </div>
              </div>

              {comparison.match && comparison.score >= 90 && (
                <div className="mt-2 flex items-center gap-1 text-xs text-emerald-600 dark:text-emerald-400">
                  <Sparkles className="h-3 w-3" />
                  完美！发音非常标准
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </Card>
  )
}
