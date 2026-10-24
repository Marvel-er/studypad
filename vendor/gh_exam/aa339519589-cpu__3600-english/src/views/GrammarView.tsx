import { useEffect, useMemo, useState } from 'react'
import {
  ArrowLeft,
  ArrowRight,
  Check,
  CheckCircle2,
  Clock3,
  Feather,
  Lightbulb,
  LockKeyhole,
  Play,
  X,
} from 'lucide-react'
import { grammarLessons, grammarStages } from '../data/grammar'
import { markGrammarCompleted } from '../lib/progress'
import type { AppProgress, GrammarLesson } from '../types'

function GrammarStudyDialog({
  lesson,
  onClose,
  onComplete,
}: {
  lesson: GrammarLesson
  onClose: () => void
  onComplete: (correct: boolean) => void
}) {
  const [phase, setPhase] = useState(0)
  const [selected, setSelected] = useState('')
  const [transferSelected, setTransferSelected] = useState('')
  const [hadWrongAnswer, setHadWrongAnswer] = useState(false)
  const challenge = lesson.challenge!
  const firstCorrect = selected === challenge.answer
  const transferCorrect = transferSelected === challenge.transfer.answer

  useEffect(() => {
    const closeOnEscape = (event: KeyboardEvent) => event.key === 'Escape' && onClose()
    window.addEventListener('keydown', closeOnEscape)
    return () => window.removeEventListener('keydown', closeOnEscape)
  }, [onClose])

  const chooseFirst = (option: string) => {
    setSelected(option)
    if (option !== challenge.answer) setHadWrongAnswer(true)
  }

  const chooseTransfer = (option: string) => {
    setTransferSelected(option)
    if (option !== challenge.transfer.answer) setHadWrongAnswer(true)
  }

  const finish = () => {
    onComplete(!hadWrongAnswer)
    setPhase(4)
  }

  return (
    <div className="study-overlay" role="presentation">
      <section className="study-dialog" role="dialog" aria-modal="true" aria-labelledby="grammar-study-title">
        <header className="study-header">
          <button className="icon-button" type="button" onClick={onClose} aria-label="退出课程" title="退出课程">
            <X size={19} />
          </button>
          <div className="study-progress" aria-label={`学习进度，第 ${phase + 1} 步，共 5 步`}>
            <span style={{ width: `${((phase + 1) / 5) * 100}%` }} />
          </div>
          <span className="study-count">{phase + 1} / 5</span>
        </header>

        <div className="study-body">
          {phase === 0 && (
            <div className="study-step">
              <p className="eyebrow">先看三句</p>
              <h2 id="grammar-study-title">{lesson.title}</h2>
              <div className="grammar-example-list">
                {lesson.examples.map((example) => (
                  <div className="grammar-example" key={example.sentence}>
                    <span>{example.focus}</span>
                    <strong>{example.sentence}</strong>
                    <p>{example.note}</p>
                  </div>
                ))}
              </div>
              <div className="study-actions">
                <button className="primary-button" type="button" onClick={() => setPhase(1)}>
                  试一试 <ArrowRight size={17} />
                </button>
              </div>
            </div>
          )}

          {phase === 1 && (
            <div className="study-step">
              <p className="eyebrow">凭感觉选</p>
              <h2 id="grammar-study-title">{challenge.prompt}</h2>
              <div className="choice-list">
                {challenge.options.map((option) => {
                  const isSelected = selected === option
                  const state = isSelected ? (option === challenge.answer ? 'correct' : 'wrong') : ''
                  return (
                    <button key={option} type="button" className={`choice-button ${state}`} onClick={() => chooseFirst(option)}>
                      <span>{option}</span>
                      {state === 'correct' && <Check size={18} />}
                    </button>
                  )
                })}
              </div>
              {selected && (
                <p className={`answer-note ${firstCorrect ? 'correct' : 'wrong'}`} aria-live="polite">
                  {firstCorrect ? '对。' : challenge.nudge}
                </p>
              )}
              <div className="study-actions split">
                <button className="text-button" type="button" onClick={() => setPhase(0)}><ArrowLeft size={16} /> 例句</button>
                <button className="primary-button" type="button" disabled={!firstCorrect} onClick={() => setPhase(2)}>
                  看规则 <ArrowRight size={17} />
                </button>
              </div>
            </div>
          )}

          {phase === 2 && (
            <div className="study-step insight-step">
              <p className="eyebrow">现在再看规则</p>
              <div className="insight-mark"><Lightbulb size={24} /></div>
              <p className="large-reading-copy">{challenge.insight}</p>
              <div className="study-actions split">
                <button className="text-button" type="button" onClick={() => setPhase(1)}><ArrowLeft size={16} /> 回看</button>
                <button className="primary-button" type="button" onClick={() => setPhase(3)}>
                  换个例子 <ArrowRight size={17} />
                </button>
              </div>
            </div>
          )}

          {phase === 3 && (
            <div className="study-step">
              <p className="eyebrow">迁移</p>
              <h2 id="grammar-study-title">{challenge.transfer.prompt}</h2>
              <div className="choice-list">
                {challenge.transfer.options.map((option) => {
                  const isSelected = transferSelected === option
                  const state = isSelected ? (option === challenge.transfer.answer ? 'correct' : 'wrong') : ''
                  return (
                    <button key={option} type="button" className={`choice-button ${state}`} onClick={() => chooseTransfer(option)}>
                      <span>{option}</span>
                      {state === 'correct' && <Check size={18} />}
                    </button>
                  )
                })}
              </div>
              {transferSelected && (
                <p className={`answer-note ${transferCorrect ? 'correct' : 'wrong'}`} aria-live="polite">
                  {transferCorrect ? '认出来了。' : '再对照一次例句和规则。'}
                </p>
              )}
              <div className="study-actions split">
                <button className="text-button" type="button" onClick={() => setPhase(2)}><ArrowLeft size={16} /> 规则</button>
                <button className="primary-button" type="button" disabled={!transferCorrect} onClick={finish}>
                  完成 <Check size={17} />
                </button>
              </div>
            </div>
          )}

          {phase === 4 && (
            <div className="study-step completion-step">
              <div className="completion-mark"><Feather size={28} /></div>
              <p className="eyebrow">完成</p>
              <h2 id="grammar-study-title">{lesson.title}</h2>
              <button className="primary-button" type="button" onClick={onClose}>下一小节已解锁 <ArrowRight size={17} /></button>
            </div>
          )}
        </div>
      </section>
    </div>
  )
}

export function GrammarView({
  progress,
  setProgress,
}: {
  progress: AppProgress
  setProgress: React.Dispatch<React.SetStateAction<AppProgress>>
}) {
  const [stageId, setStageId] = useState(progress.preferences.grammarStage)
  const [activeLesson, setActiveLesson] = useState<GrammarLesson | null>(null)
  const stage = grammarStages.find((item) => item.id === stageId) ?? grammarStages[0]
  const lessons = useMemo(() => grammarLessons.filter((lesson) => lesson.stage === stageId), [stageId])
  const completed = lessons.filter((lesson) => progress.grammar[lesson.id]?.completed).length
  const nextIndex = lessons.findIndex((lesson) => !progress.grammar[lesson.id]?.completed)
  const unlockedThrough = nextIndex === -1 ? lessons.length - 1 : nextIndex
  const totalCompleted = grammarLessons.filter((lesson) => progress.grammar[lesson.id]?.completed).length

  const chooseStage = (nextStageId: number) => {
    const nextStage = grammarStages.find((item) => item.id === nextStageId) ?? grammarStages[0]
    setStageId(nextStageId)
    setProgress((current) => ({
      ...current,
      preferences: { ...current.preferences, grammarStage: nextStageId, grammarLevel: nextStage.level },
    }))
  }

  return (
    <div className="page grammar-page">
      <section className="page-hero page-band">
        <div className="page-inner hero-row grammar-hero-row">
          <div>
            <p className="eyebrow">GRAMMAR · 48 小节</p>
            <h1>一次，只走一小步。</h1>
          </div>
          <div className="grammar-total"><strong>{totalCompleted}</strong><span>/ 48</span></div>
        </div>
      </section>

      <section className="level-band page-band">
        <div className="page-inner">
          <div className="segmented-control level-control stage-control" aria-label="语法阶段">
            {grammarStages.map((item) => (
              <button key={item.id} type="button" className={stageId === item.id ? 'active' : ''} onClick={() => chooseStage(item.id)}>
                <span>{item.id}</span>
                <small>{item.title}</small>
              </button>
            ))}
          </div>
        </div>
      </section>

      <section className="grammar-curriculum page-band">
        <div className="page-inner">
          <div className="section-heading curriculum-heading">
            <div>
              <p className="eyebrow">{stage.label} · {completed}/8</p>
              <h2>{stage.title}</h2>
            </div>
            <div className="linear-progress" aria-label={`8 节中已完成 ${completed} 节`}>
              <span style={{ width: `${(completed / 8) * 100}%` }} />
            </div>
          </div>

          <div className="lesson-list">
            {lessons.map((lesson, index) => {
              const isDone = Boolean(progress.grammar[lesson.id]?.completed)
              const isCurrent = index === unlockedThrough && !isDone
              const isLocked = index > unlockedThrough && !isDone
              return (
                <button
                  className={`lesson-row ${isCurrent ? 'current' : ''}`}
                  type="button"
                  key={lesson.id}
                  disabled={isLocked}
                  onClick={() => setActiveLesson(lesson)}
                >
                  <span className="lesson-number">{lesson.number}</span>
                  <span className="lesson-copy">
                    <strong>{lesson.title}</strong>
                    <small>{lesson.description}</small>
                  </span>
                  <span className="lesson-meta">
                    {isDone ? <CheckCircle2 className="lesson-done" size={21} /> : isLocked ? <LockKeyhole size={19} /> : <Play size={19} />}
                    <span><Clock3 size={14} /> {lesson.duration} 分钟</span>
                  </span>
                </button>
              )
            })}
          </div>
        </div>
      </section>

      {activeLesson?.challenge && (
        <GrammarStudyDialog
          lesson={activeLesson}
          onClose={() => setActiveLesson(null)}
          onComplete={(correct) => setProgress((current) => markGrammarCompleted(current, activeLesson.id, correct))}
        />
      )}
    </div>
  )
}
