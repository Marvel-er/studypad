import { ArrowUpRight, BookOpenText, Check, Clock3, Languages, Newspaper } from 'lucide-react'
import { useDailyReading } from '../hooks/useDailyReading'
import { grammarLessons } from '../data/grammar'
import { toDateKey } from '../lib/progress'
import type { AppProgress, Section } from '../types'

function calculateStreak(dates: string[]): number {
  const known = new Set(dates)
  const cursor = new Date()
  let streak = 0
  while (known.has(toDateKey(cursor))) {
    streak += 1
    cursor.setDate(cursor.getDate() - 1)
  }
  return streak
}

export function TodayView({ progress, navigate }: { progress: AppProgress; navigate: (section: Section) => void }) {
  const { article: todayReading, status: readingStatus } = useDailyReading()
  const todayKey = toDateKey()
  const currentStageLessons = grammarLessons.filter((lesson) => lesson.stage === progress.preferences.grammarStage)
  const nextGrammar = currentStageLessons.find((lesson) => !progress.grammar[lesson.id]?.completed) ?? currentStageLessons[0]
  const happenedToday = (timestamp?: string) => Boolean(timestamp && toDateKey(new Date(timestamp)) === todayKey)
  const grammarDone = Object.values(progress.grammar).some((lesson) => happenedToday(lesson.completedAt))
  const wordsMet = Object.values(progress.vocabulary).filter((word) => happenedToday(word.lastSeenAt)).length
  const dueWords = Object.values(progress.vocabulary).filter((word) => word.seen > 0 && word.dueAt <= todayKey).length
  const readingDone = Boolean(progress.reading[todayReading.id]?.completed && happenedToday(progress.reading[todayReading.id]?.completedAt))
  const completedTasks = Number(grammarDone) + Number(wordsMet >= 6) + Number(readingDone)
  const streak = calculateStreak(progress.activityDates)
  const dateLabel = new Intl.DateTimeFormat('zh-CN', {
    month: 'long',
    day: 'numeric',
    weekday: 'long',
  }).format(new Date())

  const tasks = [
    {
      id: 'grammar' as const,
      icon: BookOpenText,
      kicker: '语感练习',
      title: nextGrammar?.title ?? '继续语法路径',
      minutes: 6,
      done: grammarDone,
      tone: 'indigo',
    },
    {
      id: 'vocabulary' as const,
      icon: Languages,
      kicker: '今日词汇',
      title: dueWords ? '复习到期词' : '学习 6 个新词',
      minutes: 6,
      done: wordsMet >= 6,
      tone: 'red',
    },
    {
      id: 'reading' as const,
      icon: Newspaper,
      kicker: readingStatus === 'live' ? '今日更新' : readingStatus === 'loading' ? '更新中' : '离线精选',
      title: todayReading.title,
      minutes: todayReading.minutes,
      done: readingDone,
      tone: 'blue',
    },
  ]

  return (
    <div className="page today-page">
      <section className="today-intro page-band">
        <div className="page-inner intro-grid">
          <div>
            <p className="eyebrow">{dateLabel}</p>
            <h1>今天，读一点英语。</h1>
          </div>
          <div className="day-summary" aria-label={`今日完成 ${completedTasks} 项，共 3 项`}>
            <div className="progress-ring" style={{ '--progress': `${(completedTasks / 3) * 360}deg` } as React.CSSProperties}>
              <span>{completedTasks}<small>/ 3</small></span>
            </div>
            <div>
              <strong>{streak > 0 ? `连续 ${streak} 天` : '从今天开始'}</strong>
            </div>
          </div>
        </div>
      </section>

      <section className="learning-path page-band">
        <div className="page-inner path-grid">
          <div className="path-main">
            <div className="section-heading">
              <div>
                <h2>今日路径</h2>
              </div>
              <span className="quiet-meta"><Clock3 size={15} /> 约 {progress.preferences.dailyMinutes} 分钟</span>
            </div>

            <div className="task-list">
              {tasks.map(({ id, icon: Icon, kicker, title, minutes, done, tone }) => (
                <button className="task-row" type="button" key={id} onClick={() => navigate(id)}>
                  <span className={`task-icon ${tone}`}><Icon size={20} /></span>
                  <span className="task-copy">
                    <small>{kicker}</small>
                    <strong>{title}</strong>
                  </span>
                  <span className="task-tail">
                    {done ? <span className="done-label"><Check size={15} /> 已完成</span> : <small>{minutes} 分钟</small>}
                    <ArrowUpRight size={18} aria-hidden="true" />
                  </span>
                </button>
              ))}
            </div>
          </div>

          <aside className="reading-preview">
            <img src="/assets/book-study.jpg" alt="一摞有阅读痕迹的书，书页边缘清晰可见" />
            <div className="reading-preview-copy">
              <div className="preview-topline">
                <span>{readingStatus === 'live' ? '今日实时' : readingStatus === 'loading' ? '正在更新' : '离线精选'}</span>
                <span>{todayReading.minutes} MIN</span>
              </div>
              <h2>{todayReading.title}</h2>
              <button className="underlined-button" type="button" onClick={() => navigate('reading')}>
                打开短文 <ArrowUpRight size={16} />
              </button>
            </div>
          </aside>
        </div>
      </section>

    </div>
  )
}
