import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Sensible vs. Sensitive: What's the Difference? | TypoGrammar",
  metaDescription: "Sensible vs sensitive: \"sensible\" means showing good judgment or practicality; \"sensitive\" means easily affected emotionally or physically. See the rule, examples, and a quiz.",
  slug: 'sensible-vs-sensitive',
  h1: "Sensible vs. Sensitive: What's the Difference?",
  breadcrumbLabel: 'Sensible vs. Sensitive',
  datePublished: '2026-07-04',
  dateModified: '2026-07-04',
  quickAnswer: "\"Sensible\" describes good judgment, practicality, or common sense (it was a sensible decision to save some money). \"Sensitive\" describes being easily affected — emotionally, physically, or in reaction to a topic (she is sensitive to criticism; sensitive skin). Despite looking similar, these words describe completely different qualities: one is about wisdom, the other about how easily something is affected.",
  tableColumns: ['Sensible', 'Sensitive'],
  tableRows: [
    { feature: 'Core meaning', values: ['Showing good judgment, practicality', 'Easily affected, emotionally or physically'] },
    { feature: 'Describes', values: ['Decisions, choices, behavior', 'People, skin, topics, information, instruments'] },
    { feature: 'Example', values: ['It was a sensible choice to leave early.', 'He is very sensitive about his weight.'] },
    { feature: 'Opposite', values: ['foolish, unwise, impractical', 'insensitive, thick-skinned, tough'] },
  ],
  terms: [
    {
      label: 'Sensible',
      summary: 'Showing practical, reasonable judgment — making smart, wise choices.',
      pattern: 'sensible + noun / it is sensible to + verb',
      examples: ['"It was sensible of her to bring an umbrella."', '"He gave me some sensible advice."', '"That\'s a sensible plan."'],
    },
    {
      label: 'Sensitive',
      summary: 'Easily affected or hurt — emotionally, physically, or in reaction to sensitive subjects.',
      pattern: 'sensitive + to/about + noun',
      examples: ['"She\'s quite sensitive to criticism."', '"I have sensitive skin, so I avoid strong soaps."', '"This is a sensitive topic for many people."'],
    },
  ],
  grammarRule: '"Sensible" means practical and wise — related to good judgment and common sense. "Sensitive" means easily affected, hurt, or reactive — related to emotions, physical reactions, or delicate topics. They are false friends in several other languages, which is why learners often mix them up.',
  extraRule: 'If the sentence is about a good, practical decision, use "sensible". If the sentence is about feelings being easily hurt, allergic skin, or a delicate subject, use "sensitive".',
  mistakes: [
    { incorrect: 'She is very sensible about criticism; she cries easily.', correct: 'She is very sensitive about criticism; she cries easily.', note: 'This is about emotional reaction, so it needs "sensitive", not "sensible".' },
    { incorrect: 'He made a sensitive decision to save money for retirement.', correct: 'He made a sensible decision to save money for retirement.', note: 'This is about good judgment, so it needs "sensible", not "sensitive".' },
    { incorrect: 'My skin is very sensible to the sun; I burn quickly.', correct: 'My skin is very sensitive to the sun; I burn quickly.' },
  ],
  correctExamples: [
    'It would be sensible to book your flights early.',
    'He\'s very sensitive to loud noises.',
    'Wearing a seatbelt is just sensible.',
    'This is a sensitive subject, so please be careful how you bring it up.',
    'She gave some sensible tips on managing money.',
    'The instrument is sensitive enough to detect tiny changes in temperature.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: "Bringing extra water on a long hike is very _____." (practical judgment)', answer: 'sensible', explanation: 'This is about good, practical judgment, so it needs "sensible".' },
    { prompt: 'Choose the correct word: "He\'s quite _____ about comments regarding his work." (easily affected emotionally)', answer: 'sensitive', explanation: 'This is about being easily affected emotionally, so it needs "sensitive".' },
    { prompt: 'Fix the sentence: "That was a sensitive choice; you avoided a costly mistake."', answer: 'That was a sensible choice; you avoided a costly mistake.', explanation: 'This is about a wise, practical decision, so it needs "sensible", not "sensitive".' },
  ],
  faqs: [
    { question: 'Why do learners confuse "sensible" and "sensitive" so often?', answer: 'In several languages, a word that looks like "sensible" (such as French "sensible" or Spanish "sensible") actually means "sensitive" in English, not "practical/wise" — this is a classic "false friend" that causes confusion for many learners.' },
    { question: 'Can a person be described as both sensible and sensitive?', answer: 'Yes — someone can make wise, practical decisions (sensible) while also being emotionally responsive or easily affected by criticism (sensitive). The two traits are unrelated and can appear in the same person at the same time.' },
    { question: 'What is "sensitive information"?', answer: '"Sensitive information" refers to data that is private, confidential, or potentially damaging if shared improperly, such as medical records or financial details — this use of "sensitive" relates to something requiring careful, delicate handling.' },
  ],
  related: [
    { to: '/what-is-the-difference/farther-vs-further/', text: 'Farther vs. Further' },
    { to: '/what-is-the-difference/house-vs-home/', text: 'House vs. Home' },
    { to: '/grammar-mistakes/sensible-vs-sensitive/', text: 'Sensible vs. Sensitive (Grammar Mistakes)' },
  ],
};

const SensibleVsSensitivePage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default SensibleVsSensitivePage;
