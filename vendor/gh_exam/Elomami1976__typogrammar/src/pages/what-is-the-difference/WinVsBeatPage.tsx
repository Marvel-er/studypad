import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Win vs. Beat: What's the Difference? | TypoGrammar",
  metaDescription: "Win vs beat: \"win\" takes a competition, game, or prize as its object; \"beat\" takes an opponent (a person or team) as its object. See the rule, examples, and a quiz.",
  slug: 'win-vs-beat',
  h1: "Win vs. Beat: What's the Difference?",
  breadcrumbLabel: 'Win vs. Beat',
  datePublished: '2026-07-04',
  dateModified: '2026-07-04',
  quickAnswer: "\"Win\" is used with the competition, game, prize, or match as the object — you win a match, a prize, an election (she won the tournament). \"Beat\" is used with the opponent as the object — you beat a person or team (she beat her rival in the final). The object tells you which verb is correct: a thing to win, a person/team to beat.",
  tableColumns: ['Win', 'Beat'],
  tableRows: [
    { feature: 'Typical object', values: ['A competition, prize, game, match, election', 'An opponent (a person or team)'] },
    { feature: 'Can it take a person as object?', values: ['No', 'Yes — that is its normal object'] },
    { feature: 'Example', values: ['She won the championship.', 'She beat the defending champion.'] },
    { feature: 'Past tense', values: ['won', 'beat (beaten as past participle)'] },
  ],
  terms: [
    {
      label: 'Win',
      summary: 'Succeed in a competition, game, prize, or contest — the object is the event or prize itself.',
      pattern: 'win + competition/prize/game',
      examples: ['"They won the World Cup."', '"She won first prize."', '"He won the election easily."'],
    },
    {
      label: 'Beat',
      summary: 'Defeat an opponent — the object is the person or team you defeated.',
      pattern: 'beat + opponent (person/team)',
      examples: ['"Our team beat the rivals 3-1."', '"She beat him in the final round."', '"We beat our own record."'],
    },
  ],
  grammarRule: 'Use "win" with a competition, match, prize, title, or election as the object. Use "beat" with the opponent — a person or team — as the object. You cannot "win" a person, and you cannot "beat" a prize.',
  extraRule: 'Both can appear in the same sentence describing one event from different angles: "She beat her opponent and won the tournament" — "beat" refers to the rival, "won" refers to the competition.',
  mistakes: [
    { incorrect: 'I won him in the final match.', correct: 'I beat him in the final match.', note: '"Him" is a person (the opponent), so it needs "beat", not "win".' },
    { incorrect: 'Our team beat the championship this year.', correct: 'Our team won the championship this year.', note: '"The championship" is the competition itself, so it needs "won", not "beat".' },
    { incorrect: 'She won her sister at chess again.', correct: 'She beat her sister at chess again.' },
  ],
  correctExamples: [
    'He won the lottery last month.',
    'She beat three other finalists to take the title.',
    'They won the match 2-0.',
    'The champion beat every challenger this season.',
    'Did you win the raffle?',
    'Our school beat the rival school in the debate competition.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: "He _____ the marathon for the second year in a row."', answer: 'won', explanation: '"The marathon" is the competition itself, so it needs "won".' },
    { prompt: 'Choose the correct word: "She _____ her opponent in straight sets."', answer: 'beat', explanation: '"Her opponent" is a person, so it needs "beat".' },
    { prompt: 'Fix the sentence: "We won the other team by ten points."', answer: 'We beat the other team by ten points.', explanation: '"The other team" is the opponent, so it needs "beat", not "won".' },
  ],
  faqs: [
    { question: 'Can I say "beat a record"?', answer: 'Yes — "beat a record" is a common, correct expression meaning to surpass a previous best result, treating the record almost like an opponent to overcome. It\'s different from "win a record," which isn\'t standard usage.' },
    { question: 'What is the past participle of "beat"?', answer: 'The past simple is "beat" and the past participle is "beaten": "She has beaten every opponent this year." Learners often mistakenly use "beat" for both forms.' },
    { question: 'Is "defeat" the same as "beat"?', answer: '"Defeat" is a more formal synonym for "beat" in this competitive sense, and it follows the same pattern — used with an opponent as the object, as in "The team defeated their rivals 4-1."' },
  ],
  related: [
    { to: '/what-is-the-difference/remember-vs-remind/', text: 'Remember vs. Remind' },
    { to: '/what-is-the-difference/borrow-vs-lend/', text: 'Borrow vs. Lend' },
    { to: '/grammar-mistakes/win-vs-beat/', text: 'Win vs. Beat (Grammar Mistakes)' },
  ],
};

const WinVsBeatPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default WinVsBeatPage;
