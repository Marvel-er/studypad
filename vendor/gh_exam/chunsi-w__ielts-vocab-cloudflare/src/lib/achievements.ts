/**
 * Achievement definitions and unlock logic.
 * Shared between AchievementsCard (display) and unlock detector (toast/confetti).
 */
import type { WordProgress } from '@/store/progress'

export interface Achievement {
  id: string
  title: string
  desc: string
  icon: string // lucide icon name
  color: string
  bgColor: string
  unlocked: boolean
  progress?: { current: number; target: number }
}

export function computeStreak(history: Array<{ date: number }>): number {
  if (history.length === 0) return 0
  const days = new Set<string>()
  for (const h of history) {
    const d = new Date(h.date)
    d.setHours(0, 0, 0, 0)
    days.add(d.toISOString().slice(0, 10))
  }
  let streak = 0
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  for (let i = 0; i < 365; i++) {
    const d = new Date(today.getTime() - i * 86400000)
    const key = d.toISOString().slice(0, 10)
    if (days.has(key)) {
      streak++
    } else if (i === 0) {
      continue
    } else {
      break
    }
  }
  return streak
}

export function computeAchievements(
  progress: Record<number, WordProgress>,
  quizHistory: Array<{ date: number; total: number; correct: number; mode: string }>,
  studyHistory: Array<{ date: number; count: number }>,
): Achievement[] {
  const learnedCount = Object.values(progress).filter((p) => p.learned || p.mastery >= 4).length
  const favoriteCount = Object.values(progress).filter((p) => p.favorite).length
  const totalQuizzes = quizHistory.length
  const totalQuestions = quizHistory.reduce((s, q) => s + q.total, 0)
  const perfectQuizzes = quizHistory.filter((q) => q.total >= 5 && q.correct === q.total).length
  const streak = computeStreak([...quizHistory, ...studyHistory])

  return [
    {
      id: 'first-step',
      title: '初学乍练',
      desc: '学习第一个单词',
      icon: 'BookOpen',
      color: 'text-emerald-600 dark:text-emerald-400',
      bgColor: 'bg-emerald-100 dark:bg-emerald-950/40',
      unlocked: Object.keys(progress).length >= 1,
    },
    {
      id: 'vocab-100',
      title: '百词斩',
      desc: '掌握 100 个单词',
      icon: 'Target',
      color: 'text-sky-600 dark:text-sky-400',
      bgColor: 'bg-sky-100 dark:bg-sky-950/40',
      unlocked: learnedCount >= 100,
      progress: { current: Math.min(learnedCount, 100), target: 100 },
    },
    {
      id: 'vocab-500',
      title: '词汇达人',
      desc: '掌握 500 个单词',
      icon: 'Award',
      color: 'text-violet-600 dark:text-violet-400',
      bgColor: 'bg-violet-100 dark:bg-violet-950/40',
      unlocked: learnedCount >= 500,
      progress: { current: Math.min(learnedCount, 500), target: 500 },
    },
    {
      id: 'vocab-1000',
      title: '词汇大师',
      desc: '掌握 1000 个单词',
      icon: 'Crown',
      color: 'text-amber-600 dark:text-amber-400',
      bgColor: 'bg-amber-100 dark:bg-amber-950/40',
      unlocked: learnedCount >= 1000,
      progress: { current: Math.min(learnedCount, 1000), target: 1000 },
    },
    {
      id: 'streak-3',
      title: '连续学习',
      desc: '连续 3 天学习',
      icon: 'Flame',
      color: 'text-orange-600 dark:text-orange-400',
      bgColor: 'bg-orange-100 dark:bg-orange-950/40',
      unlocked: streak >= 3,
      progress: { current: Math.min(streak, 3), target: 3 },
    },
    {
      id: 'streak-7',
      title: '一周不辍',
      desc: '连续 7 天学习',
      icon: 'Flame',
      color: 'text-rose-600 dark:text-rose-400',
      bgColor: 'bg-rose-100 dark:bg-rose-950/40',
      unlocked: streak >= 7,
      progress: { current: Math.min(streak, 7), target: 7 },
    },
    {
      id: 'quiz-10',
      title: '测验新手',
      desc: '完成 10 次测验',
      icon: 'Zap',
      color: 'text-cyan-600 dark:text-cyan-400',
      bgColor: 'bg-cyan-100 dark:bg-cyan-950/40',
      unlocked: totalQuizzes >= 10,
      progress: { current: Math.min(totalQuizzes, 10), target: 10 },
    },
    {
      id: 'perfect-1',
      title: '完美一次',
      desc: '测验全对 (≥5题)',
      icon: 'Medal',
      color: 'text-yellow-600 dark:text-yellow-400',
      bgColor: 'bg-yellow-100 dark:bg-yellow-950/40',
      unlocked: perfectQuizzes >= 1,
      progress: { current: Math.min(perfectQuizzes, 1), target: 1 },
    },
    {
      id: 'perfect-5',
      title: '完美主义者',
      desc: '5 次测验全对',
      icon: 'Trophy',
      color: 'text-amber-600 dark:text-amber-400',
      bgColor: 'bg-amber-100 dark:bg-amber-950/40',
      unlocked: perfectQuizzes >= 5,
      progress: { current: Math.min(perfectQuizzes, 5), target: 5 },
    },
    {
      id: 'favorite-50',
      title: '收藏家',
      desc: '收藏 50 个单词',
      icon: 'Star',
      color: 'text-pink-600 dark:text-pink-400',
      bgColor: 'bg-pink-100 dark:bg-pink-950/40',
      unlocked: favoriteCount >= 50,
      progress: { current: Math.min(favoriteCount, 50), target: 50 },
    },
    {
      id: 'questions-200',
      title: '答题200',
      desc: '累计答题 200 题',
      icon: 'CheckCircle2',
      color: 'text-teal-600 dark:text-teal-400',
      bgColor: 'bg-teal-100 dark:bg-teal-950/40',
      unlocked: totalQuestions >= 200,
      progress: { current: Math.min(totalQuestions, 200), target: 200 },
    },
  ]
}
