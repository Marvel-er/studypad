import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import usePageMetadata from '../../hooks/usePageMetadata';
import SchemaMarkup from '../../components/SchemaMarkup';

const IfIWasVsIfIWerePage: React.FC = () => {
  usePageMetadata({
    title: 'If I Was vs. If I Were: What\'s the Difference? | TypoGrammar',
    description: 'Learn the difference between if I was and if I were. "If I was" describes real past situations. "If I were" uses the subjunctive mood for hypotheticals. Examples and practice.',
    canonical: 'https://typogrammar.com/grammar-mistakes/if-i-was-vs-if-i-were/'
  });

  const [showAnswer, setShowAnswer] = useState(false);

  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "If I Was vs. If I Were: What's the Difference?",
    "description": "'If I was' is used for real, possible past situations. 'If I were' uses the subjunctive mood for hypothetical, unreal, or wishful situations — including the famous 'If I were you' construction.",
    "author": { "@type": "Organization", "name": "TypoGrammar" },
    "publisher": { "@type": "Organization", "name": "TypoGrammar", "logo": { "@type": "ImageObject", "url": "https://typogrammar.com/logo.png" } },
    "mainEntityOfPage": { "@type": "WebPage", "@id": "https://typogrammar.com/grammar-mistakes/if-i-was-vs-if-i-were" },
    "datePublished": "2026-06-30",
    "dateModified": "2026-06-30"
  };

  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the difference between if I was and if I were?",
        "acceptedAnswer": { "@type": "Answer", "text": "'If I was' describes a real, possible situation in the past where you genuinely don't know the outcome (If I was rude yesterday, I apologize). 'If I were' uses the subjunctive mood for hypothetical, imaginary, or contrary-to-fact situations (If I were rich, I'd travel the world. If I were you, I'd accept the offer)." }
      },
      {
        "@type": "Question",
        "name": "Why do we say 'if I were' instead of 'if I was' for hypotheticals?",
        "acceptedAnswer": { "@type": "Answer", "text": "English uses a special subjunctive mood to mark situations that are imaginary, impossible, or contrary to fact. In the subjunctive, 'were' is used for all subjects (I, he, she, it) instead of 'was'. This is why we say 'If I were a bird' and 'If she were taller', even though normally we'd say 'I was' and 'she was'." }
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
        <span className="text-slate-900 dark:text-slate-100">If I Was vs. If I Were</span>
      </nav>

      <article className="max-w-4xl mx-auto bg-white p-8 md:p-12 rounded-xl shadow-lg shadow-slate-200/50 border border-slate-200 dark:bg-slate-800/50 dark:border-slate-700 dark:shadow-slate-900/50">
        <h1 className="font-heading text-4xl md:text-5xl font-extrabold text-slate-900 mb-6 tracking-tight dark:text-slate-100">
          If I Was vs. If I Were: What's the Difference?
        </h1>

        <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-r-lg mb-8 dark:bg-green-900/30 dark:border-green-400">
          <h2 className="text-xl font-bold text-green-900 dark:text-green-100 mb-2">Quick Answer</h2>
          <p className="text-lg text-green-800 dark:text-green-200 mb-2">
            <strong>if I was</strong> = real, possible past situations
          </p>
          <p className="text-lg text-green-800 dark:text-green-200">
            <strong>if I were</strong> = subjunctive mood — hypothetical, unreal, or wishful situations
          </p>
        </div>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Explanation
          </h2>
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <p className="font-bold text-blue-900 dark:text-blue-100 mb-2">IF I WAS (real/possible)</p>
              <p className="text-blue-800 dark:text-blue-200 mb-2 text-sm">Describes a genuine past possibility, not known to be false</p>
              <p className="text-blue-700 dark:text-blue-300 italic text-sm">"<strong>If I was</strong> rude, I'm sorry." (maybe I was)</p>
              <p className="text-blue-700 dark:text-blue-300 italic text-sm">"<strong>If I was</strong> late, it wasn't intentional."</p>
            </div>
            <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
              <p className="font-bold text-purple-900 dark:text-purple-100 mb-2">IF I WERE (subjunctive)</p>
              <p className="text-purple-800 dark:text-purple-200 mb-2 text-sm">Hypothetical, imaginary, or contrary-to-fact</p>
              <p className="text-purple-700 dark:text-purple-300 italic text-sm">"<strong>If I were</strong> you, I'd quit." (I am not you)</p>
              <p className="text-purple-700 dark:text-purple-300 italic text-sm">"<strong>If I were</strong> rich, I'd travel." (I'm not rich)</p>
            </div>
          </div>
          <div className="bg-teal-50 dark:bg-teal-900/20 p-4 rounded-lg">
            <p className="text-lg text-teal-800 dark:text-teal-200">
              <strong>Quick test:</strong> Is the situation impossible or clearly untrue right now (a wish, advice, a fantasy)? Use <strong>were</strong>. Is it a real, uncertain possibility — especially about the past? Use <strong>was</strong>.
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
              <span className="text-lg text-slate-700 dark:text-slate-300"><strong>If I were</strong> a millionaire, I'd buy a yacht. (hypothetical)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300"><strong>If I was</strong> asleep when you called, I didn't hear it. (real possibility)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300"><strong>If I were</strong> you, I would apologize. (advice, subjunctive)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">She asked <strong>if I was</strong> coming to the party. (reported question, real)</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">If I was a bird, I would fly away.</span>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Common Mistakes
          </h2>
          <div className="space-y-4">
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> If I was you, I would take the job.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> If I were you, I would take the job. (hypothetical — you can never literally be "you")</p>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> If I were late this morning, I apologize.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> If I was late this morning, I apologize. (real, uncertain possibility)</p>
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
              "If I _____ taller, I would play basketball. If I _____ rude during the call, please forgive me."
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
                  <strong>Answer:</strong> "If I <strong>were</strong> taller, I would play basketball. If I <strong>was</strong> rude during the call, please forgive me."
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
            <li><Link to="/grammar-mistakes/then-vs-than/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Then vs. Than</Link></li>
            <li><Link to="/conditionals/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Conditional Sentences Guide</Link></li>
            <li><Link to="/grammar-mistakes/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ All Grammar Mistakes</Link></li>
          </ul>
        </section>
      </article>
    </>
  );
};

export default IfIWasVsIfIWerePage;
