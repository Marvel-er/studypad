import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import usePageMetadata from '../../hooks/usePageMetadata';
import SchemaMarkup from '../SchemaMarkup';

export interface ComparisonTableRow {
  feature: string;
  values: string[];
}

export interface ComparisonTerm {
  label: string;
  summary: string;
  pattern?: string;
  examples: string[];
}

export interface ComparisonMistake {
  incorrect: string;
  correct: string;
  note?: string;
}

export interface ComparisonQuizQuestion {
  prompt: string;
  answer: string;
  explanation: string;
}

export interface ComparisonFAQ {
  question: string;
  answer: string;
}

export interface RelatedLink {
  to: string;
  text: string;
}

export interface ComparisonPageData {
  metaTitle: string;
  metaDescription: string;
  slug: string;
  h1: string;
  breadcrumbLabel: string;
  datePublished: string;
  dateModified: string;
  quickAnswer: string;
  tableColumns: string[];
  tableRows: ComparisonTableRow[];
  terms: ComparisonTerm[];
  grammarRule: string;
  extraRule?: string;
  mistakes: ComparisonMistake[];
  correctExamples: string[];
  quiz: ComparisonQuizQuestion[];
  faqs: ComparisonFAQ[];
  related: RelatedLink[];
}

const TERM_COLORS = [
  { bg: 'bg-blue-50 dark:bg-blue-900/20', text: 'text-blue-900 dark:text-blue-100', sub: 'text-blue-800 dark:text-blue-200', mono: 'text-blue-700 dark:text-blue-300' },
  { bg: 'bg-purple-50 dark:bg-purple-900/20', text: 'text-purple-900 dark:text-purple-100', sub: 'text-purple-800 dark:text-purple-200', mono: 'text-purple-700 dark:text-purple-300' },
  { bg: 'bg-teal-50 dark:bg-teal-900/20', text: 'text-teal-900 dark:text-teal-100', sub: 'text-teal-800 dark:text-teal-200', mono: 'text-teal-700 dark:text-teal-300' },
];

const gridColsClass = (n: number) => {
  if (n >= 3) return 'md:grid-cols-3';
  return 'md:grid-cols-2';
};

const ComparisonPageTemplate: React.FC<{ data: ComparisonPageData }> = ({ data }) => {
  const canonical = `https://typogrammar.com/what-is-the-difference/${data.slug}/`;

  usePageMetadata({
    title: data.metaTitle,
    description: data.metaDescription,
    canonical,
  });

  const [revealed, setRevealed] = useState<Record<number, boolean>>({});
  const toggleReveal = (i: number) => setRevealed((prev) => ({ ...prev, [i]: !prev[i] }));

  const articleSchema = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: data.h1,
    description: data.metaDescription,
    author: { '@type': 'Organization', name: 'TypoGrammar' },
    publisher: {
      '@type': 'Organization',
      name: 'TypoGrammar',
      logo: { '@type': 'ImageObject', url: 'https://typogrammar.com/logo.png' },
    },
    mainEntityOfPage: { '@type': 'WebPage', '@id': canonical },
    datePublished: data.datePublished,
    dateModified: data.dateModified,
  };

  const faqSchema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: data.faqs.map((f) => ({
      '@type': 'Question',
      name: f.question,
      acceptedAnswer: { '@type': 'Answer', text: f.answer },
    })),
  };

  return (
    <>
      <SchemaMarkup type="Article" data={articleSchema} />
      <SchemaMarkup type="FAQPage" data={faqSchema} />

      <nav className="mb-6 text-slate-600 dark:text-slate-400">
        <Link to="/" className="hover:text-blue-600 dark:hover:text-blue-400">Home</Link>
        {' › '}
        <Link to="/what-is-the-difference/" className="hover:text-blue-600 dark:hover:text-blue-400">What's the Difference</Link>
        {' › '}
        <span className="text-slate-900 dark:text-slate-100">{data.breadcrumbLabel}</span>
      </nav>

      <article className="max-w-4xl mx-auto bg-white p-8 md:p-12 rounded-xl shadow-lg shadow-slate-200/50 border border-slate-200 dark:bg-slate-800/50 dark:border-slate-700 dark:shadow-slate-900/50">
        <h1 className="font-heading text-4xl md:text-5xl font-extrabold text-slate-900 mb-6 tracking-tight dark:text-slate-100">
          {data.h1}
        </h1>

        {/* Quick Answer */}
        <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-r-lg mb-8 dark:bg-green-900/30 dark:border-green-400">
          <h2 className="text-xl font-bold text-green-900 dark:text-green-100 mb-2">Quick Answer</h2>
          <p className="text-lg text-green-800 dark:text-green-200">{data.quickAnswer}</p>
        </div>

        {/* Difference Table */}
        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Difference at a Glance
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-100 dark:bg-slate-700">
                  <th className="p-3 font-bold text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-600">Feature</th>
                  {data.tableColumns.map((col, i) => (
                    <th key={i} className="p-3 font-bold text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-600">{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.tableRows.map((row, i) => (
                  <tr key={i} className={i % 2 === 0 ? 'bg-white dark:bg-slate-800/50' : 'bg-slate-50 dark:bg-slate-700/30'}>
                    <td className="p-3 font-semibold text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-600">{row.feature}</td>
                    {row.values.map((v, j) => (
                      <td key={j} className="p-3 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-600">{v}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Definitions */}
        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Definitions
          </h2>
          <div className={`grid grid-cols-1 ${gridColsClass(data.terms.length)} gap-4`}>
            {data.terms.map((term, i) => {
              const c = TERM_COLORS[i % TERM_COLORS.length];
              return (
                <div key={i} className={`${c.bg} p-4 rounded-lg`}>
                  <p className={`font-bold ${c.text} mb-2 uppercase`}>{term.label}</p>
                  <p className={`${c.sub} mb-2`}>{term.summary}</p>
                  {term.pattern && <p className={`${c.mono} font-mono text-sm mb-2`}>{term.pattern}</p>}
                  {term.examples.map((ex, k) => (
                    <p key={k} className={`${c.mono} italic`}>{ex}</p>
                  ))}
                </div>
              );
            })}
          </div>
        </section>

        {/* Grammar Rule */}
        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Grammar Rule
          </h2>
          <div className="bg-teal-50 dark:bg-teal-900/20 p-4 rounded-lg mb-4">
            <p className="text-lg text-teal-800 dark:text-teal-200">
              <strong>Key Rule:</strong> {data.grammarRule}
            </p>
          </div>
          {data.extraRule && (
            <div className="bg-slate-100 dark:bg-slate-700 p-4 rounded-lg">
              <p className="text-slate-700 dark:text-slate-300">{data.extraRule}</p>
            </div>
          )}
        </section>

        {/* Common Mistakes */}
        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Common Mistakes
          </h2>
          <div className="space-y-4">
            {data.mistakes.map((m, i) => (
              <div key={i}>
                <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg mb-2">
                  <p className="text-lg text-red-800 dark:text-red-200"><strong>Incorrect:</strong> {m.incorrect}</p>
                </div>
                <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
                  <p className="text-lg text-green-800 dark:text-green-200"><strong>Correct:</strong> {m.correct}</p>
                  {m.note && <p className="text-green-700 dark:text-green-300 mt-1 text-base">{m.note}</p>}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Correct Examples */}
        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            More Correct Examples
          </h2>
          <div className="space-y-3">
            {data.correctExamples.map((ex, i) => (
              <div key={i} className="flex items-start">
                <span className="text-green-600 dark:text-green-400 mr-3 text-xl">✔</span>
                <span className="text-lg text-slate-700 dark:text-slate-300">{ex}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Mini Quiz */}
        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Mini Quiz
          </h2>
          <div className="space-y-4">
            {data.quiz.map((q, i) => (
              <div key={i} className="bg-teal-50 dark:bg-teal-900/20 p-6 rounded-lg">
                <p className="text-lg text-slate-800 dark:text-slate-200 mb-4">
                  <strong>{i + 1}.</strong> {q.prompt}
                </p>
                <button
                  onClick={() => toggleReveal(i)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  {revealed[i] ? 'Hide Answer' : 'Show Answer'}
                </button>
                {revealed[i] && (
                  <div className="mt-4 p-4 bg-green-100 dark:bg-green-900/30 rounded-lg">
                    <p className="text-lg text-green-800 dark:text-green-200"><strong>Answer:</strong> {q.answer}</p>
                    <p className="text-green-700 dark:text-green-300 mt-2">{q.explanation}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* FAQ */}
        <section className="mb-10">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Common Learner Questions
          </h2>
          <div className="space-y-4">
            {data.faqs.map((f, i) => (
              <div key={i} className="bg-slate-50 dark:bg-slate-700/30 p-4 rounded-lg">
                <p className="font-bold text-slate-800 dark:text-slate-200 mb-1">{f.question}</p>
                <p className="text-slate-700 dark:text-slate-300">{f.answer}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Related Comparisons */}
        <section className="mb-6">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700">
            Related Comparisons
          </h2>
          <ul className="space-y-2 text-lg">
            {data.related.map((link, i) => (
              <li key={i}>
                <Link to={link.to} className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">
                  → {link.text}
                </Link>
              </li>
            ))}
            <li>
              <Link to="/what-is-the-difference/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">
                → All "What's the Difference" Comparisons
              </Link>
            </li>
          </ul>
        </section>
      </article>
    </>
  );
};

export default ComparisonPageTemplate;
