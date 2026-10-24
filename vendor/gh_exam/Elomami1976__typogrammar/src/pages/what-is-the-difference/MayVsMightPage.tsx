import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "May vs. Might: What's the Difference? | TypoGrammar",
  metaDescription: "May vs might: both show possibility, but \"might\" usually suggests a lower or more hypothetical chance than \"may\", and \"may\" is also used for formal permission. See the rule, examples, and a quiz.",
  slug: 'may-vs-might',
  h1: "May vs. Might: What's the Difference?",
  breadcrumbLabel: 'May vs. Might',
  datePublished: '2026-07-04',
  dateModified: '2026-07-04',
  quickAnswer: "\"May\" and \"might\" both express possibility, but \"may\" often suggests a somewhat stronger or more immediate chance, while \"might\" is more tentative, hypothetical, or distant (it might rain vs. it may rain). \"May\" is also used for formal permission (may I come in?), a job \"might\" rarely does today. In casual speech, the two overlap heavily.",
  tableColumns: ['May', 'Might'],
  tableRows: [
    { feature: 'Degree of certainty', values: ['Slightly more likely / neutral possibility', 'More tentative, hypothetical, less certain'] },
    { feature: 'Permission', values: ['Yes — formal ("May I leave early?")', 'Rare, very indirect/polite'] },
    { feature: 'Past reported speech', values: ['Reports "may"', 'Reports both "may" and "might" (past of may)'] },
    { feature: 'Example', values: ['She may join us later.', 'She might join us, but she\'s not sure yet.'] },
  ],
  terms: [
    {
      label: 'May',
      summary: 'Expresses possibility (often present/future) and, formally, permission.',
      pattern: 'may + base verb',
      examples: ['"It may rain this afternoon."', '"May I ask you a question?"', '"He may already know the answer."'],
    },
    {
      label: 'Might',
      summary: 'Expresses a more tentative or hypothetical possibility; also the past/reported form of "may".',
      pattern: 'might + base verb',
      examples: ['"It might rain later, but I doubt it."', '"She said she might come."', '"If I had more time, I might travel more."'],
    },
  ],
  grammarRule: 'Use "may" for possibility that feels reasonably likely, and for formal requests of permission. Use "might" for possibility that feels more uncertain, distant, or hypothetical, and for reporting "may" in the past ("He said he may come" becomes "He said he might come").',
  extraRule: 'In everyday conversation, native speakers often use "may" and "might" interchangeably for possibility — the difference is a matter of degree, not a strict rule, except in formal permission requests, where only "may" is standard.',
  mistakes: [
    { incorrect: 'Might I use your phone, please?', correct: 'May I use your phone, please?', note: 'Formal permission requests almost always use "may", not "might".' },
    { incorrect: 'He told me yesterday that he may come today, but that was before he knew about the meeting.', correct: 'He told me yesterday that he might come today, but that was before he knew about the meeting.', note: 'Reporting a past possibility usually shifts "may" back to "might".' },
    { incorrect: 'You might not smoke in this building; it\'s against the rules.', correct: "You may not smoke in this building; it's against the rules.", note: '"May not" states a prohibition/rule; "might not" only expresses uncertainty about a future event.' },
  ],
  correctExamples: [
    'We may go to the beach this weekend if the weather is good.',
    'We might go to the beach, but it\'s only a small chance.',
    'May I borrow your pen for a moment?',
    'If she had studied harder, she might have passed the exam.',
    'Visitors may not enter after 9pm.',
    'He might be running late; the traffic looks bad today.',
  ],
  quiz: [
    { prompt: 'Choose the more formal way to ask permission: "_____ I leave the room?"', answer: 'May', explanation: 'Formal permission requests use "may", not "might".' },
    { prompt: 'Choose the word for a more distant, unlikely possibility: "I suppose I _____ win the lottery one day, but it\'s very unlikely."', answer: 'might', explanation: '"Might" suits a more tentative, hypothetical possibility.' },
    { prompt: 'Fix the sentence: "She said last week that she may visit us this weekend." (reported in the past)', answer: 'She said last week that she might visit us this weekend.', explanation: 'Reported speech about a past statement usually shifts "may" to "might".' },
  ],
  faqs: [
    { question: 'Is "might" simply the past tense of "may"?', answer: 'Historically yes, and it still works that way in reported speech ("she said she may go" → "she said she might go"). But in modern English, "might" also stands on its own as a present/future modal for weaker possibility, independent of any past tense.' },
    { question: 'Which is more polite: "may" or "might"?', answer: '"Might" can sound slightly more tentative and indirect, which some speakers use to be extra polite ("I might suggest..."), but "may" remains the standard, more formal choice for direct permission requests.' },
    { question: 'Can "may" and "might" both be used for suggestions?', answer: 'Yes. "You may want to check that again" and "You might want to check that again" both work as gentle suggestions, with "might" sounding a touch softer and more indirect.' },
  ],
  related: [
    { to: '/what-is-the-difference/must-vs-have-to/', text: 'Must vs. Have to' },
    { to: '/what-is-the-difference/can-vs-could/', text: 'Can vs. Could' },
    { to: '/what-is-the-difference/will-vs-be-going-to/', text: 'Will vs. Be Going to' },
  ],
};

const MayVsMightPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default MayVsMightPage;
