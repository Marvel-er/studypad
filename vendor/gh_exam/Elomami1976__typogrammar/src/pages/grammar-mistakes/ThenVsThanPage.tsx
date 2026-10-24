import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import usePageMetadata from '../../hooks/usePageMetadata';
import SchemaMarkup from '../../components/SchemaMarkup';

const ThenVsThanPage: React.FC = () => {
  usePageMetadata({
    title: 'Then vs. Than: What\'s the Difference? | TypoGrammar',
    description: 'Learn the difference between then and than. Then relates to time or sequence. Than is used for comparisons. Simple rules, examples, and practice.',
    canonical: 'https://typogrammar.com/grammar-mistakes/then-vs-than/'
  });

  const [showAnswer, setShowAnswer] = useState(false);

  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Then vs. Than: What's the Difference?",
    "description": "'Then' refers to time or sequence (first do this, then do that). 'Than' is used for comparisons (better than, more than).",
    "author": { "@type": "Organization", "name": "TypoGrammar" },
    "publisher": { "@type": "Organization", "name": "TypoGrammar", "logo": { "@type": "ImageObject", "url": "https://typogrammar.com/logo.png" } },
    "mainEntityOfPage": { "@type": "WebPage", "@id": "https://typogrammar.com/grammar-mistakes/then-vs-than" },
    "datePublished": "2026-06-30",
    "dateModified": "2026-06-30"
  };

  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the difference between then and than?",
        "acceptedAnswer": { "@type": "Answer", "text": "'Then' relates to time or sequence: it can mean 'at that time' (Back then, life was simpler), 'next' (First mix the ingredients, then bake), or 'in that case' (If you're tired, then rest). 'Than' is used for comparisons: 'She is taller than her brother. I'd rather sleep than watch TV.'" }
      },
      {
        "@type": "Question",
        "name": "Is it 'better then' or 'better than'?",
        "acceptedAnswer": { "@type": "Answer", "text": "The correct phrase is 'better than' — using 'than' for comparison. 'Better then' would mean 'better at that time', which is a different meaning. Whenever you are comparing two things, use 'than'." }
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
        <span className="text-slate-900 dark:text-slate-100">Then vs. Than</span>
      </nav>

      <article className="max-w-4xl mx-auto bg-white p-8 md:p-12 rounded-xl shadow-lg shadow-slate-200/50 border border-slate-200 dark:bg-slate-800/50 dark:border-slate-700 dark:shadow-slate-900/50">
        <h1 className="font-heading text-4xl md:text-5xl font-extrabold text-slate-900 mb-6 tracking-tight dark:text-slate-100">
          Then vs. Than: What's the Difference?
        </h1>

        <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-r-lg mb-8 dark:bg-green-900/30 dark:border-green-400">
          <h2 className="text-xl font-bold text-green-900 dark:text-green-100 mb-2">Quick Answer</h2>
          <p className="text-lg text-green-800 dark:text-green-200 mb-2">
            <strong>then</strong> = time, sequence, or consequence (first… then; back then; if… then)
          </p>
          <p className="text-lg text-green-800 dark:text-green-200">
            <strong>than</strong> = comparison (better than, more than, rather than)
          </p>
        </div>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Explanation
          </h2>
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <p className="font-bold text-blue-900 dark:text-blue-100 mb-2">THEN (time/sequence)</p>
              <p className="text-blue-800 dark:text-blue-200 mb-1 text-sm">1. At that time: "Back then, things were different."</p>
              <p className="text-blue-800 dark:text-blue-200 mb-1 text-sm">2. Next/after: "First stir, then bake."</p>
              <p className="text-blue-800 dark:text-blue-200 mb-2 text-sm">3. In that case: "If you're tired, then rest."</p>
              <p className="text-blue-600 dark:text-blue-400 text-xs">Tip: "then" contains "when" — both relate to time.</p>
            </div>
            <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
              <p className="font-bold text-purple-900 dark:text-purple-100 mb-2">THAN (comparison)</p>
              <p className="text-purple-800 dark:text-purple-200 mb-2 text-sm">Used after comparatives (better, more, less, faster, etc.)</p>
              <p className="text-purple-700 dark:text-purple-300 italic text-sm">"She runs faster <strong>than</strong> I do."</p>
              <p className="text-purple-700 dark:text-purple-300 italic text-sm">"I'd rather read <strong>than</strong> watch TV."</p>
              <p className="text-purple-700 dark:text-purple-300 italic text-sm">"More <strong>than</strong> 100 people attended."</p>
            </div>
          </div>
          <div className="bg-teal-50 dark:bg-teal-900/20 p-4 rounded-lg">
            <p className="text-lg text-teal-800 dark:text-teal-200">
              <strong>Quick test:</strong> Are you comparing two things? → use <strong>than</strong>. Are you talking about time or order? → use <strong>then</strong>.
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
              <span className="text-lg text-slate-700 dark:text-slate-300">This book is better <strong>than</strong> the movie. (comparison)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">First finish your homework, <strong>then</strong> you can play. (sequence)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">He was younger <strong>than</strong> she expected. (comparison)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">If you see her, <strong>then</strong> please say hello. (consequence)</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">She is taller then her sister.</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">First wash your hands, than eat.</span>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Common Mistakes
          </h2>
          <div className="space-y-4">
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> I'd rather stay home then go out.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> I'd rather stay home than go out. (comparison of preferences)</p>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> We arrived late, than we missed the bus.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> We arrived late, then we missed the bus. (sequence of events)</p>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Practice
          </h2>
          <div className="bg-teal-50 dark:bg-teal-900/20 p-6 rounded-lg">
            <p className="text-lg text-slate-700 dark:text-slate-300 mb-4">
              <strong>Fill in the blank with "then" or "than":</strong>
            </p>
            <p className="text-lg text-slate-800 dark:text-slate-200 italic mb-4">
              "Coffee is more popular _____ tea in this country. Drink it first, _____ start your work."
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
                  <strong>Answer:</strong> "...more popular <strong>than</strong> tea... Drink it first, <strong>then</strong> start..."
                </p>
                <p className="text-green-700 dark:text-green-300 mt-2">
                  "Than" = comparison. "Then" = sequence (next).
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
            <li><Link to="/grammar-mistakes/lose-vs-loose/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Lose vs. Loose</Link></li>
            <li><Link to="/grammar-mistakes/passed-vs-past/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Passed vs. Past</Link></li>
            <li><Link to="/grammar-mistakes/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ All Grammar Mistakes</Link></li>
          </ul>
        </section>
      </article>
    </>
  );
};

export default ThenVsThanPage;
