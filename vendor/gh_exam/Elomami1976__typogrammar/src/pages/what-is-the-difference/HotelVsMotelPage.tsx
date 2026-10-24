import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Hotel vs. Motel: What's the Difference? | TypoGrammar",
  metaDescription: 'Hotel vs motel: a "hotel" is typically a larger building with indoor corridors and more services, while a "motel" is a smaller roadside building with rooms opening onto the parking lot. See the rule, examples, and a quiz.',
  slug: 'hotel-vs-motel',
  h1: "Hotel vs. Motel: What's the Difference?",
  breadcrumbLabel: 'Hotel vs. Motel',
  datePublished: '2026-07-05',
  dateModified: '2026-07-05',
  quickAnswer: 'A "hotel" is typically a larger building with multiple floors, indoor corridors, and services such as room service, restaurants, and reception desks, often located in cities or near attractions. A "motel" (motor + hotel) is typically a smaller, low-rise building with rooms that open directly onto an outdoor parking lot, designed for drivers on road trips who want quick, convenient access to their car.',
  tableColumns: ['Hotel', 'Motel'],
  tableRows: [
    { feature: 'Typical size', values: ['Multiple floors, many rooms', 'Single or two-story, fewer rooms'] },
    { feature: 'Room access', values: ['Indoor hallways/elevators', 'Direct outdoor access from the parking lot'] },
    { feature: 'Location', values: ['City centers, near attractions/airports', 'Along highways, roadsides'] },
    { feature: 'Services', values: ['Reception, restaurant, room service common', 'Minimal services, self-check-in common'] },
  ],
  terms: [
    {
      label: 'Hotel',
      summary: 'A larger lodging building, usually with indoor corridors, a front desk, and additional services like a restaurant or room service.',
      pattern: 'a hotel (in/near + place)',
      examples: ['"They stayed at a hotel in the city center."', '"The hotel offers 24-hour room service."'],
    },
    {
      label: 'Motel',
      summary: 'A smaller, low-rise lodging building along a road or highway, with rooms opening directly onto the parking area, aimed at drivers.',
      pattern: 'a motel (on/along + highway)',
      examples: ['"They stopped at a roadside motel for the night."', '"The motel let them park right outside their door."'],
    },
  ],
  grammarRule: 'Use "hotel" for larger, full-service lodging with indoor access and more amenities, and "motel" for smaller, roadside lodging designed for drivers, with rooms opening directly onto the parking area.',
  extraRule: '"Motel" comes from blending "motor" and "hotel," reflecting its origin as roadside lodging built specifically for car travelers in the mid-20th century United States.',
  mistakes: [
    { incorrect: 'We stayed at a twenty-floor motel in the middle of the city.', correct: 'We stayed at a twenty-floor hotel in the middle of the city.', note: 'A tall, multi-floor building with indoor corridors is a hotel, not a motel.' },
    { incorrect: 'The roadside hotel let us park right outside our room door.', correct: 'The roadside motel let us park right outside our room door.', note: 'Direct outdoor parking access next to your room is characteristic of a motel.' },
    { incorrect: 'Motels always have full restaurants and 24-hour room service.', correct: 'Hotels are more likely to have full restaurants and 24-hour room service.', note: 'Motels typically offer minimal services compared to hotels.' },
  ],
  correctExamples: [
    'The business traveler booked a hotel near the airport.',
    'They found a cheap motel just off the highway exit.',
    'The hotel lobby had a large reception desk and a restaurant.',
    'Each motel room opened directly onto the parking lot.',
    'The family checked into a hotel with a pool and room service.',
    'Truck drivers often stop overnight at motels along long highway routes.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: A ten-story building downtown with a restaurant and room service is a _____.', answer: 'hotel', explanation: 'Tall buildings with indoor amenities are described as hotels.' },
    { prompt: 'Choose the correct word: A one-story roadside building where guests park right outside their room is a _____.', answer: 'motel', explanation: 'Direct outdoor room access along a highway is typical of a motel.' },
    { prompt: 'Fix the sentence: "The five-star motel in the city has a spa, gym, and full restaurant."', answer: 'The five-star hotel in the city has a spa, gym, and full restaurant.', explanation: 'A full-service, multi-amenity property in a city is called a hotel.' },
  ],
  faqs: [
    { question: 'Are motels cheaper than hotels?', answer: 'Motels are often (but not always) cheaper, since they typically offer fewer services and amenities than hotels, though location and demand can still affect price.' },
    { question: 'Is "motel" used outside the US?', answer: 'The word originated in the US and is most common there, though it is understood in many English-speaking countries; other regions may use different terms for similar roadside lodging.' },
    { question: 'Can a motel have more than one floor?', answer: 'Some motels have two floors with exterior walkways, but they still typically keep the direct, drive-up room access that distinguishes them from a hotel.' },
  ],
  related: [
    { to: '/what-is-the-difference/money-vs-currency/', text: 'Money vs. Currency' },
    { to: '/what-is-the-difference/jail-vs-prison/', text: 'Jail vs. Prison' },
    { to: '/what-is-the-difference/vlog-vs-blog/', text: 'Vlog vs. Blog' },
  ],
};

const HotelVsMotelPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default HotelVsMotelPage;
