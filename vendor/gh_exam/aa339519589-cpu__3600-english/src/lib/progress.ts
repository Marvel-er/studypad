import type { AppProgress, Level, ReviewRating, Section, VocabularyProgress } from '../types'

export const PROGRESS_STORAGE_KEY = 'stillword:v1'
const REVIEW_INTERVALS = [1, 1, 3, 7, 14, 30]
const LEVELS: Level[] = ['basic', 'middle', 'advanced']
const SECTIONS: Section[] = ['today', 'grammar', 'vocabulary', 'reading']

export function toDateKey(date = new Date()): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export function createDefaultProgress(): AppProgress {
  return {
    version: 1,
    preferences: {
      grammarLevel: 'basic',
      grammarStage: 1,
      vocabularyLevel: 'basic',
      dailyMinutes: 15,
    },
    activityDates: [],
    grammar: {},
    vocabulary: {},
    reading: {},
    resume: { section: 'today' },
  }
}

export const DEFAULT_PROGRESS = createDefaultProgress()

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value)
}

function safeLevel(value: unknown, fallback: Level): Level {
  return LEVELS.includes(value as Level) ? (value as Level) : fallback
}

export function mergeProgress(value: unknown): AppProgress {
  const defaults = createDefaultProgress()
  if (!isRecord(value)) return defaults
  const preferences = isRecord(value.preferences) ? value.preferences : {}
  const resume = isRecord(value.resume) ? value.resume : {}

  return {
    version: 1,
    preferences: {
      grammarLevel: safeLevel(preferences.grammarLevel, defaults.preferences.grammarLevel),
      grammarStage:
        typeof preferences.grammarStage === 'number' && preferences.grammarStage >= 1 && preferences.grammarStage <= 6
          ? preferences.grammarStage
          : defaults.preferences.grammarStage,
      vocabularyLevel: safeLevel(preferences.vocabularyLevel, defaults.preferences.vocabularyLevel),
      dailyMinutes:
        typeof preferences.dailyMinutes === 'number' && preferences.dailyMinutes > 0
          ? preferences.dailyMinutes
          : defaults.preferences.dailyMinutes,
    },
    activityDates: Array.isArray(value.activityDates)
      ? value.activityDates.filter((date): date is string => typeof date === 'string')
      : [],
    grammar: isRecord(value.grammar) ? (value.grammar as AppProgress['grammar']) : {},
    vocabulary: isRecord(value.vocabulary) ? (value.vocabulary as AppProgress['vocabulary']) : {},
    reading: isRecord(value.reading) ? (value.reading as AppProgress['reading']) : {},
    resume: {
      section: SECTIONS.includes(resume.section as Section) ? (resume.section as Section) : 'today',
      itemId: typeof resume.itemId === 'string' ? resume.itemId : undefined,
    },
  }
}

export function loadProgress(storage?: Pick<Storage, 'getItem'>): AppProgress {
  try {
    const target = storage ?? window.localStorage
    const raw = target.getItem(PROGRESS_STORAGE_KEY)
    return raw ? mergeProgress(JSON.parse(raw)) : createDefaultProgress()
  } catch {
    return createDefaultProgress()
  }
}

export function saveProgress(progress: AppProgress, storage?: Pick<Storage, 'setItem'>): void {
  try {
    const target = storage ?? window.localStorage
    target.setItem(PROGRESS_STORAGE_KEY, JSON.stringify(progress))
  } catch {
    // Learning remains usable when storage is blocked or full.
  }
}

function withActivityDate(progress: AppProgress, now: Date): string[] {
  const date = toDateKey(now)
  return progress.activityDates.includes(date) ? progress.activityDates : [...progress.activityDates, date]
}

export function markGrammarCompleted(
  progress: AppProgress,
  id: string,
  correct = true,
  now = new Date(),
): AppProgress {
  const previous = progress.grammar[id] ?? { completed: false, attempts: 0, correct: 0 }
  return {
    ...progress,
    activityDates: withActivityDate(progress, now),
    grammar: {
      ...progress.grammar,
      [id]: {
        completed: true,
        attempts: previous.attempts + 1,
        correct: previous.correct + (correct ? 1 : 0),
        completedAt: now.toISOString(),
      },
    },
    resume: { section: 'grammar', itemId: id },
  }
}

export function updateVocabularyProgress(
  progress: AppProgress,
  id: string,
  correct: boolean,
  options: { saved?: boolean; now?: Date } = {},
): AppProgress {
  return reviewVocabularyWord(progress, id, correct ? 'known' : 'forgot', options)
}

export function reviewVocabularyWord(
  progress: AppProgress,
  id: string,
  rating: ReviewRating,
  options: { saved?: boolean; now?: Date } = {},
): AppProgress {
  const now = options.now ?? new Date()
  const previous = progress.vocabulary[id] ?? {
    stage: 0,
    seen: 0,
    correct: 0,
    dueAt: toDateKey(now),
    saved: false,
    lastSeenAt: now.toISOString(),
  }
  const stage = rating === 'known'
    ? Math.min(5, previous.stage + 1)
    : rating === 'fuzzy'
      ? Math.max(0, previous.stage)
      : Math.max(0, previous.stage - 1)
  const due = new Date(now)
  due.setDate(due.getDate() + REVIEW_INTERVALS[stage])

  return {
    ...progress,
    activityDates: withActivityDate(progress, now),
    vocabulary: {
      ...progress.vocabulary,
      [id]: {
        stage,
        seen: previous.seen + 1,
        correct: previous.correct + (rating === 'known' ? 1 : 0),
        dueAt: toDateKey(due),
        saved: options.saved ?? previous.saved,
        lastSeenAt: now.toISOString(),
        lastRating: rating,
        lapses: (previous.lapses ?? 0) + (rating === 'forgot' ? 1 : 0),
      },
    },
    resume: { section: 'vocabulary', itemId: id },
  }
}

export type VocabularyStatus = 'new' | 'learning' | 'due' | 'mastered'

export function getVocabularyStatus(state?: VocabularyProgress, now = new Date()): VocabularyStatus {
  if (!state || state.seen === 0) return 'new'
  if (state.dueAt <= toDateKey(now)) return 'due'
  return state.stage >= 4 ? 'mastered' : 'learning'
}

export function toggleSavedWord(progress: AppProgress, id: string, now = new Date()): AppProgress {
  const previous = progress.vocabulary[id] ?? {
    stage: 0,
    seen: 0,
    correct: 0,
    dueAt: toDateKey(now),
    saved: false,
    lastSeenAt: now.toISOString(),
  }
  return {
    ...progress,
    vocabulary: {
      ...progress.vocabulary,
      [id]: { ...previous, saved: !previous.saved },
    },
  }
}

export function markReadingCompleted(
  progress: AppProgress,
  id: string,
  answer: string,
  savedWords: string[] = [],
  now = new Date(),
): AppProgress {
  return {
    ...progress,
    activityDates: withActivityDate(progress, now),
    reading: {
      ...progress.reading,
      [id]: { completed: true, answer, savedWords, completedAt: now.toISOString() },
    },
    resume: { section: 'reading', itemId: id },
  }
}

export function resetProgress(storage?: Pick<Storage, 'removeItem'>): AppProgress {
  try {
    const target = storage ?? window.localStorage
    target.removeItem(PROGRESS_STORAGE_KEY)
  } catch {
    // Returning a fresh state is sufficient when storage is unavailable.
  }
  return createDefaultProgress()
}
