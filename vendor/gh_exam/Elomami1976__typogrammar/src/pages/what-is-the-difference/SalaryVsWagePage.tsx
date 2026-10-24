import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Salary vs. Wage: What's the Difference? | TypoGrammar",
  metaDescription: 'Salary vs wage: a "salary" is a fixed amount paid regardless of exact hours worked, while a "wage" is pay calculated by the hour. See the rule, examples, and a quiz.',
  slug: 'salary-vs-wage',
  h1: "Salary vs. Wage: What's the Difference?",
  breadcrumbLabel: 'Salary vs. Wage',
  datePublished: '2026-07-05',
  dateModified: '2026-07-05',
  quickAnswer: 'A "salary" is a fixed amount of pay agreed for a year (or pay period), divided evenly regardless of the exact hours worked — common for full-time professional or office roles. A "wage" is pay calculated based on the number of hours (or units of work) actually worked, often paid weekly or biweekly — common for hourly, part-time, or manual labor roles.',
  tableColumns: ['Salary', 'Wage'],
  tableRows: [
    { feature: 'Basis', values: ['Fixed annual amount, divided into equal pay periods', 'Calculated by hours worked (hourly rate × hours)'] },
    { feature: 'Changes with hours', values: ['No — usually the same regardless of extra hours', 'Yes — more hours worked means more pay'] },
    { feature: 'Typical roles', values: ['Full-time professional/office jobs', 'Hourly, part-time, or manual labor jobs'] },
    { feature: 'Overtime', values: ['Often not paid separately (exempt)', 'Usually paid at a higher overtime rate'] },
  ],
  terms: [
    {
      label: 'Salary',
      summary: 'A fixed sum of pay agreed for a year or set period, paid in equal installments regardless of the exact hours worked in any given week.',
      pattern: 'a salary of $X a year',
      examples: ['"She earns an annual salary of $65,000."', '"His salary stays the same whether he works 38 or 45 hours."'],
    },
    {
      label: 'Wage',
      summary: 'Pay calculated directly from the hours (or units) actually worked, typically expressed as an hourly rate.',
      pattern: 'a wage of $X an hour',
      examples: ['"He earns a wage of $19 an hour."', '"Her wages depend on how many shifts she works each week."'],
    },
  ],
  grammarRule: 'Use "salary" for a fixed sum paid regardless of exact hours worked, usually stated as an annual figure (e.g., "$60,000 a year"). Use "wage" for pay tied directly to hours worked, usually stated as an hourly rate (e.g., "$18 an hour").',
  extraRule: '"Wages" (plural) is often used to refer to a worker\'s pay in general or legal contexts ("minimum wage", "wage laws"), while "salary" is rarely used in the same plural, legal sense.',
  mistakes: [
    { incorrect: 'The factory worker earns a fixed salary no matter how many hours she works.', correct: 'The factory worker earns a wage based on how many hours she works.', note: 'Pay that changes with hours worked is a wage, not a fixed salary.' },
    { incorrect: "His annual wage of $75,000 doesn't change even if he works extra hours.", correct: "His annual salary of $75,000 doesn't change even if he works extra hours.", note: 'A fixed yearly amount that does not change with hours is a salary.' },
    { incorrect: 'Minimum salary laws set the lowest hourly rate an employer can pay.', correct: 'Minimum wage laws set the lowest hourly rate an employer can pay.', note: 'Laws about hourly pay rates use the term "wage", not "salary".' },
  ],
  correctExamples: [
    'She negotiated a starting salary of $80,000 for the new role.',
    'He earns a wage of $22 an hour at the warehouse.',
    'Salaried employees are often not paid extra for occasional overtime.',
    'Her weekly wages depend on how many shifts she picks up.',
    'The company offers a competitive salary plus annual bonuses.',
    'Minimum wage increased this year for hourly workers across the state.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: A part-time cashier paid $17 for every hour worked earns a _____.', answer: 'wage', explanation: 'Pay calculated by the hour is a wage.' },
    { prompt: 'Choose the correct word: A full-time manager paid the same $70,000 total regardless of hours earns a _____.', answer: 'salary', explanation: 'A fixed yearly amount regardless of hours is a salary.' },
    { prompt: 'Fix the sentence: "The construction crew is paid a fixed annual salary no matter how many hours they work each week."', answer: 'The construction crew is paid an hourly wage based on how many hours they work each week.', explanation: 'Pay that varies with hours worked is described as a wage.' },
  ],
  faqs: [
    { question: 'Is salary always higher than wage?', answer: 'Not necessarily. Some skilled hourly workers earn more overall than some salaried employees, especially when overtime pay is included — the terms describe how pay is calculated, not how much it totals.' },
    { question: 'Can a salaried job still pay overtime?', answer: 'In some cases, yes, depending on local labor laws and whether the role is classified as "exempt" or "non-exempt" from overtime rules, but many salaried roles do not receive extra pay for additional hours.' },
    { question: 'What is minimum wage?', answer: 'Minimum wage is the lowest hourly rate an employer is legally allowed to pay a worker, and it applies to wage-based, hourly pay rather than fixed salaries.' },
  ],
  related: [
    { to: '/what-is-the-difference/job-vs-career/', text: 'Job vs. Career' },
    { to: '/what-is-the-difference/founder-vs-ceo/', text: 'Founder vs. CEO' },
    { to: '/what-is-the-difference/money-vs-currency/', text: 'Money vs. Currency' },
  ],
};

const SalaryVsWagePage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default SalaryVsWagePage;
