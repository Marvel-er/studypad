import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import usePageMetadata from '../../hooks/usePageMetadata';
import SchemaMarkup from '../../components/SchemaMarkup';

const EgVsIePage: React.FC = () => {
  usePageMetadata({
    title: 'e.g. vs. i.e.: What\'s the Difference? | TypoGrammar',
    description: 'Learn the difference between e.g. and i.e. e.g. means "for example" and introduces examples. i.e. means "that is" and clarifies or restates. Examples and practice.',
    canonical: 'https://typogrammar.com/grammar-mistakes/eg-vs-ie/'
  });

  const [showAnswer, setShowAnswer] = useState(false);

  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "e.g. vs. i.e.: What's the Difference?",
    "description": "'e.g.' (exempli gratia) means 'for example' and introduces a non-exhaustive list. 'i.e.' (id est) means 'that is' and clarifies or restates exactly what was meant.",
    "author": { "@type": "Organization", "name": "TypoGrammar" },
    "publisher": { "@type": "Organization", "name": "TypoGrammar", "logo": { "@type": "ImageObject", "url": "https://typogrammar.com/logo.png" } },
    "mainEntityOfPage": { "@type": "WebPage", "@id": "https://typogrammar.com/grammar-mistakes/eg-vs-ie" },
    "datePublished": "2026-06-30",
    "dateModified": "2026-06-30"
  };

  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the difference between e.g. and i.e.?",
        "acceptedAnswer": { "@type": "Answer", "text": "'e.g.' comes from the Latin 'exempli gratia' meaning 'for example' — it introduces one or more examples from a larger group (I like citrus fruits, e.g., oranges and lemons). 'i.e.' comes from 'id est' meaning 'that is' — it clarifies or restates the exact meaning of something (Use the main entrance, i.e., the one facing the street)." }
      },
      {
        "@type": "Question",
        "name": "How do I remember e.g. vs i.e.?",
        "acceptedAnswer": { "@type": "Answer", "text": "Think 'e.g.' = 'example given' (both start with E). Think 'i.e.' = 'in essence' or 'in other words' (both start with I). If you can replace the phrase with 'for example', use e.g. If you can replace it with 'that is to say', use i.e." }
      }
    ]
  };

  return (
    <>
      <SchemaMarkup type="Article" data={articleSchema} />
      <SchemaMarkup type="FAQPage" data={faqSchema} />

      <nav className="mb-6 text-slate-600 dark:text-slate-400">
        <Link to="/" className="hover:text-blue-600 dark:hover:text-blue-400">Home</Link>
        {' › '}
        <Link to="/grammar-mistakes/" className="hover:text-blue-600 dark:hover:text-blue-400">Grammar Mistakes</Link>
        {' › '}
        <span className="text-slate-900 dark:text-slate-100">e.g. vs. i.e.</span>
      </nav>

      <article className="max-w-4xl mx-auto bg-white p-8 md:p-12 rounded-xl shadow-lg shadow-slate-200/50 border border-slate-200 dark:bg-slate-800/50 dark:border-slate-700 dark:shadow-slate-900/50">
        <h1 className="font-heading text-4xl md:text-5xl font-extrabold text-slate-900 mb-6 tracking-tight dark:text-slate-100">
          e.g. vs. i.e.: What's the Difference?
        </h1>

        <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-r-lg mb-8 dark:bg-green-900/30 dark:border-green-400">
          <h2 className="text-xl font-bold text-green-900 dark:text-green-100 mb-2">Quick Answer</h2>
          <p className="text-lg text-green-800 dark:text-green-200 mb-2">
            <strong>e.g.</strong> = "for example" — introduces examples from a larger group
          </p>
          <p className="text-lg text-green-800 dark:text-green-200">
            <strong>i.e.</strong> = "that is" — clarifies or restates exactly what you mean
          </p>
        </div>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Explanation
          </h2>
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <p className="font-bold text-blue-900 dark:text-blue-100 mb-2">E.G. (for example)</p>
              <p className="text-blue-800 dark:text-blue-200 mb-1 text-sm">Latin: exempli gratia</p>
              <p className="text-blue-700 dark:text-blue-300 text-sm mb-2">Introduces a non-exhaustive list of examples</p>
              <p className="text-blue-700 dark:text-blue-300 italic text-sm">"I enjoy winter sports, <strong>e.g.</strong>, skiing and skating."</p>
              <p className="text-blue-700 dark:text-blue-300 italic text-sm">"Bring warm clothes, <strong>e.g.</strong>, a coat or sweater."</p>
            </div>
            <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
              <p className="font-bold text-purple-900 dark:text-purple-100 mb-2">I.E. (that is)</p>
              <p className="text-purple-800 dark:text-purple-200 mb-1 text-sm">Latin: id est</p>
              <p className="text-purple-700 dark:text-purple-300 text-sm mb-2">Restates or clarifies — gives the complete, exact meaning</p>
              <p className="text-purple-700 dark:text-purple-300 italic text-sm">"Use the back entrance, <strong>i.e.</strong>, the one by the parking lot."</p>
              <p className="text-purple-700 dark:text-purple-300 italic text-sm">"We meet biweekly, <strong>i.e.</strong>, twice a month."</p>
            </div>
          </div>
          <div className="bg-teal-50 dark:bg-teal-900/20 p-4 rounded-lg">
            <p className="text-lg text-teal-800 dark:text-teal-200">
              <strong>Memory trick:</strong> <strong>e.g.</strong> = "<strong>e</strong>xact <strong>g</strong>iven examples" (a sample). <strong>i.e.</strong> = "<strong>i</strong>n <strong>e</strong>ssence" (the full, precise meaning). Both abbreviations are typically followed by a comma in American English.
            </p>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Examples
          </h2>
          <div className="space-y-3">
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">She speaks several languages, <strong>e.g.</strong>, French and German. (examples, not the full list)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">The deadline is the end of the quarter, <strong>i.e.</strong>, March 31st. (exact clarification)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">Bring identification, <strong>e.g.</strong>, a passport or driver's license. (examples)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">Only full-time staff, <strong>i.e.</strong>, those working 40 hours a week, qualify. (precise definition)</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">I like fruits, i.e. apples and bananas.</span>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Common Mistakes
          </h2>
          <div className="space-y-4">
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> Please bring snacks, i.e. chips or cookies.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> Please bring snacks, e.g., chips or cookies. (these are just examples, not the only options)</p>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> The meeting is next week, e.g., Tuesday.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> The meeting is next week, i.e., Tuesday. (this is the exact day, not an example)</p>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Practice
          </h2>
          <div className="bg-teal-50 dark:bg-teal-900/20 p-6 rounded-lg">
            <p className="text-lg text-slate-700 dark:text-slate-300 mb-4">
              <strong>Choose the correct abbreviation:</strong>
            </p>
            <p className="text-lg text-slate-800 dark:text-slate-200 italic mb-4">
              "We need office supplies, _____, pens and paper. The order must arrive by the due date, _____, this Friday."
            </p>
            <button
              onClick={() => setShowAnswer(!showAnswer)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              {showAnswer ? 'Hide Answer' : 'Show Answer'}
            </button>
            {showAnswer && (
              <div className="mt-4 p-4 bg-green-100 dark:bg-green-900/30 rounded-lg">
                <p className="text-lg text-green-800 dark:text-green-200">
                  <strong>Answer:</strong> "...office supplies, <strong>e.g.</strong>, pens and paper... by the due date, <strong>i.e.</strong>, this Friday."
                </p>
              </div>
            )}
          </div>
        </section>

        <section className="mb-6">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Related Grammar
          </h2>
          <ul className="space-y-2 text-lg">
            <li><Link to="/grammar-mistakes/other-vs-another/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Other vs. Another</Link></li>
            <li><Link to="/grammar-mistakes/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ All Grammar Mistakes</Link></li>
          </ul>
        </section>
      </article>
    </>
  );
};

export default EgVsIePage;
