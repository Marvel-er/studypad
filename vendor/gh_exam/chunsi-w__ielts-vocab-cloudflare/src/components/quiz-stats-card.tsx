'use client'

import { useMemo, useState } from 'react'
import { Trophy, Clock, Target, TrendingUp, Zap, Award, ChevronRight, History } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useProgressStore } from '@/store/progress'
import { useUIStore } from '@/store/ui'
import { cn } from '@/lib/utils'

interface QuizRecord {
  date: number
  total: number
  correct: number
  mode: string
  durationMs?: number
}

function formatTime(ms: number): string {
  const totalSec = Math.floor(ms / 1000)
  const min = Math.floor(totalSec / 60)
  const sec = totalSec % 60
  return `${String(min).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
}

const modeLabels: Record<string, string> = {
  en_to_zh: '英→中',
  zh_to_en: '中→英',
  en_to_sentence: '词→句',
  spelling: '拼写',
}

export function QuizStatsCard() {
  const quizHistory = useProgressStore((s) => s.quizHistory)
  const setView = useUIStore((s) => s.setView)
  const [showHistory, setShowHistory] = useState(false)

  const stats = useMemo(() => {
    if (quizHistory.length === 0) {
      return {
        totalQuizzes: 0,
        totalQuestions: 0,
        totalCorrect: 0,
        bestAccuracy: 0,
        bestAccuracyQuiz: null as QuizRecord | null,
        fastestAvg: null as { avgSec: number; quiz: QuizRecord } | null,
        recentQuizzes: [] as QuizRecord[],
      }
    }

    const totalQuizzes = quizHistory.length
    const totalQuestions = quizHistory.reduce((s, q) => s + q.total, 0)
    const totalCorrect = quizHistory.reduce((s, q) => s + q.correct, 0)

    // best accuracy (min 5 questions to qualify)
    let bestAccuracy = 0
    let bestAccuracyQuiz: QuizRecord | null = null
    for (const q of quizHistory) {
      if (q.total < 5) continue
      const acc = q.correct / q.total
      if (acc > bestAccuracy) {
        bestAccuracy = acc
        bestAccuracyQuiz = q
      }
    }

    // fastest average per question (timed quizzes only)
    let fastestAvg: { avgSec: number; quiz: QuizRecord } | null = null
    for (const q of quizHistory) {
      if (!q.durationMs || q.total < 5) continue
      const avgSec = q.durationMs / 1000 / q.total
      if (!fastestAvg || avgSec < fastestAvg.avgSec) {
        fastestAvg = { avgSec, quiz: q }
      }
    }

    const recentQuizzes = [...quizHistory].slice(-10).reverse()

    return {
      totalQuizzes,
      totalQuestions,
      totalCorrect,
      bestAccuracy: bestAccuracy * 100,
      bestAccuracyQuiz,
      fastestAvg,
      recentQuizzes,
    }
  }, [quizHistory])

  const overallAccuracy = stats.totalQuestions > 0
    ? Math.round((stats.totalCorrect / stats.totalQuestions) * 100)
    : 0

  if (quizHistory.length === 0) {
    return (
      <Card className="p-5">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold flex items-center gap-2">
            <Trophy className="h-4 w-4 text-amber-500" />
            测验统计
          </h3>
        </div>
        <div className="py-6 text-center">
          <Trophy className="h-8 w-8 mx-auto mb-2 text-muted-foreground/30" />
          <p className="text-xs text-muted-foreground">完成测验后这里会显示你的成绩统计</p>
          <Button
            variant="outline"
            size="sm"
            className="mt-3 text-xs"
            onClick={() => setView('quiz')}
          >
            去测验
          </Button>
        </div>
      </Card>
    )
  }

  return (
    <Card className="p-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold flex items-center gap-2">
          <Trophy className="h-4 w-4 text-amber-500" />
          测验统计
        </h3>
        <Button
          variant="ghost"
          size="sm"
          className="h-6 px-2 text-xs"
          onClick={() => setShowHistory((s) => !s)}
        >
          <History className="h-3 w-3 mr-1" />
          {showHistory ? '收起' : '历史'}
        </Button>
      </div>

      {/* Overall stats grid */}
      <div className="grid grid-cols-3 gap-2 mb-3">
        <div className="rounded-lg bg-amber-50 dark:bg-amber-950/30 p-2.5 text-center">
          <div className="text-lg font-bold text-amber-600 dark:text-amber-400 tabular-nums">
            {stats.totalQuizzes}
          </div>
          <div className="text-[10px] text-muted-foreground">测验次数</div>
        </div>
        <div className="rounded-lg bg-emerald-50 dark:bg-emerald-950/30 p-2.5 text-center">
          <div className="text-lg font-bold text-emerald-600 dark:text-emerald-400 tabular-nums">
            {overallAccuracy}%
          </div>
          <div className="text-[10px] text-muted-foreground">总正确率</div>
        </div>
        <div className="rounded-lg bg-sky-50 dark:bg-sky-950/30 p-2.5 text-center">
          <div className="text-lg font-bold text-sky-600 dark:text-sky-400 tabular-nums">
            {stats.totalQuestions}
          </div>
          <div className="text-[10px] text-muted-foreground">答题总数</div>
        </div>
      </div>

      {/* Personal bests */}
      <div className="space-y-2">
        {stats.bestAccuracyQuiz && (
          <div className="flex items-center gap-2 rounded-lg border border-amber-200 dark:border-amber-900 bg-amber-50/50 dark:bg-amber-950/20 p-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-amber-500 text-white shrink-0">
              <Award className="h-4 w-4" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-medium">最高正确率</div>
              <div className="text-[11px] text-muted-foreground">
                {Math.round(stats.bestAccuracy)}% · {stats.bestAccuracyQuiz.correct}/{stats.bestAccuracyQuiz.total} · {modeLabels[stats.bestAccuracyQuiz.mode] || stats.bestAccuracyQuiz.mode}
              </div>
            </div>
          </div>
        )}

        {stats.fastestAvg && (
          <div className="flex items-center gap-2 rounded-lg border border-orange-200 dark:border-orange-900 bg-orange-50/50 dark:bg-orange-950/20 p-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-orange-500 text-white shrink-0">
              <Zap className="h-4 w-4" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-medium">最快答题速度</div>
              <div className="text-[11px] text-muted-foreground">
                {stats.fastestAvg.avgSec.toFixed(1)}s/题 · {modeLabels[stats.fastestAvg.quiz.mode] || stats.fastestAvg.quiz.mode}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* History */}
      {showHistory && (
        <div className="mt-3 pt-3 border-t border-border/60 animate-fade-in-up">
          <div className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wide mb-2">
            最近 {stats.recentQuizzes.length} 次测验
          </div>
          <div className="space-y-1.5 max-h-60 overflow-y-auto pr-1">
            {stats.recentQuizzes.map((q, i) => {
              const acc = q.total > 0 ? Math.round((q.correct / q.total) * 100) : 0
              const date = new Date(q.date)
              const dateStr = `${date.getMonth() + 1}/${date.getDate()} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
              return (
                <div key={i} className="flex items-center gap-2 rounded-md border p-2 text-xs">
                  <div className={cn(
                    'shrink-0 flex h-6 w-6 items-center justify-center rounded-full text-[10px] font-bold',
                    acc >= 80 ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300'
                    : acc >= 60 ? 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300'
                    : 'bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300',
                  )}>
                    {acc}%
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5">
                      <span className="font-medium">{q.correct}/{q.total}</span>
                      <Badge variant="outline" className="text-[9px] px-1 py-0">
                        {modeLabels[q.mode] || q.mode}
                      </Badge>
                      {q.durationMs && (
                        <span className="text-[10px] text-muted-foreground font-mono">
                          {formatTime(q.durationMs)}
                        </span>
                      )}
                    </div>
                    <div className="text-[10px] text-muted-foreground">{dateStr}</div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </Card>
  )
}
