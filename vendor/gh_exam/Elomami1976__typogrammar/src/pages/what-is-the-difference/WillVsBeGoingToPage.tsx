import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Will vs. Be Going To: What's the Difference? | TypoGrammar",
  metaDescription: "Will vs be going to: \"will\" is for spontaneous decisions, promises, and opinion-based predictions; \"be going to\" is for prior plans and evidence-based predictions. See the rule, examples, and a quiz.",
  slug: 'will-vs-be-going-to',
  h1: "Will vs. Be Going To: What's the Difference?",
  breadcrumbLabel: 'Will vs. Be Going to',
  datePublished: '2026-07-04',
  dateModified: '2026-07-04',
  quickAnswer: "\"Will\" is used for decisions made at the moment of speaking, promises, offers, and predictions based on opinion (I think it will rain). \"Be going to\" is used for plans or intentions decided before now, and for predictions based on present evidence (look at those clouds — it’s going to rain). The key difference is timing: was the decision made now, or already made/visible before you spoke?",
  tableColumns: ['Will', 'Be going to'],
  tableRows: [
    { feature: 'Decision timing', values: ['Made right now, at the moment of speaking', 'Made before now — a prior plan or intention'] },
    { feature: 'Prediction basis', values: ['Opinion, belief, general expectation', 'Visible evidence in the present situation'] },
    { feature: 'Other uses', values: ['Promises, offers, quick decisions', 'Fixed arrangements, near-certain intentions'] },
    { feature: 'Example', values: ['I\'ll help you carry that.', 'I\'m going to study medicine next year.'] },
  ],
  terms: [
    {
      label: 'Will',
      summary: 'For spontaneous decisions, promises, offers, and opinion-based predictions.',
      pattern: 'will + base verb',
      examples: ['"I\'ll answer the door."', '"I promise I will call you tonight."', '"I think the team will win."'],
    },
    {
      label: 'Be going to',
      summary: 'For plans made before now and predictions based on current evidence.',
      pattern: 'am/is/are + going to + base verb',
      examples: ['"I\'m going to visit my parents this weekend."', '"She\'s going to have a baby."', '"Look out — you\'re going to drop that!"'],
    },
  ],
  grammarRule: 'Use "will" when you decide something at the exact moment you speak, or when making a promise, offer, or opinion-based prediction. Use "be going to" when the decision was already made before now, or when you can see clear present evidence for what will happen.',
  extraRule: 'A useful test for predictions: if you are guessing based on what you can see or already know right now (dark clouds, a wobbling glass), use "going to". If you are just giving a general opinion about the future, "will" works just as well.',
  mistakes: [
    { incorrect: 'Look at the sky! It will rain any minute.', correct: "Look at the sky! It's going to rain any minute.", note: 'This prediction is based on visible evidence right now, so it needs "going to".' },
    { incorrect: 'I already decided last week — I\'m going to buy that car right now, on the spot.', correct: "I already decided last week — I'm going to buy that car.", note: 'A decision made before now needs "going to", not a sudden "will" decision.' },
    { incorrect: 'Don\'t worry, I am going to help you with your bags.', correct: "Don't worry, I will help you with your bags.", note: 'An offer made at the moment of speaking uses "will", not "going to".' },
  ],
  correctExamples: [
    'A: "The phone is ringing." B: "I\'ll get it!"',
    'I\'m going to start a new job next month.',
    'I promise I will never lie to you.',
    'She\'s going to take the exam again in June; she planned it weeks ago.',
    'I think the economy will improve next year.',
    'Watch out, that shelf is going to fall!',
  ],
  quiz: [
    { prompt: 'Choose the correct form: "We\'ve already booked the tickets — we _____ visit Japan in April."', answer: "are going to", explanation: 'This is a prior plan already decided, so it needs "be going to".' },
    { prompt: 'Choose the correct form: "The phone\'s ringing." "Okay, I _____ answer it."', answer: 'will', explanation: 'This is a spontaneous decision made right now, so it needs "will".' },
    { prompt: 'Fix the sentence: "Careful, that glass will fall off the table!" (you can see it wobbling right now)', answer: "Careful, that glass is going to fall off the table!", explanation: 'A prediction based on visible evidence needs "going to".' },
  ],
  faqs: [
    { question: 'Can "will" and "be going to" ever both be correct in the same sentence?', answer: 'Often yes, especially for general future predictions without strong evidence either way, such as "I will visit / I\'m going to visit my grandmother next week." The difference becomes important mainly with spontaneous decisions and evidence-based predictions.' },
    { question: 'Which one should I use for weather forecasts?', answer: 'Weather forecasters usually use "will" ("it will rain tomorrow") because they base predictions on data and analysis rather than something visible right now. But if you personally see dark clouds forming, "going to" fits better in casual speech.' },
    { question: 'Is "gonna" the same as "going to"?', answer: '"Gonna" is an informal spoken contraction of "going to" used in casual conversation. It should be avoided in formal writing, essays, and exams like IELTS or TOEFL.' },
  ],
  related: [
    { to: '/what-is-the-difference/may-vs-might/', text: 'May vs. Might' },
    { to: '/what-is-the-difference/must-vs-have-to/', text: 'Must vs. Have to' },
    { to: '/what-is-the-difference/can-vs-could/', text: 'Can vs. Could' },
  ],
};

const WillVsBeGoingToPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default WillVsBeGoingToPage;
