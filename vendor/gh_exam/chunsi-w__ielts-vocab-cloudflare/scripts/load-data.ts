/**
 * Data loader: reads /tmp/worddata/fldc-all-data.json
 * Loads top 5 frequency groups (occurrences >= 6) into SQLite via Prisma.
 * Limits test_sentences to 6 per word to keep DB size reasonable.
 */
import { db } from '../src/lib/db'
import * as fs from 'fs'

const SOURCE = '/tmp/worddata/fldc-all-data.json'
const MAX_GROUPS = 5 // top 5 groups by frequency (occurrences >= 6)
const MAX_SENTENCES_PER_WORD = 6

function getFirstLetter(w: string): string {
  const c = w.trim().charAt(0).toUpperCase()
  if (c >= 'A' && c <= 'Z') return c
  return '#'
}

async function main() {
  console.log('Reading source JSON...')
  const raw = fs.readFileSync(SOURCE, 'utf-8')
  const data = JSON.parse(raw) as {
    word_total: number
    groups: Array<{
      name: string
      words: Array<{
        word: string
        translation: string
        phonetic?: string
        example_en?: string
        example_zh?: string
        audio_uk?: string
        audio_us?: string
        english_definition?: string
        mnemonic?: string
        occurrences: number
        test_sentences?: Array<{
          form: string
          sentence: string
          source: string
          location: string
          translation: string
        }>
      }>
    }>
  }

  console.log(`Total groups: ${data.groups.length}, word_total: ${data.word_total}`)

  // 1. Create groups
  const groupDefs = [
    { name: '出现100次以上', min: 100, max: 999999 },
    { name: '出现40~99次', min: 40, max: 99 },
    { name: '出现20~39次', min: 20, max: 39 },
    { name: '出现10~19次', min: 10, max: 19 },
    { name: '出现6~9次', min: 6, max: 9 },
    { name: '出现3~5次', min: 3, max: 5 },
    { name: '出现1~2次', min: 1, max: 2 },
  ]

  console.log('Creating word groups...')
  const groupMap = new Map<string, number>()
  for (let i = 0; i < groupDefs.length; i++) {
    const g = groupDefs[i]
    const rec = await db.wordGroup.upsert({
      where: { name: g.name },
      update: { rank: i + 1, minOccur: g.min, maxOccur: g.max },
      create: { name: g.name, rank: i + 1, minOccur: g.min, maxOccur: g.max },
    })
    groupMap.set(g.name, rec.id)
    console.log(`  group ${rec.id}: ${g.name} (rank ${i + 1})`)
  }

  // 2. Load top MAX_GROUPS groups
  const groupsToLoad = data.groups.slice(0, MAX_GROUPS)
  let totalWords = 0
  let totalSentences = 0

  for (let gi = 0; gi < groupsToLoad.length; gi++) {
    const g = groupsToLoad[gi]
    const groupId = groupMap.get(g.name)!
    console.log(`\nLoading group ${gi + 1}/${groupsToLoad.length}: ${g.name} (${g.words.length} words)`)

    // Process in batches of 200
    const BATCH = 200
    for (let i = 0; i < g.words.length; i += BATCH) {
      const batch = g.words.slice(i, i + BATCH)
      // Use a transaction for each batch
      await db.$transaction(async (tx) => {
        for (const w of batch) {
          const word = (w.word || '').trim()
          if (!word) continue
          const firstLetter = getFirstLetter(word)
          const length = word.length
          // upsert word
          const created = await tx.word.upsert({
            where: { word },
            update: {
              translation: w.translation || '',
              phonetic: w.phonetic || null,
              exampleEn: w.example_en || null,
              exampleZh: w.example_zh || null,
              audioUk: w.audio_uk || null,
              audioUs: w.audio_us || null,
              englishDefinition: w.english_definition || null,
              mnemonic: w.mnemonic || null,
              occurrences: w.occurrences || 0,
              groupId,
              firstLetter,
              length,
            },
            create: {
              word,
              translation: w.translation || '',
              phonetic: w.phonetic || null,
              exampleEn: w.example_en || null,
              exampleZh: w.example_zh || null,
              audioUk: w.audio_uk || null,
              audioUs: w.audio_us || null,
              englishDefinition: w.english_definition || null,
              mnemonic: w.mnemonic || null,
              occurrences: w.occurrences || 0,
              groupId,
              firstLetter,
              length,
            },
          })

          // Insert test sentences (limit MAX_SENTENCES_PER_WORD)
          const sentences = (w.test_sentences || []).slice(0, MAX_SENTENCES_PER_WORD)
          for (const s of sentences) {
            const sentence = (s.sentence || '').trim()
            if (!sentence) continue
            await tx.testSentence.create({
              data: {
                wordId: created.id,
                form: s.form || word,
                sentence,
                source: s.source || '',
                location: s.location || '',
                translation: s.translation || '',
              },
            })
            totalSentences++
          }
          totalWords++
        }
      })
      if ((i + BATCH) % 1000 === 0 || i + BATCH >= g.words.length) {
        console.log(`  processed ${Math.min(i + BATCH, g.words.length)}/${g.words.length}`)
      }
    }
  }

  console.log(`\nDONE. Loaded ${totalWords} words and ${totalSentences} test sentences.`)
}

main()
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
  .finally(async () => {
    await db.$disconnect()
  })
