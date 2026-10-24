'use client'

import { useMemo, useState } from 'react'
import { Target, Check, Trophy, Settings2, ChevronDown, ChevronUp } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useProgressStore } from '@/store/progress'
import { useUIStore } from '@/store/ui'
import { cn } from '@/lib/utils'

export function DailyGoalCard() {
  const dailyGoal = useProgressStore((s) => s.dailyGoal)
  const setDailyGoal = useProgressStore((s) => s.setDailyGoal)
  const studyHistory = useProgressStore((s) => s.studyHistory)
  const quizHistory = useProgressStore((s) => s.quizHistory)
  const setView = useUIStore((s) => s.setView)
  const [editing, setEditing] = useState(false)

  const { todayWords, todayQuiz, totalToday, pct, completed } = useMemo(() => {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const todayMs = today.getTime()
    const todayStudy = studyHistory.filter((s) => s.date >= todayMs)
    const todayQuizSessions = quizHistory.filter((q) => q.date >= todayMs)
    const words = todayStudy.reduce((sum, s) => sum + s.count, 0)
    const quiz = todayQuizSessions.reduce((sum, q) => sum + q.total, 0)
    const total = words + quiz
    const pct = dailyGoal > 0 ? Math.min(100, Math.round((total / dailyGoal) * 100)) : 0
    return {
      todayWords: words,
      todayQuiz: quiz,
      totalToday: total,
      pct,
      completed: total >= dailyGoal,
    }
  }, [studyHistory, quizHistory, dailyGoal])

  // SVG ring geometry
  const size = 96
  const strokeWidth = 8
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (pct / 100) * circumference

  const goalOptions = [10, 20, 30, 50, 100]

  return (
    <Card className={cn(
      'p-5 transition-all',
      completed && 'bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-950/40 dark:to-teal-950/40 border-emerald-200 dark:border-emerald-900',
    )}>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold flex items-center gap-2">
          <Target className="h-4 w-4 text-primary" />
          每日目标
        </h3>
        <Button
          variant="ghost"
          size="sm"
          className="h-6 px-2 text-xs"
          onClick={() => setEditing((e) => !e)}
        >
          <Settings2 className="h-3 w-3 mr-1" />
          {dailyGoal} 词
          {editing ? <ChevronUp className="h-3 w-3 ml-1" /> : <ChevronDown className="h-3 w-3 ml-1" />}
        </Button>
      </div>

      {editing && (
        <div className="mb-3 flex gap-1.5 flex-wrap animate-fade-in-up">
          {goalOptions.map((n) => (
            <Button
              key={n}
              size="sm"
              variant={dailyGoal === n ? 'default' : 'outline'}
              className="h-7 px-2.5 text-xs"
              onClick={() => {
                setDailyGoal(n)
                setEditing(false)
              }}
            >
              {n}
            </Button>
          ))}
        </div>
      )}

      <div className="flex items-center gap-4">
        {/* Progress ring */}
        <div className="relative shrink-0" style={{ width: size, height: size }}>
          <svg width={size} height={size} className="-rotate-90">
            <circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="none"
              stroke="currentColor"
              strokeWidth={strokeWidth}
              className="text-muted/40"
            />
            <circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="none"
              stroke="currentColor"
              strokeWidth={strokeWidth}
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              className={cn(
                'transition-all duration-700 ease-out',
                completed ? 'text-emerald-500' : pct >= 50 ? 'text-amber-500' : 'text-rose-500',
              )}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            {completed ? (
              <Check className="h-7 w-7 text-emerald-500" />
            ) : (
              <>
                <span className="text-xl font-bold tabular-nums">{pct}%</span>
                <span className="text-[10px] text-muted-foreground">完成</span>
              </>
            )}
          </div>
        </div>

        {/* Stats */}
        <div className="flex-1 min-w-0 space-y-1.5">
          {completed ? (
            <div className="flex items-center gap-1.5 text-sm font-medium text-emerald-700 dark:text-emerald-400">
              <Trophy className="h-4 w-4" />
              今日目标已达成！
            </div>
          ) : (
            <div className="text-sm">
              <span className="font-bold tabular-nums">{totalToday}</span>
              <span className="text-muted-foreground"> / {dailyGoal} 词</span>
            </div>
          )}
          <div className="flex items-center gap-3 text-[11px] text-muted-foreground">
            <span>学习 {todayWords} 词</span>
            <span>·</span>
            <span>测验 {todayQuiz} 题</span>
          </div>
          {!completed && totalToday > 0 && (
            <div className="text-[11px] text-muted-foreground">
              还差 <span className="font-semibold text-foreground">{dailyGoal - totalToday}</span> 词达成目标
            </div>
          )}
          {!completed && totalToday === 0 && (
            <Button size="sm" variant="outline" className="h-7 mt-1 text-xs" onClick={() => setView('study')}>
              开始今日学习
            </Button>
          )}
        </div>
      </div>
    </Card>
  )
}
