import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import usePageMetadata from '../../hooks/usePageMetadata';
import SchemaMarkup from '../../components/SchemaMarkup';

const OntoVsOnToPage: React.FC = () => {
  usePageMetadata({
    title: 'Onto vs. On To: What\'s the Difference? | TypoGrammar',
    description: 'Learn the difference between onto and on to. Onto is a preposition meaning movement to a surface. On to is two separate words used with phrasal verbs. Examples and practice.',
    canonical: 'https://typogrammar.com/grammar-mistakes/onto-vs-on-to/'
  });

  const [showAnswer, setShowAnswer] = useState(false);

  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Onto vs. On To: What's the Difference?",
    "description": "'Onto' (one word) is a preposition meaning movement to a position on a surface. 'On to' (two words) occurs when 'on' is part of a phrasal verb (move on, hold on) followed by 'to'.",
    "author": { "@type": "Organization", "name": "TypoGrammar" },
    "publisher": { "@type": "Organization", "name": "TypoGrammar", "logo": { "@type": "ImageObject", "url": "https://typogrammar.com/logo.png" } },
    "mainEntityOfPage": { "@type": "WebPage", "@id": "https://typogrammar.com/grammar-mistakes/onto-vs-on-to" },
    "datePublished": "2026-06-30",
    "dateModified": "2026-06-30"
  };

  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the difference between onto and on to?",
        "acceptedAnswer": { "@type": "Answer", "text": "'Onto' (one word) is a preposition showing movement to a position on top of or onto a surface (The cat jumped onto the table). 'On to' (two words) appears when 'on' belongs to a phrasal verb like 'move on', 'hold on', or 'log on', and 'to' is a separate preposition that follows it (Let's move on to the next topic. Hold on to the railing)." }
      },
      {
        "@type": "Question",
        "name": "How do I know whether to write onto as one word or two?",
        "acceptedAnswer": { "@type": "Answer", "text": "Test: if 'on' is part of a verb phrase (carry on, hang on, move on, log on) that could stand alone without 'to', write 'on to' as two words. If you're describing physical movement to a surface or position, and 'on' isn't part of a separate verb phrase, use 'onto' as one word." }
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
        <span className="text-slate-900 dark:text-slate-100">Onto vs. On To</span>
      </nav>

      <article className="max-w-4xl mx-auto bg-white p-8 md:p-12 rounded-xl shadow-lg shadow-slate-200/50 border border-slate-200 dark:bg-slate-800/50 dark:border-slate-700 dark:shadow-slate-900/50">
        <h1 className="font-heading text-4xl md:text-5xl font-extrabold text-slate-900 mb-6 tracking-tight dark:text-slate-100">
          Onto vs. On To: What's the Difference?
        </h1>

        <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-r-lg mb-8 dark:bg-green-900/30 dark:border-green-400">
          <h2 className="text-xl font-bold text-green-900 dark:text-green-100 mb-2">Quick Answer</h2>
          <p className="text-lg text-green-800 dark:text-green-200 mb-2">
            <strong>onto</strong> = preposition — movement to a position on a surface
          </p>
          <p className="text-lg text-green-800 dark:text-green-200">
            <strong>on to</strong> = "on" (part of a phrasal verb) + separate "to" (move on to, hold on to)
          </p>
        </div>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Explanation
          </h2>
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <p className="font-bold text-blue-900 dark:text-blue-100 mb-2">ONTO (one word)</p>
              <p className="text-blue-800 dark:text-blue-200 mb-2 text-sm">Preposition: movement to a surface/position</p>
              <p className="text-blue-700 dark:text-blue-300 italic text-sm">"The dog jumped <strong>onto</strong> the bed."</p>
              <p className="text-blue-700 dark:text-blue-300 italic text-sm">"She climbed <strong>onto</strong> the roof."</p>
            </div>
            <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
              <p className="font-bold text-purple-900 dark:text-purple-100 mb-2">ON TO (two words)</p>
              <p className="text-purple-800 dark:text-purple-200 mb-2 text-sm">"On" is part of a phrasal verb + "to"</p>
              <p className="text-purple-700 dark:text-purple-300 italic text-sm">"Let's move <strong>on to</strong> the next item." (move on)</p>
              <p className="text-purple-700 dark:text-purple-300 italic text-sm">"Hold <strong>on to</strong> your hat." (hold on)</p>
            </div>
          </div>
          <div className="bg-teal-50 dark:bg-teal-900/20 p-4 rounded-lg">
            <p className="text-lg text-teal-800 dark:text-teal-200">
              <strong>Quick test:</strong> Remove "to" — does the remaining phrase still make sense as a verb (move on, hold on, log on)? Write <strong>on to</strong>. Otherwise, if it's about physical movement onto a surface, write <strong>onto</strong>.
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
              <span className="text-lg text-slate-700 dark:text-slate-300">The ball rolled <strong>onto</strong> the field. (movement to a surface)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">Let's move <strong>on to</strong> question three. (move on + to)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">He stepped <strong>onto</strong> the stage. (movement to a surface)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">Please log <strong>on to</strong> the system. (log on + to)</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">We need to move onto the next topic.</span>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Common Mistakes
          </h2>
          <div className="space-y-4">
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> Hold onto your tickets until you reach the gate.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> Hold on to your tickets until you reach the gate. (hold on + to)</p>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> The cat leaped on to the windowsill.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> The cat leaped onto the windowsill. (movement to a surface)</p>
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
              "The kids climbed _____ the fence, then we moved _____ the next activity."
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
                  <strong>Answer:</strong> "The kids climbed <strong>onto</strong> the fence, then we moved <strong>on to</strong> the next activity."
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
            <li><Link to="/grammar-mistakes/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ All Grammar Mistakes</Link></li>
          </ul>
        </section>
      </article>
    </>
  );
};

export default OntoVsOnToPage;
