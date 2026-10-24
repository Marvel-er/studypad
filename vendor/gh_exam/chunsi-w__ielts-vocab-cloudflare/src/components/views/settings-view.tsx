'use client'

import { useRef } from 'react'
import { Settings, Volume2, Sun, Moon, Target, Download, Upload, Trash2, Music, Zap, Star } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { useProgressStore } from '@/store/progress'
import { useTheme } from '@/components/theme-provider'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'

export function SettingsView() {
  const audioAccent = useProgressStore((s) => s.audioAccent)
  const setAudioAccent = useProgressStore((s) => s.setAudioAccent)
  const autoPlayAudio = useProgressStore((s) => s.autoPlayAudio)
  const setAutoPlayAudio = useProgressStore((s) => s.setAutoPlayAudio)
  const dailyGoal = useProgressStore((s) => s.dailyGoal)
  const setDailyGoal = useProgressStore((s) => s.setDailyGoal)
  const progress = useProgressStore((s) => s.progress)
  const quizHistory = useProgressStore((s) => s.quizHistory)
  const studyHistory = useProgressStore((s) => s.studyHistory)
  const tags = useProgressStore((s) => s.tags)
  const clearAll = useProgressStore((s) => s.clearAll)
  const importProgress = useProgressStore((s) => s.importProgress)
  const { theme, toggleTheme } = useTheme()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const totalWords = Object.keys(progress).length
  const learnedCount = Object.values(progress).filter((p) => p.learned || p.mastery >= 4).length
  const favoriteCount = Object.values(progress).filter((p) => p.favorite).length

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
    toast.success(`已导出 ${totalWords} 个单词记录`)
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

  const goalOptions = [10, 20, 30, 50, 100]

  return (
    <div className="space-y-4 max-w-2xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Settings className="h-6 w-6 text-primary" />
          设置
        </h1>
        <p className="text-sm text-muted-foreground mt-0.5">
          管理学习偏好、发音、目标与数据
        </p>
      </div>

      {/* Theme */}
      <Card className="p-5">
        <h2 className="text-sm font-semibold flex items-center gap-2 mb-3">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-violet-100 dark:bg-violet-950/40 text-violet-600 dark:text-violet-400">
            {theme === 'dark' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
          </div>
          外观
        </h2>
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm font-medium">主题模式</div>
            <div className="text-xs text-muted-foreground mt-0.5">
              当前: {theme === 'dark' ? '深色模式' : '浅色模式'}
            </div>
          </div>
          <Button variant="outline" size="sm" onClick={toggleTheme}>
            {theme === 'dark' ? <Sun className="h-4 w-4 mr-1" /> : <Moon className="h-4 w-4 mr-1" />}
            切换到{theme === 'dark' ? '浅色' : '深色'}
          </Button>
        </div>
      </Card>

      {/* Audio settings */}
      <Card className="p-5">
        <h2 className="text-sm font-semibold flex items-center gap-2 mb-3">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-100 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400">
            <Volume2 className="h-4 w-4" />
          </div>
          发音设置
        </h2>
        <div className="space-y-4">
          <div>
            <div className="text-sm font-medium mb-2">默认口音</div>
            <div className="flex gap-2">
              <Button
                size="sm"
                variant={audioAccent === 'uk' ? 'default' : 'outline'}
                onClick={() => setAudioAccent('uk')}
                className="flex-1"
              >
                <Music className="h-3.5 w-3.5 mr-1" />
                英式 UK
              </Button>
              <Button
                size="sm"
                variant={audioAccent === 'us' ? 'default' : 'outline'}
                onClick={() => setAudioAccent('us')}
                className="flex-1"
              >
                <Music className="h-3.5 w-3.5 mr-1" />
                美式 US
              </Button>
            </div>
          </div>
          <Separator />
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-medium flex items-center gap-1">
                <Zap className="h-3.5 w-3.5 text-amber-500" />
                自动播放发音
              </div>
              <div className="text-xs text-muted-foreground mt-0.5">
                学习翻卡时自动播放单词发音
              </div>
            </div>
            <button
              onClick={() => setAutoPlayAudio(!autoPlayAudio)}
              className={cn(
                'relative h-6 w-11 rounded-full transition-colors shrink-0',
                autoPlayAudio ? 'bg-primary' : 'bg-muted',
              )}
            >
              <div className={cn(
                'absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform',
                autoPlayAudio ? 'translate-x-5' : 'translate-x-0.5',
              )} />
            </button>
          </div>
        </div>
      </Card>

      {/* Daily goal */}
      <Card className="p-5">
        <h2 className="text-sm font-semibold flex items-center gap-2 mb-3">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-rose-100 dark:bg-rose-950/40 text-rose-600 dark:text-rose-400">
            <Target className="h-4 w-4" />
          </div>
          每日学习目标
        </h2>
        <div className="text-xs text-muted-foreground mb-2">
          每日目标: {dailyGoal} 词 (学习 + 测验)
        </div>
        <div className="flex gap-1.5 flex-wrap">
          {goalOptions.map((n) => (
            <Button
              key={n}
              size="sm"
              variant={dailyGoal === n ? 'default' : 'outline'}
              onClick={() => setDailyGoal(n)}
              className="h-8 px-3"
            >
              {n} 词
            </Button>
          ))}
        </div>
      </Card>

      {/* Data management */}
      <Card className="p-5">
        <h2 className="text-sm font-semibold flex items-center gap-2 mb-3">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-sky-100 dark:bg-sky-950/40 text-sky-600 dark:text-sky-400">
            <Download className="h-4 w-4" />
          </div>
          数据管理
        </h2>

        {/* Stats summary */}
        <div className="grid grid-cols-4 gap-2 mb-4">
          <div className="rounded-lg bg-muted/50 p-2 text-center">
            <div className="text-base font-bold tabular-nums">{totalWords}</div>
            <div className="text-[9px] text-muted-foreground">总单词</div>
          </div>
          <div className="rounded-lg bg-emerald-50 dark:bg-emerald-950/30 p-2 text-center">
            <div className="text-base font-bold tabular-nums text-emerald-600 dark:text-emerald-400">{learnedCount}</div>
            <div className="text-[9px] text-muted-foreground">已掌握</div>
          </div>
          <div className="rounded-lg bg-amber-50 dark:bg-amber-950/30 p-2 text-center">
            <div className="text-base font-bold tabular-nums text-amber-600 dark:text-amber-400">{favoriteCount}</div>
            <div className="text-[9px] text-muted-foreground">收藏</div>
          </div>
          <div className="rounded-lg bg-violet-50 dark:bg-violet-950/30 p-2 text-center">
            <div className="text-base font-bold tabular-nums text-violet-600 dark:text-violet-400">{tags.length}</div>
            <div className="text-[9px] text-muted-foreground">标签</div>
          </div>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept="application/json"
          className="hidden"
          onChange={handleImport}
        />
        <div className="grid grid-cols-2 gap-2">
          <Button variant="outline" size="sm" onClick={handleExport}>
            <Download className="h-3.5 w-3.5 mr-1" />
            导出 JSON
          </Button>
          <Button variant="outline" size="sm" onClick={() => fileInputRef.current?.click()}>
            <Upload className="h-3.5 w-3.5 mr-1" />
            导入 JSON
          </Button>
        </div>
        <Separator className="my-3" />
        <Button
          variant="outline"
          size="sm"
          className="w-full text-rose-600 hover:bg-rose-50 hover:text-rose-700 dark:hover:bg-rose-950 border-rose-200 dark:border-rose-900"
          onClick={() => {
            if (confirm('确定要清空所有学习记录吗？此操作不可撤销，包括进度、收藏、标签、历史。')) {
              clearAll()
              toast.success('已清空所有学习记录')
            }
          }}
        >
          <Trash2 className="h-3.5 w-3.5 mr-1" />
          清空所有记录
        </Button>
      </Card>

      {/* About */}
      <Card className="p-5">
        <h2 className="text-sm font-semibold flex items-center gap-2 mb-2">
          <Star className="h-4 w-4 text-amber-500" />
          关于
        </h2>
        <div className="text-xs text-muted-foreground space-y-1">
          <p>雅思词汇通 - 基于剑桥雅思真题词频数据</p>
          <p>共 34,212 高频词汇 · 76,332 真题例句</p>
          <p>学习进度保存在本地浏览器 localStorage</p>
          <p className="pt-1 text-muted-foreground/60">本站为个人学习用途，数据版权归原作者所有</p>
        </div>
      </Card>
    </div>
  )
}
