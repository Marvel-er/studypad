import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import usePageMetadata from '../../hooks/usePageMetadata';
import SchemaMarkup from '../../components/SchemaMarkup';

const WhoVsWhomPage: React.FC = () => {
  usePageMetadata({
    title: 'Who vs. Whom: What\'s the Difference? | TypoGrammar',
    description: 'Learn when to use who vs. whom. Who is a subject pronoun. Whom is an object pronoun. Use the he/him substitution test to decide. Clear examples and practice.',
    canonical: 'https://typogrammar.com/grammar-mistakes/who-vs-whom/'
  });

  const [showAnswer, setShowAnswer] = useState(false);

  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Who vs. Whom: What's the Difference?",
    "description": "'Who' is a subject pronoun (like he/she). 'Whom' is an object pronoun (like him/her). Use the he/him substitution test to decide which to use.",
    "author": { "@type": "Organization", "name": "TypoGrammar" },
    "publisher": { "@type": "Organization", "name": "TypoGrammar", "logo": { "@type": "ImageObject", "url": "https://typogrammar.com/logo.png" } },
    "mainEntityOfPage": { "@type": "WebPage", "@id": "https://typogrammar.com/grammar-mistakes/who-vs-whom" },
    "datePublished": "2026-06-30",
    "dateModified": "2026-06-30"
  };

  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "When should I use who vs. whom?",
        "acceptedAnswer": { "@type": "Answer", "text": "Use 'who' when it is the subject of the verb (Who called you? = He called you → use who). Use 'whom' when it is the object of a verb or preposition (Whom did you call? = You called him → use whom). The trick: if you can answer with 'he/she', use who; if you can answer with 'him/her', use whom." }
      },
      {
        "@type": "Question",
        "name": "Is 'To whom it may concern' correct?",
        "acceptedAnswer": { "@type": "Answer", "text": "Yes, 'To whom it may concern' is correct. 'Whom' follows the preposition 'to', so the object form is required. This is the standard formal opening for a letter addressed to an unknown recipient." }
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
        <span className="text-slate-900 dark:text-slate-100">Who vs. Whom</span>
      </nav>

      <article className="max-w-4xl mx-auto bg-white p-8 md:p-12 rounded-xl shadow-lg shadow-slate-200/50 border border-slate-200 dark:bg-slate-800/50 dark:border-slate-700 dark:shadow-slate-900/50">
        <h1 className="font-heading text-4xl md:text-5xl font-extrabold text-slate-900 mb-6 tracking-tight dark:text-slate-100">
          Who vs. Whom: What's the Difference?
        </h1>

        <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-r-lg mb-8 dark:bg-green-900/30 dark:border-green-400">
          <h2 className="text-xl font-bold text-green-900 dark:text-green-100 mb-2">Quick Answer</h2>
          <p className="text-lg text-green-800 dark:text-green-200 mb-2">
            <strong>who</strong> = subject pronoun (like he/she) — performs the action
          </p>
          <p className="text-lg text-green-800 dark:text-green-200">
            <strong>whom</strong> = object pronoun (like him/her) — receives the action
          </p>
        </div>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Explanation
          </h2>
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <p className="font-bold text-blue-900 dark:text-blue-100 mb-2">WHO (subject)</p>
              <p className="text-blue-800 dark:text-blue-200 mb-2">The one who performs the action</p>
              <p className="text-blue-700 dark:text-blue-300 font-mono text-sm mb-2">Replace with: he / she</p>
              <p className="text-blue-700 dark:text-blue-300 italic mt-3">"<strong>Who</strong> called?" → He called. ✔</p>
              <p className="text-blue-700 dark:text-blue-300 italic">"The man <strong>who</strong> helped me." → He helped me. ✔</p>
            </div>
            <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
              <p className="font-bold text-purple-900 dark:text-purple-100 mb-2">WHOM (object)</p>
              <p className="text-purple-800 dark:text-purple-200 mb-2">The one who receives the action / after a preposition</p>
              <p className="text-purple-700 dark:text-purple-300 font-mono text-sm mb-2">Replace with: him / her</p>
              <p className="text-purple-700 dark:text-purple-300 italic mt-3">"<strong>Whom</strong> did you call?" → I called him. ✔</p>
              <p className="text-purple-700 dark:text-purple-300 italic">"To <strong>whom</strong> did you speak?" → I spoke to her. ✔</p>
            </div>
          </div>
          <div className="bg-teal-50 dark:bg-teal-900/20 p-4 rounded-lg mb-4">
            <p className="text-lg text-teal-800 dark:text-teal-200">
              <strong>The He/Him Test:</strong> Answer the question with he/him. If "he" fits → use <strong>who</strong>. If "him" fits → use <strong>whom</strong>. (Both end in "m" — whom/him!)
            </p>
          </div>
          <div className="bg-slate-100 dark:bg-slate-700 p-4 rounded-lg">
            <p className="font-bold text-slate-800 dark:text-slate-200 mb-2">Always use "whom" after prepositions:</p>
            <p className="text-slate-700 dark:text-slate-300">
              to whom, for whom, with whom, from whom, about whom, by whom
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
              <span className="text-lg text-slate-700 dark:text-slate-300"><strong>Who</strong> wrote this report? (subject — he/she wrote it)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300"><strong>Whom</strong> should I contact? (object — I should contact him/her)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">She is the one <strong>who</strong> solved the problem. (subject)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">To <strong>whom</strong> it may concern. (after preposition "to")</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">Whom called you last night?</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">Who did you invite to the party?</span>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Common Mistakes
          </h2>
          <div className="space-y-4">
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> Who did the manager hire?</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> Whom did the manager hire? (Test: The manager hired him. → him → whom ✔)</p>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> The teacher whom teaches math is kind.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> The teacher who teaches math is kind. (Test: She teaches math. → she → who ✔)</p>
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
              "_____ is responsible for this project? And with _____ should I discuss the budget?"
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
                  <strong>Answer:</strong> "<strong>Who</strong> is responsible... And with <strong>whom</strong> should I discuss..."
                </p>
                <p className="text-green-700 dark:text-green-300 mt-2">
                  Who = subject (he is responsible). Whom = after preposition "with" (with him).
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
            <li><Link to="/grammar-mistakes/whose-vs-whos/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Whose vs. Who's</Link></li>
            <li><Link to="/topics/relative-clauses/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Relative Clauses</Link></li>
            <li><Link to="/grammar-mistakes/its-vs-its/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Its vs. It's</Link></li>
            <li><Link to="/grammar-mistakes/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ All Grammar Mistakes</Link></li>
          </ul>
        </section>
      </article>
    </>
  );
};

export default WhoVsWhomPage;
