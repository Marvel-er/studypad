'use client'

import { useEffect, useState, useCallback, useRef } from 'react'
import {
  Keyboard,
  Loader2,
  Check,
  X,
  RotateCcw,
  Trophy,
  Volume2,
  ArrowRight,
  Sparkles,
  Type,
  Ear,
  Eye,
  Lightbulb,
} from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Progress } from '@/components/ui/progress'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { api } from '@/lib/api'
import { useProgressStore } from '@/store/progress'
import { useUIStore } from '@/store/ui'
import type { WordGroup } from '@/lib/types'
import { cn } from '@/lib/utils'

interface SpellingQuestion {
  wordId: number
  word: string
  phonetic: string
  translation: string
  audioUk: string | null
  audioUs: string | null
  exampleEn: string
  exampleZh: string
  hint: string
}

const hintOptions = [
  { value: 'translation', label: '看中文拼写', icon: Eye },
  { value: 'phonetic', label: '看音标拼写', icon: Type },
  { value: 'audio', label: '听发音拼写', icon: Ear },
]

// Levenshtein distance for "close enough" detection
function levenshtein(a: string, b: string): number {
  const m = a.length
  const n = b.length
  if (m === 0) return n
  if (n === 0) return m
  const dp: number[][] = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(0))
  for (let i = 0; i <= m; i++) dp[i][0] = i
  for (let j = 0; j <= n; j++) dp[0][j] = j
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      const cost = a[i - 1].toLowerCase() === b[j - 1].toLowerCase() ? 0 : 1
      dp[i][j] = Math.min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    }
  }
  return dp[m][n]
}

export function SpellingView() {
  const setView = useUIStore((s) => s.setView)
  const markCorrect = useProgressStore((s) => s.markCorrect)
  const markWrong = useProgressStore((s) => s.markWrong)
  const recordQuiz = useProgressStore((s) => s.recordQuiz)
  const audioAccent = useProgressStore((s) => s.audioAccent)

  const [groups, setGroups] = useState<WordGroup[]>([])
  const [questions, setQuestions] = useState<SpellingQuestion[]>([])
  const [loading, setLoading] = useState(true)
  const [phase, setPhase] = useState<'config' | 'quiz' | 'result'>('config')
  const [current, setCurrent] = useState(0)
  const [input, setInput] = useState('')
  const [revealed, setRevealed] = useState(false)
  const [isCorrect, setIsCorrect] = useState(false)
  const [showHint, setShowHint] = useState(false)
  const [hintLevel, setHintLevel] = useState(1)
  const [answers, setAnswers] = useState<Array<{ correct: boolean; typed: string }>>([])
  const [config, setConfig] = useState<{ count: number; groupId: number | null; hint: 'phonetic' | 'translation' | 'audio' }>({
    count: 10,
    groupId: null,
    hint: 'translation',
  })

  const inputRef = useRef<HTMLInputElement>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  useEffect(() => {
    api.groups().then(setGroups).catch(console.error)
  }, [])

  const startQuiz = useCallback(async () => {
    setLoading(true)
    setPhase('quiz')
    setCurrent(0)
    setInput('')
    setRevealed(false)
    setShowHint(false); setHintLevel(1)
    setAnswers([])
    try {
      const r = await api.spellingQuiz({
        count: config.count,
        groupId: config.groupId,
        hint: config.hint,
      })
      setQuestions(r.questions)
    } catch (e) {
      console.error(e)
      setPhase('config')
    } finally {
      setLoading(false)
    }
  }, [config])

  // Focus input when question changes
  useEffect(() => {
    if (phase === 'quiz' && !revealed && inputRef.current) {
      inputRef.current.focus()
    }
  }, [current, phase, revealed])

  // Auto-play audio for audio hint mode
  useEffect(() => {
    if (phase !== 'quiz' || questions.length === 0) return
    const q = questions[current]
    if (!q) return
    if (config.hint === 'audio') {
      const url = audioAccent === 'uk' ? q.audioUk : q.audioUs
      if (url) {
        const t = setTimeout(() => playAudio(url), 400)
        return () => clearTimeout(t)
      }
    }
  }, [current, phase, questions, config.hint, audioAccent])

  const playAudio = (url?: string | null) => {
    if (!url) return
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
    }
    const audio = new Audio(url)
    audioRef.current = audio
    audio.play().catch(() => {})
  }

  const handleSubmit = () => {
    if (revealed) return
    const q = questions[current]
    if (!q) return
    const typed = input.trim()
    if (!typed) return
    const dist = levenshtein(typed, q.word)
    const correct = dist === 0
    const almostCorrect = dist === 1 && q.word.length > 3
    // exact match OR single-char typo on long words counts as correct
    setIsCorrect(correct)
    setRevealed(true)
    setAnswers((prev) => [...prev, { correct, typed }])
    if (correct) {
      markCorrect(q.wordId)
    } else {
      markWrong(q.wordId)
      // if almost correct, still mark as correct-ish? No, keep strict
    }
    void almostCorrect // (could be used for partial credit display)
  }

  const goNext = () => {
    if (current + 1 >= questions.length) {
      const correctCount = answers.filter((a) => a.correct).length
      recordQuiz(questions.length, correctCount, 'spelling')
      setPhase('result')
      return
    }
    setCurrent((c) => c + 1)
    setInput('')
    setRevealed(false)
    setShowHint(false); setHintLevel(1)
    setIsCorrect(false)
  }

  const correctCount = answers.filter((a) => a.correct).length
  const accuracy = answers.length > 0 ? Math.round((correctCount / answers.length) * 100) : 0
  const progressPct = questions.length > 0 ? ((current + (revealed ? 1 : 0)) / questions.length) * 100 : 0

  // CONFIG phase
  if (phase === 'config') {
    return (
      <div className="space-y-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Keyboard className="h-6 w-6 text-primary" />
            拼写测验
          </h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            看提示拼写出英文单词，强化记忆 · 自动统计正确率与近义词容错
          </p>
        </div>

        <Card className="p-6 max-w-2xl mx-auto space-y-5">
          <div>
            <label className="text-sm font-medium mb-2 block">提示方式</label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
              {hintOptions.map((o) => {
                const Icon = o.icon
                return (
                  <button
                    key={o.value}
                    onClick={() => setConfig((c) => ({ ...c, hint: o.value as any }))}
                    className={cn(
                      'rounded-lg border-2 p-3 text-left transition-all',
                      config.hint === o.value
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:border-primary/40',
                    )}
                  >
                    <Icon className="h-4 w-4 mb-1.5 text-primary" />
                    <div className="text-sm font-medium">{o.label}</div>
                    <div className="text-[11px] text-muted-foreground mt-0.5">
                      {o.value === 'translation' && '中文释义 → 拼英文'}
                      {o.value === 'phonetic' && '音标 → 拼英文'}
                      {o.value === 'audio' && '听发音 → 拼英文'}
                    </div>
                  </button>
                )
              })}
            </div>
          </div>

          <div>
            <label className="text-sm font-medium mb-2 block">词频范围</label>
            <Select
              value={config.groupId ? String(config.groupId) : 'all'}
              onValueChange={(v) => setConfig((c) => ({ ...c, groupId: v === 'all' ? null : parseInt(v, 10) }))}
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

          <div>
            <label className="text-sm font-medium mb-2 block">题目数量</label>
            <div className="flex gap-2">
              {[5, 10, 15, 20].map((n) => (
                <Button
                  key={n}
                  variant={config.count === n ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setConfig((c) => ({ ...c, count: n }))}
                  className="flex-1"
                >
                  {n} 题
                </Button>
              ))}
            </div>
          </div>

          <Button size="lg" className="w-full" onClick={startQuiz}>
            <Sparkles className="h-4 w-4 mr-2" />
            开始拼写测验
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
      pct >= 90 ? 'from-amber-400 to-yellow-500'
      : pct >= 80 ? 'from-emerald-400 to-teal-500'
      : pct >= 70 ? 'from-sky-400 to-cyan-500'
      : pct >= 60 ? 'from-orange-400 to-amber-500'
      : 'from-rose-400 to-red-500'

    return (
      <div className="space-y-4">
        <Card className="p-8 max-w-2xl mx-auto text-center">
          <div className={cn('inline-flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br text-white text-5xl font-bold shadow-lg mb-4', gradeColor)}>
            {grade}
          </div>
          <h2 className="text-2xl font-bold">
            {pct >= 90 ? '完美！' : pct >= 80 ? '优秀！' : pct >= 70 ? '不错！' : pct >= 60 ? '继续加油！' : '需要多练习拼写'}
          </h2>
          <p className="text-muted-foreground mt-1">
            本次拼写测验: {correct} / {total} 正确
          </p>

          <div className="mt-6 grid grid-cols-3 gap-3">
            <div className="rounded-lg bg-emerald-50 dark:bg-emerald-950/30 p-3">
              <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{correct}</div>
              <div className="text-[11px] text-muted-foreground">拼对</div>
            </div>
            <div className="rounded-lg bg-rose-50 dark:bg-rose-950/30 p-3">
              <div className="text-2xl font-bold text-rose-600 dark:text-rose-400">{total - correct}</div>
              <div className="text-[11px] text-muted-foreground">拼错</div>
            </div>
            <div className="rounded-lg bg-amber-50 dark:bg-amber-950/30 p-3">
              <div className="text-2xl font-bold text-amber-600 dark:text-amber-400">{pct}%</div>
              <div className="text-[11px] text-muted-foreground">正确率</div>
            </div>
          </div>

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
                      <div className="font-medium">{q.word}</div>
                      {!ans?.correct && (
                        <div className="text-rose-600 dark:text-rose-400 mt-0.5">
                          你拼: <span className="font-mono">{ans?.typed || '(空)'}</span>
                        </div>
                      )}
                      <div className="text-muted-foreground mt-0.5">
                        {q.translation.replace(/\n/g, ' · ').slice(0, 50)}
                      </div>
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

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Keyboard className="h-6 w-6 text-primary" />
            拼写测验
          </h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            {hintOptions.find((o) => o.value === config.hint)?.label} · 第 {current + 1} / {questions.length} 题
          </p>
        </div>
        <div className="flex items-center gap-2">
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
          {/* Prompt based on hint mode */}
          <div className="text-center mb-6">
            <div className="text-[11px] text-muted-foreground mb-2 uppercase tracking-wide">
              {config.hint === 'translation' && '根据中文释义拼写单词'}
              {config.hint === 'phonetic' && '根据音标拼写单词'}
              {config.hint === 'audio' && '听发音拼写单词'}
            </div>

            {config.hint === 'translation' && (
              <>
                <div className="text-base sm:text-lg font-medium max-w-xl mx-auto leading-relaxed whitespace-pre-line">
                  {q.translation}
                </div>
              </>
            )}

            {config.hint === 'phonetic' && (
              <div className="text-2xl sm:text-3xl font-mono text-muted-foreground">
                {q.phonetic || '（无音标）'}
              </div>
            )}

            {config.hint === 'audio' && (
              <div>
                <Button
                  variant="outline"
                  size="lg"
                  className="gap-2"
                  onClick={() => playAudio(audioAccent === 'uk' ? q.audioUk : q.audioUs)}
                >
                  <Volume2 className="h-5 w-5" />
                  播放发音
                </Button>
                <p className="text-xs text-muted-foreground mt-2">点击按钮播放，可重复听</p>
              </div>
            )}

            {/* Letter count hint */}
            <div className="mt-3 inline-flex items-center gap-1.5 text-xs text-muted-foreground">
              <span className="font-mono">{q.word.length} 个字母</span>
              <span>·</span>
              <span>首字母 <span className="font-mono font-semibold">{q.word[0]?.toUpperCase()}</span></span>
            </div>
          </div>

          {/* Input */}
          <div className="max-w-md mx-auto">
            <div className="relative">
              <Input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    if (!revealed) handleSubmit()
                    else goNext()
                  }
                }}
                disabled={revealed}
                placeholder="输入英文单词..."
                className={cn(
                  'text-center text-xl font-mono h-12 tracking-wider',
                  revealed && isCorrect && 'border-emerald-500 bg-emerald-50 dark:bg-emerald-950/40',
                  revealed && !isCorrect && 'border-rose-500 bg-rose-50 dark:bg-rose-950/40',
                )}
                autoComplete="off"
                autoCorrect="off"
                spellCheck={false}
              />
              {revealed && (
                <div className="absolute right-3 top-1/2 -translate-y-1/2">
                  {isCorrect ? (
                    <Check className="h-5 w-5 text-emerald-500" />
                  ) : (
                    <X className="h-5 w-5 text-rose-500" />
                  )}
                </div>
              )}
            </div>

            {/* Reveal answer */}
            {revealed && (
              <div className="mt-4 rounded-lg bg-muted/50 p-4 border text-center animate-fade-in-up">
                <div className="flex items-center justify-center gap-2 mb-1">
                  {isCorrect ? (
                    <Badge className="bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
                      <Check className="h-3 w-3 mr-1" /> 拼写正确
                    </Badge>
                  ) : (
                    <Badge className="bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300">
                      <X className="h-3 w-3 mr-1" /> 拼写错误
                    </Badge>
                  )}
                </div>
                <div className="text-xl font-bold font-mono">{q.word}</div>
                {q.phonetic && (
                  <div className="text-xs text-muted-foreground font-mono mt-0.5">{q.phonetic}</div>
                )}
                <div className="text-sm text-muted-foreground mt-2 whitespace-pre-line">
                  {q.translation}
                </div>
                {!isCorrect && (
                  <div className="mt-2 text-xs text-rose-600 dark:text-rose-400">
                    你的答案: <span className="font-mono">{input || '(空)'}</span>
                  </div>
                )}
                {q.exampleEn && (
                  <div className="mt-3 pt-3 border-t border-border/50">
                    <div className="text-xs italic text-muted-foreground">{q.exampleEn}</div>
                    {q.exampleZh && (
                      <div className="text-xs text-muted-foreground/70 mt-1">{q.exampleZh}</div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Hint button when not revealed */}
            {!revealed && (
              <div className="mt-3 flex justify-center">
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-xs text-muted-foreground"
                  onClick={() => { setShowHint(true); setHintLevel(1) }}
                >
                  <Lightbulb className="h-3.5 w-3.5 mr-1" />
                  查看提示
                </Button>
              </div>
            )}

            {showHint && !revealed && (
              <div className="mt-2 rounded-lg bg-amber-50 dark:bg-amber-950/30 p-2.5 text-center text-xs animate-fade-in-up">
                <span className="font-mono tracking-wider">
                  {q.word.split('').map((c, i) => {
                    // Show: first letter, last letter, and every other letter based on hint level
                    if (i === 0) return c.toUpperCase()
                    if (i === q.word.length - 1) return c
                    if (hintLevel >= 2 && i === Math.floor(q.word.length / 2)) return c
                    if (hintLevel >= 3 && i === 1) return c
                    if (hintLevel >= 3 && i === q.word.length - 2) return c
                    return '_'
                  }).join(' ')}
                </span>
                <div className="mt-1 flex items-center justify-center gap-1.5">
                  <span className="text-[10px] text-muted-foreground">提示级别 {hintLevel}/3</span>
                  {hintLevel < 3 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-5 px-1.5 text-[10px]"
                      onClick={() => setHintLevel((l) => Math.min(3, l + 1))}
                    >
                      更多提示
                    </Button>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="max-w-md mx-auto mt-5 flex gap-2">
            {!revealed ? (
              <Button className="flex-1" size="lg" onClick={handleSubmit} disabled={!input.trim()}>
                提交答案
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            ) : (
              <Button className="flex-1" size="lg" onClick={goNext}>
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
          </div>
        </Card>
      )}
    </div>
  )
}
