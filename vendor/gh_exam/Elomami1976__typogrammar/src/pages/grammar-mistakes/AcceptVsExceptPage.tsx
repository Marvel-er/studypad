import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import usePageMetadata from '../../hooks/usePageMetadata';
import SchemaMarkup from '../../components/SchemaMarkup';

const AcceptVsExceptPage: React.FC = () => {
  usePageMetadata({
    title: 'Accept vs. Except: What\'s the Difference? | TypoGrammar',
    description: 'Learn the difference between accept and except. Accept is a verb meaning to receive or agree to. Except is a preposition meaning excluding. Examples and practice.',
    canonical: 'https://typogrammar.com/grammar-mistakes/accept-vs-except/'
  });

  const [showAnswer, setShowAnswer] = useState(false);

  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Accept vs. Except: What's the Difference?",
    "description": "'Accept' is a verb meaning to receive, agree, or take something offered. 'Except' is a preposition or conjunction meaning excluding or but.",
    "author": { "@type": "Organization", "name": "TypoGrammar" },
    "publisher": { "@type": "Organization", "name": "TypoGrammar", "logo": { "@type": "ImageObject", "url": "https://typogrammar.com/logo.png" } },
    "mainEntityOfPage": { "@type": "WebPage", "@id": "https://typogrammar.com/grammar-mistakes/accept-vs-except" },
    "datePublished": "2026-06-30",
    "dateModified": "2026-06-30"
  };

  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the difference between accept and except?",
        "acceptedAnswer": { "@type": "Answer", "text": "'Accept' is a verb meaning to receive or agree to something (I accept your apology. She accepted the job offer.). 'Except' is a preposition or conjunction meaning excluding or apart from (Everyone passed except Tom. I eat everything except fish.)." }
      },
      {
        "@type": "Question",
        "name": "How do I remember accept vs. except?",
        "acceptedAnswer": { "@type": "Answer", "text": "Accept starts with 'ac' — think of ACknowledging or ACquiring something (you take it in). Except starts with 'ex' — think of EXcluding something (you leave it out). 'Ex' = out, like exit or exclude." }
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
        <span className="text-slate-900 dark:text-slate-100">Accept vs. Except</span>
      </nav>

      <article className="max-w-4xl mx-auto bg-white p-8 md:p-12 rounded-xl shadow-lg shadow-slate-200/50 border border-slate-200 dark:bg-slate-800/50 dark:border-slate-700 dark:shadow-slate-900/50">
        <h1 className="font-heading text-4xl md:text-5xl font-extrabold text-slate-900 mb-6 tracking-tight dark:text-slate-100">
          Accept vs. Except: What's the Difference?
        </h1>

        <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-r-lg mb-8 dark:bg-green-900/30 dark:border-green-400">
          <h2 className="text-xl font-bold text-green-900 dark:text-green-100 mb-2">Quick Answer</h2>
          <p className="text-lg text-green-800 dark:text-green-200 mb-2">
            <strong>accept</strong> = verb — to receive, agree to, or take something
          </p>
          <p className="text-lg text-green-800 dark:text-green-200">
            <strong>except</strong> = preposition/conjunction — excluding, apart from, but
          </p>
        </div>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Explanation
          </h2>
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <p className="font-bold text-blue-900 dark:text-blue-100 mb-2">ACCEPT (verb)</p>
              <p className="text-blue-800 dark:text-blue-200 mb-2">To receive, agree to, or approve</p>
              <p className="text-blue-700 dark:text-blue-300 font-mono text-sm mb-2">accept + object</p>
              <p className="text-blue-700 dark:text-blue-300 italic mt-3">"She <strong>accepted</strong> the invitation."</p>
              <p className="text-blue-700 dark:text-blue-300 italic">"Please <strong>accept</strong> my apology."</p>
              <p className="text-blue-700 dark:text-blue-300 italic">"He <strong>accepted</strong> the challenge."</p>
            </div>
            <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
              <p className="font-bold text-purple-900 dark:text-purple-100 mb-2">EXCEPT (preposition)</p>
              <p className="text-purple-800 dark:text-purple-200 mb-2">Excluding, apart from, but</p>
              <p className="text-purple-700 dark:text-purple-300 font-mono text-sm mb-2">everyone/all/everything + except + noun</p>
              <p className="text-purple-700 dark:text-purple-300 italic mt-3">"Everyone passed <strong>except</strong> Tom."</p>
              <p className="text-purple-700 dark:text-purple-300 italic">"I eat everything <strong>except</strong> fish."</p>
              <p className="text-purple-700 dark:text-purple-300 italic">"Open daily <strong>except</strong> Sundays."</p>
            </div>
          </div>
          <div className="bg-teal-50 dark:bg-teal-900/20 p-4 rounded-lg">
            <p className="text-lg text-teal-800 dark:text-teal-200">
              <strong>Memory trick:</strong> <strong>Acc</strong>ept = Acquire (you take it in). <strong>Ex</strong>cept = Exclude (you leave it out — like "exit" or "exclude").
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
              <span className="text-lg text-slate-700 dark:text-slate-300">I <strong>accept</strong> full responsibility. (verb)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">All students passed <strong>except</strong> one. (excluding)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">We <strong>accept</strong> cash and credit cards. (verb)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">The store is open every day <strong>except</strong> Monday. (excluding)</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">I can't except this kind of behaviour.</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">Everyone was invited accept John.</span>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Common Mistakes
          </h2>
          <div className="space-y-4">
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> Will you except my offer?</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> Will you accept my offer? (accept = verb, to agree to)</p>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> I like all vegetables accept broccoli.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> I like all vegetables except broccoli. (except = excluding)</p>
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
              "Everyone _____ Maria decided to _____ the new contract."
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
                  <strong>Answer:</strong> "Everyone <strong>except</strong> Maria decided to <strong>accept</strong> the new contract."
                </p>
                <p className="text-green-700 dark:text-green-300 mt-2">
                  Except = excluding Maria. Accept = to agree to / sign the contract.
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
            <li><Link to="/grammar-mistakes/advice-vs-advise/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Advice vs. Advise</Link></li>
            <li><Link to="/grammar-mistakes/lose-vs-loose/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Lose vs. Loose</Link></li>
            <li><Link to="/commonly-confused-words/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Commonly Confused Words</Link></li>
            <li><Link to="/grammar-mistakes/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ All Grammar Mistakes</Link></li>
          </ul>
        </section>
      </article>
    </>
  );
};

export default AcceptVsExceptPage;
