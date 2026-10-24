'use client'

import { useEffect, useState, useCallback, useRef } from 'react'
import { Search, X, Filter, ArrowUpDown, ChevronLeft, ChevronRight, Loader2 } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { api } from '@/lib/api'
import { useUIStore } from '@/store/ui'
import type { WordListItem, WordGroup } from '@/lib/types'
import { WordCard } from '@/components/word/word-card'
import { cn } from '@/lib/utils'

const PAGE_SIZE = 24
const LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')

// Module-level scroll position cache (survives view switches)
const browseScrollCache = new Map<string, number>()

const sortOptions = [
  { value: 'occurrences_desc', label: '词频 高→低' },
  { value: 'occurrences_asc', label: '词频 低→高' },
  { value: 'word_asc', label: '字母 A→Z' },
  { value: 'word_desc', label: '字母 Z→A' },
]

export function BrowseView() {
  const groupId = useUIStore((s) => s.browseGroupId)
  const letter = useUIStore((s) => s.browseLetter)
  const search = useUIStore((s) => s.browseSearch)
  const setBrowseFilters = useUIStore((s) => s.setBrowseFilters)
  const view = useUIStore((s) => s.view)

  const [groups, setGroups] = useState<WordGroup[]>([])
  const [words, setWords] = useState<WordListItem[]>([])
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const [sort, setSort] = useState('occurrences_desc')
  const [loading, setLoading] = useState(true)
  const [searchInput, setSearchInput] = useState(search)
  const containerRef = useRef<HTMLDivElement>(null)
  const hasRestoredRef = useRef(false)

  // Cache key for current filter state
  const cacheKey = `${groupId ?? 'all'}-${letter ?? 'all'}-${search || 'none'}-${sort}-${page}`

  // Restore scroll position when returning to browse (e.g. from word detail via back button)
  useEffect(() => {
    if (view !== 'browse' || loading || words.length === 0) return
    if (hasRestoredRef.current) return
    hasRestoredRef.current = true
    let saved = browseScrollCache.get(cacheKey)
    if (saved === undefined) {
      try {
        const s = sessionStorage.getItem('browseScroll_' + cacheKey)
        if (s) saved = parseInt(s, 10)
      } catch {}
    }
    if (saved !== undefined && saved > 0) {
      // Use setTimeout to ensure DOM is fully painted after words render
      setTimeout(() => {
        window.scrollTo(0, saved)
      }, 100)
    }
  }, [view, loading, words.length, cacheKey])

  // Reset restoration flag when filters change (component remount also resets ref)
  useEffect(() => {
    hasRestoredRef.current = false
  }, [cacheKey])

  // load groups once
  useEffect(() => {
    api.groups().then(setGroups).catch(console.error)
  }, [])

  // debounce search
  useEffect(() => {
    const t = setTimeout(() => {
      if (searchInput !== search) {
        setBrowseFilters({ browseSearch: searchInput } as any)
        setPage(1)
      }
    }, 350)
    return () => clearTimeout(t)
  }, [searchInput, search, setBrowseFilters])

  // reset page when filters change
  useEffect(() => {
    setPage(1)
  }, [groupId, letter, search])

  const loadWords = useCallback(async () => {
    setLoading(true)
    try {
      const r = await api.words({
        page,
        pageSize: PAGE_SIZE,
        groupId: groupId ?? undefined,
        firstLetter: letter ?? undefined,
        search: search || undefined,
        sort,
      })
      setWords(r.words)
      setTotal(r.total)
      setTotalPages(r.totalPages)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }, [page, groupId, letter, search, sort])

  useEffect(() => {
    loadWords()
  }, [loadWords])

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold">词库浏览</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            共 {total.toLocaleString()} 个单词 · 第 {page} / {totalPages || 1} 页
          </p>
        </div>
        {(groupId || letter || search) && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setBrowseFilters({
                browseGroupId: null,
                browseLetter: null,
                browseSearch: '',
              } as any)
              setSearchInput('')
              setPage(1)
            }}
          >
            <X className="h-3.5 w-3.5 mr-1" />
            清除筛选
          </Button>
        )}
      </div>

      {/* Filters */}
      <Card className="p-4 space-y-3">
        {/* Search bar */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="搜索单词、中文翻译或英文释义..."
            className="pl-9 pr-9"
          />
          {searchInput && (
            <button
              onClick={() => {
                setSearchInput('')
                setBrowseFilters({ browseSearch: '' } as any)
              }}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        {/* Group filter pills */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs text-muted-foreground flex items-center gap-1 shrink-0">
            <Filter className="h-3 w-3" />
            词频:
          </span>
          <button
            onClick={() => setBrowseFilters({ browseGroupId: null } as any)}
            className={cn(
              'rounded-full px-2.5 py-1 text-xs font-medium transition-colors',
              !groupId
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted text-muted-foreground hover:bg-muted/80 hover:text-foreground',
            )}
          >
            全部
          </button>
          {groups.map((g) => (
            <button
              key={g.id}
              onClick={() => setBrowseFilters({ browseGroupId: g.id } as any)}
              className={cn(
                'rounded-full px-2.5 py-1 text-xs font-medium transition-colors',
                groupId === g.id
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted text-muted-foreground hover:bg-muted/80 hover:text-foreground',
              )}
            >
              {g.name}
              <span className="ml-1 opacity-70">({g.wordCount})</span>
            </button>
          ))}
        </div>

        {/* Letter filter */}
        <div className="flex items-center gap-1 flex-wrap">
          <span className="text-xs text-muted-foreground shrink-0 mr-1">首字母:</span>
          <button
            onClick={() => setBrowseFilters({ browseLetter: null } as any)}
            className={cn(
              'rounded px-1.5 py-0.5 text-xs font-mono transition-colors',
              !letter ? 'bg-primary text-primary-foreground' : 'hover:bg-muted',
            )}
          >
            全部
          </button>
          {LETTERS.map((l) => (
            <button
              key={l}
              onClick={() => setBrowseFilters({ browseLetter: l } as any)}
              className={cn(
                'rounded px-1.5 py-0.5 text-xs font-mono transition-colors',
                letter === l
                  ? 'bg-primary text-primary-foreground'
                  : 'hover:bg-muted',
              )}
            >
              {l}
            </button>
          ))}
        </div>

        {/* Sort */}
        <div className="flex items-center gap-2">
          <ArrowUpDown className="h-3.5 w-3.5 text-muted-foreground" />
          <Select value={sort} onValueChange={setSort}>
            <SelectTrigger className="h-8 w-[160px] text-xs">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {sortOptions.map((o) => (
                <SelectItem key={o.value} value={o.value} className="text-xs">
                  {o.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </Card>

      {/* Words grid */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
          {Array.from({ length: 12 }).map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      ) : words.length === 0 ? (
        <Card className="p-10 text-center">
          <p className="text-muted-foreground">未找到符合条件的单词</p>
        </Card>
      ) : (
        <>
          <div ref={containerRef} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
            {words.map((w) => (
              <WordCard
                key={w.id}
                word={w}
                onClick={() => {
                  // Save scroll position before navigating to word detail
                  const scrollY = window.scrollY
                  browseScrollCache.set(cacheKey, scrollY)
                  try {
                    sessionStorage.setItem('browseScroll_' + cacheKey, String(scrollY))
                  } catch {}
                }}
              />
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 pt-2">
              <Button
                variant="outline"
                size="sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
              >
                <ChevronLeft className="h-4 w-4" />
                上一页
              </Button>
              <span className="text-sm text-muted-foreground px-2">
                {page} / {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              >
                下一页
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
