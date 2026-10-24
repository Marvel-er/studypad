import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Church vs. Cathedral: What's the Difference? | TypoGrammar",
  metaDescription: 'Church vs cathedral: "church" is the general word for any Christian worship building, while "cathedral" specifically names the main church of a diocese, home to a bishop\'s seat. See the rule, examples, and a quiz.',
  slug: 'church-vs-cathedral',
  h1: "Church vs. Cathedral: What's the Difference?",
  breadcrumbLabel: 'Church vs. Cathedral',
  datePublished: '2026-07-05',
  dateModified: '2026-07-05',
  quickAnswer: 'A "church" is a general term for any building used for Christian worship, of any size or importance. A "cathedral" is a specific, often large and architecturally significant church that serves as the official seat of a bishop, overseeing a wider geographic area called a diocese.',
  tableColumns: ['Church', 'Cathedral'],
  tableRows: [
    { feature: 'Scope of term', values: ['General — any Christian worship building', "Specific — a bishop's official seat church"] },
    { feature: 'Size', values: ['Any size, often small or medium', 'Usually large and architecturally significant'] },
    { feature: 'Leadership', values: ['May be led by a priest, pastor, or minister', 'Seat of a bishop who oversees a diocese'] },
    { feature: 'Example', values: ['"The small village church holds fifty people."', '"The cathedral in the city has stood for 800 years."'] },
  ],
  terms: [
    {
      label: 'Church',
      summary: 'The general word for any Christian place of worship, or for the wider Christian religious institution.',
      pattern: 'a/the church (of + name)',
      examples: ['"They attend the church down the street."', '"The church was built in the 1800s."'],
    },
    {
      label: 'Cathedral',
      summary: 'A specific church that houses the "cathedra" (bishop\'s throne) and serves as the main church of a diocese.',
      pattern: 'a/the cathedral (of + city)',
      examples: ['"The cathedral hosts the bishop\'s main services."', '"Tourists visit the cathedral for its stained glass windows."'],
    },
  ],
  grammarRule: 'Use "church" as the general word for any Christian place of worship, and "cathedral" specifically for the main church of a diocese that houses a bishop\'s official seat (the "cathedra"). Every cathedral is a church, but not every church is a cathedral.',
  extraRule: 'The word "cathedral" comes from the Latin "cathedra," meaning "chair" or "seat," referring to the bishop\'s ceremonial chair inside.',
  mistakes: [
    { incorrect: 'The small parish cathedral has only one priest and seats fifty people.', correct: 'The small parish church has only one priest and seats fifty people.', note: 'A small, ordinary worship building is a church, not a cathedral.' },
    { incorrect: 'Every church in the city is the official seat of a bishop.', correct: 'Only the cathedral in the city is the official seat of a bishop.', note: 'Only one specific church, the cathedral, holds the bishop\'s official seat.' },
    { incorrect: 'The cathedral is just a general term for any Christian building.', correct: 'The church is the general term for any Christian building; a cathedral is a specific type of church.', note: '"Church" is the broad term; "cathedral" is the specific one.' },
  ],
  correctExamples: [
    'The family attends a small Baptist church in their neighborhood.',
    'The cathedral in the old city center took over 200 years to build.',
    'Every Sunday, the church holds two morning services.',
    "The bishop's official seat is located inside the cathedral.",
    'Tourists photograph the cathedral\'s towering spires.',
    'The village church was recently repainted by volunteers.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: The tiny worship building in the countryside village is called a _____.', answer: 'church', explanation: 'Any Christian worship building, regardless of size, can be called a church.' },
    { prompt: 'Choose the correct word: The grand, historic building housing the bishop\'s official seat is called a _____.', answer: 'cathedral', explanation: 'The specific building housing the bishop\'s seat is a cathedral.' },
    { prompt: 'Fix the sentence: "Every small church in the diocese is technically a cathedral."', answer: 'Only the main church of the diocese is technically a cathedral.', explanation: 'Only one church per diocese, the one with the bishop\'s seat, is a cathedral.' },
  ],
  faqs: [
    { question: 'Is a cathedral always bigger than a church?', answer: 'Cathedrals are often large and architecturally significant, but their defining feature is housing a bishop\'s seat, not simply their size — some cathedrals are more modest than large non-cathedral churches.' },
    { question: 'Can a cathedral also just be called a church?', answer: 'Yes — since every cathedral is a type of church, it is accurate, though less specific, to refer to a cathedral simply as "the church."' },
    { question: 'Do other religions have buildings similar to cathedrals?', answer: 'Other religions have their own terms for major worship buildings (such as a grand mosque or a main synagogue), but the term "cathedral" specifically applies to a bishop\'s seat church within Christian traditions.' },
  ],
  related: [
    { to: '/what-is-the-difference/priest-vs-monk/', text: 'Priest vs. Monk' },
    { to: '/what-is-the-difference/theism-vs-deism/', text: 'Theism vs. Deism' },
    { to: '/what-is-the-difference/imam-vs-sheikh/', text: 'Imam vs. Sheikh' },
  ],
};

const ChurchVsCathedralPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default ChurchVsCathedralPage;
