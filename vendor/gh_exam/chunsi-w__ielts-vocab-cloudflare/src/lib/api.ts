/**
 * Centralized fetch helpers for the API.
 * In static mode (NEXT_PUBLIC_STATIC_DATA=true), uses pre-built JSON files.
 */
import type {
  Stats,
  WordGroup,
  WordListItem,
  WordDetail,
  QuizResponse,
} from './types'

export const isStaticMode = process.env.NEXT_PUBLIC_STATIC_DATA === 'true'

async function jsonFetch<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init)
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(`API ${res.status}: ${text || res.statusText}`)
  }
  return res.json() as Promise<T>
}

// Lazy-loaded static API (only used in static mode)
let _staticApi: any = null
let _staticMod: any = null
async function staticApi() {
  if (!_staticApi) {
    _staticMod = await import('./static-api')
    _staticApi = _staticMod.staticApi
  }
  return _staticApi
}

// Re-export progress tracking (only works in static mode)
export async function onWordLoadProgress(cb: (p: { loaded: number; total: number; letters: string[] }) => void): Promise<() => void> {
  if (!isStaticMode) return () => {}
  await staticApi()
  return _staticMod.onWordLoadProgress(cb)
}

export async function preloadHighFreqWords(): Promise<void> {
  if (!isStaticMode) return
  await staticApi()
  return _staticMod.preloadHighFreqWords()
}

export const api = {
  stats: () => (isStaticMode ? staticApi().then((a) => a.stats()) : jsonFetch<Stats>('/api/stats')),
  groups: () => (isStaticMode ? staticApi().then((a) => a.groups()) : jsonFetch<WordGroup[]>('/api/groups')),

  words: (params: {
    page?: number
    pageSize?: number
    groupId?: number | null
    firstLetter?: string | null
    search?: string
    sort?: string
  }) => {
    if (isStaticMode) return staticApi().then((a) => a.words(params))
    const sp = new URLSearchParams()
    if (params.page) sp.set('page', String(params.page))
    if (params.pageSize) sp.set('pageSize', String(params.pageSize))
    if (params.groupId) sp.set('groupId', String(params.groupId))
    if (params.firstLetter) sp.set('firstLetter', params.firstLetter)
    if (params.search) sp.set('search', params.search)
    if (params.sort) sp.set('sort', params.sort)
    return jsonFetch<{
      page: number
      pageSize: number
      total: number
      totalPages: number
      words: WordListItem[]
    }>(`/api/words?${sp.toString()}`)
  },

  wordById: (id: number) => (isStaticMode ? staticApi().then((a) => a.wordById(id)) : jsonFetch<WordDetail>(`/api/words/${id}`)),

  relatedWords: (id: number, limit?: number) => {
    if (isStaticMode) return staticApi().then((a) => a.relatedWords(id, limit))
    const sp = new URLSearchParams()
    if (limit) sp.set('limit', String(limit))
    return jsonFetch<{ words: WordListItem[] }>(`/api/words/${id}/related?${sp.toString()}`)
  },

  randomWords: (params: { count?: number; groupId?: number | null; excludeIds?: number[] }) => {
    if (isStaticMode) return staticApi().then((a) => a.randomWords(params))
    const sp = new URLSearchParams()
    if (params.count) sp.set('count', String(params.count))
    if (params.groupId) sp.set('groupId', String(params.groupId))
    if (params.excludeIds?.length) sp.set('excludeIds', params.excludeIds.join(','))
    return jsonFetch<{ words: WordListItem[] }>(`/api/words/random?${sp.toString()}`)
  },

  wordsByIds: (ids: number[]) =>
    isStaticMode
      ? staticApi().then((a) => a.wordsByIds(ids))
      : jsonFetch<{ words: WordListItem[] }>('/api/words/by-ids', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ids }),
        }),

  search: (q: string, limit?: number) => {
    if (isStaticMode) return staticApi().then((a) => a.search(q, limit))
    const sp = new URLSearchParams()
    sp.set('q', q)
    if (limit) sp.set('limit', String(limit))
    return jsonFetch<{
      results: Array<{
        id: number
        word: string
        translation: string
        phonetic: string | null
        occurrences: number
        groupName: string
        groupRank: number
      }>
    }>(`/api/search?${sp.toString()}`)
  },

  quiz: (params: { count?: number; groupId?: number | null; mode?: string; difficulty?: string; focusWordIds?: number[] }) => {
    if (isStaticMode) return staticApi().then((a) => a.quiz(params))
    const sp = new URLSearchParams()
    if (params.count) sp.set('count', String(params.count))
    if (params.groupId) sp.set('groupId', String(params.groupId))
    if (params.mode) sp.set('mode', params.mode)
    if (params.difficulty) sp.set('difficulty', params.difficulty)
    if (params.focusWordIds?.length) sp.set('focusWordIds', params.focusWordIds.join(','))
    return jsonFetch<QuizResponse>(`/api/quiz?${sp.toString()}`)
  },

  spellingQuiz: (params: { count?: number; groupId?: number | null; hint?: 'phonetic' | 'translation' | 'audio' }) => {
    if (isStaticMode) return staticApi().then((a) => a.spellingQuiz(params))
    const sp = new URLSearchParams()
    if (params.count) sp.set('count', String(params.count))
    if (params.groupId) sp.set('groupId', String(params.groupId))
    if (params.hint) sp.set('hint', params.hint)
    return jsonFetch<{
      mode: 'spelling'
      hint: string
      count: number
      questions: Array<{
        wordId: number
        word: string
        phonetic: string
        translation: string
        audioUk: string | null
        audioUs: string | null
        exampleEn: string
        exampleZh: string
        hint: string
      }>
    }>(`/api/quiz/spelling?${sp.toString()}`)
  },

  clozeQuiz: (params: { count?: number; groupId?: number | null }) => {
    if (isStaticMode) return staticApi().then((a) => a.clozeQuiz(params))
    const sp = new URLSearchParams()
    if (params.count) sp.set('count', String(params.count))
    if (params.groupId) sp.set('groupId', String(params.groupId))
    return jsonFetch<{
      mode: 'cloze'
      count: number
      questions: Array<{
        wordId: number
        word: string
        form: string
        sentence: string
        originalSentence: string
        source: string
        location: string
        translation: string
        phonetic: string
        groupName: string
        hint: string
        length: number
      }>
    }>(`/api/quiz/cloze?${sp.toString()}`)
  },

  reviewDue: (ids: number[]) =>
    isStaticMode
      ? staticApi().then((a) => a.reviewDue(ids))
      : jsonFetch<{ words: WordListItem[] }>('/api/review/due', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ids }),
        }),
}
