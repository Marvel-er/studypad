'use client'

import { useEffect, useRef, useState } from 'react'

interface ConfettiPiece {
  x: number
  y: number
  vx: number
  vy: number
  rotation: number
  rotationSpeed: number
  color: string
  size: number
  shape: 'rect' | 'circle'
  opacity: number
}

const COLORS = [
  '#f43f5e', // rose-500
  '#f97316', // orange-500
  '#eab308', // yellow-500
  '#22c55e', // green-500
  '#06b6d4', // cyan-500
  '#8b5cf6', // violet-500
  '#ec4899', // pink-500
  '#f59e0b', // amber-500
]

interface ConfettiProps {
  /** Trigger confetti burst (change value to re-trigger) */
  trigger: number | string
  /** Duration in ms (default 3000) */
  duration?: number
  /** Number of pieces (default 80) */
  count?: number
}

/**
 * Lightweight canvas-based confetti animation.
 * Renders a fullscreen overlay that auto-dismisses after `duration`.
 */
export function Confetti({ trigger, duration = 3000, count = 80 }: ConfettiProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animationRef = useRef<number | null>(null)
  const piecesRef = useRef<ConfettiPiece[]>([])
  const startTimeRef = useRef<number>(0)
  const [active, setActive] = useState(false)

  useEffect(() => {
    if (trigger === 0 || trigger === '') return
    let cancelled = false
    let resizeHandler: (() => void) | null = null

    // defer to avoid synchronous setState in effect
    Promise.resolve().then(() => {
      if (cancelled) return
      setActive(true)
      startTimeRef.current = Date.now()

      const canvas = canvasRef.current
      if (!canvas) return
      const ctx = canvas.getContext('2d')
      if (!ctx) return

      const resize = () => {
        canvas.width = window.innerWidth
        canvas.height = window.innerHeight
      }
      resize()
      resizeHandler = resize
      window.addEventListener('resize', resize)

      // init pieces - burst from center top
      const cx = canvas.width / 2
      const cy = canvas.height * 0.25
      const pieces: ConfettiPiece[] = []
      for (let i = 0; i < count; i++) {
        const angle = (Math.PI * 2 * i) / count + Math.random() * 0.5
        const speed = 6 + Math.random() * 8
        pieces.push({
          x: cx + (Math.random() - 0.5) * 100,
          y: cy + (Math.random() - 0.5) * 50,
          vx: Math.cos(angle) * speed,
          vy: Math.sin(angle) * speed - 4,
          rotation: Math.random() * Math.PI * 2,
          rotationSpeed: (Math.random() - 0.5) * 0.3,
          color: COLORS[Math.floor(Math.random() * COLORS.length)],
          size: 6 + Math.random() * 8,
          shape: Math.random() > 0.5 ? 'rect' : 'circle',
          opacity: 1,
        })
      }
      piecesRef.current = pieces

      const animate = () => {
        const elapsed = Date.now() - startTimeRef.current
        const progress = elapsed / duration
        ctx.clearRect(0, 0, canvas.width, canvas.height)

        const gravity = 0.25
        const drag = 0.99

        for (const p of pieces) {
          p.vy += gravity
          p.vx *= drag
          p.vy *= drag
          p.x += p.vx
          p.y += p.vy
          p.rotation += p.rotationSpeed
          // fade out in last 30%
          p.opacity = progress > 0.7 ? Math.max(0, 1 - (progress - 0.7) / 0.3) : 1

          ctx.save()
          ctx.globalAlpha = p.opacity
          ctx.translate(p.x, p.y)
          ctx.rotate(p.rotation)
          ctx.fillStyle = p.color
          if (p.shape === 'rect') {
            ctx.fillRect(-p.size / 2, -p.size / 4, p.size, p.size / 2)
          } else {
            ctx.beginPath()
            ctx.arc(0, 0, p.size / 2, 0, Math.PI * 2)
            ctx.fill()
          }
          ctx.restore()
        }

        if (progress < 1) {
          animationRef.current = requestAnimationFrame(animate)
        } else {
          if (!cancelled) setActive(false)
        }
      }
      animationRef.current = requestAnimationFrame(animate)
    })

    return () => {
      cancelled = true
      if (resizeHandler) window.removeEventListener('resize', resizeHandler)
      if (animationRef.current) cancelAnimationFrame(animationRef.current)
    }
  }, [trigger, duration, count])

  if (!active) return null

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 z-[100] pointer-events-none"
      style={{ width: '100vw', height: '100vh' }}
      aria-hidden="true"
    />
  )
}
