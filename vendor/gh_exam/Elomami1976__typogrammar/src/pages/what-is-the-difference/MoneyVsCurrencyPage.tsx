import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Money vs. Currency: What's the Difference? | TypoGrammar",
  metaDescription: 'Money vs currency: "money" is the general concept of anything used as payment, while "currency" refers specifically to a country\'s official monetary system, like the dollar or euro. See the rule, examples, and a quiz.',
  slug: 'money-vs-currency',
  h1: "Money vs. Currency: What's the Difference?",
  breadcrumbLabel: 'Money vs. Currency',
  datePublished: '2026-07-05',
  dateModified: '2026-07-05',
  quickAnswer: '"Money" is the general concept of anything widely accepted as payment for goods and services — cash, coins, digital balances, and more. "Currency" refers specifically to the physical or official monetary system issued by a country (the US dollar, the euro, the yen) — one particular form or unit that money can take.',
  tableColumns: ['Money', 'Currency'],
  tableRows: [
    { feature: 'Scope', values: ['General concept of payment/wealth', 'A specific national monetary system/unit'] },
    { feature: 'Examples', values: ['Cash, coins, bank balances, cryptocurrency', 'US dollar, euro, yen, pound'] },
    { feature: 'Countable', values: ['Uncountable ("money", not "moneys")', 'Countable when comparing systems ("several currencies")'] },
    { feature: 'Typical use', values: ['"I don\'t have enough money."', '"The currency of Japan is the yen."'] },
  ],
  terms: [
    {
      label: 'Money',
      summary: 'The general, uncountable concept of wealth or any accepted means of payment, in any form.',
      pattern: 'money (uncountable)',
      examples: ['"He saved a lot of money this year."', '"She doesn\'t carry much cash, but she has money in the bank."'],
    },
    {
      label: 'Currency',
      summary: "A country's specific official unit or system of money, used when naming or comparing different national monetary systems.",
      pattern: 'a/the currency (of + country)',
      examples: ['"The currency of the UK is the pound."', '"They exchanged their currency at the airport."'],
    },
  ],
  grammarRule: "Use \"money\" as the general, uncountable term for wealth or a means of payment in any form. Use \"currency\" specifically when referring to a country's official unit of money or when comparing different national monetary systems.",
  extraRule: "All currency is money, but not all money refers to a single currency — a savings account, for example, holds money that happens to be denominated in one specific currency, like US dollars.",
  mistakes: [
    { incorrect: 'The currency he has left is twenty dollars in cash.', correct: 'The money he has left is twenty dollars in cash.', note: 'A general amount of cash on hand is described as money.' },
    { incorrect: "Japan's official money is the yen.", correct: "Japan's official currency is the yen.", note: 'A specific national unit like the yen is called a currency.' },
    { incorrect: "She doesn't have enough currency to pay the rent.", correct: "She doesn't have enough money to pay the rent.", note: 'A general shortage of funds is described using "money," not "currency."' },
  ],
  correctExamples: [
    'He exchanged his currency for euros before the trip.',
    "She doesn't have enough money to buy a new car yet.",
    'Several countries in Europe share the same currency, the euro.',
    'They keep most of their money in a savings account.',
    'The traveler compared exchange rates for the local currency.',
    'Cryptocurrency is a newer, digital form of money.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: Before flying to France, he exchanged his dollars for the local _____.', answer: 'currency', explanation: 'A specific national monetary unit is a currency.' },
    { prompt: 'Choose the correct word: She saved enough _____ over the year to buy a laptop.', answer: 'money', explanation: 'A general amount of savings is described as money.' },
    { prompt: 'Fix the sentence: "Canada\'s official money is the Canadian dollar."', answer: "Canada's official currency is the Canadian dollar.", explanation: 'The specific national unit is called a currency.' },
  ],
  faqs: [
    { question: 'Is cryptocurrency a currency or money?', answer: 'Cryptocurrency is often described as a form of digital money, and in some cases functions like a currency, though whether it counts as "official" currency depends on whether a government recognizes and issues it.' },
    { question: 'Can a country have more than one official currency?', answer: 'Yes — some countries officially accept more than one currency for transactions, though most have a single primary national currency.' },
    { question: 'Why do exchange rates apply to currency, not money in general?', answer: 'Exchange rates compare the value of one specific national currency to another, so the term "currency" is used rather than the broader, more general word "money."' },
  ],
  related: [
    { to: '/what-is-the-difference/salary-vs-wage/', text: 'Salary vs. Wage' },
    { to: '/what-is-the-difference/founder-vs-ceo/', text: 'Founder vs. CEO' },
    { to: '/what-is-the-difference/hotel-vs-motel/', text: 'Hotel vs. Motel' },
  ],
};

const MoneyVsCurrencyPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default MoneyVsCurrencyPage;
