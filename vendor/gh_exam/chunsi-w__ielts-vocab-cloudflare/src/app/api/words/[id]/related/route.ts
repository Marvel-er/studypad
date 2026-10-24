import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'

export const dynamic = 'force-dynamic'

// GET /api/words/[id]/related - find related words (same first letter, similar length)
// Query: limit (default 6, max 12)
export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params
  const wordId = parseInt(id, 10)
  if (Number.isNaN(wordId)) {
    return NextResponse.json({ error: 'Invalid id' }, { status: 400 })
  }
  const sp = req.nextUrl.searchParams
  const limit = Math.min(12, Math.max(3, parseInt(sp.get('limit') || '6', 10)))

  const word = await db.word.findUnique({
    where: { id: wordId },
    select: { id: true, word: true, firstLetter: true, length: true, groupId: true },
  })
  if (!word) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 })
  }

  // Strategy:
  // 1. Same first letter, similar length (±3) — most related
  // 2. Same first letter, any length — fill remaining
  // 3. Similar length, different letter — fill remaining
  const tolerance = 3
  const results: any[] = []
  const usedIds = new Set<number>([wordId])

  // Batch 1: same first letter + similar length
  if (results.length < limit) {
    const batch1 = await db.word.findMany({
      where: {
        id: { notIn: [...usedIds] },
        firstLetter: word.firstLetter,
        length: { gte: Math.max(2, word.length - tolerance), lte: word.length + tolerance },
      },
      take: limit * 2,
      orderBy: { occurrences: 'desc' },
      include: {
        group: { select: { name: true, rank: true } },
        _count: { select: { testSentences: true } },
      },
    })
    // shuffle batch1 and take remaining
    for (let i = batch1.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1))
      ;[batch1[i], batch1[j]] = [batch1[j], batch1[i]]
    }
    for (const w of batch1) {
      if (results.length >= limit) break
      results.push(w)
      usedIds.add(w.id)
    }
  }

  // Batch 2: same first letter, any length
  if (results.length < limit) {
    const batch2 = await db.word.findMany({
      where: {
        id: { notIn: [...usedIds] },
        firstLetter: word.firstLetter,
      },
      take: limit * 2,
      orderBy: { occurrences: 'desc' },
      include: {
        group: { select: { name: true, rank: true } },
        _count: { select: { testSentences: true } },
      },
    })
    for (let i = batch2.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1))
      ;[batch2[i], batch2[j]] = [batch2[j], batch2[i]]
    }
    for (const w of batch2) {
      if (results.length >= limit) break
      results.push(w)
      usedIds.add(w.id)
    }
  }

  // Batch 3: similar length, different letter
  if (results.length < limit) {
    const batch3 = await db.word.findMany({
      where: {
        id: { notIn: [...usedIds] },
        length: { gte: Math.max(2, word.length - tolerance), lte: word.length + tolerance },
      },
      take: limit * 2,
      orderBy: { occurrences: 'desc' },
      include: {
        group: { select: { name: true, rank: true } },
        _count: { select: { testSentences: true } },
      },
    })
    for (let i = batch3.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1))
      ;[batch3[i], batch3[j]] = [batch3[j], batch3[i]]
    }
    for (const w of batch3) {
      if (results.length >= limit) break
      results.push(w)
      usedIds.add(w.id)
    }
  }

  return NextResponse.json({
    words: results.map((w) => ({
      id: w.id,
      word: w.word,
      translation: w.translation,
      phonetic: w.phonetic,
      exampleEn: w.exampleEn,
      exampleZh: w.exampleZh,
      audioUk: w.audioUk,
      audioUs: w.audioUs,
      englishDefinition: w.englishDefinition,
      mnemonic: w.mnemonic,
      occurrences: w.occurrences,
      groupId: w.groupId,
      groupName: w.group.name,
      groupRank: w.group.rank,
      firstLetter: w.firstLetter,
      length: w.length,
      sentenceCount: w._count.testSentences,
    })),
  })
}
