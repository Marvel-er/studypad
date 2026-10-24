import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'

export const dynamic = 'force-dynamic'

// GET /api/quiz/cloze - generate cloze (fill-in-the-blank) quiz questions
// Query params:
//   count: number (default 10, max 20)
//   groupId: number (optional)
export async function GET(req: NextRequest) {
  const sp = req.nextUrl.searchParams
  const count = Math.min(20, Math.max(3, parseInt(sp.get('count') || '10', 10)))
  const groupId = sp.get('groupId') ? parseInt(sp.get('groupId')!, 10) : undefined

  // Words that have test sentences (cloze requires a sentence)
  const where: any = {
    testSentences: { some: {} },
  }
  if (groupId) where.groupId = groupId

  const total = await db.word.count({ where })
  if (total < count) {
    return NextResponse.json(
      { error: 'Not enough words with test sentences to generate cloze quiz' },
      { status: 400 },
    )
  }

  const picked: any[] = []
  const usedIds = new Set<number>()
  let attempts = 0
  while (picked.length < count && attempts < count * 10) {
    attempts++
    const offset = Math.floor(Math.random() * total)
    const w = await db.word.findFirst({
      where: { ...where, id: { notIn: [...usedIds] } },
      skip: offset,
      take: 1,
      include: {
        testSentences: { take: 1 },
        group: { select: { name: true, rank: true } },
      },
    })
    if (w && !usedIds.has(w.id) && w.testSentences[0]) {
      picked.push(w)
      usedIds.add(w.id)
    }
  }

  // Generate cloze questions
  const questions = picked.map((w) => {
    const sentence = w.testSentences[0].sentence
    const form = w.testSentences[0].form || w.word
    // Find the word form in the sentence (case-insensitive)
    const formLower = form.toLowerCase()
    const sentenceLower = sentence.toLowerCase()
    const idx = sentenceLower.indexOf(formLower)

    let blanked = sentence
    let displayWord = form
    if (idx >= 0) {
      // Replace the form with a blank, preserving surrounding text
      blanked =
        sentence.slice(0, idx) +
        '_____'.padEnd(Math.max(5, form.length), '_') +
        sentence.slice(idx + form.length)
      displayWord = sentence.slice(idx, idx + form.length) // preserve original case
    } else {
      // Fallback: if form not found, use the base word
      const wordLower = w.word.toLowerCase()
      const wIdx = sentenceLower.indexOf(wordLower)
      if (wIdx >= 0) {
        blanked =
          sentence.slice(0, wIdx) +
          '_____'.padEnd(Math.max(5, w.word.length), '_') +
          sentence.slice(wIdx + w.word.length)
        displayWord = sentence.slice(wIdx, wIdx + w.word.length)
      }
    }

    return {
      wordId: w.id,
      word: w.word,
      form: displayWord,
      sentence: blanked,
      originalSentence: sentence,
      source: w.testSentences[0].source,
      location: w.testSentences[0].location,
      translation: w.translation,
      phonetic: w.phonetic || '',
      groupName: w.group.name,
      // Hint: first letter + length
      hint: `${displayWord[0]?.toUpperCase() || ''}${'_'.repeat(Math.max(0, displayWord.length - 1))}`,
      length: displayWord.length,
    }
  })

  return NextResponse.json({ mode: 'cloze', count: questions.length, questions })
}
