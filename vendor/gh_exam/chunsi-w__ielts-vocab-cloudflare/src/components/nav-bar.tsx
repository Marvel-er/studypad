'use client'

import { useEffect, useState } from 'react'
import { Home, BookOpen, GraduationCap, ClipboardCheck, Star, BookMarked, Sun, Moon, Command, Keyboard, RefreshCw } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useUIStore, type ViewName } from '@/store/ui'
import { useProgressStore } from '@/store/progress'
import { Button } from '@/components/ui/button'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'
import { useTheme } from '@/components/theme-provider'
import { CommandPalette } from '@/components/command-palette'
import { getReviewStats } from '@/lib/review'

const navItems: Array<{ key: ViewName; label: string; icon: typeof Home }> = [
  { key: 'home', label: '首页', icon: Home },
  { key: 'browse', label: '浏览', icon: BookOpen },
  { key: 'study', label: '学习', icon: GraduationCap },
  { key: 'quiz', label: '测验', icon: ClipboardCheck },
  { key: 'spelling', label: '拼写', icon: Keyboard },
  { key: 'review', label: '复习', icon: RefreshCw },
  { key: 'favorites', label: '收藏', icon: Star },
]

export function NavBar() {
  const view = useUIStore((s) => s.view)
  const setView = useUIStore((s) => s.setView)
  const favoriteCount = useProgressStore((s) =>
    Object.values(s.progress).filter((p) => p.favorite).length,
  )
  const learnedCount = useProgressStore((s) =>
    Object.values(s.progress).filter((p) => p.learned || p.mastery >= 4).length,
  )
  const progress = useProgressStore((s) => s.progress)
  const reviewDueCount = getReviewStats(progress).dueNow
  const { theme, toggleTheme } = useTheme()
  const [paletteOpen, setPaletteOpen] = useState(false)

  // Global Cmd+K / Ctrl+K shortcut
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setPaletteOpen((o) => !o)
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  return (
    <>
    <header className="sticky top-0 z-40 w-full border-b border-border/60 bg-background/80 backdrop-blur-lg supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-14 max-w-7xl items-center justify-between gap-4 px-4">
        <button
          onClick={() => setView('home')}
          className="flex items-center gap-2 shrink-0 group"
          aria-label="返回首页"
        >
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-rose-500 to-orange-500 text-white font-bold text-sm shadow-sm transition-transform group-hover:scale-105">
            雅
          </div>
          <span className="font-semibold text-base hidden sm:inline">
            雅思词汇通
          </span>
        </button>

        <div className="flex items-center gap-2">
        <nav className="hidden sm:flex items-center gap-0.5 sm:gap-1">
          {navItems.map((item) => {
            const Icon = item.icon
            const active = view === item.key || (item.key === 'browse' && view === 'word')
            const badge =
              item.key === 'favorites' && favoriteCount > 0
                ? favoriteCount
                : item.key === 'review' && reviewDueCount > 0
                  ? reviewDueCount
                  : item.key === 'home' && learnedCount > 0
                    ? learnedCount
                    : 0
            return (
              <Button
                key={item.key}
                variant={active ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setView(item.key)}
                className={cn(
                  'gap-1.5 relative',
                  active
                    ? 'bg-primary text-primary-foreground shadow-sm'
                    : 'text-muted-foreground hover:text-foreground',
                )}
              >
                <Icon className="h-4 w-4" />
                <span className="hidden sm:inline">{item.label}</span>
                {badge > 0 && (
                  <span
                    className={cn(
                      'ml-1 rounded-full px-1.5 py-0 text-[10px] font-semibold leading-4',
                      active
                        ? 'bg-primary-foreground/20 text-primary-foreground'
                        : item.key === 'review'
                          ? 'bg-rose-500 text-white animate-pulse-soft'
                          : 'bg-amber-500/15 text-amber-600 dark:text-amber-400',
                    )}
                  >
                    {badge > 99 ? '99+' : badge}
                  </span>
                )}
              </Button>
            )
          })}
        </nav>

        <div className="flex items-center gap-1">
          <TooltipProvider delayDuration={400}>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPaletteOpen(true)}
                  className="h-8 gap-1.5 px-2 text-xs text-muted-foreground"
                >
                  <Command className="h-3.5 w-3.5" />
                  <span className="hidden md:inline">搜索</span>
                  <kbd className="hidden md:inline-flex items-center gap-0.5 rounded border bg-muted px-1 py-0 text-[10px] font-mono">
                    ⌘K
                  </kbd>
                </Button>
              </TooltipTrigger>
              <TooltipContent side="bottom">命令面板 (⌘K)</TooltipContent>
            </Tooltip>
          </TooltipProvider>

          <TooltipProvider delayDuration={400}>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={toggleTheme}
                  className="h-8 w-8 text-muted-foreground hover:text-foreground"
                  aria-label="切换主题"
                >
                  {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
                </Button>
              </TooltipTrigger>
              <TooltipContent side="bottom">切换主题 ({theme === 'dark' ? '深色' : '浅色'})</TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
        </div>
      </div>
    </header>
    <CommandPalette open={paletteOpen} onOpenChange={setPaletteOpen} />
    </>
  )
}

export function Footer() {
  return (
    <footer className="mt-auto border-t border-border/60 bg-muted/30 hidden sm:block">
      <div className="container mx-auto max-w-7xl px-4 py-6 text-center text-xs text-muted-foreground">
        <p className="flex items-center justify-center gap-1.5 flex-wrap">
          <BookMarked className="h-3.5 w-3.5" />
          <span>数据来源：FLDC 剑桥雅思真题词频 · 共 34,212 高频词汇 · 76,332 真题例句</span>
        </p>
        <p className="mt-1.5">
          本站为个人学习用途，所有数据版权归原作者所有 · 学习进度保存在本地浏览器
        </p>
      </div>
    </footer>
  )
}
