import { useEffect, useMemo, useState } from 'react'
import {
  ArrowRight,
  Bookmark,
  Check,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  CircleHelp,
  RotateCcw,
  Search,
  Volume2,
  X,
} from 'lucide-react'
import vocabularyData from '../data/vocabulary.json'
import { featuredWords } from '../data/featuredWords'
import {
  getVocabularyStatus,
  reviewVocabularyWord,
  toDateKey,
  toggleSavedWord,
  type VocabularyStatus,
} from '../lib/progress'
import type { AppProgress, FeaturedWord, Level, ReviewRating, VocabularyWord } from '../types'

const vocabulary = vocabularyData as VocabularyWord[]
const levels: Level[] = ['basic', 'middle', 'advanced']
const PAGE_SIZE = 24
const levelMeta: Record<Level, { label: string; description: string }> = {
  basic: { label: '基础', description: '日常高频 1200 词' },
  middle: { label: '中阶', description: '阅读常用 1200 词' },
  advanced: { label: '拔高', description: '深入表达 1200 词' },
}
const statusMeta: Record<VocabularyStatus, { label: string; short: string }> = {
  new: { label: '未学', short: '新' },
  learning: { label: '学习中', short: '学' },
  due: { label: '待复习', short: '复' },
  mastered: { label: '已掌握', short: '熟' },
}
type LibraryFilter = 'all' | 'due' | 'learning' | 'mastered' | 'saved'

function speak(word: string) {
  if (!('speechSynthesis' in window)) return
  window.speechSynthesis.cancel()
  const utterance = new SpeechSynthesisUtterance(word)
  utterance.lang = 'en-US'
  utterance.rate = 0.86
  window.speechSynthesis.speak(utterance)
}

function RatingButtons({ onRate }: { onRate: (rating: ReviewRating) => void }) {
  return (
    <div className="rating-buttons" aria-label="回忆程度">
      <button type="button" className="rating-forgot" onClick={() => onRate('forgot')}>
        <RotateCcw size={17} /><span>忘了</span>
      </button>
      <button type="button" className="rating-fuzzy" onClick={() => onRate('fuzzy')}>
        <CircleHelp size={17} /><span>模糊</span>
      </button>
      <button type="button" className="rating-known" onClick={() => onRate('known')}>
        <Check size={17} /><span>记得</span>
      </button>
    </div>
  )
}

function WordDetailDialog({
  word,
  progress,
  setProgress,
  onClose,
}: {
  word: VocabularyWord
  progress: AppProgress
  setProgress: React.Dispatch<React.SetStateAction<AppProgress>>
  onClose: () => void
}) {
  const state = progress.vocabulary[word.id]
  const saved = Boolean(state?.saved)
  const status = getVocabularyStatus(state)

  useEffect(() => {
    const close = (event: KeyboardEvent) => event.key === 'Escape' && onClose()
    window.addEventListener('keydown', close)
    return () => window.removeEventListener('keydown', close)
  }, [onClose])

  const rate = (rating: ReviewRating) => {
    setProgress((current) => reviewVocabularyWord(current, word.id, rating))
  }

  return (
    <div className="dialog-backdrop" role="presentation" onMouseDown={onClose}>
      <section className="word-dialog" role="dialog" aria-modal="true" aria-labelledby="word-detail-title" onMouseDown={(event) => event.stopPropagation()}>
        <div className="dialog-heading">
          <span className={`memory-badge ${status}`}>{statusMeta[status].label}</span>
          <button className="icon-button" type="button" onClick={onClose} aria-label="关闭词条" title="关闭"><X size={18} /></button>
        </div>
        <div className="word-title-row">
          <div>
            <h2 id="word-detail-title">{word.word}</h2>
            <p>{word.phonetic || '暂无音标'} <span>{word.partOfSpeech}</span></p>
          </div>
          <button className="round-audio-button" type="button" onClick={() => speak(word.word)} aria-label={`朗读 ${word.word}`} title="朗读单词">
            <Volume2 size={20} />
          </button>
        </div>
        <div className="word-meaning">
          <p>{word.gloss}</p>
        </div>
        <div className="memory-state">
          <span>复习 {state?.seen ?? 0} 次</span>
          <span>阶段 {state?.stage ?? 0}/5</span>
          <span>{state ? (state.dueAt <= toDateKey() ? '今天到期' : `${state.dueAt} 复习`) : '尚未学习'}</span>
        </div>
        <RatingButtons onRate={rate} />
        <button className={`save-word-button ${saved ? 'saved' : ''}`} type="button" onClick={() => setProgress((current) => toggleSavedWord(current, word.id))}>
          <Bookmark size={16} fill={saved ? 'currentColor' : 'none'} /> {saved ? '移出词本' : '收藏到词本'}
        </button>
      </section>
    </div>
  )
}

function WordStudyDialog({
  items,
  progress,
  setProgress,
  onClose,
}: {
  items: VocabularyWord[]
  progress: AppProgress
  setProgress: React.Dispatch<React.SetStateAction<AppProgress>>
  onClose: () => void
}) {
  const [index, setIndex] = useState(0)
  const [revealed, setRevealed] = useState(false)
  const [finished, setFinished] = useState(false)
  const [ratings, setRatings] = useState<Record<ReviewRating, number>>({ forgot: 0, fuzzy: 0, known: 0 })
  const item = items[index]
  const featured: FeaturedWord | undefined = featuredWords.find((entry) => entry.word.toLowerCase() === item?.word.toLowerCase())

  useEffect(() => {
    const close = (event: KeyboardEvent) => event.key === 'Escape' && onClose()
    window.addEventListener('keydown', close)
    return () => window.removeEventListener('keydown', close)
  }, [onClose])

  if (!item) return null

  const rate = (rating: ReviewRating) => {
    setProgress((current) => reviewVocabularyWord(current, item.id, rating))
    setRatings((current) => ({ ...current, [rating]: current[rating] + 1 }))
    if (index === items.length - 1) {
      setFinished(true)
    } else {
      setIndex((current) => current + 1)
      setRevealed(false)
    }
  }

  const status = getVocabularyStatus(progress.vocabulary[item.id])

  return (
    <div className="study-overlay" role="presentation">
      <section className="study-dialog word-study-dialog" role="dialog" aria-modal="true" aria-labelledby="word-study-title">
        <header className="study-header">
          <button className="icon-button" type="button" onClick={onClose} aria-label="退出词汇练习" title="退出练习"><X size={19} /></button>
          <div className="study-progress" aria-label={`词汇进度，第 ${index + 1} 个，共 ${items.length} 个`}>
            <span style={{ width: `${((index + Number(revealed)) / items.length) * 100}%` }} />
          </div>
          <span className="study-count">{finished ? items.length : index + 1} / {items.length}</span>
        </header>

        {!finished ? (
          <div className="study-body">
            <div className="study-step recall-step">
              <div className="word-study-kicker">
                <span className={`memory-badge ${status}`}>{statusMeta[status].label}</span>
                <button className="icon-button" type="button" onClick={() => speak(item.word)} aria-label={`朗读 ${item.word}`} title="朗读单词"><Volume2 size={18} /></button>
              </div>
              <h2 id="word-study-title" className="recall-word">{item.word}</h2>
              <p className="recall-phonetic">{item.phonetic}</p>
              {featured && !revealed && <p className="recall-context">{featured.sentence.replace(new RegExp(featured.word, 'i'), '_____')}</p>}

              {!revealed ? (
                <button className="primary-button reveal-button" type="button" onClick={() => setRevealed(true)}>看答案</button>
              ) : (
                <div className="recall-answer" aria-live="polite">
                  <p>{item.gloss}</p>
                  {featured && <><span>{featured.sentence}</span><small>{featured.collocations.join(' · ')}</small></>}
                  <RatingButtons onRate={rate} />
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="study-body">
            <div className="study-step completion-step">
              <div className="completion-mark"><CheckCircle2 size={28} /></div>
              <p className="eyebrow">今日完成</p>
              <h2 id="word-study-title">记得 {ratings.known} · 模糊 {ratings.fuzzy} · 忘了 {ratings.forgot}</h2>
              <button className="primary-button" type="button" onClick={onClose}>回到词库 <Check size={17} /></button>
            </div>
          </div>
        )}
      </section>
    </div>
  )
}

export function VocabularyView({
  progress,
  setProgress,
}: {
  progress: AppProgress
  setProgress: React.Dispatch<React.SetStateAction<AppProgress>>
}) {
  const [level, setLevel] = useState<Level>(progress.preferences.vocabularyLevel)
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(1)
  const [filter, setFilter] = useState<LibraryFilter>('all')
  const [selectedWord, setSelectedWord] = useState<VocabularyWord | null>(null)
  const [studyItems, setStudyItems] = useState<VocabularyWord[] | null>(null)
  const levelWords = useMemo(() => vocabulary.filter((word) => word.level === level), [level])
  const statusCounts = useMemo(() => {
    const counts = { new: 0, learning: 0, due: 0, mastered: 0 }
    levelWords.forEach((word) => { counts[getVocabularyStatus(progress.vocabulary[word.id])] += 1 })
    return counts
  }, [levelWords, progress.vocabulary])

  const dailyQueue = useMemo(() => {
    const due = levelWords
      .filter((word) => getVocabularyStatus(progress.vocabulary[word.id]) === 'due')
      .sort((a, b) => (progress.vocabulary[a.id]?.dueAt ?? '').localeCompare(progress.vocabulary[b.id]?.dueAt ?? ''))
    const fresh = levelWords.filter((word) => getVocabularyStatus(progress.vocabulary[word.id]) === 'new')
    return [...due.slice(0, 6), ...fresh.slice(0, Math.max(0, 6 - due.length))]
  }, [levelWords, progress.vocabulary])

  const filtered = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase()
    return vocabulary.filter((word) => {
      const state = progress.vocabulary[word.id]
      if (!normalizedQuery && word.level !== level) return false
      if (filter === 'saved' && !state?.saved) return false
      if (filter !== 'all' && filter !== 'saved' && getVocabularyStatus(state) !== filter) return false
      if (!normalizedQuery) return true
      return word.word.toLowerCase().includes(normalizedQuery) || word.gloss.includes(normalizedQuery)
    })
  }, [filter, level, progress.vocabulary, query])

  const pageCount = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE))
  const safePage = Math.min(page, pageCount)
  const visible = filtered.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE)
  const savedCount = Object.values(progress.vocabulary).filter((word) => word.saved).length

  const chooseLevel = (nextLevel: Level) => {
    setLevel(nextLevel)
    setFilter('all')
    setPage(1)
    setProgress((current) => ({ ...current, preferences: { ...current.preferences, vocabularyLevel: nextLevel } }))
  }

  const chooseFilter = (nextFilter: LibraryFilter) => {
    setFilter(nextFilter)
    setPage(1)
  }

  return (
    <div className="page vocabulary-page">
      <section className="page-hero vocabulary-hero page-band">
        <div className="page-inner vocabulary-hero-grid">
          <div>
            <p className="eyebrow">3600 WORDS · 记忆系统</p>
            <h1>{statusCounts.due ? `${statusCounts.due} 个词今天到期。` : '今天，学 6 个词。'}</h1>
          </div>
          <button className="start-session-button" type="button" disabled={!dailyQueue.length} onClick={() => setStudyItems(dailyQueue)}>
            <span><small>{statusCounts.due ? `复习 ${Math.min(6, statusCounts.due)} 个` : levelMeta[level].label}</small><strong>开始今日队列</strong></span>
            <ArrowRight size={21} />
          </button>
        </div>
      </section>

      <section className="vocab-controls page-band">
        <div className="page-inner">
          <div className="segmented-control level-control" aria-label="词汇难度">
            {levels.map((item) => (
              <button key={item} type="button" className={level === item ? 'active' : ''} onClick={() => chooseLevel(item)}>
                <span>{levelMeta[item].label} 1200</span>
              </button>
            ))}
          </div>
        </div>
      </section>

      <section className="vocabulary-library page-band">
        <div className="page-inner">
          <div className="vocab-toolbar">
            <div><h2>{query ? `“${query}”` : levelMeta[level].description}</h2></div>
            <label className="search-field">
              <Search size={17} aria-hidden="true" />
              <input type="search" value={query} onChange={(event) => { setQuery(event.target.value); setPage(1) }} placeholder="搜索 3600 词" aria-label="搜索词汇" />
              {query && <button type="button" onClick={() => { setQuery(''); setPage(1) }} aria-label="清除搜索"><X size={15} /></button>}
            </label>
          </div>

          <div className="vocab-view-tabs" role="tablist" aria-label="记忆状态">
            <button type="button" role="tab" aria-selected={filter === 'all'} className={filter === 'all' ? 'active' : ''} onClick={() => chooseFilter('all')}>全部 1200</button>
            <button type="button" role="tab" aria-selected={filter === 'due'} className={filter === 'due' ? 'active' : ''} onClick={() => chooseFilter('due')}>待复习 {statusCounts.due}</button>
            <button type="button" role="tab" aria-selected={filter === 'learning'} className={filter === 'learning' ? 'active' : ''} onClick={() => chooseFilter('learning')}>学习中 {statusCounts.learning}</button>
            <button type="button" role="tab" aria-selected={filter === 'mastered'} className={filter === 'mastered' ? 'active' : ''} onClick={() => chooseFilter('mastered')}>已掌握 {statusCounts.mastered}</button>
            <button type="button" role="tab" aria-selected={filter === 'saved'} className={filter === 'saved' ? 'active' : ''} onClick={() => chooseFilter('saved')}>词本 {savedCount}</button>
          </div>

          {visible.length ? (
            <div className="word-grid">
              {visible.map((word) => {
                const state = progress.vocabulary[word.id]
                const status = getVocabularyStatus(state)
                return (
                  <button className="word-card" type="button" key={word.id} onClick={() => setSelectedWord(word)}>
                    <span className="word-card-topline">
                      <small>{word.partOfSpeech || levelMeta[word.level].label}</small>
                      <span className={`memory-badge ${status}`}>{statusMeta[status].short}</span>
                    </span>
                    <strong>{word.word}</strong>
                    <span className="phonetic">{word.phonetic || ' '}</span>
                    <p>{word.gloss}</p>
                    {state?.saved && <span className="met-label"><Bookmark size={12} fill="currentColor" /> 词本</span>}
                  </button>
                )
              })}
            </div>
          ) : (
            <div className="empty-state"><CheckCircle2 size={24} /><h3>这里已经清空</h3></div>
          )}

          {filtered.length > PAGE_SIZE && (
            <div className="pagination" aria-label="词汇分页">
              <button className="icon-button" type="button" disabled={safePage === 1} onClick={() => setPage(safePage - 1)} aria-label="上一页"><ChevronLeft size={18} /></button>
              <span>{safePage} / {pageCount} · {filtered.length} 词</span>
              <button className="icon-button" type="button" disabled={safePage === pageCount} onClick={() => setPage(safePage + 1)} aria-label="下一页"><ChevronRight size={18} /></button>
            </div>
          )}
        </div>
      </section>

      {selectedWord && <WordDetailDialog word={selectedWord} progress={progress} setProgress={setProgress} onClose={() => setSelectedWord(null)} />}
      {studyItems && <WordStudyDialog items={studyItems} progress={progress} setProgress={setProgress} onClose={() => setStudyItems(null)} />}
    </div>
  )
}
