import { describe, expect, it } from 'vitest'
import { readings } from './readings'

function wordCount(text: string) {
  return text.trim().split(/\s+/).filter(Boolean).length
}

describe('fallback readings', () => {
  it('keeps every article within the 400-600 word reading range', () => {
    readings.forEach((article) => {
      const count = wordCount(article.paragraphs.join(' '))
      expect(count, article.title).toBeGreaterThanOrEqual(400)
      expect(count, article.title).toBeLessThanOrEqual(600)
    })
  })

  it('contains substantial paragraphs rather than short fragments', () => {
    readings.forEach((article) => {
      expect(article.paragraphs.length, article.title).toBeGreaterThanOrEqual(6)
    })
  })
})
