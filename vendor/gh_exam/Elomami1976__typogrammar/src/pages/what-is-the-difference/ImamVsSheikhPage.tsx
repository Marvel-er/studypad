import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Imam vs. Sheikh: What's the Difference? | TypoGrammar",
  metaDescription: 'Imam vs sheikh: an "imam" specifically leads congregational prayers in a mosque, while "sheikh" is a broader honorific for a respected scholar, elder, or leader. See the rule, examples, and a quiz.',
  slug: 'imam-vs-sheikh',
  h1: "Imam vs. Sheikh: What's the Difference?",
  breadcrumbLabel: 'Imam vs. Sheikh',
  datePublished: '2026-07-05',
  dateModified: '2026-07-05',
  quickAnswer: 'An "imam" is specifically the person who leads congregational prayers in a mosque and often provides religious guidance to that community. A "sheikh" is a broader title of respect for a knowledgeable, senior figure in Islamic scholarship, a tribal leader, or a respected elder, and does not necessarily involve leading prayers.',
  tableColumns: ['Imam', 'Sheikh'],
  tableRows: [
    { feature: 'Main role', values: ['Leads congregational prayers in a mosque', 'Broad title of respect for a scholar or elder'] },
    { feature: 'Scope of title', values: ['Specific religious leadership role', 'Can apply to scholars, tribal leaders, or respected elders'] },
    { feature: 'How it is earned', values: ["Recognized by a community to lead prayer", 'Earned through knowledge, age, or standing'] },
    { feature: 'Example', values: ['"The imam led the Friday prayer at the mosque."', '"The sheikh was known for his religious scholarship."'] },
  ],
  terms: [
    {
      label: 'Imam',
      summary: 'The person who leads Islamic congregational prayers and often provides religious teaching and guidance to a mosque community.',
      pattern: 'the imam (of + mosque)',
      examples: ['"The imam delivered the Friday sermon."', '"They asked the imam for religious guidance."'],
    },
    {
      label: 'Sheikh',
      summary: 'A title of respect given to a knowledgeable or senior figure in Islamic scholarship, a tribal leader, or an elder, in Arab and Islamic culture.',
      pattern: 'a/the sheikh',
      examples: ['"The sheikh was widely respected for his religious knowledge."', '"Local tribes were led by a sheikh."'],
    },
  ],
  grammarRule: 'Use "imam" specifically for the person who leads prayers in a mosque. Use "sheikh" as a broader honorific for a respected scholar, elder, or leader, which can apply well beyond the role of leading prayer — and many imams are also referred to as sheikhs if they have significant religious standing.',
  extraRule: 'The exact meaning and use of "sheikh" varies by country and context — in some regions it refers mainly to religious scholars, while in others it can also refer to tribal or political leaders.',
  mistakes: [
    { incorrect: 'Only tribal leaders are ever called imams.', correct: 'Tribal leaders may be called sheikhs; imams specifically lead prayers in a mosque.', note: '"Imam" is tied to the prayer-leading role, not tribal leadership.' },
    { incorrect: 'The sheikh led the call to prayer every Friday at the mosque.', correct: 'The imam led the call to prayer every Friday at the mosque.', note: 'Leading prayer at the mosque is specifically the role of an imam.' },
    { incorrect: 'Every sheikh must formally lead prayers to earn the title.', correct: 'A sheikh does not have to lead prayers to earn the title — it can reflect scholarship, age, or leadership instead.', note: '"Sheikh" is a broader honorific, not tied only to leading prayer.' },
  ],
  correctExamples: [
    'The imam guided the congregation through Friday prayers.',
    'The sheikh was consulted by the community on matters of religious law.',
    'Many mosques choose their imam based on his knowledge of the Quran.',
    "The sheikh's wisdom was respected across the entire region.",
    'The imam also served as a teacher for younger members of the community.',
    'Local elders often held the title of sheikh within their community.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: The person who leads the five daily prayers at the mosque is the _____.', answer: 'imam', explanation: 'Leading prayers at the mosque is specifically the role of an imam.' },
    { prompt: 'Choose the correct word: A respected elder known for his religious knowledge, but who does not lead prayers, might be called a _____.', answer: 'sheikh', explanation: '"Sheikh" is a broader honorific for a respected scholar or elder.' },
    { prompt: 'Fix the sentence: "The sheikh performed the call to prayer at the mosque every morning."', answer: 'The imam performed the call to prayer at the mosque every morning.', explanation: 'Leading prayer is specifically the imam\'s role.' },
  ],
  faqs: [
    { question: 'Can an imam also be called a sheikh?', answer: 'Yes — an imam with significant religious knowledge or standing is often also referred to as a sheikh, since the titles can overlap for the same person.' },
    { question: 'Is "sheikh" only a religious title?', answer: 'Not always — depending on the region, "sheikh" can also refer to a tribal leader, a senior family member, or a political figure, in addition to religious scholars.' },
    { question: 'Who chooses an imam?', answer: 'An imam is typically chosen or recognized by the mosque community or its leadership based on his knowledge of Islamic teachings and ability to lead prayer.' },
  ],
  related: [
    { to: '/what-is-the-difference/priest-vs-monk/', text: 'Priest vs. Monk' },
    { to: '/what-is-the-difference/church-vs-cathedral/', text: 'Church vs. Cathedral' },
    { to: '/what-is-the-difference/theism-vs-deism/', text: 'Theism vs. Deism' },
  ],
};

const ImamVsSheikhPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default ImamVsSheikhPage;
