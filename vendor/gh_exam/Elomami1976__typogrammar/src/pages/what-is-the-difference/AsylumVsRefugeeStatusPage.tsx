import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Asylum vs. Refugee Status: What's the Difference? | TypoGrammar",
  metaDescription: "Asylum vs refugee status: \"asylum\" is protection requested from within or at the border of the country of destination; \"refugee status\" is usually determined before entry, often abroad through the UNHCR. Vocabulary explanation with examples and a quiz.",
  slug: 'asylum-vs-refugee-status',
  h1: "Asylum vs. Refugee Status: What's the Difference?",
  breadcrumbLabel: 'Asylum vs. Refugee Status',
  datePublished: '2026-07-04',
  dateModified: '2026-07-04',
  quickAnswer: "\"Asylum\" is protection a person requests after they have already arrived in, or are at the border of, the country where they want to stay (he applied for asylum after landing). \"Refugee status\" is a recognized legal status usually determined before someone enters their destination country, often while they are still abroad, sometimes through a UNHCR resettlement process. Both protect people fleeing danger, but they differ in where and when the claim is made. This page explains the vocabulary; it is not legal advice.",
  tableColumns: ['Asylum', 'Refugee status'],
  tableRows: [
    { feature: 'Where the claim is made', values: ['Within or at the border of the destination country', 'Often outside the destination country, before travel'] },
    { feature: 'Who applies', values: ['An "asylum seeker"', 'A person recognized and resettled as a "refugee"'] },
    { feature: 'Common verb', values: ['to seek/claim/apply for asylum', 'to be granted/recognized as having refugee status'] },
    { feature: 'Example', values: ['She applied for asylum at the airport.', 'He was granted refugee status before being resettled.'] },
  ],
  terms: [
    {
      label: 'Asylum',
      summary: 'Protection requested by someone already in, or at the border of, the country where they hope to stay.',
      pattern: 'seek/apply for/claim + asylum',
      examples: ['"She sought asylum as soon as she crossed the border."', '"His asylum application is still being processed."', '"They were granted asylum after a lengthy hearing."'],
    },
    {
      label: 'Refugee status',
      summary: 'A recognized legal status, often determined before entering the destination country, sometimes through international resettlement.',
      pattern: 'be granted/recognized as having + refugee status',
      examples: ['"He was granted refugee status by the UNHCR."', '"Refugee status gives certain legal protections."', '"Her refugee status was confirmed before she was resettled."'],
    },
  ],
  grammarRule: '"Asylum" is typically requested from within, or at the border of, the country a person wants to stay in — the process happens on the territory of the destination country. "Refugee status" is a formal recognition that a person meets the international definition of a refugee, and it is often determined before entry, sometimes abroad through organizations like the UNHCR, as part of a resettlement process.',
  extraRule: 'This page explains common English vocabulary used in the news and IELTS/TOEFL-style topics about migration. It is a general language guide, not legal or immigration advice — always consult official government or UNHCR sources for legal definitions in a specific country.',
  mistakes: [
    { incorrect: 'He applied for refugee status at the airport when he arrived, requesting to stay in the country.', correct: 'He applied for asylum at the airport when he arrived, requesting to stay in the country.', note: 'A claim made after arriving at the destination is normally described as "asylum", not "refugee status".' },
    { incorrect: 'She was granted asylum by the UNHCR while still living in a refugee camp abroad, before being resettled.', correct: 'She was granted refugee status by the UNHCR while still living in a refugee camp abroad, before being resettled.', note: 'A status determined abroad before resettlement is usually "refugee status", not "asylum".' },
    { incorrect: 'The country accepted thousands of asylums last year.', correct: 'The country accepted thousands of asylum seekers last year.', note: '"Asylum" itself is uncountable; the people are called "asylum seekers", not "asylums".' },
  ],
  correctExamples: [
    'Thousands of people apply for asylum in the country every year.',
    'The organization helps refugees who have already been granted refugee status find housing.',
    'Her asylum claim was approved after a long legal process.',
    'Refugee status can allow a person to be resettled in a new country with international protection.',
    'He is an asylum seeker waiting for a decision on his case.',
    'The agency assists refugees during the resettlement process after refugee status is confirmed.',
  ],
  quiz: [
    { prompt: 'Choose the correct term: "After crossing the border on foot, she immediately requested _____ from local officials."', answer: 'asylum', explanation: 'A claim made after arriving at the border/destination is typically called "asylum".' },
    { prompt: 'Choose the correct term: "While still in a camp in a neighboring country, his application for _____ was approved by the UNHCR."', answer: 'refugee status', explanation: 'A status determined abroad before resettlement is typically called "refugee status".' },
    { prompt: 'Fix the sentence: "People who ask for protection after arriving in a country are called refugee status holders."', answer: 'People who ask for protection after arriving in a country are called asylum seekers.', explanation: 'People requesting protection after arrival are called "asylum seekers", not "refugee status holders".' },
  ],
  faqs: [
    { question: 'Is an asylum seeker the same as a refugee?', answer: 'Not exactly. An "asylum seeker" is someone who has applied for protection but whose claim has not yet been decided. If their claim is approved, they may then be legally recognized as a "refugee". The words describe different stages of the same general situation.' },
    { question: 'Does this page give legal advice about immigration law?', answer: 'No. This page explains general English vocabulary often seen in news articles and essay topics about migration. Immigration and asylum law vary by country and change over time, so always check official government or UNHCR sources for accurate legal information.' },
    { question: 'Why do these words often appear together in IELTS/TOEFL essay topics?', answer: 'Migration, asylum, and refugees are common Writing Task 2 and TOEFL independent essay themes, so knowing the precise vocabulary — rather than using the words interchangeably — helps demonstrate stronger lexical resource and topic knowledge in exam writing.' },
  ],
  related: [
    { to: '/what-is-the-difference/customer-vs-client/', text: 'Customer vs. Client' },
    { to: '/what-is-the-difference/house-vs-home/', text: 'House vs. Home' },
    { to: '/what-is-the-difference/custom-vs-habit/', text: 'Custom vs. Habit' },
  ],
};

const AsylumVsRefugeeStatusPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default AsylumVsRefugeeStatusPage;
