import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Bored vs. Boring: What's the Difference? | TypoGrammar",
  metaDescription: "Bored vs boring: \"bored\" (-ed) describes how a person feels; \"boring\" (-ing) describes the thing or person that causes that feeling. See the rule, examples, and a quiz.",
  slug: 'bored-vs-boring',
  h1: "Bored vs. Boring: What's the Difference?",
  breadcrumbLabel: 'Bored vs. Boring',
  datePublished: '2026-07-04',
  dateModified: '2026-07-04',
  quickAnswer: "\"Bored\" is an -ed adjective describing how a person feels — a lack of interest or entertainment (I am bored). \"Boring\" is an -ing adjective describing the thing, person, or situation that causes that feeling (this movie is boring). The same pattern applies to many other pairs, like interested/interesting and excited/exciting: -ed for the feeler, -ing for the cause.",
  tableColumns: ['Bored (-ed)', 'Boring (-ing)'],
  tableRows: [
    { feature: 'Describes', values: ['The person experiencing the feeling', 'The thing/person causing the feeling'] },
    { feature: 'Typical subject', values: ['A person (I, she, they)', 'A thing, event, or person that causes boredom'] },
    { feature: 'Example', values: ['I am bored.', 'This lecture is boring.'] },
    { feature: 'Same pattern applies to', values: ['tired, interested, excited, confused', 'tiring, interesting, exciting, confusing'] },
  ],
  terms: [
    {
      label: 'Bored',
      summary: 'Describes the feeling a person has — not interested, tired of something.',
      pattern: 'subject (person) + is/am/are + bored',
      examples: ['"I feel bored on rainy days."', '"The students looked bored during the lecture."', '"Are you bored right now?"'],
    },
    {
      label: 'Boring',
      summary: 'Describes the quality of the thing or person that causes the feeling of boredom.',
      pattern: 'subject (thing/person) + is/am/are + boring',
      examples: ['"This documentary is boring."', '"He gives really boring speeches."', '"The meeting was so boring."'],
    },
  ],
  grammarRule: '-ed adjectives (bored, tired, interested, excited) describe how a person feels. -ing adjectives (boring, tiring, interesting, exciting) describe the thing or person that produces that feeling in others. Never use "boring" to describe how you personally feel.',
  extraRule: 'Quick test: if you can replace the word with "I feel ___", use the -ed form. If you can replace it with "It makes people feel ___", use the -ing form.',
  mistakes: [
    { incorrect: 'I am so boring right now; there\'s nothing to do.', correct: "I am so bored right now; there's nothing to do.", note: 'This describes how the speaker feels, so it needs "bored", not "boring".' },
    { incorrect: 'This textbook is very bored; nobody wants to read it.', correct: 'This textbook is very boring; nobody wants to read it.', note: 'This describes the quality of the textbook, so it needs "boring", not "bored".' },
    { incorrect: 'The teacher was boring during the exam because it was too hard.', correct: 'The teacher was bored during the exam because there was nothing to do.', note: 'Here the intended meaning is how the teacher felt, so "bored" is correct.' },
  ],
  correctExamples: [
    'The children got bored after an hour in the car.',
    'Long car rides can be boring for children.',
    'I was bored during the entire meeting.',
    'That was the most boring meeting I\'ve ever attended.',
    'She felt bored and started scrolling on her phone.',
    'His stories are never boring; they\'re always full of surprises.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: "The movie was so _____ that half the audience fell asleep."', answer: 'boring', explanation: 'This describes the movie, the cause of the feeling, so it needs the -ing form.' },
    { prompt: 'Choose the correct word: "I felt completely _____ during the three-hour lecture."', answer: 'bored', explanation: 'This describes how the speaker felt, so it needs the -ed form.' },
    { prompt: 'Fix the sentence: "Everyone in the room looked so boring during the presentation."', answer: 'Everyone in the room looked so bored during the presentation.', explanation: 'This describes how the people felt, so it needs "bored", not "boring".' },
  ],
  faqs: [
    { question: 'Does this -ed/-ing rule apply to other adjectives too?', answer: 'Yes, it\'s a general pattern in English for adjectives formed from verbs about emotion: tired/tiring, interested/interesting, excited/exciting, confused/confusing, annoyed/annoying, and more. -ed = how someone feels; -ing = what causes the feeling.' },
    { question: 'Can a person ever be described as "boring"?', answer: 'Yes — "boring" can describe a person when that person causes boredom in others, as in "He\'s such a boring speaker." This is different from saying the person themselves feels bored ("He is bored").' },
    { question: 'Is it wrong to say "I am boring of this"?', answer: 'Yes, that phrasing is incorrect. Say "I am bored of this" or, more standard, "I am bored with this" or "I am tired of this."' },
  ],
  related: [
    { to: '/what-is-the-difference/can-vs-could/', text: 'Can vs. Could' },
    { to: '/what-is-the-difference/may-vs-might/', text: 'May vs. Might' },
    { to: '/topics/adjectives-adverbs/', text: 'Adjectives and Adverbs' },
  ],
};

const BoredVsBoringPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default BoredVsBoringPage;
