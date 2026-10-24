import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Travel vs. Journey vs. Trip: What's the Difference? | TypoGrammar",
  metaDescription: "Travel vs journey vs trip: \"travel\" is the general, usually uncountable activity of moving between places; \"journey\" is the process of getting somewhere; \"trip\" is a whole excursion, there and back. See the rule, examples, and a quiz.",
  slug: 'travel-vs-journey-vs-trip',
  h1: "Travel vs. Journey vs. Trip: What's the Difference?",
  breadcrumbLabel: 'Travel vs. Journey vs. Trip',
  datePublished: '2026-07-04',
  dateModified: '2026-07-04',
  quickAnswer: "\"Travel\" is the general, usually uncountable idea of moving between places (I love to travel). \"Journey\" is a countable noun for the process of going from one place to another, often emphasizing the time or distance covered (a long journey). \"Trip\" is a countable noun for a whole excursion, including the destination and activities, usually with a return (a weekend trip to the coast).",
  tableColumns: ['Travel', 'Journey', 'Trip'],
  tableRows: [
    { feature: 'Countable?', values: ['Usually uncountable', 'Countable', 'Countable'] },
    { feature: 'Focus', values: ['The general activity/concept', 'The process of getting there', 'The whole excursion, there and (usually) back'] },
    { feature: 'Example', values: ['I love to travel.', 'It was a long, tiring journey.', 'We took a weekend trip to the mountains.'] },
    { feature: 'Common collocation', values: ['travel abroad, business travel', 'a journey of a lifetime', 'a business trip, a road trip'] },
  ],
  terms: [
    {
      label: 'Travel',
      summary: 'The general concept or activity of moving between places — usually uncountable as a noun, and also a common verb.',
      pattern: 'travel (uncountable noun) / to travel (verb)',
      examples: ['"Travel broadens the mind."', '"She works in the travel industry."', '"They travel a lot for work."'],
    },
    {
      label: 'Journey',
      summary: 'A countable noun describing the process of going from one place to another, often long or significant.',
      pattern: 'a/the + journey',
      examples: ['"The journey took almost twelve hours."', '"It was a difficult journey through the mountains."', '"Enjoy your journey home!"'],
    },
    {
      label: 'Trip',
      summary: 'A countable noun describing a whole excursion — going somewhere, staying, and usually returning.',
      pattern: 'a + trip (+ to + place)',
      examples: ['"We\'re planning a trip to Japan."', '"How was your business trip?"', '"Let\'s take a road trip this summer."'],
    },
  ],
  grammarRule: 'Use "travel" as the general, usually uncountable concept or the verb form. Use "journey" for one countable instance of moving from one place to another, focusing on the process itself. Use "trip" for a whole countable excursion, including arrival, activities, and (usually) the return.',
  extraRule: 'Because "travel" is normally uncountable in this sense, avoid saying "a travel" or "travels" for a single event — say "a trip" or "a journey" instead.',
  mistakes: [
    { incorrect: 'We had an amazing travel to Italy last summer.', correct: 'We had an amazing trip to Italy last summer.', note: '"Travel" is uncountable, so a single excursion needs "trip" or "journey", not "a travel".' },
    { incorrect: 'The journey to the airport was fun; we saw so many places and stayed three nights.', correct: 'The trip to the airport was fun; we saw so many places and stayed three nights.', note: 'A multi-day excursion with a stay is a "trip", while "journey" better fits the process of travel itself.' },
    { incorrect: 'I love traveling; it was the best travel of my life.', correct: 'I love traveling; it was the best trip of my life.' },
  ],
  correctExamples: [
    'International travel has increased a lot in recent years.',
    'The journey from London to Edinburgh takes about four hours by train.',
    'We\'re going on a family trip to the beach next month.',
    'She wrote a book about her travels through South America.',
    'It was an exhausting journey, but we made it safely.',
    'How was your trip? Did you enjoy the city?',
  ],
  quiz: [
    { prompt: 'Choose the correct word: "_____ is one of my biggest passions in life." (general concept)', answer: 'Travel', explanation: 'This refers to the general activity/concept, so it needs the uncountable noun "travel".' },
    { prompt: 'Choose the correct word: "The _____ across the desert took three exhausting days." (the process of getting there)', answer: 'journey', explanation: 'This emphasizes the process and difficulty of getting somewhere, so it needs "journey".' },
    { prompt: 'Fix the sentence: "We\'re planning a travel to Portugal next spring, including a week at the beach."', answer: 'We\'re planning a trip to Portugal next spring, including a week at the beach.', explanation: 'A whole excursion including a stay is a "trip", and "travel" cannot take the article "a" in this sense.' },
  ],
  faqs: [
    { question: 'Can "journey" be used figuratively?', answer: 'Yes, very often. "Journey" is commonly used to describe a process of personal change or growth, as in "her career journey" or "the journey to recovery," beyond just physical movement.' },
    { question: 'Is "trip" always short and "journey" always long?', answer: 'Not strictly, but in practice "trip" often implies a more complete excursion with a purpose and return (a business trip, a day trip), while "journey" tends to emphasize the traveling process itself, which can be short or very long.' },
    { question: 'Why can\'t I say "a travel" or "travels" for one trip?', answer: 'In its most common modern sense, "travel" behaves as an uncountable noun, similar to "information" or "advice" — it describes an activity in general, not a single, countable event. For one specific event, use "trip" or "journey" instead.' },
  ],
  related: [
    { to: '/what-is-the-difference/job-vs-work/', text: 'Job vs. Work' },
    { to: '/what-is-the-difference/house-vs-home/', text: 'House vs. Home' },
    { to: '/what-is-the-difference/for-vs-since/', text: 'For vs. Since' },
  ],
};

const TravelVsJourneyVsTripPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default TravelVsJourneyVsTripPage;
