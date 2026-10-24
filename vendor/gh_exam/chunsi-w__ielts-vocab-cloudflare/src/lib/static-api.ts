/**
 * Static data client for Cloudflare Pages deployment.
 * Fetches pre-built JSON files from /data/ instead of API routes.
 * Prioritizes high-frequency letters (A, S, C, P, T) for faster first paint.
 */
import type {
  Stats,
  WordGroup,
  WordListItem,
  WordDetail,
  QuizResponse,
  TestSentence,
} from './types'

async function jsonFetchStatic<T>(path: string): Promise<T> {
  const res = await fetch(path)
  if (!res.ok) throw new Error(`Static fetch ${res.status}: ${path}`)
  return res.json() as Promise<T>
}

// In-memory cache for fetched data
const cache = new Map<string, any>()

async function getCached<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
  if (cache.has(key)) return cache.get(key) as T
  const data = await fetcher()
  cache.set(key, data)
  return data
}

// Progress tracking for word loading
type LoadProgress = { loaded: number; total: number; letters: string[] }
let loadProgress: LoadProgress = { loaded: 0, total: 26, letters: [] }
const progressListeners = new Set<(p: LoadProgress) => void>()

export function onWordLoadProgress(cb: (p: LoadProgress) => void): () => void {
  progressListeners.add(cb)
  return () => progressListeners.delete(cb)
}

function updateProgress(loaded: number, letter: string) {
  loadProgress = { ...loadProgress, loaded, letters: [...loadProgress.letters, letter] }
  progressListeners.forEach((cb) => cb(loadProgress))
}

// Letters sorted by frequency (A, S, C, P, T, R, B, M, D, I, E, N, O, L, F, G, H, U, W, V, Y, K, J, X, Z, Q)
const LETTER_PRIORITY = 'ASCPTPBMDIENOLF' .split('').filter((l, i, arr) => arr.indexOf(l) === i)
const ALL_LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')

// All words loaded from letter chunks (progressive)
let allWordsCache: WordListItem[] | null = null
let loadingPromise: Promise<WordListItem[]> | null = null

async function loadAllWords(): Promise<WordListItem[]> {
  if (allWordsCache) return allWordsCache
  if (loadingPromise) return loadingPromise

  loadingPromise = (async () => {
    const results: WordListItem[] = []
    let loaded = 0

    // Load in priority order (high-frequency letters first)
    for (const letter of ALL_LETTERS) {
      try {
        const words = await jsonFetchStatic<WordListItem[]>(`/data/words-${letter}.json`)
        results.push(...words)
        loaded++
        updateProgress(loaded, letter)
      } catch (e) {
        console.warn(`Failed to load words-${letter}.json:`, e)
        loaded++
        updateProgress(loaded, letter)
      }
    }

    allWordsCache = results
    return results
  })()

  return loadingPromise
}

// Get words that are already loaded (non-blocking, for progressive UI)
function getLoadedWords(): WordListItem[] {
  return cache.get('loadedWords') || []
}

// Preload high-frequency letters (A, S, C, P, T) for faster first paint
export async function preloadHighFreqWords(): Promise<void> {
  const priority = ['A', 'S', 'C', 'P', 'T']
  await Promise.all(
    priority.map(async (letter) => {
      if (!cache.has(`words-${letter}`)) {
        try {
          const words = await jsonFetchStatic<WordListItem[]>(`/data/words-${letter}.json`)
          cache.set(`words-${letter}`, words)
        } catch {}
      }
    }),
  )
}

export const staticApi = {
  stats: async () => {
    return getCached<Stats>('stats', () => jsonFetchStatic('/data/stats.json'))
  },

  groups: async () => {
    return getCached<WordGroup[]>('groups', () => jsonFetchStatic('/data/groups.json'))
  },

  words: async (params: {
    page?: number
    pageSize?: number
    groupId?: number | null
    firstLetter?: string | null
    search?: string
    sort?: string
  }) => {
    const all = await loadAllWords()
    let filtered = [...all]

    if (params.groupId) filtered = filtered.filter((w) => w.groupId === params.groupId)
    if (params.firstLetter) filtered = filtered.filter((w) => w.firstLetter === params.firstLetter)
    if (params.search) {
      const q = params.search.toLowerCase()
      filtered = filtered.filter(
        (w) =>
          w.word.toLowerCase().includes(q) ||
          w.translation.includes(q) ||
          (w.englishDefinition || '').toLowerCase().includes(q),
      )
    }

    const sort = params.sort || 'occurrences_desc'
    if (sort === 'occurrences_desc') filtered.sort((a, b) => b.occurrences - a.occurrences)
    else if (sort === 'occurrences_asc') filtered.sort((a, b) => a.occurrences - b.occurrences)
    else if (sort === 'word_asc') filtered.sort((a, b) => a.word.localeCompare(b.word))
    else if (sort === 'word_desc') filtered.sort((a, b) => b.word.localeCompare(a.word))

    const page = params.page || 1
    const pageSize = params.pageSize || 24
    const total = filtered.length
    const start = (page - 1) * pageSize
    const words = filtered.slice(start, start + pageSize)

    return {
      page,
      pageSize,
      total,
      totalPages: Math.ceil(total / pageSize),
      words,
    }
  },

  wordById: async (id: number) => {
    const all = await loadAllWords()
    const word = all.find((w) => w.id === id)
    if (!word) throw new Error('Word not found')

    // Load sentences for this word
    const chunkIdx = Math.floor((id - 1) / 1000)
    const sentences = await getCached(`sentences-${chunkIdx}`, () =>
      jsonFetchStatic<TestSentence[]>(`/data/sentences-${chunkIdx}.json`),
    )
    const wordSentences = sentences.filter((s) => s.wordId === id)

    return {
      ...word,
      group: {
        id: word.groupId,
        name: word.groupName,
        rank: word.groupRank,
        minOccur: 0,
        maxOccur: 0,
      },
      testSentences: wordSentences,
    } as WordDetail
  },

  relatedWords: async (id: number, limit?: number) => {
    const all = await loadAllWords()
    const word = all.find((w) => w.id === id)
    if (!word) return { words: [] }

    const tolerance = 3
    const results: WordListItem[] = []
    const usedIds = new Set<number>([id])

    // Batch 1: same first letter + similar length
    for (const w of all) {
      if (results.length >= (limit || 6)) break
      if (usedIds.has(w.id)) continue
      if (w.firstLetter === word.firstLetter && Math.abs(w.length - word.length) <= tolerance) {
        results.push(w)
        usedIds.add(w.id)
      }
    }
    // Batch 2: same first letter
    for (const w of all) {
      if (results.length >= (limit || 6)) break
      if (usedIds.has(w.id)) continue
      if (w.firstLetter === word.firstLetter) {
        results.push(w)
        usedIds.add(w.id)
      }
    }
    // Batch 3: similar length
    for (const w of all) {
      if (results.length >= (limit || 6)) break
      if (usedIds.has(w.id)) continue
      if (Math.abs(w.length - word.length) <= tolerance) {
        results.push(w)
        usedIds.add(w.id)
      }
    }
    return { words: results }
  },

  randomWords: async (params: { count?: number; groupId?: number | null; excludeIds?: number[] }) => {
    const all = await loadAllWords()
    let pool = all
    if (params.groupId) pool = pool.filter((w) => w.groupId === params.groupId)
    if (params.excludeIds?.length) pool = pool.filter((w) => !params.excludeIds!.includes(w.id))

    const count = params.count || 1
    const results: WordListItem[] = []
    const used = new Set<number>()
    for (let i = 0; i < count && pool.length > 0; i++) {
      const idx = Math.floor(Math.random() * pool.length)
      const w = pool[idx]
      if (!used.has(w.id)) {
        results.push(w)
        used.add(w.id)
      }
    }
    return { words: results }
  },

  wordsByIds: async (ids: number[]) => {
    const all = await loadAllWords()
    const map = new Map(all.map((w) => [w.id, w]))
    return { words: ids.map((id) => map.get(id)).filter(Boolean) as WordListItem[] }
  },

  search: async (q: string, limit?: number) => {
    const all = await loadAllWords()
    const ql = q.toLowerCase()
    const results = all
      .filter(
        (w) => w.word.toLowerCase().includes(ql) || w.translation.includes(q),
      )
      .slice(0, limit || 10)
    return { results }
  },

  quiz: async (params: { count?: number; groupId?: number | null; mode?: string; difficulty?: string; focusWordIds?: number[] }) => {
    const all = await loadAllWords()
    const count = Math.min(20, Math.max(3, params.count || 10))
    const mode = params.mode || 'en_to_zh'
    const difficulty = params.difficulty || 'adaptive'

    let pool = all.filter((w) => w.translation && w.translation !== '')
    if (params.groupId) {
      pool = pool.filter((w) => w.groupId === params.groupId)
    } else if (difficulty === 'easy') {
      pool = pool.filter((w) => [1, 2].includes(w.groupId))
    } else if (difficulty === 'medium') {
      pool = pool.filter((w) => [3, 4].includes(w.groupId))
    } else if (difficulty === 'hard') {
      pool = pool.filter((w) => [5, 6].includes(w.groupId))
    }

    // pick random words
    const picked: WordListItem[] = []
    const used = new Set<number>()
    while (picked.length < count && pool.length > 0) {
      const idx = Math.floor(Math.random() * pool.length)
      const w = pool[idx]
      if (!used.has(w.id)) {
        picked.push(w)
        used.add(w.id)
      }
    }

    // generate questions with distractors
    const questions = picked.map((w) => {
      // pick 3 distractors
      const distractors: WordListItem[] = []
      const dUsed = new Set<number>([w.id])
      // prefer same first letter
      const sameLetter = pool.filter((x) => x.firstLetter === w.firstLetter && !dUsed.has(x.id))
      for (let i = 0; i < 2 && sameLetter.length > 0; i++) {
        const idx = Math.floor(Math.random() * sameLetter.length)
        const d = sameLetter[idx]
        if (d && !dUsed.has(d.id)) {
          distractors.push(d)
          dUsed.add(d.id)
          sameLetter.splice(idx, 1)
        }
      }
      // fill with random
      while (distractors.length < 3 && pool.length > 0) {
        const idx = Math.floor(Math.random() * pool.length)
        const d = pool[idx]
        if (d && !dUsed.has(d.id)) {
          distractors.push(d)
          dUsed.add(d.id)
        }
      }

      const options = [...distractors, w]
      // shuffle
      for (let i = options.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1))
        ;[options[i], options[j]] = [options[j], options[i]]
      }

      let prompt = ''
      let promptTranslation = ''
      let answerIndex = -1
      let optionTexts: string[] = []

      if (mode === 'en_to_zh') {
        prompt = w.word
        promptTranslation = w.phonetic || ''
        optionTexts = options.map((o) => o.translation)
        answerIndex = options.findIndex((o) => o.id === w.id)
      } else if (mode === 'zh_to_en') {
        prompt = w.translation
        optionTexts = options.map((o) => o.word)
        answerIndex = options.findIndex((o) => o.id === w.id)
      } else {
        prompt = w.word
        promptTranslation = w.translation
        optionTexts = options.map((o) => o.exampleEn || o.translation)
        answerIndex = options.findIndex((o) => o.id === w.id)
      }

      return {
        wordId: w.id,
        word: w.word,
        mode,
        prompt,
        promptTranslation,
        options: optionTexts,
        answerIndex,
        explanation: {
          word: w.word,
          translation: w.translation,
          phonetic: w.phonetic || '',
          exampleEn: w.exampleEn || '',
          exampleZh: w.exampleZh || '',
        },
      }
    })

    return { mode, count: questions.length, questions } as QuizResponse
  },

  spellingQuiz: async (params: { count?: number; groupId?: number | null; hint?: string }) => {
    const all = await loadAllWords()
    const count = Math.min(20, Math.max(3, params.count || 10))
    const hint = params.hint || 'translation'

    let pool = all.filter(
      (w) => w.word && w.translation && !w.word.includes(' ') && w.length <= 20,
    )
    if (params.groupId) pool = pool.filter((w) => w.groupId === params.groupId)

    const picked: WordListItem[] = []
    const used = new Set<number>()
    while (picked.length < count && pool.length > 0) {
      const idx = Math.floor(Math.random() * pool.length)
      const w = pool[idx]
      if (!used.has(w.id)) {
        picked.push(w)
        used.add(w.id)
      }
    }

    return {
      mode: 'spelling' as const,
      hint,
      count: picked.length,
      questions: picked.map((w) => ({
        wordId: w.id,
        word: w.word,
        phonetic: w.phonetic || '',
        translation: w.translation,
        audioUk: w.audioUk,
        audioUs: w.audioUs,
        exampleEn: w.exampleEn || '',
        exampleZh: w.exampleZh || '',
        hint,
      })),
    }
  },

  clozeQuiz: async (params: { count?: number; groupId?: number | null }) => {
    // Load all sentences
    const all = await loadAllWords()
    const count = Math.min(20, Math.max(3, params.count || 10))

    // Words with sentences - need to check sentenceCount
    let pool = all.filter((w) => w.sentenceCount > 0)
    if (params.groupId) pool = pool.filter((w) => w.groupId === params.groupId)

    const picked: WordListItem[] = []
    const used = new Set<number>()
    while (picked.length < count && pool.length > 0) {
      const idx = Math.floor(Math.random() * pool.length)
      const w = pool[idx]
      if (!used.has(w.id)) {
        picked.push(w)
        used.add(w.id)
      }
    }

    // Load sentences for picked words
    const questions = await Promise.all(
      picked.map(async (w) => {
        const chunkIdx = Math.floor((w.id - 1) / 1000)
        const sentences = await getCached(`sentences-${chunkIdx}`, () =>
          jsonFetchStatic<TestSentence[]>(`/data/sentences-${chunkIdx}.json`),
        )
        const wordSentences = sentences.filter((s) => s.wordId === w.id)
        const ts = wordSentences[0]
        if (!ts) return null

        const form = ts.form || w.word
        const sentence = ts.sentence
        const formLower = form.toLowerCase()
        const sentenceLower = sentence.toLowerCase()
        const idx = sentenceLower.indexOf(formLower)

        let blanked = sentence
        let displayWord = form
        if (idx >= 0) {
          blanked = sentence.slice(0, idx) + '_____'.padEnd(Math.max(5, form.length), '_') + sentence.slice(idx + form.length)
          displayWord = sentence.slice(idx, idx + form.length)
        }

        return {
          wordId: w.id,
          word: w.word,
          form: displayWord,
          sentence: blanked,
          originalSentence: sentence,
          source: ts.source,
          location: ts.location,
          translation: w.translation,
          phonetic: w.phonetic || '',
          groupName: w.groupName,
          hint: `${displayWord[0]?.toUpperCase() || ''}${'_'.repeat(Math.max(0, displayWord.length - 1))}`,
          length: displayWord.length,
        }
      }),
    )

    return {
      mode: 'cloze' as const,
      count: questions.filter(Boolean).length,
      questions: questions.filter(Boolean) as any[],
    }
  },

  reviewDue: async (ids: number[]) => {
    const all = await loadAllWords()
    const map = new Map(all.map((w) => [w.id, w]))
    return { words: ids.map((id) => map.get(id)).filter(Boolean) as WordListItem[] }
  },
}
