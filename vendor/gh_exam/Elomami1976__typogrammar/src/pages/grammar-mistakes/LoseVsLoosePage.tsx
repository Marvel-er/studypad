import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import usePageMetadata from '../../hooks/usePageMetadata';
import SchemaMarkup from '../../components/SchemaMarkup';

const LoseVsLoosePage: React.FC = () => {
  usePageMetadata({
    title: 'Lose vs. Loose: What\'s the Difference? | TypoGrammar',
    description: 'Learn the difference between lose and loose. Lose is a verb (to misplace or not win). Loose is an adjective (not tight). Clear examples and practice exercises.',
    canonical: 'https://typogrammar.com/grammar-mistakes/lose-vs-loose/'
  });

  const [showAnswer, setShowAnswer] = useState(false);

  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Lose vs. Loose: What's the Difference?",
    "description": "'Lose' is a verb meaning to misplace something or fail to win. 'Loose' is an adjective meaning not tight or not firmly attached.",
    "author": { "@type": "Organization", "name": "TypoGrammar" },
    "publisher": { "@type": "Organization", "name": "TypoGrammar", "logo": { "@type": "ImageObject", "url": "https://typogrammar.com/logo.png" } },
    "mainEntityOfPage": { "@type": "WebPage", "@id": "https://typogrammar.com/grammar-mistakes/lose-vs-loose" },
    "datePublished": "2026-06-30",
    "dateModified": "2026-06-30"
  };

  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the difference between lose and loose?",
        "acceptedAnswer": { "@type": "Answer", "text": "'Lose' (one 'o') is a verb meaning to misplace something or fail to win (Don't lose your ticket. Our team might lose). 'Loose' (two o's) is an adjective meaning not tight or not firmly attached (The screw is loose. Wear loose clothing). Remember: lose rhymes with 'whose' and 'choose'." }
      },
      {
        "@type": "Question",
        "name": "How do I remember lose vs. loose?",
        "acceptedAnswer": { "@type": "Answer", "text": "Lose has one 'o' and is a verb. Loose has two o's — picture them as two 'o's that have come loose from their positions. Another tip: 'loose' rhymes with 'goose', a thing that is free and untethered." }
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
        <span className="text-slate-900 dark:text-slate-100">Lose vs. Loose</span>
      </nav>

      <article className="max-w-4xl mx-auto bg-white p-8 md:p-12 rounded-xl shadow-lg shadow-slate-200/50 border border-slate-200 dark:bg-slate-800/50 dark:border-slate-700 dark:shadow-slate-900/50">
        <h1 className="font-heading text-4xl md:text-5xl font-extrabold text-slate-900 mb-6 tracking-tight dark:text-slate-100">
          Lose vs. Loose: What's the Difference?
        </h1>

        <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-r-lg mb-8 dark:bg-green-900/30 dark:border-green-400">
          <h2 className="text-xl font-bold text-green-900 dark:text-green-100 mb-2">Quick Answer</h2>
          <p className="text-lg text-green-800 dark:text-green-200 mb-2">
            <strong>lose</strong> (1 "o") = verb — to misplace something or fail to win
          </p>
          <p className="text-lg text-green-800 dark:text-green-200">
            <strong>loose</strong> (2 "o"s) = adjective — not tight, not firmly attached
          </p>
        </div>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Explanation
          </h2>
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <p className="font-bold text-blue-900 dark:text-blue-100 mb-2">LOSE (verb) — one "o"</p>
              <p className="text-blue-800 dark:text-blue-200 mb-2">To be unable to find / to fail to win</p>
              <p className="text-blue-700 dark:text-blue-300 font-mono text-sm mb-2">lose → lost → lost</p>
              <p className="text-blue-700 dark:text-blue-300 italic mt-3">"Don't <strong>lose</strong> your keys."</p>
              <p className="text-blue-700 dark:text-blue-300 italic">"We might <strong>lose</strong> the game."</p>
              <p className="text-blue-700 dark:text-blue-300 italic">"I always <strong>lose</strong> track of time."</p>
            </div>
            <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
              <p className="font-bold text-purple-900 dark:text-purple-100 mb-2">LOOSE (adjective) — two "o"s</p>
              <p className="text-purple-800 dark:text-purple-200 mb-2">Not tight, not firmly attached, free</p>
              <p className="text-purple-700 dark:text-purple-300 font-mono text-sm mb-2">opposite: tight, fixed, secure</p>
              <p className="text-purple-700 dark:text-purple-300 italic mt-3">"This screw is <strong>loose</strong>."</p>
              <p className="text-purple-700 dark:text-purple-300 italic">"Wear <strong>loose</strong> clothing to the gym."</p>
              <p className="text-purple-700 dark:text-purple-300 italic">"The dog got <strong>loose</strong> from its leash."</p>
            </div>
          </div>
          <div className="bg-teal-50 dark:bg-teal-900/20 p-4 rounded-lg">
            <p className="text-lg text-teal-800 dark:text-teal-200">
              <strong>Memory trick:</strong> "loose" has a double-o that has come loose — two o's floating free. "lose" rhymes with "whose" and "choose" — single-o verb.
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
              <span className="text-lg text-slate-700 dark:text-slate-300">Be careful not to <strong>lose</strong> your passport. (verb)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">My jeans are too <strong>loose</strong> now that I've lost weight. (adjective)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">Did you <strong>lose</strong> the match? (verb)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">There is a <strong>loose</strong> wire in the socket. (adjective)</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">Don't loose your temper.</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">The knot is to lose.</span>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Common Mistakes
          </h2>
          <div className="space-y-4">
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> I always loose my phone.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> I always lose my phone. ("lose" = verb, to misplace)</p>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> The button on my shirt is lose.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> The button on my shirt is loose. ("loose" = adjective, not tight)</p>
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
              "If you don't tighten that _____ screw, you'll _____ the whole shelf."
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
                  <strong>Answer:</strong> "...that <strong>loose</strong> screw, you'll <strong>lose</strong> the whole shelf."
                </p>
                <p className="text-green-700 dark:text-green-300 mt-2">
                  Loose = adjective (not tight). Lose = verb (to cause to fall apart / be lost).
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
            <li><Link to="/grammar-mistakes/affect-vs-effect/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Affect vs. Effect</Link></li>
            <li><Link to="/grammar-mistakes/passed-vs-past/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Passed vs. Past</Link></li>
            <li><Link to="/grammar-mistakes/lead-vs-led/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Lead vs. Led</Link></li>
            <li><Link to="/grammar-mistakes/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ All Grammar Mistakes</Link></li>
          </ul>
        </section>
      </article>
    </>
  );
};

export default LoseVsLoosePage;
