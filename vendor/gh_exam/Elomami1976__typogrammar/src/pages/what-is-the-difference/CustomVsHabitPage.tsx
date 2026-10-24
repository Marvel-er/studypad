import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Custom vs. Habit: What's the Difference? | TypoGrammar",
  metaDescription: "Custom vs habit: \"custom\" is a traditional practice shared by a society, culture, or group; \"habit\" is a repeated behavior of one individual person. See the rule, examples, and a quiz.",
  slug: 'custom-vs-habit',
  h1: "Custom vs. Habit: What's the Difference?",
  breadcrumbLabel: 'Custom vs. Habit',
  datePublished: '2026-07-04',
  dateModified: '2026-07-04',
  quickAnswer: "\"Custom\" refers to a traditional practice or social convention shared by a culture, community, or group, often passed down over generations (it's a custom to remove your shoes before entering). \"Habit\" refers to an individual person's repeated, often automatic behavior (she has a habit of biting her nails). The key difference is scale: custom belongs to a group; habit belongs to a person.",
  tableColumns: ['Custom', 'Habit'],
  tableRows: [
    { feature: 'Who does it apply to?', values: ['A whole society, culture, or group', 'One individual person'] },
    { feature: 'Origin', values: ['Tradition, shared over generations', 'Personal, repeated behavior'] },
    { feature: 'Example', values: ['It\'s a local custom to greet elders first.', 'He has a habit of checking his phone constantly.'] },
    { feature: 'Typical collocation', values: ['local custom, national custom, wedding custom', 'bad habit, good habit, nervous habit'] },
  ],
  terms: [
    {
      label: 'Custom',
      summary: 'A traditional practice or social convention shared by a group, community, or culture.',
      pattern: 'a/the + custom (of + culture/place)',
      examples: ['"It\'s a Japanese custom to bow when greeting someone."', '"Wedding customs vary widely around the world."', '"Tipping is not a custom in every country."'],
    },
    {
      label: 'Habit',
      summary: 'A repeated, often automatic behavior belonging to one individual person.',
      pattern: 'a + habit (of + -ing)',
      examples: ['"He has a habit of tapping his pen when he\'s nervous."', '"Smoking is a hard habit to break."', '"I\'m trying to build a habit of reading every night."'],
    },
  ],
  grammarRule: 'Use "custom" for a practice shared by a whole group, community, or culture, often rooted in tradition. Use "habit" for a repeated behavior belonging to a single person, which may or may not be shared by others.',
  extraRule: 'A quick test: if the behavior belongs to "people in general in this culture", use "custom". If it belongs to "this one specific person", use "habit".',
  mistakes: [
    { incorrect: 'It\'s my custom to check my email first thing every morning.', correct: 'It\'s my habit to check my email first thing every morning.', note: 'This describes one person\'s individual behavior, so it needs "habit", not "custom".' },
    { incorrect: 'Bowing when greeting is a common habit in Japan.', correct: 'Bowing when greeting is a common custom in Japan.', note: 'This is a shared cultural practice, so it needs "custom", not "habit".' },
    { incorrect: 'She has a strange custom of talking to herself while cooking.', correct: 'She has a strange habit of talking to herself while cooking.' },
  ],
  correctExamples: [
    'It\'s a local custom to bring a small gift when visiting someone\'s home.',
    'He developed a habit of going for a run every morning.',
    'Many wedding customs involve exchanging rings.',
    'Biting your nails is a difficult habit to break.',
    'The custom of celebrating the new year with fireworks is common worldwide.',
    'She has a habit of arriving fifteen minutes early to every meeting.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: "Removing your shoes before entering a home is a common _____ in many Asian countries."', answer: 'custom', explanation: 'This is a shared cultural practice, so it needs "custom".' },
    { prompt: 'Choose the correct word: "My brother has a strange _____ of humming while he works."', answer: 'habit', explanation: 'This describes one individual\'s personal behavior, so it needs "habit".' },
    { prompt: 'Fix the sentence: "Drinking tea at 5pm is a family habit that started with my great-grandmother and is followed by our whole extended family."', answer: 'Drinking tea at 5pm is a family custom that started with my great-grandmother and is followed by our whole extended family.', explanation: 'This is a tradition shared by a whole family/group across generations, so it fits "custom" better than "habit".' },
  ],
  faqs: [
    { question: 'Can "custom" ever refer to just one person?', answer: 'Rarely, but it can describe a personal tradition someone follows consistently, as in "It was his custom to read the newspaper every morning" — even here, the word suggests something more formal or ritualistic than a simple "habit".' },
    { question: 'Is a habit always negative?', answer: 'No. "Habit" is neutral and can describe both good and bad behaviors — "a healthy habit of exercising daily" is just as valid as "a bad habit of procrastinating".' },
    { question: 'What is the difference between "custom" and "tradition"?', answer: '"Custom" often refers to a specific practiced behavior (how people greet each other, what they eat at a festival), while "tradition" is a broader term for beliefs, customs, and practices passed down through generations — a tradition can include many customs.' },
  ],
  related: [
    { to: '/what-is-the-difference/customer-vs-client/', text: 'Customer vs. Client' },
    { to: '/what-is-the-difference/job-vs-work/', text: 'Job vs. Work' },
    { to: '/what-is-the-difference/house-vs-home/', text: 'House vs. Home' },
  ],
};

const CustomVsHabitPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default CustomVsHabitPage;
