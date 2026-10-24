import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Borrow vs. Lend: What's the Difference? | TypoGrammar",
  metaDescription: "Borrow vs lend: \"borrow\" means to take something temporarily from someone; \"lend\" means to give something temporarily to someone. See the rule, examples, and a quiz.",
  slug: 'borrow-vs-lend',
  h1: "Borrow vs. Lend: What's the Difference?",
  breadcrumbLabel: 'Borrow vs. Lend',
  datePublished: '2026-07-04',
  dateModified: '2026-07-04',
  quickAnswer: "\"Borrow\" means you take something from someone else temporarily — the action is seen from the receiver's side (can I borrow your pen?). \"Lend\" means you give something to someone else temporarily — the action is seen from the giver's side (can you lend me your pen?). Both describe the same event, but from opposite directions.",
  tableColumns: ['Borrow', 'Lend'],
  tableRows: [
    { feature: 'Direction', values: ['Take from someone (receiver\'s view)', 'Give to someone (giver\'s view)'] },
    { feature: 'Preposition with source/receiver', values: ['borrow something FROM someone', 'lend something TO someone / lend someone something'] },
    { feature: 'Example', values: ['I borrowed a book from the library.', 'The library lent me a book.'] },
    { feature: 'Who initiates the request?', values: ['The person who wants the item', 'The person who owns the item'] },
  ],
  terms: [
    {
      label: 'Borrow',
      summary: 'Take something temporarily, with the intention of returning it.',
      pattern: 'borrow + thing (+ from + person)',
      examples: ['"Can I borrow your umbrella?"', '"I borrowed some money from my brother."', '"She borrowed a pen from a classmate."'],
    },
    {
      label: 'Lend',
      summary: 'Give something to someone temporarily, expecting it back.',
      pattern: 'lend + person + thing / lend + thing + to + person',
      examples: ['"Can you lend me your umbrella?"', '"My brother lent me some money."', '"She lent her notes to a classmate."'],
    },
  ],
  grammarRule: '"Borrow" is used from the perspective of the person receiving the item (borrow something FROM someone). "Lend" is used from the perspective of the person giving the item (lend someone something, or lend something TO someone). They describe the same transaction from opposite sides.',
  extraRule: 'A simple memory trick: you borrow FROM a person, but you lend TO a person (or lend a person something directly, with no preposition needed in that word order).',
  mistakes: [
    { incorrect: 'Can you borrow me your car this weekend?', correct: 'Can you lend me your car this weekend?', note: 'The listener is being asked to give something, so it needs "lend", not "borrow".' },
    { incorrect: 'I lent his charger yesterday because mine broke.', correct: 'I borrowed his charger yesterday because mine broke.', note: 'The speaker took the charger, so it needs "borrowed", not "lent".' },
    { incorrect: 'She borrowed me twenty dollars last week.', correct: 'She lent me twenty dollars last week.', note: 'She gave the money, so it needs "lent", not "borrowed".' },
  ],
  correctExamples: [
    'I borrowed my sister\'s laptop for the weekend.',
    'My sister lent me her laptop for the weekend.',
    'Could I borrow a pen, please?',
    'Could you lend me a pen, please?',
    'Banks lend money to people who want to buy a house.',
    'Many students borrow money to pay for university.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: "I need to _____ some money from my parents this month."', answer: 'borrow', explanation: 'The speaker is taking money, so it needs "borrow".' },
    { prompt: 'Choose the correct word: "Could you _____ me your notes from yesterday\'s class?"', answer: 'lend', explanation: 'The listener is being asked to give something, so it needs "lend".' },
    { prompt: 'Fix the sentence: "He always borrows his tools to his neighbors."', answer: 'He always lends his tools to his neighbors.', explanation: 'He is giving his tools to others, so it needs "lends", not "borrows".' },
  ],
  faqs: [
    { question: 'Is "loan" the same as "lend"?', answer: 'As a verb, "loan" is used the same way as "lend" (especially in American English, for money: "The bank loaned her $5,000"). As a noun, "loan" refers to the thing that was lent, as in "I took out a loan."' },
    { question: 'Can "borrow" be used without "from"?', answer: 'Yes, "from" can be dropped when the source is clear or unimportant, as in "Can I borrow a pen?" — you don\'t need to say "from you" because it\'s obvious from context.' },
    { question: 'What preposition goes with "lend"?', answer: 'Use "lend + person + thing" (lend me your pen) or "lend + thing + to + person" (lend your pen to me) — both are correct, similar to the patterns for "give".' },
  ],
  related: [
    { to: '/what-is-the-difference/bring-vs-take/', text: 'Bring vs. Take' },
    { to: '/what-is-the-difference/win-vs-beat/', text: 'Win vs. Beat' },
    { to: '/grammar-mistakes/borrow-vs-lend/', text: 'Borrow vs. Lend (Grammar Mistakes)' },
  ],
};

const BorrowVsLendPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default BorrowVsLendPage;
