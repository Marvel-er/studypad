import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import usePageMetadata from '../../hooks/usePageMetadata';
import SchemaMarkup from '../../components/SchemaMarkup';

const AnymoreVsAnyMorePage: React.FC = () => {
  usePageMetadata({
    title: 'Anymore vs. Any More: What\'s the Difference? | TypoGrammar',
    description: 'Learn the difference between anymore and any more. Anymore is an adverb meaning "no longer". Any more refers to an additional quantity. Examples and practice.',
    canonical: 'https://typogrammar.com/grammar-mistakes/anymore-vs-any-more/'
  });

  const [showAnswer, setShowAnswer] = useState(false);

  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Anymore vs. Any More: What's the Difference?",
    "description": "'Anymore' is an adverb meaning 'no longer' or 'any longer', usually used in negative sentences. 'Any more' is a determiner phrase referring to an additional quantity of something.",
    "author": { "@type": "Organization", "name": "TypoGrammar" },
    "publisher": { "@type": "Organization", "name": "TypoGrammar", "logo": { "@type": "ImageObject", "url": "https://typogrammar.com/logo.png" } },
    "mainEntityOfPage": { "@type": "WebPage", "@id": "https://typogrammar.com/grammar-mistakes/anymore-vs-any-more" },
    "datePublished": "2026-06-30",
    "dateModified": "2026-06-30"
  };

  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the difference between anymore and any more?",
        "acceptedAnswer": { "@type": "Answer", "text": "'Anymore' (one word) is an adverb meaning 'no longer' or 'any longer', typically used in negative or question sentences (I don't live here anymore. Do you smoke anymore?). 'Any more' (two words) refers to an additional quantity of something (Would you like any more tea? I don't have any more questions)." }
      },
      {
        "@type": "Question",
        "name": "How do I know whether to write anymore as one word or two?",
        "acceptedAnswer": { "@type": "Answer", "text": "If you can replace the phrase with 'any longer' or 'no longer', write it as one word: 'anymore'. If you're talking about additional quantity (more of something), write it as two words: 'any more'. Example: 'I can't wait any longer' = 'I can't wait anymore'. 'I don't want extra cake' = 'I don't want any more cake'." }
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
        <span className="text-slate-900 dark:text-slate-100">Anymore vs. Any More</span>
      </nav>

      <article className="max-w-4xl mx-auto bg-white p-8 md:p-12 rounded-xl shadow-lg shadow-slate-200/50 border border-slate-200 dark:bg-slate-800/50 dark:border-slate-700 dark:shadow-slate-900/50">
        <h1 className="font-heading text-4xl md:text-5xl font-extrabold text-slate-900 mb-6 tracking-tight dark:text-slate-100">
          Anymore vs. Any More: What's the Difference?
        </h1>

        <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-r-lg mb-8 dark:bg-green-900/30 dark:border-green-400">
          <h2 className="text-xl font-bold text-green-900 dark:text-green-100 mb-2">Quick Answer</h2>
          <p className="text-lg text-green-800 dark:text-green-200 mb-2">
            <strong>anymore</strong> = adverb meaning "no longer" / "any longer"
          </p>
          <p className="text-lg text-green-800 dark:text-green-200">
            <strong>any more</strong> = determiner phrase meaning an additional quantity
          </p>
        </div>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Explanation
          </h2>
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <p className="font-bold text-blue-900 dark:text-blue-100 mb-2">ANYMORE (one word, adverb)</p>
              <p className="text-blue-800 dark:text-blue-200 mb-2 text-sm">Means "no longer" — used with negatives/questions</p>
              <p className="text-blue-700 dark:text-blue-300 italic text-sm">"I don't eat meat <strong>anymore</strong>."</p>
              <p className="text-blue-700 dark:text-blue-300 italic text-sm">"Does she work here <strong>anymore</strong>?"</p>
            </div>
            <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
              <p className="font-bold text-purple-900 dark:text-purple-100 mb-2">ANY MORE (two words)</p>
              <p className="text-purple-800 dark:text-purple-200 mb-2 text-sm">Means an additional quantity of something</p>
              <p className="text-purple-700 dark:text-purple-300 italic text-sm">"Is there <strong>any more</strong> coffee?"</p>
              <p className="text-purple-700 dark:text-purple-300 italic text-sm">"I don't need <strong>any more</strong> help."</p>
            </div>
          </div>
          <div className="bg-teal-50 dark:bg-teal-900/20 p-4 rounded-lg">
            <p className="text-lg text-teal-800 dark:text-teal-200">
              <strong>Quick test:</strong> Can you replace it with "no longer"? Use <strong>anymore</strong>. Is it followed by (or referring to) a noun, asking for extra quantity? Use <strong>any more</strong>.
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
              <span className="text-lg text-slate-700 dark:text-slate-300">She doesn't live in this city <strong>anymore</strong>. (no longer)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">Do you want <strong>any more</strong> pizza? (additional quantity)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">I can't deal with this <strong>anymore</strong>. (no longer)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">We don't have <strong>any more</strong> tickets left. (additional quantity)</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">I don't want any more to wait.</span>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Common Mistakes
          </h2>
          <div className="space-y-4">
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> I don't have any more time for this nonsense any more.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> I don't have any more time for this nonsense anymore. (any more = extra time; anymore = no longer)</p>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> We can't afford anymore vacations this year.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> We can't afford any more vacations this year. (additional quantity)</p>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Practice
          </h2>
          <div className="bg-teal-50 dark:bg-teal-900/20 p-6 rounded-lg">
            <p className="text-lg text-slate-700 dark:text-slate-300 mb-4">
              <strong>Choose the correct form:</strong>
            </p>
            <p className="text-lg text-slate-800 dark:text-slate-200 italic mb-4">
              "I don't have _____ patience for this game _____, so I won't buy _____ copies."
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
                  <strong>Answer:</strong> "I don't have <strong>any more</strong> patience for this game <strong>anymore</strong>, so I won't buy <strong>any more</strong> copies."
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
            <li><Link to="/grammar-mistakes/everyone-vs-every-one/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Everyone vs. Every One</Link></li>
            <li><Link to="/grammar-mistakes/onto-vs-on-to/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Onto vs. On To</Link></li>
            <li><Link to="/grammar-mistakes/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ All Grammar Mistakes</Link></li>
          </ul>
        </section>
      </article>
    </>
  );
};

export default AnymoreVsAnyMorePage;
