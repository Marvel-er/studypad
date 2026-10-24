'use client'

import { useMemo, useState } from 'react'
import { Calendar } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { useProgressStore } from '@/store/progress'
import { cn } from '@/lib/utils'

const WEEKS = 18 // ~18 weeks ≈ 126 days
const DAYS = WEEKS * 7

function dayKey(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function getWeekday(d: Date): number {
  // 0 = Sunday ... 6 = Saturday
  return d.getDay()
}

export function StudyHeatmap() {
  const quizHistory = useProgressStore((s) => s.quizHistory)
  const studyHistory = useProgressStore((s) => s.studyHistory)
  const [hoveredCell, setHoveredCell] = useState<{ x: number; y: number; date: Date; words: number; total: number } | null>(null)

  const { cells, monthLabels, totalWords, totalQuizzes, activeDays } = useMemo(() => {
    // aggregate activity by day
    const map = new Map<string, { words: number; correct: number; total: number }>()
    const today = new Date()
    today.setHours(0, 0, 0, 0)

    // index study history
    for (const s of studyHistory) {
      const d = new Date(s.date)
      d.setHours(0, 0, 0, 0)
      const k = dayKey(d)
      const cur = map.get(k) || { words: 0, correct: 0, total: 0 }
      cur.words += s.count
      map.set(k, cur)
    }
    // index quiz history
    for (const q of quizHistory) {
      const d = new Date(q.date)
      d.setHours(0, 0, 0, 0)
      const k = dayKey(d)
      const cur = map.get(k) || { words: 0, correct: 0, total: 0 }
      cur.total += q.total
      cur.correct += q.correct
      map.set(k, cur)
    }

    // Build grid aligned to week (start Sunday)
    const cells: Array<{ date: Date; words: number; total: number; intensity: 0 | 1 | 2 | 3 | 4; isToday: boolean; isFuture: boolean }> = []
    // start from WEEKS*7 days ago, aligned to Sunday
    const start = new Date(today)
    start.setDate(start.getDate() - (DAYS - 1))
    // align start to Sunday
    start.setDate(start.getDate() - getWeekday(start))

    for (let i = 0; i < DAYS; i++) {
      const d = new Date(start)
      d.setDate(start.getDate() + i)
      const k = dayKey(d)
      const act = map.get(k)
      const words = act?.words ?? 0
      const total = act?.total ?? 0
      const combined = words + total
      let intensity: 0 | 1 | 2 | 3 | 4 = 0
      if (combined >= 30) intensity = 4
      else if (combined >= 15) intensity = 3
      else if (combined >= 6) intensity = 2
      else if (combined >= 1) intensity = 1
      cells.push({
        date: d,
        words,
        total,
        intensity,
        isToday: k === dayKey(today),
        isFuture: d > today,
      })
    }

    // Month labels - show first week of each month
    const monthLabels: Array<{ label: string; col: number }> = []
    let lastMonth = -1
    for (let i = 0; i < WEEKS; i++) {
      const firstCell = cells[i * 7]
      if (firstCell) {
        const m = firstCell.date.getMonth()
        if (m !== lastMonth) {
          monthLabels.push({ label: `${m + 1}月`, col: i })
          lastMonth = m
        }
      }
    }

    const totalWords = studyHistory.reduce((s, h) => s + h.count, 0)
    const totalQuizzes = quizHistory.reduce((s, h) => s + h.total, 0)
    const activeDays = map.size

    return { cells, monthLabels, totalWords, totalQuizzes, activeDays }
  }, [quizHistory, studyHistory])

  const maxIntensity = 4

  return (
    <Card className="p-4 sm:p-5">
      <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
        <h3 className="text-sm font-semibold flex items-center gap-2">
          <Calendar className="h-4 w-4 text-primary" />
          学习日历
        </h3>
        <div className="flex items-center gap-3 text-[11px] text-muted-foreground">
          <span>活跃 {activeDays} 天</span>
          <span>·</span>
          <span>累计 {totalWords} 词</span>
          <span>·</span>
          <span>{totalQuizzes} 题</span>
        </div>
      </div>

      {activeDays === 0 ? (
        <div className="py-6 text-center text-xs text-muted-foreground">
          <Calendar className="h-8 w-8 mx-auto mb-2 text-muted-foreground/30" />
          暂无学习记录，开始学习后会在这里展示学习热力图
        </div>
      ) : (
        <>
          {/* Month labels */}
          <div className="flex gap-[3px] pl-6 mb-1 text-[10px] text-muted-foreground relative">
            {Array.from({ length: WEEKS }).map((_, i) => {
              const label = monthLabels.find((m) => m.col === i)
              return (
                <div key={i} className="w-[14px] text-center" style={{ minWidth: '14px' }}>
                  {label?.label}
                </div>
              )
            })}
          </div>

          <div className="flex gap-[3px]">
            {/* Weekday labels */}
            <div className="flex flex-col gap-[3px] w-6 text-[10px] text-muted-foreground pr-1">
              <div className="h-[14px] leading-[14px]">一</div>
              <div className="h-[14px]" />
              <div className="h-[14px] leading-[14px]">三</div>
              <div className="h-[14px]" />
              <div className="h-[14px] leading-[14px]">五</div>
              <div className="h-[14px]" />
              <div className="h-[14px]" />
            </div>

            {/* Grid + tooltip container */}
            <div className="relative flex-1 min-w-0" data-heatmap-container>
            <div className="flex gap-[3px] overflow-x-auto">
              {Array.from({ length: WEEKS }).map((_, weekIdx) => (
                <div key={weekIdx} className="flex flex-col gap-[3px]">
                  {Array.from({ length: 7 }).map((_, dayIdx) => {
                    const cell = cells[weekIdx * 7 + dayIdx]
                    if (!cell || cell.isFuture) {
                      return <div key={dayIdx} className="w-[14px] h-[14px]" style={{ width: 14, height: 14 }} />
                    }
                    return (
                      <div
                        key={dayIdx}
                        onMouseEnter={(e) => {
                          const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
                          const containerRect = (e.currentTarget as HTMLElement).closest('[data-heatmap-container]')?.getBoundingClientRect()
                          setHoveredCell({
                            x: rect.left - (containerRect?.left ?? 0) + rect.width / 2,
                            y: rect.top - (containerRect?.top ?? 0),
                            date: cell.date,
                            words: cell.words,
                            total: cell.total,
                          })
                        }}
                        onMouseLeave={() => setHoveredCell(null)}
                        className={cn(
                          'w-[14px] h-[14px] rounded-[3px] cursor-default transition-all hover:ring-2 hover:ring-primary/50 hover:scale-125',
                          cell.intensity === 0 && 'bg-muted-foreground/15',
                          cell.intensity === 1 && 'bg-rose-200 dark:bg-rose-900/70',
                          cell.intensity === 2 && 'bg-rose-400 dark:bg-rose-700',
                          cell.intensity === 3 && 'bg-rose-500 dark:bg-rose-600',
                          cell.intensity === 4 && 'bg-rose-600 dark:bg-rose-500',
                          cell.isToday && 'ring-2 ring-offset-1 ring-offset-background ring-primary',
                        )}
                        style={{ width: 14, height: 14 }}
                      />
                    )
                  })}
                </div>
              ))}
            </div>

            {/* Hover tooltip */}
            {hoveredCell && (
              <div
                className="absolute z-20 pointer-events-none animate-fade-in-up"
                style={{
                  left: hoveredCell.x,
                  top: hoveredCell.y - 4,
                  transform: 'translate(-50%, -100%)',
                }}
              >
                <div className="rounded-md bg-popover border border-border shadow-lg px-2.5 py-1.5 text-[11px] whitespace-nowrap">
                  <div className="font-semibold">
                    {hoveredCell.date.getFullYear()}/{hoveredCell.date.getMonth() + 1}/{hoveredCell.date.getDate()}
                  </div>
                  <div className="text-muted-foreground mt-0.5">
                    {hoveredCell.words === 0 && hoveredCell.total === 0 ? (
                      <span>无学习记录</span>
                    ) : (
                      <>
                        {hoveredCell.words > 0 && <span>学习 {hoveredCell.words} 词</span>}
                        {hoveredCell.words > 0 && hoveredCell.total > 0 && <span> · </span>}
                        {hoveredCell.total > 0 && <span>测验 {hoveredCell.total} 题</span>}
                      </>
                    )}
                  </div>
                </div>
                <div
                  className="absolute left-1/2 -translate-x-1/2 top-full border-4 border-transparent"
                  style={{ borderTopColor: 'var(--popover)' }}
                />
              </div>
            )}
            </div>
          </div>

          {/* Legend */}
          <div className="flex items-center justify-end gap-1.5 mt-2 text-[10px] text-muted-foreground">
            <span>少</span>
            {[0, 1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className={cn(
                  'w-[12px] h-[12px] rounded-[3px]',
                  i === 0 && 'bg-muted/60',
                  i === 1 && 'bg-rose-200 dark:bg-rose-900/60',
                  i === 2 && 'bg-rose-400 dark:bg-rose-700',
                  i === 3 && 'bg-rose-500 dark:bg-rose-600',
                  i === 4 && 'bg-rose-600 dark:bg-rose-500',
                )}
              />
            ))}
            <span>多</span>
          </div>
        </>
      )}
    </Card>
  )
}
