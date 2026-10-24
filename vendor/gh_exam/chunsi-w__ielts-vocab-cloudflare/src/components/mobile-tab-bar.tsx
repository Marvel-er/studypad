'use client'

import { useState } from 'react'
import { Home, GraduationCap, ClipboardCheck, RefreshCw, Star, BookOpen, Keyboard, MoreHorizontal, Settings as SettingsIcon, Sun, Moon, FileText } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useUIStore, type ViewName } from '@/store/ui'
import { useProgressStore } from '@/store/progress'
import { useTheme } from '@/components/theme-provider'
import { getReviewStats } from '@/lib/review'
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet'

// 4 main tabs + 1 "more" button
const mainNavItems: Array<{ key: ViewName; label: string; icon: typeof Home }> = [
  { key: 'home', label: '首页', icon: Home },
  { key: 'study', label: '学习', icon: GraduationCap },
  { key: 'quiz', label: '测验', icon: ClipboardCheck },
  { key: 'review', label: '复习', icon: RefreshCw },
]

// Items in the "more" sheet
const moreNavItems: Array<{ key: ViewName; label: string; icon: typeof Home; desc: string }> = [
  { key: 'browse', label: '浏览词库', icon: BookOpen, desc: '34,212 个单词' },
  { key: 'spelling', label: '拼写测验', icon: Keyboard, desc: '听写模式练习' },
  { key: 'cloze', label: '例句填空', icon: FileText, desc: '真题语境填空' },
  { key: 'favorites', label: '我的单词本', icon: Star, desc: '收藏与标签管理' },
  { key: 'settings', label: '设置', icon: SettingsIcon, desc: '偏好与数据管理' },
]

export function MobileTabBar() {
  const view = useUIStore((s) => s.view)
  const setView = useUIStore((s) => s.setView)
  const progress = useProgressStore((s) => s.progress)
  const reviewDueCount = getReviewStats(progress).dueNow
  const favoriteCount = Object.values(progress).filter((p) => p.favorite).length
  const { theme, toggleTheme } = useTheme()
  const [moreOpen, setMoreOpen] = useState(false)

  const handleNavigate = (key: ViewName) => {
    setView(key)
    setMoreOpen(false)
  }

  // Check if current view is in the "more" list
  const moreActive = moreNavItems.some((item) => item.key === view)

  return (
    <nav
      className="sm:hidden fixed bottom-0 left-0 right-0 z-50 border-t border-border/60 bg-background/95 backdrop-blur-lg supports-[backdrop-filter]:bg-background/80"
      style={{ paddingBottom: 'env(safe-area-inset-bottom, 0px)' }}
      aria-label="移动端导航"
    >
      <div className="flex items-stretch justify-around h-14">
        {mainNavItems.map((item) => {
          const Icon = item.icon
          const active = view === item.key
          const badge = item.key === 'review' && reviewDueCount > 0 ? reviewDueCount : 0
          return (
            <button
              key={item.key}
              onClick={() => setView(item.key)}
              className={cn(
                'flex-1 flex flex-col items-center justify-center gap-0.5 relative transition-colors',
                active ? 'text-primary' : 'text-muted-foreground hover:text-foreground',
              )}
              aria-label={item.label}
              aria-current={active ? 'page' : undefined}
            >
              <div className="relative">
                <Icon className={cn('h-5 w-5 transition-transform', active && 'scale-110')} />
                {badge > 0 && (
                  <span className="absolute -top-1.5 -right-2 min-w-[16px] h-4 px-1 rounded-full text-[9px] font-bold flex items-center justify-center bg-rose-500 text-white">
                    {badge > 99 ? '99+' : badge}
                  </span>
                )}
              </div>
              <span className={cn('text-[10px] font-medium', active && 'font-semibold')}>{item.label}</span>
              {active && (
                <span className="absolute top-0 left-1/2 -translate-x-1/2 w-8 h-0.5 bg-primary rounded-full" />
              )}
            </button>
          )
        })}

        {/* More button */}
        <Sheet open={moreOpen} onOpenChange={setMoreOpen}>
          <SheetTrigger asChild>
            <button
              className={cn(
                'flex-1 flex flex-col items-center justify-center gap-0.5 relative transition-colors',
                moreActive ? 'text-primary' : 'text-muted-foreground hover:text-foreground',
              )}
              aria-label="更多"
              aria-current={moreActive ? 'page' : undefined}
            >
              <div className="relative">
                <MoreHorizontal className={cn('h-5 w-5 transition-transform', moreActive && 'scale-110')} />
                {favoriteCount > 0 && (
                  <span className="absolute -top-1.5 -right-2 min-w-[16px] h-4 px-1 rounded-full text-[9px] font-bold flex items-center justify-center bg-amber-500 text-white">
                    {favoriteCount > 99 ? '99+' : favoriteCount}
                  </span>
                )}
              </div>
              <span className={cn('text-[10px] font-medium', moreActive && 'font-semibold')}>更多</span>
              {moreActive && (
                <span className="absolute top-0 left-1/2 -translate-x-1/2 w-8 h-0.5 bg-primary rounded-full" />
              )}
            </button>
          </SheetTrigger>
          <SheetContent side="bottom" className="rounded-t-2xl">
            <SheetHeader>
              <SheetTitle>更多功能</SheetTitle>
            </SheetHeader>
            <div className="mt-4 space-y-1.5">
              {moreNavItems.map((item) => {
                const Icon = item.icon
                const active = view === item.key
                const badge = item.key === 'favorites' && favoriteCount > 0 ? favoriteCount : 0
                return (
                  <button
                    key={item.key}
                    onClick={() => handleNavigate(item.key)}
                    className={cn(
                      'w-full flex items-center gap-3 rounded-lg p-3 transition-colors text-left',
                      active ? 'bg-primary/10' : 'hover:bg-muted',
                    )}
                  >
                    <div className={cn(
                      'flex h-9 w-9 items-center justify-center rounded-lg',
                      active ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground',
                    )}>
                      <Icon className="h-4 w-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium flex items-center gap-2">
                        {item.label}
                        {badge > 0 && (
                          <span className="bg-amber-500 text-white text-[9px] font-bold rounded-full px-1.5 py-0.5 min-w-[16px] text-center">
                            {badge > 99 ? '99+' : badge}
                          </span>
                        )}
                      </div>
                      <div className="text-[11px] text-muted-foreground">{item.desc}</div>
                    </div>
                  </button>
                )
              })}

              {/* Theme toggle */}
              <button
                onClick={toggleTheme}
                className="w-full flex items-center gap-3 rounded-lg p-3 transition-colors text-left hover:bg-muted"
              >
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-muted text-muted-foreground">
                  {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium">
                    {theme === 'dark' ? '切换到浅色' : '切换到深色'}
                  </div>
                  <div className="text-[11px] text-muted-foreground">当前: {theme === 'dark' ? '深色' : '浅色'}</div>
                </div>
              </button>
            </div>
          </SheetContent>
        </Sheet>
      </div>
    </nav>
  )
}
