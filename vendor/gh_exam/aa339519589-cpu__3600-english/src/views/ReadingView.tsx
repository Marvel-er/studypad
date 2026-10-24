import { useMemo, useState } from 'react'
import { Bookmark, Check, CheckCircle2, Clock3, ExternalLink, Minus, Plus, Volume2 } from 'lucide-react'
import vocabularyData from '../data/vocabulary.json'
import { readings } from '../data/readings'
import { useDailyReading } from '../hooks/useDailyReading'
import { markReadingCompleted, toggleSavedWord } from '../lib/progress'
import type { AppProgress, ReadingArticle, ReadingWord, VocabularyWord } from '../types'

const vocabulary = vocabularyData as VocabularyWord[]
const inflectionRoots: Record<string, string> = {
  faded: 'fade',
  remained: 'remain',
  reflected: 'reflect',
  neatly: 'neat',
  bent: 'bend',
  scattered: 'scatter',
  marked: 'mark',
  restored: 'restore',
}

function speak(text: string) {
  if (!('speechSynthesis' in window)) return
  window.speechSynthesis.cancel()
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = 'en-US'
  utterance.rate = 0.84
  window.speechSynthesis.speak(utterance)
}

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function findVocabularyWord(readingWord: ReadingWord) {
  const target = inflectionRoots[readingWord.word.toLowerCase()] ?? readingWord.word.toLowerCase()
  return vocabulary.find((word) => word.word.toLowerCase() === target)
}

function ReadingParagraph({
  text,
  words,
  onWord,
}: {
  text: string
  words: ReadingWord[]
  onWord: (word: ReadingWord) => void
}) {
  const byWord = new Map(words.map((item) => [item.word.toLowerCase(), item]))
  const pattern = new RegExp(`\\b(${words.map((item) => escapeRegExp(item.word)).join('|')})\\b`, 'gi')
  return (
    <p>
      {text.split(pattern).map((part, index) => {
        const word = byWord.get(part.toLowerCase())
        return word ? (
          <button className="inline-word" type="button" key={`${part}-${index}`} onClick={() => onWord(word)}>
            {part}
          </button>
        ) : (
          part
        )
      })}
    </p>
  )
}

export function ReadingView({
  progress,
  setProgress,
}: {
  progress: AppProgress
  setProgress: React.Dispatch<React.SetStateAction<AppProgress>>
}) {
  const { article: todayReading, status: dailyStatus } = useDailyReading()
  const [selectedArticleId, setSelectedArticleId] = useState<string | null>(null)
  const [activeWord, setActiveWord] = useState<ReadingWord | null>(null)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [fontSize, setFontSize] = useState(20)
  const articleList = useMemo(
    () => [todayReading, ...readings.filter((item) => item.id !== todayReading.id)],
    [todayReading],
  )
  const article = selectedArticleId
    ? articleList.find((item) => item.id === selectedArticleId) ?? todayReading
    : todayReading
  const answer = answers[article.id] ?? progress.reading[article.id]?.answer ?? ''
  const isCorrect = answer === article.answer
  const completed = Boolean(progress.reading[article.id]?.completed)
  const savedWordIds = useMemo(
    () => article.words
      .map(findVocabularyWord)
      .filter((word): word is VocabularyWord => Boolean(word && progress.vocabulary[word.id]?.saved))
      .map((word) => word.id),
    [article.words, progress.vocabulary],
  )

  const activeVocabularyWord = useMemo(() => {
    if (!activeWord) return undefined
    return findVocabularyWord(activeWord)
  }, [activeWord])

  const switchArticle = (nextArticle: ReadingArticle) => {
    setSelectedArticleId(nextArticle.id === todayReading.id ? null : nextArticle.id)
    setActiveWord(null)
  }

  const saveActiveWord = () => {
    if (!activeVocabularyWord) return
    const id = activeVocabularyWord.id
    setProgress((current) => toggleSavedWord(current, id))
  }

  const chooseAnswer = (choice: string) => {
    setAnswers((current) => ({ ...current, [article.id]: choice }))
    if (choice === article.answer) {
      setProgress((current) => markReadingCompleted(current, article.id, choice, savedWordIds))
    }
  }

  const activeWordSaved = activeVocabularyWord ? Boolean(progress.vocabulary[activeVocabularyWord.id]?.saved) : false

  return (
    <div className="page reading-page">
      <section className="page-hero reading-hero page-band">
        <div className="page-inner hero-row">
          <div>
            <p className="eyebrow">DAILY READING · 每日短文</p>
            <h1>每天，读完一小篇。</h1>
          </div>
        </div>
      </section>

      <section className="reader-band page-band">
        <div className="page-inner reader-layout">
          <aside className="article-index">
            <div className="index-heading">
              <p className="eyebrow">最近阅读</p>
              <span>{articleList.filter((item) => progress.reading[item.id]?.completed).length} / {articleList.length} 已读</span>
            </div>
            <div className="article-index-list">
              {articleList.map((item) => {
                const isActive = item.id === article.id
                const isDone = Boolean(progress.reading[item.id]?.completed)
                return (
                  <button className={isActive ? 'article-index-item active' : 'article-index-item'} type="button" key={item.id} onClick={() => switchArticle(item)}>
                    <span className="article-date">{item.id === todayReading.id ? (dailyStatus === 'live' ? '今日更新' : '今日') : '往日'}</span>
                    <strong>{item.title}</strong>
                    <span>{item.minutes} 分钟</span>
                    {isDone && <CheckCircle2 size={17} aria-label="已完成" />}
                  </button>
                )
              })}
            </div>
          </aside>

          <article className="reading-sheet">
            <header className="article-heading">
              <div className="article-meta">
                <span>{article.id === todayReading.id ? 'TODAY' : 'ARCHIVE'}</span>
                <span><Clock3 size={14} /> {article.minutes} MIN READ</span>
                {completed && <span className="article-complete"><Check size={13} /> COMPLETED</span>}
              </div>
              <h2>{article.title}</h2>
              {article.source?.url && (
                <a className="article-source" href={article.source.url} target="_blank" rel="noreferrer">
                  {article.source.name} <ExternalLink size={13} />
                </a>
              )}
              <div className="reader-tools" aria-label="阅读工具">
                <button className="icon-button" type="button" disabled={fontSize === 18} onClick={() => setFontSize((size) => size - 2)} aria-label="缩小正文字号" title="缩小字号">
                  <Minus size={16} />
                </button>
                <span>正文</span>
                <button className="icon-button" type="button" disabled={fontSize === 24} onClick={() => setFontSize((size) => size + 2)} aria-label="放大正文字号" title="放大字号">
                  <Plus size={16} />
                </button>
                <button className="text-button listen-button" type="button" onClick={() => speak(article.paragraphs.join(' '))}>
                  <Volume2 size={16} /> 朗读全文
                </button>
              </div>
            </header>

            <div className="article-body" style={{ fontSize }}>
              {article.paragraphs.map((paragraph) => (
                <ReadingParagraph key={paragraph} text={paragraph} words={article.words} onWord={setActiveWord} />
              ))}
            </div>

            {activeWord && (
              <aside className="inline-definition" aria-live="polite">
                <div>
                  <p className="eyebrow">文中词义</p>
                  <h3>{activeWord.word}</h3>
                  <p>{activeWord.gloss}</p>
                </div>
                <div className="definition-actions">
                  <button className="icon-button" type="button" onClick={() => speak(activeWord.word)} aria-label={`朗读 ${activeWord.word}`} title="朗读单词">
                    <Volume2 size={17} />
                  </button>
                  <button className={`secondary-button ${activeWordSaved ? 'saved' : ''}`} type="button" disabled={!activeVocabularyWord} onClick={saveActiveWord}>
                    <Bookmark size={16} fill={activeWordSaved ? 'currentColor' : 'none'} />
                    {activeVocabularyWord ? (activeWordSaved ? '已在词本' : '收进词本') : '词库未收录'}
                  </button>
                </div>
              </aside>
            )}

            <section className="reading-question" aria-labelledby="reading-question-title">
              <p className="eyebrow">读完以后</p>
              <h3 id="reading-question-title">{article.question}</h3>
              <div className="reading-choices">
                {article.choices.map((choice) => {
                  const selected = answer === choice
                  const state = selected ? (choice === article.answer ? 'correct' : 'wrong') : ''
                  return (
                    <button className={`choice-button ${state}`} type="button" key={choice} onClick={() => chooseAnswer(choice)}>
                      <span>{choice}</span>
                      {state === 'correct' && <Check size={17} />}
                    </button>
                  )
                })}
              </div>
              {answer && !isCorrect && <p className="answer-note wrong" role="alert">再看一遍正文，找最接近全文中心的描述。</p>}
              {isCorrect && (
                <div className="reading-reflection" aria-live="polite">
                  <CheckCircle2 size={20} />
                  <div><strong>读懂了。</strong><p>{article.reflection}</p></div>
                </div>
              )}
            </section>
          </article>
        </div>
      </section>
    </div>
  )
}
