import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'

export const dynamic = 'force-dynamic'

// GET /api/words - paginated word list with filters
// Query params:
//   page: number (default 1)
//   pageSize: number (default 24, max 60)
//   groupId: number (optional)
//   firstLetter: string (optional, e.g. "A")
//   search: string (optional, search word/translation)
//   sort: "occurrences_desc" | "occurrences_asc" | "word_asc" | "word_desc" (default occurrences_desc)
export async function GET(req: NextRequest) {
  const sp = req.nextUrl.searchParams
  const page = Math.max(1, parseInt(sp.get('page') || '1', 10))
  const pageSize = Math.min(60, Math.max(1, parseInt(sp.get('pageSize') || '24', 10)))
  const groupId = sp.get('groupId') ? parseInt(sp.get('groupId')!, 10) : undefined
  const firstLetter = sp.get('firstLetter') || undefined
  const search = sp.get('search')?.trim() || undefined
  const sort = sp.get('sort') || 'occurrences_desc'

  const where: any = {}
  if (groupId) where.groupId = groupId
  if (firstLetter) where.firstLetter = firstLetter
  if (search) {
    where.OR = [
      { word: { contains: search } },
      { translation: { contains: search } },
      { englishDefinition: { contains: search } },
    ]
  }

  let orderBy: any = { occurrences: 'desc' }
  if (sort === 'occurrences_asc') orderBy = { occurrences: 'asc' }
  else if (sort === 'word_asc') orderBy = { word: 'asc' }
  else if (sort === 'word_desc') orderBy = { word: 'desc' }

  const [total, words] = await Promise.all([
    db.word.count({ where }),
    db.word.findMany({
      where,
      orderBy,
      skip: (page - 1) * pageSize,
      take: pageSize,
      include: {
        group: { select: { name: true, rank: true } },
        _count: { select: { testSentences: true } },
      },
    }),
  ])

  return NextResponse.json({
    page,
    pageSize,
    total,
    totalPages: Math.ceil(total / pageSize),
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
