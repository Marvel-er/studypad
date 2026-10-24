import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "IQ vs. Intelligence: What's the Difference? | TypoGrammar",
  metaDescription: 'IQ vs intelligence: "IQ" is a specific numerical score from a standardized test, while "intelligence" is the broader concept of mental ability that no single test fully captures. See the rule, examples, and a quiz.',
  slug: 'iq-vs-intelligence',
  h1: "IQ vs. Intelligence: What's the Difference?",
  breadcrumbLabel: 'IQ vs. Intelligence',
  datePublished: '2026-07-05',
  dateModified: '2026-07-05',
  quickAnswer: '"IQ" (Intelligence Quotient) is a specific numerical score from a standardized test designed to measure certain cognitive abilities, such as logical reasoning and pattern recognition, compared to an average score of 100. "Intelligence" is the broader, more general concept of mental ability — including reasoning, learning, problem-solving, creativity, and practical skills — that cannot be fully captured by any single test or number.',
  tableColumns: ['IQ', 'Intelligence'],
  tableRows: [
    { feature: 'What it is', values: ['A test score (a number)', 'A broad mental ability or trait'] },
    { feature: 'Measured by', values: ['A standardized test', 'Not fully measurable by any single test'] },
    { feature: 'Scope', values: ['Narrow — logic, patterns, memory, math', 'Broad — includes creativity and practical skills'] },
    { feature: 'Can change', values: ['Relatively stable, but can shift slightly', 'Can develop through learning, environment, experience'] },
  ],
  terms: [
    {
      label: 'IQ',
      summary: 'A numerical score from a standardized test intended to measure specific cognitive abilities relative to an average of 100.',
      pattern: 'an IQ of + number',
      examples: ['"Her IQ was measured at 128."', '"IQ tests focus on logic and pattern recognition."'],
    },
    {
      label: 'Intelligence',
      summary: 'The general, broader concept of mental ability, encompassing reasoning, learning, creativity, and problem-solving beyond what a single test measures.',
      pattern: 'intelligence (uncountable)',
      examples: ['"His intelligence showed in how quickly he solved real-world problems."', '"Intelligence takes many forms beyond test scores."'],
    },
  ],
  grammarRule: 'Use "IQ" only when referring to the specific number or score from an intelligence test. Use "intelligence" for the general concept of mental ability, which is wider than what any IQ test measures.',
  extraRule: 'Many psychologists distinguish IQ from other forms of intelligence, such as emotional intelligence (EQ) and practical or creative intelligence, which standard IQ tests do not directly measure.',
  mistakes: [
    { incorrect: 'Her intelligence was measured at 130 on the test.', correct: 'Her IQ was measured at 130 on the test.', note: 'A specific test score is an IQ, not "intelligence" itself.' },
    { incorrect: 'A high IQ guarantees success in every area of life.', correct: 'High intelligence, in its many forms, can help with success, but a high IQ score alone does not guarantee it.', note: 'IQ measures only certain cognitive skills, not every factor behind real-world success.' },
    { incorrect: 'IQ and intelligence mean exactly the same thing in every context.', correct: 'IQ refers to a specific test score, while intelligence is a much broader concept.', note: 'IQ is one narrow measurement; intelligence is the wider trait it attempts to estimate.' },
  ],
  correctExamples: [
    'He scored an IQ of 115 on the standardized test.',
    'Her intelligence became obvious in how creatively she solved the problem.',
    'IQ tests mainly measure logical and mathematical reasoning.',
    'Emotional intelligence is not captured by a typical IQ score.',
    'Intelligence can be developed through education and experience.',
    'A person with an average IQ can still show remarkable practical intelligence.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: The psychologist recorded a score of 122 as his _____.', answer: 'IQ', explanation: 'A specific numerical test score is called an IQ.' },
    { prompt: 'Choose the correct word: Creativity and problem-solving skill are both forms of _____.', answer: 'intelligence', explanation: 'Broad mental abilities beyond a single score fall under "intelligence".' },
    { prompt: 'Fix the sentence: "His IQ includes creativity, emotional skill, and practical problem-solving."', answer: 'His intelligence includes creativity, emotional skill, and practical problem-solving.', explanation: 'IQ refers only to a test score; the broader set of abilities is intelligence.' },
  ],
  faqs: [
    { question: 'Is IQ a perfect measure of intelligence?', answer: 'No. IQ tests measure specific cognitive skills like logic, memory, and pattern recognition, but they do not fully capture creativity, emotional understanding, or practical problem-solving, which are also part of intelligence.' },
    { question: 'Can IQ change over time?', answer: "IQ scores are relatively stable across a person's life, though they can shift somewhat due to education, health, and other environmental factors." },
    { question: 'What is emotional intelligence?', answer: 'Emotional intelligence (EQ) refers to the ability to recognize, understand, and manage emotions in oneself and others — a form of intelligence not measured by standard IQ tests.' },
  ],
  related: [
    { to: '/what-is-the-difference/skill-vs-talent/', text: 'Skill vs. Talent' },
    { to: '/what-is-the-difference/professor-vs-teacher/', text: 'Professor vs. Teacher' },
    { to: '/what-is-the-difference/fact-vs-truth/', text: 'Fact vs. Truth' },
  ],
};

const IQVsIntelligencePage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default IQVsIntelligencePage;
