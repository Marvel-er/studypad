import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "In Time vs. On Time: What's the Difference? | TypoGrammar",
  metaDescription: "In time vs on time: \"on time\" means punctual, at the scheduled moment; \"in time\" means early enough, before it's too late. See the rule, examples, and a quiz.",
  slug: 'in-time-vs-on-time',
  h1: "In Time vs. On Time: What's the Difference?",
  breadcrumbLabel: 'In Time vs. On Time',
  datePublished: '2026-07-04',
  dateModified: '2026-07-04',
  quickAnswer: "\"On time\" means punctual — happening exactly at the scheduled or expected moment (the train arrived on time). \"In time (for something / to do something)\" means early enough to avoid missing a deadline or opportunity — with a little time to spare (we arrived just in time for the show). One is about punctuality; the other is about not being too late.",
  tableColumns: ['On time', 'In time'],
  tableRows: [
    { feature: 'Meaning', values: ['Punctual, according to schedule', 'Before it is too late; with time to spare'] },
    { feature: 'Refers to', values: ['A fixed, expected moment', 'A deadline or last possible moment'] },
    { feature: 'Example', values: ['The meeting started on time.', 'We got to the airport just in time.'] },
    { feature: 'Often followed by', values: ['(nothing extra needed)', 'for + noun / to + verb'] },
  ],
  terms: [
    {
      label: 'On time',
      summary: 'Happening at the exact moment that was planned or expected — punctual.',
      pattern: 'on time (no article)',
      examples: ['"The bus arrived on time."', '"She always starts meetings on time."', '"The flight left right on time."'],
    },
    {
      label: 'In time',
      summary: 'Early enough to avoid missing something — not too late, with time to spare.',
      pattern: 'in time (+ for + noun / + to + verb)',
      examples: ['"We arrived in time for the movie."', '"He got to the hospital just in time."', '"I finished in time to catch my flight."'],
    },
  ],
  grammarRule: 'Use "on time" to say something happened exactly when scheduled — neither early nor late. Use "in time" to say something happened before a deadline or before it was too late, often with "for + noun" or "to + verb" attached.',
  extraRule: 'A useful test: if you can add "just before it was too late" to the sentence without changing the meaning, use "in time". If the sentence is really about punctuality and schedules, use "on time".',
  mistakes: [
    { incorrect: 'The train arrived in time, exactly at 9:00 as scheduled.', correct: 'The train arrived on time, exactly at 9:00 as scheduled.', note: 'This is about punctuality according to a schedule, so it needs "on time".' },
    { incorrect: 'We got to the station on time to catch the last train, just before the doors closed.', correct: 'We got to the station in time to catch the last train, just before the doors closed.', note: 'This is about arriving before it was too late, so it needs "in time".' },
    { incorrect: 'He finished the exam on time to check his answers again.', correct: 'He finished the exam in time to check his answers again.' },
  ],
  correctExamples: [
    'The plane landed right on time, at 6:45pm.',
    'We got home just in time before the storm started.',
    'She always pays her bills on time.',
    'The doctor arrived in time to save the patient.',
    'The meeting will start on time, so please don\'t be late.',
    'He reached the station in time for the last train.',
  ],
  quiz: [
    { prompt: 'Choose the correct phrase: "Don\'t worry, the bus is always _____; it never leaves early or late."', answer: 'on time', explanation: 'This describes punctuality according to a fixed schedule, so it needs "on time".' },
    { prompt: 'Choose the correct phrase: "We ran the last block and got there _____ to see the fireworks start."', answer: 'in time', explanation: 'This is about arriving before it was too late, so it needs "in time".' },
    { prompt: 'Fix the sentence: "The ambulance arrived in time, exactly at the moment scheduled."', answer: 'The ambulance arrived on time, exactly at the moment scheduled.', explanation: 'A fixed, scheduled moment needs "on time".' },
  ],
  faqs: [
    { question: 'Can something be "on time" and "in time" at once?', answer: 'Yes. If a scheduled train arrives exactly as planned, and that also lets you catch your connection before it leaves, you could say it arrived "on time" and, as a result, you were "in time" for your connection — but each phrase is still describing a different idea (punctuality vs. not being too late).' },
    { question: 'Is "just in time" a fixed expression?', answer: 'Yes. "Just in time" is a very common collocation meaning "at the last possible moment, right before it would have been too late," as in "We finished the project just in time for the deadline."' },
    { question: 'Does "on time" ever take an article, like "on the time"?', answer: 'No. "On time" is a fixed expression with no article. Adding "the" ("on the time") is incorrect.' },
  ],
  related: [
    { to: '/what-is-the-difference/until-vs-by/', text: 'Until vs. By' },
    { to: '/what-is-the-difference/for-vs-since/', text: 'For vs. Since' },
    { to: '/what-is-the-difference/during-vs-while/', text: 'During vs. While' },
  ],
};

const InTimeVsOnTimePage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default InTimeVsOnTimePage;
