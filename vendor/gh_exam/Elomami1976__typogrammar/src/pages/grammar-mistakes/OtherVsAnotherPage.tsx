import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import usePageMetadata from '../../hooks/usePageMetadata';
import SchemaMarkup from '../../components/SchemaMarkup';

const OtherVsAnotherPage: React.FC = () => {
  usePageMetadata({
    title: 'Other vs. Another: What\'s the Difference? | TypoGrammar',
    description: 'Learn the difference between other and another. Other is used with plurals or "the". Another means "one more" or "a different one" and is always singular. Examples and practice.',
    canonical: 'https://typogrammar.com/grammar-mistakes/other-vs-another/'
  });

  const [showAnswer, setShowAnswer] = useState(false);

  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Other vs. Another: What's the Difference?",
    "description": "'Other' is an adjective/pronoun used with plural nouns or 'the' (the other one, other people). 'Another' is always singular, meaning 'one more' or 'a different one' (an + other).",
    "author": { "@type": "Organization", "name": "TypoGrammar" },
    "publisher": { "@type": "Organization", "name": "TypoGrammar", "logo": { "@type": "ImageObject", "url": "https://typogrammar.com/logo.png" } },
    "mainEntityOfPage": { "@type": "WebPage", "@id": "https://typogrammar.com/grammar-mistakes/other-vs-another" },
    "datePublished": "2026-06-30",
    "dateModified": "2026-06-30"
  };

  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the difference between other and another?",
        "acceptedAnswer": { "@type": "Answer", "text": "'Another' (literally 'an' + 'other') is always singular, meaning 'one more' or 'a different one' (Can I have another cookie? Let's try another approach). 'Other' is used with plural nouns (other people, other options) or with 'the' for a specific singular item (the other shoe, the other side)." }
      },
      {
        "@type": "Question",
        "name": "Why can't I say 'an other' or use 'another' with plurals?",
        "acceptedAnswer": { "@type": "Answer", "text": "'Another' is already a fusion of 'an' + 'other', so writing 'an other' as two words is incorrect and redundant — just use 'another'. And because 'another' contains the singular article 'an', it can never be used with plural nouns; you cannot say 'another cookies' — use 'other cookies' or 'more cookies' instead." }
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
        <span className="text-slate-900 dark:text-slate-100">Other vs. Another</span>
      </nav>

      <article className="max-w-4xl mx-auto bg-white p-8 md:p-12 rounded-xl shadow-lg shadow-slate-200/50 border border-slate-200 dark:bg-slate-800/50 dark:border-slate-700 dark:shadow-slate-900/50">
        <h1 className="font-heading text-4xl md:text-5xl font-extrabold text-slate-900 mb-6 tracking-tight dark:text-slate-100">
          Other vs. Another: What's the Difference?
        </h1>

        <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-r-lg mb-8 dark:bg-green-900/30 dark:border-green-400">
          <h2 className="text-xl font-bold text-green-900 dark:text-green-100 mb-2">Quick Answer</h2>
          <p className="text-lg text-green-800 dark:text-green-200 mb-2">
            <strong>other</strong> = used with plural nouns or "the" (other books, the other one)
          </p>
          <p className="text-lg text-green-800 dark:text-green-200">
            <strong>another</strong> = always singular — "one more" or "a different one" (an + other)
          </p>
        </div>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Explanation
          </h2>
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <p className="font-bold text-blue-900 dark:text-blue-100 mb-2">OTHER</p>
              <p className="text-blue-800 dark:text-blue-200 mb-2 text-sm">With plural nouns, or "the" + singular</p>
              <p className="text-blue-700 dark:text-blue-300 italic text-sm">"I have <strong>other</strong> plans." (plural)</p>
              <p className="text-blue-700 dark:text-blue-300 italic text-sm">"Where's the <strong>other</strong> shoe?" (the + singular)</p>
            </div>
            <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
              <p className="font-bold text-purple-900 dark:text-purple-100 mb-2">ANOTHER</p>
              <p className="text-purple-800 dark:text-purple-200 mb-2 text-sm">Always singular — one more / a different one</p>
              <p className="text-purple-700 dark:text-purple-300 italic text-sm">"Can I have <strong>another</strong> coffee?" (one more)</p>
              <p className="text-purple-700 dark:text-purple-300 italic text-sm">"Let's try <strong>another</strong> way." (different one)</p>
            </div>
          </div>
          <div className="bg-teal-50 dark:bg-teal-900/20 p-4 rounded-lg">
            <p className="text-lg text-teal-800 dark:text-teal-200">
              <strong>Memory trick:</strong> <strong>Another</strong> = "an" + "other" — and "an" only goes with singular nouns, so <strong>another</strong> is always singular. <strong>Other</strong> is more flexible: plural nouns (other people) or with "the" (the other day).
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
              <span className="text-lg text-slate-700 dark:text-slate-300">There are <strong>other</strong> ways to solve this problem. (plural)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">I'd like <strong>another</strong> slice of cake. (one more)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">The <strong>other</strong> students left early. (the + plural)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">That's <strong>another</strong> matter entirely. (a different one)</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">I need another two days to finish.</span>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Common Mistakes
          </h2>
          <div className="space-y-4">
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> Can you show me other example?</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> Can you show me another example? (singular — one more)</p>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> I need to buy another shoes.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> I need to buy other shoes. (plural noun, not "another")</p>
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
              "I tried one solution, then _____ , but neither worked. The _____ team members suggested _____ approach."
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
                  <strong>Answer:</strong> "...then <strong>another</strong>, but neither worked. The <strong>other</strong> team members suggested <strong>another</strong> approach."
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
            <li><Link to="/grammar-mistakes/eg-vs-ie/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ e.g. vs. i.e.</Link></li>
            <li><Link to="/grammar-mistakes/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ All Grammar Mistakes</Link></li>
          </ul>
        </section>
      </article>
    </>
  );
};

export default OtherVsAnotherPage;
