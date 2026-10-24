import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import usePageMetadata from '../../hooks/usePageMetadata';
import SchemaMarkup from '../../components/SchemaMarkup';

const ToVsTooVsTwoPage: React.FC = () => {
  usePageMetadata({
    title: 'To vs. Too vs. Two: What\'s the Difference? | TypoGrammar',
    description: 'Learn the difference between to, too, and two. To is a preposition or infinitive marker. Too means also or excessively. Two is the number 2. Examples and practice.',
    canonical: 'https://typogrammar.com/grammar-mistakes/to-vs-too-vs-two/'
  });

  const [showAnswer, setShowAnswer] = useState(false);

  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "To vs. Too vs. Two: What's the Difference?",
    "description": "'To' is a preposition or infinitive marker. 'Too' means also or excessively. 'Two' is the number 2. These three homophones sound the same but have completely different meanings.",
    "author": { "@type": "Organization", "name": "TypoGrammar" },
    "publisher": { "@type": "Organization", "name": "TypoGrammar", "logo": { "@type": "ImageObject", "url": "https://typogrammar.com/logo.png" } },
    "mainEntityOfPage": { "@type": "WebPage", "@id": "https://typogrammar.com/grammar-mistakes/to-vs-too-vs-two" },
    "datePublished": "2026-06-30",
    "dateModified": "2026-06-30"
  };

  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the difference between to, too, and two?",
        "acceptedAnswer": { "@type": "Answer", "text": "'To' has many uses: it is a preposition (go to school, from A to B) and the infinitive marker (want to eat, how to do it). 'Too' is an adverb meaning 'also' (I want some too) or 'excessively' (too loud, too much). 'Two' is simply the number 2 (two cats, two hours)." }
      },
      {
        "@type": "Question",
        "name": "When should I use 'too' vs 'to'?",
        "acceptedAnswer": { "@type": "Answer", "text": "Use 'too' when you mean 'also' (She is coming too) or 'excessively/more than enough' (This coffee is too hot. You ate too much). In all other cases — preposition direction, infinitive verbs, phrases — use 'to'." }
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
        <span className="text-slate-900 dark:text-slate-100">To vs. Too vs. Two</span>
      </nav>

      <article className="max-w-4xl mx-auto bg-white p-8 md:p-12 rounded-xl shadow-lg shadow-slate-200/50 border border-slate-200 dark:bg-slate-800/50 dark:border-slate-700 dark:shadow-slate-900/50">
        <h1 className="font-heading text-4xl md:text-5xl font-extrabold text-slate-900 mb-6 tracking-tight dark:text-slate-100">
          To vs. Too vs. Two: What's the Difference?
        </h1>

        <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-r-lg mb-8 dark:bg-green-900/30 dark:border-green-400">
          <h2 className="text-xl font-bold text-green-900 dark:text-green-100 mb-2">Quick Answer</h2>
          <p className="text-lg text-green-800 dark:text-green-200 mb-1"><strong>to</strong> = preposition (go to) or infinitive marker (want to eat)</p>
          <p className="text-lg text-green-800 dark:text-green-200 mb-1"><strong>too</strong> = also / excessively (me too, too loud)</p>
          <p className="text-lg text-green-800 dark:text-green-200"><strong>two</strong> = the number 2</p>
        </div>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Explanation
          </h2>
          <div className="grid md:grid-cols-3 gap-4 mb-6">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <p className="font-bold text-blue-900 dark:text-blue-100 mb-2">TO</p>
              <p className="text-blue-800 dark:text-blue-200 mb-1 text-sm">1. Preposition of direction/purpose</p>
              <p className="text-blue-800 dark:text-blue-200 mb-2 text-sm">2. Infinitive marker (to + verb)</p>
              <p className="text-blue-700 dark:text-blue-300 italic text-sm">"Go <strong>to</strong> school."</p>
              <p className="text-blue-700 dark:text-blue-300 italic text-sm">"I want <strong>to</strong> sleep."</p>
              <p className="text-blue-700 dark:text-blue-300 italic text-sm">"from 9 <strong>to</strong> 5"</p>
            </div>
            <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
              <p className="font-bold text-purple-900 dark:text-purple-100 mb-2">TOO</p>
              <p className="text-purple-800 dark:text-purple-200 mb-1 text-sm">1. Also / as well</p>
              <p className="text-purple-800 dark:text-purple-200 mb-2 text-sm">2. Excessively / more than enough</p>
              <p className="text-purple-700 dark:text-purple-300 italic text-sm">"I want some <strong>too</strong>." (also)</p>
              <p className="text-purple-700 dark:text-purple-300 italic text-sm">"<strong>Too</strong> hot to drink." (excessive)</p>
              <p className="text-purple-700 dark:text-purple-300 italic text-sm">"<strong>Too</strong> much sugar."</p>
            </div>
            <div className="bg-orange-50 dark:bg-orange-900/20 p-4 rounded-lg">
              <p className="font-bold text-orange-900 dark:text-orange-100 mb-2">TWO</p>
              <p className="text-orange-800 dark:text-orange-200 mb-2 text-sm">The number 2 — always</p>
              <p className="text-orange-700 dark:text-orange-300 italic text-sm">"<strong>Two</strong> tickets please."</p>
              <p className="text-orange-700 dark:text-orange-300 italic text-sm">"<strong>Two</strong> hours later."</p>
              <p className="text-orange-700 dark:text-orange-300 italic text-sm">"one or <strong>two</strong> days"</p>
            </div>
          </div>
          <div className="bg-teal-50 dark:bg-teal-900/20 p-4 rounded-lg">
            <p className="text-lg text-teal-800 dark:text-teal-200">
              <strong>Memory tip:</strong> <strong>Too</strong> has an extra "o" because it means <em>extra</em> or <em>also</em>. <strong>Two</strong> starts with "tw" like "twelve" and "twenty" — numbers. When in doubt and it's not a number or "extra/also", use <strong>to</strong>.
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
              <span className="text-lg text-slate-700 dark:text-slate-300">I'm going <strong>to</strong> the gym. (preposition)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">She wants <strong>to</strong> become a doctor. (infinitive)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">Can I come <strong>too</strong>? (also)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">This bag is <strong>too</strong> heavy. (excessively)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">I need <strong>two</strong> more minutes. (number)</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">I want to go to, but its to far.</span>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Common Mistakes
          </h2>
          <div className="space-y-4">
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> This soup is to hot to eat.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> This soup is too hot to eat. (too = excessively)</p>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> I bought too books at the store.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> I bought two books at the store. (two = the number 2)</p>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Practice
          </h2>
          <div className="bg-teal-50 dark:bg-teal-900/20 p-6 rounded-lg">
            <p className="text-lg text-slate-700 dark:text-slate-300 mb-4">
              <strong>Fill in the blanks:</strong>
            </p>
            <p className="text-lg text-slate-800 dark:text-slate-200 italic mb-4">
              "I need _____ more days _____ finish the project. My colleague wants _____ help _____ ."
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
                  <strong>Answer:</strong> "I need <strong>two</strong> more days <strong>to</strong> finish... My colleague wants <strong>to</strong> help <strong>too</strong>."
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
            <li><Link to="/grammar-mistakes/there-vs-their-vs-theyre/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ There vs. Their vs. They're</Link></li>
            <li><Link to="/grammar-mistakes/its-vs-its/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Its vs. It's</Link></li>
            <li><Link to="/vocabulary/homophones-homonyms-homographs/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Homophones Guide</Link></li>
            <li><Link to="/grammar-mistakes/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ All Grammar Mistakes</Link></li>
          </ul>
        </section>
      </article>
    </>
  );
};

export default ToVsTooVsTwoPage;
