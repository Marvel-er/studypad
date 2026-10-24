import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Problem vs. Issue: What's the Difference? | TypoGrammar",
  metaDescription: 'Problem vs issue: a "problem" is a difficulty that needs solving, while an "issue" is a broader, often more neutral word for a topic or concern. See the rule, examples, and a quiz.',
  slug: 'problem-vs-issue',
  h1: "Problem vs. Issue: What's the Difference?",
  breadcrumbLabel: 'Problem vs. Issue',
  datePublished: '2026-07-05',
  dateModified: '2026-07-05',
  quickAnswer: 'A "problem" is a difficulty or obstacle that needs to be solved, often implying something is clearly wrong and requires a direct fix. An "issue" is a broader, often more neutral term that can mean a topic, concern, or point of discussion — it doesn\'t always imply something is broken, and is sometimes chosen as a softer way to describe a problem.',
  tableColumns: ['Problem', 'Issue'],
  tableRows: [
    { feature: 'Implication', values: ['Something is wrong and needs solving', 'A topic or concern (can be neutral)'] },
    { feature: 'Tone', values: ['Can sound more direct or negative', 'Can sound softer, more diplomatic'] },
    { feature: 'Neutral topic use', values: ['Less common for neutral topics', '"Let\'s discuss the issue of remote work."'] },
    { feature: 'Something broken', values: ['"There is a problem with the printer."', '"There is an issue with the printer." (softer)'] },
  ],
  terms: [
    {
      label: 'Problem',
      summary: 'A difficulty or obstacle that is clearly wrong and typically needs a direct solution.',
      pattern: 'a problem (with + thing)',
      examples: ['"There is a problem with the engine."', '"We need to solve this problem quickly."'],
    },
    {
      label: 'Issue',
      summary: 'A broader, often more neutral term for a topic, concern, or point of discussion, which may or may not involve something being wrong.',
      pattern: 'an issue (of/with + topic)',
      examples: ['"Let\'s discuss the issue of school start times."', '"He raised an issue about the new policy."'],
    },
  ],
  grammarRule: 'Use "problem" when something is clearly broken, wrong, or needs a direct solution. Use "issue" for a broader topic of concern or discussion, which may or may not involve something being wrong — it is often chosen as a milder, more diplomatic word than "problem."',
  extraRule: 'In technical and customer service contexts, "issue" has become the more common word for describing malfunctions or complaints, largely because it sounds less blaming than "problem."',
  mistakes: [
    { incorrect: 'The teacher wants to discuss the problem of school start times at the next meeting.', correct: 'The teacher wants to discuss the issue of school start times at the next meeting.', note: 'A neutral topic open for discussion, not necessarily something broken, is better described as an issue.' },
    { incorrect: 'Every issue in life needs an urgent solution today.', correct: 'Every problem in life needs an urgent solution today.', note: '"Problem" fits better when emphasizing something that clearly needs fixing.' },
    { incorrect: 'The customer said there was an issue because the product was completely broken and unusable.', correct: 'The customer said there was a problem because the product was completely broken and unusable.', note: 'When something is clearly and seriously broken, "problem" states it more directly than the softer "issue."' },
  ],
  correctExamples: [
    'There is a problem with the car — the engine won\'t start.',
    'The committee will discuss the issue of public transportation funding.',
    'She reported a technical issue with her account login.',
    'They need to fix the problem before the deadline.',
    'Climate change is a major issue debated around the world.',
    'The mechanic quickly identified the problem with the brakes.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: The team wants to raise the _____ of flexible work hours at the next meeting.', answer: 'issue', explanation: 'A neutral topic for discussion is better described as an issue.' },
    { prompt: 'Choose the correct word: The washing machine is leaking water everywhere — there is a serious _____.', answer: 'problem', explanation: 'Something clearly broken needing a direct fix is a problem.' },
    { prompt: 'Fix the sentence: "Let\'s discuss the problem of school uniform policy at the parent meeting."', answer: 'Let\'s discuss the issue of school uniform policy at the parent meeting.', explanation: 'A topic open for discussion, without implying something is broken, fits "issue" better.' },
  ],
  faqs: [
    { question: 'Are "problem" and "issue" always interchangeable?', answer: 'They overlap in many everyday situations, but "problem" leans toward something clearly wrong needing a fix, while "issue" can describe a neutral topic or a softer way of raising a concern.' },
    { question: 'Why do customer service reps say "issue" instead of "problem"?', answer: '"Issue" tends to sound less blaming and more neutral, which is often preferred in customer service to keep the tone calm and cooperative.' },
    { question: 'Can "issue" mean a magazine edition?', answer: 'Yes — in publishing, "issue" also refers to a specific edition of a magazine or journal, an unrelated meaning from the "topic or concern" sense discussed here.' },
  ],
  related: [
    { to: '/what-is-the-difference/fact-vs-truth/', text: 'Fact vs. Truth' },
    { to: '/what-is-the-difference/trauma-vs-sadness/', text: 'Trauma vs. Sadness' },
    { to: '/what-is-the-difference/skill-vs-talent/', text: 'Skill vs. Talent' },
  ],
};

const ProblemVsIssuePage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default ProblemVsIssuePage;
