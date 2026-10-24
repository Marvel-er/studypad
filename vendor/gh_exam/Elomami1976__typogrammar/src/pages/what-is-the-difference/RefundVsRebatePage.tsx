import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Refund vs. Rebate: What's the Difference? | TypoGrammar",
  metaDescription: 'Refund vs rebate: a "refund" returns money after a return, cancellation, or billing error, while a "rebate" gives back part of a purchase price as a promotional incentive. See the rule, examples, and a quiz.',
  slug: 'refund-vs-rebate',
  h1: "Refund vs. Rebate: What's the Difference?",
  breadcrumbLabel: 'Refund vs. Rebate',
  datePublished: '2026-07-05',
  dateModified: '2026-07-05',
  quickAnswer: 'A "refund" is money returned to a customer, typically because a product was returned, canceled, or overcharged — restoring the original payment. A "rebate" is a partial amount of money given back to a customer after a purchase, often as a promotional incentive, usually requiring the customer to submit a claim or form after buying the product at full price.',
  tableColumns: ['Refund', 'Rebate'],
  tableRows: [
    { feature: 'When it happens', values: ['After a return, cancellation, or billing error', 'After a purchase, as a promotional incentive'] },
    { feature: 'Amount', values: ['Usually the full amount paid', 'Usually a partial amount'] },
    { feature: 'Action required', values: ['Often automatic once a return is processed', 'Usually requires submitting a claim or form'] },
    { feature: 'Example', values: ['"She got a refund after returning the faulty blender."', '"He received a $50 rebate after mailing in his receipt."'] },
  ],
  terms: [
    {
      label: 'Refund',
      summary: 'Money returned to a customer, typically restoring the original payment after a return, cancellation, or error.',
      pattern: 'a refund (for + item/service)',
      examples: ['"He requested a refund for the defective phone."', '"Her refund was processed within five business days."'],
    },
    {
      label: 'Rebate',
      summary: 'A partial amount given back after a purchase, often as a promotional incentive, usually requiring a claim process.',
      pattern: 'a rebate (on/for + product)',
      examples: ['"She submitted the paperwork to claim her rebate."', '"The rebate reduced the effective price by $50."'],
    },
  ],
  grammarRule: 'Use "refund" for money returned because of a return, cancellation, or billing mistake, typically restoring the full amount paid. Use "rebate" for a partial amount given back as a promotional incentive after a purchase, usually requiring the buyer to submit a claim.',
  extraRule: 'Rebates are often used by manufacturers to make a product appear cheaper at checkout while still charging the full price upfront, since many buyers never complete the rebate claim process.',
  mistakes: [
    { incorrect: 'She returned the broken laptop and received a rebate for the full purchase price.', correct: 'She returned the broken laptop and received a refund for the full purchase price.', note: 'Money returned for a faulty product return is a refund.' },
    { incorrect: 'He filled out a form and mailed in his receipt to claim his refund from the manufacturer.', correct: 'He filled out a form and mailed in his receipt to claim his rebate from the manufacturer.', note: 'A claim-based promotional payback is a rebate.' },
    { incorrect: 'A rebate is automatically processed as soon as a customer returns a faulty item.', correct: 'A refund is automatically processed as soon as a customer returns a faulty item.', note: 'Automatic processing after a return describes a refund.' },
  ],
  correctExamples: [
    'He received a full refund after canceling his hotel reservation.',
    'The store offered a $30 rebate on the printer after mailing in the form.',
    'Her refund appeared in her bank account within a week.',
    'Many customers forget to claim their mail-in rebate.',
    'The airline issued a refund after the flight was canceled.',
    'The rebate made the appliance cheaper than the sticker price suggested.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: After returning the defective item, she received her money back as a _____.', answer: 'refund', explanation: 'Money returned after a product return is a refund.' },
    { prompt: 'Choose the correct word: After buying the laptop, he mailed in a form and later received $40 back as a _____.', answer: 'rebate', explanation: 'A partial, claim-based payback after a purchase is a rebate.' },
    { prompt: 'Fix the sentence: "The store automatically issued a rebate the moment she returned the broken item."', answer: 'The store automatically issued a refund the moment she returned the broken item.', explanation: 'Automatic money-back after a return is a refund, not a rebate.' },
  ],
  faqs: [
    { question: 'Do all rebates require paperwork?', answer: 'Many rebates require submitting a claim, receipt, or form, though some retailers now offer "instant rebates" applied automatically at checkout.' },
    { question: 'Is a refund always for the full amount?', answer: 'Refunds are usually for the full amount paid, though partial refunds can occur in some cases, such as restocking fees or partial returns.' },
    { question: 'Can a rebate be given instantly at checkout?', answer: 'Yes — some rebates are applied immediately as a discount at the register, though traditional rebates require mailing in a claim after the purchase.' },
  ],
  related: [
    { to: '/what-is-the-difference/subscription-vs-membership/', text: 'Subscription vs. Membership' },
    { to: '/what-is-the-difference/credit-score-vs-credit-report/', text: 'Credit Score vs. Credit Report' },
    { to: '/what-is-the-difference/money-vs-currency/', text: 'Money vs. Currency' },
  ],
};

const RefundVsRebatePage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default RefundVsRebatePage;
