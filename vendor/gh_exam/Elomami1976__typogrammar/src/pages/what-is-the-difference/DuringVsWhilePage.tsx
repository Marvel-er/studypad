import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "During vs. While: What's the Difference? | TypoGrammar",
  metaDescription: "During vs while: during is a preposition followed by a noun (during the meeting); while is a conjunction followed by a clause (while I was working). See rules, examples, and a quiz.",
  slug: 'during-vs-while',
  h1: "During vs. While: What's the Difference?",
  breadcrumbLabel: 'During vs. While',
  datePublished: '2026-07-04',
  dateModified: '2026-07-04',
  quickAnswer: "\"During\" is a preposition followed by a noun or noun phrase (during the meeting, during summer). \"While\" is a conjunction followed by a subject and verb — a full clause (while I was cooking). Both describe something happening at the same time as something else, but the grammar that follows each word is different.",
  tableColumns: ['During', 'While'],
  tableRows: [
    { feature: 'Part of speech', values: ['Preposition', 'Conjunction'] },
    { feature: 'Followed by', values: ['A noun / noun phrase', 'A clause (subject + verb)'] },
    { feature: 'Example', values: ['during the flight', 'while we were flying'] },
    { feature: 'Can start a sentence?', values: ['Yes: "During the flight, I slept."', 'Yes: "While we were flying, I slept."'] },
  ],
  terms: [
    {
      label: 'During',
      summary: 'A preposition that must be followed by a noun or noun phrase.',
      pattern: 'during + noun',
      examples: ['"during the meeting"', '"during the war"', '"during my childhood"'],
    },
    {
      label: 'While',
      summary: 'A conjunction that must be followed by a clause (a subject and a verb).',
      pattern: 'while + subject + verb',
      examples: ['"while I was studying"', '"while it was raining"', '"while she cooks dinner"'],
    },
  ],
  grammarRule: '"During" is always followed by a noun (during + noun). "While" is always followed by a clause with its own subject and verb (while + subject + verb). Never put a clause after "during" or a bare noun after "while".',
  extraRule: 'Quick test: if you can put a comma and then "he/she/it/they + verb" after the word, you need "while", not "during".',
  mistakes: [
    { incorrect: 'During I was sleeping, the phone rang.', correct: 'While I was sleeping, the phone rang.', note: '"I was sleeping" is a clause, so it needs "while", not "during".' },
    { incorrect: 'While the meeting, nobody spoke.', correct: 'During the meeting, nobody spoke.', note: '"the meeting" is a noun phrase, so it needs "during", not "while".' },
    { incorrect: 'I fell asleep during I was watching the movie.', correct: 'I fell asleep while I was watching the movie.' },
  ],
  correctExamples: [
    'During the interview, she stayed calm and confident.',
    'While the interview was happening, her phone kept buzzing.',
    'He hurt his knee during the match.',
    'He hurt his knee while he was playing the match.',
    'Please stay seated during the announcement.',
    'While you wait, feel free to read a magazine.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: "_____ the flight, the baby cried for an hour."', answer: 'During', explanation: '"the flight" is a noun phrase, so it takes "during".' },
    { prompt: 'Choose the correct word: "_____ I was cooking, the smoke alarm went off."', answer: 'While', explanation: '"I was cooking" is a clause with a subject and verb, so it takes "while".' },
    { prompt: 'Fix the sentence: "During she was driving, she listened to a podcast."', answer: 'While she was driving, she listened to a podcast.', explanation: '"she was driving" is a clause, so "during" must be replaced with "while".' },
  ],
  faqs: [
    { question: 'Can "during" and "while" ever both be correct in the same sentence?', answer: 'Yes, but the words around them must change. "During the storm, the lights went out" and "While the storm was happening, the lights went out" both work because each version pairs the right word with the right structure (noun vs. clause).' },
    { question: 'Is "during" more formal than "while"?', answer: 'Not necessarily more formal, just more compact. "During" lets you compress a phrase into a noun, which is common in formal writing, reports, and news, while "while" is used just as often in everyday spoken English.' },
    { question: 'Can "while" mean "although"?', answer: 'Yes. "While" can also mean "although" or "whereas" to show contrast, as in "While I understand your point, I disagree." This is a separate use from the time meaning covered on this page.' },
  ],
  related: [
    { to: '/what-is-the-difference/until-vs-by/', text: 'Until vs. By' },
    { to: '/what-is-the-difference/for-vs-since/', text: 'For vs. Since' },
    { to: '/what-is-the-difference/in-time-vs-on-time/', text: 'In Time vs. On Time' },
    { to: '/grammar-mistakes/during-vs-for-vs-while/', text: 'During vs. For vs. While (Grammar Mistakes)' },
  ],
};

const DuringVsWhilePage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default DuringVsWhilePage;
