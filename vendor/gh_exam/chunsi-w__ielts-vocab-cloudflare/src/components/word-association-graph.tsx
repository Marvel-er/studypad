'use client'

import { useEffect, useState, useMemo } from 'react'
import { Network, Loader2, ArrowRight } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { api } from '@/lib/api'
import { useUIStore } from '@/store/ui'
import type { WordListItem } from '@/lib/types'
import { cn } from '@/lib/utils'

interface WordAssociationGraphProps {
  wordId: number
  word: string
  firstLetter: string
  length: number
  groupId: number
  groupName: string
}

interface RelatedNode {
  word: WordListItem
  relation: 'same-letter' | 'same-length' | 'same-group'
  relationLabel: string
}

const relationColors: Record<string, string> = {
  'same-letter': '#f43f5e', // rose
  'same-length': '#f97316', // orange
  'same-group': '#22c55e', // green
}

const relationLabels: Record<string, string> = {
  'same-letter': '同首字母',
  'same-length': '同长度',
  'same-group': '同词频组',
}

export function WordAssociationGraph({
  wordId,
  word,
  firstLetter,
  length,
  groupId,
  groupName,
}: WordAssociationGraphProps) {
  const [related, setRelated] = useState<WordListItem[]>([])
  const [loading, setLoading] = useState(true)
  const openWord = useUIStore((s) => s.openWord)

  useEffect(() => {
    let active = true
    Promise.resolve().then(() => {
      if (active) setLoading(true)
    })
    api
      .relatedWords(wordId, 8)
      .then((r) => {
        if (active) {
          setRelated(r.words)
          setLoading(false)
        }
      })
      .catch(() => {
        if (active) {
          setRelated([])
          setLoading(false)
        }
      })
    return () => {
      active = false
    }
  }, [wordId])

  // Categorize related words by relation type
  const nodes = useMemo<RelatedNode[]>(() => {
    return related.map((w) => {
      const sameLetter = w.firstLetter === firstLetter
      const sameLength = Math.abs(w.length - length) <= 2
      const sameGroup = w.groupId === groupId
      let relation: RelatedNode['relation'] = 'same-group'
      let relationLabel = relationLabels['same-group']
      if (sameLetter && sameLength) {
        relation = 'same-letter'
        relationLabel = '同首字母+同长度'
      } else if (sameLetter) {
        relation = 'same-letter'
        relationLabel = relationLabels['same-letter']
      } else if (sameLength) {
        relation = 'same-length'
        relationLabel = relationLabels['same-length']
      } else if (sameGroup) {
        relation = 'same-group'
        relationLabel = `${relationLabels['same-group']} ${groupName}`
      }
      return { word: w, relation, relationLabel }
    })
  }, [related, firstLetter, length, groupId, groupName])

  if (!loading && related.length === 0) return null

  return (
    <Card className="p-5 sm:p-6">
      <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
        <h2 className="text-base font-semibold flex items-center gap-2">
          <Network className="h-4 w-4 text-primary" />
          单词联想图
        </h2>
        <div className="flex items-center gap-2 flex-wrap">
          {Object.entries(relationLabels).map(([key, label]) => (
            <Badge
              key={key}
              variant="outline"
              className="text-[9px] gap-1 px-1.5 py-0"
            >
              <span
                className="h-2 w-2 rounded-full"
                style={{ backgroundColor: relationColors[key] }}
              />
              {label}
            </Badge>
          ))}
        </div>
      </div>

      {loading ? (
        <Skeleton className="h-64 w-full" />
      ) : (
        <div className="relative">
          {/* Graph visualization */}
          <div className="relative h-64 sm:h-80 flex items-center justify-center">
            {/* SVG connections */}
            <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 0 }}>
              {nodes.map((node, idx) => {
                const angle = (idx / nodes.length) * 2 * Math.PI - Math.PI / 2
                const radius = 38 // percentage
                const x = 50 + radius * Math.cos(angle)
                const y = 50 + radius * Math.sin(angle)
                return (
                  <line
                    key={idx}
                    x1="50%"
                    y1="50%"
                    x2={`${x}%`}
                    y2={`${y}%`}
                    stroke={relationColors[node.relation]}
                    strokeWidth="1.5"
                    strokeOpacity="0.4"
                    strokeDasharray={node.relation === 'same-group' ? '4 2' : undefined}
                  />
                )
              })}
            </svg>

            {/* Center node (current word) */}
            <div
              className="absolute z-10 flex flex-col items-center justify-center"
              style={{ left: '50%', top: '50%', transform: 'translate(-50%, -50%)' }}
            >
              <div className="rounded-xl bg-gradient-to-br from-rose-500 to-orange-500 text-white px-4 py-2.5 shadow-lg min-w-[100px] text-center">
                <div className="text-base font-bold">{word}</div>
                <div className="text-[9px] opacity-80 mt-0.5">{groupName}</div>
              </div>
              <div className="text-[9px] text-muted-foreground mt-1">当前单词</div>
            </div>

            {/* Related nodes positioned radially */}
            {nodes.map((node, idx) => {
              const angle = (idx / nodes.length) * 2 * Math.PI - Math.PI / 2
              const radius = 38
              const x = 50 + radius * Math.cos(angle)
              const y = 50 + radius * Math.sin(angle)
              return (
                <button
                  key={node.word.id}
                  onClick={() => openWord(node.word.id)}
                  className="absolute z-10 group"
                  style={{
                    left: `${x}%`,
                    top: `${y}%`,
                    transform: 'translate(-50%, -50%)',
                  }}
                >
                  <div
                    className="rounded-lg border-2 bg-card px-3 py-1.5 shadow-sm transition-all group-hover:shadow-md group-hover:scale-110 group-hover:-translate-y-0.5 text-center"
                    style={{ borderColor: relationColors[node.relation] }}
                  >
                    <div className="text-xs font-semibold whitespace-nowrap">{node.word.word}</div>
                    <div className="flex items-center justify-center gap-0.5 mt-0.5">
                      <span
                        className="h-1.5 w-1.5 rounded-full"
                        style={{ backgroundColor: relationColors[node.relation] }}
                      />
                      <span className="text-[8px] text-muted-foreground truncate max-w-[60px]">
                        {node.word.occurrences}次
                      </span>
                    </div>
                  </div>
                </button>
              )
            })}
          </div>

          {/* List view (for accessibility / mobile) */}
          <div className="mt-4 pt-3 border-t border-border/60">
            <div className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wide mb-2">
              联想单词列表
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-1.5">
              {nodes.map((node, idx) => (
                <button
                  key={node.word.id}
                  onClick={() => openWord(node.word.id)}
                  className="group text-left rounded-md border p-1.5 transition-all hover:shadow-sm hover:border-primary/40 animate-fade-in-up"
                  style={{ animationDelay: `${idx * 40}ms` }}
                >
                  <div className="flex items-center gap-1">
                    <span
                      className="h-2 w-2 rounded-full shrink-0"
                      style={{ backgroundColor: relationColors[node.relation] }}
                    />
                    <span className="text-xs font-medium truncate">{node.word.word}</span>
                  </div>
                  <div className="text-[9px] text-muted-foreground mt-0.5 truncate">
                    {node.relationLabel}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </Card>
  )
}
