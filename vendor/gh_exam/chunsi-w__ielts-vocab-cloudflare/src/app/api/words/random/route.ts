import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'

export const dynamic = 'force-dynamic'

// GET /api/words/random - random words
// Query params:
//   count: number (default 1, max 20)
//   groupId: number (optional)
//   excludeIds: comma-separated ids (optional)
export async function GET(req: NextRequest) {
  const sp = req.nextUrl.searchParams
  const count = Math.min(20, Math.max(1, parseInt(sp.get('count') || '1', 10)))
  const groupId = sp.get('groupId') ? parseInt(sp.get('groupId')!, 10) : undefined
  const excludeIdsStr = sp.get('excludeIds') || ''
  const excludeIds = excludeIdsStr
    .split(',')
    .map((s) => parseInt(s, 10))
    .filter((n) => !Number.isNaN(n))

  // SQLite doesn't support native random sampling efficiently, use random offset
  const where: any = {}
  if (groupId) where.groupId = groupId
  if (excludeIds.length) where.id = { notIn: excludeIds }

  const total = await db.word.count({ where })
  if (total === 0) {
    return NextResponse.json({ words: [] })
  }

  // pick `count` random offsets
  const words: any[] = []
  const usedOffsets = new Set<number>()
  const maxAttempts = count * 5
  let attempts = 0
  while (words.length < count && attempts < maxAttempts) {
    attempts++
    const offset = Math.floor(Math.random() * total)
    if (usedOffsets.has(offset)) continue
    usedOffsets.add(offset)
    const w = await db.word.findFirst({
      where,
      skip: offset,
      take: 1,
      include: {
        group: { select: { name: true, rank: true } },
        _count: { select: { testSentences: true } },
      },
    })
    if (w && !words.find((x) => x.id === w.id)) {
      words.push(w)
    }
  }

  return NextResponse.json({
    words: words.map((w) => ({
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
