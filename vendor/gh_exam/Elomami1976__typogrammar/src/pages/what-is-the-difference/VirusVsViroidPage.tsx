import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Virus vs. Viroid: What's the Difference? | TypoGrammar",
  metaDescription: 'Virus vs viroid: a "virus" has genetic material inside a protein coat and infects many kinds of organisms, while a "viroid" is a protein-free strand of RNA known to infect only plants. See the rule, examples, and a quiz.',
  slug: 'virus-vs-viroid',
  h1: "Virus vs. Viroid: What's the Difference?",
  breadcrumbLabel: 'Virus vs. Viroid',
  datePublished: '2026-07-05',
  dateModified: '2026-07-05',
  quickAnswer: 'A "virus" is a microscopic infectious agent made of genetic material (DNA or RNA) enclosed in a protein coat, which needs a host cell to reproduce and can infect animals, plants, and other organisms. A "viroid" is an even smaller, simpler infectious agent made only of a short strand of RNA, with no protein coat at all, and is known to infect only plants.',
  tableColumns: ['Virus', 'Viroid'],
  tableRows: [
    { feature: 'Structure', values: ['Genetic material (DNA or RNA) inside a protein coat', 'A short strand of RNA only, no protein coat'] },
    { feature: 'Size', values: ['Larger (though still microscopic)', 'Much smaller than viruses'] },
    { feature: 'Hosts infected', values: ['Animals, plants, bacteria, fungi, and more', 'Plants only (currently known)'] },
    { feature: 'Example', values: ['"The flu is caused by a virus."', '"Potato spindle tuber viroid damages potato crops."'] },
  ],
  terms: [
    {
      label: 'Virus',
      summary: 'A microscopic infectious agent consisting of genetic material enclosed in a protein coat, requiring a host cell to reproduce.',
      pattern: 'a virus (that causes + disease)',
      examples: ['"The common cold is caused by a virus."', '"Viruses cannot reproduce without a host cell."'],
    },
    {
      label: 'Viroid',
      summary: 'An extremely small infectious agent made of a short RNA strand with no protein coat, known to infect only plants.',
      pattern: 'a viroid (that infects + plant)',
      examples: ['"The viroid spread through the tomato crop."', '"Viroids lack the protein coat found in viruses."'],
    },
  ],
  grammarRule: 'Use "virus" for infectious agents with genetic material enclosed in a protein coat, capable of infecting a wide range of hosts, including animals and plants. Use "viroid" specifically for the simpler, protein-free RNA agents currently known only to infect plants.',
  extraRule: 'Because viroids lack a protein coat, they were only discovered decades after viruses, once scientists had tools sensitive enough to detect infectious agents made of RNA alone.',
  mistakes: [
    { incorrect: 'The flu is caused by a viroid that infects the human respiratory system.', correct: 'The flu is caused by a virus that infects the human respiratory system.', note: 'Human diseases like the flu are caused by viruses, not viroids.' },
    { incorrect: 'Viroids have a protein coat surrounding their genetic material.', correct: 'Viroids have no protein coat; only a short strand of RNA.', note: 'Lacking a protein coat is a defining feature of viroids.' },
    { incorrect: 'Viruses are currently known to infect only plant species.', correct: 'Viroids are currently known to infect only plant species; viruses can infect animals, plants, and more.', note: 'Plant-only infection currently describes viroids, not viruses.' },
  ],
  correctExamples: [
    'Scientists study how viruses invade and hijack host cells.',
    'A viroid damaged an entire field of potato plants.',
    'Vaccines help the immune system fight off specific viruses.',
    'Viroids are among the smallest known infectious agents.',
    'The virus mutated slightly as it spread between hosts.',
    'Researchers first identified viroids decades after they discovered viruses.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: An infectious agent with genetic material wrapped in a protein coat is a _____.', answer: 'virus', explanation: 'Having a protein coat is a defining feature of a virus.' },
    { prompt: 'Choose the correct word: A tiny infectious RNA strand with no protein coat, known to infect only plants, is a _____.', answer: 'viroid', explanation: 'Lacking a protein coat and infecting only plants describes a viroid.' },
    { prompt: 'Fix the sentence: "The viroid causing the flu spread quickly through the office."', answer: 'The virus causing the flu spread quickly through the office.', explanation: 'The flu is caused by a virus, not a viroid.' },
  ],
  faqs: [
    { question: 'Are viroids alive?', answer: 'Like viruses, viroids are generally not considered fully "alive" by most biological definitions, since they cannot reproduce without a host cell and lack many features of living organisms.' },
    { question: 'Can viroids infect humans?', answer: 'No — viroids are currently known to infect only plants, unlike viruses, which can infect a much wider range of hosts, including humans, other animals, and plants.' },
    { question: 'Which was discovered first, viruses or viroids?', answer: 'Viruses were discovered first, in the late 19th century, while viroids were not identified until the 1970s, once scientists had the tools to detect infectious agents made only of RNA.' },
  ],
  related: [
    { to: '/what-is-the-difference/reflection-vs-refraction/', text: 'Reflection vs. Refraction' },
    { to: '/what-is-the-difference/supernova-vs-kilonova/', text: 'Supernova vs. Kilonova' },
    { to: '/what-is-the-difference/iq-vs-intelligence/', text: 'IQ vs. Intelligence' },
  ],
};

const VirusVsViroidPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default VirusVsViroidPage;
