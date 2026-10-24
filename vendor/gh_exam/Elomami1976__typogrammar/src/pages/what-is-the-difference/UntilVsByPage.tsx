import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Until vs. By: What's the Difference? | TypoGrammar",
  metaDescription: "Until vs by: \"until\" describes an action that continues up to a point in time; \"by\" describes an action completed no later than a point in time. See the rule, examples, and a quiz.",
  slug: 'until-vs-by',
  h1: "Until vs. By: What's the Difference?",
  breadcrumbLabel: 'Until vs. By',
  datePublished: '2026-07-04',
  dateModified: '2026-07-04',
  quickAnswer: "\"Until\" marks the end point of a continuous action — the action keeps happening up to that moment (I will wait until 5pm). \"By\" marks a deadline for a completed action — the action happens at or before that moment, not continuously (I will finish by 5pm). Choosing the wrong one changes whether an action is ongoing or finished.",
  tableColumns: ['Until', 'By'],
  tableRows: [
    { feature: 'Type of action', values: ['Continuous, ongoing up to a point', 'One-time, completed no later than a point'] },
    { feature: 'Typical verbs', values: ['wait, stay, sleep, work, continue', 'finish, submit, arrive, decide, complete'] },
    { feature: 'Example', values: ['I will stay until 6pm.', 'I will leave by 6pm.'] },
    { feature: 'Answers the question', values: ['"How long?"', '"By when? / No later than when?"'] },
  ],
  terms: [
    {
      label: 'Until',
      summary: 'Marks the end of a continuing, ongoing action or state.',
      pattern: 'until + point in time',
      examples: ['"I will wait here until you arrive."', '"The shop is open until 9pm."', '"She worked until midnight."'],
    },
    {
      label: 'By',
      summary: 'Marks a deadline: something happens at or before this point, not continuously.',
      pattern: 'by + point in time',
      examples: ['"Please finish the report by Friday."', '"We need to decide by tomorrow."', '"The package will arrive by noon."'],
    },
  ],
  grammarRule: 'Use "until" with verbs describing a state or action that continues without stopping up to a certain time. Use "by" with verbs describing a single, completed action that must happen no later than a certain time.',
  extraRule: 'Test it: can you insert "continuously" or "the whole time" before the deadline and keep the meaning? If yes, use "until". If the action is a one-time completion, use "by".',
  mistakes: [
    { incorrect: 'I will finish the report until Friday.', correct: 'I will finish the report by Friday.', note: '"finish" is a one-time completed action, so it needs "by", not "until".' },
    { incorrect: 'Please stay by the meeting ends.', correct: 'Please stay until the meeting ends.', note: '"stay" is a continuous action, so it needs "until", not "by".' },
    { incorrect: 'We need your answer until tomorrow.', correct: 'We need your answer by tomorrow.' },
  ],
  correctExamples: [
    'The store stays open until midnight during the holidays.',
    'Please submit your application by the end of the month.',
    'She waited until the rain stopped before leaving.',
    'I will call you by 3pm at the latest.',
    'He kept practicing until he got it right.',
    'All invoices must be paid by the 5th of each month.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: "You must return the book _____ Friday."', answer: 'by', explanation: '"return the book" is a one-time completed action with a deadline, so it needs "by".' },
    { prompt: 'Choose the correct word: "I will keep working _____ the deadline."', answer: 'until', explanation: '"keep working" is a continuous action, so it needs "until".' },
    { prompt: 'Fix the sentence: "The offer is valid by the end of the week."', answer: 'The offer is valid until the end of the week.', explanation: '"is valid" describes a continuing state, so it needs "until", not "by".' },
  ],
  faqs: [
    { question: 'Can "by" mean the same as "until" in any context?', answer: 'Not usually. Some learners confuse them because both refer to time limits, but "by" always implies a completed action at or before a point, while "until" always implies continuation up to that point. Swapping them changes the meaning of the sentence.' },
    { question: 'What about "by the time"?', answer: '"By the time" introduces a clause and works like "by": it marks a deadline for a completed action, as in "By the time we arrived, the show had already started."' },
    { question: 'Is there a difference between "until" and "till"?', answer: '"Till" is an informal, shorter variant of "until" with the same meaning. "Until" is preferred in formal and written English.' },
  ],
  related: [
    { to: '/what-is-the-difference/during-vs-while/', text: 'During vs. While' },
    { to: '/what-is-the-difference/for-vs-since/', text: 'For vs. Since' },
    { to: '/what-is-the-difference/in-time-vs-on-time/', text: 'In Time vs. On Time' },
  ],
};

const UntilVsByPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default UntilVsByPage;
