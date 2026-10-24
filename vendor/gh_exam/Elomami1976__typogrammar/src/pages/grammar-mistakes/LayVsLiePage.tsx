import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import usePageMetadata from '../../hooks/usePageMetadata';
import SchemaMarkup from '../../components/SchemaMarkup';

const LayVsLiePage: React.FC = () => {
  usePageMetadata({
    title: 'Lay vs. Lie: What\'s the Difference? | TypoGrammar',
    description: 'Learn the difference between lay and lie. Lay is transitive (needs an object). Lie is intransitive (no object). Includes confusing past tenses explained clearly.',
    canonical: 'https://typogrammar.com/grammar-mistakes/lay-vs-lie/'
  });

  const [showAnswer, setShowAnswer] = useState(false);

  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Lay vs. Lie: What's the Difference?",
    "description": "'Lay' means to place something down (transitive — needs an object). 'Lie' means to recline or be in a horizontal position (intransitive — no object). The confusion grows because the past tense of 'lie' is 'lay'.",
    "author": { "@type": "Organization", "name": "TypoGrammar" },
    "publisher": { "@type": "Organization", "name": "TypoGrammar", "logo": { "@type": "ImageObject", "url": "https://typogrammar.com/logo.png" } },
    "mainEntityOfPage": { "@type": "WebPage", "@id": "https://typogrammar.com/grammar-mistakes/lay-vs-lie" },
    "datePublished": "2026-06-30",
    "dateModified": "2026-06-30"
  };

  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the difference between lay and lie?",
        "acceptedAnswer": { "@type": "Answer", "text": "'Lay' is a transitive verb — it needs an object (lay the book down, lay the table). 'Lie' is intransitive — it does not take an object (lie down, lie on the sofa). The trickiest part: the past tense of 'lie' is 'lay' (Yesterday I lay on the beach), while the past tense of 'lay' is 'laid' (She laid the book on the table)." }
      },
      {
        "@type": "Question",
        "name": "Is it 'lay down' or 'lie down'?",
        "acceptedAnswer": { "@type": "Answer", "text": "When you mean to recline yourself, the correct phrase is 'lie down' (Go lie down if you're tired). 'Lay down' would need an object — for example, 'Lay down your weapons' (put them down). In casual speech 'lay down' is commonly used for both, but in formal writing use 'lie down' when no object follows." }
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
        <span className="text-slate-900 dark:text-slate-100">Lay vs. Lie</span>
      </nav>

      <article className="max-w-4xl mx-auto bg-white p-8 md:p-12 rounded-xl shadow-lg shadow-slate-200/50 border border-slate-200 dark:bg-slate-800/50 dark:border-slate-700 dark:shadow-slate-900/50">
        <h1 className="font-heading text-4xl md:text-5xl font-extrabold text-slate-900 mb-6 tracking-tight dark:text-slate-100">
          Lay vs. Lie: What's the Difference?
        </h1>

        <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-r-lg mb-8 dark:bg-green-900/30 dark:border-green-400">
          <h2 className="text-xl font-bold text-green-900 dark:text-green-100 mb-2">Quick Answer</h2>
          <p className="text-lg text-green-800 dark:text-green-200 mb-2">
            <strong>lay</strong> = to place something (transitive — always needs an object)
          </p>
          <p className="text-lg text-green-800 dark:text-green-200">
            <strong>lie</strong> = to recline / be horizontal (intransitive — no object)
          </p>
        </div>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Explanation
          </h2>
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <p className="font-bold text-blue-900 dark:text-blue-100 mb-2">LAY (transitive)</p>
              <p className="text-blue-800 dark:text-blue-200 mb-1 text-sm">To put/place something somewhere</p>
              <p className="text-blue-700 dark:text-blue-300 text-sm mb-2">Always needs an object after it</p>
              <div className="bg-blue-100 dark:bg-blue-800/30 rounded p-2 text-sm mb-2">
                <p className="text-blue-800 dark:text-blue-200 font-mono">Present: lay</p>
                <p className="text-blue-800 dark:text-blue-200 font-mono">Past: laid</p>
                <p className="text-blue-800 dark:text-blue-200 font-mono">Past participle: laid</p>
              </div>
              <p className="text-blue-700 dark:text-blue-300 italic text-sm">"<strong>Lay</strong> the book on the table."</p>
              <p className="text-blue-700 dark:text-blue-300 italic text-sm">"She <strong>laid</strong> her coat on the chair."</p>
            </div>
            <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
              <p className="font-bold text-purple-900 dark:text-purple-100 mb-2">LIE (intransitive)</p>
              <p className="text-purple-800 dark:text-purple-200 mb-1 text-sm">To recline or be in a flat position</p>
              <p className="text-purple-700 dark:text-purple-300 text-sm mb-2">No object needed after it</p>
              <div className="bg-purple-100 dark:bg-purple-800/30 rounded p-2 text-sm mb-2">
                <p className="text-purple-800 dark:text-purple-200 font-mono">Present: lie</p>
                <p className="text-purple-800 dark:text-purple-200 font-mono">Past: lay ← (confusing!)</p>
                <p className="text-purple-800 dark:text-purple-200 font-mono">Past participle: lain</p>
              </div>
              <p className="text-purple-700 dark:text-purple-300 italic text-sm">"<strong>Lie</strong> down and rest."</p>
              <p className="text-purple-700 dark:text-purple-300 italic text-sm">"Yesterday I <strong>lay</strong> on the sofa."</p>
            </div>
          </div>
          <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg mb-4">
            <p className="font-bold text-yellow-900 dark:text-yellow-100 mb-2">⚠ The Tricky Part: Past Tenses</p>
            <p className="text-yellow-800 dark:text-yellow-200">
              The past tense of <strong>lie</strong> is <strong>lay</strong> — the same word as the present tense of <em>lay</em>. This is what causes most confusion.
            </p>
            <ul className="mt-2 space-y-1 text-yellow-800 dark:text-yellow-200 text-sm">
              <li>"I <strong>lie</strong> down every afternoon." → "Yesterday I <strong>lay</strong> down for an hour."</li>
              <li>"Please <strong>lay</strong> the table." → "She <strong>laid</strong> the table for six people."</li>
            </ul>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Examples
          </h2>
          <div className="space-y-3">
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300"><strong>Lay</strong> your phone on the desk. (place it — transitive)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">I need to <strong>lie</strong> down — I have a headache. (recline — intransitive)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">The cat <strong>lay</strong> in the sun all afternoon. (past tense of lie)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">She <strong>laid</strong> the baby in the crib. (past tense of lay)</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">I'm going to lay down for a nap.</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">Please lie the towel on the chair.</span>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Common Mistakes
          </h2>
          <div className="space-y-4">
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> The dog is laying on the couch.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> The dog is lying on the couch. (lie = recline, no object)</p>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> He lied the book on the shelf.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> He laid the book on the shelf. (past tense of lay)</p>
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
              "She was so tired that she _____ down on the sofa and _____ her head on a pillow."
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
                  <strong>Answer:</strong> "She...she <strong>lay</strong> down on the sofa and <strong>laid</strong> her head on a pillow."
                </p>
                <p className="text-green-700 dark:text-green-300 mt-2">
                  "Lay" = past tense of "lie" (she reclined). "Laid" = past tense of "lay" (she placed her head).
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
            <li><Link to="/irregular-verbs/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Irregular Verbs List</Link></li>
            <li><Link to="/grammar-mistakes/lead-vs-led/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Lead vs. Led</Link></li>
            <li><Link to="/grammar-mistakes/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ All Grammar Mistakes</Link></li>
          </ul>
        </section>
      </article>
    </>
  );
};

export default LayVsLiePage;
