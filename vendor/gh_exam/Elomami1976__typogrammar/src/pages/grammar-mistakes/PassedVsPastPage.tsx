import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import usePageMetadata from '../../hooks/usePageMetadata';
import SchemaMarkup from '../../components/SchemaMarkup';

const PassedVsPastPage: React.FC = () => {
  usePageMetadata({
    title: 'Passed vs. Past: What\'s the Difference? | TypoGrammar',
    description: 'Learn the difference between passed and past. Passed is the past tense of the verb "pass". Past is an adjective, noun, or preposition about time or position. Clear examples.',
    canonical: 'https://typogrammar.com/grammar-mistakes/passed-vs-past/'
  });

  const [showAnswer, setShowAnswer] = useState(false);

  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Passed vs. Past: What's the Difference?",
    "description": "'Passed' is the past tense and past participle of the verb 'to pass'. 'Past' functions as an adjective, noun, adverb, or preposition — it is never a verb.",
    "author": { "@type": "Organization", "name": "TypoGrammar" },
    "publisher": { "@type": "Organization", "name": "TypoGrammar", "logo": { "@type": "ImageObject", "url": "https://typogrammar.com/logo.png" } },
    "mainEntityOfPage": { "@type": "WebPage", "@id": "https://typogrammar.com/grammar-mistakes/passed-vs-past" },
    "datePublished": "2026-06-30",
    "dateModified": "2026-06-30"
  };

  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the difference between passed and past?",
        "acceptedAnswer": { "@type": "Answer", "text": "'Passed' is only ever a verb — the past tense of 'pass' (He passed the exam. Time has passed). 'Past' is never a verb; it works as an adjective (past events), noun (in the past), preposition (walk past the shop), or adverb (the car drove past)." }
      },
      {
        "@type": "Question",
        "name": "How do I know whether to use passed or past?",
        "acceptedAnswer": { "@type": "Answer", "text": "Test: can you replace the word with another verb form like 'went by' or 'moved'? If yes, use 'passed' (a verb). If the word is modifying a noun or following a preposition, use 'past'. Example: 'We passed the museum' = we went past it (verb). 'The museum is past the bridge' = beyond the bridge (preposition)." }
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
        <span className="text-slate-900 dark:text-slate-100">Passed vs. Past</span>
      </nav>

      <article className="max-w-4xl mx-auto bg-white p-8 md:p-12 rounded-xl shadow-lg shadow-slate-200/50 border border-slate-200 dark:bg-slate-800/50 dark:border-slate-700 dark:shadow-slate-900/50">
        <h1 className="font-heading text-4xl md:text-5xl font-extrabold text-slate-900 mb-6 tracking-tight dark:text-slate-100">
          Passed vs. Past: What's the Difference?
        </h1>

        <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-r-lg mb-8 dark:bg-green-900/30 dark:border-green-400">
          <h2 className="text-xl font-bold text-green-900 dark:text-green-100 mb-2">Quick Answer</h2>
          <p className="text-lg text-green-800 dark:text-green-200 mb-2">
            <strong>passed</strong> = verb only — past tense of "pass" (He passed the test.)
          </p>
          <p className="text-lg text-green-800 dark:text-green-200">
            <strong>past</strong> = adjective, noun, preposition, or adverb — never a verb
          </p>
        </div>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Explanation
          </h2>
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <p className="font-bold text-blue-900 dark:text-blue-100 mb-2">PASSED (verb)</p>
              <p className="text-blue-800 dark:text-blue-200 mb-2">Past tense / past participle of "pass"</p>
              <p className="text-blue-700 dark:text-blue-300 font-mono text-sm mb-2">pass → passed → passed</p>
              <p className="text-blue-700 dark:text-blue-300 italic mt-3">"She <strong>passed</strong> her driving test."</p>
              <p className="text-blue-700 dark:text-blue-300 italic">"Time <strong>passed</strong> slowly."</p>
              <p className="text-blue-700 dark:text-blue-300 italic">"He <strong>passed</strong> the ball."</p>
            </div>
            <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
              <p className="font-bold text-purple-900 dark:text-purple-100 mb-2">PAST (not a verb)</p>
              <p className="text-purple-800 dark:text-purple-200 mb-1 text-sm">Adjective: "past events", "past mistakes"</p>
              <p className="text-purple-800 dark:text-purple-200 mb-1 text-sm">Noun: "in the past", "forget the past"</p>
              <p className="text-purple-800 dark:text-purple-200 mb-1 text-sm">Preposition: "walk past the shop"</p>
              <p className="text-purple-800 dark:text-purple-200 mb-2 text-sm">Adverb: "a car drove past"</p>
              <p className="text-purple-700 dark:text-purple-300 italic text-sm">"In the <strong>past</strong>, things were different." (noun)</p>
              <p className="text-purple-700 dark:text-purple-300 italic text-sm">"Walk <strong>past</strong> the church." (preposition)</p>
            </div>
          </div>
          <div className="bg-teal-50 dark:bg-teal-900/20 p-4 rounded-lg">
            <p className="text-lg text-teal-800 dark:text-teal-200">
              <strong>Quick test:</strong> Can you replace the word with "went by" or another verb? → use <strong>passed</strong>. Is it followed by a noun or acting as a noun/adjective? → use <strong>past</strong>.
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
              <span className="text-lg text-slate-700 dark:text-slate-300">Three months have <strong>passed</strong> since we met. (verb)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">We need to learn from our <strong>past</strong> mistakes. (adjective)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">The bus stop is just <strong>past</strong> the traffic lights. (preposition)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">A stranger <strong>passed</strong> us on the road. (verb)</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">It is half past three — time has past so quickly.</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">She walked passed the café without stopping.</span>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Common Mistakes
          </h2>
          <div className="space-y-4">
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> A lot of time has past since then.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> A lot of time has passed since then. (verb — has + past participle)</p>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> Turn left just passed the school.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> Turn left just past the school. (preposition — beyond the school)</p>
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
              "In the _____, she had _____ every exam with top marks."
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
                  <strong>Answer:</strong> "In the <strong>past</strong>, she had <strong>passed</strong> every exam..."
                </p>
                <p className="text-green-700 dark:text-green-300 mt-2">
                  Past = noun (the time before now). Passed = verb (past tense of pass).
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
            <li><Link to="/grammar-mistakes/lead-vs-led/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Lead vs. Led</Link></li>
            <li><Link to="/grammar-mistakes/then-vs-than/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Then vs. Than</Link></li>
            <li><Link to="/grammar-mistakes/affect-vs-effect/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Affect vs. Effect</Link></li>
            <li><Link to="/grammar-mistakes/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ All Grammar Mistakes</Link></li>
          </ul>
        </section>
      </article>
    </>
  );
};

export default PassedVsPastPage;
