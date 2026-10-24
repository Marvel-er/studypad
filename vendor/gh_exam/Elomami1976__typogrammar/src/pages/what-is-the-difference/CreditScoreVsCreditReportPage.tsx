import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Credit Score vs. Credit Report: What's the Difference? | TypoGrammar",
  metaDescription: 'A "credit score" is a single number summarizing creditworthiness, while a "credit report" is the detailed document of accounts and payment history behind that score. See the rule, examples, and a quiz.',
  slug: 'credit-score-vs-credit-report',
  h1: "Credit Score vs. Credit Report: What's the Difference?",
  breadcrumbLabel: 'Credit Score vs. Credit Report',
  datePublished: '2026-07-05',
  dateModified: '2026-07-05',
  quickAnswer: 'A "credit score" is a single three-digit number summarizing how creditworthy a person is, calculated from their credit history. A "credit report" is the detailed underlying document listing a person\'s credit accounts, payment history, debts, and inquiries — the raw information used to calculate the credit score.',
  tableColumns: ['Credit Score', 'Credit Report'],
  tableRows: [
    { feature: 'Format', values: ['A single number (roughly 300-850)', 'A detailed, multi-page document'] },
    { feature: 'Contains', values: ['A summary reflecting creditworthiness', 'Full list of accounts, balances, payment history, inquiries'] },
    { feature: 'Purpose', values: ['Quick snapshot for lenders', 'Detailed record used to calculate the score and review history'] },
    { feature: 'Example', values: ['"Her credit score is 750."', '"He reviewed his credit report to check for errors."'] },
  ],
  terms: [
    {
      label: 'Credit Score',
      summary: "A single number, usually ranging from about 300 to 850, summarizing a person's creditworthiness based on their credit history.",
      pattern: 'a credit score of + number',
      examples: ['"A credit score above 700 is generally considered good."', '"His credit score dropped after he missed a payment."'],
    },
    {
      label: 'Credit Report',
      summary: "A detailed document listing a person's credit accounts, payment history, outstanding debts, and recent credit inquiries.",
      pattern: 'a/the credit report',
      examples: ['"She requested a free copy of her credit report."', '"He found an error on his credit report and disputed it."'],
    },
  ],
  grammarRule: 'Use "credit score" for the single summary number lenders use to quickly assess risk. Use "credit report" for the detailed document containing the full account and payment history behind that score.',
  extraRule: 'Checking your credit report regularly (not just your score) is important because errors in the report — like an account that isn\'t yours — can lower your score without your knowledge.',
  mistakes: [
    { incorrect: 'He reviewed his credit score, which listed all of his individual accounts and payment history.', correct: 'He reviewed his credit report, which listed all of his individual accounts and payment history.', note: 'A detailed, account-by-account document is the credit report, not the score.' },
    { incorrect: 'Her credit report is 720, a fairly good number.', correct: 'Her credit score is 720, a fairly good number.', note: 'A single numerical figure is the credit score.' },
    { incorrect: 'A credit score is a lengthy, detailed document with account-by-account information.', correct: 'A credit report is a lengthy, detailed document with account-by-account information; a credit score is a single summary number.', note: 'The detailed document is the credit report.' },
  ],
  correctExamples: [
    'His credit score rose after he paid off his credit card balance.',
    'She checks her credit report once a year for any errors.',
    'Lenders often check your credit score before approving a loan.',
    'The credit report listed every account she had opened in the past decade.',
    'A missed payment can quickly lower your credit score.',
    'He disputed an incorrect account listed on his credit report.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: The three-digit number lenders check to quickly judge risk is the _____.', answer: 'credit score', explanation: 'A single summary number is the credit score.' },
    { prompt: 'Choose the correct word: The detailed document listing every account, balance, and payment history is the _____.', answer: 'credit report', explanation: 'The full, detailed document is the credit report.' },
    { prompt: 'Fix the sentence: "She pulled her credit score to check for any incorrect accounts listed under her name."', answer: 'She pulled her credit report to check for any incorrect accounts listed under her name.', explanation: 'Checking for incorrect accounts requires the detailed credit report, not just the score.' },
  ],
  faqs: [
    { question: 'How often should you check your credit report?', answer: 'Many experts recommend checking your credit report at least once a year, since errors in the report can lower your credit score without your knowledge.' },
    { question: 'Does checking your own credit score lower it?', answer: 'No — checking your own credit score or report is considered a "soft inquiry" and does not affect your score, unlike a lender\'s formal application check, called a "hard inquiry."' },
    { question: 'What is considered a good credit score?', answer: 'Ranges vary by scoring model, but scores above roughly 700 (on a typical 300-850 scale) are generally considered good, with higher scores reflecting stronger creditworthiness.' },
  ],
  related: [
    { to: '/what-is-the-difference/refund-vs-rebate/', text: 'Refund vs. Rebate' },
    { to: '/what-is-the-difference/subscription-vs-membership/', text: 'Subscription vs. Membership' },
    { to: '/what-is-the-difference/salary-vs-wage/', text: 'Salary vs. Wage' },
  ],
};

const CreditScoreVsCreditReportPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default CreditScoreVsCreditReportPage;
