import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'

export const dynamic = 'force-dynamic'

// GET /api/search - quick search for autocomplete
// Query: q (string), limit (default 10, max 20)
export async function GET(req: NextRequest) {
  const sp = req.nextUrl.searchParams
  const q = (sp.get('q') || '').trim()
  const limit = Math.min(20, Math.max(1, parseInt(sp.get('limit') || '10', 10)))
  if (!q) return NextResponse.json({ results: [] })

  const words = await db.word.findMany({
    where: {
      OR: [
        { word: { contains: q } },
        { translation: { contains: q } },
      ],
    },
    take: limit,
    orderBy: { occurrences: 'desc' },
    select: {
      id: true,
      word: true,
      translation: true,
      phonetic: true,
      occurrences: true,
      group: { select: { name: true, rank: true } },
    },
  })

  return NextResponse.json({
    results: words.map((w) => ({
      id: w.id,
      word: w.word,
      translation: w.translation,
      phonetic: w.phonetic,
      occurrences: w.occurrences,
      groupName: w.group.name,
      groupRank: w.group.rank,
    })),
  })
}
