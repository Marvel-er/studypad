import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Between vs. Among: What's the Difference? | TypoGrammar",
  metaDescription: "Between vs among: \"between\" is used for two distinct, individually identified things; \"among\" is used for three or more things treated as a group. See the rule, examples, and a quiz.",
  slug: 'between-vs-among',
  h1: "Between vs. Among: What's the Difference?",
  breadcrumbLabel: 'Between vs. Among',
  datePublished: '2026-07-04',
  dateModified: '2026-07-04',
  quickAnswer: "\"Between\" is used for two clearly separate, individually identified people or things (between you and me). \"Among\" is used for three or more things treated as a group or mass, without naming each one separately (among the crowd). The key test is not the number, but whether each item is named individually (between) or treated as part of a group (among).",
  tableColumns: ['Between', 'Among'],
  tableRows: [
    { feature: 'Typical number', values: ['Two distinct items', 'Three or more, as a group'] },
    { feature: 'Items named individually?', values: ['Yes', 'No — treated collectively'] },
    { feature: 'Example', values: ['between the two doors', 'among the doors in the hallway'] },
    { feature: 'Common use', values: ['Relationships, choices, positions', 'Belonging, distribution, comparison within a group'] },
  ],
  terms: [
    {
      label: 'Between',
      summary: 'Used for two (or a small, individually named) set of separate things.',
      pattern: 'between + A and B',
      examples: ['"between the two of us"', '"choose between tea and coffee"', '"between France, Germany, and Italy" (each named)'],
    },
    {
      label: 'Among',
      summary: 'Used for three or more things treated as one undivided group.',
      pattern: 'among + group (plural/mass noun)',
      examples: ['"among the students"', '"hidden among the trees"', '"popular among teenagers"'],
    },
  ],
  grammarRule: 'Use "between" when the items are individually identified — even if there are more than two (between the five candidates). Use "among" when the items are treated as one collective group rather than named separately (among the candidates).',
  extraRule: 'A simple classroom rule that works almost every time: 2 items = between, 3+ items as one group = among. Use the "individually named" test only for advanced or exam-level precision.',
  mistakes: [
    { incorrect: 'Please divide the pizza among the two of you.', correct: 'Please divide the pizza between the two of you.', note: 'Only two people are involved, so it needs "between", not "among".' },
    { incorrect: 'The prize will be shared between all the winners.', correct: 'The prize will be shared among all the winners.', note: '"all the winners" is a collective group (likely 3+), so it needs "among".' },
    { incorrect: 'There is a strong bond among the two sisters.', correct: 'There is a strong bond between the two sisters.' },
  ],
  correctExamples: [
    'You have to choose between the blue shirt and the red one.',
    'The treasure was buried among the rocks on the beach.',
    'There was heated debate between the two lawyers.',
    'The tradition is still common among older generations.',
    'The award was split between the two co-authors.',
    'She felt at home among people who shared her interests.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: "The negotiation is _____ the two companies."', answer: 'between', explanation: 'Only two companies are involved, so it needs "between".' },
    { prompt: 'Choose the correct word: "The rumor spread quickly _____ the employees."', answer: 'among', explanation: '"the employees" is treated as one collective group, so it needs "among".' },
    { prompt: 'Fix the sentence: "Keep this secret among you and me."', answer: 'Keep this secret between you and me.', explanation: 'Only two people ("you and me") are named individually, so it needs "between".' },
  ],
  faqs: [
    { question: 'Is it always wrong to use "between" with more than two things?', answer: 'No. "Between" is correct with more than two items when each item is individually named or considered in relation to the others, as in "trade between the United States, Canada, and Mexico." "Among" is used when the group is treated as a single, undifferentiated whole.' },
    { question: 'Is "amongst" the same as "among"?', answer: '"Amongst" is an older, more formal British variant of "among" with an identical meaning. Modern English (especially American English) almost always prefers "among".' },
    { question: 'Which one is correct: "between you and I" or "between you and me"?', answer: '"Between you and me" is correct. "Between" is a preposition, and pronouns after a preposition take the object form ("me"), not the subject form ("I").' },
  ],
  related: [
    { to: '/what-is-the-difference/during-vs-while/', text: 'During vs. While' },
    { to: '/what-is-the-difference/until-vs-by/', text: 'Until vs. By' },
    { to: '/grammar-mistakes/each-of-or-every-of/', text: 'Each of or Every of?' },
  ],
};

const BetweenVsAmongPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default BetweenVsAmongPage;
