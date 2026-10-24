'use client'

import { Volume2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { useAudioPlayer } from '@/hooks/use-audio'

interface AudioButtonProps {
  url?: string | null
  accent?: 'uk' | 'us'
  label?: string
  size?: 'sm' | 'md' | 'icon'
  className?: string
}

export function AudioButton({
  url,
  accent,
  label,
  size = 'icon',
  className,
}: AudioButtonProps) {
  const { play } = useAudioPlayer()
  if (!url) return null
  return (
    <Button
      type="button"
      variant="ghost"
      size={size}
      onClick={(e) => {
        e.stopPropagation()
        e.preventDefault()
        play(url, accent)
      }}
      className={cn('gap-1', className)}
      title={accent === 'uk' ? '英式发音' : '美式发音'}
    >
      <Volume2 className="h-4 w-4" />
      {label && <span className="text-xs">{label}</span>}
    </Button>
  )
}
