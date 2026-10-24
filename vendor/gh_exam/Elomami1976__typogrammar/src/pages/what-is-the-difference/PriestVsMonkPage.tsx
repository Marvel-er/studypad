import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Priest vs. Monk: What's the Difference? | TypoGrammar",
  metaDescription: 'Priest vs monk: a "priest" is ordained to lead worship and perform sacraments for a congregation, while a "monk" lives a communal, prayer-focused life in a monastery. See the rule, examples, and a quiz.',
  slug: 'priest-vs-monk',
  h1: "Priest vs. Monk: What's the Difference?",
  breadcrumbLabel: 'Priest vs. Monk',
  datePublished: '2026-07-05',
  dateModified: '2026-07-05',
  quickAnswer: 'A "priest" is a religious leader ordained to perform sacraments and lead worship services, often serving a congregation in a parish or church. A "monk" is a man who has taken vows to live a communal, often secluded religious life dedicated to prayer and work, typically within a monastery, and is not necessarily ordained to perform sacraments.',
  tableColumns: ['Priest', 'Monk'],
  tableRows: [
    { feature: 'Main role', values: ['Leads worship, performs sacraments', 'Lives a life of prayer and work in community'] },
    { feature: 'Typical setting', values: ['Parish or church, serving a congregation', 'Monastery, often withdrawn from public life'] },
    { feature: 'Ordained', values: ['Yes, ordained to perform sacraments', 'Not necessarily ordained'] },
    { feature: 'Vows', values: ['Vows tied to priesthood duties', 'Vows of poverty, chastity, obedience'] },
  ],
  terms: [
    {
      label: 'Priest',
      summary: 'An ordained religious leader authorized to lead worship and administer sacraments, usually serving a specific congregation.',
      pattern: 'a/the priest (of/at + church)',
      examples: ['"The priest baptized the newborn baby."', '"She spoke with the parish priest after the service."'],
    },
    {
      label: 'Monk',
      summary: 'A man devoted to a religious life within a monastic community, focused on prayer, work, and simplicity, often withdrawn from public life.',
      pattern: 'a monk (at + monastery)',
      examples: ['"The monks rose before dawn for morning prayers."', '"He became a monk after leaving his career."'],
    },
  ],
  grammarRule: 'Use "priest" for an ordained leader who performs sacraments and serves a congregation, and "monk" for someone living a communal, often secluded religious life dedicated to prayer within a monastery. Some monks are also ordained priests, but many are not.',
  extraRule: 'In some traditions, a monk who is also ordained is called a "priest-monk" or "hieromonk," showing the two roles can combine, though they remain distinct by default.',
  mistakes: [
    { incorrect: 'The monk performed the wedding ceremony at the local parish.', correct: 'The priest performed the wedding ceremony at the local parish.', note: 'Performing sacraments for a congregation is the role of a priest.' },
    { incorrect: 'Every priest lives a secluded life in a monastery.', correct: 'Every monk lives a secluded life in a monastery, but priests usually serve public congregations.', note: 'Monastic seclusion describes monks, not priests in general.' },
    { incorrect: 'All monks are ordained to administer sacraments.', correct: 'Not all monks are ordained to administer sacraments; some are, but many are not.', note: 'Ordination is not automatic for monks.' },
  ],
  correctExamples: [
    'The priest led Sunday Mass at the parish church.',
    'The monks spent their day in silent prayer and manual labor.',
    'She asked the priest to bless her new home.',
    'He joined a monastery and became a monk in his thirties.',
    "The priest's sermon focused on forgiveness.",
    'The monks followed a strict daily schedule of prayer and work.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: The person who baptizes babies and leads the Sunday service is the _____.', answer: 'priest', explanation: 'Leading worship and performing sacraments is the role of a priest.' },
    { prompt: 'Choose the correct word: The man who lives in a monastery devoted to prayer and simple work is a _____.', answer: 'monk', explanation: 'A communal, prayer-focused life in a monastery describes a monk.' },
    { prompt: 'Fix the sentence: "All monks are ordained and serve a public congregation every Sunday."', answer: 'Not all monks are ordained, and most do not serve a public congregation the way priests do.', explanation: 'Monks are not automatically ordained, and typically live apart from public congregations.' },
  ],
  faqs: [
    { question: 'Can a monk become a priest?', answer: 'Yes — in some traditions, a monk can also be ordained as a priest, sometimes called a "hieromonk," combining monastic life with the ability to perform sacraments.' },
    { question: 'Do all religions have monks?', answer: 'Monastic traditions exist in several religions, including Christianity and Buddhism, though the specific practices, vows, and roles vary between traditions.' },
    { question: 'What is the difference between a monk and a nun?', answer: 'A monk is a man living a monastic religious life, while a nun is a woman doing so — both typically take similar vows of poverty, chastity, and obedience within their communities.' },
  ],
  related: [
    { to: '/what-is-the-difference/church-vs-cathedral/', text: 'Church vs. Cathedral' },
    { to: '/what-is-the-difference/imam-vs-sheikh/', text: 'Imam vs. Sheikh' },
    { to: '/what-is-the-difference/theism-vs-deism/', text: 'Theism vs. Deism' },
  ],
};

const PriestVsMonkPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default PriestVsMonkPage;
