'use client'

import { useEffect, useRef, useState } from 'react'
import { Trophy, X } from 'lucide-react'
import { useProgressStore } from '@/store/progress'
import { computeAchievements, type Achievement } from '@/lib/achievements'
import { Confetti } from '@/components/confetti'
import { toast } from 'sonner'
import * as Icons from 'lucide-react'

/**
 * Detects newly unlocked achievements and shows a toast + confetti celebration.
 * Tracks unlocked achievement IDs in a ref to detect transitions.
 */
export function AchievementUnlockDetector() {
  const progress = useProgressStore((s) => s.progress)
  const quizHistory = useProgressStore((s) => s.quizHistory)
  const studyHistory = useProgressStore((s) => s.studyHistory)
  const unlockedRef = useRef<Set<string>>(new Set())
  const [confettiTrigger, setConfettiTrigger] = useState(0)
  const [initialized, setInitialized] = useState(false)

  useEffect(() => {
    const achievements = computeAchievements(progress, quizHistory, studyHistory)
    const currentlyUnlocked = new Set(
      achievements.filter((a) => a.unlocked).map((a) => a.id),
    )

    if (!initialized) {
      // First run: initialize without showing toasts for already-unlocked
      unlockedRef.current = currentlyUnlocked
      Promise.resolve().then(() => setInitialized(true))
      return
    }

    // Detect newly unlocked
    const newlyUnlocked: Achievement[] = []
    for (const a of achievements) {
      if (a.unlocked && !unlockedRef.current.has(a.id)) {
        newlyUnlocked.push(a)
      }
    }

    if (newlyUnlocked.length > 0) {
      // Update the ref
      for (const a of newlyUnlocked) {
        unlockedRef.current.add(a.id)
      }
      // Show toast + confetti for the first newly unlocked achievement
      const first = newlyUnlocked[0]
      const IconComponent = (Icons as any)[first.icon] || Trophy
      toast.custom(
        (t) => (
          <div className="bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-950/40 dark:to-orange-950/40 border-2 border-amber-300 dark:border-amber-700 rounded-lg p-3 shadow-lg flex items-center gap-3 max-w-sm">
            <div className={`flex h-10 w-10 items-center justify-center rounded-full ${first.bgColor} shrink-0`}>
              <IconComponent className={`h-5 w-5 ${first.color}`} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-semibold text-amber-700 dark:text-amber-400 flex items-center gap-1">
                <Trophy className="h-3 w-3" />
                成就解锁！
              </div>
              <div className="text-sm font-bold truncate">{first.title}</div>
              <div className="text-[11px] text-muted-foreground truncate">{first.desc}</div>
            </div>
            <button
              onClick={() => toast.dismiss(t)}
              className="text-muted-foreground hover:text-foreground shrink-0"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        ),
        { duration: 5000 },
      )
      // Trigger confetti (defer to avoid synchronous setState in effect)
      Promise.resolve().then(() => setConfettiTrigger((t) => t + 1))
    } else {
      // Update ref in case some achievements were reset (e.g. clearAll)
      unlockedRef.current = currentlyUnlocked
    }
  }, [progress, quizHistory, studyHistory, initialized])

  return <Confetti trigger={confettiTrigger} duration={4000} count={120} />
}
