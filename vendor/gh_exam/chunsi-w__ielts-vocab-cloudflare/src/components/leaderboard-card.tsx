'use client'

import { useMemo } from 'react'
import { Medal, TrendingUp, Clock } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useProgressStore } from '@/store/progress'
import { cn } from '@/lib/utils'

const modeLabels: Record<string, string> = {
  en_to_zh: '英→中',
  zh_to_en: '中→英',
  en_to_sentence: '词→句',
  spelling: '拼写',
  cloze: '填空',
}

interface ModeBest {
  mode: string
  bestAccuracy: number
  bestAccuracyCorrect: number
  bestAccuracyTotal: number
  bestAccuracyDate: number
  fastestAvgSec: number | null
  fastestDate: number
  attempts: number
}

function formatTime(ms: number): string {
  const totalSec = Math.floor(ms / 1000)
  const min = Math.floor(totalSec / 60)
  const sec = totalSec % 60
  return `${String(min).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
}

export function LeaderboardCard() {
  const quizHistory = useProgressStore((s) => s.quizHistory)

  const modeBests = useMemo<ModeBest[]>(() => {
    const byMode = new Map<string, ModeBest>()
    for (const q of quizHistory) {
      const mode = q.mode
      if (!byMode.has(mode)) {
        byMode.set(mode, {
          mode,
          bestAccuracy: 0,
          bestAccuracyCorrect: 0,
          bestAccuracyTotal: 0,
          bestAccuracyDate: 0,
          fastestAvgSec: null,
          fastestDate: 0,
          attempts: 0,
        })
      }
      const best = byMode.get(mode)!
      best.attempts++
      const acc = q.total > 0 ? q.correct / q.total : 0
      // best accuracy (min 5 questions)
      if (q.total >= 5 && acc > best.bestAccuracy) {
        best.bestAccuracy = acc
        best.bestAccuracyCorrect = q.correct
        best.bestAccuracyTotal = q.total
        best.bestAccuracyDate = q.date
      }
      // fastest average
      if (q.durationMs && q.total >= 5) {
        const avgSec = q.durationMs / 1000 / q.total
        if (best.fastestAvgSec === null || avgSec < best.fastestAvgSec) {
          best.fastestAvgSec = avgSec
          best.fastestDate = q.date
        }
      }
    }
    // sort by bestAccuracy desc
    return Array.from(byMode.values()).sort((a, b) => b.bestAccuracy - a.bestAccuracy)
  }, [quizHistory])

  if (quizHistory.length === 0) return null

  return (
    <Card className="p-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold flex items-center gap-2">
          <Medal className="h-4 w-4 text-amber-500" />
          模式排行榜
        </h3>
        <Badge variant="secondary" className="text-[10px]">
          {quizHistory.length} 次
        </Badge>
      </div>

      <div className="space-y-2">
        {modeBests.map((best, idx) => {
          const pct = Math.round(best.bestAccuracy * 100)
          const medalColor = idx === 0 ? 'text-amber-500' : idx === 1 ? 'text-slate-400' : idx === 2 ? 'text-orange-600' : 'text-muted-foreground'
          return (
            <div
              key={best.mode}
              className={cn(
                'rounded-lg border p-2.5 transition-all',
                idx === 0 && 'border-amber-200 dark:border-amber-900 bg-amber-50/50 dark:bg-amber-950/20',
              )}
            >
              <div className="flex items-center gap-2">
                <div className={cn('text-base font-bold shrink-0', medalColor)}>
                  {idx + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs font-medium">{modeLabels[best.mode] || best.mode}</span>
                    <span className="text-[10px] text-muted-foreground">({best.attempts}次)</span>
                  </div>
                  <div className="flex items-center gap-3 mt-0.5">
                    <span className="flex items-center gap-1 text-[11px]">
                      <TrendingUp className="h-3 w-3 text-emerald-500" />
                      <span className="font-semibold text-emerald-600 dark:text-emerald-400">
                        {pct}%
                      </span>
                      <span className="text-muted-foreground">
                        ({best.bestAccuracyCorrect}/{best.bestAccuracyTotal})
                      </span>
                    </span>
                    {best.fastestAvgSec !== null && (
                      <span className="flex items-center gap-1 text-[11px]">
                        <Clock className="h-3 w-3 text-orange-500" />
                        <span className="font-semibold text-orange-600 dark:text-orange-400">
                          {best.fastestAvgSec.toFixed(1)}s/题
                        </span>
                      </span>
                    )}
                  </div>
                </div>
                {idx === 0 && pct > 0 && (
                  <Medal className={cn('h-4 w-4 shrink-0', medalColor)} />
                )}
              </div>
            </div>
          )
        })}
      </div>
    </Card>
  )
}
