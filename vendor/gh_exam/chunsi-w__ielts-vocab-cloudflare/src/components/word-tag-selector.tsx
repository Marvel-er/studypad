'use client'

import { useState, useRef, useMemo } from 'react'
import { Tag, Plus, X, Check } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import { useProgressStore, TAG_COLORS } from '@/store/progress'
import { cn } from '@/lib/utils'

interface WordTagSelectorProps {
  wordId: number
}

export function WordTagSelector({ wordId }: WordTagSelectorProps) {
  const tags = useProgressStore((s) => s.tags)
  // subscribe to whole progress object (stable reference unless changed)
  const progress = useProgressStore((s) => s.progress)
  const wordTags = useMemo(() => progress[wordId]?.tags ?? [], [progress, wordId])
  const toggleWordTag = useProgressStore((s) => s.toggleWordTag)
  const addTag = useProgressStore((s) => s.addTag)
  const removeTag = useProgressStore((s) => s.removeTag)
  const [open, setOpen] = useState(false)
  const [newTagName, setNewTagName] = useState('')
  const [newTagColor, setNewTagColor] = useState(TAG_COLORS[0])
  const inputRef = useRef<HTMLInputElement>(null)

  // Compute tag counts with useMemo (stable)
  const tagCounts = useMemo(() => {
    const counts: Record<string, number> = {}
    for (const p of Object.values(progress)) {
      for (const t of p.tags || []) {
        counts[t] = (counts[t] || 0) + 1
      }
    }
    return counts
  }, [progress])

  const handleAddTag = () => {
    const name = newTagName.trim()
    if (!name) return
    addTag(name, newTagColor)
    // auto-assign to this word
    toggleWordTag(wordId, name)
    setNewTagName('')
    setNewTagColor(TAG_COLORS[(tags.length + 1) % TAG_COLORS.length])
    inputRef.current?.focus()
  }

  const getTagColor = (name: string) => {
    return tags.find((t) => t.name === name)?.color || '#6b7280'
  }

  return (
    <div className="flex items-center gap-2 flex-wrap">
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button variant="outline" size="sm" className="h-7 gap-1 text-xs">
            <Tag className="h-3 w-3" />
            标签
            {wordTags.length > 0 && (
              <Badge variant="secondary" className="ml-1 h-4 px-1 text-[9px]">
                {wordTags.length}
              </Badge>
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-72 p-3" align="start">
          <div className="space-y-3">
            <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
              单词标签
            </div>

            {/* Existing tags */}
            {tags.length > 0 && (
              <div className="space-y-1.5 max-h-40 overflow-y-auto">
                {tags.map((t) => {
                  const active = wordTags.includes(t.name)
                  const count = tagCounts[t.name] || 0
                  return (
                    <div
                      key={t.name}
                      className={cn(
                        'flex items-center gap-2 rounded-md p-1.5 transition-colors cursor-pointer',
                        active ? 'bg-muted' : 'hover:bg-muted/60',
                      )}
                      onClick={() => toggleWordTag(wordId, t.name)}
                    >
                      <span
                        className="h-3 w-3 rounded-full shrink-0"
                        style={{ backgroundColor: t.color }}
                      />
                      <span className="text-xs flex-1">{t.name}</span>
                      <span className="text-[10px] text-muted-foreground">{count}</span>
                      {active && <Check className="h-3 w-3 text-emerald-500" />}
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          if (confirm(`删除标签「${t.name}」？将从此单词及所有其他单词移除。`)) {
                            removeTag(t.name)
                          }
                        }}
                        className="text-muted-foreground hover:text-rose-500"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </div>
                  )
                })}
              </div>
            )}

            {/* Add new tag */}
            <div className="pt-2 border-t border-border/60 space-y-2">
              <div className="text-[10px] text-muted-foreground">创建新标签</div>
              <Input
                ref={inputRef}
                value={newTagName}
                onChange={(e) => setNewTagName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    handleAddTag()
                  }
                }}
                placeholder="标签名，如：写作高频"
                className="h-8 text-xs"
              />
              <div className="flex items-center gap-1.5 flex-wrap">
                {TAG_COLORS.map((c) => (
                  <button
                    key={c}
                    onClick={() => setNewTagColor(c)}
                    className={cn(
                      'h-5 w-5 rounded-full transition-transform',
                      newTagColor === c && 'ring-2 ring-offset-1 ring-offset-background scale-110',
                    )}
                    style={{ backgroundColor: c }}
                    aria-label={`颜色 ${c}`}
                  />
                ))}
              </div>
              <Button size="sm" className="w-full h-7 text-xs" onClick={handleAddTag} disabled={!newTagName.trim()}>
                <Plus className="h-3 w-3 mr-1" />
                创建并添加
              </Button>
            </div>
          </div>
        </PopoverContent>
      </Popover>

      {/* Active tag badges */}
      {wordTags.map((tagName) => (
        <Badge
          key={tagName}
          variant="secondary"
          className="text-[10px] gap-1 pr-1.5"
          style={{
            backgroundColor: `${getTagColor(tagName)}20`,
            color: getTagColor(tagName),
          }}
        >
          {tagName}
          <button
            onClick={() => toggleWordTag(wordId, tagName)}
            className="hover:opacity-70"
          >
            <X className="h-2.5 w-2.5" />
          </button>
        </Badge>
      ))}
    </div>
  )
}
