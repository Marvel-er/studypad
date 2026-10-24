import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'

export const dynamic = 'force-dynamic'

// GET /api/words/[id] - single word with full detail
export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params
  const wordId = parseInt(id, 10)
  if (Number.isNaN(wordId)) {
    return NextResponse.json({ error: 'Invalid id' }, { status: 400 })
  }

  const word = await db.word.findUnique({
    where: { id: wordId },
    include: {
      group: true,
      testSentences: { orderBy: { source: 'asc' } },
    },
  })

  if (!word) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 })
  }

  return NextResponse.json({
    id: word.id,
    word: word.word,
    translation: word.translation,
    phonetic: word.phonetic,
    exampleEn: word.exampleEn,
    exampleZh: word.exampleZh,
    audioUk: word.audioUk,
    audioUs: word.audioUs,
    englishDefinition: word.englishDefinition,
    mnemonic: word.mnemonic,
    occurrences: word.occurrences,
    groupId: word.groupId,
    group: word.group,
    firstLetter: word.firstLetter,
    length: word.length,
    testSentences: word.testSentences,
  })
}
