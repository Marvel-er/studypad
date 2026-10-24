/**
 * Spaced repetition (Ebbinghaus) review scheduling helpers.
 *
 * Intervals per mastery level (in hours). After each review:
 *   - Correct: mastery +1 (cap 5), schedule next review at now + interval[newMastery]
 *   - Wrong:   mastery -1 (floor 0), schedule next review at now + 30 min (relearn)
 *   - New word (mastery 0) first seen: schedule at now + 4 hours
 *
 * Intervals grow roughly by 2x each level, approximating the forgetting curve.
 */
import type { WordProgress, MasteryLevel } from '@/store/progress'

// hours per mastery level (0=new, 5=mastered)
export const REVIEW_INTERVAL_HOURS: Record<MasteryLevel, number> = {
  0: 4,      // new: 4 hours
  1: 12,     // 12 hours
  2: 24,     // 1 day
  3: 72,     // 3 days
  4: 168,    // 7 days
  5: 336,    // 14 days (mastered, occasional refresh)
}

// 30 minutes for relearn after a wrong answer (mastery drops to >=0)
const RELEARN_INTERVAL_MS = 30 * 60 * 1000

export interface ReviewStatus {
  due: boolean
  dueAt: number // ms timestamp when next review is due
  overdueMs: number // ms overdue (negative = not yet due)
  intervalHours: number
}

/**
 * Compute review status for a word given its progress.
 * Words with no progress (never seen) are NOT due (they should be learned first).
 */
export function getReviewStatus(progress: WordProgress | undefined, now: number = Date.now()): ReviewStatus | null {
  if (!progress || progress.mastery === 0 && progress.lastReviewed === 0) {
    return null // never seen
  }
  const intervalMs = REVIEW_INTERVAL_HOURS[progress.mastery] * 60 * 60 * 1000
  const dueAt = progress.lastReviewed + intervalMs
  const overdueMs = now - dueAt
  return {
    due: overdueMs >= 0,
    dueAt,
    overdueMs,
    intervalHours: REVIEW_INTERVAL_HOURS[progress.mastery],
  }
}

/**
 * Get list of word IDs that are due for review, sorted by most overdue first.
 */
export function getDueWordIds(
  progress: Record<number, WordProgress>,
  now: number = Date.now(),
): Array<{ id: number; overdueMs: number; mastery: MasteryLevel }> {
  const due: Array<{ id: number; overdueMs: number; mastery: MasteryLevel }> = []
  for (const [idStr, p] of Object.entries(progress)) {
    // skip mastered words that are also flagged learned (already in long-term memory)
    const status = getReviewStatus(p, now)
    if (status && status.due) {
      due.push({ id: parseInt(idStr, 10), overdueMs: status.overdueMs, mastery: p.mastery })
    }
  }
  due.sort((a, b) => b.overdueMs - a.overdueMs)
  return due
}

/**
 * Count of due words + upcoming (due within next 24h) words.
 */
export function getReviewStats(
  progress: Record<number, WordProgress>,
  now: number = Date.now(),
): { dueNow: number; dueIn24h: number; totalLearning: number } {
  let dueNow = 0
  let dueIn24h = 0
  let totalLearning = 0
  const next24h = now + 24 * 60 * 60 * 1000
  for (const p of Object.values(progress)) {
    const status = getReviewStatus(p, now)
    if (!status) continue
    if (p.mastery > 0 && p.mastery < 5) totalLearning++
    if (status.due) {
      dueNow++
    } else if (status.dueAt <= next24h) {
      dueIn24h++
    }
  }
  return { dueNow, dueIn24h, totalLearning }
}

/**
 * Mark a word as reviewed (correct) — bump mastery and schedule next.
 * Returns the new mastery level.
 */
export function computeCorrectMastery(current: MasteryLevel): MasteryLevel {
  return Math.min(5, current + 1) as MasteryLevel
}

/**
 * Mark a word as reviewed (wrong) — drop mastery and schedule a quick relearn.
 */
export function computeWrongMastery(current: MasteryLevel): MasteryLevel {
  return Math.max(0, current - 1) as MasteryLevel
}

export { RELEARN_INTERVAL_MS }
