import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Farther vs. Further: What's the Difference? | TypoGrammar",
  metaDescription: "Farther vs further: \"farther\" refers to physical, measurable distance; \"further\" refers to figurative extent, degree, or additional amount. See the rule, examples, and a quiz.",
  slug: 'farther-vs-further',
  h1: "Farther vs. Further: What's the Difference?",
  breadcrumbLabel: 'Farther vs. Further',
  datePublished: '2026-07-04',
  dateModified: '2026-07-04',
  quickAnswer: "Traditionally, \"farther\" describes physical, measurable distance (the store is farther than the bank), while \"further\" describes figurative distance, extent, or degree, and also means \"additional\" (we need further information). In everyday modern English the two overlap a lot, but this distinction is still taught and tested in careful writing and exams.",
  tableColumns: ['Farther', 'Further'],
  tableRows: [
    { feature: 'Type of distance', values: ['Physical, literal, measurable', 'Figurative, abstract, or additional'] },
    { feature: 'Example', values: ['The gas station is farther than I thought.', 'We need further discussion on this topic.'] },
    { feature: 'Can mean "additional"?', values: ['No', 'Yes ("further details", "further questions")'] },
    { feature: 'Used as a verb?', values: ['No', 'Yes ("to further a cause")'] },
  ],
  terms: [
    {
      label: 'Farther',
      summary: 'Describes literal, physical distance that can be measured.',
      pattern: 'farther (than) + physical distance',
      examples: ['"My house is farther from the city than yours."', '"He can throw the ball farther than me."', '"We drove farther than planned."'],
    },
    {
      label: 'Further',
      summary: 'Describes figurative distance, extent, or degree, and also means "additional" or "more".',
      pattern: 'further + noun / further (than)',
      examples: ['"Let\'s discuss this further."', '"I have nothing further to add."', '"She needs further training."'],
    },
  ],
  grammarRule: 'Use "farther" for physical distance you could measure with a ruler, map, or odometer. Use "further" for abstract or figurative extent (ideas, discussions, progress) and whenever the meaning is "additional" or "more", as in "further information" or "further notice".',
  extraRule: 'If in doubt, "further" is the safer, more flexible choice — it can replace "farther" in almost every context, while "farther" cannot replace "further" in figurative or "additional" meanings.',
  mistakes: [
    { incorrect: 'We need to discuss this farther before deciding.', correct: 'We need to discuss this further before deciding.', note: 'This is a figurative, abstract extension of a discussion, so it needs "further".' },
    { incorrect: 'Please provide farther details about your application.', correct: 'Please provide further details about your application.', note: '"Additional" details should use "further", not "farther".' },
    { incorrect: 'The next town is further than I expected, about ten miles away.', correct: 'The next town is farther than I expected, about ten miles away.', note: 'This describes physical, measurable distance, so "farther" is the traditional choice (though "further" is widely accepted too).' },
  ],
  correctExamples: [
    'The airport is farther from downtown than the train station.',
    'Until further notice, the office will remain closed.',
    'He ran farther than anyone else in the race.',
    'I have no further questions for the witness.',
    'She lives farther away now that she moved to the suburbs.',
    'The committee will look further into the matter next week.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: "The lake is a little _____ than the map shows." (physical distance)', answer: 'farther', explanation: 'This is a literal, measurable distance, so "farther" is the traditional choice.' },
    { prompt: 'Choose the correct word: "Without _____ ado, let\'s begin the ceremony." (figurative/additional)', answer: 'further', explanation: '"Additional" delay is a figurative use, so it needs "further".' },
    { prompt: 'Fix the sentence: "I can\'t go farther with this argument; it doesn\'t make sense to me."', answer: "I can't go further with this argument; it doesn't make sense to me.", explanation: 'This is a figurative extension of an argument, so it needs "further", not "farther".' },
  ],
  faqs: [
    { question: 'Is it wrong to use "further" for physical distance?', answer: 'Not really — in modern usage, especially in British English, "further" is commonly used for physical distance too, and many style guides now treat the words as largely interchangeable there. The traditional farther/further split is stricter in American English and formal writing.' },
    { question: 'Can "farther" be used for figurative meanings?', answer: 'This is far less common and generally considered nonstandard. Stick to "further" for anything abstract, additional, or non-physical to stay safe in formal writing and exams.' },
    { question: 'Which one is a comparative adjective and which is used as a verb too?', answer: 'Both "farther" and "further" work as comparative adjectives/adverbs, but only "further" is also used as a verb, meaning to help something progress, as in "to further one\'s career" or "to further world peace."' },
  ],
  related: [
    { to: '/what-is-the-difference/job-vs-work/', text: 'Job vs. Work' },
    { to: '/what-is-the-difference/house-vs-home/', text: 'House vs. Home' },
    { to: '/what-is-the-difference/sensible-vs-sensitive/', text: 'Sensible vs. Sensitive' },
  ],
};

const FartherVsFurtherPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default FartherVsFurtherPage;
