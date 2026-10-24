import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "House vs. Home: What's the Difference? | TypoGrammar",
  metaDescription: "House vs home: \"house\" is the physical building; \"home\" is the place where someone lives, with an emotional, personal meaning. See the rule, examples, and a quiz.",
  slug: 'house-vs-home',
  h1: "House vs. Home: What's the Difference?",
  breadcrumbLabel: 'House vs. Home',
  datePublished: '2026-07-04',
  dateModified: '2026-07-04',
  quickAnswer: "\"House\" refers to the physical building or structure where people live — bricks, walls, and a roof (they bought a new house). \"Home\" refers to the place where someone lives and feels they belong, with an emotional or personal meaning that can include a house, apartment, city, or even country (there's no place like home). A building is always a house, but \"home\" is about feeling, not just structure.",
  tableColumns: ['House', 'Home'],
  tableRows: [
    { feature: 'What it refers to', values: ['The physical building/structure', 'The place where you live and belong (emotional)'] },
    { feature: 'Can be bought/sold?', values: ['Yes — a house is real estate', 'Not directly — you buy the house, not the feeling'] },
    { feature: 'Grammar with "go"', values: ['go to the house (needs "to the")', 'go home (no preposition, no article)'] },
    { feature: 'Example', values: ['They are painting the house.', 'There\'s no place like home.'] },
  ],
  terms: [
    {
      label: 'House',
      summary: 'The physical, structural building where someone may or may not live.',
      pattern: 'a/the + house',
      examples: ['"They just bought a new house."', '"The house has four bedrooms."', '"We\'re renovating the house next year."'],
    },
    {
      label: 'Home',
      summary: 'The place someone lives and feels they belong — an emotional or personal concept, not just a structure.',
      pattern: 'home (often no article, especially with "go/be/stay")',
      examples: ['"I can\'t wait to get home."', '"Home is where the heart is."', '"She feels most relaxed at home."'],
    },
  ],
  grammarRule: '"House" describes the physical structure and is treated like any regular countable noun (a house, the house, two houses). "Home" describes the emotional sense of belonging to a place, and in many common expressions (go home, be home, stay home, get home) it is used with no article and no preposition "to".',
  extraRule: 'A house can be empty and still be called a house, but an empty building rarely feels like a "home" — the word "home" implies people, memories, and comfort, not just walls and a roof.',
  mistakes: [
    { incorrect: 'I need to go to home after work.', correct: 'I need to go home after work.', note: '"Go home" is a fixed expression with no preposition and no article.' },
    { incorrect: 'This house is where my family belongs; we love this house so much, it\'s full of memories.', correct: 'This home is where my family belongs; we love this home so much, it\'s full of memories.', note: 'This sentence emphasizes emotional belonging and memories, which fits "home" better than the purely physical "house".' },
    { incorrect: 'The real estate agent showed us three different homes to buy.', correct: 'The real estate agent showed us three different houses to buy.', note: 'A real estate listing describes physical buildings, so it needs "houses", not "homes" (though "homes" is sometimes used commercially, "houses" is more precise here).' },
  ],
  correctExamples: [
    'The house on the corner has a red door.',
    'No matter where I travel, I always miss home.',
    'They\'re building a new house down the street.',
    'Home is wherever my family is.',
    'The house was empty when the new owners moved in.',
    'After years abroad, she finally felt at home again.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: "The _____ has three floors and a large garden." (the physical building)', answer: 'house', explanation: 'This describes the physical structure, so it needs "house".' },
    { prompt: 'Choose the correct phrase: "After a long trip, it feels great to finally be _____."', answer: 'home', explanation: 'This is the fixed expression "be home", with no article.' },
    { prompt: 'Fix the sentence: "I\'m going to house now; see you tomorrow."', answer: "I'm going home now; see you tomorrow.", explanation: '"Go home" never takes "to" or an article.' },
  ],
  faqs: [
    { question: 'Can "home" ever refer to a physical building?', answer: 'Yes, especially in real estate advertising, where "home" is often used instead of "house" to sound warmer and more appealing ("beautiful family home for sale"). In everyday speech, though, "home" usually emphasizes feeling and belonging rather than the structure itself.' },
    { question: 'Why is there no "the" before "home" in "go home"?', answer: '"Home" behaves like an adverb of place in expressions such as "go home," "come home," "stay home," and "be home" — similarly to "here" and "there," it does not need an article or the preposition "to" in these fixed patterns.' },
    { question: 'Is "homeland" related to "home"?', answer: 'Yes — "homeland" extends the emotional idea of "home" to a whole country or region of origin, referring to the country someone (or their family) originally comes from, with a similar sense of belonging.' },
  ],
  related: [
    { to: '/what-is-the-difference/custom-vs-habit/', text: 'Custom vs. Habit' },
    { to: '/what-is-the-difference/travel-vs-journey-vs-trip/', text: 'Travel vs. Journey vs. Trip' },
    { to: '/what-is-the-difference/farther-vs-further/', text: 'Farther vs. Further' },
  ],
};

const HouseVsHomePage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default HouseVsHomePage;
