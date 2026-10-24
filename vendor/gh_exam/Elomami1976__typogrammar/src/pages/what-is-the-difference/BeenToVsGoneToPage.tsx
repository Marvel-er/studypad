import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Been to vs. Gone to: What's the Difference? | TypoGrammar",
  metaDescription: "Been to vs gone to: \"have been to\" means someone visited a place and came back; \"have gone to\" means someone is still there or on the way. See the rule, examples, and a quiz.",
  slug: 'been-to-vs-gone-to',
  h1: "Been to vs. Gone to: What's the Difference?",
  breadcrumbLabel: 'Been to vs. Gone to',
  datePublished: '2026-07-04',
  dateModified: '2026-07-04',
  quickAnswer: "\"Have/has been to\" describes a completed visit — the person went somewhere and has already returned (she has been to Japan twice). \"Have/has gone to\" describes someone who is currently away — they left and have not come back yet (she has gone to Japan, so she isn’t here). Mixing them up changes whether the person is present or absent right now.",
  tableColumns: ['Have been to', 'Have gone to'],
  tableRows: [
    { feature: 'Is the person back?', values: ['Yes, they returned', 'No, they are still away'] },
    { feature: 'Describes', values: ['A life experience / completed visit', 'A current absence'] },
    { feature: 'Example', values: ['She has been to Italy three times.', 'She has gone to Italy (she\'s not here now).'] },
    { feature: 'Can it take a number of times?', values: ['Yes: "twice", "three times"', 'Not usually, since it describes one current trip'] },
  ],
  terms: [
    {
      label: 'Have been to',
      summary: 'Describes a visit that is finished — the subject went and returned.',
      pattern: 'have/has + been to + place',
      examples: ['"I have been to Rome before."', '"Have you ever been to Egypt?"', '"She has been to Peru twice."'],
    },
    {
      label: 'Have gone to',
      summary: 'Describes someone who left and is still away — they have not returned.',
      pattern: 'have/has + gone to + place',
      examples: ['"He has gone to the bank." (he\'s not here)', '"They have gone to lunch."', '"Where has she gone to?"'],
    },
  ],
  grammarRule: 'Use "have/has been to" for a completed trip or experience — the traveler is back with you now. Use "have/has gone to" when the traveler is currently at that place or on the way there — not back yet.',
  extraRule: 'If you can add "and now they\'re back" without contradicting the sentence, use "been to". If the sentence explains someone\'s current absence, use "gone to".',
  mistakes: [
    { incorrect: 'She has gone to France five times.', correct: 'She has been to France five times.', note: 'Repeated past visits describe an experience, so it needs "been to", not "gone to".' },
    { incorrect: 'Where is Tom? He has been to the gym, he\'ll be back soon.', correct: "Where is Tom? He has gone to the gym, he'll be back soon.", note: 'Tom is currently away, so it needs "gone to".' },
    { incorrect: 'I have gone to that restaurant many times; it\'s excellent.', correct: "I have been to that restaurant many times; it's excellent." },
  ],
  correctExamples: [
    'Have you ever been to Thailand?',
    'He has gone to the airport to pick up his parents.',
    'We have been to that museum at least four times.',
    'She has gone to bed already, so please be quiet.',
    'I have never been to a live concert before.',
    'They have gone to the market and will be back in an hour.',
  ],
  quiz: [
    { prompt: 'Choose the correct phrase: "I can\'t find Maria anywhere." "Oh, she _____ the store, she\'ll be back in ten minutes."', answer: 'has gone to', explanation: 'Maria is currently away, so it needs "has gone to".' },
    { prompt: 'Choose the correct phrase: "_____ ever _____ New York?" "Yes, twice, and I loved it."', answer: 'Have / been to', explanation: 'This asks about a completed travel experience, so it needs "have been to".' },
    { prompt: 'Fix the sentence: "We have gone to Spain three times on vacation."', answer: 'We have been to Spain three times on vacation.', explanation: 'Repeated completed visits use "been to", not "gone to".' },
  ],
  faqs: [
    { question: 'Can I use "been to" for someone who is still traveling right now?', answer: 'No. If the person has not returned yet, "gone to" is correct. "Been to" is reserved for trips that are already finished, even if the person went more than once in the past.' },
    { question: 'What about "have been in" a place?', answer: '"Have been in [place]" describes staying in a location for a period, often with a duration, as in "I have been in London for three days." It is a slightly different use from "been to", which emphasizes the visit itself rather than the length of stay.' },
    { question: 'Is "gone to" ever used for repeated actions?', answer: 'Rarely, and usually only in specific fixed contexts, like "He has gone to prison twice," where each time he is currently there in that state. For everyday travel experiences, "been to" is almost always correct for repeated visits.' },
  ],
  related: [
    { to: '/what-is-the-difference/may-vs-might/', text: 'May vs. Might' },
    { to: '/what-is-the-difference/must-vs-have-to/', text: 'Must vs. Have to' },
    { to: '/grammar-mistakes/i-have-went-or-have-gone/', text: 'I Have Went or Have Gone?' },
  ],
};

const BeenToVsGoneToPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default BeenToVsGoneToPage;
