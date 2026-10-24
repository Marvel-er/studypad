import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import usePageMetadata from '../../hooks/usePageMetadata';
import SchemaMarkup from '../../components/SchemaMarkup';

const AffectVsEffectPage: React.FC = () => {
  usePageMetadata({
    title: 'Affect vs. Effect: What\'s the Difference? | TypoGrammar',
    description: 'Learn the difference between affect and effect. Affect is usually a verb meaning to influence. Effect is usually a noun meaning a result. Clear examples and practice.',
    canonical: 'https://typogrammar.com/grammar-mistakes/affect-vs-effect/'
  });

  const [showAnswer, setShowAnswer] = useState(false);

  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Affect vs. Effect: What's the Difference?",
    "description": "Affect is usually a verb meaning to influence or have an impact on. Effect is usually a noun meaning a result or outcome.",
    "author": { "@type": "Organization", "name": "TypoGrammar" },
    "publisher": { "@type": "Organization", "name": "TypoGrammar", "logo": { "@type": "ImageObject", "url": "https://typogrammar.com/logo.png" } },
    "mainEntityOfPage": { "@type": "WebPage", "@id": "https://typogrammar.com/grammar-mistakes/affect-vs-effect" },
    "datePublished": "2026-06-30",
    "dateModified": "2026-06-30"
  };

  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the difference between affect and effect?",
        "acceptedAnswer": { "@type": "Answer", "text": "'Affect' is usually a verb meaning to influence or have an impact on something (The weather affects my mood). 'Effect' is usually a noun meaning a result or consequence (The effect of the medicine was immediate). Remember: Affect = Action (verb); Effect = End result (noun)." }
      },
      {
        "@type": "Question",
        "name": "Can effect be a verb and affect be a noun?",
        "acceptedAnswer": { "@type": "Answer", "text": "Yes, but rarely. 'Effect' can be a verb meaning 'to bring about' (to effect change — meaning to cause change to happen). 'Affect' can be a noun in psychology meaning an emotional state. For most everyday writing, treat affect as a verb and effect as a noun." }
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
        <span className="text-slate-900 dark:text-slate-100">Affect vs. Effect</span>
      </nav>

      <article className="max-w-4xl mx-auto bg-white p-8 md:p-12 rounded-xl shadow-lg shadow-slate-200/50 border border-slate-200 dark:bg-slate-800/50 dark:border-slate-700 dark:shadow-slate-900/50">
        <h1 className="font-heading text-4xl md:text-5xl font-extrabold text-slate-900 mb-6 tracking-tight dark:text-slate-100">
          Affect vs. Effect: What's the Difference?
        </h1>

        <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-r-lg mb-8 dark:bg-green-900/30 dark:border-green-400">
          <h2 className="text-xl font-bold text-green-900 dark:text-green-100 mb-2">Quick Answer</h2>
          <p className="text-lg text-green-800 dark:text-green-200 mb-2">
            <strong>affect</strong> = verb (to influence something)
          </p>
          <p className="text-lg text-green-800 dark:text-green-200">
            <strong>effect</strong> = noun (a result or outcome)
          </p>
        </div>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Explanation
          </h2>
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <p className="font-bold text-blue-900 dark:text-blue-100 mb-2">AFFECT (verb)</p>
              <p className="text-blue-800 dark:text-blue-200 mb-2">To influence or have an impact on</p>
              <p className="text-blue-700 dark:text-blue-300 font-mono text-sm mb-2">subject + affect + object</p>
              <p className="text-blue-700 dark:text-blue-300 italic mt-3">"Stress <strong>affects</strong> your health."</p>
              <p className="text-blue-700 dark:text-blue-300 italic">"The cold weather <strong>affected</strong> the crops."</p>
            </div>
            <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
              <p className="font-bold text-purple-900 dark:text-purple-100 mb-2">EFFECT (noun)</p>
              <p className="text-purple-800 dark:text-purple-200 mb-2">A result, consequence, or outcome</p>
              <p className="text-purple-700 dark:text-purple-300 font-mono text-sm mb-2">the effect of / have an effect on</p>
              <p className="text-purple-700 dark:text-purple-300 italic mt-3">"The <strong>effect</strong> of stress on health is serious."</p>
              <p className="text-purple-700 dark:text-purple-300 italic">"The drug had no <strong>effect</strong>."</p>
            </div>
          </div>
          <div className="bg-teal-50 dark:bg-teal-900/20 p-4 rounded-lg mb-4">
            <p className="text-lg text-teal-800 dark:text-teal-200">
              <strong>Memory trick — RAVEN:</strong> Remember Affect Verb Effect Noun. Or: <strong>A</strong>ffect = <strong>A</strong>ction (verb) → <strong>E</strong>ffect = <strong>E</strong>nd result (noun).
            </p>
          </div>
          <div className="bg-slate-100 dark:bg-slate-700 p-4 rounded-lg">
            <p className="font-bold text-slate-800 dark:text-slate-200 mb-2">Common phrases with "effect":</p>
            <p className="text-slate-700 dark:text-slate-300">
              side effect, take effect, in effect, special effects, cause and effect, have an effect on
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
              <span className="text-lg text-slate-700 dark:text-slate-300">Lack of sleep can <strong>affect</strong> your concentration. (verb)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">The <strong>effect</strong> of the medication was noticeable. (noun)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">How does pollution <strong>affect</strong> marine life? (verb)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">The new law takes <strong>effect</strong> next month. (noun)</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">The medicine had a great affect.</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">How does the cold effect your body?</span>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Common Mistakes
          </h2>
          <div className="space-y-4">
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> Stress can effect your performance.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> Stress can affect your performance. (affect = verb)</p>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> The affect of the training was impressive.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> The effect of the training was impressive. (effect = noun, the result)</p>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Practice
          </h2>
          <div className="bg-teal-50 dark:bg-teal-900/20 p-6 rounded-lg">
            <p className="text-lg text-slate-700 dark:text-slate-300 mb-4">
              <strong>Fill in the blank with "affect" or "effect":</strong>
            </p>
            <p className="text-lg text-slate-800 dark:text-slate-200 italic mb-4">
              "The noise from the construction site _____ everyone's ability to concentrate. The _____ on productivity was significant."
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
                  <strong>Answer:</strong> "...construction site <strong>affected</strong> everyone's ability... The <strong>effect</strong> on productivity..."
                </p>
                <p className="text-green-700 dark:text-green-300 mt-2">
                  Affected = verb (influenced). Effect = noun (the result).
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
            <li><Link to="/grammar-mistakes/advice-vs-advise/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Advice vs. Advise</Link></li>
            <li><Link to="/grammar-mistakes/accept-vs-except/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Accept vs. Except</Link></li>
            <li><Link to="/grammar-mistakes/lose-vs-loose/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Lose vs. Loose</Link></li>
            <li><Link to="/commonly-confused-words/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Commonly Confused Words</Link></li>
            <li><Link to="/grammar-mistakes/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ All Grammar Mistakes</Link></li>
          </ul>
        </section>
      </article>
    </>
  );
};

export default AffectVsEffectPage;
