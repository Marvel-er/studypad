import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Must vs. Have To: What's the Difference? | TypoGrammar",
  metaDescription: "Must vs have to: \"must\" expresses a personal/internal obligation or strong deduction; \"have to\" expresses an external obligation imposed by a rule or another person. See the rule, examples, and a quiz.",
  slug: 'must-vs-have-to',
  h1: "Must vs. Have To: What's the Difference?",
  breadcrumbLabel: 'Must vs. Have to',
  datePublished: '2026-07-04',
  dateModified: '2026-07-04',
  quickAnswer: "\"Must\" usually expresses a personal, internal obligation — something the speaker believes is necessary (I must call my mom) — or a strong logical conclusion (he must be tired). \"Have to\" expresses an external obligation imposed by someone else, a rule, or a law (I have to wear a uniform at work). \"Must\" has no past tense; \"have to\" changes freely across all tenses.",
  tableColumns: ['Must', 'Have to'],
  tableRows: [
    { feature: 'Source of obligation', values: ['Internal — the speaker\'s own opinion', 'External — a rule, law, or other person'] },
    { feature: 'Past tense form', values: ['None — use "had to" instead', '"had to" (regular in all tenses)'] },
    { feature: 'Negative meaning', values: ['"must not" = prohibited, forbidden', '"don\'t have to" = not necessary, optional'] },
    { feature: 'Example', values: ['I must finish this myself; it matters to me.', 'I have to wear safety goggles; it\'s the law.'] },
  ],
  terms: [
    {
      label: 'Must',
      summary: 'Personal/internal obligation, or a strong logical deduction — no past tense form.',
      pattern: 'must + base verb',
      examples: ['"I must remember to water the plants."', '"He must be exhausted after that trip."', '"You must not touch that; it\'s dangerous."'],
    },
    {
      label: 'Have to',
      summary: 'External obligation from a rule, law, or other person; works in every tense.',
      pattern: 'have/has/had to + base verb',
      examples: ['"Employees have to clock in by 9am."', '"She had to leave early yesterday."', '"We will have to reschedule the meeting."'],
    },
  ],
  grammarRule: '"Must" expresses the speaker\'s own sense of necessity or a confident conclusion, and it has no past form (use "had to" for the past). "Have to" expresses an obligation coming from outside the speaker — a rule, law, schedule, or another person — and it conjugates normally in every tense.',
  extraRule: 'The negatives are not interchangeable: "must not" (mustn\'t) means something is forbidden, while "don\'t have to" means something is simply not required — you are free to do it or not.',
  mistakes: [
    { incorrect: 'Yesterday I must finish the report before noon.', correct: 'Yesterday I had to finish the report before noon.', note: '"Must" has no past tense form; the past of obligation uses "had to".' },
    { incorrect: 'You must not clean your room; it\'s optional.', correct: "You don't have to clean your room; it's optional.", note: '"must not" means forbidden, not "not necessary" — "don\'t have to" is needed here.' },
    { incorrect: 'According to the airline\'s policy, passengers must wear a seatbelt (a strict rule set by the airline).', correct: "According to the airline's policy, passengers have to wear a seatbelt.", note: 'When the obligation clearly comes from an external rule, "have to" is more natural, though "must" is not wrong here.' },
  ],
  correctExamples: [
    'I must call the dentist today; I keep forgetting.',
    'Students have to submit their essays by Friday, according to the syllabus.',
    'You must be starving after that long hike!',
    'We had to wait two hours at the airport yesterday.',
    'You mustn\'t share your password with anyone.',
    'You don\'t have to bring anything; we already have enough food.',
  ],
  quiz: [
    { prompt: 'Choose the correct form for the past: "Last year, employees _____ arrive by 8am."', answer: 'had to', explanation: '"Must" has no past form, so the past of obligation is "had to".' },
    { prompt: 'Choose the correct meaning: "You don\'t have to attend the meeting" means…', answer: "It's optional — attendance is not required.", explanation: '"Don\'t have to" means something is not necessary, unlike "mustn\'t", which means forbidden.' },
    { prompt: 'Fix the sentence: "Visitors must not to pay an entry fee before 10am; it\'s free."', answer: "Visitors don't have to pay an entry fee before 10am; it's free.", explanation: 'The intended meaning is "not required", so it needs "don\'t have to", not "must not".' },
  ],
  faqs: [
    { question: 'Is "must" too strong for everyday requests?', answer: 'It can sound quite direct or formal, so in casual speech people often prefer "have to" or softer alternatives like "need to" for everyday obligations, saving "must" for strong personal feelings, rules in writing, or firm recommendations.' },
    { question: 'Can "must" express certainty instead of obligation?', answer: 'Yes. "Must" is also used for confident logical conclusions, as in "The light is on, so she must be home." This use has nothing to do with obligation — it expresses how sure the speaker is.' },
    { question: 'What is the difference between "have to" and "need to"?', answer: '"Have to" and "need to" are very close in meaning and often interchangeable for obligation ("I have to go" / "I need to go"), though "need to" can sound slightly softer and more focused on necessity for the speaker\'s own goals.' },
  ],
  related: [
    { to: '/what-is-the-difference/may-vs-might/', text: 'May vs. Might' },
    { to: '/what-is-the-difference/can-vs-could/', text: 'Can vs. Could' },
    { to: '/what-is-the-difference/will-vs-be-going-to/', text: 'Will vs. Be Going to' },
  ],
};

const MustVsHaveToPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default MustVsHaveToPage;
