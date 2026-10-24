import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Remember vs. Remind: What's the Difference? | TypoGrammar",
  metaDescription: "Remember vs remind: \"remember\" means to recall something yourself; \"remind\" means to make another person recall something, and it always needs an object. See the rule, examples, and a quiz.",
  slug: 'remember-vs-remind',
  h1: "Remember vs. Remind: What's the Difference?",
  breadcrumbLabel: 'Remember vs. Remind',
  datePublished: '2026-07-04',
  dateModified: '2026-07-04',
  quickAnswer: "\"Remember\" means you recall something in your own mind — no other person is involved (I remember her birthday). \"Remind\" means you cause someone else to remember something — it always needs a person as its object (please remind me to call her). If a person appears right after the verb, you almost certainly need \"remind\", not \"remember\".",
  tableColumns: ['Remember', 'Remind'],
  tableRows: [
    { feature: 'Who recalls?', values: ['The subject, on their own', 'Another person, caused by the subject'] },
    { feature: 'Object needed?', values: ['Optional (the thing remembered)', 'Required (the person reminded)'] },
    { feature: 'Example', values: ['I remember your name.', 'Remind me of your name later.'] },
    { feature: 'Typical pattern', values: ['remember + thing/to do/-ing', 'remind + person + to do / of / that'] },
  ],
  terms: [
    {
      label: 'Remember',
      summary: 'The subject recalls something from their own memory.',
      pattern: 'remember + noun / to + verb / -ing',
      examples: ['"I remember my first day of school."', '"Remember to lock the door."', '"I remember visiting that castle as a kid."'],
    },
    {
      label: 'Remind',
      summary: 'The subject causes another person to remember something — always needs a person as the object.',
      pattern: 'remind + person + to + verb / of + noun / that + clause',
      examples: ['"Remind me to buy milk."', '"She reminds me of my sister."', '"Please remind him that the meeting moved."'],
    },
  ],
  grammarRule: '"Remember" is something you do for yourself — no other person needed. "Remind" is something you do to someone else, so it must always be followed by a person as its object, then "to + verb", "of + noun", or "that + clause".',
  extraRule: 'A quick test: if a person\'s name or a pronoun like "me/him/her/us" comes directly after the verb, you need "remind" ("remind me"), never "remember" ("remember me" would mean something completely different — to keep someone in your memory, as in a farewell).',
  mistakes: [
    { incorrect: 'Please remember me to call my mother tonight.', correct: 'Please remind me to call my mother tonight.', note: 'A person ("me") directly follows the verb, so it needs "remind", not "remember".' },
    { incorrect: 'I always remind that I need my keys before leaving.', correct: 'I always remember that I need my keys before leaving.', note: 'No other person is being made to recall anything here, so it needs "remember".' },
    { incorrect: 'This song remembers me of my childhood.', correct: 'This song reminds me of my childhood.', note: 'The song is causing the speaker to recall something, so it needs "reminds".' },
  ],
  correctExamples: [
    'I still remember the smell of my grandmother\'s kitchen.',
    'Can you remind me to send that email tomorrow?',
    'Do you remember where we parked the car?',
    'This photo reminds her of her wedding day.',
    'I remembered his name just in time.',
    'Please remind the team that the deadline is Friday.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: "Can you _____ me to pick up the dry cleaning?"', answer: 'remind', explanation: 'A person ("me") follows the verb, so it needs "remind".' },
    { prompt: 'Choose the correct word: "I don\'t _____ where I left my glasses."', answer: 'remember', explanation: 'No other person is involved; the subject is recalling something themselves.' },
    { prompt: 'Fix the sentence: "This place remembers me of my hometown."', answer: 'This place reminds me of my hometown.', explanation: 'The place is causing the speaker to recall something, so it needs "reminds".' },
  ],
  faqs: [
    { question: 'Can "remember" ever take a person as its object?', answer: 'Yes, but with a different meaning: "remember me" means to keep someone in your memory or thoughts (often said as a farewell, "Remember me when you\'re famous!"), not to make someone else recall something — that meaning belongs to "remind".' },
    { question: 'What is the structure "remind someone of something"?', answer: '"Remind + person + of + noun/gerund" is used when something triggers a memory or comparison, as in "You remind me of an old friend" or "This smell reminds me of summer."' },
    { question: 'Is "remind" followed by an infinitive or a gerund?', answer: '"Remind" is typically followed by "to + base verb" for an action someone should do in the future ("remind me to call"), not by an -ing form.' },
  ],
  related: [
    { to: '/what-is-the-difference/hear-vs-listen/', text: 'Hear vs. Listen' },
    { to: '/what-is-the-difference/borrow-vs-lend/', text: 'Borrow vs. Lend' },
    { to: '/grammar-mistakes/remember-vs-remind/', text: 'Remember vs. Remind (Grammar Mistakes)' },
  ],
};

const RememberVsRemindPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default RememberVsRemindPage;
