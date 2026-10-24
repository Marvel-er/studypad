'use client'

import { useEffect, useState, useCallback, useRef, useMemo } from 'react'
import {
  GraduationCap,
  ChevronLeft,
  ChevronRight,
  RotateCcw,
  Volume2,
  Check,
  X,
  Sparkles,
  Settings,
  Star,
  Brain,
} from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Progress } from '@/components/ui/progress'
import { api } from '@/lib/api'
import { useUIStore } from '@/store/ui'
import { useProgressStore } from '@/store/progress'
import { useAudioPlayer } from '@/hooks/use-audio'
import type { WordListItem, WordGroup } from '@/lib/types'
import { cn } from '@/lib/utils'

const STUDY_BATCH = 10

export function StudyView() {
  const studyGroupId = useUIStore((s) => s.studyGroupId)
  const setStudyGroup = useUIStore((s) => s.setStudyGroup)
  const openWord = useUIStore((s) => s.openWord)
  const audioAccent = useProgressStore((s) => s.audioAccent)
  const autoPlayAudio = useProgressStore((s) => s.autoPlayAudio)

  const [groups, setGroups] = useState<WordGroup[]>([])
  const [words, setWords] = useState<WordListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [current, setCurrent] = useState(0)
  const [flipped, setFlipped] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [animating, setAnimating] = useState(false)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  const markStudied = useProgressStore((s) => s.markStudied)
  const setMastery = useProgressStore((s) => s.setMastery)
  const toggleFavorite = useProgressStore((s) => s.toggleFavorite)
  const toggleLearned = useProgressStore((s) => s.toggleLearned)
  const recordStudy = useProgressStore((s) => s.recordStudy)
  // subscribe to whole progress object (stable reference unless changed)
  const progress = useProgressStore((s) => s.progress)
  // derive favorite/learned maps with useMemo to avoid new object every render
  const favoriteMap = useMemo(() => {
    const m: Record<number, boolean> = {}
    for (const w of words) m[w.id] = progress[w.id]?.favorite ?? false
    return m
  }, [progress, words])
  const learnedMap = useMemo(() => {
    const m: Record<number, boolean> = {}
    for (const w of words) m[w.id] = progress[w.id]?.learned ?? false
    return m
  }, [progress, words])

  const loadWords = useCallback(async () => {
    setLoading(true)
    setFlipped(false)
    setCurrent(0)
    try {
      const r = await api.randomWords({
        count: STUDY_BATCH,
        groupId: studyGroupId ?? undefined,
      })
      setWords(r.words)
      recordStudy(r.words.length)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }, [studyGroupId, recordStudy])

  useEffect(() => {
    api.groups().then(setGroups).catch(console.error)
  }, [])

  useEffect(() => {
    loadWords()
  }, [loadWords])

  const playAudio = useCallback(
    (url?: string | null) => {
      if (!url) return
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current.currentTime = 0
      }
      const audio = new Audio(url)
      audioRef.current = audio
      audio.play().catch(() => {})
    },
    [],
  )

  // Auto-play audio on word change
  useEffect(() => {
    if (!autoPlayAudio || words.length === 0) return
    const w = words[current]
    if (!w) return
    const url = audioAccent === 'uk' ? w.audioUk : w.audioUs
    if (url) {
      const t = setTimeout(() => playAudio(url), 300)
      return () => clearTimeout(t)
    }
  }, [current, words, autoPlayAudio, audioAccent, playAudio])

  const goNext = useCallback(() => {
    setAnimating(true)
    setFlipped(false)
    setTimeout(() => {
      setCurrent((c) => Math.min(words.length - 1, c + 1))
      setAnimating(false)
    }, 200)
  }, [words.length])

  const goPrev = useCallback(() => {
    setAnimating(true)
    setFlipped(false)
    setTimeout(() => {
      setCurrent((c) => Math.max(0, c - 1))
      setAnimating(false)
    }, 200)
  }, [])

  const handleFlip = useCallback(() => {
    setFlipped((f) => {
      if (!f) {
        // marking as studied when first flipped
        const w = words[current]
        if (w) markStudied(w.id)
      }
      return !f
    })
  }, [current, words, markStudied])

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === ' ' || e.key === 'Enter') {
        e.preventDefault()
        handleFlip()
      } else if (e.key === 'ArrowRight') {
        e.preventDefault()
        goNext()
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault()
        goPrev()
      } else if (e.key === '1') {
        // mark as unknown
        const w = words[current]
        if (w) {
          setMastery(w.id, 1)
          goNext()
        }
      } else if (e.key === '2') {
        // mark as familiar
        const w = words[current]
        if (w) {
          setMastery(w.id, 3)
          goNext()
        }
      } else if (e.key === '3') {
        // mark as known
        const w = words[current]
        if (w) {
          setMastery(w.id, 5)
          goNext()
        }
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [current, words, handleFlip, goNext, goPrev, setMastery])

  const word = words[current]
  const progressPct = words.length > 0 ? ((current + 1) / words.length) * 100 : 0

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <GraduationCap className="h-6 w-6 text-primary" />
            单词学习
          </h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            翻卡查看释义 · 空格/Enter 翻转 · ←/→ 切换 · 1/2/3 评级
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Select
            value={studyGroupId ? String(studyGroupId) : 'all'}
            onValueChange={(v) => setStudyGroup(v === 'all' ? null : parseInt(v, 10))}
          >
            <SelectTrigger className="h-9 w-[160px]">
              <SelectValue placeholder="选择分组" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部分组</SelectItem>
              {groups.map((g) => (
                <SelectItem key={g.id} value={String(g.id)}>
                  {g.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button variant="outline" size="sm" onClick={() => setShowSettings((s) => !s)}>
            <Settings className="h-4 w-4" />
          </Button>
          <Button variant="default" size="sm" onClick={loadWords}>
            <RotateCcw className="h-4 w-4 mr-1" />
            换一批
          </Button>
        </div>
      </div>

      {/* Settings panel */}
      {showSettings && (
        <Card className="p-4">
          <div className="flex items-center gap-6 flex-wrap">
            <div className="flex items-center gap-2">
              <span className="text-sm">发音口音:</span>
              <div className="flex gap-1">
                <Button
                  size="sm"
                  variant={audioAccent === 'uk' ? 'default' : 'outline'}
                  onClick={() => useProgressStore.getState().setAudioAccent('uk')}
                >
                  英式 UK
                </Button>
                <Button
                  size="sm"
                  variant={audioAccent === 'us' ? 'default' : 'outline'}
                  onClick={() => useProgressStore.getState().setAudioAccent('us')}
                >
                  美式 US
                </Button>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm">自动播放:</span>
              <Button
                size="sm"
                variant={autoPlayAudio ? 'default' : 'outline'}
                onClick={() => useProgressStore.getState().setAutoPlayAudio(!autoPlayAudio)}
              >
                {autoPlayAudio ? '已开启' : '已关闭'}
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Progress bar */}
      <div>
        <div className="flex justify-between text-xs text-muted-foreground mb-1.5">
          <span>进度 {current + 1} / {words.length}</span>
          <span>{Math.round(progressPct)}%</span>
        </div>
        <Progress value={progressPct} className="h-1.5" />
      </div>

      {/* Flashcard */}
      {loading ? (
        <Skeleton className="h-[420px] w-full" />
      ) : !word ? (
        <Card className="p-10 text-center">
          <p className="text-muted-foreground">暂无单词</p>
        </Card>
      ) : (
        <div className="space-y-3">
          <Card
            className={cn(
              'relative min-h-[420px] cursor-pointer overflow-hidden transition-all duration-300',
              animating && 'opacity-0 translate-x-4',
            )}
            onClick={handleFlip}
          >
            {/* Front: English word */}
            {!flipped && (
              <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center">
                <div className="absolute top-4 left-4">
                  <Badge variant="secondary" className="text-[10px]">
                    {word.groupName}
                  </Badge>
                </div>
                <div className="absolute top-4 right-4 flex items-center gap-1">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7"
                    onClick={(e) => {
                      e.stopPropagation()
                      toggleFavorite(word.id)
                    }}
                  >
                    <Star className={cn('h-4 w-4', favoriteMap[word.id] && 'fill-amber-400 text-amber-400')} />
                  </Button>
                </div>

                <h2 className="text-4xl sm:text-5xl font-bold tracking-tight">
                  {word.word}
                </h2>
                {word.phonetic && (
                  <p className="mt-3 text-base text-muted-foreground font-mono">
                    {word.phonetic}
                  </p>
                )}

                <div className="mt-5 flex items-center gap-2">
                  {word.audioUk && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        playAudio(word.audioUk)
                      }}
                    >
                      <Volume2 className="h-3.5 w-3.5 mr-1" />
                      UK
                    </Button>
                  )}
                  {word.audioUs && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        playAudio(word.audioUs)
                      }}
                    >
                      <Volume2 className="h-3.5 w-3.5 mr-1" />
                      US
                    </Button>
                  )}
                </div>

                <p className="mt-8 text-xs text-muted-foreground animate-pulse">
                  点击卡片或按 空格 查看释义
                </p>
                <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-[10px] text-muted-foreground/60">
                  出现 {word.occurrences} 次 · {word.sentenceCount} 例句
                </div>
              </div>
            )}

            {/* Back: Translation & details */}
            {flipped && (
              <div className="absolute inset-0 overflow-y-auto p-5 sm:p-6">
                <div className="flex items-start justify-between gap-2 mb-3">
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <h2 className="text-2xl font-bold">{word.word}</h2>
                      <Badge variant="secondary" className="text-[10px]">
                        {word.groupName}
                      </Badge>
                      {learnedMap[word.id] && (
                        <Badge variant="secondary" className="text-[10px] bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
                          已掌握
                        </Badge>
                      )}
                    </div>
                    {word.phonetic && (
                      <p className="text-xs text-muted-foreground font-mono mt-0.5">
                        {word.phonetic}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-1 shrink-0">
                    {word.audioUs && (
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7"
                        onClick={(e) => {
                          e.stopPropagation()
                          playAudio(word.audioUs)
                        }}
                      >
                        <Volume2 className="h-4 w-4" />
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7"
                      onClick={(e) => {
                        e.stopPropagation()
                        toggleFavorite(word.id)
                      }}
                    >
                      <Star className={cn('h-4 w-4', favoriteMap[word.id] && 'fill-amber-400 text-amber-400')} />
                    </Button>
                  </div>
                </div>

                {/* Translation */}
                <div className="rounded-lg bg-rose-50 dark:bg-rose-950/30 p-3 mb-3">
                  <div className="text-[10px] text-muted-foreground mb-1">中文释义</div>
                  <p className="text-sm whitespace-pre-line leading-relaxed">
                    {word.translation}
                  </p>
                </div>

                {/* English definition */}
                {word.englishDefinition && (
                  <div className="rounded-lg bg-muted/50 p-3 mb-3">
                    <div className="text-[10px] text-muted-foreground mb-1">英文释义</div>
                    <p className="text-sm italic leading-relaxed">
                      {word.englishDefinition}
                    </p>
                  </div>
                )}

                {/* Example */}
                {word.exampleEn && (
                  <div className="rounded-lg bg-emerald-50 dark:bg-emerald-950/30 p-3 mb-3">
                    <div className="text-[10px] text-muted-foreground mb-1">例句</div>
                    <p className="text-sm leading-relaxed">{word.exampleEn}</p>
                    {word.exampleZh && (
                      <p className="text-xs text-muted-foreground mt-1.5 leading-relaxed">
                        {word.exampleZh}
                      </p>
                    )}
                  </div>
                )}

                {/* Mnemonic */}
                {word.mnemonic && (
                  <div className="rounded-lg bg-amber-50 dark:bg-amber-950/30 p-3">
                    <div className="text-[10px] text-muted-foreground mb-1 flex items-center gap-1">
                      <Brain className="h-3 w-3" />
                      记忆法
                    </div>
                    <p className="text-sm whitespace-pre-line leading-relaxed">
                      {word.mnemonic}
                    </p>
                  </div>
                )}

                <Button
                  variant="link"
                  size="sm"
                  className="mt-3 h-7 px-0 text-xs"
                  onClick={(e) => {
                    e.stopPropagation()
                    openWord(word.id)
                  }}
                >
                  查看全部 {word.sentenceCount} 条真题例句 →
                </Button>
              </div>
            )}
          </Card>

          {/* Action buttons */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
            <Button variant="outline" onClick={goPrev} disabled={current === 0}>
              <ChevronLeft className="h-4 w-4 mr-1" />
              上一词
            </Button>
            <Button
              variant="outline"
              className="border-rose-200 text-rose-600 hover:bg-rose-50 hover:text-rose-700 dark:border-rose-900 dark:hover:bg-rose-950"
              onClick={() => {
                setMastery(word.id, 1)
                goNext()
              }}
            >
              <X className="h-4 w-4 mr-1" />
              不熟 (1)
            </Button>
            <Button
              variant="outline"
              className="border-amber-200 text-amber-600 hover:bg-amber-50 hover:text-amber-700 dark:border-amber-900 dark:hover:bg-amber-950"
              onClick={() => {
                setMastery(word.id, 3)
                goNext()
              }}
            >
              <Sparkles className="h-4 w-4 mr-1" />
              熟悉 (2)
            </Button>
            <Button
              variant="outline"
              className="border-emerald-200 text-emerald-600 hover:bg-emerald-50 hover:text-emerald-700 dark:border-emerald-900 dark:hover:bg-emerald-950"
              onClick={() => {
                setMastery(word.id, 5)
                toggleLearned(word.id)
                goNext()
              }}
            >
              <Check className="h-4 w-4 mr-1" />
              掌握 (3)
            </Button>
            <Button variant="outline" onClick={goNext} disabled={current === words.length - 1}>
              下一词
              <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </div>

          {/* Session complete */}
          {current === words.length - 1 && flipped && (
            <Card className="p-5 bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-950/40 dark:to-teal-950/40 border-emerald-300 dark:border-emerald-900 animate-fade-in-up">
              <div className="flex flex-col items-center gap-3 text-center">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500 text-white shadow-lg">
                  <Check className="h-6 w-6" />
                </div>
                <div>
                  <p className="text-base font-bold text-emerald-700 dark:text-emerald-400">
                    🎉 本组单词学习完成！
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    已学习 {words.length} 个单词 · 继续学习更多单词吧
                  </p>
                </div>
                <div className="flex gap-2">
                  <Button size="sm" variant="outline" onClick={() => setView('home')}>
                    返回首页
                  </Button>
                  <Button size="sm" onClick={loadWords} className="bg-emerald-500 hover:bg-emerald-600">
                    <RotateCcw className="h-3.5 w-3.5 mr-1" />
                    换一批继续
                  </Button>
                </div>
              </div>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}
