import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import usePageMetadata from '../../hooks/usePageMetadata';
import SchemaMarkup from '../../components/SchemaMarkup';

const QuietVsQuitePage: React.FC = () => {
  usePageMetadata({
    title: 'Quiet vs. Quite: What\'s the Difference? | TypoGrammar',
    description: 'Learn the difference between quiet and quite. Quiet is an adjective meaning silent or calm. Quite is an adverb meaning fairly or completely. Clear examples and practice.',
    canonical: 'https://typogrammar.com/grammar-mistakes/quiet-vs-quite/'
  });

  const [showAnswer, setShowAnswer] = useState(false);

  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Quiet vs. Quite: What's the Difference?",
    "description": "'Quiet' is an adjective meaning making little noise or calm. 'Quite' is an adverb meaning fairly, rather, or completely.",
    "author": { "@type": "Organization", "name": "TypoGrammar" },
    "publisher": { "@type": "Organization", "name": "TypoGrammar", "logo": { "@type": "ImageObject", "url": "https://typogrammar.com/logo.png" } },
    "mainEntityOfPage": { "@type": "WebPage", "@id": "https://typogrammar.com/grammar-mistakes/quiet-vs-quite" },
    "datePublished": "2026-06-30",
    "dateModified": "2026-06-30"
  };

  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the difference between quiet and quite?",
        "acceptedAnswer": { "@type": "Answer", "text": "'Quiet' is an adjective meaning making little or no noise, or calm and peaceful (Please be quiet. It's a quiet neighborhood). 'Quite' is an adverb meaning fairly/rather (quite good) or completely (quite sure, quite right)." }
      },
      {
        "@type": "Question",
        "name": "How do I avoid mixing up quiet and quite?",
        "acceptedAnswer": { "@type": "Answer", "text": "Quiet has two syllables (qui-et) and describes sound or calmness — think of a 'quiet' library. Quite has one syllable and modifies adjectives or adverbs — think 'quite' as a synonym for 'rather' or 'very'. If you can replace the word with 'rather' or 'very', use 'quite'." }
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
        <span className="text-slate-900 dark:text-slate-100">Quiet vs. Quite</span>
      </nav>

      <article className="max-w-4xl mx-auto bg-white p-8 md:p-12 rounded-xl shadow-lg shadow-slate-200/50 border border-slate-200 dark:bg-slate-800/50 dark:border-slate-700 dark:shadow-slate-900/50">
        <h1 className="font-heading text-4xl md:text-5xl font-extrabold text-slate-900 mb-6 tracking-tight dark:text-slate-100">
          Quiet vs. Quite: What's the Difference?
        </h1>

        <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-r-lg mb-8 dark:bg-green-900/30 dark:border-green-400">
          <h2 className="text-xl font-bold text-green-900 dark:text-green-100 mb-2">Quick Answer</h2>
          <p className="text-lg text-green-800 dark:text-green-200 mb-2">
            <strong>quiet</strong> = adjective — silent, calm, making little noise
          </p>
          <p className="text-lg text-green-800 dark:text-green-200">
            <strong>quite</strong> = adverb — fairly/rather, or completely
          </p>
        </div>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Explanation
          </h2>
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <p className="font-bold text-blue-900 dark:text-blue-100 mb-2">QUIET (adjective)</p>
              <p className="text-blue-800 dark:text-blue-200 mb-2">Silent, calm, peaceful</p>
              <p className="text-blue-700 dark:text-blue-300 font-mono text-sm mb-2">opposite: loud, noisy</p>
              <p className="text-blue-700 dark:text-blue-300 italic mt-3">"Please be <strong>quiet</strong> in the library."</p>
              <p className="text-blue-700 dark:text-blue-300 italic">"It's a <strong>quiet</strong> little town."</p>
            </div>
            <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
              <p className="font-bold text-purple-900 dark:text-purple-100 mb-2">QUITE (adverb)</p>
              <p className="text-purple-800 dark:text-purple-200 mb-2">Fairly/rather, or completely</p>
              <p className="text-purple-700 dark:text-purple-300 font-mono text-sm mb-2">quite + adjective/adverb</p>
              <p className="text-purple-700 dark:text-purple-300 italic mt-3">"It's <strong>quite</strong> cold today." (fairly)</p>
              <p className="text-purple-700 dark:text-purple-300 italic">"I'm <strong>quite</strong> sure." (completely)</p>
            </div>
          </div>
          <div className="bg-teal-50 dark:bg-teal-900/20 p-4 rounded-lg">
            <p className="text-lg text-teal-800 dark:text-teal-200">
              <strong>Memory trick:</strong> <strong>Quiet</strong> has two syllables, like a hushed "qui-et" whisper. <strong>Quite</strong> has just one syllable and pairs with adjectives — replace it with "rather" or "very" to check.
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
              <span className="text-lg text-slate-700 dark:text-slate-300">The classroom was completely <strong>quiet</strong>. (adjective)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">This exam is <strong>quite</strong> difficult. (rather)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">She has a <strong>quiet</strong> voice. (adjective)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">You're <strong>quite</strong> right about that. (completely)</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">Please be quite during the test.</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">It's quiet cold outside today.</span>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Common Mistakes
          </h2>
          <div className="space-y-4">
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> The hotel room was quite and comfortable.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> The hotel room was quiet and comfortable. (quiet = adjective, peaceful)</p>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> I was quiet surprised by the news.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> I was quite surprised by the news. (quite = rather/very)</p>
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
              "The library was _____ , and I was _____ impressed by how organized it was."
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
                  <strong>Answer:</strong> "The library was <strong>quiet</strong>, and I was <strong>quite</strong> impressed..."
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
            <li><Link to="/grammar-mistakes/very-vs-too-vs-so/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Very vs. Too vs. So</Link></li>
            <li><Link to="/grammar-mistakes/weather-vs-whether/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Weather vs. Whether</Link></li>
            <li><Link to="/grammar-mistakes/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ All Grammar Mistakes</Link></li>
          </ul>
        </section>
      </article>
    </>
  );
};

export default QuietVsQuitePage;
