import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Fact vs. Truth: What's the Difference? | TypoGrammar",
  metaDescription: 'Fact vs truth: a "fact" is a piece of information that can be objectively proven, while "truth" is the broader concept of what is real or accurate, which can include personal perspective. See the rule, examples, and a quiz.',
  slug: 'fact-vs-truth',
  h1: "Fact vs. Truth: What's the Difference?",
  breadcrumbLabel: 'Fact vs. Truth',
  datePublished: '2026-07-05',
  dateModified: '2026-07-05',
  quickAnswer: 'A "fact" is a piece of information that can be objectively proven or verified — it doesn\'t depend on personal belief or perspective. "Truth" is a broader concept referring to what is real or accurate, which can sometimes include subjective or personal elements (someone\'s "own truth" or experience), even when it isn\'t a strictly provable, checkable fact.',
  tableColumns: ['Fact', 'Truth'],
  tableRows: [
    { feature: 'Provable', values: ['Yes — can be checked/verified objectively', 'Not always — can include subjective or personal reality'] },
    { feature: 'Scope', values: ['Specific, concrete pieces of information', 'Broader concept of what is real or accurate'] },
    { feature: 'Example', values: ['"Water boils at 100°C at sea level."', '"Speaking your truth" (personal experience/perspective)'] },
    { feature: 'Changes with perspective', values: ['No — a verified fact stays a fact', 'Can vary by viewpoint, especially in personal use'] },
  ],
  terms: [
    {
      label: 'Fact',
      summary: 'A specific piece of information that can be objectively verified, independent of personal belief.',
      pattern: 'a fact (about + topic)',
      examples: ['"It is a fact that the Earth orbits the sun."', '"She checked the facts before publishing the article."'],
    },
    {
      label: 'Truth',
      summary: 'The broader concept of what is real or accurate, which can include verifiable facts as well as personal experience or perspective.',
      pattern: 'the truth (about + topic)',
      examples: ['"He finally told the truth about what happened."', '"Everyone has their own truth based on experience."'],
    },
  ],
  grammarRule: 'Use "fact" for specific, objectively verifiable information. Use "truth" for the broader idea of what is real or accurate overall, which in everyday and philosophical language can also include personal perspective or experience, unlike a strictly checkable fact.',
  extraRule: 'Not every statement someone believes counts as a fact — facts require external verification, while truth, in its broader, personal sense, can be based on individual experience or belief.',
  mistakes: [
    { incorrect: "His opinion about the movie is a fact everyone must accept.", correct: 'His opinion about the movie is his truth, not a fact everyone must accept.', note: 'An opinion cannot be a verifiable fact, but it can be described as someone\'s personal truth.' },
    { incorrect: '"The Earth is round" is just someone\'s personal truth.', correct: '"The Earth is round" is a fact, not just someone\'s personal truth.', note: 'A statement that can be objectively verified is a fact, not merely a personal perspective.' },
    { incorrect: 'Facts can change depending on who you ask.', correct: 'Verified facts do not change depending on who you ask, though people\'s sense of truth can differ.', note: 'A fact stays true regardless of who is asked, unlike more subjective notions of truth.' },
  ],
  correctExamples: [
    'It is a fact that water freezes at zero degrees Celsius.',
    'She finally admitted the truth about the missing money.',
    'The report was fact-checked before it was published.',
    'Everyone experiences grief differently, and that is part of their truth.',
    'The scientist presented the facts clearly, without opinion.',
    'The documentary explored both the facts and the emotional truth of the event.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: The textbook stated the _____ that the human body has 206 bones.', answer: 'fact', explanation: 'A specific, verifiable piece of information is a fact.' },
    { prompt: 'Choose the correct word: After years of silence, she finally shared the _____ about her childhood.', answer: 'truth', explanation: 'A broader, personal reality being revealed is described as the truth.' },
    { prompt: 'Fix the sentence: "It is just a fact that some people find spicy food more enjoyable than others."', answer: 'It is just a truth (or a matter of personal experience) that some people find spicy food more enjoyable than others.', explanation: 'A subjective, personal difference is not a strictly verifiable fact.' },
  ],
  faqs: [
    { question: 'Can a fact ever be wrong?', answer: 'What is presented as a fact can later be shown to be incorrect if new evidence emerges, but a genuinely verified fact, by definition, remains accurate.' },
    { question: 'Is "your truth" the same as a fact?', answer: 'Not necessarily — "your truth" often refers to your personal experience or perspective, which may not be independently verifiable the way a fact is.' },
    { question: 'How do facts and truth relate in journalism?', answer: 'Good journalism aims to report verified facts accurately while also conveying the broader truth of a situation, including context and impact that a single fact alone might not capture.' },
  ],
  related: [
    { to: '/what-is-the-difference/problem-vs-issue/', text: 'Problem vs. Issue' },
    { to: '/what-is-the-difference/trauma-vs-sadness/', text: 'Trauma vs. Sadness' },
    { to: '/what-is-the-difference/iq-vs-intelligence/', text: 'IQ vs. Intelligence' },
  ],
};

const FactVsTruthPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default FactVsTruthPage;
