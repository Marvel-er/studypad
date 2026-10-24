/**
 * Incremental loader: loads group 6 (occurrences 3-5) only.
 * Reads /tmp/worddata/fldc-all-data.json
 * Limits test_sentences to 3 per word (low-freq words have fewer anyway).
 */
import { db } from '../src/lib/db'
import * as fs from 'fs'

const SOURCE = '/tmp/worddata/fldc-all-data.json'
const TARGET_GROUP_NAME = '出现3~5次'
const MAX_SENTENCES_PER_WORD = 3

function getFirstLetter(w: string): string {
  const c = w.trim().charAt(0).toUpperCase()
  if (c >= 'A' && c <= 'Z') return c
  return '#'
}

async function main() {
  console.log('Reading source JSON...')
  const raw = fs.readFileSync(SOURCE, 'utf-8')
  const data = JSON.parse(raw) as {
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

  // Find the target group
  const group = data.groups.find((g) => g.name === TARGET_GROUP_NAME)
  if (!group) {
    console.error(`Group "${TARGET_GROUP_NAME}" not found`)
    process.exit(1)
  }

  // Get the group record from DB
  const dbGroup = await db.wordGroup.findUnique({ where: { name: TARGET_GROUP_NAME } })
  if (!dbGroup) {
    console.error(`DB group "${TARGET_GROUP_NAME}" not found. Run load-data.ts first.`)
    process.exit(1)
  }
  console.log(`Loading group: ${group.name} (${group.words.length} words) into DB group id=${dbGroup.id}`)

  let totalWords = 0
  let totalSentences = 0
  let skipped = 0

  const BATCH = 200
  for (let i = 0; i < group.words.length; i += BATCH) {
    const batch = group.words.slice(i, i + BATCH)
    await db.$transaction(async (tx) => {
      for (const w of batch) {
        const word = (w.word || '').trim()
        if (!word) {
          skipped++
          continue
        }
        // skip if already exists (from previous groups)
        const existing = await tx.word.findUnique({ where: { word }, select: { id: true } })
        if (existing) {
          skipped++
          continue
        }
        const firstLetter = getFirstLetter(word)
        const length = word.length
        const created = await tx.word.create({
          data: {
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
            groupId: dbGroup.id,
            firstLetter,
            length,
          },
        })

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
    if ((i + BATCH) % 2000 === 0 || i + BATCH >= group.words.length) {
      console.log(`  processed ${Math.min(i + BATCH, group.words.length)}/${group.words.length} (skipped ${skipped})`)
    }
  }

  console.log(`\nDONE. Loaded ${totalWords} new words and ${totalSentences} test sentences. Skipped ${skipped} (empty or existing).`)
}

main()
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
  .finally(async () => {
    await db.$disconnect()
  })
