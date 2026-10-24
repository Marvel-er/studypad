import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "For vs. Since: What's the Difference? | TypoGrammar",
  metaDescription: "For vs since: \"for\" is used with a period/duration of time (for three years); \"since\" is used with a starting point in time (since 2020). See the rule, examples, and a quiz.",
  slug: 'for-vs-since',
  h1: "For vs. Since: What's the Difference?",
  breadcrumbLabel: 'For vs. Since',
  datePublished: '2026-07-04',
  dateModified: '2026-07-04',
  quickAnswer: "\"For\" is used with a length or duration of time — how long something has lasted (for three years, for a long time). \"Since\" is used with a starting point in time — when something began (since 2020, since Monday, since I moved here). Both are common with perfect tenses, but they answer different questions: \"for\" answers \"how long?\" and \"since\" answers \"from when?\"",
  tableColumns: ['For', 'Since'],
  tableRows: [
    { feature: 'Answers the question', values: ['How long?', 'From when? / Starting when?'] },
    { feature: 'Followed by', values: ['A duration (three years, a week, ages)', 'A point in time (2020, Monday, I was young)'] },
    { feature: 'Example', values: ['for two hours', 'since 3 o\'clock'] },
    { feature: 'Common tense pairing', values: ['Present perfect / past perfect', 'Present perfect / past perfect'] },
  ],
  terms: [
    {
      label: 'For',
      summary: 'Used with a period or duration of time — a length of time, not a specific starting moment.',
      pattern: 'for + duration',
      examples: ['"for three years"', '"for a long time"', '"for two weeks"'],
    },
    {
      label: 'Since',
      summary: 'Used with a specific starting point in time — a date, event, or moment.',
      pattern: 'since + point in time',
      examples: ['"since 2020"', '"since I graduated"', '"since last Monday"'],
    },
  ],
  grammarRule: 'Use "for" before a length of time (an amount, like "three years" or "a while"). Use "since" before a fixed point in time (a date, day, event, or clause describing when something started), typically with the present perfect or past perfect tense.',
  extraRule: 'Quick test: if the phrase answers "how much time?", use "for". If it answers "starting from when?", use "since".',
  mistakes: [
    { incorrect: 'I have lived here since three years.', correct: 'I have lived here for three years.', note: '"three years" is a duration, so it needs "for", not "since".' },
    { incorrect: 'She has worked here for 2019.', correct: 'She has worked here since 2019.', note: '"2019" is a fixed point in time, so it needs "since", not "for".' },
    { incorrect: 'We haven\'t spoken since a long time.', correct: "We haven't spoken for a long time.", note: '"a long time" is a duration, so it needs "for".' },
  ],
  correctExamples: [
    'They have been married for ten years.',
    'They have been married since 2015.',
    'I haven\'t eaten since breakfast.',
    'I haven\'t eaten for six hours.',
    'She has been studying English for two years.',
    'She has been studying English since she was a teenager.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: "We have known each other _____ high school."', answer: 'since', explanation: '"high school" is a starting point in time, so it needs "since".' },
    { prompt: 'Choose the correct word: "We have known each other _____ ten years."', answer: 'for', explanation: '"ten years" is a duration, so it needs "for".' },
    { prompt: 'Fix the sentence: "He has been unemployed since six months."', answer: 'He has been unemployed for six months.', explanation: '"six months" is a duration, so it needs "for", not "since".' },
  ],
  faqs: [
    { question: 'Can "since" be followed by a clause instead of a date?', answer: 'Yes. "Since" can introduce a time clause, as in "since I moved to this city" or "since she started her new job." The clause describes the starting point, just like a date would.' },
    { question: 'Do "for" and "since" only work with the present perfect tense?', answer: 'No, though that is their most common use. They also appear with the past perfect ("She had lived there for ten years before she moved") and, less often, other tenses when talking about duration or a starting point.' },
    { question: 'Is it correct to say "for a long time ago"?', answer: 'No. "Ago" already marks a point in the past counted back from now (three years ago), so it should not be combined with "for". Use either "for three years" or "three years ago", not both together.' },
  ],
  related: [
    { to: '/what-is-the-difference/until-vs-by/', text: 'Until vs. By' },
    { to: '/what-is-the-difference/during-vs-while/', text: 'During vs. While' },
    { to: '/grammar-mistakes/since-vs-for/', text: 'Since vs. For (Grammar Mistakes)' },
  ],
};

const ForVsSincePage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default ForVsSincePage;
