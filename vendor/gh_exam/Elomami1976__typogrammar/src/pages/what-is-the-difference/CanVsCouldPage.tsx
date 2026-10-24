import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Can vs. Could: What's the Difference? | TypoGrammar",
  metaDescription: "Can vs could: \"can\" expresses present ability or permission; \"could\" expresses past general ability, polite requests, and hypothetical possibility. See the rule, examples, and a quiz.",
  slug: 'can-vs-could',
  h1: "Can vs. Could: What's the Difference?",
  breadcrumbLabel: 'Can vs. Could',
  datePublished: '2026-07-04',
  dateModified: '2026-07-04',
  quickAnswer: "\"Can\" expresses present ability, permission, or possibility (I can swim; can I leave early?). \"Could\" expresses past general ability (I could swim when I was five), a more polite or tentative present request (could you help me?), or a hypothetical possibility (I could go, but I'm not sure). \"Could\" is more indirect and softer than \"can\" in almost every use.",
  tableColumns: ['Can', 'Could'],
  tableRows: [
    { feature: 'Time reference', values: ['Present / general truth', 'Past general ability, or present hypothetical'] },
    { feature: 'Requests / permission', values: ['Direct, casual ("Can I sit here?")', 'More polite, indirect ("Could I sit here?")'] },
    { feature: 'Specific past achievement', values: ['Not used for this', 'Not used alone — use "was/were able to" or "managed to"'] },
    { feature: 'Example', values: ['She can speak three languages.', 'She could speak French even as a child.'] },
  ],
  terms: [
    {
      label: 'Can',
      summary: 'Present ability, permission, or general possibility.',
      pattern: 'can + base verb',
      examples: ['"He can play the guitar."', '"Can I open the window?"', '"Traffic can be terrible here."'],
    },
    {
      label: 'Could',
      summary: 'Past general ability, polite requests, or hypothetical possibility.',
      pattern: 'could + base verb',
      examples: ['"I could read before I started school."', '"Could you pass the salt, please?"', '"We could go to the beach this weekend."'],
    },
  ],
  grammarRule: 'Use "can" for present ability, permission, or possibility. Use "could" for general ability in the past, for softer and more polite requests in the present, and for hypothetical or uncertain possibilities.',
  extraRule: 'Important exception: for a single, specific past achievement (not a general ability), avoid "could" and use "was/were able to" or "managed to" instead — for example, "After years of practice, she was able to finish the marathon," not "she could finish the marathon."',
  mistakes: [
    { incorrect: 'Despite the flat tire, he could arrive on time.', correct: 'Despite the flat tire, he was able to arrive on time.', note: 'A single, specific past success should use "was able to", not "could".' },
    { incorrect: 'Can you please to close the door?', correct: 'Could you please close the door?', note: 'Modal verbs like "could" are followed directly by the base verb, with no "to".' },
    { incorrect: 'When I was a child, I can climb trees easily.', correct: 'When I was a child, I could climb trees easily.', note: 'General ability in the past needs "could", not "can".' },
  ],
  correctExamples: [
    'I can drive, but I don\'t have a car right now.',
    'My grandmother could dance beautifully when she was young.',
    'Can I ask you something?',
    'Could you possibly help me carry these boxes?',
    'It can get very cold here in winter.',
    'We could try that new restaurant tonight, if you\'re free.',
  ],
  quiz: [
    { prompt: 'Choose the more polite request: "_____ you open the window, please?"', answer: 'Could', explanation: '"Could" sounds softer and more polite than "can" for requests.' },
    { prompt: 'Choose the correct word: "As a teenager, she _____ run five kilometers without stopping."', answer: 'could', explanation: 'This describes a general past ability, so it needs "could".' },
    { prompt: 'Fix the sentence: "After months of training, he could finally run a marathon."', answer: 'After months of training, he was able to finally run a marathon.', explanation: 'This is a single, specific past achievement, so "was able to" is needed instead of "could".' },
  ],
  faqs: [
    { question: 'Why can\'t I use "could" for a specific past success?', answer: 'In standard English, "could" describes a general capacity that existed over a period of time, not a single completed event. For one specific success (passing a test, winning a race, escaping danger), native speakers use "was/were able to" or "managed to" instead.' },
    { question: 'Is "could" always more polite than "can"?', answer: 'In requests, yes — "could" sounds softer and more indirect than "can", which is why it\'s common in polite or formal situations, such as speaking to a stranger, a customer, or a superior.' },
    { question: 'Can "could" refer to the future?', answer: 'Yes, "could" often expresses a present or future possibility that is uncertain or hypothetical, as in "We could go camping next month if the weather is nice" — this is not about the past at all.' },
  ],
  related: [
    { to: '/what-is-the-difference/must-vs-have-to/', text: 'Must vs. Have to' },
    { to: '/what-is-the-difference/may-vs-might/', text: 'May vs. Might' },
    { to: '/what-is-the-difference/will-vs-be-going-to/', text: 'Will vs. Be Going to' },
  ],
};

const CanVsCouldPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default CanVsCouldPage;
