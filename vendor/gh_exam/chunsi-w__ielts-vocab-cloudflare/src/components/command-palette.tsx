'use client'

import { useEffect, useState, useCallback } from 'react'
import { CommandDialog, CommandInput, CommandList, CommandEmpty, CommandGroup, CommandItem, CommandSeparator, CommandShortcut } from '@/components/ui/command'
import { Home, BookOpen, GraduationCap, ClipboardCheck, Star, Search, CornerDownRight, TrendingUp, Settings as SettingsIcon, Sun, Moon, Keyboard, RefreshCw, FileText } from 'lucide-react'
import { api } from '@/lib/api'
import { useUIStore } from '@/store/ui'
import { useTheme } from '@/components/theme-provider'
import { useProgressStore } from '@/store/progress'
import type { WordGroup } from '@/lib/types'

interface SearchResult {
  id: number
  word: string
  translation: string
  phonetic: string | null
  occurrences: number
  groupName: string
  groupRank: number
}

interface CommandPaletteProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function CommandPalette({ open, onOpenChange }: CommandPaletteProps) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [groups, setGroups] = useState<WordGroup[]>([])
  const [searching, setSearching] = useState(false)

  const setView = useUIStore((s) => s.setView)
  const openWord = useUIStore((s) => s.openWord)
  const setBrowseFilters = useUIStore((s) => s.setBrowseFilters)
  const setStudyGroup = useUIStore((s) => s.setStudyGroup)
  const setQuizConfig = useUIStore((s) => s.setQuizConfig)
  const { theme, toggleTheme } = useTheme()
  const favoriteCount = useProgressStore((s) => Object.values(s.progress).filter((p) => p.favorite).length)

  // Load groups
  useEffect(() => {
    api.groups().then(setGroups).catch(console.error)
  }, [])

  // Debounced search
  useEffect(() => {
    if (!query.trim()) {
      // defer to avoid synchronous setState in effect
      Promise.resolve().then(() => setResults([]))
      return
    }
    let cancelled = false
    Promise.resolve().then(() => {
      if (!cancelled) setSearching(true)
    })
    const t = setTimeout(() => {
      api
        .search(query.trim(), 8)
        .then((r) => {
          if (!cancelled) setResults(r.results)
        })
        .catch(() => {
          if (!cancelled) setResults([])
        })
        .finally(() => {
          if (!cancelled) setSearching(false)
        })
    }, 250)
    return () => {
      cancelled = true
      clearTimeout(t)
    }
  }, [query])

  const go = useCallback(
    (action: () => void) => {
      action()
      onOpenChange(false)
      setQuery('')
    },
    [onOpenChange],
  )

  return (
    <CommandDialog open={open} onOpenChange={onOpenChange}>
      <CommandInput
        placeholder="搜索单词，或输入命令... (例如: debate, 学习, 测验)"
        value={query}
        onValueChange={setQuery}
      />
      <CommandList>
        <CommandEmpty>{searching ? '搜索中...' : query.trim() ? '未找到匹配结果' : '输入关键词搜索单词'}</CommandEmpty>

        {/* Word search results */}
        {results.length > 0 && (
          <CommandGroup heading="单词结果" className="max-h-[280px] overflow-y-auto">
            {results.map((r) => (
              <CommandItem
                key={r.id}
                value={`word-${r.word}`}
                onSelect={() => go(() => openWord(r.id))}
                className="flex items-center gap-2"
              >
                <Search className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{r.word}</span>
                    {r.phonetic && (
                      <span className="text-[11px] text-muted-foreground font-mono truncate">
                        {r.phonetic}
                      </span>
                    )}
                  </div>
                  <div className="text-[11px] text-muted-foreground truncate">
                    {r.translation.replace(/\n/g, ' · ').slice(0, 50)}
                  </div>
                </div>
                <span className="text-[10px] text-muted-foreground shrink-0">{r.groupName}</span>
              </CommandItem>
            ))}
          </CommandGroup>
        )}

        {results.length > 0 && <CommandSeparator />}

        {/* Navigation commands */}
        {!query.trim() && (
          <CommandGroup heading="页面导航">
            <CommandItem value="首页 home" onSelect={() => go(() => setView('home'))}>
              <Home className="h-4 w-4" />
              <span>返回首页</span>
              <CommandShortcut>首页</CommandShortcut>
            </CommandItem>
            <CommandItem value="浏览 browse 词库" onSelect={() => go(() => setView('browse'))}>
              <BookOpen className="h-4 w-4" />
              <span>浏览词库</span>
              <CommandShortcut>浏览</CommandShortcut>
            </CommandItem>
            <CommandItem value="学习 study 翻卡" onSelect={() => go(() => setView('study'))}>
              <GraduationCap className="h-4 w-4" />
              <span>开始学习 (翻卡模式)</span>
              <CommandShortcut>学习</CommandShortcut>
            </CommandItem>
            <CommandItem value="测验 quiz 测试" onSelect={() => go(() => setView('quiz'))}>
              <ClipboardCheck className="h-4 w-4" />
              <span>单词测验</span>
              <CommandShortcut>测验</CommandShortcut>
            </CommandItem>
            <CommandItem value="拼写 spelling 听写" onSelect={() => go(() => setView('spelling'))}>
              <Keyboard className="h-4 w-4" />
              <span>拼写测验 (听写模式)</span>
              <CommandShortcut>拼写</CommandShortcut>
            </CommandItem>
            <CommandItem value="填空 cloze 例句" onSelect={() => go(() => setView('cloze'))}>
              <FileText className="h-4 w-4" />
              <span>例句填空 (真题语境)</span>
              <CommandShortcut>填空</CommandShortcut>
            </CommandItem>
            <CommandItem value="复习 review 艾宾浩斯" onSelect={() => go(() => setView('review'))}>
              <RefreshCw className="h-4 w-4" />
              <span>智能复习 (艾宾浩斯)</span>
              <CommandShortcut>复习</CommandShortcut>
            </CommandItem>
            <CommandItem value="收藏 favorites 生词本" onSelect={() => go(() => setView('favorites'))}>
              <Star className="h-4 w-4" />
              <span>我的单词本</span>
              {favoriteCount > 0 && (
                <span className="ml-auto text-[10px] bg-amber-500/15 text-amber-600 dark:text-amber-400 rounded-full px-1.5 py-0.5">
                  {favoriteCount}
                </span>
              )}
            </CommandItem>
            <CommandItem value="设置 settings 配置" onSelect={() => go(() => setView('settings'))}>
              <SettingsIcon className="h-4 w-4" />
              <span>设置</span>
              <CommandShortcut>设置</CommandShortcut>
            </CommandItem>
          </CommandGroup>
        )}

        {/* Group shortcuts */}
        {!query.trim() && groups.length > 0 && (
          <>
            <CommandSeparator />
            <CommandGroup heading="按词频学习">
              {groups.map((g) => (
                <CommandItem
                  key={g.id}
                  value={`group ${g.name}`}
                  onSelect={() =>
                    go(() => {
                      setStudyGroup(g.id)
                      setView('study')
                    })
                  }
                >
                  <TrendingUp className="h-4 w-4" />
                  <span>学习「{g.name}」</span>
                  <CommandShortcut>{g.wordCount} 词</CommandShortcut>
                </CommandItem>
              ))}
            </CommandGroup>
          </>
        )}

        {/* Settings */}
        {!query.trim() && (
          <>
            <CommandSeparator />
            <CommandGroup heading="设置">
              <CommandItem
                value="theme dark light 主题 深色 浅色"
                onSelect={() => go(() => toggleTheme())}
              >
                {theme === 'dark' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
                <span>切换主题 (当前: {theme === 'dark' ? '深色' : '浅色'})</span>
              </CommandItem>
              <CommandItem value="高频词 top100" onSelect={() => go(() => {
                setBrowseFilters({ browseGroupId: 1, browseLetter: null, browseSearch: '' } as any)
                setView('browse')
              })}>
                <CornerDownRight className="h-4 w-4" />
                <span>高频词 Top (Rank 1)</span>
              </CommandItem>
              <CommandItem value="英中测验 en_to_zh" onSelect={() => go(() => {
                setQuizConfig({ quizMode: 'en_to_zh', quizGroupId: null, quizCount: 10 })
                setView('quiz')
              })}>
                <CornerDownRight className="h-4 w-4" />
                <span>英→中 测验</span>
              </CommandItem>
            </CommandGroup>
          </>
        )}
      </CommandList>
    </CommandDialog>
  )
}
