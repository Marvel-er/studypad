import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Trauma vs. Sadness: What's the Difference? | TypoGrammar",
  metaDescription: 'Trauma vs sadness: "sadness" is a normal, temporary emotion, while "trauma" is a deep, lasting psychological response to a distressing event that can require professional treatment. See the rule, examples, and a quiz.',
  slug: 'trauma-vs-sadness',
  h1: "Trauma vs. Sadness: What's the Difference?",
  breadcrumbLabel: 'Trauma vs. Sadness',
  datePublished: '2026-07-05',
  dateModified: '2026-07-05',
  quickAnswer: '"Sadness" is a normal, temporary emotion felt in response to a disappointing or upsetting event, which usually fades with time. "Trauma" refers to a deep, lasting psychological response to a distressing or frightening event, which can affect a person\'s mental and physical wellbeing long after the event has ended, and may benefit from professional support.',
  tableColumns: ['Sadness', 'Trauma'],
  tableRows: [
    { feature: 'Nature', values: ['A normal, temporary emotion', 'A lasting psychological response'] },
    { feature: 'Cause', values: ['Disappointing or upsetting events', 'Distressing, frightening, or life-threatening events'] },
    { feature: 'Duration', values: ['Usually fades within days or weeks', 'Can persist for months or years without support'] },
    { feature: 'Effect on daily life', values: ['Mild, temporary impact', 'Can seriously disrupt sleep, relationships, daily functioning'] },
  ],
  terms: [
    {
      label: 'Sadness',
      summary: 'A normal, temporary emotional response to a disappointing or upsetting event, which generally passes with time.',
      pattern: 'sadness (about/over + event)',
      examples: ['"He felt sadness after losing the match."', '"Her sadness faded within a few days."'],
    },
    {
      label: 'Trauma',
      summary: "A lasting psychological injury caused by a deeply distressing or frightening experience, which can affect a person's wellbeing long-term.",
      pattern: 'trauma (from + event)',
      examples: ['"The accident left her with lasting trauma."', '"He is working through childhood trauma with a therapist."'],
    },
  ],
  grammarRule: 'Use "sadness" for the everyday emotion of feeling unhappy or down, which is a normal part of life. Use "trauma" specifically for the lasting psychological impact of a deeply distressing or frightening experience — it is not simply a stronger word for sadness.',
  extraRule: 'Not every difficult experience causes trauma, and not every sad feeling is minor — but clinically, "trauma" implies a specific injury to a person\'s sense of safety, not just an intense version of sadness. Anyone experiencing lasting symptoms of trauma is encouraged to seek support from a qualified professional.',
  mistakes: [
    { incorrect: 'I felt so traumatized after my team lost the game.', correct: 'I felt so sad after my team lost the game.', note: 'Unless something genuinely distressing happened, "traumatized" overstates ordinary disappointment.' },
    { incorrect: 'Her sadness from the car accident affected her sleep for years afterward.', correct: 'Her trauma from the car accident affected her sleep for years afterward.', note: 'A lasting effect on sleep and functioning years later points to trauma, not simple sadness.' },
    { incorrect: 'Trauma always goes away after a good night\'s sleep.', correct: "Sadness often eases after a good night's sleep, but trauma usually needs more time or professional support.", note: 'Trauma is a deeper, longer-lasting response than everyday sadness.' },
  ],
  correctExamples: [
    'He felt a wave of sadness when his favorite show ended.',
    'She sought therapy to work through the trauma of the accident.',
    'Sadness after a breakup is a normal part of moving on.',
    'Survivors of natural disasters often experience lasting trauma.',
    'His sadness lifted once he spent time with friends.',
    'Childhood trauma can affect relationships well into adulthood.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: She felt _____ for a few days after her houseplant died.', answer: 'sadness', explanation: 'A brief, everyday emotional reaction to a minor loss is sadness.' },
    { prompt: 'Choose the correct word: Survivors of the earthquake showed signs of lasting _____ months later.', answer: 'trauma', explanation: 'A long-lasting psychological effect from a frightening event is trauma.' },
    { prompt: 'Fix the sentence: "He was traumatized for an afternoon after missing his bus."', answer: 'He was upset (or sad) for an afternoon after missing his bus.', explanation: 'A brief, minor inconvenience causes sadness or annoyance, not trauma.' },
  ],
  faqs: [
    { question: 'Is trauma just extreme sadness?', answer: 'No — trauma is a distinct psychological response involving a deep sense of threat or helplessness, which can affect memory, sleep, and behavior in ways that go beyond ordinary sadness.' },
    { question: 'Can trauma go away on its own?', answer: 'Some people recover from difficult experiences over time, but persistent trauma symptoms often benefit from support from a mental health professional.' },
    { question: 'When should someone seek help for trauma versus sadness?', answer: 'If sadness or distress persists for weeks, worsens, or interferes with daily life, sleep, or relationships, it is worth speaking with a qualified mental health professional.' },
  ],
  related: [
    { to: '/what-is-the-difference/fact-vs-truth/', text: 'Fact vs. Truth' },
    { to: '/what-is-the-difference/problem-vs-issue/', text: 'Problem vs. Issue' },
    { to: '/what-is-the-difference/iq-vs-intelligence/', text: 'IQ vs. Intelligence' },
  ],
};

const TraumaVsSadnessPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default TraumaVsSadnessPage;
