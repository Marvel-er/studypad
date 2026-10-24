import { lazy, Suspense, useEffect, useState } from 'react'
import {
  BookMarked,
  BookOpenText,
  Home,
  Languages,
  RotateCcw,
  Settings,
  SlidersHorizontal,
  X,
} from 'lucide-react'
import { TodayView } from './views/TodayView'
import { loadProgress, PROGRESS_STORAGE_KEY, resetProgress, saveProgress } from './lib/progress'
import type { AppProgress, Section } from './types'

const navigation: { id: Section; label: string; icon: typeof Home }[] = [
  { id: 'today', label: '今日', icon: Home },
  { id: 'grammar', label: '语法', icon: BookOpenText },
  { id: 'vocabulary', label: '词汇', icon: Languages },
  { id: 'reading', label: '每日阅读', icon: BookMarked },
]

const GrammarView = lazy(() => import('./views/GrammarView').then((module) => ({ default: module.GrammarView })))
const VocabularyView = lazy(() => import('./views/VocabularyView').then((module) => ({ default: module.VocabularyView })))
const ReadingView = lazy(() => import('./views/ReadingView').then((module) => ({ default: module.ReadingView })))

function SettingsDialog({
  progress,
  setProgress,
  onClose,
}: {
  progress: AppProgress
  setProgress: React.Dispatch<React.SetStateAction<AppProgress>>
  onClose: () => void
}) {
  const [confirmReset, setConfirmReset] = useState(false)

  const setMinutes = (dailyMinutes: number) => {
    setProgress((current) => ({
      ...current,
      preferences: { ...current.preferences, dailyMinutes },
    }))
  }

  const handleReset = () => {
    if (!confirmReset) {
      setConfirmReset(true)
      return
    }
    setProgress(resetProgress())
    onClose()
  }

  return (
    <div className="dialog-backdrop" role="presentation" onMouseDown={onClose}>
      <section
        className="settings-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="settings-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="dialog-heading">
          <div>
            <p className="eyebrow">偏好</p>
            <h2 id="settings-title">把每天留得刚刚好</h2>
          </div>
          <button className="icon-button" type="button" onClick={onClose} aria-label="关闭设置" title="关闭">
            <X size={18} />
          </button>
        </div>

        <div className="settings-section">
          <div>
            <h3>每日学习时长</h3>
          </div>
          <div className="segmented-control compact" aria-label="每日学习时长">
            {[10, 15, 20].map((minutes) => (
              <button
                key={minutes}
                type="button"
                className={progress.preferences.dailyMinutes === minutes ? 'active' : ''}
                onClick={() => setMinutes(minutes)}
              >
                {minutes} 分钟
              </button>
            ))}
          </div>
        </div>

        <div className="settings-section local-note">
          <SlidersHorizontal size={19} aria-hidden="true" />
          <div>
            <h3>进度保存在这台设备</h3>
            <p>只存当前浏览器。</p>
          </div>
        </div>

        <div className="settings-footer">
          {confirmReset && <p role="alert">再点一次，将清除这台设备上的全部学习记录。</p>}
          <button className="text-button danger" type="button" onClick={handleReset}>
            <RotateCcw size={16} />
            {confirmReset ? '确认清除' : '清除本地进度'}
          </button>
        </div>
      </section>
    </div>
  )
}

export default function App() {
  const [section, setSection] = useState<Section>('today')
  const [progress, setProgress] = useState<AppProgress>(() => loadProgress())
  const [settingsOpen, setSettingsOpen] = useState(false)

  useEffect(() => saveProgress(progress), [progress])

  useEffect(() => {
    const syncProgress = (event: StorageEvent) => {
      if (event.key === PROGRESS_STORAGE_KEY) setProgress(loadProgress())
    }
    window.addEventListener('storage', syncProgress)
    return () => window.removeEventListener('storage', syncProgress)
  }, [])

  const navigate = (nextSection: Section) => {
    setSection(nextSection)
    setProgress((current) => ({ ...current, resume: { section: nextSection } }))
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <div className="app-shell">
      <header className="site-header">
        <button className="brand" type="button" onClick={() => navigate('today')} aria-label="返回今日学习">
          <span className="brand-mark" aria-hidden="true">静</span>
          <span>
            <strong>静词</strong>
            <small>STILLWORD</small>
          </span>
        </button>

        <nav className="desktop-nav" aria-label="主导航">
          {navigation.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              type="button"
              className={section === id ? 'active' : ''}
              onClick={() => navigate(id)}
              aria-current={section === id ? 'page' : undefined}
            >
              <Icon size={17} />
              {label}
            </button>
          ))}
        </nav>

        <button
          className="icon-button header-settings"
          type="button"
          onClick={() => setSettingsOpen(true)}
          aria-label="学习设置"
          title="学习设置"
        >
          <Settings size={19} />
        </button>
      </header>

      <main id="main-content">
        <Suspense fallback={<div className="page-loading" role="status">正在翻开这一页…</div>}>
          {section === 'today' && <TodayView progress={progress} navigate={navigate} />}
          {section === 'grammar' && <GrammarView progress={progress} setProgress={setProgress} />}
          {section === 'vocabulary' && <VocabularyView progress={progress} setProgress={setProgress} />}
          {section === 'reading' && <ReadingView progress={progress} setProgress={setProgress} />}
        </Suspense>
      </main>

      <nav className="mobile-nav" aria-label="移动端主导航">
        {navigation.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            type="button"
            className={section === id ? 'active' : ''}
            onClick={() => navigate(id)}
            aria-current={section === id ? 'page' : undefined}
          >
            <Icon size={20} />
            <span>{label === '每日阅读' ? '阅读' : label}</span>
          </button>
        ))}
      </nav>

      {settingsOpen && (
        <SettingsDialog progress={progress} setProgress={setProgress} onClose={() => setSettingsOpen(false)} />
      )}
    </div>
  )
}
