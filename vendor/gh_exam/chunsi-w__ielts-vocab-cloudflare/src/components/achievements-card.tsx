'use client'

import { useMemo } from 'react'
import { Trophy, Flame, Target, Zap, BookOpen, Star, CheckCircle2, Crown, Award, Medal } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useProgressStore } from '@/store/progress'
import { computeAchievements } from '@/lib/achievements'
import { cn } from '@/lib/utils'

const iconMap: Record<string, typeof Trophy> = {
  Trophy,
  Flame,
  Target,
  Zap,
  BookOpen,
  Star,
  CheckCircle2,
  Crown,
  Award,
  Medal,
}

export function AchievementsCard() {
  const progress = useProgressStore((s) => s.progress)
  const quizHistory = useProgressStore((s) => s.quizHistory)
  const studyHistory = useProgressStore((s) => s.studyHistory)

  const achievements = useMemo(
    () => computeAchievements(progress, quizHistory, studyHistory),
    [progress, quizHistory, studyHistory],
  )

  const unlockedCount = achievements.filter((a) => a.unlocked).length

  return (
    <Card className="p-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold flex items-center gap-2">
          <Trophy className="h-4 w-4 text-amber-500" />
          学习成就
        </h3>
        <Badge variant="secondary" className="text-[10px]">
          {unlockedCount}/{achievements.length}
        </Badge>
      </div>

      <div className="grid grid-cols-2 gap-2">
        {achievements.map((a) => {
          const Icon = iconMap[a.icon] || Trophy
          return (
            <div
              key={a.id}
              className={cn(
                'rounded-lg border p-2.5 transition-all',
                a.unlocked
                  ? 'border-border bg-card hover:shadow-sm'
                  : 'border-border/40 bg-muted/30 opacity-60',
              )}
            >
              <div className="flex items-center gap-2">
                <div className={cn(
                  'flex h-8 w-8 items-center justify-center rounded-lg shrink-0',
                  a.unlocked ? a.bgColor : 'bg-muted',
                )}>
                  <Icon className={cn('h-4 w-4', a.unlocked ? a.color : 'text-muted-foreground')} />
                </div>
                <div className="min-w-0 flex-1">
                  <div className={cn(
                    'text-xs font-medium truncate',
                    a.unlocked ? 'text-foreground' : 'text-muted-foreground',
                  )}>
                    {a.title}
                  </div>
                  <div className="text-[9px] text-muted-foreground truncate">{a.desc}</div>
                </div>
              </div>
              {a.progress && !a.unlocked && (
                <div className="mt-1.5">
                  <div className="flex justify-between text-[9px] text-muted-foreground mb-0.5">
                    <span>{a.progress.current}/{a.progress.target}</span>
                    <span>{Math.round((a.progress.current / a.progress.target) * 100)}%</span>
                  </div>
                  <div className="h-1 rounded-full bg-muted overflow-hidden">
                    <div
                      className="h-full bg-primary rounded-full transition-all"
                      style={{ width: `${Math.min(100, (a.progress.current / a.progress.target) * 100)}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </Card>
  )
}
