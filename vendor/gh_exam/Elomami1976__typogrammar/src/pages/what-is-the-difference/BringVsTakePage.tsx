import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Bring vs. Take: What's the Difference? | TypoGrammar",
  metaDescription: "Bring vs take: \"bring\" means to move something toward the speaker's or listener's location (here); \"take\" means to move something away from that location (there). See the rule, examples, and a quiz.",
  slug: 'bring-vs-take',
  h1: "Bring vs. Take: What's the Difference?",
  breadcrumbLabel: 'Bring vs. Take',
  datePublished: '2026-07-04',
  dateModified: '2026-07-04',
  quickAnswer: "\"Bring\" means to carry or move something toward the place where the speaker or listener is, or will be — toward \"here\" (please bring your laptop to the meeting). \"Take\" means to carry or move something away from that place — toward \"there\" (please take your laptop home). The direction of movement relative to the speaker decides which verb is correct.",
  tableColumns: ['Bring', 'Take'],
  tableRows: [
    { feature: 'Direction', values: ['Toward the speaker/listener\'s location ("here")', 'Away from the speaker\'s current location ("there")'] },
    { feature: 'Typical use', values: ['Inviting something to your location', 'Moving something to another location'] },
    { feature: 'Example', values: ['Bring your ID card to the office (where I am).', 'Take these documents to the office (where you are going).'] },
    { feature: 'Question form', values: ['"What should I bring?" (to where we\'ll be)', '"What should I take?" (to where I\'m going)'] },
  ],
  terms: [
    {
      label: 'Bring',
      summary: 'Move something toward the location of the speaker, the listener, or the point of reference.',
      pattern: 'bring + object (+ to/here)',
      examples: ['"Please bring your umbrella; it might rain here later."', '"Can you bring me some water?"', '"Bring your friends to the party!"'],
    },
    {
      label: 'Take',
      summary: 'Move something away from the current location, toward another place.',
      pattern: 'take + object (+ to/there)',
      examples: ['"Take this letter to the post office."', '"I\'ll take my umbrella when I leave."', '"Don\'t forget to take your keys."'],
    },
  ],
  grammarRule: 'Use "bring" when the movement is toward the speaker or the place being discussed (here). Use "take" when the movement is away from the speaker\'s current location, toward somewhere else (there). Always check where the speaker is standing — literally or in the conversation — before choosing.',
  extraRule: 'A helpful test: imagine the speaker standing at a fixed point. If the object moves toward that point, use "bring". If it moves away from that point, use "take".',
  mistakes: [
    { incorrect: 'I will bring my laptop to the office tomorrow (said while at home, talking about a place they are not at).', correct: "I will take my laptop to the office tomorrow.", note: 'The speaker is moving the laptop away from their current location, so it needs "take".' },
    { incorrect: 'Can you take me a glass of water? (said to someone in the same room, asking them to get water and come back)', correct: 'Can you bring me a glass of water?', note: 'The water needs to move toward the speaker, so it needs "bring".' },
    { incorrect: 'Please take your books to class tomorrow when you come here.', correct: 'Please bring your books to class tomorrow when you come here.', note: '"Come here" signals movement toward the speaker\'s location, so it needs "bring".' },
  ],
  correctExamples: [
    'Don\'t forget to bring your passport when you visit us next week.',
    'I need to take these papers to the bank this afternoon.',
    'She always brings a gift when she comes to dinner.',
    'He took his dog for a walk in the park.',
    'Could you bring your guitar to the party on Saturday?',
    'I\'ll take the trash out before I leave for work.',
  ],
  quiz: [
    { prompt: 'Choose the correct word (you are hosting a party at your house): "Please _____ some snacks when you come over."', answer: 'bring', explanation: 'The snacks need to move toward the speaker\'s location (the party), so it needs "bring".' },
    { prompt: 'Choose the correct word (you are leaving your house to run an errand): "I need to _____ these letters to the post office."', answer: 'take', explanation: 'The letters are moving away from the speaker\'s current location, so it needs "take".' },
    { prompt: 'Fix the sentence (a friend calls you at home and asks for help): "I\'ll take you some soup right now."', answer: "I'll bring you some soup right now.", explanation: 'The soup needs to move toward the listener\'s location, so it needs "bring".' },
  ],
  faqs: [
    { question: 'Does "bring" always mean movement to where I am right now?', answer: "Mostly, but it also applies to the location of the person you're speaking to or a shared reference point, even if you aren't there yet — for example, telling a friend \"I'll bring the drinks to the picnic\" uses \"bring\" because the picnic is the shared destination both speakers are focused on." },
    { question: 'Is "take" ever used for movement toward the speaker?', answer: 'Not typically — "take" almost always implies movement away from the current point of reference. If the movement is toward that point, "bring" is the natural choice.' },
    { question: 'Do British and American English use "bring" and "take" differently?', answer: 'The core rule is the same in both varieties. Any differences are usually about individual phrases and idioms (like "take a shower" vs. regional variants), not the fundamental bring/take direction rule.' },
  ],
  related: [
    { to: '/what-is-the-difference/borrow-vs-lend/', text: 'Borrow vs. Lend' },
    { to: '/what-is-the-difference/win-vs-beat/', text: 'Win vs. Beat' },
    { to: '/grammar-mistakes/bring-vs-take/', text: 'Bring vs. Take (Grammar Mistakes)' },
  ],
};

const BringVsTakePage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default BringVsTakePage;
