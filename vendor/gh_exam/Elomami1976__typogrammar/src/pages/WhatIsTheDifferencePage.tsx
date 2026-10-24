import React from 'react';
import { Link } from 'react-router-dom';
import usePageMetadata from '../hooks/usePageMetadata';
import SchemaMarkup from '../components/SchemaMarkup';

const WhatIsTheDifferencePage: React.FC = () => {
  usePageMetadata({
    title: "What's the Difference? Confusing English Word Pairs Explained | TypoGrammar",
    description: "What's the difference between during and while, may and might, hear and listen? Clear explanations, tables, and examples for the English words learners confuse most.",
    canonical: 'https://typogrammar.com/what-is-the-difference/'
  });

  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "What's the Difference? Confusing English Word Pairs Explained",
    "description": "A complete guide to the English word pairs and triples that learners confuse most, with difference tables, rules, examples, and quizzes.",
    "author": {
      "@type": "Organization",
      "name": "TypoGrammar"
    },
    "publisher": {
      "@type": "Organization",
      "name": "TypoGrammar",
      "logo": {
        "@type": "ImageObject",
        "url": "https://typogrammar.com/logo.png"
      }
    },
    "mainEntityOfPage": {
      "@type": "WebPage",
      "@id": "https://typogrammar.com/what-is-the-difference"
    },
    "datePublished": "2026-07-04",
    "dateModified": "2026-07-04"
  };

  const categories = [
    {
      title: "Confusing Prepositions & Connectors",
      description: "Master the small words that change the meaning and timing of a sentence.",
      links: [
        { to: "/what-is-the-difference/during-vs-while/", text: "During vs. While" },
        { to: "/what-is-the-difference/because-vs-because-of/", text: "Because vs. Because of" },
        { to: "/what-is-the-difference/between-vs-among/", text: "Between vs. Among" },
        { to: "/what-is-the-difference/until-vs-by/", text: "Until vs. By" },
        { to: "/what-is-the-difference/in-time-vs-on-time/", text: "In Time vs. On Time" },
        { to: "/what-is-the-difference/for-vs-since/", text: "For vs. Since" },
      ]
    },
    {
      title: "Grammar & Verb Tenses",
      description: "Learn the tense and modal verb distinctions that trip up even advanced learners.",
      links: [
        { to: "/what-is-the-difference/been-to-vs-gone-to/", text: "Been to vs. Gone to" },
        { to: "/what-is-the-difference/may-vs-might/", text: "May vs. Might" },
        { to: "/what-is-the-difference/will-vs-be-going-to/", text: "Will vs. Be Going to" },
        { to: "/what-is-the-difference/must-vs-have-to/", text: "Must vs. Have to" },
        { to: "/what-is-the-difference/can-vs-could/", text: "Can vs. Could" },
        { to: "/what-is-the-difference/bored-vs-boring/", text: "Bored vs. Boring" },
      ]
    },
    {
      title: "Easily Confused Verbs (Action & Communication)",
      description: "Choose the right verb for hearing, seeing, remembering, and everyday actions.",
      links: [
        { to: "/what-is-the-difference/hear-vs-listen/", text: "Hear vs. Listen" },
        { to: "/what-is-the-difference/see-vs-look-vs-watch/", text: "See vs. Look vs. Watch" },
        { to: "/what-is-the-difference/remember-vs-remind/", text: "Remember vs. Remind" },
        { to: "/what-is-the-difference/win-vs-beat/", text: "Win vs. Beat" },
        { to: "/what-is-the-difference/borrow-vs-lend/", text: "Borrow vs. Lend" },
        { to: "/what-is-the-difference/bring-vs-take/", text: "Bring vs. Take" },
      ]
    },
    {
      title: "Subtle Vocabulary Distinctions",
      description: "Understand the fine shades of meaning between words that look almost interchangeable.",
      links: [
        { to: "/what-is-the-difference/farther-vs-further/", text: "Farther vs. Further" },
        { to: "/what-is-the-difference/job-vs-work/", text: "Job vs. Work" },
        { to: "/what-is-the-difference/travel-vs-journey-vs-trip/", text: "Travel vs. Journey vs. Trip" },
        { to: "/what-is-the-difference/custom-vs-habit/", text: "Custom vs. Habit" },
        { to: "/what-is-the-difference/customer-vs-client/", text: "Customer vs. Client" },
        { to: "/what-is-the-difference/house-vs-home/", text: "House vs. Home" },
        { to: "/what-is-the-difference/sensible-vs-sensitive/", text: "Sensible vs. Sensitive" },
        { to: "/what-is-the-difference/asylum-vs-refugee-status/", text: "Asylum vs. Refugee Status" },
      ]
    },
    {
      title: "Career & Work Life",
      description: "Get the workplace and career vocabulary right, from applications to titles and pay.",
      links: [
        { to: "/what-is-the-difference/resume-vs-cv/", text: "Resume vs. CV" },
        { to: "/what-is-the-difference/internship-vs-apprenticeship/", text: "Internship vs. Apprenticeship" },
        { to: "/what-is-the-difference/founder-vs-ceo/", text: "Founder vs. CEO" },
        { to: "/what-is-the-difference/job-vs-career/", text: "Job vs. Career" },
        { to: "/what-is-the-difference/salary-vs-wage/", text: "Salary vs. Wage" },
      ]
    },
    {
      title: "Education & Mind",
      description: "Distinguish the words learners mix up around teaching, ability, and intelligence.",
      links: [
        { to: "/what-is-the-difference/professor-vs-teacher/", text: "Professor vs. Teacher" },
        { to: "/what-is-the-difference/iq-vs-intelligence/", text: "IQ vs. Intelligence" },
        { to: "/what-is-the-difference/skill-vs-talent/", text: "Skill vs. Talent" },
      ]
    },
    {
      title: "Everyday Life & Media",
      description: "Everyday nouns that look similar but describe different things in daily life and media.",
      links: [
        { to: "/what-is-the-difference/photo-vs-picture-vs-image/", text: "Photo vs. Picture vs. Image" },
        { to: "/what-is-the-difference/vlog-vs-blog/", text: "Vlog vs. Blog" },
        { to: "/what-is-the-difference/hotel-vs-motel/", text: "Hotel vs. Motel" },
        { to: "/what-is-the-difference/money-vs-currency/", text: "Money vs. Currency" },
        { to: "/what-is-the-difference/jail-vs-prison/", text: "Jail vs. Prison" },
        { to: "/what-is-the-difference/screenplay-vs-script/", text: "Screenplay vs. Script" },
      ]
    },
    {
      title: "Emotions & Abstract Concepts",
      description: "Understand the nuance between feelings, ideas, and concepts that are often confused.",
      links: [
        { to: "/what-is-the-difference/trauma-vs-sadness/", text: "Trauma vs. Sadness" },
        { to: "/what-is-the-difference/problem-vs-issue/", text: "Problem vs. Issue" },
        { to: "/what-is-the-difference/fact-vs-truth/", text: "Fact vs. Truth" },
        { to: "/what-is-the-difference/ambition-vs-greed/", text: "Ambition vs. Greed" },
      ]
    },
    {
      title: "Religion & Belief",
      description: "Learn the precise meaning of terms describing religious buildings, roles, and beliefs.",
      links: [
        { to: "/what-is-the-difference/church-vs-cathedral/", text: "Church vs. Cathedral" },
        { to: "/what-is-the-difference/theism-vs-deism/", text: "Theism vs. Deism" },
        { to: "/what-is-the-difference/priest-vs-monk/", text: "Priest vs. Monk" },
        { to: "/what-is-the-difference/imam-vs-sheikh/", text: "Imam vs. Sheikh" },
      ]
    },
    {
      title: "Politics & Society",
      description: "Understand key political, historical, and social terms that are often mixed up.",
      links: [
        { to: "/what-is-the-difference/utopia-vs-dystopia/", text: "Utopia vs. Dystopia" },
        { to: "/what-is-the-difference/fascism-vs-nazism/", text: "Fascism vs. Nazism" },
        { to: "/what-is-the-difference/communism-vs-socialism/", text: "Communism vs. Socialism" },
        { to: "/what-is-the-difference/sheriff-vs-police/", text: "Sheriff vs. Police" },
      ]
    },
    {
      title: "Money & Consumer Life",
      description: "Get clear on the everyday financial and consumer terms that sound alike.",
      links: [
        { to: "/what-is-the-difference/subscription-vs-membership/", text: "Subscription vs. Membership" },
        { to: "/what-is-the-difference/refund-vs-rebate/", text: "Refund vs. Rebate" },
        { to: "/what-is-the-difference/credit-score-vs-credit-report/", text: "Credit Score vs. Credit Report" },
      ]
    },
    {
      title: "Science & Nature",
      description: "Clarify commonly confused scientific terms in physics, biology, and astronomy.",
      links: [
        { to: "/what-is-the-difference/reflection-vs-refraction/", text: "Reflection vs. Refraction" },
        { to: "/what-is-the-difference/virus-vs-viroid/", text: "Virus vs. Viroid" },
        { to: "/what-is-the-difference/supernova-vs-kilonova/", text: "Supernova vs. Kilonova" },
      ]
    },
  ];

  return (
    <>
      <SchemaMarkup type="Article" data={articleSchema} />

      {/* Breadcrumb Navigation */}
      <nav className="mb-6 text-slate-600 dark:text-slate-400">
        <Link to="/" className="hover:text-blue-600 dark:hover:text-blue-400">Home</Link>
        {' › '}
        <span className="text-slate-900 dark:text-slate-100">What's the Difference</span>
      </nav>

      <article className="max-w-4xl mx-auto bg-white p-8 md:p-12 rounded-xl shadow-lg shadow-slate-200/50 border border-slate-200 dark:bg-slate-800/50 dark:border-slate-700 dark:shadow-slate-900/50">
        <h1 className="font-heading text-4xl md:text-5xl font-extrabold text-slate-900 mb-6 tracking-tight dark:text-slate-100">
          What's the Difference? Confusing English Word Pairs Explained
        </h1>

        {/* Quick Answer Box */}
        <div className="bg-blue-50 border-l-4 border-blue-500 p-6 rounded-r-lg mb-8 dark:bg-blue-900/30 dark:border-blue-400">
          <h2 className="text-xl font-bold text-blue-900 dark:text-blue-100 mb-2">What You'll Learn</h2>
          <p className="text-lg text-blue-800 dark:text-blue-200">
            This hub explains the English word pairs (and triples) that learners confuse most: prepositions
            and connectors like during vs. while, verb tenses and modals like may vs. might, easily confused
            action verbs like hear vs. listen, and subtle vocabulary distinctions like farther vs. further.
            Every page has a quick answer, a difference table, definitions, a grammar rule, common mistakes,
            correct examples, a mini quiz, and an FAQ.
          </p>
        </div>

        <p className="text-lg text-slate-700 dark:text-slate-300 mb-8">
          Some English words look almost identical in meaning but follow different rules or fit different
          situations. Getting them right makes your writing and speaking sound more precise and natural.
          Choose a comparison below to see the exact difference, with clear examples and practice questions.
        </p>

        {/* Categories Grid */}
        <div className="space-y-10">
          {categories.map((category, index) => (
            <section key={index} className="border-b border-slate-200 dark:border-slate-700 pb-8 last:border-b-0">
              <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-3">
                {category.title}
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                {category.description}
              </p>
              <ul className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {category.links.map((link, linkIndex) => (
                  <li key={linkIndex}>
                    <Link
                      to={link.to}
                      className="flex items-center p-3 bg-slate-50 hover:bg-slate-100 rounded-lg transition-colors dark:bg-slate-700/50 dark:hover:bg-slate-700 group"
                    >
                      <span className="text-blue-600 dark:text-blue-400 mr-2 group-hover:translate-x-1 transition-transform">→</span>
                      <span className="text-slate-700 dark:text-slate-300 group-hover:text-blue-600 dark:group-hover:text-blue-400">
                        {link.text}
                      </span>
                    </Link>
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>

        {/* Why This Matters Section */}
        <section className="mt-12 p-6 bg-teal-50 rounded-xl dark:bg-teal-900/20">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4">
            Why These Distinctions Matter
          </h2>
          <ul className="space-y-3 text-lg text-slate-700 dark:text-slate-300">
            <li className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-2">✓</span>
              <span><strong>Precision:</strong> Choosing the right word shows control of nuance, not just vocabulary size.</span>
            </li>
            <li className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-2">✓</span>
              <span><strong>Higher Test Scores:</strong> IELTS and TOEFL examiners reward accurate word choice in Lexical Resource.</span>
            </li>
            <li className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-2">✓</span>
              <span><strong>Clearer Communication:</strong> The right word prevents misunderstandings in emails, essays, and conversation.</span>
            </li>
            <li className="flex items-start">
              <span className="text-green-600 dark:text-green-400 mr-2">✓</span>
              <span><strong>Confidence:</strong> Once you know the rule, you stop guessing and start using these words naturally.</span>
            </li>
          </ul>
        </section>

        {/* Related Resources */}
        <section className="mt-10 p-6 bg-slate-50 rounded-xl dark:bg-slate-700/30">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4">
            Related Resources
          </h2>
          <ul className="space-y-2 text-lg">
            <li>
              <Link to="/grammar-mistakes/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">
                → Common English Grammar Mistakes
              </Link>
            </li>
            <li>
              <Link to="/commonly-confused-words/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">
                → Commonly Confused Words
              </Link>
            </li>
            <li>
              <Link to="/grammar/verb-tenses/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">
                → The 12 English Verb Tenses
              </Link>
            </li>
            <li>
              <Link to="/grammar-guide/" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">
                → Complete Grammar Guide
              </Link>
            </li>
          </ul>
        </section>
      </article>
    </>
  );
};

export default WhatIsTheDifferencePage;
