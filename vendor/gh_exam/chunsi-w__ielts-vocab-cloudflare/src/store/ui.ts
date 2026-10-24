/**
 * UI view state - which tab/section is currently shown.
 * Since we only have one route (/), this controls view switching.
 * Syncs to URL hash so browser back/forward works and state persists on reload.
 */
import { create } from 'zustand'

export type ViewName = 'home' | 'browse' | 'study' | 'quiz' | 'spelling' | 'cloze' | 'review' | 'favorites' | 'settings' | 'word'

interface UIState {
  view: ViewName
  // for word detail view
  selectedWordId: number | null
  // for browse filters persistence
  browseGroupId: number | null
  browseLetter: string | null
  browseSearch: string
  // for study session config
  studyGroupId: number | null
  // for quiz config
  quizMode: 'en_to_zh' | 'zh_to_en' | 'en_to_sentence'
  quizGroupId: number | null
  quizCount: number

  setView: (v: ViewName) => void
  openWord: (id: number) => void
  setBrowseFilters: (f: Partial<Pick<UIState, 'browseGroupId' | 'browseLetter' | 'browseSearch'>>) => void
  setStudyGroup: (g: number | null) => void
  setQuizConfig: (f: Partial<Pick<UIState, 'quizMode' | 'quizGroupId' | 'quizCount'>>) => void
}

// Parse current URL hash into view state
function parseHash(): { view: ViewName; selectedWordId: number | null } {
  if (typeof window === 'undefined') {
    return { view: 'home', selectedWordId: null }
  }
  const hash = window.location.hash.replace(/^#/, '')
  if (!hash) return { view: 'home', selectedWordId: null }
  // formats: #word/123, #browse, #study, etc.
  const parts = hash.split('/')
  const viewName = parts[0] as ViewName
  const validViews: ViewName[] = ['home', 'browse', 'study', 'quiz', 'spelling', 'cloze', 'review', 'favorites', 'settings', 'word']
  if (!validViews.includes(viewName)) return { view: 'home', selectedWordId: null }
  const selectedWordId = viewName === 'word' && parts[1] ? parseInt(parts[1], 10) : null
  return { view: viewName, selectedWordId: Number.isNaN(selectedWordId as number) ? null : selectedWordId }
}

// Build URL hash from view state
function buildHash(view: ViewName, selectedWordId: number | null): string {
  if (view === 'word' && selectedWordId) {
    return `#word/${selectedWordId}`
  }
  return `#${view}`
}

const initial = parseHash()

export const useUIStore = create<UIState>((set, get) => ({
  view: initial.view,
  selectedWordId: initial.selectedWordId,
  browseGroupId: null,
  browseLetter: null,
  browseSearch: '',
  studyGroupId: null,
  quizMode: 'en_to_zh',
  quizGroupId: null,
  quizCount: 10,

  setView: (v) => {
    set({ view: v })
    // push to URL history so browser back works
    if (typeof window !== 'undefined') {
      const state = get()
      const newHash = buildHash(v, state.selectedWordId)
      if (window.location.hash !== newHash) {
        window.history.pushState(null, '', newHash)
      }
    }
  },
  openWord: (id) => {
    set({ view: 'word', selectedWordId: id })
    if (typeof window !== 'undefined') {
      const newHash = buildHash('word', id)
      window.history.pushState(null, '', newHash)
    }
  },
  setBrowseFilters: (f) => set(f),
  setStudyGroup: (g) => set({ studyGroupId: g }),
  setQuizConfig: (f) => set(f),
}))

// Listen for browser back/forward (popstate) to sync view
if (typeof window !== 'undefined') {
  window.addEventListener('popstate', () => {
    const { view, selectedWordId } = parseHash()
    useUIStore.setState({ view, selectedWordId })
  })
}
