import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Hear vs. Listen: What's the Difference? | TypoGrammar",
  metaDescription: "Hear vs listen: \"hear\" means to perceive sound without trying; \"listen (to)\" means to pay deliberate attention to a sound. See the rule, examples, and a quiz.",
  slug: 'hear-vs-listen',
  h1: "Hear vs. Listen: What's the Difference?",
  breadcrumbLabel: 'Hear vs. Listen',
  datePublished: '2026-07-04',
  dateModified: '2026-07-04',
  quickAnswer: "\"Hear\" means sound reaches your ears without any effort — it's involuntary (I heard a noise outside). \"Listen (to)\" means you pay deliberate, focused attention to a sound (I listened to the whole album). \"Hear\" is passive perception; \"listen\" is an active choice, and it needs \"to\" before an object.",
  tableColumns: ['Hear', 'Listen (to)'],
  tableRows: [
    { feature: 'Type of action', values: ['Involuntary, passive perception', 'Voluntary, deliberate attention'] },
    { feature: 'Grammar with object', values: ['hear + object (no preposition)', 'listen + to + object'] },
    { feature: 'Example', values: ['I heard a strange noise.', 'I listened to the noise carefully.'] },
    { feature: 'Typical use', values: ['Sudden sounds, ability to hear', 'Music, podcasts, advice, lectures'] },
  ],
  terms: [
    {
      label: 'Hear',
      summary: 'Perceiving sound without effort — it just happens to your ears.',
      pattern: 'hear + object (no preposition)',
      examples: ['"I heard a car horn outside."', '"Can you hear me?"', '"She can\'t hear very well in her left ear."'],
    },
    {
      label: 'Listen (to)',
      summary: 'Choosing to pay attention to a sound on purpose.',
      pattern: 'listen + to + object',
      examples: ['"I listen to podcasts every morning."', '"Please listen to your teacher."', '"He was listening carefully to the instructions."'],
    },
  ],
  grammarRule: '"Hear" describes sound reaching your ears passively — no effort or attention required, and no preposition before the object. "Listen" describes actively focusing on a sound, and it must be followed by "to" before the object ("listen to music", not "listen music").',
  extraRule: 'Because "hear" is normally a stative verb (describing a state, not an action in progress), avoid the progressive form "I am hearing" for simple perception — use the simple present or past instead ("I hear you", "I heard a noise").',
  mistakes: [
    { incorrect: 'I am hearing music right now, do you want to join?', correct: "I am listening to music right now, do you want to join?", note: 'This is a deliberate, ongoing activity, so it needs "listening to", not "hearing".' },
    { incorrect: 'Please listen the instructions carefully.', correct: 'Please listen to the instructions carefully.', note: '"Listen" always needs "to" before its object.' },
    { incorrect: 'Did you listen that strange noise last night?', correct: 'Did you hear that strange noise last night?', note: 'A sudden, unintentional sound is something you "hear", not "listen to".' },
  ],
  correctExamples: [
    'I heard someone knock on the door.',
    'She listens to the radio every morning while getting ready.',
    'Sorry, I can\'t hear you — the connection is bad.',
    'He never listens to anyone\'s advice.',
    'We heard thunder in the distance.',
    'Listen carefully to the announcement before boarding.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: "I _____ a loud bang from the kitchen just now."', answer: 'heard', explanation: 'A sudden, unintentional sound uses "hear", not "listen".' },
    { prompt: 'Choose the correct word: "Every night before bed, she _____ soft music to help her relax."', answer: 'listens to', explanation: 'This is a deliberate activity, and "listen" needs "to" before its object.' },
    { prompt: 'Fix the sentence: "I never hear to podcasts during my commute."', answer: 'I never listen to podcasts during my commute.', explanation: 'A deliberate activity like listening to podcasts needs "listen to", not "hear".' },
  ],
  faqs: [
    { question: 'Can I say "I\'m listening" without "to"?', answer: 'Yes, when there is no object mentioned, "listen" can stand alone, as in "I\'m listening" (meaning you are paying attention). "To" is only required when you name what you are listening to.' },
    { question: 'Is "hear" ever used deliberately, like "hear a case in court"?', answer: 'Yes, in formal or legal contexts, "hear" can describe an official, deliberate act of listening, as in "The judge will hear the case tomorrow." This is a specialized use separate from everyday, passive hearing.' },
    { question: 'What does "I hear you" mean in casual conversation?', answer: 'Informally, "I hear you" is used to show you understand and acknowledge what someone said or how they feel, even beyond literally perceiving the sound of their voice.' },
  ],
  related: [
    { to: '/what-is-the-difference/see-vs-look-vs-watch/', text: 'See vs. Look vs. Watch' },
    { to: '/what-is-the-difference/remember-vs-remind/', text: 'Remember vs. Remind' },
    { to: '/grammar-mistakes/listen-vs-hear/', text: 'Listen vs. Hear (Grammar Mistakes)' },
  ],
};

const HearVsListenPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default HearVsListenPage;
