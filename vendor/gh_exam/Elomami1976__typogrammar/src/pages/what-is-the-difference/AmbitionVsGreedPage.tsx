import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Ambition vs. Greed: What's the Difference? | TypoGrammar",
  metaDescription: 'Ambition vs greed: "ambition" is a generally positive drive to achieve success, while "greed" is an excessive, selfish desire for more than one needs. See the rule, examples, and a quiz.',
  slug: 'ambition-vs-greed',
  h1: "Ambition vs. Greed: What's the Difference?",
  breadcrumbLabel: 'Ambition vs. Greed',
  datePublished: '2026-07-05',
  dateModified: '2026-07-05',
  quickAnswer: '"Ambition" is a strong desire to achieve success, status, or a particular goal, generally viewed as a positive or neutral trait that drives effort and achievement. "Greed" is an excessive, often selfish desire for more than one needs — usually wealth, power, or possessions — viewed negatively because it can come at the expense of others.',
  tableColumns: ['Ambition', 'Greed'],
  tableRows: [
    { feature: 'Connotation', values: ['Generally positive or neutral', 'Generally negative'] },
    { feature: 'Focus', values: ['Achieving goals, success, growth', "Accumulating more than needed, often at others' expense"] },
    { feature: 'Effect on others', values: ['Can inspire and coexist with fairness', 'Often involves selfishness or harm to others'] },
    { feature: 'Example', values: ['"Her ambition drove her to start a successful company."', '"His greed led him to cheat his business partners."'] },
  ],
  terms: [
    {
      label: 'Ambition',
      summary: 'A strong drive or desire to achieve success, status, or a specific goal, often viewed positively.',
      pattern: 'ambition (uncountable) / ambitious (adjective)',
      examples: ['"His ambition pushed him to finish the marathon."', '"She has always been ambitious about her career."'],
    },
    {
      label: 'Greed',
      summary: "An excessive and selfish desire for more wealth, power, or possessions than one needs, often at the expense of others.",
      pattern: 'greed (uncountable) / greedy (adjective)',
      examples: ['"Greed drove him to overcharge his customers."', '"The executive was criticized for his greedy business practices."'],
    },
  ],
  grammarRule: 'Use "ambition" for a generally positive or neutral drive to achieve goals and succeed. Use "greed" for an excessive, selfish desire for more than one needs, especially when it harms or exploits others.',
  extraRule: 'The line between ambition and greed is often about ethics and excess — ambition pursued fairly is usually admired, while the same drive taken to an extreme or pursued unfairly can be described as greed.',
  mistakes: [
    { incorrect: 'Her greed to succeed in her career inspired her whole team.', correct: 'Her ambition to succeed in her career inspired her whole team.', note: 'An inspiring drive to succeed is described as ambition, not greed.' },
    { incorrect: 'His ambition led him to cheat his investors out of their savings.', correct: 'His greed led him to cheat his investors out of their savings.', note: 'Cheating others for personal gain reflects greed, not ambition.' },
    { incorrect: 'Greed is always viewed as an admirable, positive trait.', correct: 'Ambition is often viewed as an admirable, positive trait; greed is usually viewed negatively.', note: '"Ambition" typically carries a positive connotation; "greed" does not.' },
  ],
  correctExamples: [
    "Her ambition led her to open three successful restaurants.",
    'His greed for profit caused him to ignore his employees\' safety concerns.',
    'Ambitious students often set challenging academic goals for themselves.',
    'The novel explores how greed can corrupt even well-meaning people.',
    'His ambition to become a doctor motivated years of hard study.',
    'The company was criticized for its greedy pricing during the crisis.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: Her strong desire to become a successful entrepreneur is best described as _____.', answer: 'ambition', explanation: 'A positive drive toward achieving a goal is ambition.' },
    { prompt: 'Choose the correct word: His excessive desire for more money, even at his employees\' expense, is best described as _____.', answer: 'greed', explanation: 'An excessive, selfish desire that harms others is greed.' },
    { prompt: 'Fix the sentence: "Her ambition led her to exploit her business partners for personal gain."', answer: 'Her greed led her to exploit her business partners for personal gain.', explanation: 'Exploiting others for personal gain reflects greed, not ambition.' },
  ],
  faqs: [
    { question: 'Can ambition turn into greed?', answer: 'Yes — many stories and real-life examples show how an initially healthy ambition can shift into greed when someone starts pursuing success at the unfair expense of others.' },
    { question: 'Is ambition always a good trait?', answer: 'Ambition is generally viewed positively, though even ambition can become harmful if it pushes someone to ignore ethics or other people\'s wellbeing in the pursuit of a goal.' },
    { question: 'Why is greed viewed so negatively across cultures?', answer: 'Greed is widely criticized because it prioritizes personal gain over fairness and the wellbeing of others, often leading to exploitation, inequality, or harm within a community.' },
  ],
  related: [
    { to: '/what-is-the-difference/fact-vs-truth/', text: 'Fact vs. Truth' },
    { to: '/what-is-the-difference/problem-vs-issue/', text: 'Problem vs. Issue' },
    { to: '/what-is-the-difference/trauma-vs-sadness/', text: 'Trauma vs. Sadness' },
  ],
};

const AmbitionVsGreedPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default AmbitionVsGreedPage;
