import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'

export const dynamic = 'force-dynamic'

// GET /api/quiz/spelling - generate spelling quiz questions
// Query params:
//   count: number (default 10, max 20)
//   groupId: number (optional)
//   hint: "phonetic" | "translation" | "audio" (default translation)
export async function GET(req: NextRequest) {
  const sp = req.nextUrl.searchParams
  const count = Math.min(20, Math.max(3, parseInt(sp.get('count') || '10', 10)))
  const groupId = sp.get('groupId') ? parseInt(sp.get('groupId')!, 10) : undefined
  const hint = (sp.get('hint') || 'translation') as 'phonetic' | 'translation' | 'audio'

  const where: any = { word: { not: '' }, translation: { not: '' } }
  if (groupId) where.groupId = groupId
  // skip multi-word phrases (contain space) - spelling is for single words
  where.NOT = [{ word: { contains: ' ' } }]
  // prefer words <= 20 chars
  where.length = { lte: 20 }

  const total = await db.word.count({ where })
  if (total < count) {
    return NextResponse.json(
      { error: 'Not enough words to generate spelling quiz' },
      { status: 400 },
    )
  }

  const picked: any[] = []
  const usedOffsets = new Set<number>()
  let attempts = 0
  while (picked.length < count && attempts < count * 10) {
    attempts++
    const offset = Math.floor(Math.random() * total)
    if (usedOffsets.has(offset)) continue
    usedOffsets.add(offset)
    const w = await db.word.findFirst({
      where,
      skip: offset,
      take: 1,
    })
    if (w && !picked.find((x) => x.id === w.id)) {
      picked.push(w)
    }
  }

  const questions = picked.map((w) => ({
    wordId: w.id,
    word: w.word,
    phonetic: w.phonetic || '',
    translation: w.translation,
    audioUk: w.audioUk || null,
    audioUs: w.audioUs || null,
    exampleEn: w.exampleEn || '',
    exampleZh: w.exampleZh || '',
    hint,
  }))

  return NextResponse.json({ mode: 'spelling', hint, count: questions.length, questions })
}
