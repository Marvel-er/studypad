import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import usePageMetadata from '../../hooks/usePageMetadata';
import SchemaMarkup from '../../components/SchemaMarkup';

const WhoseVsWhosPage: React.FC = () => {
  usePageMetadata({
    title: "Whose vs. Who's: What's the Difference? | TypoGrammar",
    description: "Learn the difference between whose and who's. Whose is a possessive pronoun. Who's is a contraction of 'who is' or 'who has'. Examples, test, and practice.",
    canonical: 'https://typogrammar.com/grammar-mistakes/whose-vs-whos/'
  });

  const [showAnswer, setShowAnswer] = useState(false);

  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Whose vs. Who's: What's the Difference?",
    "description": "'Whose' is a possessive pronoun (Whose bag is this?). 'Who's' is a contraction of 'who is' or 'who has' (Who's coming? Who's been here?).",
    "author": { "@type": "Organization", "name": "TypoGrammar" },
    "publisher": { "@type": "Organization", "name": "TypoGrammar", "logo": { "@type": "ImageObject", "url": "https://typogrammar.com/logo.png" } },
    "mainEntityOfPage": { "@type": "WebPage", "@id": "https://typogrammar.com/grammar-mistakes/whose-vs-whos" },
    "datePublished": "2026-06-30",
    "dateModified": "2026-06-30"
  };

  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the difference between whose and who's?",
        "acceptedAnswer": { "@type": "Answer", "text": "'Whose' is a possessive pronoun meaning 'belonging to whom' (Whose phone is this? The student whose essay won the prize). 'Who's' is a contraction of 'who is' or 'who has' (Who's coming to the party? Who's been here?). To test: replace with 'who is' or 'who has'. If it makes sense, use who's." }
      },
      {
        "@type": "Question",
        "name": "Can 'whose' refer to things, not just people?",
        "acceptedAnswer": { "@type": "Answer", "text": "Yes! 'Whose' can refer to both people and things. Example: 'a company whose profits are rising' or 'a building whose roof was damaged'. It is the possessive form of both 'who' and 'which'." }
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
        <span className="text-slate-900 dark:text-slate-100">Whose vs. Who's</span>
      </nav>

      <article className="max-w-4xl mx-auto bg-white p-8 md:p-12 rounded-xl shadow-lg shadow-slate-200/50 border border-slate-200 dark:bg-slate-800/50 dark:border-slate-700 dark:shadow-slate-900/50">
        <h1 className="font-heading text-4xl md:text-5xl font-extrabold text-slate-900 mb-6 tracking-tight dark:text-slate-100">
          Whose vs. Who's: What's the Difference?
        </h1>

        <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-r-lg mb-8 dark:bg-green-900/30 dark:border-green-400">
          <h2 className="text-xl font-bold text-green-900 dark:text-green-100 mb-2">Quick Answer</h2>
          <p className="text-lg text-green-800 dark:text-green-200 mb-2">
            <strong>whose</strong> = possessive pronoun (belonging to whom)
          </p>
          <p className="text-lg text-green-800 dark:text-green-200">
            <strong>who's</strong> = contraction of "who is" or "who has"
          </p>
        </div>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Explanation
          </h2>
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <p className="font-bold text-blue-900 dark:text-blue-100 mb-2">WHOSE (possessive)</p>
              <p className="text-blue-800 dark:text-blue-200 mb-2">Asks about or shows ownership</p>
              <p className="text-blue-700 dark:text-blue-300 font-mono text-sm mb-2">Like: his, her, their, its</p>
              <p className="text-blue-700 dark:text-blue-300 italic mt-3">"<strong>Whose</strong> jacket is this?"</p>
              <p className="text-blue-700 dark:text-blue-300 italic">"The student <strong>whose</strong> essay won."</p>
              <p className="text-blue-700 dark:text-blue-300 italic">"A city <strong>whose</strong> history is rich."</p>
            </div>
            <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
              <p className="font-bold text-purple-900 dark:text-purple-100 mb-2">WHO'S (contraction)</p>
              <p className="text-purple-800 dark:text-purple-200 mb-2">Short for "who is" or "who has"</p>
              <p className="text-purple-700 dark:text-purple-300 font-mono text-sm mb-2">who's = who is / who has</p>
              <p className="text-purple-700 dark:text-purple-300 italic mt-3">"<strong>Who's</strong> at the door?" (who is)</p>
              <p className="text-purple-700 dark:text-purple-300 italic">"<strong>Who's</strong> been using my computer?" (who has)</p>
            </div>
          </div>
          <div className="bg-teal-50 dark:bg-teal-900/20 p-4 rounded-lg">
            <p className="text-lg text-teal-800 dark:text-teal-200">
              <strong>Quick test:</strong> Replace with "who is" or "who has". If it still makes sense → use <strong>who's</strong>. If not → use <strong>whose</strong>.
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
              <span className="text-lg text-slate-700 dark:text-slate-300"><strong>Whose</strong> keys are on the table? (possessive)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300"><strong>Who's</strong> coming to the meeting? (who is)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">The author <strong>whose</strong> books I love lives in London. (possessive)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300"><strong>Who's</strong> been eating my lunch? (who has)</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">Who's bag did you borrow?</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">Whose going to the party?</span>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Common Mistakes
          </h2>
          <div className="space-y-4">
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> I don't know who's book this is.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> I don't know whose book this is. (Test: "who is book" ✘ → use whose)</p>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> Whose responsible for this mistake?</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> Who's responsible for this mistake? (Test: "who is responsible" ✔ → use who's)</p>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Practice
          </h2>
          <div className="bg-teal-50 dark:bg-teal-900/20 p-6 rounded-lg">
            <p className="text-lg text-slate-700 dark:text-slate-300 mb-4">
              <strong>Fill in the blank:</strong>
            </p>
            <p className="text-lg text-slate-800 dark:text-slate-200 italic mb-4">
              "_____ the new manager? And _____ office is that?"
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
                  <strong>Answer:</strong> "<strong>Who's</strong> the new manager? And <strong>whose</strong> office is that?"
                </p>
                <p className="text-green-700 dark:text-green-300 mt-2">
                  Who's = who is (contraction). Whose = belonging to whom (possessive).
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
            <li><Link to="/grammar-mistakes/who-vs-whom/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Who vs. Whom</Link></li>
            <li><Link to="/grammar-mistakes/its-vs-its/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Its vs. It's</Link></li>
            <li><Link to="/grammar-mistakes/your-vs-youre/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Your vs. You're</Link></li>
            <li><Link to="/topics/apostrophes/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Apostrophes Guide</Link></li>
            <li><Link to="/grammar-mistakes/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ All Grammar Mistakes</Link></li>
          </ul>
        </section>
      </article>
    </>
  );
};

export default WhoseVsWhosPage;
