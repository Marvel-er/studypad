import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Supernova vs. Kilonova: What's the Difference? | TypoGrammar",
  metaDescription: 'Supernova vs kilonova: a "supernova" is the explosive death of a massive star, while a "kilonova" is caused by the merger of two neutron stars and produces heavy elements like gold. See the rule, examples, and a quiz.',
  slug: 'supernova-vs-kilonova',
  h1: "Supernova vs. Kilonova: What's the Difference?",
  breadcrumbLabel: 'Supernova vs. Kilonova',
  datePublished: '2026-07-05',
  dateModified: '2026-07-05',
  quickAnswer: 'A "supernova" is the explosive death of a massive star, occurring when it runs out of nuclear fuel and collapses, releasing an enormous burst of light and energy. A "kilonova" is a different, generally fainter explosion caused by the merger of two extremely dense objects, such as two neutron stars or a neutron star and a black hole, which produces many of the universe\'s heaviest elements, like gold and platinum.',
  tableColumns: ['Supernova', 'Kilonova'],
  tableRows: [
    { feature: 'Cause', values: ['A massive star running out of fuel and collapsing', 'The merger of two neutron stars (or a neutron star and black hole)'] },
    { feature: 'Brightness', values: ['Extremely bright, among the brightest events in the universe', 'Fainter than a supernova, though still very powerful'] },
    { feature: 'Elements produced', values: ['Many elements up to iron, plus some heavier elements', 'Very heavy elements, such as gold and platinum, in large quantities'] },
    { feature: 'Example', values: ['"A supernova can outshine an entire galaxy briefly."', '"The 2017 neutron star merger produced a detected kilonova."'] },
  ],
  terms: [
    {
      label: 'Supernova',
      summary: 'The explosive death of a massive star, occurring after it exhausts its nuclear fuel and collapses, releasing intense light and energy.',
      pattern: 'a supernova (of/in + galaxy)',
      examples: ['"Astronomers observed a supernova in a distant galaxy."', '"A supernova can briefly outshine its entire galaxy."'],
    },
    {
      label: 'Kilonova',
      summary: 'An explosion caused by the merger of two ultra-dense objects, such as neutron stars, producing heavy elements like gold and platinum.',
      pattern: 'a kilonova (from + merger)',
      examples: ['"The kilonova was detected through gravitational waves and light."', '"Kilonovas help explain the origin of heavy elements like gold."'],
    },
  ],
  grammarRule: 'Use "supernova" for the explosive death of a massive star. Use "kilonova" specifically for the explosion caused by the merger of two extremely dense stellar remnants, such as neutron stars, which is a distinct astronomical event from a supernova.',
  extraRule: 'Kilonovas were confirmed observationally more recently than supernovas, notably in 2017, when a neutron star merger was detected in both gravitational waves and light, confirming decades of theoretical prediction.',
  mistakes: [
    { incorrect: 'A kilonova occurs when a massive star runs out of fuel and collapses.', correct: 'A supernova occurs when a massive star runs out of fuel and collapses.', note: 'A collapsing, fuel-exhausted star produces a supernova, not a kilonova.' },
    { incorrect: 'Supernovas are caused by the merger of two neutron stars.', correct: 'Kilonovas are caused by the merger of two neutron stars.', note: 'A neutron star merger produces a kilonova.' },
    { incorrect: 'Kilonovas are typically brighter than supernovas.', correct: 'Kilonovas are typically fainter than supernovas.', note: 'Supernovas are generally the brighter of the two events.' },
  ],
  correctExamples: [
    'The supernova was visible in the night sky for several weeks.',
    'Scientists detected a kilonova following the collision of two neutron stars.',
    'A supernova can leave behind a neutron star or black hole.',
    'The 2017 kilonova confirmed that neutron star mergers produce heavy elements.',
    'Ancient supernovas seeded the universe with elements up to iron.',
    'Astronomers used telescopes and gravitational wave detectors to study the kilonova.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: The explosive collapse of a massive star running out of fuel is called a _____.', answer: 'supernova', explanation: 'A collapsing massive star produces a supernova.' },
    { prompt: 'Choose the correct word: The explosion from two colliding neutron stars, producing gold and platinum, is called a _____.', answer: 'kilonova', explanation: 'A neutron star merger produces a kilonova.' },
    { prompt: 'Fix the sentence: "The supernova in 2017 was detected through gravitational waves from a neutron star merger."', answer: 'The kilonova in 2017 was detected through gravitational waves from a neutron star merger.', explanation: 'The 2017 neutron star merger event was a kilonova, not a supernova.' },
  ],
  faqs: [
    { question: 'Which produces more heavy elements, a supernova or a kilonova?', answer: 'Kilonovas are thought to produce a larger share of the universe\'s heaviest elements, such as gold and platinum, compared to supernovas, which mainly produce elements up to iron and some heavier elements.' },
    { question: 'Was a kilonova ever directly observed?', answer: 'Yes — in 2017, astronomers directly observed a kilonova resulting from a neutron star merger, detecting it through both gravitational waves and light across the electromagnetic spectrum.' },
    { question: 'Can a supernova lead to a kilonova later?', answer: 'Indirectly, yes — a supernova can leave behind a neutron star, and if that neutron star eventually merges with another dense object, the resulting explosion would be a kilonova, though this process can take a very long time.' },
  ],
  related: [
    { to: '/what-is-the-difference/virus-vs-viroid/', text: 'Virus vs. Viroid' },
    { to: '/what-is-the-difference/reflection-vs-refraction/', text: 'Reflection vs. Refraction' },
    { to: '/what-is-the-difference/iq-vs-intelligence/', text: 'IQ vs. Intelligence' },
  ],
};

const SupernovaVsKilonovaPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default SupernovaVsKilonovaPage;
