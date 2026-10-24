'use client'

import { useMemo } from 'react'
import { BarChart3, BookOpen } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import type { TestSentence } from '@/lib/types'
import { cn } from '@/lib/utils'

interface SourceStatsProps {
  testSentences: TestSentence[]
}

interface SourceStat {
  source: string
  count: number
  percentage: number
}

// Extract base source name (e.g. "剑10" from "剑10", "机经 6" from "机经 6")
function getBaseSource(source: string): string {
  const trimmed = source.trim()
  // Match 剑X or 机经 X patterns
  const jianMatch = trimmed.match(/^剑(\d+)/)
  if (jianMatch) return `剑 ${jianMatch[1]}`
  const jigMatch = trimmed.match(/^机经\s*(\d+)/)
  if (jigMatch) return `机经 ${jigMatch[1]}`
  return trimmed || '其他'
}

// Categorize source into type
function getSourceType(source: string): 'cambridge' | 'jijing' | 'other' {
  if (source.startsWith('剑')) return 'cambridge'
  if (source.startsWith('机经')) return 'jijing'
  return 'other'
}

const typeColors = {
  cambridge: 'bg-rose-500',
  jijing: 'bg-amber-500',
  other: 'bg-sky-500',
}

const typeLabels = {
  cambridge: '剑桥雅思',
  jijing: '机经真题',
  other: '其他',
}

export function SourceStats({ testSentences }: SourceStatsProps) {
  const stats = useMemo(() => {
    if (testSentences.length === 0) return null

    // Count by base source
    const sourceMap = new Map<string, { count: number; type: 'cambridge' | 'jijing' | 'other' }>()
    for (const s of testSentences) {
      const base = getBaseSource(s.source)
      const type = getSourceType(s.source)
      const cur = sourceMap.get(base) || { count: 0, type }
      cur.count++
      sourceMap.set(base, cur)
    }

    // Sort by count desc, take top 12
    const sorted: SourceStat[] = Array.from(sourceMap.entries())
      .map(([source, { count, type }]) => ({
        source,
        count,
        percentage: Math.round((count / testSentences.length) * 100),
        type,
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 12)

    // Type summary
    const typeSummary = {
      cambridge: Array.from(sourceMap.values()).filter((v) => v.type === 'cambridge').reduce((s, v) => s + v.count, 0),
      jijing: Array.from(sourceMap.values()).filter((v) => v.type === 'jijing').reduce((s, v) => s + v.count, 0),
      other: Array.from(sourceMap.values()).filter((v) => v.type === 'other').reduce((s, v) => s + v.count, 0),
    }

    return { sorted, typeSummary, total: testSentences.length }
  }, [testSentences])

  if (!stats) return null

  const maxCount = stats.sorted[0]?.count || 1

  return (
    <Card className="p-5 sm:p-6">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-base font-semibold flex items-center gap-2">
          <BarChart3 className="h-4 w-4 text-primary" />
          真题出处统计
        </h2>
        <Badge variant="secondary" className="text-[10px]">
          {stats.total} 条例句
        </Badge>
      </div>

      {/* Type summary */}
      <div className="grid grid-cols-3 gap-2 mb-4">
        {(['cambridge', 'jijing', 'other'] as const).map((type) => (
          <div key={type} className="rounded-lg bg-muted/50 p-2 text-center">
            <div className="flex items-center justify-center gap-1.5 mb-0.5">
              <span className={cn('h-2 w-2 rounded-full', typeColors[type])} />
              <span className="text-[10px] text-muted-foreground">{typeLabels[type]}</span>
            </div>
            <div className="text-base font-bold tabular-nums">
              {stats.typeSummary[type]}
            </div>
          </div>
        ))}
      </div>

      {/* Source distribution bar chart */}
      <div className="space-y-1.5">
        {stats.sorted.map((stat, idx) => (
          <div key={stat.source} className="flex items-center gap-2">
            <div className="w-16 text-xs text-muted-foreground truncate shrink-0 text-right">
              {stat.source}
            </div>
            <div className="flex-1 h-5 bg-muted/50 rounded overflow-hidden relative">
              <div
                className={cn(
                  'h-full transition-all duration-500 rounded',
                  stat.type === 'cambridge' ? 'bg-rose-500/70 dark:bg-rose-600/70'
                  : stat.type === 'jijing' ? 'bg-amber-500/70 dark:bg-amber-600/70'
                  : 'bg-sky-500/70 dark:bg-sky-600/70',
                )}
                style={{
                  width: `${(stat.count / maxCount) * 100}%`,
                  animationDelay: `${idx * 30}ms`,
                }}
              />
              <span className="absolute right-1.5 top-1/2 -translate-y-1/2 text-[10px] font-medium text-foreground">
                {stat.count}
              </span>
            </div>
            <div className="w-10 text-[10px] text-muted-foreground shrink-0">
              {stat.percentage}%
            </div>
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="mt-3 pt-3 border-t border-border/60 flex items-center gap-3 text-[10px] text-muted-foreground">
        {(['cambridge', 'jijing', 'other'] as const).map((type) => (
          <div key={type} className="flex items-center gap-1">
            <span className={cn('h-2 w-2 rounded-full', typeColors[type])} />
            {typeLabels[type]}
          </div>
        ))}
      </div>
    </Card>
  )
}
