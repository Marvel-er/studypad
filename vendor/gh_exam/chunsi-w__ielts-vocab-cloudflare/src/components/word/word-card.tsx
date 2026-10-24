'use client'

import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { FavoriteButton } from './favorite-button'
import { AudioButton } from './audio-button'
import { useProgressStore } from '@/store/progress'
import { useUIStore } from '@/store/ui'
import type { WordListItem } from '@/lib/types'
import { cn } from '@/lib/utils'

interface WordCardProps {
  word: WordListItem
  onClick?: () => void
}

const groupColors: Record<number, string> = {
  1: 'bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300',
  2: 'bg-orange-100 text-orange-700 dark:bg-orange-950 dark:text-orange-300',
  3: 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300',
  4: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300',
  5: 'bg-teal-100 text-teal-700 dark:bg-teal-950 dark:text-teal-300',
}

const masteryColors = [
  'bg-muted text-muted-foreground',
  'bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300',
  'bg-orange-100 text-orange-700 dark:bg-orange-950 dark:text-orange-300',
  'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300',
  'bg-lime-100 text-lime-700 dark:bg-lime-950 dark:text-lime-300',
  'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300',
]

export function WordCard({ word, onClick }: WordCardProps) {
  const openWord = useUIStore((s) => s.openWord)
  const mastery = useProgressStore((s) => s.progress[word.id]?.mastery ?? 0)
  const learned = useProgressStore((s) => s.progress[word.id]?.learned ?? false)

  const handleClick = () => {
    // Call the optional onClick callback first (e.g. to save scroll position)
    if (onClick) {
      onClick()
    }
    // Always open the word detail
    openWord(word.id)
  }

  return (
    <Card
      onClick={handleClick}
      className={cn(
        'group relative cursor-pointer p-4 transition-all hover:shadow-md hover:-translate-y-0.5',
        'border-border/60 hover:border-primary/40',
      )}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="font-semibold text-base truncate group-hover:text-primary transition-colors">
              {word.word}
            </h3>
            {word.phonetic && (
              <span className="text-xs text-muted-foreground truncate">
                {word.phonetic}
              </span>
            )}
          </div>
          <p className="mt-1 text-sm text-muted-foreground line-clamp-2 leading-relaxed">
            {word.translation}
          </p>
        </div>
        <FavoriteButton wordId={word.id} />
      </div>

      {word.englishDefinition && (
        <p className="mt-2 text-xs text-muted-foreground/80 italic line-clamp-2">
          {word.englishDefinition}
        </p>
      )}

      <div className="mt-3 flex items-center justify-between gap-2 flex-wrap">
        <div className="flex items-center gap-1.5 flex-wrap">
          <Badge
            variant="secondary"
            className={cn('text-[10px] px-1.5 py-0', groupColors[word.groupId] || groupColors[5])}
          >
            {word.groupName}
          </Badge>
          {learned && (
            <Badge variant="secondary" className="text-[10px] px-1.5 py-0 bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
              已掌握
            </Badge>
          )}
          {!learned && mastery > 0 && (
            <Badge variant="secondary" className={cn('text-[10px] px-1.5 py-0', masteryColors[mastery])}>
              Lv.{mastery}
            </Badge>
          )}
          {word.sentenceCount > 0 && (
            <Badge variant="outline" className="text-[10px] px-1.5 py-0">
              {word.sentenceCount} 例句
            </Badge>
          )}
          <Badge variant="outline" className="text-[10px] px-1.5 py-0">
            出现 {word.occurrences} 次
          </Badge>
        </div>
        <AudioButton url={word.audioUs} accent="us" label="US" size="sm" />
      </div>
    </Card>
  )
}
