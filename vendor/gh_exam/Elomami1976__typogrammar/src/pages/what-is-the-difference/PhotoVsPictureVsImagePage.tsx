import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Photo vs. Picture vs. Image: What's the Difference? | TypoGrammar",
  metaDescription: '"Photo" is a camera-captured image, "picture" is the broad everyday word for any visual (photo, drawing, painting), and "image" is the most general or technical term. See the rule, examples, and a quiz.',
  slug: 'photo-vs-picture-vs-image',
  h1: "Photo vs. Picture vs. Image: What's the Difference?",
  breadcrumbLabel: 'Photo vs. Picture vs. Image',
  datePublished: '2026-07-05',
  dateModified: '2026-07-05',
  quickAnswer: '"Photo" (short for photograph) refers specifically to a picture captured with a camera. "Picture" is a broad, everyday word that can mean a photo, a drawing, a painting, or any visual representation. "Image" is the most general and often technical term, referring to any visual representation, including digital graphics and scans, and even abstract uses like a company\'s "public image."',
  tableColumns: ['Photo', 'Picture', 'Image'],
  tableRows: [
    { feature: 'Source', values: ['Camera only', 'Camera, drawing, painting, or any visual', 'Any visual representation, including digital/technical'] },
    { feature: 'Formality', values: ['Informal, everyday', 'Most informal, everyday', 'More formal or technical'] },
    { feature: 'Common use', values: ['"Take a photo."', '"Draw/take a picture."', '"Medical image", "brand image"'] },
    { feature: 'Can be abstract', values: ['No', 'Rarely ("mental picture")', 'Yes ("public image")'] },
  ],
  terms: [
    {
      label: 'Photo',
      summary: 'A picture captured specifically with a camera; short for "photograph."',
      pattern: 'a photo (of + subject)',
      examples: ['"She took a photo of the sunset."', '"He posted a photo from his trip."'],
    },
    {
      label: 'Picture',
      summary: 'A general, everyday word for any visual representation — a photo, drawing, painting, or illustration.',
      pattern: 'a picture (of + subject)',
      examples: ['"The child drew a picture of a house."', '"Can you take a picture of us?"'],
    },
    {
      label: 'Image',
      summary: 'The most general or technical term for any visual representation, including digital, scanned, medical, or abstract (non-physical) visuals.',
      pattern: 'an image (of/file)',
      examples: ['"The MRI image showed no damage."', '"The brand is rebuilding its public image."'],
    },
  ],
  grammarRule: 'Use "photo" only for something captured by a camera. Use "picture" as the everyday, general word that covers photos, drawings, and paintings alike. Use "image" as the most general or technical term, especially for digital, scanned, medical, or abstract visuals such as a company\'s "public image."',
  extraRule: '"Picture" can also be used figuratively ("get the picture" meaning "understand"), and "image" can mean reputation or mental impression ("protect its public image"), while "photo" is never used figuratively.',
  mistakes: [
    { incorrect: 'She drew a beautiful photo of the mountains.', correct: 'She drew a beautiful picture of the mountains.', note: 'A drawing is not captured by a camera, so it cannot be called a photo.' },
    { incorrect: "The doctor reviewed the patient's photo to check the fracture.", correct: "The doctor reviewed the patient's image (X-ray) to check the fracture.", note: 'Medical scans are called images, a more technical term than photo or picture.' },
    { incorrect: 'The company is worried about its public photo.', correct: 'The company is worried about its public image.', note: 'A reputation is described as an "image," an abstract use that "photo" cannot take.' },
  ],
  correctExamples: [
    'He took a photo of the mountains with his new camera.',
    'The children painted a picture of their family.',
    'The satellite image showed the storm forming over the ocean.',
    'She framed her favorite picture from the wedding.',
    'The clinic keeps digital images of every X-ray on file.',
    'Can you send me that photo from last night?',
  ],
  quiz: [
    { prompt: 'Choose the correct word: He used his phone to take a _____ of the birthday cake.', answer: 'photo', explanation: 'Something captured with a camera is a photo.' },
    { prompt: 'Choose the correct word: The artist finished a _____ of the countryside using watercolors.', answer: 'picture', explanation: 'A painting is a type of picture, the broad everyday term.' },
    { prompt: 'Fix the sentence: "The hospital stores every patient\'s scan as a digital photo."', answer: "The hospital stores every patient's scan as a digital image.", explanation: 'Medical scans are technical visuals, so "image" is the more accurate word.' },
  ],
  faqs: [
    { question: 'Can "picture" mean photo?', answer: 'Yes — in everyday speech, "picture" is often used loosely to mean a photo, as in "take a picture," even though it technically covers drawings and paintings too.' },
    { question: 'Is "image" only used for digital visuals?', answer: 'No, though it is common in digital and technical contexts, "image" is the broadest term and can describe any visual representation, physical or digital, as well as abstract ideas like reputation.' },
    { question: 'Why do we say "self-image" and not "self-photo"?', answer: '"Image" extends naturally to abstract meanings like a person\'s reputation or the way they see themselves, a figurative use that "photo" does not have.' },
  ],
  related: [
    { to: '/what-is-the-difference/vlog-vs-blog/', text: 'Vlog vs. Blog' },
    { to: '/what-is-the-difference/money-vs-currency/', text: 'Money vs. Currency' },
    { to: '/what-is-the-difference/hotel-vs-motel/', text: 'Hotel vs. Motel' },
  ],
};

const PhotoVsPictureVsImagePage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default PhotoVsPictureVsImagePage;
