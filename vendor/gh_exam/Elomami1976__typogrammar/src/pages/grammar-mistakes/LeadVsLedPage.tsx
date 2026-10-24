import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import usePageMetadata from '../../hooks/usePageMetadata';
import SchemaMarkup from '../../components/SchemaMarkup';

const LeadVsLedPage: React.FC = () => {
  usePageMetadata({
    title: 'Lead vs. Led: What\'s the Difference? | TypoGrammar',
    description: 'Learn the difference between lead and led. Lead is the present tense verb (or a metal). Led is the past tense of lead. Clear examples and practice.',
    canonical: 'https://typogrammar.com/grammar-mistakes/lead-vs-led/'
  });

  const [showAnswer, setShowAnswer] = useState(false);

  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Lead vs. Led: What's the Difference?",
    "description": "'Lead' is the present tense verb meaning to guide (or a noun referring to the metal). 'Led' is the past tense and past participle of the verb 'lead'.",
    "author": { "@type": "Organization", "name": "TypoGrammar" },
    "publisher": { "@type": "Organization", "name": "TypoGrammar", "logo": { "@type": "ImageObject", "url": "https://typogrammar.com/logo.png" } },
    "mainEntityOfPage": { "@type": "WebPage", "@id": "https://typogrammar.com/grammar-mistakes/lead-vs-led" },
    "datePublished": "2026-06-30",
    "dateModified": "2026-06-30"
  };

  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the difference between lead and led?",
        "acceptedAnswer": { "@type": "Answer", "text": "'Lead' (rhymes with 'reed') is the present tense verb meaning to guide or be in charge (She will lead the team). It's also a noun for the metal (rhymes with 'red'). 'Led' (rhymes with 'red') is always the past tense/past participle of the verb 'lead' (Yesterday she led the team)." }
      },
      {
        "@type": "Question",
        "name": "Why do people confuse lead and led?",
        "acceptedAnswer": { "@type": "Answer", "text": "The confusion happens because the noun 'lead' (the metal) is pronounced exactly like 'led', tricking writers into spelling the past tense verb as 'lead' too. Remember: the past tense verb is always spelled 'led', never 'lead'." }
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
        <span className="text-slate-900 dark:text-slate-100">Lead vs. Led</span>
      </nav>

      <article className="max-w-4xl mx-auto bg-white p-8 md:p-12 rounded-xl shadow-lg shadow-slate-200/50 border border-slate-200 dark:bg-slate-800/50 dark:border-slate-700 dark:shadow-slate-900/50">
        <h1 className="font-heading text-4xl md:text-5xl font-extrabold text-slate-900 mb-6 tracking-tight dark:text-slate-100">
          Lead vs. Led: What's the Difference?
        </h1>

        <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-r-lg mb-8 dark:bg-green-900/30 dark:border-green-400">
          <h2 className="text-xl font-bold text-green-900 dark:text-green-100 mb-2">Quick Answer</h2>
          <p className="text-lg text-green-800 dark:text-green-200 mb-2">
            <strong>lead</strong> = present tense verb "to guide" (rhymes with "reed"), or the metal (rhymes with "red")
          </p>
          <p className="text-lg text-green-800 dark:text-green-200">
            <strong>led</strong> = past tense/past participle of "lead" (always rhymes with "red")
          </p>
        </div>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Explanation
          </h2>
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <p className="font-bold text-blue-900 dark:text-blue-100 mb-2">LEAD (present tense / noun)</p>
              <p className="text-blue-800 dark:text-blue-200 mb-1 text-sm">Verb: to guide, be in charge (rhymes with "reed")</p>
              <p className="text-blue-800 dark:text-blue-200 mb-2 text-sm">Noun: a heavy metal (rhymes with "red")</p>
              <p className="text-blue-700 dark:text-blue-300 italic text-sm">"She will <strong>lead</strong> the meeting."</p>
              <p className="text-blue-700 dark:text-blue-300 italic text-sm">"Pipes used to be made of <strong>lead</strong>."</p>
            </div>
            <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
              <p className="font-bold text-purple-900 dark:text-purple-100 mb-2">LED (past tense)</p>
              <p className="text-purple-800 dark:text-purple-200 mb-2 text-sm">Past tense / past participle of "lead" (rhymes with "red")</p>
              <p className="text-purple-700 dark:text-purple-300 font-mono text-sm mb-2">lead → led → led</p>
              <p className="text-purple-700 dark:text-purple-300 italic text-sm">"She <strong>led</strong> the meeting yesterday."</p>
              <p className="text-purple-700 dark:text-purple-300 italic text-sm">"He has <strong>led</strong> the company for years."</p>
            </div>
          </div>
          <div className="bg-teal-50 dark:bg-teal-900/20 p-4 rounded-lg">
            <p className="text-lg text-teal-800 dark:text-teal-200">
              <strong>Memory trick:</strong> The metal "lead" is spelled like the present-tense verb but sounds like "led" — that's the trap. Just remember: the <strong>past tense verb is always "led"</strong>, three letters, no exceptions.
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
              <span className="text-lg text-slate-700 dark:text-slate-300">Please <strong>lead</strong> the way. (present tense verb)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">The coach <strong>led</strong> the team to victory. (past tense)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">Old paint often contained <strong>lead</strong>. (noun, metal)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">This road <strong>leads</strong> to the city center. (present tense)</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">She lead the team to victory last year.</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">He will led the new project.</span>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Common Mistakes
          </h2>
          <div className="space-y-4">
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> Yesterday, the CEO lead the announcement.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> Yesterday, the CEO led the announcement. (past tense)</p>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> She will led the workshop tomorrow.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> She will lead the workshop tomorrow. (future + present-tense verb)</p>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Practice
          </h2>
          <div className="bg-teal-50 dark:bg-teal-900/20 p-6 rounded-lg">
            <p className="text-lg text-slate-700 dark:text-slate-300 mb-4">
              <strong>Choose the correct word:</strong>
            </p>
            <p className="text-lg text-slate-800 dark:text-slate-200 italic mb-4">
              "Last year, she _____ the company through a crisis. Now she will _____ it into a new era."
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
                  <strong>Answer:</strong> "Last year, she <strong>led</strong> the company... Now she will <strong>lead</strong> it..."
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
            <li><Link to="/grammar-mistakes/passed-vs-past/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Passed vs. Past</Link></li>
            <li><Link to="/irregular-verbs/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Irregular Verbs List</Link></li>
            <li><Link to="/grammar-mistakes/lay-vs-lie/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Lay vs. Lie</Link></li>
            <li><Link to="/grammar-mistakes/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ All Grammar Mistakes</Link></li>
          </ul>
        </section>
      </article>
    </>
  );
};

export default LeadVsLedPage;
