import { describe, expect, it, vi } from 'vitest'
import {
  PROGRESS_STORAGE_KEY,
  createDefaultProgress,
  getVocabularyStatus,
  loadProgress,
  markGrammarCompleted,
  markReadingCompleted,
  resetProgress,
  reviewVocabularyWord,
  updateVocabularyProgress,
} from './progress'

describe('progress model', () => {
  it('recovers from malformed storage', () => {
    const storage = { getItem: () => '{not-json' }
    expect(loadProgress(storage).version).toBe(1)
    expect(loadProgress(storage).grammar).toEqual({})
  })

  it('merges partial settings with defaults', () => {
    const storage = { getItem: () => JSON.stringify({ preferences: { grammarLevel: 'middle' } }) }
    const progress = loadProgress(storage)
    expect(progress.preferences.grammarLevel).toBe('middle')
    expect(progress.preferences.vocabularyLevel).toBe('basic')
  })

  it('records grammar completion without mutating prior state', () => {
    const initial = createDefaultProgress()
    const now = new Date(2026, 6, 11)
    const next = markGrammarCompleted(initial, 'g-basic-01', true, now)
    expect(initial.grammar).toEqual({})
    expect(next.grammar['g-basic-01']).toEqual({ completed: true, attempts: 1, correct: 1, completedAt: now.toISOString() })
    expect(next.activityDates).toEqual(['2026-07-11'])
  })

  it('schedules a correct word further into the future', () => {
    const next = updateVocabularyProgress(createDefaultProgress(), 'w0001', true, {
      now: new Date(2026, 6, 11, 10),
    })
    expect(next.vocabulary.w0001.stage).toBe(1)
    expect(next.vocabulary.w0001.dueAt).toBe('2026-07-12')
  })

  it('records reading completion', () => {
    const now = new Date(2026, 6, 11)
    const next = markReadingCompleted(
      createDefaultProgress(),
      'r-one',
      'answer',
      ['w0001'],
      now,
    )
    expect(next.reading['r-one']).toEqual({ completed: true, answer: 'answer', savedWords: ['w0001'], completedAt: now.toISOString() })
  })

  it('schedules vocabulary from honest recall ratings', () => {
    const now = new Date(2026, 6, 11, 9)
    const known = reviewVocabularyWord(createDefaultProgress(), 'w0001', 'known', { now })
    const fuzzy = reviewVocabularyWord(known, 'w0001', 'fuzzy', { now })
    const forgot = reviewVocabularyWord(fuzzy, 'w0001', 'forgot', { now })

    expect(known.vocabulary.w0001).toMatchObject({ stage: 1, seen: 1, correct: 1, dueAt: '2026-07-12', lastRating: 'known' })
    expect(fuzzy.vocabulary.w0001).toMatchObject({ stage: 1, seen: 2, correct: 1, dueAt: '2026-07-12', lastRating: 'fuzzy' })
    expect(forgot.vocabulary.w0001).toMatchObject({ stage: 0, seen: 3, correct: 1, dueAt: '2026-07-12', lastRating: 'forgot', lapses: 1 })
  })

  it('distinguishes new, due, learning, and mastered words', () => {
    const now = new Date(2026, 6, 11, 9)
    expect(getVocabularyStatus(undefined, now)).toBe('new')
    expect(getVocabularyStatus({ stage: 2, seen: 2, correct: 1, dueAt: '2026-07-11', saved: false, lastSeenAt: now.toISOString() }, now)).toBe('due')
    expect(getVocabularyStatus({ stage: 2, seen: 2, correct: 2, dueAt: '2026-07-14', saved: false, lastSeenAt: now.toISOString() }, now)).toBe('learning')
    expect(getVocabularyStatus({ stage: 4, seen: 5, correct: 5, dueAt: '2026-07-25', saved: false, lastSeenAt: now.toISOString() }, now)).toBe('mastered')
  })

  it('removes persisted progress when reset', () => {
    const removeItem = vi.fn()
    const progress = resetProgress({ removeItem })
    expect(removeItem).toHaveBeenCalledWith(PROGRESS_STORAGE_KEY)
    expect(progress).toEqual(createDefaultProgress())
  })
})
