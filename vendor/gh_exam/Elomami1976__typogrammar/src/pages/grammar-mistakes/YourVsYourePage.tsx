import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import usePageMetadata from '../../hooks/usePageMetadata';
import SchemaMarkup from '../../components/SchemaMarkup';

const YourVsYourePage: React.FC = () => {
  usePageMetadata({
    title: "Your vs. You're: What's the Difference? | TypoGrammar",
    description: "Learn the difference between \"your\" and \"you're\". Your is a possessive pronoun. You're is a contraction of \"you are\". Clear examples and a quick test.",
    canonical: 'https://typogrammar.com/grammar-mistakes/your-vs-youre/'
  });

  const [showAnswer, setShowAnswer] = useState(false);

  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Your vs. You're: What's the Difference?",
    "description": "Your is a possessive pronoun (your book, your idea). You're is a contraction of 'you are' (you're right, you're welcome).",
    "author": { "@type": "Organization", "name": "TypoGrammar" },
    "publisher": { "@type": "Organization", "name": "TypoGrammar", "logo": { "@type": "ImageObject", "url": "https://typogrammar.com/logo.png" } },
    "mainEntityOfPage": { "@type": "WebPage", "@id": "https://typogrammar.com/grammar-mistakes/your-vs-youre" },
    "datePublished": "2026-06-30",
    "dateModified": "2026-06-30"
  };

  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the difference between your and you're?",
        "acceptedAnswer": { "@type": "Answer", "text": "'Your' is a possessive pronoun meaning 'belonging to you' (your book, your idea). 'You're' is a contraction of 'you are' (You're amazing. You're welcome.). To test: replace the word with 'you are'. If it makes sense, use 'you're'." }
      },
      {
        "@type": "Question",
        "name": "Is it 'your welcome' or 'you're welcome'?",
        "acceptedAnswer": { "@type": "Answer", "text": "The correct phrase is 'you're welcome' — a contraction of 'you are welcome'. 'Your welcome' is incorrect because 'your' is possessive and doesn't fit here." }
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
        <span className="text-slate-900 dark:text-slate-100">Your vs. You're</span>
      </nav>

      <article className="max-w-4xl mx-auto bg-white p-8 md:p-12 rounded-xl shadow-lg shadow-slate-200/50 border border-slate-200 dark:bg-slate-800/50 dark:border-slate-700 dark:shadow-slate-900/50">
        <h1 className="font-heading text-4xl md:text-5xl font-extrabold text-slate-900 mb-6 tracking-tight dark:text-slate-100">
          Your vs. You're: What's the Difference?
        </h1>

        <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-r-lg mb-8 dark:bg-green-900/30 dark:border-green-400">
          <h2 className="text-xl font-bold text-green-900 dark:text-green-100 mb-2">Quick Answer</h2>
          <p className="text-lg text-green-800 dark:text-green-200 mb-2">
            <strong>your</strong> = possessive pronoun (belonging to you)
          </p>
          <p className="text-lg text-green-800 dark:text-green-200">
            <strong>you're</strong> = contraction of "you are"
          </p>
        </div>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Explanation
          </h2>
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <p className="font-bold text-blue-900 dark:text-blue-100 mb-2">YOUR (no apostrophe)</p>
              <p className="text-blue-800 dark:text-blue-200 mb-2">Possessive pronoun — belonging to you</p>
              <p className="text-blue-700 dark:text-blue-300 font-mono text-sm mb-2">Like: my, his, her, our, their</p>
              <p className="text-blue-700 dark:text-blue-300 italic mt-3">"Is this <strong>your</strong> bag?"</p>
              <p className="text-blue-700 dark:text-blue-300 italic">"<strong>Your</strong> idea is brilliant."</p>
            </div>
            <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
              <p className="font-bold text-purple-900 dark:text-purple-100 mb-2">YOU'RE (with apostrophe)</p>
              <p className="text-purple-800 dark:text-purple-200 mb-2">Contraction of "you are"</p>
              <p className="text-purple-700 dark:text-purple-300 font-mono text-sm mb-2">you're = you are</p>
              <p className="text-purple-700 dark:text-purple-300 italic mt-3">"<strong>You're</strong> doing great!" (you are)</p>
              <p className="text-purple-700 dark:text-purple-300 italic">"<strong>You're</strong> welcome." (you are)</p>
            </div>
          </div>
          <div className="bg-teal-50 dark:bg-teal-900/20 p-4 rounded-lg">
            <p className="text-lg text-teal-800 dark:text-teal-200">
              <strong>Quick test:</strong> Replace the word with "you are". If the sentence still makes sense → use <strong>you're</strong>. If not → use <strong>your</strong>.
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
              <span className="text-lg text-slate-700 dark:text-slate-300">Is that <strong>your</strong> car? (possessive)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300"><strong>You're</strong> going to love this. (you are)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">I love <strong>your</strong> style. (possessive)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300"><strong>You're</strong> welcome. (you are welcome)</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">Your going to be late.</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">You're bag is on the table.</span>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Common Mistakes
          </h2>
          <div className="space-y-4">
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> Your the best teacher I've ever had.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> You're the best teacher I've ever had. (you are ✔)</p>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> I can't believe you're excuse.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> I can't believe your excuse. (possessive — "I can't believe you are excuse" ✘)</p>
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
              "_____ going to need _____ passport at the airport."
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
                  <strong>Answer:</strong> <strong>You're</strong> going to need <strong>your</strong> passport.
                </p>
                <p className="text-green-700 dark:text-green-300 mt-2">
                  "You're" = you are (contraction). "Your" = belonging to you (possessive).
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
            <li><Link to="/grammar-mistakes/its-vs-its/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Its vs. It's</Link></li>
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

export default YourVsYourePage;
