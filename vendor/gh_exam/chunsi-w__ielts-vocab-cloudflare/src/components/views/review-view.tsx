'use client'

import { useEffect, useState, useMemo, useCallback, useRef } from 'react'
import {
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  Volume2,
  Check,
  X,
  Brain,
  Clock,
  Calendar,
  Sparkles,
  RotateCcw,
  TrendingUp,
  AlertCircle,
} from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Progress } from '@/components/ui/progress'
import { api } from '@/lib/api'
import { useProgressStore } from '@/store/progress'
import { useUIStore } from '@/store/ui'
import { useAudioPlayer } from '@/hooks/use-audio'
import { getDueWordIds, getReviewStats, getReviewStatus, REVIEW_INTERVAL_HOURS } from '@/lib/review'
import type { WordListItem } from '@/lib/types'
import { cn } from '@/lib/utils'

export function ReviewView() {
  const progress = useProgressStore((s) => s.progress)
  const reviewCorrect = useProgressStore((s) => s.reviewCorrect)
  const reviewWrong = useProgressStore((s) => s.reviewWrong)
  const recordReviewSession = useProgressStore((s) => s.recordReviewSession)
  const openWord = useUIStore((s) => s.openWord)
  const { play } = useAudioPlayer()

  const [phase, setPhase] = useState<'overview' | 'review' | 'done'>('overview')
  const [queue, setQueue] = useState<WordListItem[]>([])
  const [current, setCurrent] = useState(0)
  const [flipped, setFlipped] = useState(false)
  const [answers, setAnswers] = useState<Array<{ wordId: number; correct: boolean }>>([])
  const [loading, setLoading] = useState(false)
  const [animating, setAnimating] = useState(false)

  // Compute due words and stats
  const { dueIds, stats } = useMemo(() => {
    const due = getDueWordIds(progress)
    const s = getReviewStats(progress)
    return { dueIds: due.map((d) => d.id), stats: s }
  }, [progress])

  const startReview = useCallback(async () => {
    if (dueIds.length === 0) return
    setLoading(true)
    setPhase('review')
    setCurrent(0)
    setFlipped(false)
    setAnswers([])
    try {
      const r = await api.reviewDue(dueIds.slice(0, 50))
      setQueue(r.words)
    } catch (e) {
      console.error(e)
      setPhase('overview')
    } finally {
      setLoading(false)
    }
  }, [dueIds])

  const handleFlip = useCallback(() => {
    setFlipped((f) => !f)
  }, [])

  const handleAnswer = useCallback(
    (correct: boolean) => {
      const w = queue[current]
      if (!w) return
      if (correct) {
        reviewCorrect(w.id)
      } else {
        reviewWrong(w.id)
      }
      setAnswers((prev) => [...prev, { wordId: w.id, correct }])
      setAnimating(true)
      setFlipped(false)
      setTimeout(() => {
        if (current + 1 >= queue.length) {
          recordReviewSession(queue.length)
          setPhase('done')
        } else {
          setCurrent((c) => c + 1)
        }
        setAnimating(false)
      }, 250)
    },
    [queue, current, reviewCorrect, reviewWrong, recordReviewSession],
  )

  // Keyboard shortcuts
  useEffect(() => {
    if (phase !== 'review') return
    const handler = (e: KeyboardEvent) => {
      if (e.key === ' ' || e.key === 'Enter') {
        e.preventDefault()
        if (!flipped) handleFlip()
      } else if (e.key === '1') {
        e.preventDefault()
        if (flipped) handleAnswer(false)
      } else if (e.key === '2') {
        e.preventDefault()
        if (flipped) handleAnswer(true)
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault()
        // can't go back in review
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [phase, flipped, handleFlip, handleAnswer])

  // OVERVIEW phase
  if (phase === 'overview') {
    const totalLearning = Object.values(progress).filter((p) => p.mastery > 0 && p.mastery < 5).length
    const mastered = Object.values(progress).filter((p) => p.mastery >= 5 || p.learned).length

    return (
      <div className="space-y-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <RefreshCw className="h-6 w-6 text-primary" />
            智能复习
          </h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            基于艾宾浩斯遗忘曲线，优先复习即将遗忘的单词
          </p>
        </div>

        {stats.dueNow === 0 ? (
          <Card className="p-8 max-w-2xl mx-auto text-center">
            <div className="inline-flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100 dark:bg-emerald-950/40 mb-3">
              <Check className="h-8 w-8 text-emerald-600 dark:text-emerald-400" />
            </div>
            <h2 className="text-lg font-semibold">暂无待复习单词</h2>
            <p className="text-sm text-muted-foreground mt-1">
              {stats.dueIn24h > 0
                ? `未来 24 小时内有 ${stats.dueIn24h} 个单词将到期`
                : '继续学习新单词，复习队列会自动生成'}
            </p>
            <div className="mt-4 flex gap-2 justify-center">
              <Button variant="outline" size="sm" onClick={() => useUIStore.getState().setView('study')}>
                <Sparkles className="h-3.5 w-3.5 mr-1" />
                去学习新单词
              </Button>
              {stats.dueIn24h > 0 && (
                <Button size="sm" onClick={startReview} disabled>
                  <Clock className="h-3.5 w-3.5 mr-1" />
                  {stats.dueIn24h} 个即将到期
                </Button>
              )}
            </div>
          </Card>
        ) : (
          <Card className="p-6 max-w-2xl mx-auto">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-semibold flex items-center gap-2">
                  <AlertCircle className="h-5 w-5 text-rose-500" />
                  {stats.dueNow} 个单词待复习
                </h2>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {stats.dueIn24h > 0 && `+ ${stats.dueIn24h} 个将在 24h 内到期 · `}
                  共 {stats.totalLearning} 个单词在学习中
                </p>
              </div>
              <Button size="lg" onClick={startReview} disabled={loading}>
                <RefreshCw className={cn('h-4 w-4 mr-1', loading && 'animate-spin')} />
                开始复习
              </Button>
            </div>

            {/* Stats grid */}
            <div className="grid grid-cols-3 gap-3 mt-4">
              <div className="rounded-lg bg-rose-50 dark:bg-rose-950/30 p-3 text-center">
                <div className="text-2xl font-bold text-rose-600 dark:text-rose-400">{stats.dueNow}</div>
                <div className="text-[11px] text-muted-foreground mt-0.5">待复习</div>
              </div>
              <div className="rounded-lg bg-amber-50 dark:bg-amber-950/30 p-3 text-center">
                <div className="text-2xl font-bold text-amber-600 dark:text-amber-400">{stats.dueIn24h}</div>
                <div className="text-[11px] text-muted-foreground mt-0.5">24h 内到期</div>
              </div>
              <div className="rounded-lg bg-emerald-50 dark:bg-emerald-950/30 p-3 text-center">
                <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{mastered}</div>
                <div className="text-[11px] text-muted-foreground mt-0.5">已掌握</div>
              </div>
            </div>

            {/* How it works */}
            <div className="mt-5 pt-4 border-t border-border/60">
              <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2 flex items-center gap-1.5">
                <Brain className="h-3.5 w-3.5" />
                复习间隔（艾宾浩斯遗忘曲线）
              </h3>
              <div className="grid grid-cols-6 gap-1.5">
                {([0, 1, 2, 3, 4, 5] as const).map((lvl) => (
                  <div key={lvl} className="rounded-md bg-muted/50 p-2 text-center">
                    <div className="text-[10px] text-muted-foreground">Lv.{lvl}</div>
                    <div className="text-xs font-semibold mt-0.5">
                      {REVIEW_INTERVAL_HOURS[lvl] >= 24
                        ? `${Math.round(REVIEW_INTERVAL_HOURS[lvl] / 24)}天`
                        : `${REVIEW_INTERVAL_HOURS[lvl]}h`}
                    </div>
                  </div>
                ))}
              </div>
              <p className="text-[11px] text-muted-foreground mt-2 leading-relaxed">
                答对：掌握度 +1，下次复习间隔翻倍 · 答错：掌握度 -1，30 分钟后重新复习
              </p>
            </div>
          </Card>
        )}
      </div>
    )
  }

  // DONE phase
  if (phase === 'done') {
    const correct = answers.filter((a) => a.correct).length
    const total = answers.length
    const pct = total > 0 ? Math.round((correct / total) * 100) : 0
    return (
      <div className="space-y-4">
        <Card className="p-8 max-w-2xl mx-auto text-center">
          <div className={cn(
            'inline-flex h-20 w-20 items-center justify-center rounded-full mb-4',
            pct >= 80 ? 'bg-emerald-100 dark:bg-emerald-950/40' : pct >= 60 ? 'bg-amber-100 dark:bg-amber-950/40' : 'bg-rose-100 dark:bg-rose-950/40',
          )}>
            <TrendingUp className={cn('h-10 w-10', pct >= 80 ? 'text-emerald-600 dark:text-emerald-400' : pct >= 60 ? 'text-amber-600 dark:text-amber-400' : 'text-rose-600 dark:text-rose-400')} />
          </div>
          <h2 className="text-2xl font-bold">复习完成！</h2>
          <p className="text-muted-foreground mt-1">本次复习 {total} 个单词</p>
          <div className="mt-6 grid grid-cols-3 gap-3">
            <div className="rounded-lg bg-emerald-50 dark:bg-emerald-950/30 p-3">
              <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{correct}</div>
              <div className="text-[11px] text-muted-foreground">记得</div>
            </div>
            <div className="rounded-lg bg-rose-50 dark:bg-rose-950/30 p-3">
              <div className="text-2xl font-bold text-rose-600 dark:text-rose-400">{total - correct}</div>
              <div className="text-[11px] text-muted-foreground">遗忘</div>
            </div>
            <div className="rounded-lg bg-amber-50 dark:bg-amber-950/30 p-3">
              <div className="text-2xl font-bold text-amber-600 dark:text-amber-400">{pct}%</div>
              <div className="text-[11px] text-muted-foreground">记忆率</div>
            </div>
          </div>
          <div className="mt-6 flex gap-2">
            <Button variant="outline" className="flex-1" onClick={() => setPhase('overview')}>
              返回概览
            </Button>
            <Button className="flex-1" onClick={() => setPhase('overview')}>
              <RotateCcw className="h-4 w-4 mr-1" />
              再复习一轮
            </Button>
          </div>
        </Card>
      </div>
    )
  }

  // REVIEW phase
  const word = queue[current]
  const progressPct = queue.length > 0 ? ((current + 1) / queue.length) * 100 : 0
  const wordProgress = word ? progress[word.id] : undefined
  const reviewStatus = word && wordProgress ? getReviewStatus(wordProgress) : null

  if (loading || !word) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-32" />
        <Skeleton className="h-1.5 w-full" />
        <Skeleton className="h-96 w-full" />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <RefreshCw className="h-6 w-6 text-primary" />
            智能复习
          </h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            第 {current + 1} / {queue.length} 题 · 空格翻卡 · 1 遗忘 / 2 记得
          </p>
        </div>
        <Badge variant="outline" className="gap-1">
          <Clock className="h-3 w-3" />
          {reviewStatus && (
            <span>
              {reviewStatus.overdueMs > 24 * 60 * 60 * 1000
                ? `逾期 ${Math.floor(reviewStatus.overdueMs / (24 * 60 * 60 * 1000))} 天`
                : reviewStatus.overdueMs > 60 * 60 * 1000
                  ? `逾期 ${Math.floor(reviewStatus.overdueMs / (60 * 60 * 1000))} 小时`
                  : '即将到期'}
            </span>
          )}
        </Badge>
      </div>

      <Progress value={progressPct} className="h-1.5" />

      <Card
        className={cn(
          'relative min-h-[420px] cursor-pointer overflow-hidden transition-all duration-300',
          animating && 'opacity-0 translate-x-4',
        )}
        onClick={handleFlip}
      >
        {!flipped && (
          <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center">
            <div className="absolute top-4 left-4 flex items-center gap-2">
              <Badge variant="secondary" className="text-[10px]">{word.groupName}</Badge>
              <Badge variant="outline" className="text-[10px] gap-1">
                <Brain className="h-3 w-3" />
                Lv.{wordProgress?.mastery ?? 0}
              </Badge>
            </div>
            <h2 className="text-4xl sm:text-5xl font-bold tracking-tight">{word.word}</h2>
            {word.phonetic && (
              <p className="mt-3 text-base text-muted-foreground font-mono">{word.phonetic}</p>
            )}
            <div className="mt-5 flex items-center gap-2">
              {word.audioUk && (
                <Button variant="outline" size="sm" onClick={(e) => { e.stopPropagation(); play(word.audioUk, 'uk') }}>
                  <Volume2 className="h-3.5 w-3.5 mr-1" />UK
                </Button>
              )}
              {word.audioUs && (
                <Button variant="outline" size="sm" onClick={(e) => { e.stopPropagation(); play(word.audioUs, 'us') }}>
                  <Volume2 className="h-3.5 w-3.5 mr-1" />US
                </Button>
              )}
            </div>
            <p className="mt-8 text-xs text-muted-foreground animate-pulse">
              你还记得这个单词吗？点击查看释义
            </p>
          </div>
        )}

        {flipped && (
          <div className="absolute inset-0 overflow-y-auto p-5 sm:p-6">
            <div className="flex items-start justify-between gap-2 mb-3">
              <div>
                <div className="flex items-center gap-2 flex-wrap">
                  <h2 className="text-2xl font-bold">{word.word}</h2>
                  <Badge variant="secondary" className="text-[10px]">{word.groupName}</Badge>
                  <Badge variant="outline" className="text-[10px] gap-1">
                    <Brain className="h-3 w-3" />Lv.{wordProgress?.mastery ?? 0}
                  </Badge>
                </div>
                {word.phonetic && (
                  <p className="text-xs text-muted-foreground font-mono mt-0.5">{word.phonetic}</p>
                )}
              </div>
              <div className="flex items-center gap-1 shrink-0">
                {word.audioUs && (
                  <Button variant="ghost" size="icon" className="h-7 w-7" onClick={(e) => { e.stopPropagation(); play(word.audioUs, 'us') }}>
                    <Volume2 className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </div>

            <div className="rounded-lg bg-rose-50 dark:bg-rose-950/30 p-3 mb-3">
              <div className="text-[10px] text-muted-foreground mb-1">中文释义</div>
              <p className="text-sm whitespace-pre-line leading-relaxed">{word.translation}</p>
            </div>

            {word.englishDefinition && (
              <div className="rounded-lg bg-muted/50 p-3 mb-3">
                <div className="text-[10px] text-muted-foreground mb-1">英文释义</div>
                <p className="text-sm italic leading-relaxed">{word.englishDefinition}</p>
              </div>
            )}

            {word.exampleEn && (
              <div className="rounded-lg bg-emerald-50 dark:bg-emerald-950/30 p-3 mb-3">
                <div className="text-[10px] text-muted-foreground mb-1">例句</div>
                <p className="text-sm leading-relaxed">{word.exampleEn}</p>
                {word.exampleZh && <p className="text-xs text-muted-foreground mt-1.5">{word.exampleZh}</p>}
              </div>
            )}

            {word.mnemonic && (
              <div className="rounded-lg bg-amber-50 dark:bg-amber-950/30 p-3">
                <div className="text-[10px] text-muted-foreground mb-1 flex items-center gap-1">
                  <Brain className="h-3 w-3" />记忆法
                </div>
                <p className="text-sm whitespace-pre-line leading-relaxed">{word.mnemonic}</p>
              </div>
            )}

            <div className="mt-4 p-3 rounded-lg border-2 border-dashed border-border/60 text-center">
              <p className="text-xs text-muted-foreground mb-2">你记得这个单词吗？</p>
              <div className="flex gap-2 justify-center">
                <Button
                  variant="outline"
                  className="border-rose-300 text-rose-600 hover:bg-rose-50 dark:border-rose-800 dark:hover:bg-rose-950"
                  onClick={(e) => { e.stopPropagation(); handleAnswer(false) }}
                >
                  <X className="h-4 w-4 mr-1" />
                  遗忘了 (1)
                </Button>
                <Button
                  variant="outline"
                  className="border-emerald-300 text-emerald-600 hover:bg-emerald-50 dark:border-emerald-800 dark:hover:bg-emerald-950"
                  onClick={(e) => { e.stopPropagation(); handleAnswer(true) }}
                >
                  <Check className="h-4 w-4 mr-1" />
                  还记得 (2)
                </Button>
              </div>
            </div>
          </div>
        )}
      </Card>

      {/* Action buttons (visible only when not flipped) */}
      {!flipped && (
        <div className="grid grid-cols-2 gap-2">
          <Button variant="outline" disabled>
            <ChevronLeft className="h-4 w-4 mr-1" />
            上一题
          </Button>
          <Button variant="outline" onClick={handleFlip}>
            点击翻卡
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </div>
      )}
    </div>
  )
}
