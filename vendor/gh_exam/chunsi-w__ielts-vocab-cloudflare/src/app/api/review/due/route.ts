import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'

export const dynamic = 'force-dynamic'

// POST /api/review/due - get full word details for a list of due word IDs
// Body: { ids: number[] }
export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => ({}))
  const ids: number[] = Array.isArray(body?.ids) ? body.ids : []
  if (ids.length === 0) return NextResponse.json({ words: [] })

  const limited = ids.slice(0, 100)
  const words = await db.word.findMany({
    where: { id: { in: limited } },
    orderBy: { occurrences: 'desc' },
    include: {
      group: { select: { name: true, rank: true } },
      _count: { select: { testSentences: true } },
    },
  })

  // preserve order from input ids (most overdue first)
  const map = new Map(words.map((w) => [w.id, w]))
  const ordered = limited.map((id) => map.get(id)).filter(Boolean)

  return NextResponse.json({
    words: ordered.map((w: any) => ({
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
