'use client'

import { useEffect, useState, useRef } from 'react'
import {
  BookOpen,
  GraduationCap,
  ClipboardCheck,
  Star,
  TrendingUp,
  ListChecks,
  Sparkles,
  ArrowRight,
  Trophy,
  Flame,
  Calendar,
  Keyboard,
  RefreshCw,
  FileText,
} from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Progress } from '@/components/ui/progress'
import { api } from '@/lib/api'
import { useUIStore } from '@/store/ui'
import { useProgressStore } from '@/store/progress'
import type { Stats, WordListItem } from '@/lib/types'
import { cn } from '@/lib/utils'
import { StudyHeatmap } from '@/components/study-heatmap'
import { DailyGoalCard } from '@/components/daily-goal-card'
import { Confetti } from '@/components/confetti'
import { QuizStatsCard } from '@/components/quiz-stats-card'
import { AchievementsCard } from '@/components/achievements-card'
import { LeaderboardCard } from '@/components/leaderboard-card'
import { QuizTrendChart } from '@/components/quiz-trend-chart'
import { getReviewStats } from '@/lib/review'

const groupColors: Record<number, string> = {
  1: 'from-rose-500 to-pink-500',
  2: 'from-orange-500 to-amber-500',
  3: 'from-amber-500 to-yellow-500',
  4: 'from-emerald-500 to-teal-500',
  5: 'from-teal-500 to-cyan-500',
}

export function HomeView() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [featured, setFeatured] = useState<WordListItem[]>([])
  const setView = useUIStore((s) => s.setView)
  const openWord = useUIStore((s) => s.openWord)
  const setBrowseFilters = useUIStore((s) => s.setBrowseFilters)
  const setStudyGroup = useUIStore((s) => s.setStudyGroup)
  const setQuizConfig = useUIStore((s) => s.setQuizConfig)

  const progress = useProgressStore((s) => s.progress)
  const quizHistory = useProgressStore((s) => s.quizHistory)
  const studyHistory = useProgressStore((s) => s.studyHistory)

  const learnedCount = Object.values(progress).filter((p) => p.learned || p.mastery >= 4).length
  const learningCount = Object.values(progress).filter((p) => p.mastery > 0 && p.mastery < 4).length
  const favoriteCount = Object.values(progress).filter((p) => p.favorite).length
  const reviewStats = getReviewStats(progress)
  const reviewDueCount = reviewStats.dueNow
  const dailyGoal = useProgressStore((s) => s.dailyGoal)

  // Today's study stats
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const todayMs = today.getTime()
  const todayQuiz = quizHistory.filter((q) => q.date >= todayMs)
  const todayStudy = studyHistory.filter((s) => s.date >= todayMs)
  const todayWords = todayStudy.reduce((sum, s) => sum + s.count, 0)
  const todayCorrect = todayQuiz.reduce((sum, q) => sum + q.correct, 0)
  const todayTotal = todayQuiz.reduce((sum, q) => sum + q.total, 0)
  const accuracy = todayTotal > 0 ? Math.round((todayCorrect / todayTotal) * 100) : 0
  const todayTotalActivity = todayWords + todayTotal
  const goalCompleted = todayTotalActivity >= dailyGoal && dailyGoal > 0

  // 7-day streak (study or quiz)
  const streak = computeStreak([...quizHistory, ...studyHistory])

  // Confetti trigger: fire once when goal is newly completed
  const [confettiTrigger, setConfettiTrigger] = useState(0)
  const wasCompletedRef = useRef(false)
  useEffect(() => {
    // defer to avoid synchronous setState in effect
    Promise.resolve().then(() => {
      if (goalCompleted && !wasCompletedRef.current) {
        wasCompletedRef.current = true
        setConfettiTrigger((t) => t + 1)
      } else if (!goalCompleted && wasCompletedRef.current) {
        wasCompletedRef.current = false
      }
    })
  }, [goalCompleted])

  useEffect(() => {
    let cancelled = false
    Promise.all([api.stats(), api.randomWords({ count: 4 })])
      .then(([s, r]) => {
        if (cancelled) return
        setStats(s)
        setFeatured(r.words)
      })
      .catch((e) => console.error(e))
      .finally(() => !cancelled && setLoading(false))
    return () => {
      cancelled = true
    }
  }, [])

  const totalWords = stats?.wordCount ?? 22695
  const learnedPct = totalWords > 0 ? Math.round((learnedCount / totalWords) * 100) : 0

  return (
    <div className="space-y-8">
      <Confetti trigger={confettiTrigger} duration={3500} count={100} />
      {/* Hero */}
      <section className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-rose-500 via-orange-500 to-amber-500 p-6 sm:p-10 text-white shadow-lg">
        <div className="absolute inset-0 opacity-20" style={{
          backgroundImage: 'radial-gradient(circle at 20% 30%, white 1px, transparent 1px), radial-gradient(circle at 80% 70%, white 1px, transparent 1px)',
          backgroundSize: '60px 60px, 80px 80px',
        }} />
        <div className="relative z-10 max-w-3xl">
          <Badge className="bg-white/20 text-white border-white/30 hover:bg-white/20 mb-3">
            <Sparkles className="h-3 w-3 mr-1" />
            剑桥雅思真题词频
          </Badge>
          <h1 className="text-3xl sm:text-5xl font-bold leading-tight tracking-tight">
            高效背单词，<br className="sm:hidden" />征服雅思阅读听力
          </h1>
          <p className="mt-3 text-white/85 text-sm sm:text-base max-w-2xl">
            基于剑桥雅思 4-19 真题语料库整理的 22,695 个高频词汇，每个单词配有音标、英英释义、记忆法、真题例句与英美发音。
          </p>
          <div className="mt-5 flex flex-wrap gap-2.5">
            <Button
              size="lg"
              variant="secondary"
              className="bg-white text-rose-600 hover:bg-white/90 font-semibold"
              onClick={() => setView('study')}
            >
              <GraduationCap className="h-4 w-4 mr-1" />
              开始学习
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="bg-transparent border-white/40 text-white hover:bg-white/10 hover:text-white"
              onClick={() => setView('quiz')}
            >
              <ClipboardCheck className="h-4 w-4 mr-1" />
              单词测验
            </Button>
            <Button
              size="lg"
              variant="ghost"
              className="text-white hover:bg-white/10 hover:text-white"
              onClick={() => setView('browse')}
            >
              浏览词库
              <ArrowRight className="h-4 w-4 ml-1" />
            </Button>
          </div>
        </div>
      </section>

      {/* Review reminder banner */}
      {reviewDueCount > 0 && (
        <Card
          className="p-4 border-rose-200 dark:border-rose-900 bg-gradient-to-r from-rose-50 via-orange-50 to-amber-50 dark:from-rose-950/40 dark:via-orange-950/40 dark:to-amber-950/40 cursor-pointer hover:shadow-lg hover:-translate-y-0.5 transition-all animate-fade-in-up relative overflow-hidden"
          onClick={() => setView('review')}
        >
          <div className="absolute inset-0 opacity-30 pointer-events-none" style={{
            background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)',
            backgroundSize: '200% 100%',
            animation: 'shimmer 3s infinite',
          }} />
          <div className="relative flex items-center justify-between gap-3">
            <div className="flex items-center gap-3 min-w-0">
              <div className="relative flex h-10 w-10 items-center justify-center rounded-full bg-rose-500 text-white shrink-0 shadow-md">
                <RefreshCw className="h-5 w-5 animate-spin" style={{ animationDuration: '3s' }} />
                <span className="absolute inset-0 rounded-full bg-rose-500 animate-ping opacity-20" />
              </div>
              <div className="min-w-0">
                <p className="text-sm font-semibold text-rose-700 dark:text-rose-300">
                  {reviewDueCount} 个单词待复习
                </p>
                <p className="text-xs text-muted-foreground">
                  基于艾宾浩斯遗忘曲线，现在复习效果最佳
                </p>
              </div>
            </div>
            <Button size="sm" variant="default" className="shrink-0 bg-rose-500 hover:bg-rose-600 shadow-sm">
              开始复习
              <ArrowRight className="h-3.5 w-3.5 ml-1" />
            </Button>
          </div>
        </Card>
      )}

      {/* Today's stats */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
        <StatCard
          icon={<Flame className="h-5 w-5" />}
          label="连续学习"
          value={`${streak} 天`}
          accent="text-orange-500"
          bgAccent="bg-orange-50 dark:bg-orange-950/40"
        />
        <StatCard
          icon={<ListChecks className="h-5 w-5" />}
          label="今日学习"
          value={`${todayWords} 词`}
          accent="text-emerald-500"
          bgAccent="bg-emerald-50 dark:bg-emerald-950/40"
        />
        <StatCard
          icon={<Trophy className="h-5 w-5" />}
          label="今日正确率"
          value={todayTotal > 0 ? `${accuracy}%` : '—'}
          sub={todayTotal > 0 ? `${todayCorrect}/${todayTotal}` : '今日未测验'}
          accent="text-amber-500"
          bgAccent="bg-amber-50 dark:bg-amber-950/40"
        />
        <StatCard
          icon={<Star className="h-5 w-5" />}
          label="收藏单词"
          value={`${favoriteCount} 词`}
          accent="text-rose-500"
          bgAccent="bg-rose-50 dark:bg-rose-950/40"
        />
      </section>

      {/* Study calendar heatmap */}
      <StudyHeatmap />

      {/* Quiz accuracy trend */}
      <QuizTrendChart />

      {/* Progress overview + daily goal */}
      <section className="grid gap-4 md:grid-cols-3">
        <Card className="p-5 md:col-span-2">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-base font-semibold flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-primary" />
              学习进度
            </h2>
            <Button variant="ghost" size="sm" onClick={() => setView('browse')}>
              查看全部 <ArrowRight className="h-3 w-3 ml-1" />
            </Button>
          </div>
          {loading ? (
            <Skeleton className="h-24 w-full" />
          ) : (
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-xs mb-1.5">
                  <span className="text-muted-foreground">已掌握 / 全部</span>
                  <span className="font-medium">
                    {learnedCount} / {totalWords} ({learnedPct}%)
                  </span>
                </div>
                <Progress value={learnedPct} className="h-2.5" />
              </div>
              <div className="grid grid-cols-3 gap-3 pt-1">
                <div className="rounded-lg bg-emerald-50 dark:bg-emerald-950/30 p-3 text-center">
                  <div className="text-xl font-bold text-emerald-600 dark:text-emerald-400">
                    {learnedCount}
                  </div>
                  <div className="text-[11px] text-muted-foreground mt-0.5">已掌握</div>
                </div>
                <div className="rounded-lg bg-amber-50 dark:bg-amber-950/30 p-3 text-center">
                  <div className="text-xl font-bold text-amber-600 dark:text-amber-400">
                    {learningCount}
                  </div>
                  <div className="text-[11px] text-muted-foreground mt-0.5">学习中</div>
                </div>
                <div className="rounded-lg bg-rose-50 dark:bg-rose-950/30 p-3 text-center">
                  <div className="text-xl font-bold text-rose-600 dark:text-rose-400">
                    {favoriteCount}
                  </div>
                  <div className="text-[11px] text-muted-foreground mt-0.5">已收藏</div>
                </div>
              </div>
            </div>
          )}
        </Card>

        <div className="space-y-4">
        <DailyGoalCard />
        <QuizStatsCard />
        <LeaderboardCard />
        <AchievementsCard />
        <Card className="p-5">
          <h2 className="text-base font-semibold flex items-center gap-2 mb-3">
            <Calendar className="h-4 w-4 text-primary" />
            快速操作
          </h2>
          <div className="space-y-2">
            <Button
              variant="outline"
              className="w-full justify-start gap-2"
              onClick={() => {
                setStudyGroup(null)
                setView('study')
              }}
            >
              <GraduationCap className="h-4 w-4 text-primary" />
              随机学 10 词
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start gap-2"
              onClick={() => {
                setQuizConfig({ mode: 'en_to_zh', groupId: null, count: 10 })
                setView('quiz')
              }}
            >
              <ClipboardCheck className="h-4 w-4 text-primary" />
              英→中测验
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start gap-2"
              onClick={() => {
                setBrowseFilters({ groupId: 1, letter: null, search: '' })
                setView('browse')
              }}
            >
              <BookOpen className="h-4 w-4 text-primary" />
              高频词 Top 100
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start gap-2"
              onClick={() => setView('spelling')}
            >
              <Keyboard className="h-4 w-4 text-primary" />
              拼写测验 (听写)
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start gap-2"
              onClick={() => setView('review')}
            >
              <RefreshCw className="h-4 w-4 text-primary" />
              智能复习
              {reviewDueCount > 0 && (
                <Badge variant="secondary" className="ml-auto bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300 text-[10px]">
                  {reviewDueCount}
                </Badge>
              )}
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start gap-2"
              onClick={() => setView('cloze')}
            >
              <FileText className="h-4 w-4 text-primary" />
              例句填空
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start gap-2"
              onClick={() => setView('favorites')}
            >
              <Star className="h-4 w-4 text-primary" />
              复习收藏
            </Button>
          </div>
        </Card>
        </div>
      </section>

      {/* Word groups */}
      <section>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-base font-semibold flex items-center gap-2">
            <BookOpen className="h-4 w-4 text-primary" />
            按词频分组学习
          </h2>
          <Button variant="ghost" size="sm" onClick={() => setView('browse')}>
            浏览全部 <ArrowRight className="h-3 w-3 ml-1" />
          </Button>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {loading ? (
            Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-24" />)
          ) : (
            stats?.groups.map((g, idx) => (
              <button
                key={g.id}
                onClick={() => {
                  setBrowseFilters({ groupId: g.id, browseLetter: null, search: '' } as any)
                  setView('browse')
                }}
                className="group text-left animate-fade-in-up"
                style={{ animationDelay: `${idx * 50}ms` }}
              >
                <Card className="relative overflow-hidden p-4 transition-all hover:shadow-md hover:-translate-y-1 hover:border-primary/40">
                  <div
                    className={cn(
                      'absolute right-0 top-0 h-full w-1.5 bg-gradient-to-b',
                      groupColors[g.id] || 'from-muted to-muted-foreground',
                    )}
                  />
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="text-sm font-medium">{g.name}</div>
                      <div className="mt-1 text-2xl font-bold tabular-nums">
                        {g.wordCount.toLocaleString()}
                        <span className="ml-1 text-xs font-normal text-muted-foreground">词</span>
                      </div>
                    </div>
                    <Badge variant="outline" className="text-[10px]">
                      Rank {g.rank}
                    </Badge>
                  </div>
                  <div className="mt-2 text-[11px] text-muted-foreground">
                    出现 {g.minOccur}
                    {g.maxOccur < 99999 ? `~${g.maxOccur}` : '+'} 次 / 词
                  </div>
                </Card>
              </button>
            ))
          )}
        </div>
      </section>

      {/* Featured random words */}
      <section>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-base font-semibold flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-primary" />
            今日推荐
          </h2>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              api.randomWords({ count: 4 }).then((r) => setFeatured(r.words))
            }}
          >
            换一批
          </Button>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {loading
            ? Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-32" />)
            : featured.map((w, idx) => (
                <Card
                  key={w.id}
                  className="p-4 cursor-pointer hover:shadow-md hover:-translate-y-1 hover:border-primary/40 transition-all animate-fade-in-up"
                  style={{ animationDelay: `${idx * 60}ms` }}
                  onClick={() => openWord(w.id)}
                >
                  <div className="flex items-baseline justify-between gap-2">
                    <h3 className="font-semibold truncate">{w.word}</h3>
                    <Badge variant="outline" className="text-[10px] shrink-0">
                      {w.groupName}
                    </Badge>
                  </div>
                  {w.phonetic && (
                    <p className="text-[11px] text-muted-foreground mt-0.5 truncate">
                      {w.phonetic}
                    </p>
                  )}
                  <p className="mt-2 text-xs text-muted-foreground line-clamp-3 leading-relaxed">
                    {w.translation}
                  </p>
                  <div className="mt-2 text-[10px] text-muted-foreground/70">
                    出现 {w.occurrences} 次
                  </div>
                </Card>
              ))}
        </div>
      </section>
    </div>
  )
}

function StatCard({
  icon,
  label,
  value,
  sub,
  accent,
  bgAccent,
}: {
  icon: React.ReactNode
  label: string
  value: string
  sub?: string
  accent: string
  bgAccent: string
}) {
  return (
    <Card className="p-3 sm:p-4 transition-all hover:shadow-md hover:-translate-y-0.5 group">
      <div className="flex items-center gap-3">
        <div className={cn(
          'flex h-9 w-9 sm:h-10 sm:w-10 items-center justify-center rounded-lg transition-transform group-hover:scale-110',
          bgAccent, accent,
        )}>
          {icon}
        </div>
        <div className="min-w-0 flex-1">
          <div className="text-[11px] sm:text-xs text-muted-foreground truncate">{label}</div>
          <div className="text-base sm:text-lg font-bold leading-tight tabular-nums">{value}</div>
          {sub && <div className="text-[10px] text-muted-foreground truncate">{sub}</div>}
        </div>
      </div>
    </Card>
  )
}

function computeStreak(history: Array<{ date: number }>): number {
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
      // today not yet active, allow streak to continue if yesterday was
      continue
    } else {
      break
    }
  }
  return streak
}
