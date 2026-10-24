import { NextResponse } from 'next/server'
import { db } from '@/lib/db'

export const dynamic = 'force-dynamic'

// GET /api/stats - overall platform statistics
export async function GET() {
  const [wordCount, sentenceCount, groupCount, groupStats] = await Promise.all([
    db.word.count(),
    db.testSentence.count(),
    db.wordGroup.count(),
    db.wordGroup.findMany({
      where: { rank: { lte: 5 } },
      orderBy: { rank: 'asc' },
      include: { _count: { select: { words: true } } },
    }),
  ])

  // distinct first letters
  const letters = await db.word.findMany({
    where: { firstLetter: { not: '#' } },
    select: { firstLetter: true },
    distinct: ['firstLetter'],
    orderBy: { firstLetter: 'asc' },
  })

  return NextResponse.json({
    wordCount,
    sentenceCount,
    groupCount,
    letters: letters.map((l) => l.firstLetter),
    groups: groupStats.map((g) => ({
      id: g.id,
      name: g.name,
      rank: g.rank,
      minOccur: g.minOccur,
      maxOccur: g.maxOccur,
      wordCount: g._count.words,
    })),
  })
}
