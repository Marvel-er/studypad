import { describe, expect, it } from 'vitest'
import { grammarLessons, grammarStages } from './grammar'

describe('grammar curriculum', () => {
  it('contains six ordered stages with eight lessons each', () => {
    expect(grammarStages).toHaveLength(6)
    expect(grammarLessons).toHaveLength(48)
    grammarStages.forEach((stage) => {
      expect(grammarLessons.filter((lesson) => lesson.stage === stage.id)).toHaveLength(8)
    })
  })

  it('gives every lesson examples, judgment, rule, and transfer practice', () => {
    grammarLessons.forEach((lesson) => {
      expect(lesson.examples).toHaveLength(3)
      expect(lesson.challenge?.options).toHaveLength(2)
      expect(lesson.challenge?.insight.length).toBeGreaterThan(10)
      expect(lesson.challenge?.transfer.options).toHaveLength(2)
    })
  })
})
