import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'

export const dynamic = 'force-dynamic'

// POST /api/words/by-ids - fetch words by list of ids (for favorites/learned view)
// Body: { ids: number[] }
export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => ({}))
  const ids: number[] = Array.isArray(body?.ids) ? body.ids : []
  if (ids.length === 0) return NextResponse.json({ words: [] })

  // cap to 500 ids
  const limited = ids.slice(0, 500)
  const words = await db.word.findMany({
    where: { id: { in: limited } },
    orderBy: { occurrences: 'desc' },
    include: {
      group: { select: { name: true, rank: true } },
      _count: { select: { testSentences: true } },
    },
  })

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
