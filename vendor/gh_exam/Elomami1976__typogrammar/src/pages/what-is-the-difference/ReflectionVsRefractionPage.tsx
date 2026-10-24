import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Reflection vs. Refraction: What's the Difference? | TypoGrammar",
  metaDescription: 'Reflection vs refraction: "reflection" is light bouncing off a surface, while "refraction" is light bending as it passes into a different medium. See the rule, examples, and a quiz.',
  slug: 'reflection-vs-refraction',
  h1: "Reflection vs. Refraction: What's the Difference?",
  breadcrumbLabel: 'Reflection vs. Refraction',
  datePublished: '2026-07-05',
  dateModified: '2026-07-05',
  quickAnswer: '"Reflection" occurs when light (or another wave) bounces off a surface and changes direction while staying in the same medium, like light bouncing off a mirror. "Refraction" occurs when light bends as it passes from one medium into another (such as from air into water), because its speed changes between the two materials.',
  tableColumns: ['Reflection', 'Refraction'],
  tableRows: [
    { feature: 'What happens', values: ['Light bounces off a surface', 'Light bends as it enters a new medium'] },
    { feature: 'Medium change', values: ['No — stays in the same medium', 'Yes — moves from one medium to another'] },
    { feature: 'Cause', values: ['The surface reflects the wave back', "A change in the wave's speed between media"] },
    { feature: 'Example', values: ['"You see your reflection in a mirror."', '"A straw looks bent in a glass of water due to refraction."'] },
  ],
  terms: [
    {
      label: 'Reflection',
      summary: 'The bouncing of light (or another wave) off a surface, staying within the same medium, producing images such as mirror reflections.',
      pattern: 'reflection (of + light/image)',
      examples: ['"The lake showed a clear reflection of the mountains."', '"Mirrors work through the reflection of light."'],
    },
    {
      label: 'Refraction',
      summary: 'The bending of light as it passes from one medium into another, caused by a change in the speed of the wave.',
      pattern: 'refraction (of + light)',
      examples: ['"Refraction causes a pencil to look bent in water."', '"Lenses use refraction to focus light."'],
    },
  ],
  grammarRule: 'Use "reflection" for light bouncing off a surface without changing medium, as with mirrors. Use "refraction" for light bending as it passes between different media, such as from air into water or glass, due to a change in speed.',
  extraRule: 'Both effects can happen at once — for example, at the surface of water, some light reflects back into the air while some light refracts and bends as it enters the water.',
  mistakes: [
    { incorrect: 'The straw appears bent in the glass of water due to reflection.', correct: 'The straw appears bent in the glass of water due to refraction.', note: 'Bending as light enters a new medium (water) is refraction.' },
    { incorrect: 'You see your image in the mirror because of refraction.', correct: 'You see your image in the mirror because of reflection.', note: 'Bouncing off a surface, like a mirror, is reflection.' },
    { incorrect: 'Refraction happens when light stays within the same medium and simply bounces back.', correct: 'Reflection happens when light stays within the same medium and simply bounces back.', note: 'Staying within the same medium describes reflection, not refraction.' },
  ],
  correctExamples: [
    'The calm lake produced a perfect reflection of the sunset.',
    "A prism uses refraction to split white light into a rainbow of colors.",
    'Sunglasses reduce glare caused by reflection off bright surfaces.',
    "A fish appears closer than it really is due to the water's refraction.",
    'The mirror\'s reflection showed the entire room behind her.',
    'Eyeglasses correct vision by refracting light before it reaches the eye.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: Light bouncing off a still lake to create a mirror-like image is called _____.', answer: 'reflection', explanation: 'Light bouncing off a surface, staying in the same medium, is reflection.' },
    { prompt: 'Choose the correct word: Light bending as it passes from air into a glass lens is called _____.', answer: 'refraction', explanation: 'Bending as light changes medium is refraction.' },
    { prompt: 'Fix the sentence: "A prism splits white light into colors through reflection."', answer: 'A prism splits white light into colors through refraction.', explanation: 'Bending light through a different medium (glass) is refraction.' },
  ],
  faqs: [
    { question: 'Can reflection and refraction happen at the same time?', answer: 'Yes — at the surface of water or glass, some light reflects back while some light refracts and continues into the new medium, both occurring simultaneously.' },
    { question: 'Why does a pencil look bent in a glass of water?', answer: 'The pencil appears bent because light refracts, or bends, as it passes from the water into the air, changing the angle at which it reaches your eyes.' },
    { question: 'Does sound also reflect and refract?', answer: 'Yes — sound waves can also reflect (as with echoes) and refract (as when sound bends passing through air of different temperatures), following similar wave principles as light.' },
  ],
  related: [
    { to: '/what-is-the-difference/virus-vs-viroid/', text: 'Virus vs. Viroid' },
    { to: '/what-is-the-difference/supernova-vs-kilonova/', text: 'Supernova vs. Kilonova' },
    { to: '/what-is-the-difference/iq-vs-intelligence/', text: 'IQ vs. Intelligence' },
  ],
};

const ReflectionVsRefractionPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default ReflectionVsRefractionPage;
