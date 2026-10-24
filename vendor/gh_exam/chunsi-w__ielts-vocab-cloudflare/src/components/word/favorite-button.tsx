'use client'

import { Star } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useProgressStore } from '@/store/progress'
import { Button } from '@/components/ui/button'

interface FavoriteButtonProps {
  wordId: number
  size?: 'sm' | 'md' | 'lg' | 'icon'
  variant?: 'default' | 'ghost' | 'outline'
  className?: string
}

export function FavoriteButton({
  wordId,
  size = 'icon',
  variant = 'ghost',
  className,
}: FavoriteButtonProps) {
  const favorite = useProgressStore((s) => s.progress[wordId]?.favorite ?? false)
  const toggle = useProgressStore((s) => s.toggleFavorite)

  return (
    <Button
      type="button"
      variant={variant}
      size={size}
      onClick={(e) => {
        e.stopPropagation()
        e.preventDefault()
        toggle(wordId)
      }}
      className={cn(className)}
      aria-label={favorite ? '取消收藏' : '收藏单词'}
      title={favorite ? '取消收藏' : '收藏单词'}
    >
      <Star
        className={cn(
          'h-4 w-4 transition-colors',
          favorite ? 'fill-amber-400 text-amber-400' : 'text-muted-foreground',
        )}
      />
    </Button>
  )
}
