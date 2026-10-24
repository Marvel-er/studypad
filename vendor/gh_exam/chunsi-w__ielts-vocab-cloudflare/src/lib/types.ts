/**
 * Types shared across the app
 */

export interface WordGroup {
  id: number
  name: string
  rank: number
  minOccur: number
  maxOccur: number
  wordCount: number
}

export interface WordListItem {
  id: number
  word: string
  translation: string
  phonetic: string | null
  exampleEn: string | null
  exampleZh: string | null
  audioUk: string | null
  audioUs: string | null
  englishDefinition: string | null
  mnemonic: string | null
  occurrences: number
  groupId: number
  groupName: string
  groupRank: number
  firstLetter: string
  length: number
  sentenceCount: number
}

export interface TestSentence {
  id: number
  wordId: number
  form: string
  sentence: string
  source: string
  location: string
  translation: string
}

export interface WordDetail extends WordListItem {
  group: WordGroup
  testSentences: TestSentence[]
}

export interface Stats {
  wordCount: number
  sentenceCount: number
  groupCount: number
  letters: string[]
  groups: WordGroup[]
}

export interface QuizQuestion {
  wordId: number
  word: string
  mode: 'en_to_zh' | 'zh_to_en' | 'en_to_sentence'
  prompt: string
  promptTranslation: string
  options: string[]
  answerIndex: number
  explanation: {
    word: string
    translation: string
    phonetic: string
    exampleEn: string
    exampleZh: string
  }
}

export interface QuizResponse {
  mode: string
  count: number
  questions: QuizQuestion[]
}
