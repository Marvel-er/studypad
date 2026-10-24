import { NextResponse } from 'next/server'
import { db } from '@/lib/db'

export const dynamic = 'force-dynamic'

// GET /api/groups - list all word groups
export async function GET() {
  const groups = await db.wordGroup.findMany({
    where: { rank: { lte: 5 } },
    orderBy: { rank: 'asc' },
    include: { _count: { select: { words: true } } },
  })
  return NextResponse.json(
    groups.map((g) => ({
      id: g.id,
      name: g.name,
      rank: g.rank,
      minOccur: g.minOccur,
      maxOccur: g.maxOccur,
      wordCount: g._count.words,
    })),
  )
}
