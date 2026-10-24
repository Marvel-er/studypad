import React from 'react';
import { Link } from 'react-router-dom';
import usePageMetadata from '../hooks/usePageMetadata';
import { ArticleParagraph, ArticleHeading, BulletList } from '../components/ArticleComponents';
import SchemaMarkup from '../components/SchemaMarkup';
import RelatedContent from '../components/RelatedContent';

const educationTopics = [
  'Should university education be free for everyone?',
  'Do students learn better in online classes or traditional classrooms?',
  'Should schools focus more on practical skills than academic subjects?',
  'Is it better to specialize early or study a broad range of subjects?',
  'Should homework be abolished in primary schools?',
  'Should foreign languages be compulsory in schools?',
  'Do exams accurately measure a student\'s ability?',
  'Should students evaluate their teachers\' performance?',
  'Is studying abroad more beneficial than studying at home?',
  'Should gap years be encouraged before university?',
];

const technologyTopics = [
  'Has the internet made people more or less connected?',
  'Should children have limited access to smartphones and tablets?',
  'Will artificial intelligence create more jobs than it destroys?',
  'Do social media platforms do more harm than good?',
  'Should governments regulate how tech companies collect personal data?',
  'Is online shopping better than shopping in physical stores?',
  'Will robots replace most human jobs in the future?',
  'Should schools rely more on technology for teaching?',
  'Is society becoming too dependent on technology?',
  'Should there be an age limit for using social media?',
];

const environmentTopics = [
  'Should governments impose stricter laws on companies that pollute?',
  'Is individual action or government policy more important for climate change?',
  'Should single-use plastics be banned worldwide?',
  'Is nuclear energy a good solution to reduce carbon emissions?',
  'Should countries be fined for failing to meet climate targets?',
  'Do zoos help or harm wildlife conservation?',
  'Should there be limits on the number of cars allowed in cities?',
  'Is recycling enough to solve the world\'s waste problem?',
  'Should meat consumption be reduced to protect the environment?',
  'Are electric vehicles the best solution for reducing pollution?',
];

const societyTopics = [
  'Is the gap between rich and poor a serious problem in modern society?',
  'Should governments provide a universal basic income?',
  'Are people today less connected to their communities than in the past?',
  'Should the retirement age be increased as life expectancy rises?',
  'Is crime better prevented through punishment or rehabilitation?',
  'Should the media be more strictly regulated?',
  'Are celebrities a bad influence on young people?',
  'Should voting be compulsory for all citizens?',
  'Is gender equality fully achieved in most societies today?',
  'Should governments do more to support struggling families?',
];

const workTopics = [
  'Is job satisfaction more important than a high salary?',
  'Should companies allow employees to work from home permanently?',
  'Is a four-day work week better for employees and businesses?',
  'Should retirement be mandatory at a certain age?',
  'Are large corporations better employers than small businesses?',
  'Should students choose a career based on passion or salary potential?',
  'Is unpaid overtime acceptable in modern workplaces?',
  'Should companies be required to hire a diverse workforce?',
  'Is it better to change careers frequently or stay in one field?',
  'Should employees be paid based on performance rather than hours worked?',
];

const healthTopics = [
  'Should governments tax unhealthy food and drinks?',
  'Is mental health as important as physical health in healthcare systems?',
  'Should healthcare be free for everyone, funded by taxes?',
  'Is fast food responsible for the rise in obesity rates?',
  'Should exercise be a compulsory part of the school curriculum?',
  'Is alternative medicine as effective as conventional medicine?',
  'Should smoking be banned in all public places?',
  'Is social media harming young people\'s mental health?',
  'Should governments run public health awareness campaigns?',
  'Is preventative healthcare more important than treatment?',
];

const TopicList = ({ topics, startNumber }: { topics: string[]; startNumber: number }) => (
  <ol className="list-decimal list-inside space-y-3 mb-6" start={startNumber}>
    {topics.map((topic, index) => (
      <li key={index} className="text-slate-700 dark:text-slate-300 pl-2">
        {topic}
      </li>
    ))}
  </ol>
);

const IELTSEssayTopicsPage: React.FC = () => {
  usePageMetadata({
    title: 'IELTS Essay Topics 2026: 60+ Writing Task 2 Prompts (Free PDF) | TypoGrammar',
    description: 'Free PDF: 60+ IELTS essay topics for Writing Task 2 covering education, technology, environment, society, work, and health - with a random generator to practice.',
    canonical: 'https://typogrammar.com/ielts/ielts-essay-topics/',
  });

  const itemListSchema = {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name: 'IELTS Essay Topics 2026',
    description: '60+ IELTS Writing Task 2 essay topics and prompts for practice.',
    numberOfItems: 60,
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Education Topics' },
      { '@type': 'ListItem', position: 2, name: 'Technology Topics' },
      { '@type': 'ListItem', position: 3, name: 'Environment Topics' },
      { '@type': 'ListItem', position: 4, name: 'Society Topics' },
      { '@type': 'ListItem', position: 5, name: 'Work Topics' },
      { '@type': 'ListItem', position: 6, name: 'Health Topics' },
    ],
  };

  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: [
      {
        '@type': 'Question',
        name: 'What are common IELTS essay topics?',
        acceptedAnswer: { '@type': 'Answer', text: 'IELTS Writing Task 2 essay topics usually fall into categories like education, technology, environment, society, work, and health. Prompts ask you to agree/disagree, discuss both views, or give an opinion on an issue.' },
      },
      {
        '@type': 'Question',
        name: 'How many essay topics should I practice for IELTS?',
        acceptedAnswer: { '@type': 'Answer', text: 'Practicing at least 15-20 topics across different categories is a good starting point. Focus on the categories you find hardest and time yourself at 40 minutes per essay.' },
      },
      {
        '@type': 'Question',
        name: 'Where can I get random IELTS essay topics to practice?',
        acceptedAnswer: { '@type': 'Answer', text: 'Use the topics on this page, or try the free random essay topic generator for an unlimited supply of practice prompts.' },
      },
    ],
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <SchemaMarkup
        type="Article"
        data={{
          headline: 'IELTS Essay Topics 2026: 60+ Writing Task 2 Prompts',
          description: 'Free PDF: 60+ IELTS essay topics for Writing Task 2 covering education, technology, environment, society, work, and health.',
          keywords: ['IELTS essay topics', 'IELTS Writing Task 2 topics', 'IELTS essay questions', 'IELTS writing prompts'],
        }}
      />
      <SchemaMarkup schema={itemListSchema} />
      <SchemaMarkup schema={faqSchema} />

      <article>
        <h1 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-6">
          IELTS Essay Topics 2026: 60+ Writing Task 2 Prompts
        </h1>

        <ArticleParagraph>
          If you are preparing for <strong>IELTS Writing Task 2</strong>, practicing with real <strong>IELTS essay topics</strong> is one of the best ways to improve your score.
        </ArticleParagraph>

        <ArticleParagraph>
          IELTS essays cover academic and everyday themes such as education, technology, environment, society, work, and health. Practicing across categories helps you build ideas quickly and organize a clear, well-supported response under timed conditions.
        </ArticleParagraph>

        <ArticleParagraph>
          In this guide, you will find <strong>60+ IELTS essay topics</strong> for practice, similar to the prompts used in the real exam. Prefer a random prompt instead? Try the <Link to="/essay-topic-generator/" className="text-blue-600 dark:text-blue-400 hover:underline">free essay topic generator</Link>.
        </ArticleParagraph>

        <nav aria-label="Table of contents" className="bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-lg p-5 mb-8">
          <p className="font-semibold text-slate-800 dark:text-slate-200 mb-3">Jump to a topic category:</p>
          <ul className="grid sm:grid-cols-2 gap-x-6 gap-y-2 text-blue-600 dark:text-blue-400">
            <li><a href="#education-topics" className="hover:underline">Education Topics</a></li>
            <li><a href="#technology-topics" className="hover:underline">Technology Topics</a></li>
            <li><a href="#environment-topics" className="hover:underline">Environment Topics</a></li>
            <li><a href="#society-topics" className="hover:underline">Society Topics</a></li>
            <li><a href="#work-topics" className="hover:underline">Work Topics</a></li>
            <li><a href="#health-topics" className="hover:underline">Health Topics</a></li>
          </ul>
        </nav>

        <ArticleHeading>What Are IELTS Essay Topics?</ArticleHeading>
        <ArticleParagraph>
          IELTS essay topics are the prompts used in Writing Task 2. They test your ability to:
        </ArticleParagraph>
        <BulletList items={[
          'Express and support a clear opinion',
          'Discuss both sides of an argument',
          'Organize ideas logically with paragraphs and linking words',
          'Write 250+ words in 40 minutes',
        ]} />

        <ArticleHeading id="education-topics">IELTS Essay Topics About Education</ArticleHeading>
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-6 mb-6">
          <TopicList topics={educationTopics} startNumber={1} />
        </div>

        <ArticleHeading id="technology-topics">IELTS Essay Topics About Technology</ArticleHeading>
        <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-6 mb-6">
          <TopicList topics={technologyTopics} startNumber={11} />
        </div>

        <ArticleHeading id="environment-topics">IELTS Essay Topics About the Environment</ArticleHeading>
        <div className="bg-emerald-50 dark:bg-emerald-900/20 rounded-lg p-6 mb-6">
          <TopicList topics={environmentTopics} startNumber={21} />
        </div>

        <ArticleHeading id="society-topics">IELTS Essay Topics About Society</ArticleHeading>
        <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-6 mb-6">
          <TopicList topics={societyTopics} startNumber={31} />
        </div>

        <ArticleHeading id="work-topics">IELTS Essay Topics About Work</ArticleHeading>
        <div className="bg-teal-50 dark:bg-teal-900/20 rounded-lg p-6 mb-6">
          <TopicList topics={workTopics} startNumber={41} />
        </div>

        <ArticleHeading id="health-topics">IELTS Essay Topics About Health</ArticleHeading>
        <div className="bg-slate-100 dark:bg-slate-800 rounded-lg p-6 mb-6">
          <TopicList topics={healthTopics} startNumber={51} />
        </div>

        <ArticleHeading>Frequently Asked Questions</ArticleHeading>
        <div className="space-y-4 mb-6">
          <div>
            <p className="font-semibold text-slate-800 dark:text-slate-200">What are common IELTS essay topics?</p>
            <p className="text-slate-700 dark:text-slate-300">IELTS Writing Task 2 essay topics usually fall into categories like education, technology, environment, society, work, and health. Prompts ask you to agree/disagree, discuss both views, or give an opinion on an issue.</p>
          </div>
          <div>
            <p className="font-semibold text-slate-800 dark:text-slate-200">How many essay topics should I practice for IELTS?</p>
            <p className="text-slate-700 dark:text-slate-300">Practicing at least 15-20 topics across different categories is a good starting point. Focus on the categories you find hardest and time yourself at 40 minutes per essay.</p>
          </div>
          <div>
            <p className="font-semibold text-slate-800 dark:text-slate-200">Where can I get random IELTS essay topics to practice?</p>
            <p className="text-slate-700 dark:text-slate-300">Use the topics on this page, or try the free <Link to="/essay-topic-generator/" className="text-blue-600 dark:text-blue-400 hover:underline">random essay topic generator</Link> for an unlimited supply of practice prompts.</p>
          </div>
        </div>

        <RelatedContent
          items={[
            { to: '/essay-topic-generator/', title: 'Random Essay Topic Generator', subtitle: 'Generate unlimited random essay prompts for free.', badge: 'Tool' },
            { to: '/ielts/ielts-writing-task-2-essay-types/', title: 'IELTS Writing Task 2 Essay Types', subtitle: 'Learn the 5 essay types and how to structure each one.', badge: 'Lesson' },
            { to: '/ielts/50-band-9-ielts-writing-task-2-sample-essays/', title: '50 Band 9 IELTS Writing Task 2 Sample Essays', subtitle: 'Model essays with expert explanations.', badge: 'PDF' },
          ]}
        />
      </article>
    </div>
  );
};

export default IELTSEssayTopicsPage;
