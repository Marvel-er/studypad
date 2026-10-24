/**
 * Clean up duplicated content in exampleEn, exampleZh, and mnemonic fields.
 * The source data has repeated segments separated by ；that need to be deduplicated.
 */
import { db } from '../src/lib/db'

function deduplicateSegments(text: string | null): string | null {
  if (!text) return text
  const parts = text.split('；')
  const seen = new Set<string>()
  const result: string[] = []
  for (const p of parts) {
    const trimmed = p.trim()
    if (!trimmed) continue
    // Use first 30 chars as dedup key (handles minor whitespace differences)
    const key = trimmed.slice(0, 30)
    if (!seen.has(key)) {
      seen.add(key)
      result.push(trimmed)
    }
  }
  return result.length > 0 ? result.join('；') : text
}

async function main() {
  console.log('Cleaning up duplicated content in word fields...')

  // Get all words with potential duplicates
  const words = await db.word.findMany({
    where: {
      OR: [
        { exampleEn: { not: null } },
        { exampleZh: { not: null } },
        { mnemonic: { not: null } },
      ],
    },
    select: { id: true, word: true, exampleEn: true, exampleZh: true, mnemonic: true },
  })

  console.log(`Total words to check: ${words.length}`)

  let cleaned = 0
  const BATCH = 100
  for (let i = 0; i < words.length; i += BATCH) {
    const batch = words.slice(i, i + BATCH)
    await db.$transaction(
      batch.map((w) => {
        const newExampleEn = deduplicateSegments(w.exampleEn)
        const newExampleZh = deduplicateSegments(w.exampleZh)
        const newMnemonic = deduplicateSegments(w.mnemonic)

        // Only update if something changed
        if (
          newExampleEn !== w.exampleEn ||
          newExampleZh !== w.exampleZh ||
          newMnemonic !== w.mnemonic
        ) {
          cleaned++
          return db.word.update({
            where: { id: w.id },
            data: {
              exampleEn: newExampleEn,
              exampleZh: newExampleZh,
              mnemonic: newMnemonic,
            },
          })
        }
        return db.word.count() // no-op
      }),
    )
    if ((i + BATCH) % 5000 === 0) {
      console.log(`  processed ${Math.min(i + BATCH, words.length)}/${words.length}, cleaned ${cleaned}`)
    }
  }

  console.log(`\nDONE. Cleaned ${cleaned} words.`)
}

main()
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
  .finally(async () => {
    await db.$disconnect()
  })
