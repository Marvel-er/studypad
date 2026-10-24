'use client'

import { useEffect, useState } from 'react'
import {
  ArrowLeft,
  Volume2,
  Star,
  Brain,
  BookOpen,
  ClipboardList,
  CheckCircle2,
  GraduationCap,
  Loader2,
} from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Separator } from '@/components/ui/separator'
import { api } from '@/lib/api'
import { useUIStore } from '@/store/ui'
import { useProgressStore } from '@/store/progress'
import { useAudioPlayer } from '@/hooks/use-audio'
import type { WordDetail } from '@/lib/types'
import { cn } from '@/lib/utils'
import { PronunciationPractice } from '@/components/pronunciation-practice'
import { WordAssociationGraph } from '@/components/word-association-graph'
import { WordTagSelector } from '@/components/word-tag-selector'
import { SourceStats } from '@/components/source-stats'

export function WordDetailView() {
  const wordId = useUIStore((s) => s.selectedWordId)
  const setView = useUIStore((s) => s.setView)
  const setStudyGroup = useUIStore((s) => s.setStudyGroup)

  const [word, setWord] = useState<WordDetail | null>(null)
  const [loading, setLoading] = useState(true)

  const progress = useProgressStore((s) => (wordId ? s.progress[wordId] : undefined))
  const toggleFavorite = useProgressStore((s) => s.toggleFavorite)
  const toggleLearned = useProgressStore((s) => s.toggleLearned)
  const setMastery = useProgressStore((s) => s.setMastery)
  const { play } = useAudioPlayer()

  useEffect(() => {
    if (!wordId) {
      setView('browse')
      return
    }
    let active = true
    // defer loading state to avoid synchronous setState in effect
    Promise.resolve().then(() => {
      if (active) setLoading(true)
    })
    api.wordById(wordId)
      .then((w) => {
        if (active) {
          setWord(w)
          setLoading(false)
        }
      })
      .catch((e) => {
        console.error(e)
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [wordId, setView])

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-32" />
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-48 w-full" />
      </div>
    )
  }

  if (!word) {
    return (
      <Card className="p-10 text-center">
        <p className="text-muted-foreground">单词未找到</p>
        <Button className="mt-3" onClick={() => setView('browse')}>返回浏览</Button>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => {
          // Use browser history back to preserve previous view + scroll position
          if (typeof window !== 'undefined' && window.history.length > 1) {
            window.history.back()
          } else {
            setView('browse')
          }
        }}
      >
        <ArrowLeft className="h-4 w-4 mr-1" />
        返回
      </Button>

      {/* Main word card */}
      <Card className="overflow-hidden">
        <div className="bg-gradient-to-br from-rose-500 via-orange-500 to-amber-500 p-6 text-white">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0 flex-1">
              <div className="flex items-baseline gap-3 flex-wrap">
                <h1 className="text-3xl sm:text-5xl font-bold tracking-tight">
                  {word.word}
                </h1>
                {word.phonetic && (
                  <span className="font-mono text-base sm:text-lg opacity-90">
                    {word.phonetic}
                  </span>
                )}
              </div>
              <div className="mt-2 flex items-center gap-2 flex-wrap">
                <Badge className="bg-white/20 text-white border-white/30">
                  {word.group.name}
                </Badge>
                <Badge className="bg-white/20 text-white border-white/30">
                  出现 {word.occurrences} 次
                </Badge>
                <Badge className="bg-white/20 text-white border-white/30">
                  {word.testSentences.length} 真题例句
                </Badge>
                {progress?.learned && (
                  <Badge className="bg-emerald-400/30 text-white border-emerald-300/30">
                    <CheckCircle2 className="h-3 w-3 mr-1" />
                    已掌握
                  </Badge>
                )}
              </div>
            </div>
            <div className="flex flex-col gap-1.5 shrink-0">
              {word.audioUk && (
                <Button
                  size="sm"
                  variant="secondary"
                  className="bg-white/20 text-white border-white/30 hover:bg-white/30"
                  onClick={() => play(word.audioUk, 'uk')}
                >
                  <Volume2 className="h-3.5 w-3.5 mr-1" />
                  UK
                </Button>
              )}
              {word.audioUs && (
                <Button
                  size="sm"
                  variant="secondary"
                  className="bg-white/20 text-white border-white/30 hover:bg-white/30"
                  onClick={() => play(word.audioUs, 'us')}
                >
                  <Volume2 className="h-3.5 w-3.5 mr-1" />
                  US
                </Button>
              )}
            </div>
          </div>
        </div>

        <div className="p-5 sm:p-6 space-y-4">
          {/* Action buttons */}
          <div className="flex flex-wrap gap-2">
            <Button
              variant={progress?.favorite ? 'default' : 'outline'}
              size="sm"
              onClick={() => toggleFavorite(word.id)}
            >
              <Star className={cn('h-4 w-4 mr-1', progress?.favorite && 'fill-current')} />
              {progress?.favorite ? '已收藏' : '收藏'}
            </Button>
            <Button
              variant={progress?.learned ? 'default' : 'outline'}
              size="sm"
              onClick={() => toggleLearned(word.id)}
            >
              <CheckCircle2 className="h-4 w-4 mr-1" />
              {progress?.learned ? '已掌握' : '标记掌握'}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setStudyGroup(word.groupId)
                setView('study')
              }}
            >
              <GraduationCap className="h-4 w-4 mr-1" />
              学这一组
            </Button>
          </div>

          {/* Tag selector */}
          <WordTagSelector wordId={word.id} />

          {/* Translation */}
          <div className="rounded-lg bg-rose-50 dark:bg-rose-950/30 p-4">
            <div className="text-[11px] text-muted-foreground mb-1.5 flex items-center gap-1">
              <BookOpen className="h-3 w-3" />
              中文释义
            </div>
            <p className="text-sm sm:text-base whitespace-pre-line leading-relaxed">
              {word.translation}
            </p>
          </div>

          {/* English definition */}
          {word.englishDefinition && (
            <div className="rounded-lg bg-muted/50 p-4">
              <div className="text-[11px] text-muted-foreground mb-1.5">
                English Definition
              </div>
              <p className="text-sm italic leading-relaxed">
                {word.englishDefinition}
              </p>
            </div>
          )}

          {/* Example */}
          {word.exampleEn && (
            <div className="rounded-lg bg-emerald-50 dark:bg-emerald-950/30 p-4">
              <div className="text-[11px] text-muted-foreground mb-1.5">
                示例例句
              </div>
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
            <div className="rounded-lg bg-amber-50 dark:bg-amber-950/30 p-4">
              <div className="text-[11px] text-muted-foreground mb-1.5 flex items-center gap-1">
                <Brain className="h-3 w-3" />
                记忆法
              </div>
              <p className="text-sm whitespace-pre-line leading-relaxed">
                {word.mnemonic}
              </p>
            </div>
          )}

          {/* Mastery controls */}
          <div>
            <div className="text-[11px] text-muted-foreground mb-2">掌握程度</div>
            <div className="flex gap-1.5">
              {[0, 1, 2, 3, 4, 5].map((m) => (
                <button
                  key={m}
                  onClick={() => setMastery(word.id, m as any)}
                  className={cn(
                    'flex-1 h-8 rounded-md text-xs font-medium transition-colors',
                    (progress?.mastery ?? 0) === m
                      ? m === 0
                        ? 'bg-muted text-muted-foreground'
                        : m <= 1
                          ? 'bg-rose-500 text-white'
                          : m <= 3
                            ? 'bg-amber-500 text-white'
                            : 'bg-emerald-500 text-white'
                      : 'bg-muted/50 text-muted-foreground hover:bg-muted',
                  )}
                >
                  {m === 0 ? '未学' : `Lv.${m}`}
                </button>
              ))}
            </div>
          </div>
        </div>
      </Card>

      {/* Pronunciation practice */}
      <PronunciationPractice
        word={word.word}
        audioUk={word.audioUk}
        audioUs={word.audioUs}
      />

      {/* Source statistics */}
      {word.testSentences.length > 0 && (
        <SourceStats testSentences={word.testSentences} />
      )}

      {/* Test sentences */}
      {word.testSentences.length > 0 && (
        <Card className="p-5 sm:p-6">
          <h2 className="text-base font-semibold flex items-center gap-2 mb-3">
            <ClipboardList className="h-4 w-4 text-primary" />
            剑桥雅思真题例句
            <Badge variant="secondary" className="text-[10px]">
              {word.testSentences.length}
            </Badge>
          </h2>
          <div className="space-y-3 max-h-[600px] overflow-y-auto pr-1">
            {word.testSentences.map((s, i) => (
              <div key={s.id} className="rounded-lg border p-3.5">
                <div className="flex items-center gap-2 flex-wrap mb-2">
                  <Badge variant="outline" className="text-[10px]">
                    {s.source}
                  </Badge>
                  {s.location && (
                    <Badge variant="secondary" className="text-[10px]">
                      {s.location}
                    </Badge>
                  )}
                  {s.form !== word.word && (
                    <Badge variant="secondary" className="text-[10px] bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300">
                      形态: {s.form}
                    </Badge>
                  )}
                  {s.translation && (
                    <Badge variant="outline" className="text-[10px] text-sky-600 dark:text-sky-400 border-sky-200 dark:border-sky-900">
                      {s.translation}
                    </Badge>
                  )}
                </div>
                <p className="text-sm leading-relaxed">{s.sentence}</p>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Word association graph */}
      <WordAssociationGraph
        wordId={word.id}
        word={word.word}
        firstLetter={word.firstLetter}
        length={word.length}
        groupId={word.groupId}
        groupName={word.group.name}
      />
    </div>
  )
}
