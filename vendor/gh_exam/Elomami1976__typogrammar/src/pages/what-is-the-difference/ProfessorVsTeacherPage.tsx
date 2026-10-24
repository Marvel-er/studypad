import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Professor vs. Teacher: What's the Difference? | TypoGrammar",
  metaDescription: 'Professor vs teacher: "teacher" is the general word for anyone who instructs students, while "professor" is a specific academic rank at a college or university. See the rule, examples, and a quiz.',
  slug: 'professor-vs-teacher',
  h1: "Professor vs. Teacher: What's the Difference?",
  breadcrumbLabel: 'Professor vs. Teacher',
  datePublished: '2026-07-05',
  dateModified: '2026-07-05',
  quickAnswer: 'A "teacher" is a general term for anyone who instructs students, most commonly used for primary and secondary (K-12) education. A "professor" is a specific, higher academic rank held by an instructor at a college or university, usually requiring an advanced degree (often a PhD) and involving research responsibilities alongside teaching.',
  tableColumns: ['Teacher', 'Professor'],
  tableRows: [
    { feature: 'Level taught', values: ['Primary/secondary school (also a general term)', 'College/university'] },
    { feature: 'Typical qualification', values: ['Teaching degree/certification', 'Doctorate (PhD) in most countries'] },
    { feature: 'Main duties', values: ['Classroom instruction', 'Teaching, research, publishing, advising'] },
    { feature: 'Scope of term', values: ['General — any instructor', 'Specific academic rank/title'] },
  ],
  terms: [
    {
      label: 'Teacher',
      summary: 'The general word for someone who instructs students, especially at school level, or as a broad category covering all instructors.',
      pattern: 'a/the teacher (of + subject)',
      examples: ['"Her math teacher assigned extra homework."', '"He has been a high school teacher for ten years."'],
    },
    {
      label: 'Professor',
      summary: 'A specific university-level academic rank, usually earned through advanced degrees and ongoing research, alongside teaching.',
      pattern: 'a/the professor (of + subject)',
      examples: ['"The professor published a new study on climate change."', '"She became a professor after finishing her PhD and years of research."'],
    },
  ],
  grammarRule: 'Use "teacher" as the general word for anyone who teaches, especially at school level, or as a broad category covering all instructors. Use "professor" specifically for a university-level academic rank, usually earned through advanced degrees and research.',
  extraRule: 'In casual speech, university instructors are sometimes loosely called "teachers," and all professors are technically teachers — but not all teachers are professors, since "professor" is a specific rank within the broader "teacher" category.',
  mistakes: [
    { incorrect: 'The elementary school professor gave the students a math worksheet.', correct: 'The elementary school teacher gave the students a math worksheet.', note: 'Elementary instructors are called teachers, not professors.' },
    { incorrect: 'Every university teacher must complete a PhD and publish research to get the title.', correct: 'Every university professor must complete a PhD and publish research to get the title.', note: '"Professor" specifically requires the advanced degree and research record described here.' },
    { incorrect: 'She calls herself a professor after finishing her teaching certificate for high school.', correct: 'She calls herself a teacher after finishing her teaching certificate for high school.', note: 'A high school teaching certificate leads to the title "teacher," not "professor."' },
  ],
  correctExamples: [
    'His high school English teacher inspired him to study literature.',
    'The university professor spent the morning in the research lab.',
    'She is training to become a certified elementary school teacher.',
    'The professor is publishing a new paper alongside her teaching duties.',
    'Every professor is technically a teacher, but not every teacher is a professor.',
    'The chemistry professor has taught at the university for fifteen years.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: The person who teaches third grade at the local school is called a _____.', answer: 'teacher', explanation: 'K-12 instructors are called teachers, the general term.' },
    { prompt: 'Choose the correct word: A university instructor with a PhD who both teaches and publishes research is a _____.', answer: 'professor', explanation: 'Teaching combined with research at a university is the professor rank.' },
    { prompt: 'Fix the sentence: "My kindergarten professor reads us a story every afternoon."', answer: 'My kindergarten teacher reads us a story every afternoon.', explanation: 'Kindergarten instructors are teachers, not professors.' },
  ],
  faqs: [
    { question: 'Are all university instructors professors?', answer: 'Not necessarily — some university instructors hold titles like "lecturer" or "instructor" without having earned the full "professor" rank, which usually requires an advanced degree and research record.' },
    { question: 'Can a professor also be called a teacher?', answer: 'Yes — "teacher" is the broad category that includes professors, so it is accurate (if informal) to call a professor a teacher, even though "professor" is more specific.' },
    { question: 'What ranks exist below professor?', answer: 'Many universities use a ladder such as lecturer, assistant professor, associate professor, and full professor, each requiring different levels of experience and research achievement.' },
  ],
  related: [
    { to: '/what-is-the-difference/iq-vs-intelligence/', text: 'IQ vs. Intelligence' },
    { to: '/what-is-the-difference/skill-vs-talent/', text: 'Skill vs. Talent' },
    { to: '/what-is-the-difference/internship-vs-apprenticeship/', text: 'Internship vs. Apprenticeship' },
  ],
};

const ProfessorVsTeacherPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default ProfessorVsTeacherPage;
