import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "See vs. Look vs. Watch: What's the Difference? | TypoGrammar",
  metaDescription: "See vs look vs watch: \"see\" means to perceive with your eyes without effort; \"look (at)\" means to direct your eyes deliberately at something still; \"watch\" means to observe something moving or changing. See the rule, examples, and a quiz.",
  slug: 'see-vs-look-vs-watch',
  h1: "See vs. Look vs. Watch: What's the Difference?",
  breadcrumbLabel: 'See vs. Look vs. Watch',
  datePublished: '2026-07-04',
  dateModified: '2026-07-04',
  quickAnswer: "\"See\" means images reach your eyes without effort — it's involuntary (I see a bird). \"Look (at)\" means you deliberately direct your eyes at something, usually still (look at the picture). \"Watch\" means you pay close, ongoing attention to something that moves or changes over time (watch a movie, watch the game). The difference is effort and movement, not just eyesight.",
  tableColumns: ['See', 'Look (at)', 'Watch'],
  tableRows: [
    { feature: 'Effort', values: ['Involuntary', 'Deliberate, brief', 'Deliberate, sustained'] },
    { feature: 'Movement of subject', values: ['Not relevant', 'Usually still', 'Usually moving/changing'] },
    { feature: 'Grammar with object', values: ['see + object', 'look + at + object', 'watch + object'] },
    { feature: 'Typical example', values: ['I see a plane in the sky.', 'Look at that painting.', 'Watch the plane take off.'] },
  ],
  terms: [
    {
      label: 'See',
      summary: 'Perceiving something with your eyes without any special effort — a stative, involuntary action.',
      pattern: 'see + object',
      examples: ['"I see a bird on the roof."', '"Can you see the mountains from here?"', '"I saw her at the store yesterday."'],
    },
    {
      label: 'Look (at)',
      summary: 'Deliberately directing your eyes toward something, usually still or in one place.',
      pattern: 'look + at + object',
      examples: ['"Look at this photo!"', '"She looked at her watch."', '"He looked out the window."'],
    },
    {
      label: 'Watch',
      summary: 'Paying close, sustained attention to something that moves, changes, or unfolds over time.',
      pattern: 'watch + object',
      examples: ['"We watched the sunset."', '"I watch the news every night."', '"They watched the children playing."'],
    },
  ],
  grammarRule: 'Use "see" for involuntary perception. Use "look (at)" for a deliberate, usually brief glance at something that isn\'t moving. Use "watch" for deliberate, ongoing attention to something in motion or changing, like a screen, an event, or an activity.',
  extraRule: 'Note the grammar difference: "see" and "watch" take a direct object with no preposition ("see a movie", "watch a movie"), while "look" needs "at" before its object ("look at a movie poster").',
  mistakes: [
    { incorrect: 'I watched a bird on the roof for one second and then looked away.', correct: 'I saw a bird on the roof for one second and then looked away.', note: 'A brief, involuntary glimpse is "see", not "watch", which implies sustained attention.' },
    { incorrect: 'Let\'s see the football match tonight; kickoff is at 8.', correct: "Let's watch the football match tonight; kickoff is at 8.", note: 'A moving, ongoing event like a match should be "watched", not just "seen".' },
    { incorrect: 'Look this photo of my new puppy!', correct: 'Look at this photo of my new puppy!', note: '"Look" always needs "at" before its object.' },
  ],
  correctExamples: [
    'I can\'t see anything without my glasses.',
    'Look at the board and copy these notes.',
    'We watched an entire season of the show in one weekend.',
    'She saw a familiar face in the crowd.',
    'He looked at his phone every five minutes.',
    'The children watched the fireworks in amazement.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: "Please _____ the whiteboard for the instructions."', answer: 'look at', explanation: 'This is a deliberate glance at something still, so it needs "look at".' },
    { prompt: 'Choose the correct word: "We stayed up late to _____ the entire game."', answer: 'watch', explanation: 'A game is ongoing and changing, so it needs "watch".' },
    { prompt: 'Fix the sentence: "I looked a shooting star for just a second."', answer: 'I saw a shooting star for just a second.', explanation: 'A brief, involuntary glimpse uses "see", not "look".' },
  ],
  faqs: [
    { question: 'Can "watch" ever be used for something that isn\'t moving?', answer: "Yes, in contexts where you're carefully monitoring something for a change, such as \"watch the pot so it doesn't boil over\" or \"watch your step.\" The key idea is sustained attention for potential change, not literal motion." },
    { question: 'Why is it "watch TV" but "look at the TV screen"?', answer: '"Watch TV" refers to following moving content (shows, programs) over time, while "look at the TV" simply describes glancing at the physical screen itself, without necessarily following the content.' },
    { question: 'Is "see a movie" the same as "watch a movie"?', answer: 'They are used almost interchangeably, though "see a movie" often implies going to a cinema as an experience, while "watch a movie" focuses more on the act of viewing, wherever it happens.' },
  ],
  related: [
    { to: '/what-is-the-difference/hear-vs-listen/', text: 'Hear vs. Listen' },
    { to: '/what-is-the-difference/remember-vs-remind/', text: 'Remember vs. Remind' },
    { to: '/grammar-mistakes/look-vs-see-vs-watch/', text: 'Look vs. See vs. Watch (Grammar Mistakes)' },
  ],
};

const SeeVsLookVsWatchPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default SeeVsLookVsWatchPage;
