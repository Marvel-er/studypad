import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import usePageMetadata from '../../hooks/usePageMetadata';
import SchemaMarkup from '../../components/SchemaMarkup';

const WeatherVsWhetherPage: React.FC = () => {
  usePageMetadata({
    title: 'Weather vs. Whether: What\'s the Difference? | TypoGrammar',
    description: 'Learn the difference between weather and whether. Weather is a noun about climate. Whether is a conjunction expressing alternatives or doubt. Examples and practice.',
    canonical: 'https://typogrammar.com/grammar-mistakes/weather-vs-whether/'
  });

  const [showAnswer, setShowAnswer] = useState(false);

  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Weather vs. Whether: What's the Difference?",
    "description": "'Weather' is a noun (or verb) about atmospheric conditions. 'Whether' is a conjunction used to express doubt, alternatives, or indirect questions.",
    "author": { "@type": "Organization", "name": "TypoGrammar" },
    "publisher": { "@type": "Organization", "name": "TypoGrammar", "logo": { "@type": "ImageObject", "url": "https://typogrammar.com/logo.png" } },
    "mainEntityOfPage": { "@type": "WebPage", "@id": "https://typogrammar.com/grammar-mistakes/weather-vs-whether" },
    "datePublished": "2026-06-30",
    "dateModified": "2026-06-30"
  };

  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {
        "@type": "Question",
        "name": "What is the difference between weather and whether?",
        "acceptedAnswer": { "@type": "Answer", "text": "'Weather' refers to atmospheric conditions like rain, sun, snow, and temperature (The weather is lovely today. I don't like cold weather). 'Whether' is a conjunction meaning 'if' or expressing alternatives (I don't know whether she's coming. Whether you like it or not, we must go)." }
      },
      {
        "@type": "Question",
        "name": "Is it 'weather or not' or 'whether or not'?",
        "acceptedAnswer": { "@type": "Answer", "text": "The correct phrase is 'whether or not' — using the conjunction 'whether'. 'Weather or not' is incorrect. Example: 'We are going whether or not it rains.' You can also use 'whether' alone: 'I'm not sure whether she'll come.'" }
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
        <span className="text-slate-900 dark:text-slate-100">Weather vs. Whether</span>
      </nav>

      <article className="max-w-4xl mx-auto bg-white p-8 md:p-12 rounded-xl shadow-lg shadow-slate-200/50 border border-slate-200 dark:bg-slate-800/50 dark:border-slate-700 dark:shadow-slate-900/50">
        <h1 className="font-heading text-4xl md:text-5xl font-extrabold text-slate-900 mb-6 tracking-tight dark:text-slate-100">
          Weather vs. Whether: What's the Difference?
        </h1>

        <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-r-lg mb-8 dark:bg-green-900/30 dark:border-green-400">
          <h2 className="text-xl font-bold text-green-900 dark:text-green-100 mb-2">Quick Answer</h2>
          <p className="text-lg text-green-800 dark:text-green-200 mb-2">
            <strong>weather</strong> = noun/verb about climate (sun, rain, snow, temperature)
          </p>
          <p className="text-lg text-green-800 dark:text-green-200">
            <strong>whether</strong> = conjunction meaning "if" or expressing alternatives
          </p>
        </div>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Explanation
          </h2>
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
              <p className="font-bold text-blue-900 dark:text-blue-100 mb-2">WEATHER (noun/verb)</p>
              <p className="text-blue-800 dark:text-blue-200 mb-2">Atmospheric conditions; to survive or endure</p>
              <p className="text-blue-700 dark:text-blue-300 italic mt-3">"The <strong>weather</strong> is beautiful today." (noun)</p>
              <p className="text-blue-700 dark:text-blue-300 italic">"Cold <strong>weather</strong> is coming." (noun)</p>
              <p className="text-blue-700 dark:text-blue-300 italic">"We <strong>weathered</strong> the storm." (verb)</p>
            </div>
            <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
              <p className="font-bold text-purple-900 dark:text-purple-100 mb-2">WHETHER (conjunction)</p>
              <p className="text-purple-800 dark:text-purple-200 mb-2">Introduces alternatives or indirect yes/no questions</p>
              <p className="text-purple-700 dark:text-purple-300 italic mt-3">"I wonder <strong>whether</strong> she'll come." (if)</p>
              <p className="text-purple-700 dark:text-purple-300 italic">"<strong>Whether</strong> you like it or not..." (alternatives)</p>
              <p className="text-purple-700 dark:text-purple-300 italic">"I don't know <strong>whether</strong> to go." (if)</p>
            </div>
          </div>
          <div className="bg-teal-50 dark:bg-teal-900/20 p-4 rounded-lg">
            <p className="text-lg text-teal-800 dark:text-teal-200">
              <strong>Memory trick:</strong> <em>Weath</em>er contains "eat" — think of <strong>weather</strong> as something you can almost feel/experience (heat, cold). <em>Wh</em>ether starts like "which" — it expresses a choice or question.
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
              <span className="text-lg text-slate-700 dark:text-slate-300">Check the <strong>weather</strong> forecast before going out. (noun)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">I'm not sure <strong>whether</strong> the meeting is today or tomorrow. (conjunction)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">The bad <strong>weather</strong> cancelled the match. (noun)</span>
            </div>
            <div className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
              <span className="text-lg text-slate-700 dark:text-slate-300">We'll go <strong>whether</strong> or not it rains. (alternatives)</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">I don't know weather she's coming.</span>
            </div>
            <div className="flex items-start">
              <span className="text-red-600 dark:text-red-400 mr-3 text-xl">✘</span>
              <span className="text-lg text-slate-700 dark:text-slate-300 line-through">The whether has been terrible this week.</span>
            </div>
          </div>
        </section>

        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Common Mistakes
          </h2>
          <div className="space-y-4">
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> I can't decide weather to accept the offer.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> I can't decide whether to accept the offer. (whether = if)</p>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
              <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> The whether forecast says it will snow.</p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> The weather forecast says it will snow. (weather = climate)</p>
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
              "_____ the _____ is good or bad, the festival will continue."
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
                  <strong>Answer:</strong> "<strong>Whether</strong> the <strong>weather</strong> is good or bad..."
                </p>
                <p className="text-green-700 dark:text-green-300 mt-2">
                  Whether = regardless of alternatives. Weather = climate conditions.
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
            <li><Link to="/grammar-mistakes/quiet-vs-quite/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Quiet vs. Quite</Link></li>
            <li><Link to="/grammar-mistakes/affect-vs-effect/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Affect vs. Effect</Link></li>
            <li><Link to="/vocabulary/homophones-homonyms-homographs/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ Homophones Guide</Link></li>
            <li><Link to="/grammar-mistakes/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">→ All Grammar Mistakes</Link></li>
          </ul>
        </section>
      </article>
    </>
  );
};

export default WeatherVsWhetherPage;
