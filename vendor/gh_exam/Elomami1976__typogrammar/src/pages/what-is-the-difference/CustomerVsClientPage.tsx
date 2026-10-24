import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Customer vs. Client: What's the Difference? | TypoGrammar",
  metaDescription: "Customer vs client: a \"customer\" buys goods or products, often in a single or casual transaction; a \"client\" pays for professional services or advice, often in an ongoing relationship. See the rule, examples, and a quiz.",
  slug: 'customer-vs-client',
  h1: "Customer vs. Client: What's the Difference?",
  breadcrumbLabel: 'Customer vs. Client',
  datePublished: '2026-07-04',
  dateModified: '2026-07-04',
  quickAnswer: "A \"customer\" buys goods or products from a business, often in a one-time or casual transaction (a supermarket customer). A \"client\" pays for professional services or expert advice, usually within an ongoing relationship (a lawyer's client, a consulting firm's client). The distinction is about what is exchanged — products versus professional services — and how long the relationship lasts.",
  tableColumns: ['Customer', 'Client'],
  tableRows: [
    { feature: 'What is exchanged', values: ['Goods or products', 'Professional services or advice'] },
    { feature: 'Relationship length', values: ['Often one-time or casual', 'Often ongoing, more personal'] },
    { feature: 'Typical business', values: ['Shops, restaurants, supermarkets', 'Law firms, agencies, consultants, banks'] },
    { feature: 'Example', values: ['A customer buys groceries at the store.', 'A client hires a lawyer for legal advice.'] },
  ],
  terms: [
    {
      label: 'Customer',
      summary: 'A person who buys goods or products, typically in a retail or one-time transaction.',
      pattern: 'a/the + customer',
      examples: ['"The store thanked its loyal customers."', '"A customer complained about the price."', '"We have hundreds of customers every day."'],
    },
    {
      label: 'Client',
      summary: 'A person who receives professional services or expert advice, often over an ongoing relationship.',
      pattern: 'a/the + client',
      examples: ['"The lawyer met with a new client."', '"Our agency has clients all over the world."', '"The consultant tailors advice to each client."'],
    },
  ],
  grammarRule: 'Use "customer" for someone buying a product or a straightforward service at a shop, restaurant, or similar business. Use "client" for someone receiving professional, expert, or personalized services, typically from lawyers, accountants, consultants, agencies, or banks.',
  extraRule: 'Some professions use both words depending on their business model — for example, a bank might call everyday account holders "customers" but call people receiving investment advice "clients". Context and industry convention matter.',
  mistakes: [
    { incorrect: 'The lawyer has many customers who need legal advice.', correct: 'The lawyer has many clients who need legal advice.', note: 'A lawyer provides professional services, so it needs "clients", not "customers".' },
    { incorrect: 'The supermarket has thousands of clients every week.', correct: 'The supermarket has thousands of customers every week.', note: 'A supermarket sells products in casual transactions, so it needs "customers", not "clients".' },
    { incorrect: 'Our accounting firm serves customers with complex tax needs.', correct: 'Our accounting firm serves clients with complex tax needs.' },
  ],
  correctExamples: [
    'The restaurant tries to make every customer feel welcome.',
    'The consulting firm works closely with each client to solve their problems.',
    'A regular customer comes in for coffee every morning.',
    'The therapist has been seeing the same client for two years.',
    'The store offers discounts to returning customers.',
    'The advertising agency presented its new campaign to the client.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: "The bakery greeted every _____ with a smile."', answer: 'customer', explanation: 'A bakery sells products in casual transactions, so it needs "customer".' },
    { prompt: 'Choose the correct word: "The financial advisor reviewed her _____\'s investment portfolio."', answer: "client's", explanation: 'A financial advisor provides ongoing professional services, so it needs "client".' },
    { prompt: 'Fix the sentence: "The architect designed a custom home for his customer."', answer: 'The architect designed a custom home for his client.', explanation: 'An architect provides professional services, so it needs "client", not "customer".' },
  ],
  faqs: [
    { question: 'Can a business call the same person both a customer and a client?', answer: 'Yes, this can happen when a business offers both products and professional services — for example, a bank might refer to someone buying a simple product as a "customer" but refer to that same person as a "client" when discussing personalized wealth management.' },
    { question: 'Is "client" more formal or more prestigious than "customer"?', answer: 'It can feel that way in some industries, since "client" often implies a closer, advisory relationship, but the choice really depends on the nature of the business rather than one word being objectively better than the other.' },
    { question: 'What word is used for government or public services?', answer: 'Public sector organizations sometimes use other terms such as "citizen", "resident", or "service user" instead of "customer" or "client", though "customer" is increasingly used in customer-service contexts even in government agencies.' },
  ],
  related: [
    { to: '/what-is-the-difference/job-vs-work/', text: 'Job vs. Work' },
    { to: '/what-is-the-difference/custom-vs-habit/', text: 'Custom vs. Habit' },
    { to: '/what-is-the-difference/asylum-vs-refugee-status/', text: 'Asylum vs. Refugee Status' },
  ],
};

const CustomerVsClientPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default CustomerVsClientPage;
