import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import usePageMetadata from '../../hooks/usePageMetadata';
import SchemaMarkup from '../../components/SchemaMarkup';

const ThereVsTheirVsTheyrePage: React.FC = () => {
  usePageMetadata({
    title: "There vs. Their vs. They're: What's the Difference? | TypoGrammar",
    description: "Learn the difference between there, their, and they're. There = place or existence. Their = possessive. They're = contraction of they are. Examples and practice.",
    canonical: 'https://typogrammar.com/grammar-mistakes/there-vs-their-vs-theyre/'
  });

  const [showAnswer, setShowAnswer] = useState(false);

  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "There vs. Their vs. They're: What's the Difference?",
    "description": "'There' refers to a place or existence. 'Their' is a possessive pronoun. 'They're' is a contraction of 'they are'.",
    "author": { "@type": "Organization", "name": "TypoGrammar" },
    "publisher": { "@type": "Organization", "name": "TypoGrammar", "logo": { "@type": "ImageObject", "url": "https://typogrammar.com/logo.png" } },
    "mainEntityOfPage": { "@type": "WebPage", "@id": "https://typogrammar.com/grammar-mistakes/there-vs-their-vs-theyre" },
    "datePublished": "2026-06-30",
    "dateModified": "2026-06-30"
  };

  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the difference between there, their, and they're?",
        "acceptedAnswer": { "@type": "Answer", "text": "'There' refers to a place (over there) or existence (There is a problem). 'Their' is a possessive pronoun meaning 'belonging to them' (their house, their ideas). 'They're' is a contraction of 'they are' (They're coming soon)." }
      },
      {
        "@type": "Question",
        "name": "How do I remember there, their, and they're?",
        "acceptedAnswer": { "@type": "Answer", "text": "Test 1: Can you replace it with 'they are'? → use they're. Test 2: Does it show ownership? → use their. Test 3: Does it refer to a place or existence? → use there. The word 'here' is inside 'there' — both refer to place." }
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
        <span className="text-slate-900 dark:text-slate-100">There vs. Their vs. They're</span>
      </nav>

      <article className="max-w-4xl mx-auto bg-white p-8 md:p-12 rounded-xl shadow-lg shadow-slate-200/50 border border-slate-200 dark:bg-slate-800/50 dark:border-slate-700 dark:shadow-slate-900/50">
        <h1 className="font-heading text-4xl md:text-5xl font-extrabold text-slate-900 mb-6 tracking-tight dark:text-slate-100">
          There vs. Their vs. They're
        </h1>

        <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-r-lg mb-8 dark:bg-green-900/30 dark:border-green-400">
          <h2 className="text-xl font-bold text-green-900 dark:text-green-100 mb-2">Quick Answer</h2>
          <p className="text-lg text-green-800 dark:text-green-200 mb-1"><strong>there</strong> = place or existence (Put it over there. There is a way.)</p>
          <p className="text-lg text-green-800 dark:text-green-200 mb-1"><strong>their</strong> = possessive pronoun (their house, their ideas)</p>
          <p className="text-lg text-green-800 dark:text-green-200"><strong>they're</strong> = contraction of "they are" (They're coming.)</p>
        </div>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Explanation
          </h2>
          <div className="grid md:grid-cols-3 gap-4 mb-6">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <p className="font-bold text-blue-900 dark:text-blue-100 mb-2">THERE</p>
              <p className="text-blue-800 dark:text-blue-200 mb-1 text-sm">1. Place (≠ here)</p>
              <p className="text-blue-800 dark:text-blue-200 mb-2 text-sm">2. Existence (there is/are)</p>
              <p className="text-blue-700 dark:text-blue-300 italic text-sm">"Put it over <strong>there</strong>."</p>
              <p className="text-blue-700 dark:text-blue-300 italic text-sm">"<strong>There</strong> is a problem."</p>
              <p className="text-blue-600 dark:text-blue-400 text-xs mt-2">Tip: "here" is inside "there"</p>
            </div>
            <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
              <p className="font-bold text-purple-900 dark:text-purple-100 mb-2">THEIR</p>
              <p className="text-purple-800 dark:text-purple-200 mb-2 text-sm">Possessive — belonging to them</p>
              <p className="text-purple-700 dark:text-purple-300 italic text-sm">"<strong>Their</strong> house is big."</p>
              <p className="text-purple-700 dark:text-purple-300 italic text-sm">"I like <strong>their</strong> music."</p>
              <p className="text-purple-600 dark:text-purple-400 text-xs mt-2">Like: my, your, his, her, our</p>
            </div>
            <div className="bg-orange-50 dark:bg-orange-900/20 p-4 rounded-lg">
              <p className="font-bold text-orange-900 dark:text-orange-100 mb-2">THEY'RE</p>
              <p className="text-orange-800 dark:text-orange-200 mb-2 text-sm">Contraction: they are</p>
              <p className="text-orange-700 dark:text-orange-300 italic text-sm">"<strong>They're</strong> coming soon."</p>
              <p className="text-orange-700 dark:text-orange-300 italic text-sm">"<strong>They're</strong> my friends."</p>
              <p className="text-orange-600 dark:text-orange-400 text-xs mt-2">Test: replace with "they are"</p>
            </div>
          </div>
          <div className="bg-teal-50 dark:bg-teal-900/20 p-4 rounded-lg">
            <p className="text-lg text-teal-800 dark:text-teal-200">
              <strong>Memory trick:</strong> The word <em>here</em> is hidden inside <em>there</em> — both deal with place. <em>Their</em> contains <em>heir</em> — someone who inherits (owns) things. <em>They're</em> has an apostrophe → contraction of "they are".
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
              <span className="text-lg text-slate-700 dark:text-slate-300">I left my keys over <strong>there</strong>. (place)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300"><strong>Their</strong> flight was delayed. (possessive)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300"><strong>They're</strong> planning a trip to Japan. (they are)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300"><strong>There</strong> are many ways to solve this problem.</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">I love there new apartment.</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">Their going to be late.</span>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Common Mistakes
          </h2>
          <div className="space-y-4">
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> Have you seen there new car?</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> Have you seen their new car? (possessive — belonging to them)</p>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> They're house is beautiful.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> Their house is beautiful. ("they are house" ✘ → use their)</p>
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
              "_____ late again — _____ boss is standing right _____ ."
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
                  <strong>Answer:</strong> <strong>They're</strong> late again — <strong>their</strong> boss is standing right <strong>there</strong>.
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
            <li><Link to="/grammar-mistakes/your-vs-youre/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Your vs. You're</Link></li>
            <li><Link to="/grammar-mistakes/whose-vs-whos/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Whose vs. Who's</Link></li>
            <li><Link to="/vocabulary/homophones-homonyms-homographs/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Homophones Guide</Link></li>
            <li><Link to="/grammar-mistakes/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ All Grammar Mistakes</Link></li>
          </ul>
        </section>
      </article>
    </>
  );
};

export default ThereVsTheirVsTheyrePage;
