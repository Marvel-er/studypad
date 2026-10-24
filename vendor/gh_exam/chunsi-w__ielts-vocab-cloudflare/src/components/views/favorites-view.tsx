'use client'

import { useEffect, useState, useMemo, useRef } from 'react'
import { Star, Trash2, Loader2, BookOpen, Heart, CheckCircle2, Clock, Download, Upload, Tag, CheckSquare, Square, X } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
  DropdownMenuCheckboxItem,
} from '@/components/ui/dropdown-menu'
import { api } from '@/lib/api'
import { useProgressStore, TAG_COLORS } from '@/store/progress'
import { useUIStore } from '@/store/ui'
import type { WordListItem } from '@/lib/types'
import { WordCard } from '@/components/word/word-card'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'

export function FavoritesView() {
  const progress = useProgressStore((s) => s.progress)
  const quizHistory = useProgressStore((s) => s.quizHistory)
  const studyHistory = useProgressStore((s) => s.studyHistory)
  const tags = useProgressStore((s) => s.tags)
  const clearAll = useProgressStore((s) => s.clearAll)
  const setView = useUIStore((s) => s.setView)
  const setBrowseFilters = useUIStore((s) => s.setBrowseFilters)
  const importProgress = useProgressStore((s) => s.importProgress)
  const toggleWordTag = useProgressStore((s) => s.toggleWordTag)

  const [tab, setTab] = useState<'favorites' | 'learned' | 'learning'>('favorites')
  const [loading, setLoading] = useState(true)
  const [words, setWords] = useState<WordListItem[]>([])
  const [activeTag, setActiveTag] = useState<string | null>(null)
  const [selectMode, setSelectMode] = useState(false)
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set())
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Compute IDs based on tab + active tag filter
  const ids = useMemo(() => {
    return Object.entries(progress)
      .filter(([, p]) => {
        if (tab === 'favorites') {
          if (!p.favorite) return false
        } else if (tab === 'learned') {
          if (!(p.learned || p.mastery >= 4)) return false
        } else if (tab === 'learning') {
          if (!(p.mastery > 0 && p.mastery < 4)) return false
        }
        // tag filter
        if (activeTag && !(p.tags || []).includes(activeTag)) return false
        return true
      })
      .map(([id]) => parseInt(id, 10))
  }, [progress, tab, activeTag])

  useEffect(() => {
    if (ids.length === 0) {
      // defer to avoid synchronous setState in effect
      Promise.resolve().then(() => {
        setWords([])
        setLoading(false)
      })
      return
    }
    let active = true
    Promise.resolve().then(() => {
      if (active) setLoading(true)
    })
    api.wordsByIds(ids)
      .then((r) => {
        if (active) {
          setWords(r.words)
          setLoading(false)
        }
      })
      .catch((e) => {
        console.error(e)
        if (active) {
          setWords([])
          setLoading(false)
        }
      })
    return () => {
      active = false
    }
  }, [ids])

  const handleExport = () => {
    const data = {
      version: 1,
      exportedAt: new Date().toISOString(),
      progress,
      quizHistory,
      studyHistory,
      tags,
    }
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `ielts-vocab-backup-${new Date().toISOString().slice(0, 10)}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    toast.success(`已导出 ${Object.keys(progress).length} 个单词记录`)
  }

  const handleImport = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const reader = new FileReader()
    reader.onload = () => {
      try {
        const data = JSON.parse(reader.result as string)
        if (!data.progress || typeof data.progress !== 'object') {
          throw new Error('Invalid file format')
        }
        if (confirm(`即将导入 ${Object.keys(data.progress).length} 个单词记录，将与现有记录合并。继续？`)) {
          importProgress(data.progress, data.quizHistory, data.studyHistory)
          toast.success(`已导入 ${Object.keys(data.progress).length} 个单词记录`)
        }
      } catch (err) {
        toast.error('导入失败：文件格式不正确')
      }
    }
    reader.readAsText(file)
    e.target.value = ''
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Star className="h-6 w-6 text-amber-400" />
            我的单词本
          </h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            收藏、学习、掌握的单词都在这里
          </p>
        </div>
        <div className="flex items-center gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept="application/json"
            className="hidden"
            onChange={handleImport}
          />
          {words.length > 0 && (
            <Button
              variant={selectMode ? 'default' : 'outline'}
              size="sm"
              onClick={() => {
                setSelectMode((s) => !s)
                setSelectedIds(new Set())
              }}
            >
              <CheckSquare className="h-3.5 w-3.5 mr-1" />
              {selectMode ? `已选 ${selectedIds.size}` : '批量'}
            </Button>
          )}
          {selectMode && selectedIds.size > 0 && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="default" size="sm">
                  <Tag className="h-3.5 w-3.5 mr-1" />
                  打标签
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>批量添加标签</DropdownMenuLabel>
                <DropdownMenuSeparator />
                {tags.map((t) => (
                  <DropdownMenuItem
                    key={t.name}
                    onClick={() => {
                      selectedIds.forEach((id) => {
                        if (!(progress[id]?.tags || []).includes(t.name)) {
                          toggleWordTag(id, t.name)
                        }
                      })
                      toast.success(`已为 ${selectedIds.size} 个单词添加「${t.name}」标签`)
                      setSelectedIds(new Set())
                      setSelectMode(false)
                    }}
                  >
                    <span
                      className="h-2.5 w-2.5 rounded-full mr-2"
                      style={{ backgroundColor: t.color }}
                    />
                    {t.name}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          )}
          {selectMode && selectedIds.size > 0 && (
            <Button
              variant="outline"
              size="sm"
              className="text-rose-600 hover:bg-rose-50 hover:text-rose-700 dark:hover:bg-rose-950"
              onClick={() => {
                setSelectedIds(new Set())
              }}
            >
              <X className="h-3.5 w-3.5 mr-1" />
              取消
            </Button>
          )}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <Download className="h-3.5 w-3.5 mr-1" />
                数据
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={handleExport}>
                <Download className="h-3.5 w-3.5 mr-2" />
                导出生词本 (JSON)
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => fileInputRef.current?.click()}>
                <Upload className="h-3.5 w-3.5 mr-2" />
                导入生词本
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className="text-rose-600 focus:text-rose-700"
                onClick={() => {
                  if (confirm('确定要清空所有学习记录吗？此操作不可撤销。')) {
                    clearAll()
                    setWords([])
                    toast.success('已清空学习记录')
                  }
                }}
              >
                <Trash2 className="h-3.5 w-3.5 mr-2" />
                清空记录
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      <Tabs value={tab} onValueChange={(v) => setTab(v as any)}>
        <TabsList className="grid w-full grid-cols-3 max-w-md">
          <TabsTrigger value="favorites" className="gap-1">
            <Heart className="h-3.5 w-3.5" />
            收藏 ({Object.values(progress).filter((p) => p.favorite).length})
          </TabsTrigger>
          <TabsTrigger value="learning" className="gap-1">
            <Clock className="h-3.5 w-3.5" />
            学习中 ({Object.values(progress).filter((p) => p.mastery > 0 && p.mastery < 4).length})
          </TabsTrigger>
          <TabsTrigger value="learned" className="gap-1">
            <CheckCircle2 className="h-3.5 w-3.5" />
            已掌握 ({Object.values(progress).filter((p) => p.learned || p.mastery >= 4).length})
          </TabsTrigger>
        </TabsList>

        {/* Tag filter row */}
        {tags.length > 0 && (
          <div className="flex items-center gap-1.5 flex-wrap mt-3">
            <span className="text-xs text-muted-foreground flex items-center gap-1 shrink-0">
              <Tag className="h-3 w-3" />
              标签:
            </span>
            <button
              onClick={() => setActiveTag(null)}
              className={cn(
                'rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors',
                !activeTag
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted text-muted-foreground hover:bg-muted/80 hover:text-foreground',
              )}
            >
              全部
            </button>
            {tags.map((t) => {
              const count = Object.values(progress).filter(
                (p) => p.tags?.includes(t.name),
              ).length
              return (
                <button
                  key={t.name}
                  onClick={() => setActiveTag(activeTag === t.name ? null : t.name)}
                  className={cn(
                    'rounded-full px-2.5 py-0.5 text-xs font-medium transition-all flex items-center gap-1',
                    activeTag === t.name
                      ? 'text-white shadow-sm'
                      : 'bg-muted text-muted-foreground hover:bg-muted/80 hover:text-foreground',
                  )}
                  style={activeTag === t.name ? { backgroundColor: t.color } : undefined}
                >
                  <span
                    className="h-2 w-2 rounded-full"
                    style={{ backgroundColor: activeTag === t.name ? 'white' : t.color }}
                  />
                  {t.name}
                  <span className="opacity-70">({count})</span>
                </button>
              )
            })}
          </div>
        )}

        <TabsContent value={tab} className="mt-4">
          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
              {Array.from({ length: 8 }).map((_, i) => (
                <Skeleton key={i} className="h-32" />
              ))}
            </div>
          ) : words.length === 0 ? (
            <Card className="p-10 text-center">
              <BookOpen className="h-10 w-10 text-muted-foreground/40 mx-auto mb-3" />
              <p className="text-muted-foreground">
                {tab === 'favorites' && '还没有收藏的单词'}
                {tab === 'learning' && '还没有学习中的单词'}
                {tab === 'learned' && '还没有掌握的单词'}
              </p>
              <p className="text-xs text-muted-foreground/70 mt-1">
                去浏览词库或开始学习吧
              </p>
              <div className="mt-4 flex gap-2 justify-center">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setBrowseFilters({ browseGroupId: null, browseLetter: null, browseSearch: '' } as any)
                    setView('browse')
                  }}
                >
                  <BookOpen className="h-3.5 w-3.5 mr-1" />
                  浏览词库
                </Button>
                <Button size="sm" onClick={() => setView('study')}>
                  开始学习
                </Button>
              </div>
            </Card>
          ) : (
            <>
              <div className="flex items-center justify-between text-xs text-muted-foreground mb-3">
                <span>共 {words.length} 个单词</span>
                {selectMode && (
                  <button
                    onClick={() => {
                      if (selectedIds.size === words.length) {
                        setSelectedIds(new Set())
                      } else {
                        setSelectedIds(new Set(words.map((w) => w.id)))
                      }
                    }}
                    className="hover:text-foreground transition-colors"
                  >
                    {selectedIds.size === words.length ? '取消全选' : '全选'}
                  </button>
                )}
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
                {words.map((w) => {
                  const isSelected = selectedIds.has(w.id)
                  return (
                    <div
                      key={w.id}
                      className={cn(
                        'relative rounded-xl transition-all',
                        selectMode && 'cursor-pointer',
                        selectMode && isSelected && 'ring-2 ring-primary ring-offset-2 ring-offset-background rounded-xl',
                      )}
                      onClick={selectMode ? (e) => {
                        e.stopPropagation()
                        setSelectedIds((prev) => {
                          const next = new Set(prev)
                          if (next.has(w.id)) {
                            next.delete(w.id)
                          } else {
                            next.add(w.id)
                          }
                          return next
                        })
                      } : undefined}
                    >
                      {selectMode && (
                        <div className={cn(
                          'absolute top-2 right-2 z-10 flex h-6 w-6 items-center justify-center rounded-full border-2 transition-all',
                          isSelected
                            ? 'bg-primary border-primary text-primary-foreground'
                            : 'bg-background/80 border-border backdrop-blur',
                        )}>
                          {isSelected ? <CheckSquare className="h-3.5 w-3.5" /> : <Square className="h-3.5 w-3.5" />}
                        </div>
                      )}
                      <WordCard word={w} />
                    </div>
                  )
                })}
              </div>
            </>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
