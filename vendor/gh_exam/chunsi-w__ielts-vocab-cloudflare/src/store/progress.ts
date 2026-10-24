/**
 * User progress store with localStorage persistence.
 * Tracks: learned words, favorite words, mastery levels, study/quiz stats.
 */
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type MasteryLevel = 0 | 1 | 2 | 3 | 4 | 5 // 0=new, 5=mastered

export interface WordProgress {
  // mastery level
  mastery: MasteryLevel
  // times studied (flashcard flipped)
  studiedCount: number
  // times correct in quiz
  correctCount: number
  // times wrong in quiz
  wrongCount: number
  // last reviewed timestamp (ms)
  lastReviewed: number
  // added to favorites
  favorite: boolean
  // added to learned list (user marked as known)
  learned: boolean
  // custom tags assigned by user (e.g. "难词", "雅思核心")
  tags: string[]
}

interface ProgressState {
  // wordId -> progress
  progress: Record<number, WordProgress>
  // history of quiz sessions: [{ date, total, correct }]
  quizHistory: Array<{ date: number; total: number; correct: number; mode: string; durationMs?: number }>
  // history of study sessions: [{ date, count }]
  studyHistory: Array<{ date: number; count: number }>
  // daily goal settings
  dailyGoal: number // target words per day (default 20)
  // custom tag definitions (user-created)
  tags: Array<{ name: string; color: string; createdAt: number }>
  // settings
  audioAccent: 'uk' | 'us'
  autoPlayAudio: boolean

  // actions
  getProgress: (wordId: number) => WordProgress
  markStudied: (wordId: number) => void
  markCorrect: (wordId: number) => void
  markWrong: (wordId: number) => void
  toggleFavorite: (wordId: number) => void
  toggleLearned: (wordId: number) => void
  setMastery: (wordId: number, m: MasteryLevel) => void
  resetWord: (wordId: number) => void
  recordQuiz: (total: number, correct: number, mode: string, durationMs?: number) => void
  recordStudy: (count: number) => void
  clearAll: () => void
  importProgress: (
    progress: Record<number, WordProgress>,
    quizHistory?: Array<{ date: number; total: number; correct: number; mode: string }>,
    studyHistory?: Array<{ date: number; count: number }>,
  ) => void
  setAudioAccent: (a: 'uk' | 'us') => void
  setAutoPlayAudio: (v: boolean) => void
  // Spaced-repetition review actions (use interval scheduling)
  reviewCorrect: (wordId: number) => void
  reviewWrong: (wordId: number) => void
  recordReviewSession: (count: number) => void
  // Daily goal
  setDailyGoal: (n: number) => void
  // Tags
  addTag: (name: string, color: string) => void
  removeTag: (name: string) => void
  toggleWordTag: (wordId: number, tagName: string) => void
}

const DEFAULT_PROGRESS: WordProgress = {
  mastery: 0,
  studiedCount: 0,
  correctCount: 0,
  wrongCount: 0,
  lastReviewed: 0,
  favorite: false,
  learned: false,
  tags: [],
}

// Preset tag colors for new tags (cycle through)
export const TAG_COLORS = [
  '#f43f5e', // rose
  '#f97316', // orange
  '#eab308', // yellow
  '#22c55e', // green
  '#06b6d4', // cyan
  '#8b5cf6', // violet
  '#ec4899', // pink
  '#6366f1', // indigo
  '#14b8a6', // teal
  '#a855f7', // purple
]

export const useProgressStore = create<ProgressState>()(
  persist(
    (set, get) => ({
      progress: {},
      quizHistory: [],
      studyHistory: [],
      dailyGoal: 20,
      tags: [
        { name: '难词', color: '#f43f5e', createdAt: Date.now() },
        { name: '雅思核心', color: '#f97316', createdAt: Date.now() },
        { name: '易混淆', color: '#8b5cf6', createdAt: Date.now() },
      ],
      audioAccent: 'us',
      autoPlayAudio: false,

      getProgress: (wordId) => {
        const p = get().progress[wordId]
        return p ? { ...DEFAULT_PROGRESS, ...p } : { ...DEFAULT_PROGRESS }
      },

      markStudied: (wordId) =>
        set((state) => {
          const cur = state.progress[wordId] || { ...DEFAULT_PROGRESS }
          return {
            progress: {
              ...state.progress,
              [wordId]: {
                ...cur,
                studiedCount: cur.studiedCount + 1,
                lastReviewed: Date.now(),
                mastery: Math.min(5, Math.max(cur.mastery, 1)) as MasteryLevel,
              },
            },
          }
        }),

      markCorrect: (wordId) =>
        set((state) => {
          const cur = state.progress[wordId] || { ...DEFAULT_PROGRESS }
          const newCorrect = cur.correctCount + 1
          // mastery goes up after 2 consecutive correct
          const newMastery = Math.min(5, Math.max(cur.mastery, Math.floor(newCorrect / 2) + 1)) as MasteryLevel
          return {
            progress: {
              ...state.progress,
              [wordId]: {
                ...cur,
                correctCount: newCorrect,
                lastReviewed: Date.now(),
                mastery: newMastery,
                learned: newMastery >= 4 ? true : cur.learned,
              },
            },
          }
        }),

      markWrong: (wordId) =>
        set((state) => {
          const cur = state.progress[wordId] || { ...DEFAULT_PROGRESS }
          const newMastery = Math.max(0, cur.mastery - 1) as MasteryLevel
          return {
            progress: {
              ...state.progress,
              [wordId]: {
                ...cur,
                wrongCount: cur.wrongCount + 1,
                lastReviewed: Date.now(),
                mastery: newMastery,
              },
            },
          }
        }),

      toggleFavorite: (wordId) =>
        set((state) => {
          const cur = state.progress[wordId] || { ...DEFAULT_PROGRESS }
          return {
            progress: {
              ...state.progress,
              [wordId]: { ...cur, favorite: !cur.favorite },
            },
          }
        }),

      toggleLearned: (wordId) =>
        set((state) => {
          const cur = state.progress[wordId] || { ...DEFAULT_PROGRESS }
          return {
            progress: {
              ...state.progress,
              [wordId]: {
                ...cur,
                learned: !cur.learned,
                mastery: !cur.learned ? 5 : cur.mastery,
              },
            },
          }
        }),

      setMastery: (wordId, m) =>
        set((state) => {
          const cur = state.progress[wordId] || { ...DEFAULT_PROGRESS }
          return {
            progress: {
              ...state.progress,
              [wordId]: { ...cur, mastery: m, lastReviewed: Date.now() },
            },
          }
        }),

      resetWord: (wordId) =>
        set((state) => {
          const { [wordId]: _, ...rest } = state.progress
          return { progress: rest }
        }),

      recordQuiz: (total, correct, mode) =>
        set((state) => ({
          quizHistory: [
            ...state.quizHistory.slice(-99), // keep last 100
            { date: Date.now(), total, correct, mode },
          ],
        })),

      recordStudy: (count) =>
        set((state) => ({
          studyHistory: [
            ...state.studyHistory.slice(-99),
            { date: Date.now(), count },
          ],
        })),

      clearAll: () =>
        set({ progress: {}, quizHistory: [], studyHistory: [], tags: [] }),

      importProgress: (importedProgress, importedQuiz, importedStudy) =>
        set((state) => {
          // Merge progress: take max of mastery/studied/correct/wrong counts; OR favorite/learned; union tags
          const merged = { ...state.progress }
          for (const [k, p] of Object.entries(importedProgress)) {
            const id = parseInt(k, 10)
            const cur = merged[id] || { ...DEFAULT_PROGRESS }
            merged[id] = {
              mastery: Math.max(cur.mastery, p.mastery ?? 0) as MasteryLevel,
              studiedCount: Math.max(cur.studiedCount, p.studiedCount ?? 0),
              correctCount: Math.max(cur.correctCount, p.correctCount ?? 0),
              wrongCount: Math.max(cur.wrongCount, p.wrongCount ?? 0),
              lastReviewed: Math.max(cur.lastReviewed, p.lastReviewed ?? 0),
              favorite: cur.favorite || p.favorite || false,
              learned: cur.learned || p.learned || false,
              tags: Array.from(new Set([...(cur.tags || []), ...(p.tags || [])])),
            }
          }
          return {
            progress: merged,
            quizHistory: importedQuiz && importedQuiz.length > 0 ? importedQuiz : state.quizHistory,
            studyHistory: importedStudy && importedStudy.length > 0 ? importedStudy : state.studyHistory,
          }
        }),

      setAudioAccent: (a) => set({ audioAccent: a }),
      setAutoPlayAudio: (v) => set({ autoPlayAudio: v }),

      setDailyGoal: (n) => set({ dailyGoal: Math.max(5, Math.min(200, n)) }),

      reviewCorrect: (wordId) =>
        set((state) => {
          const cur = state.progress[wordId] || { ...DEFAULT_PROGRESS }
          // bump mastery, schedule next review based on new mastery interval
          const newMastery = Math.min(5, cur.mastery + 1) as MasteryLevel
          const newCorrect = cur.correctCount + 1
          return {
            progress: {
              ...state.progress,
              [wordId]: {
                ...cur,
                mastery: newMastery,
                correctCount: newCorrect,
                lastReviewed: Date.now(),
                studiedCount: cur.studiedCount + 1,
                learned: newMastery >= 5 ? true : cur.learned,
              },
            },
          }
        }),

      reviewWrong: (wordId) =>
        set((state) => {
          const cur = state.progress[wordId] || { ...DEFAULT_PROGRESS }
          // drop mastery, schedule a quick relearn (lastReviewed=now so due in 30min per review.ts)
          const newMastery = Math.max(0, cur.mastery - 1) as MasteryLevel
          return {
            progress: {
              ...state.progress,
              [wordId]: {
                ...cur,
                mastery: newMastery,
                wrongCount: cur.wrongCount + 1,
                lastReviewed: Date.now() - (4 - 0.5) * 60 * 60 * 1000, // due in ~30 min (interval 4h - 3.5h)
                studiedCount: cur.studiedCount + 1,
              },
            },
          }
        }),

      recordReviewSession: (count) =>
        set((state) => ({
          studyHistory: [
            ...state.studyHistory.slice(-99),
            { date: Date.now(), count },
          ],
        })),

      // Tags
      addTag: (name, color) =>
        set((state) => {
          const trimmed = name.trim()
          if (!trimmed) return state
          if (state.tags.find((t) => t.name === trimmed)) return state
          return {
            tags: [...state.tags, { name: trimmed, color, createdAt: Date.now() }],
          }
        }),

      removeTag: (name) =>
        set((state) => {
          // also remove tag from all words
          const newProgress: Record<number, WordProgress> = {}
          for (const [k, p] of Object.entries(state.progress)) {
            newProgress[parseInt(k, 10)] = {
              ...p,
              tags: (p.tags || []).filter((t) => t !== name),
            }
          }
          return {
            tags: state.tags.filter((t) => t.name !== name),
            progress: newProgress,
          }
        }),

      toggleWordTag: (wordId, tagName) =>
        set((state) => {
          const cur = state.progress[wordId] || { ...DEFAULT_PROGRESS }
          const curTags = cur.tags || []
          const has = curTags.includes(tagName)
          return {
            progress: {
              ...state.progress,
              [wordId]: {
                ...cur,
                tags: has ? curTags.filter((t) => t !== tagName) : [...curTags, tagName],
              },
            },
          }
        }),
    }),
    {
      name: 'ielts-vocab-progress-v1',
      version: 1,
    },
  ),
)

// Helper selectors
export const selectFavoriteIds = (state: ProgressState): number[] =>
  Object.entries(state.progress)
    .filter(([, p]) => p.favorite)
    .map(([id]) => parseInt(id, 10))

export const selectLearnedIds = (state: ProgressState): number[] =>
  Object.entries(state.progress)
    .filter(([, p]) => p.learned || p.mastery >= 4)
    .map(([id]) => parseInt(id, 10))

export const selectLearningIds = (state: ProgressState): number[] =>
  Object.entries(state.progress)
    .filter(([, p]) => p.mastery > 0 && p.mastery < 4)
    .map(([id]) => parseInt(id, 10))
