import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Because vs. Because Of: What's the Difference? | TypoGrammar",
  metaDescription: "Because vs because of: \"because\" is a conjunction followed by a clause (because it rained); \"because of\" is a preposition followed by a noun (because of the rain). Rules, examples, and a quiz.",
  slug: 'because-vs-because-of',
  h1: "Because vs. Because Of: What's the Difference?",
  breadcrumbLabel: 'Because vs. Because Of',
  datePublished: '2026-07-04',
  dateModified: '2026-07-04',
  quickAnswer: "\"Because\" is a conjunction followed by a full clause with a subject and verb (because it was raining). \"Because of\" is a preposition followed by a noun, pronoun, or gerund (because of the rain). Both give a reason, but the grammar after each phrase is different, and mixing them up is one of the most common learner errors.",
  tableColumns: ['Because', 'Because of'],
  tableRows: [
    { feature: 'Part of speech', values: ['Conjunction', 'Preposition'] },
    { feature: 'Followed by', values: ['A clause (subject + verb)', 'A noun / pronoun / gerund'] },
    { feature: 'Example', values: ['because it was cold', 'because of the cold'] },
    { feature: 'Typical position', values: ['Joins two clauses', 'Introduces a noun phrase'] },
  ],
  terms: [
    {
      label: 'Because',
      summary: 'A subordinating conjunction that introduces a reason clause.',
      pattern: 'because + subject + verb',
      examples: ['"because it was raining"', '"because she studied hard"', '"because I forgot my keys"'],
    },
    {
      label: 'Because of',
      summary: 'A two-word preposition that introduces a noun, pronoun, or gerund.',
      pattern: 'because of + noun/gerund',
      examples: ['"because of the rain"', '"because of her hard work"', '"because of forgetting my keys"'],
    },
  ],
  grammarRule: '"Because" needs a clause (a subject and a verb) after it. "Because of" needs a noun, pronoun, or -ing form (gerund) after it — never a full clause.',
  extraRule: 'A fast check: if what follows has its own verb, use "because". If what follows is just a thing, a name, or an -ing word acting like a noun, use "because of".',
  mistakes: [
    { incorrect: 'The game was cancelled because of it was raining.', correct: 'The game was cancelled because it was raining.', note: '"it was raining" is a clause, so it needs "because", not "because of".' },
    { incorrect: 'She was late because the traffic.', correct: 'She was late because of the traffic.', note: '"the traffic" is a noun phrase, so it needs "because of".' },
    { incorrect: 'He passed the exam because of he studied every day.', correct: 'He passed the exam because he studied every day.' },
  ],
  correctExamples: [
    'We stayed home because it was snowing heavily.',
    'We stayed home because of the heavy snow.',
    'She got the promotion because she worked so hard.',
    'She got the promotion because of her hard work.',
    'The flight was delayed because of a technical problem.',
    'The flight was delayed because a warning light came on.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: "The trip was cancelled _____ the storm."', answer: 'because of', explanation: '"the storm" is a noun phrase, so it needs "because of".' },
    { prompt: 'Choose the correct word: "The trip was cancelled _____ a storm was approaching."', answer: 'because', explanation: '"a storm was approaching" is a clause, so it needs "because".' },
    { prompt: 'Fix the sentence: "He failed the test because of he didn\'t study."', answer: "He failed the test because he didn't study.", explanation: '"he didn\'t study" is a clause, so "because of" must become "because".' },
  ],
  faqs: [
    { question: 'Is "because of" a preposition or two words joined together?', answer: '"Because of" functions as a single compound preposition. Grammatically it behaves exactly like other prepositions (such as "due to" or "owing to"): it must be followed by a noun, pronoun, or gerund, never by a full clause.' },
    { question: 'Can I start a sentence with "because"?', answer: 'Yes. "Because it was late, we went home" is correct as long as the "because" clause is followed by a main clause. This is a common style myth — starting a sentence with "because" is grammatically fine.' },
    { question: 'What is the difference between "because of" and "due to"?', answer: '"Because of" and "due to" are used the same way grammatically (both need a noun after them), though traditional style guides prefer "due to" after a form of "to be" (the delay was due to rain) and "because of" elsewhere. In everyday and IELTS/TOEFL writing, both are widely accepted.' },
  ],
  related: [
    { to: '/what-is-the-difference/during-vs-while/', text: 'During vs. While' },
    { to: '/what-is-the-difference/for-vs-since/', text: 'For vs. Since' },
    { to: '/what-is-the-difference/until-vs-by/', text: 'Until vs. By' },
  ],
};

const BecauseVsBecauseOfPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default BecauseVsBecauseOfPage;
