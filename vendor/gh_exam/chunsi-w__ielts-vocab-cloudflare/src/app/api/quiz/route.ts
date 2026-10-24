import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'

export const dynamic = 'force-dynamic'

// GET /api/quiz - generate quiz questions
// Query params:
//   count: number (default 10, max 20)
//   groupId: number (optional)
//   mode: "en_to_zh" | "zh_to_en" | "en_to_sentence" (default en_to_zh)
//   difficulty: "easy" | "medium" | "hard" | "adaptive" (default adaptive)
//     easy = high-freq groups (rank 1-2)
//     medium = mid groups (rank 3-4)
//     hard = low-freq groups (rank 5-6)
//     adaptive = mix based on groupRank weighting
//   focusWordIds: comma-separated word IDs (optional) - prioritize these words (e.g. wrong words)
export async function GET(req: NextRequest) {
  const sp = req.nextUrl.searchParams
  const count = Math.min(20, Math.max(3, parseInt(sp.get('count') || '10', 10)))
  const groupId = sp.get('groupId') ? parseInt(sp.get('groupId')!, 10) : undefined
  const mode = (sp.get('mode') || 'en_to_zh') as
    | 'en_to_zh'
    | 'zh_to_en'
    | 'en_to_sentence'
  const difficulty = sp.get('difficulty') || 'adaptive'
  const focusWordIdsStr = sp.get('focusWordIds') || ''
  const focusWordIds = focusWordIdsStr
    .split(',')
    .map((s) => parseInt(s, 10))
    .filter((n) => !Number.isNaN(n))
    .slice(0, 50) // cap at 50 focus words

  const where: any = {}
  if (groupId) {
    where.groupId = groupId
  } else if (difficulty === 'easy') {
    where.groupId = { in: [1, 2] }
  } else if (difficulty === 'medium') {
    where.groupId = { in: [3, 4] }
  } else if (difficulty === 'hard') {
    where.groupId = { in: [5, 6] }
  }
  // adaptive: no group filter, random across all groups
  // require translation for quiz
  where.translation = { not: '' }

  // Load focus words first (prioritize user's wrong words)
  const picked: any[] = []
  const usedIds = new Set<number>()
  if (focusWordIds.length > 0) {
    const focusWords = await db.word.findMany({
      where: { id: { in: focusWordIds }, translation: { not: '' } },
      take: count,
      include: { testSentences: { take: 1 } },
    })
    // shuffle focus words
    for (let i = focusWords.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1))
      ;[focusWords[i], focusWords[j]] = [focusWords[j], focusWords[i]]
    }
    for (const w of focusWords) {
      if (picked.length >= count) break
      picked.push(w)
      usedIds.add(w.id)
    }
  }

  const total = await db.word.count({ where })
  if (total < 4) {
    return NextResponse.json(
      { error: 'Not enough words to generate quiz' },
      { status: 400 },
    )
  }

  // Fill remaining slots with random words
  const usedOffsets = new Set<number>()
  let attempts = 0
  while (picked.length < count && attempts < count * 8) {
    attempts++
    const offset = Math.floor(Math.random() * total)
    if (usedOffsets.has(offset)) continue
    usedOffsets.add(offset)
    const w = await db.word.findFirst({
      where: { ...where, id: { notIn: [...usedIds] } },
      skip: offset,
      take: 1,
      include: {
        testSentences: { take: 1 },
      },
    })
    if (w && !usedIds.has(w.id)) {
      picked.push(w)
      usedIds.add(w.id)
    }
  }

  // For each picked word, gather 3 distractors.
  // Strategy: prefer words with the same first letter (en_to_zh mode) or similar length,
  // making distractors more challenging. Fall back to random if not enough.
  const questions = []
  for (const w of picked) {
    const distractors: any[] = []
    const distractorUsedIds = new Set<number>([w.id])

    // For en_to_zh mode: prefer same firstLetter (so options look similar)
    // For zh_to_en mode: prefer same length (so word options look similar)
    const targetFirstLetter = w.firstLetter
    const targetLength = w.length
    const lengthTolerance = Math.max(2, Math.round(w.length * 0.3))

    // Try same-first-letter distractors first (max 2 to keep variety)
    if (mode === 'en_to_zh' && targetFirstLetter !== '#') {
      let dlAttempts = 0
      const sameLetterTotal = await db.word.count({
        where: { ...where, id: { notIn: [...distractorUsedIds] }, firstLetter: targetFirstLetter },
      })
      while (distractors.length < 2 && dlAttempts < 8 && sameLetterTotal > 0) {
        dlAttempts++
        const offset = Math.floor(Math.random() * sameLetterTotal)
        const d = await db.word.findFirst({
          where: { ...where, id: { notIn: [...distractorUsedIds] }, firstLetter: targetFirstLetter },
          skip: offset,
          take: 1,
          select: { id: true, word: true, translation: true, exampleEn: true, exampleZh: true, firstLetter: true, length: true },
        })
        if (d && !distractorUsedIds.has(d.id)) {
          distractors.push(d)
          distractorUsedIds.add(d.id)
        }
      }
    }

    // Try similar-length distractors (for zh_to_en, or to fill remaining for en_to_zh)
    if (distractors.length < 3) {
      const similarWhere = {
        ...where,
        id: { notIn: [...distractorUsedIds] },
        length: { gte: Math.max(2, targetLength - lengthTolerance), lte: targetLength + lengthTolerance },
      }
      const similarTotal = await db.word.count({ where: similarWhere })
      let slAttempts = 0
      while (distractors.length < 3 && slAttempts < 6 && similarTotal > 0) {
        slAttempts++
        const offset = Math.floor(Math.random() * similarTotal)
        const d = await db.word.findFirst({
          where: similarWhere,
          skip: offset,
          take: 1,
          select: { id: true, word: true, translation: true, exampleEn: true, exampleZh: true, firstLetter: true, length: true },
        })
        if (d && !distractorUsedIds.has(d.id)) {
          distractors.push(d)
          distractorUsedIds.add(d.id)
        }
      }
    }

    // Fill remaining with random distractors
    let dAttempts = 0
    while (distractors.length < 3 && dAttempts < 20) {
      dAttempts++
      const offset = Math.floor(Math.random() * total)
      const d = await db.word.findFirst({
        where: { ...where, id: { notIn: [...distractorUsedIds] } },
        skip: offset,
        take: 1,
        select: { id: true, word: true, translation: true, exampleEn: true, exampleZh: true, firstLetter: true, length: true },
      })
      if (d && !distractorUsedIds.has(d.id)) {
        distractors.push(d)
        distractorUsedIds.add(d.id)
      }
    }
    if (distractors.length < 3) continue

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
      promptTranslation = ''
      optionTexts = options.map((o) => o.word)
      answerIndex = options.findIndex((o) => o.id === w.id)
    } else {
      // en_to_sentence: prompt = word, options = example sentences
      // For this mode, use the word's test sentence as correct, other words' exampleEn as distractors
      const correctSentence = w.testSentences[0]?.sentence || w.exampleEn || ''
      if (!correctSentence) continue
      // For distractors, we already have other words; use their exampleEn
      const distractorSentences = distractors
        .map((d) => d.exampleEn)
        .filter((s): s is string => !!s && s.length > 0)
      if (distractorSentences.length < 3) continue
      prompt = w.word
      promptTranslation = w.translation
      const sentOptions = [...distractorSentences.slice(0, 3), correctSentence]
      // shuffle
      for (let i = sentOptions.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1))
        ;[sentOptions[i], sentOptions[j]] = [sentOptions[j], sentOptions[i]]
      }
      optionTexts = sentOptions
      answerIndex = sentOptions.indexOf(correctSentence)
    }

    questions.push({
      wordId: w.id,
      word: w.word,
      mode,
      prompt,
      promptTranslation,
      options: optionTexts,
      answerIndex,
      // include for review after answering
      explanation: {
        word: w.word,
        translation: w.translation,
        phonetic: w.phonetic || '',
        exampleEn: w.exampleEn || '',
        exampleZh: w.exampleZh || '',
      },
    })
  }

  return NextResponse.json({ mode, count: questions.length, questions })
}
