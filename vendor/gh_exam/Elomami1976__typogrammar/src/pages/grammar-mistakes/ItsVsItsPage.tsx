import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import usePageMetadata from '../../hooks/usePageMetadata';
import SchemaMarkup from '../../components/SchemaMarkup';

const ItsVsItsPage: React.FC = () => {
  usePageMetadata({
    title: "Its vs. It's: What's the Difference? | TypoGrammar",
    description: "Learn the difference between \"its\" and \"it's\". Its is a possessive pronoun. It's is a contraction of \"it is\" or \"it has\". Never confuse them again.",
    canonical: 'https://typogrammar.com/grammar-mistakes/its-vs-its/'
  });

  const [showAnswer, setShowAnswer] = useState(false);

  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Its vs. It's: What's the Difference?",
    "description": "Its is a possessive pronoun showing ownership. It's is a contraction of 'it is' or 'it has'. A simple apostrophe makes all the difference.",
    "author": { "@type": "Organization", "name": "TypoGrammar" },
    "publisher": { "@type": "Organization", "name": "TypoGrammar", "logo": { "@type": "ImageObject", "url": "https://typogrammar.com/logo.png" } },
    "mainEntityOfPage": { "@type": "WebPage", "@id": "https://typogrammar.com/grammar-mistakes/its-vs-its" },
    "datePublished": "2026-06-30",
    "dateModified": "2026-06-30"
  };

  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the difference between its and it's?",
        "acceptedAnswer": { "@type": "Answer", "text": "'Its' is a possessive pronoun meaning 'belonging to it' (The dog wagged its tail). 'It's' is a contraction of 'it is' or 'it has' (It's raining. It's been a long day.). The apostrophe in 'it's' always signals a contraction, never possession." }
      },
      {
        "@type": "Question",
        "name": "How do I know when to use its or it's?",
        "acceptedAnswer": { "@type": "Answer", "text": "Replace the word with 'it is' or 'it has'. If the sentence still makes sense, use 'it's'. If not, use 'its'. Example: 'It's [it is] raining' ✔. 'The cat licked it is paw' ✘ — so use 'its paw'." }
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
        <span className="text-slate-900 dark:text-slate-100">Its vs. It's</span>
      </nav>

      <article className="max-w-4xl mx-auto bg-white p-8 md:p-12 rounded-xl shadow-lg shadow-slate-200/50 border border-slate-200 dark:bg-slate-800/50 dark:border-slate-700 dark:shadow-slate-900/50">
        <h1 className="font-heading text-4xl md:text-5xl font-extrabold text-slate-900 mb-6 tracking-tight dark:text-slate-100">
          Its vs. It's: What's the Difference?
        </h1>

        <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-r-lg mb-8 dark:bg-green-900/30 dark:border-green-400">
          <h2 className="text-xl font-bold text-green-900 dark:text-green-100 mb-2">Quick Answer</h2>
          <p className="text-lg text-green-800 dark:text-green-200 mb-2">
            <strong>its</strong> = possessive pronoun (belonging to it) — no apostrophe
          </p>
          <p className="text-lg text-green-800 dark:text-green-200">
            <strong>it's</strong> = contraction of "it is" or "it has"
          </p>
        </div>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Explanation
          </h2>
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <p className="font-bold text-blue-900 dark:text-blue-100 mb-2">ITS (no apostrophe)</p>
              <p className="text-blue-800 dark:text-blue-200 mb-2">Possessive pronoun — shows ownership</p>
              <p className="text-blue-700 dark:text-blue-300 font-mono text-sm mb-2">Like: his, her, our, their</p>
              <p className="text-blue-700 dark:text-blue-300 italic mt-3">"The dog wagged <strong>its</strong> tail."</p>
              <p className="text-blue-700 dark:text-blue-300 italic">"The company lost <strong>its</strong> CEO."</p>
            </div>
            <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
              <p className="font-bold text-purple-900 dark:text-purple-100 mb-2">IT'S (with apostrophe)</p>
              <p className="text-purple-800 dark:text-purple-200 mb-2">Contraction of "it is" or "it has"</p>
              <p className="text-purple-700 dark:text-purple-300 font-mono text-sm mb-2">it's = it is / it has</p>
              <p className="text-purple-700 dark:text-purple-300 italic mt-3">"<strong>It's</strong> raining outside." (it is)</p>
              <p className="text-purple-700 dark:text-purple-300 italic">"<strong>It's</strong> been a great year." (it has)</p>
            </div>
          </div>
          <div className="bg-teal-50 dark:bg-teal-900/20 p-4 rounded-lg mb-4">
            <p className="text-lg text-teal-800 dark:text-teal-200">
              <strong>Quick test:</strong> Replace the word with "it is" or "it has". If the sentence still makes sense → use <strong>it's</strong>. If not → use <strong>its</strong>.
            </p>
          </div>
          <div className="bg-slate-100 dark:bg-slate-700 p-4 rounded-lg">
            <p className="font-bold text-slate-800 dark:text-slate-200 mb-2">Why no apostrophe for possession?</p>
            <p className="text-slate-700 dark:text-slate-300">
              Possessive pronouns (his, hers, ours, theirs, <strong>its</strong>) never use apostrophes. The apostrophe in "it's" always marks a missing letter — the "i" in "is" or the "ha" in "has".
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
              <span className="text-lg text-slate-700 dark:text-slate-300">The cat licked <strong>its</strong> paw. (possessive)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300"><strong>It's</strong> a beautiful day. (it is)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">The phone lost <strong>its</strong> charge. (possessive)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300"><strong>It's</strong> been three years. (it has)</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">The dog wagged it's tail.</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">Its a great idea.</span>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Common Mistakes
          </h2>
          <div className="space-y-4">
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> The team celebrated it's victory.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> The team celebrated its victory. (possessive — replace test: "the team celebrated it is victory" ✘)</p>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> Its getting late.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> It's getting late. (it is getting late ✔)</p>
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
              "The bird returned to _____ nest after the storm."
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
                  <strong>Answer:</strong> The bird returned to <strong>its</strong> nest.
                </p>
                <p className="text-green-700 dark:text-green-300 mt-2">
                  "Its" is correct — possessive. Test: "the bird returned to it is nest" ✘ → use its.
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
            <li><Link to="/grammar-mistakes/your-vs-youre/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Your vs. You're</Link></li>
            <li><Link to="/grammar-mistakes/whose-vs-whos/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Whose vs. Who's</Link></li>
            <li><Link to="/grammar-mistakes/there-vs-their-vs-theyre/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ There vs. Their vs. They're</Link></li>
            <li><Link to="/topics/apostrophes/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Apostrophes Guide</Link></li>
            <li><Link to="/grammar-mistakes/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ All Grammar Mistakes</Link></li>
          </ul>
        </section>
      </article>
    </>
  );
};

export default ItsVsItsPage;
