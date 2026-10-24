import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Job vs. Work: What's the Difference? | TypoGrammar",
  metaDescription: "Job vs work: \"job\" is a specific, countable position or role; \"work\" is a general, usually uncountable concept of activity or employment. See the rule, examples, and a quiz.",
  slug: 'job-vs-work',
  h1: "Job vs. Work: What's the Difference?",
  breadcrumbLabel: 'Job vs. Work',
  datePublished: '2026-07-04',
  dateModified: '2026-07-04',
  quickAnswer: "\"Job\" is a countable noun referring to a specific position or role someone is employed to do (she got a new job at a bank). \"Work\" is usually an uncountable noun referring to the general activity or effort of working, or tasks to complete (I have a lot of work to do). You can count jobs (one job, two jobs) but you cannot normally count \"works\" in this sense.",
  tableColumns: ['Job', 'Work'],
  tableRows: [
    { feature: 'Countable?', values: ['Yes (a job, two jobs)', 'Usually uncountable (no plural in this sense)'] },
    { feature: 'Refers to', values: ['A specific position or role', 'General activity, effort, or employment'] },
    { feature: 'Example', values: ['She has a great job as a teacher.', 'She has a lot of work this week.'] },
    { feature: 'Can use an article?', values: ['Yes: "a job", "the job"', 'Rarely: usually no article ("work", not "a work")'] },
  ],
  terms: [
    {
      label: 'Job',
      summary: 'A specific, countable position or role that someone is paid to do.',
      pattern: 'a/the + job',
      examples: ['"He got a new job last month."', '"This is the best job I\'ve ever had."', '"She applied for three different jobs."'],
    },
    {
      label: 'Work',
      summary: 'The general, usually uncountable concept of activity, effort, tasks, or employment.',
      pattern: 'work (no article, uncountable)',
      examples: ['"I have too much work this week."', '"She goes to work at 8am."', '"He is out of work right now."'],
    },
  ],
  grammarRule: '"Job" is countable and refers to a specific position (you can have "a job" or "two jobs"). "Work" is generally uncountable and refers to activity, tasks, or effort in general — it does not take "a" or a plural form in this everyday sense.',
  extraRule: 'Common fixed expressions use "work", not "job": go to work, be at work, be out of work, work overtime. Common fixed expressions use "job": get a job, lose a job, apply for a job, quit a job.',
  mistakes: [
    { incorrect: 'I have a new work at the hospital.', correct: 'I have a new job at the hospital.', note: 'A specific position needs the countable noun "job", not "work".' },
    { incorrect: 'She has a lot of jobs to finish before Friday.', correct: 'She has a lot of work to finish before Friday.', note: 'General tasks/effort need the uncountable noun "work", not "job".' },
    { incorrect: 'He goes to job every day at 9am.', correct: 'He goes to work every day at 9am.', note: 'The fixed expression is "go to work", not "go to job".' },
  ],
  correctExamples: [
    'I\'m looking for a part-time job while I study.',
    'There\'s so much work piled up on my desk.',
    'She quit her job to start her own business.',
    'He\'s been out of work since the factory closed.',
    'This is a demanding job, but I enjoy it.',
    'We finished all the work before the deadline.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: "He finally found a _____ as a graphic designer."', answer: 'job', explanation: 'This is a specific, countable position, so it needs "job".' },
    { prompt: 'Choose the correct word: "I still have so much _____ to do before the trip."', answer: 'work', explanation: 'This refers to general tasks/effort, an uncountable concept, so it needs "work".' },
    { prompt: 'Fix the sentence: "She has two work: one in the morning and one at night."', answer: 'She has two jobs: one in the morning and one at night.', explanation: 'Countable positions need "jobs" in the plural, not "work".' },
  ],
  faqs: [
    { question: 'Can "work" ever be countable?', answer: 'Yes, but with a different meaning: "a work" can refer to a piece of art, literature, or music, as in "a work by Picasso" or "the complete works of Shakespeare." In the everyday sense of employment/effort, "work" stays uncountable.' },
    { question: 'What is the difference between "job" and "career"?', answer: '"Job" refers to one specific position you currently hold or are applying for, while "career" refers to your whole professional path over time, often across several jobs, as in "a career in medicine."' },
    { question: 'Is "occupation" the same as "job"?', answer: '"Occupation" is a more formal word, often used on official forms, referring to the type of work someone does in general (e.g., "teacher", "engineer"), while "job" more often refers to the specific position at a specific employer.' },
  ],
  related: [
    { to: '/what-is-the-difference/customer-vs-client/', text: 'Customer vs. Client' },
    { to: '/what-is-the-difference/farther-vs-further/', text: 'Farther vs. Further' },
    { to: '/what-is-the-difference/custom-vs-habit/', text: 'Custom vs. Habit' },
  ],
};

const JobVsWorkPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default JobVsWorkPage;
