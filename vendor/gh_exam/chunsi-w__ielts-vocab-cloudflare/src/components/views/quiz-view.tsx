'use client'

import { useEffect, useState, useCallback, useRef } from 'react'
import {
  ClipboardCheck,
  Loader2,
  Check,
  X,
  RotateCcw,
  Trophy,
  Volume2,
  ArrowRight,
  Sparkles,
  Timer,
  Zap,
  Gauge,
  Target,
} from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Progress } from '@/components/ui/progress'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { api } from '@/lib/api'
import { useUIStore } from '@/store/ui'
import { useProgressStore } from '@/store/progress'
import { useAudioPlayer } from '@/hooks/use-audio'
import type { QuizQuestion, WordGroup, QuizResponse } from '@/lib/types'
import { cn } from '@/lib/utils'
import { Confetti } from '@/components/confetti'

const modeLabels: Record<string, string> = {
  en_to_zh: '英文 → 中文',
  zh_to_en: '中文 → 英文',
  en_to_sentence: '单词 → 例句',
}

function formatTime(ms: number): string {
  const totalSec = Math.floor(ms / 1000)
  const min = Math.floor(totalSec / 60)
  const sec = totalSec % 60
  return `${String(min).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
}

export function QuizView() {
  const quizMode = useUIStore((s) => s.quizMode)
  const quizGroupId = useUIStore((s) => s.quizGroupId)
  const quizCount = useUIStore((s) => s.quizCount)
  const setQuizConfig = useUIStore((s) => s.setQuizConfig)

  const [groups, setGroups] = useState<WordGroup[]>([])
  const [questions, setQuestions] = useState<QuizQuestion[]>([])
  const [loading, setLoading] = useState(true)
  const [current, setCurrent] = useState(0)
  const [selected, setSelected] = useState<number | null>(null)
  const [revealed, setRevealed] = useState(false)
  const [answers, setAnswers] = useState<Array<{ correct: boolean; selectedIdx: number }>>([])
  const [phase, setPhase] = useState<'config' | 'quiz' | 'result'>('config')
  const [timedMode, setTimedMode] = useState(false)
  const [elapsedMs, setElapsedMs] = useState(0)
  const [difficulty, setDifficulty] = useState<'adaptive' | 'easy' | 'medium' | 'hard'>('adaptive')
  const [focusWrong, setFocusWrong] = useState(false)
  const startTimeRef = useRef<number>(0)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const progress = useProgressStore((s) => s.progress)

  const markCorrect = useProgressStore((s) => s.markCorrect)
  const markWrong = useProgressStore((s) => s.markWrong)
  const recordQuiz = useProgressStore((s) => s.recordQuiz)
  const { play } = useAudioPlayer()

  useEffect(() => {
    api.groups().then(setGroups).catch(console.error)
  }, [])

  const startQuiz = useCallback(async () => {
    setLoading(true)
    setPhase('quiz')
    setCurrent(0)
    setSelected(null)
    setRevealed(false)
    setAnswers([])
    setElapsedMs(0)
    try {
      // Compute focus word IDs (words with wrongCount > correctCount) if focusWrong enabled
      let focusWordIds: number[] | undefined
      if (focusWrong) {
        focusWordIds = Object.entries(progress)
          .filter(([, p]) => p.wrongCount > p.correctCount && p.mastery < 5)
          .map(([id]) => parseInt(id, 10))
          .slice(0, 50)
      }
      const r: QuizResponse = await api.quiz({
        count: quizCount,
        groupId: quizGroupId ?? undefined,
        mode: quizMode,
        difficulty: quizGroupId ? undefined : difficulty,
        focusWordIds,
      })
      setQuestions(r.questions)
      // start timer if timed mode
      if (timedMode) {
        startTimeRef.current = Date.now()
        if (timerRef.current) clearInterval(timerRef.current)
        timerRef.current = setInterval(() => {
          setElapsedMs(Date.now() - startTimeRef.current)
        }, 100)
      }
    } catch (e) {
      console.error(e)
      setPhase('config')
    } finally {
      setLoading(false)
    }
  }, [quizCount, quizGroupId, quizMode, timedMode, difficulty, focusWrong, progress])

  // stop timer when phase changes away from quiz
  useEffect(() => {
    if (phase !== 'quiz' && timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
  }, [phase])

  // cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [])

  const handleSelect = (idx: number) => {
    if (revealed) return
    setSelected(idx)
    setRevealed(true)
    const q = questions[current]
    const correct = idx === q.answerIndex
    setAnswers((prev) => [...prev, { correct, selectedIdx: idx }])
    if (correct) {
      markCorrect(q.wordId)
    } else {
      markWrong(q.wordId)
    }
  }

  const goNext = () => {
    if (current + 1 >= questions.length) {
      // finish
      const correctCount = answers.filter((a) => a.correct).length
      const finalElapsed = timedMode ? Date.now() - startTimeRef.current : undefined
      recordQuiz(questions.length, correctCount, quizMode, finalElapsed)
      setPhase('result')
      return
    }
    setCurrent((c) => c + 1)
    setSelected(null)
    setRevealed(false)
  }

  const correctCount = answers.filter((a) => a.correct).length
  const accuracy = answers.length > 0 ? Math.round((correctCount / answers.length) * 100) : 0

  // Confetti trigger for perfect score
  const [quizConfetti, setQuizConfetti] = useState(0)
  const wasPerfectRef = useRef(false)
  useEffect(() => {
    if (phase === 'result') {
      const correct = answers.filter((a) => a.correct).length
      const total = questions.length
      const pct = total > 0 ? Math.round((correct / total) * 100) : 0
      if (pct === 100 && total >= 5 && !wasPerfectRef.current) {
        wasPerfectRef.current = true
        Promise.resolve().then(() => setQuizConfetti((t) => t + 1))
      }
    } else {
      wasPerfectRef.current = false
    }
  }, [phase, answers, questions.length])

  // CONFIG phase
  if (phase === 'config') {
    return (
      <div className="space-y-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <ClipboardCheck className="h-6 w-6 text-primary" />
            单词测验
          </h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            选择测验模式与范围，开始挑战自己
          </p>
        </div>

        <Card className="p-6 max-w-2xl mx-auto space-y-5">
          <div>
            <label className="text-sm font-medium mb-2 block">测验模式</label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
              {Object.entries(modeLabels).map(([k, label]) => (
                <button
                  key={k}
                  onClick={() => setQuizConfig({ quizMode: k as any })}
                  className={cn(
                    'rounded-lg border-2 p-3 text-left transition-all',
                    quizMode === k
                      ? 'border-primary bg-primary/5'
                      : 'border-border hover:border-primary/40',
                  )}
                >
                  <div className="text-sm font-medium">{label}</div>
                  <div className="text-[11px] text-muted-foreground mt-0.5">
                    {k === 'en_to_zh' && '看英文选中文释义'}
                    {k === 'zh_to_en' && '看中文选英文单词'}
                    {k === 'en_to_sentence' && '看单词选正确例句'}
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="text-sm font-medium mb-2 block">词频范围</label>
            <Select
              value={quizGroupId ? String(quizGroupId) : 'all'}
              onValueChange={(v) => setQuizConfig({ quizGroupId: v === 'all' ? null : parseInt(v, 10) })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">全部分组</SelectItem>
                {groups.map((g) => (
                  <SelectItem key={g.id} value={String(g.id)}>
                    {g.name} ({g.wordCount})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Difficulty selector (only when no specific group selected) */}
          {!quizGroupId && (
            <div>
              <label className="text-sm font-medium mb-2 block">难度</label>
              <div className="grid grid-cols-4 gap-1.5">
                {([
                  { v: 'adaptive', label: '自适应', desc: '混合', color: 'text-primary' },
                  { v: 'easy', label: '简单', desc: '高频', color: 'text-emerald-600 dark:text-emerald-400' },
                  { v: 'medium', label: '中等', desc: '中频', color: 'text-amber-600 dark:text-amber-400' },
                  { v: 'hard', label: '困难', desc: '低频', color: 'text-rose-600 dark:text-rose-400' },
                ] as const).map((opt) => (
                  <button
                    key={opt.v}
                    onClick={() => setDifficulty(opt.v)}
                    className={cn(
                      'rounded-lg border-2 p-2 text-center transition-all',
                      difficulty === opt.v
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:border-primary/40',
                    )}
                  >
                    <div className={cn('text-xs font-medium', difficulty === opt.v ? opt.color : '')}>
                      {opt.label}
                    </div>
                    <div className="text-[9px] text-muted-foreground mt-0.5">{opt.desc}</div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Focus wrong words toggle */}
          {(() => {
            const wrongCount = Object.values(progress).filter((p) => p.wrongCount > p.correctCount && p.mastery < 5).length
            if (wrongCount === 0) return null
            return (
              <div>
                <label className="text-sm font-medium mb-2 block flex items-center gap-1.5">
                  <Target className="h-3.5 w-3.5 text-rose-500" />
                  错题优先
                </label>
                <button
                  onClick={() => setFocusWrong((f) => !f)}
                  className={cn(
                    'w-full rounded-lg border-2 p-3 text-left transition-all flex items-center justify-between gap-3',
                    focusWrong
                      ? 'border-rose-400 bg-rose-50 dark:bg-rose-950/30'
                      : 'border-border hover:border-primary/40',
                  )}
                >
                  <div className="flex items-center gap-2.5">
                    <div className={cn(
                      'flex h-8 w-8 items-center justify-center rounded-lg',
                      focusWrong ? 'bg-rose-500 text-white' : 'bg-muted text-muted-foreground',
                    )}>
                      <Target className="h-4 w-4" />
                    </div>
                    <div>
                      <div className="text-sm font-medium">
                        {focusWrong ? '错题优先已开启' : '错题优先已关闭'}
                      </div>
                      <div className="text-[11px] text-muted-foreground">
                        优先出 {wrongCount} 个答错过的单词
                      </div>
                    </div>
                  </div>
                  <div className={cn(
                    'relative h-6 w-11 rounded-full transition-colors',
                    focusWrong ? 'bg-rose-500' : 'bg-muted',
                  )}>
                    <div className={cn(
                      'absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform',
                      focusWrong ? 'translate-x-5' : 'translate-x-0.5',
                    )} />
                  </div>
                </button>
              </div>
            )
          })()}

          <div>
            <label className="text-sm font-medium mb-2 block">题目数量</label>
            <div className="flex gap-2">
              {[5, 10, 15, 20].map((n) => (
                <Button
                  key={n}
                  variant={quizCount === n ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setQuizConfig({ quizCount: n })}
                  className="flex-1"
                >
                  {n} 题
                </Button>
              ))}
            </div>
          </div>

          {/* Timed mode toggle */}
          <div>
            <label className="text-sm font-medium mb-2 block flex items-center gap-1.5">
              <Timer className="h-3.5 w-3.5 text-primary" />
              计时挑战
            </label>
            <button
              onClick={() => setTimedMode((t) => !t)}
              className={cn(
                'w-full rounded-lg border-2 p-3 text-left transition-all flex items-center justify-between gap-3',
                timedMode
                  ? 'border-amber-400 bg-amber-50 dark:bg-amber-950/30'
                  : 'border-border hover:border-primary/40',
              )}
            >
              <div className="flex items-center gap-2.5">
                <div className={cn(
                  'flex h-8 w-8 items-center justify-center rounded-lg',
                  timedMode ? 'bg-amber-500 text-white' : 'bg-muted text-muted-foreground',
                )}>
                  <Zap className="h-4 w-4" />
                </div>
                <div>
                  <div className="text-sm font-medium">
                    {timedMode ? '计时模式已开启' : '计时模式已关闭'}
                  </div>
                  <div className="text-[11px] text-muted-foreground">
                    {timedMode ? '记录答题总时长，挑战速度极限' : '开启后记录答题速度'}
                  </div>
                </div>
              </div>
              <div className={cn(
                'relative h-6 w-11 rounded-full transition-colors',
                timedMode ? 'bg-amber-500' : 'bg-muted',
              )}>
                <div className={cn(
                  'absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform',
                  timedMode ? 'translate-x-5' : 'translate-x-0.5',
                )} />
              </div>
            </button>
          </div>

          <Button size="lg" className="w-full" onClick={startQuiz}>
            <Sparkles className="h-4 w-4 mr-2" />
            {timedMode ? '开始计时挑战' : '开始测验'}
          </Button>
        </Card>
      </div>
    )
  }

  // RESULT phase
  if (phase === 'result') {
    const correct = answers.filter((a) => a.correct).length
    const total = questions.length
    const pct = total > 0 ? Math.round((correct / total) * 100) : 0
    const grade = pct >= 90 ? 'S' : pct >= 80 ? 'A' : pct >= 70 ? 'B' : pct >= 60 ? 'C' : 'D'
    const gradeColor =
      pct >= 90
        ? 'from-amber-400 to-yellow-500'
        : pct >= 80
          ? 'from-emerald-400 to-teal-500'
          : pct >= 70
            ? 'from-sky-400 to-cyan-500'
            : pct >= 60
              ? 'from-orange-400 to-amber-500'
              : 'from-rose-400 to-red-500'

    return (
      <div className="space-y-4">
        <Confetti trigger={quizConfetti} duration={4000} count={120} />
        <Card className="p-8 max-w-2xl mx-auto text-center">
          <div className={cn('inline-flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br text-white text-5xl font-bold shadow-lg mb-4', gradeColor)}>
            {grade}
          </div>
          <h2 className="text-2xl font-bold">
            {pct >= 90 ? '完美！' : pct >= 80 ? '优秀！' : pct >= 70 ? '不错！' : pct >= 60 ? '继续加油！' : '需要复习'}
          </h2>
          <p className="text-muted-foreground mt-1">
            本次测验: {correct} / {total} 正确
          </p>

          <div className="mt-6 grid grid-cols-3 gap-3">
            <div className="rounded-lg bg-emerald-50 dark:bg-emerald-950/30 p-3">
              <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{correct}</div>
              <div className="text-[11px] text-muted-foreground">答对</div>
            </div>
            <div className="rounded-lg bg-rose-50 dark:bg-rose-950/30 p-3">
              <div className="text-2xl font-bold text-rose-600 dark:text-rose-400">{total - correct}</div>
              <div className="text-[11px] text-muted-foreground">答错</div>
            </div>
            <div className="rounded-lg bg-amber-50 dark:bg-amber-950/30 p-3">
              <div className="text-2xl font-bold text-amber-600 dark:text-amber-400">{pct}%</div>
              <div className="text-[11px] text-muted-foreground">正确率</div>
            </div>
          </div>

          {/* Timed mode stats */}
          {timedMode && total > 0 && (
            <div className="mt-3 rounded-lg bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-950/30 dark:to-orange-950/30 p-3 flex items-center justify-around gap-3 border border-amber-200 dark:border-amber-900">
              <div className="text-center">
                <div className="flex items-center gap-1 justify-center text-amber-600 dark:text-amber-400">
                  <Timer className="h-4 w-4" />
                  <span className="text-lg font-bold font-mono tabular-nums">{formatTime(elapsedMs)}</span>
                </div>
                <div className="text-[10px] text-muted-foreground mt-0.5">总用时</div>
              </div>
              <div className="h-8 w-px bg-amber-200 dark:bg-amber-900" />
              <div className="text-center">
                <div className="flex items-center gap-1 justify-center text-amber-600 dark:text-amber-400">
                  <Gauge className="h-4 w-4" />
                  <span className="text-lg font-bold font-mono tabular-nums">
                    {(elapsedMs / 1000 / total).toFixed(1)}s
                  </span>
                </div>
                <div className="text-[10px] text-muted-foreground mt-0.5">平均每题</div>
              </div>
            </div>
          )}

          <div className="mt-6 flex gap-2">
            <Button variant="outline" className="flex-1" onClick={() => setPhase('config')}>
              重新配置
            </Button>
            <Button className="flex-1" onClick={startQuiz}>
              <RotateCcw className="h-4 w-4 mr-1" />
              再来一局
            </Button>
          </div>
        </Card>

        {/* Question review */}
        <Card className="p-4 max-w-2xl mx-auto">
          <h3 className="text-sm font-semibold mb-3">题目回顾</h3>
          <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
            {questions.map((q, i) => {
              const ans = answers[i]
              return (
                <div key={i} className="rounded-lg border p-2.5 text-xs">
                  <div className="flex items-start gap-2">
                    <span className={cn(
                      'shrink-0 flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-bold',
                      ans?.correct ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300' : 'bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300',
                    )}>
                      {ans?.correct ? <Check className="h-3 w-3" /> : <X className="h-3 w-3" />}
                    </span>
                    <div className="min-w-0 flex-1">
                      <div className="font-medium">{q.prompt}</div>
                      <div className="text-muted-foreground mt-0.5">
                        正确: {q.options[q.answerIndex]}
                      </div>
                      {!ans?.correct && (
                        <div className="text-rose-600 dark:text-rose-400 mt-0.5">
                          你选: {q.options[ans?.selectedIdx ?? -1] || '未作答'}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </Card>
      </div>
    )
  }

  // QUIZ phase
  const q = questions[current]
  const progressPct = questions.length > 0 ? ((current + (revealed ? 1 : 0)) / questions.length) * 100 : 0

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <ClipboardCheck className="h-6 w-6 text-primary" />
            测验中
          </h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            {modeLabels[quizMode]} · 第 {current + 1} / {questions.length} 题
            {!quizGroupId && difficulty !== 'adaptive' && (
              <span className="ml-1">· {
                difficulty === 'easy' ? '简单' :
                difficulty === 'medium' ? '中等' : '困难'
              }</span>
            )}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {timedMode && (
            <Badge
              variant="outline"
              className={cn(
                'gap-1 font-mono tabular-nums',
                elapsedMs > 60000 ? 'text-rose-600 dark:text-rose-400 border-rose-300' : 'text-amber-600 dark:text-amber-400 border-amber-300',
              )}
            >
              <Timer className="h-3 w-3" />
              {formatTime(elapsedMs)}
            </Badge>
          )}
          <Badge variant="outline" className="gap-1">
            <Check className="h-3 w-3 text-emerald-500" />
            {correctCount}
          </Badge>
          <Badge variant="outline" className="gap-1">
            <X className="h-3 w-3 text-rose-500" />
            {answers.length - correctCount}
          </Badge>
          <Badge variant="secondary">{accuracy}%</Badge>
        </div>
      </div>

      <Progress value={progressPct} className="h-1.5" />

      {loading ? (
        <Skeleton className="h-96 w-full" />
      ) : !q ? (
        <Card className="p-10 text-center">
          <p className="text-muted-foreground">无法生成题目，请尝试其他设置</p>
          <Button className="mt-3" onClick={() => setPhase('config')}>返回配置</Button>
        </Card>
      ) : (
        <Card className="p-6 sm:p-8">
          {/* Prompt */}
          <div className="text-center mb-6">
            <div className="text-[11px] text-muted-foreground mb-2 uppercase tracking-wide">
              {modeLabels[q.mode]}
            </div>
            <div className="text-3xl sm:text-4xl font-bold tracking-tight">
              {q.prompt}
            </div>
            {q.promptTranslation && (
              <div className="mt-2 text-sm text-muted-foreground font-mono">
                {q.promptTranslation}
              </div>
            )}
            {/* For en_to_zh, play audio (if URL available - we don't have URL in quiz, so skip) */}
          </div>

          {/* Options */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {q.options.map((opt, idx) => {
              const isSelected = selected === idx
              const isAnswer = idx === q.answerIndex
              const showCorrect = revealed && isAnswer
              const showWrong = revealed && isSelected && !isAnswer
              return (
                <button
                  key={idx}
                  onClick={() => handleSelect(idx)}
                  disabled={revealed}
                  style={{ animationDelay: `${idx * 50}ms` }}
                  className={cn(
                    'relative text-left rounded-lg border-2 p-3.5 transition-all animate-fade-in-up',
                    'hover:border-primary/60 hover:bg-muted/40',
                    !revealed && 'cursor-pointer',
                    showCorrect && 'border-emerald-500 bg-emerald-50 dark:bg-emerald-950/40',
                    showWrong && 'border-rose-500 bg-rose-50 dark:bg-rose-950/40',
                    revealed && !showCorrect && !showWrong && 'opacity-50',
                  )}
                >
                  <div className="flex items-start gap-2.5">
                    <span className={cn(
                      'shrink-0 flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold',
                      showCorrect
                        ? 'bg-emerald-500 text-white'
                        : showWrong
                          ? 'bg-rose-500 text-white'
                          : 'bg-muted text-muted-foreground',
                    )}>
                      {showCorrect ? <Check className="h-3.5 w-3.5" /> : showWrong ? <X className="h-3.5 w-3.5" /> : String.fromCharCode(65 + idx)}
                    </span>
                    <span className="text-sm leading-relaxed flex-1">{opt}</span>
                  </div>
                </button>
              )
            })}
          </div>

          {/* Explanation after reveal */}
          {revealed && (
            <div className="mt-5 rounded-lg bg-muted/50 p-4 border">
              <div className="flex items-center gap-2 mb-2">
                {selected === q.answerIndex ? (
                  <Badge className="bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
                    <Check className="h-3 w-3 mr-1" /> 回答正确
                  </Badge>
                ) : (
                  <Badge className="bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300">
                    <X className="h-3 w-3 mr-1" /> 回答错误
                  </Badge>
                )}
              </div>
              <div className="space-y-1.5 text-sm">
                <div>
                  <span className="font-semibold">{q.explanation.word}</span>
                  {q.explanation.phonetic && (
                    <span className="ml-2 text-xs text-muted-foreground font-mono">
                      {q.explanation.phonetic}
                    </span>
                  )}
                </div>
                <div className="text-muted-foreground whitespace-pre-line">
                  {q.explanation.translation}
                </div>
                {q.explanation.exampleEn && (
                  <div className="text-xs italic text-muted-foreground/80 mt-2">
                    {q.explanation.exampleEn}
                  </div>
                )}
                {q.explanation.exampleZh && (
                  <div className="text-xs text-muted-foreground/60">
                    {q.explanation.exampleZh}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Next button */}
          {revealed && (
            <Button className="w-full mt-4" size="lg" onClick={goNext}>
              {current + 1 >= questions.length ? (
                <>
                  <Trophy className="h-4 w-4 mr-2" />
                  查看结果
                </>
              ) : (
                <>
                  下一题
                  <ArrowRight className="h-4 w-4 ml-2" />
                </>
              )}
            </Button>
          )}
        </Card>
      )}
    </div>
  )
}
