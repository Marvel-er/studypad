import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Job vs. Career: What's the Difference? | TypoGrammar",
  metaDescription: 'Job vs career: a "job" is a specific paid position, often short-term, while a "career" is the long-term progression of related jobs and experience in a field. See the rule, examples, and a quiz.',
  slug: 'job-vs-career',
  h1: "Job vs. Career: What's the Difference?",
  breadcrumbLabel: 'Job vs. Career',
  datePublished: '2026-07-05',
  dateModified: '2026-07-05',
  quickAnswer: 'A "job" is a specific position or role you are paid to do, often short-term and focused mainly on earning income (a summer job, a job at a café). A "career" is the long-term progression of related jobs, positions, and experience in a field, reflecting professional growth and long-term goals (a career in medicine, a career in journalism). A single career is usually made up of several different jobs over time.',
  tableColumns: ['Job', 'Career'],
  tableRows: [
    { feature: 'Time frame', values: ['Can be short-term or temporary', 'Long-term, spans years or decades'] },
    { feature: 'Focus', values: ['Earning income in a specific role', 'Professional growth and progression in a field'] },
    { feature: 'Example', values: ['"She has a part-time job at a bookstore."', '"She is building a career in publishing."'] },
    { feature: 'Typical usage', values: ['a job / jobs (casual, countable)', "a career / one's career (reflective, long-term)"] },
  ],
  terms: [
    {
      label: 'Job',
      summary: 'A specific paid position or role, which can be short-term, part-time, or unrelated to long-term professional goals.',
      pattern: 'a job (at/as + role)',
      examples: ['"He took a job at the warehouse to save money for college."', '"She has had three different jobs this year."'],
    },
    {
      label: 'Career',
      summary: "The long-term path of related jobs, roles, and experience someone builds in a particular field over years or decades.",
      pattern: "a career (in + field)",
      examples: ['"She has spent her entire career in nursing."', '"He changed careers from teaching to software development."'],
    },
  ],
  grammarRule: 'Use "job" for a specific paid position, which can be temporary or unrelated to long-term goals. Use "career" for the broader, long-term path of related jobs and professional development within a field.',
  extraRule: 'A single career can include many different jobs — for example, someone can have a long career in teaching while having held several different teaching jobs at different schools.',
  mistakes: [
    { incorrect: 'He has had the same career at the coffee shop for one summer.', correct: 'He has had the same job at the coffee shop for one summer.', note: 'A short-term, specific position like a summer coffee shop role is a job, not a career.' },
    { incorrect: 'She is passionate about her job in medicine, which she has planned for over a decade.', correct: 'She is passionate about her career in medicine, which she has planned for over a decade.', note: 'A long-term professional path planned over years is a career.' },
    { incorrect: 'Quitting one job ended her entire career in journalism forever.', correct: 'Quitting one job did not end her entire career in journalism — she found a new job in the same field.', note: 'Losing a single job does not necessarily end a broader career in that field.' },
  ],
  correctExamples: [
    'His first job after graduating was as a junior accountant.',
    'She built a thirty-year career in international law.',
    'Changing jobs within the same company is common early in a career.',
    'He is looking for a summer job, not a long-term career move.',
    'Her career in medicine began with a residency at a small hospital.',
    'They both switched jobs but stayed in the same overall career field.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: She took a weekend _____ at a local restaurant to earn extra cash.', answer: 'job', explanation: 'A short-term, specific paid role is a job.' },
    { prompt: 'Choose the correct word: After twenty years in finance, he considers it his lifelong _____.', answer: 'career', explanation: 'A long-term professional path spanning decades is a career.' },
    { prompt: 'Fix the sentence: "She has held the same job in nursing for the past twenty-five years, moving through several hospitals."', answer: 'She has had the same career in nursing for the past twenty-five years, moving through several jobs at different hospitals.', explanation: 'A twenty-five-year professional path is a career, made up of several individual jobs.' },
  ],
  faqs: [
    { question: 'Can you have a career without a specific job title?', answer: 'A career is usually made up of a series of jobs and roles, so while the term describes the overall path, it is still built from specific jobs held along the way.' },
    { question: 'Is switching jobs bad for a career?', answer: 'Not necessarily — moving between related jobs can build valuable experience and is a normal part of many careers, as long as the moves fit a coherent professional direction.' },
    { question: 'What is the difference between job satisfaction and career satisfaction?', answer: 'Job satisfaction refers to how someone feels about their current specific role, while career satisfaction reflects a broader sense of fulfillment with their overall professional path over time.' },
  ],
  related: [
    { to: '/what-is-the-difference/job-vs-work/', text: 'Job vs. Work' },
    { to: '/what-is-the-difference/founder-vs-ceo/', text: 'Founder vs. CEO' },
    { to: '/what-is-the-difference/salary-vs-wage/', text: 'Salary vs. Wage' },
  ],
};

const JobVsCareerPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default JobVsCareerPage;
