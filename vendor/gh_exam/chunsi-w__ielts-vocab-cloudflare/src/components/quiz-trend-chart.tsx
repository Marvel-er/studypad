'use client'

import { useMemo } from 'react'
import { TrendingUp, Calendar } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useProgressStore } from '@/store/progress'
import { cn } from '@/lib/utils'
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
} from 'recharts'

interface ChartPoint {
  date: number
  label: string
  accuracy: number
  total: number
  correct: number
}

export function QuizTrendChart() {
  const quizHistory = useProgressStore((s) => s.quizHistory)

  const { chartData, avgAccuracy, trend } = useMemo(() => {
    if (quizHistory.length === 0) {
      return { chartData: [] as ChartPoint[], avgAccuracy: 0, trend: 0 }
    }
    // Sort by date ascending
    const sorted = [...quizHistory].sort((a, b) => a.date - b.date)
    const points: ChartPoint[] = sorted.map((q) => {
      const d = new Date(q.date)
      const acc = q.total > 0 ? Math.round((q.correct / q.total) * 100) : 0
      return {
        date: q.date,
        label: `${d.getMonth() + 1}/${d.getDate()}`,
        accuracy: acc,
        total: q.total,
        correct: q.correct,
      }
    })

    const avgAcc = points.length > 0
      ? Math.round(points.reduce((s, p) => s + p.accuracy, 0) / points.length)
      : 0

    // Trend: compare last 3 vs previous 3
    let trendVal = 0
    if (points.length >= 4) {
      const recent = points.slice(-3)
      const previous = points.slice(-6, -3)
      const recentAvg = recent.reduce((s, p) => s + p.accuracy, 0) / recent.length
      const prevAvg = previous.length > 0
        ? previous.reduce((s, p) => s + p.accuracy, 0) / previous.length
        : recentAvg
      trendVal = Math.round(recentAvg - prevAvg)
    }

    return { chartData: points, avgAccuracy: avgAcc, trend: trendVal }
  }, [quizHistory])

  if (quizHistory.length < 2) {
    return null
  }

  return (
    <Card className="p-5">
      <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
        <h3 className="text-sm font-semibold flex items-center gap-2">
          <TrendingUp className="h-4 w-4 text-primary" />
          正确率趋势
        </h3>
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="text-[10px]">
            平均 {avgAccuracy}%
          </Badge>
          {trend !== 0 && (
            <Badge
              variant="outline"
              className={cn(
                'text-[10px] gap-0.5',
                trend > 0
                  ? 'text-emerald-600 dark:text-emerald-400 border-emerald-300 dark:border-emerald-800'
                  : 'text-rose-600 dark:text-rose-400 border-rose-300 dark:border-rose-800',
              )}
            >
              {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
            </Badge>
          )}
        </div>
      </div>

      <div className="h-40 -ml-2">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 5, right: 10, bottom: 0, left: 0 }}>
            <defs>
              <linearGradient id="accGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#f43f5e" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#f43f5e" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.3} />
            <XAxis
              dataKey="label"
              tick={{ fontSize: 10, fill: 'var(--muted-foreground)' }}
              tickLine={false}
              axisLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              domain={[0, 100]}
              tick={{ fontSize: 10, fill: 'var(--muted-foreground)' }}
              tickLine={false}
              axisLine={false}
              ticks={[0, 50, 100]}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'var(--popover)',
                border: '1px solid var(--border)',
                borderRadius: '8px',
                fontSize: '12px',
              }}
              labelStyle={{ color: 'var(--popover-foreground)' }}
              formatter={(value: number) => [`${value}%`, '正确率']}
            />
            <ReferenceLine y={60} stroke="#f59e0b" strokeDasharray="4 4" strokeOpacity={0.4} />
            <Area
              type="monotone"
              dataKey="accuracy"
              stroke="#f43f5e"
              strokeWidth={2}
              fill="url(#accGradient)"
              dot={{ fill: '#f43f5e', r: 3 }}
              activeDot={{ r: 5 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-2 flex items-center justify-between text-[10px] text-muted-foreground">
        <span className="flex items-center gap-1">
          <Calendar className="h-3 w-3" />
          {chartData.length} 次测验
        </span>
        <span>虚线 = 及格线 60%</span>
      </div>
    </Card>
  )
}
