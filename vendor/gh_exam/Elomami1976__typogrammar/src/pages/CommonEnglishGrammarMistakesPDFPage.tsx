import React, { useEffect } from 'react';
import usePageMetadata from '../hooks/usePageMetadata';
import { Download, Check, BookOpen, Target, Users, HelpCircle, FileText, Award, Star, CheckCircle, BookMarked, AlertCircle } from 'lucide-react';

const CommonEnglishGrammarMistakesPDFPage: React.FC = () => {
  usePageMetadata({
    title: 'Common English Grammar Mistakes PDF (Free Download) | TypoGrammar',
    description: 'Download the Common English Grammar Mistakes Handbook PDF from TypoGrammar. Identify and correct 95+ frequent grammar errors with clear rules, examples, a 20-question quiz, and a printable cheat sheet.',
    canonical: 'https://typogrammar.com/downloads/common-english-grammar-mistakes/',
    ogTitle: 'Common English Grammar Mistakes PDF (Free Download) | TypoGrammar',
    ogDescription: 'Download the Common English Grammar Mistakes Handbook PDF from TypoGrammar. Identify and correct 95+ frequent grammar errors with clear rules, examples, a 20-question quiz, and a printable cheat sheet.',
    ogUrl: 'https://typogrammar.com/downloads/common-english-grammar-mistakes',
    ogImage: 'https://typogrammar.com/images/books/Common_English_grammar_mistakes.jpg',
    ogType: 'book',
    twitterCard: 'summary_large_image',
    twitterTitle: 'Common English Grammar Mistakes PDF (Free Download) | TypoGrammar',
    twitterDescription: 'Download the Common English Grammar Mistakes Handbook PDF from TypoGrammar. Identify and correct 95+ frequent grammar errors with clear rules, examples, a 20-question quiz, and a printable cheat sheet.',
    twitterImage: 'https://typogrammar.com/images/books/Common_English_grammar_mistakes.jpg',
  });

  useEffect(() => {
    const bookSchema = {
      '@context': 'https://schema.org',
      '@type': 'Book',
      name: 'Common English Grammar Mistakes Handbook',
      author: {
        '@type': 'Organization',
        name: 'TypoGrammar',
      },
      publisher: {
        '@type': 'Organization',
        name: 'TypoGrammar',
      },
      inLanguage: 'en',
      bookFormat: 'EBook',
      url: 'https://typogrammar.com/downloads/common-english-grammar-mistakes',
      image: 'https://typogrammar.com/images/books/Common_English_grammar_mistakes.jpg',
      description:
        'A practical reference handbook covering more than 95 common English grammar mistakes organized into six categories: subject-verb agreement, verb form errors, confused words, preposition mistakes, quantifier errors, and redundancy. Includes rule explanations, correct and incorrect examples, grammar tips, a 20-question self-test quiz with answer key, and a printable cheat sheet.',
      offers: {
        '@type': 'Offer',
        price: '0',
        priceCurrency: 'USD',
        availability: 'https://schema.org/InStock',
      },
    };

    const learningResourceSchema = {
      '@context': 'https://schema.org',
      '@type': 'LearningResource',
      name: 'Common English Grammar Mistakes Handbook PDF',
      learningResourceType: 'ebook',
      about: ['English grammar', 'Grammar mistakes', 'IELTS grammar', 'TOEFL grammar', 'ESL writing'],
      url: 'https://typogrammar.com/downloads/common-english-grammar-mistakes',
      description:
        'Download the Common English Grammar Mistakes Handbook PDF. Identify and correct 95+ common grammar errors with clear explanations, examples, grammar tips, a self-test quiz, and a printable cheat sheet.',
    };

    const faqSchema = {
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      mainEntity: [
        {
          '@type': 'Question',
          name: 'Is this PDF free?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'Yes. The Common English Grammar Mistakes Handbook PDF is available as a free educational resource from TypoGrammar.',
          },
        },
        {
          '@type': 'Question',
          name: 'How many grammar mistakes does this handbook cover?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'The handbook covers more than 95 common English grammar mistakes organized into six clearly labeled categories.',
          },
        },
        {
          '@type': 'Question',
          name: 'Is this handbook suitable for beginners?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'Yes. Every explanation is written in clear, learner-friendly English, making the handbook suitable for beginners, intermediate learners, and advanced students.',
          },
        },
        {
          '@type': 'Question',
          name: 'Does the PDF include practice activities?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'Yes. The handbook includes a 20-question self-test quiz with a detailed answer key and explanations to help you check your understanding.',
          },
        },
        {
          '@type': 'Question',
          name: 'Can I use this handbook for IELTS preparation?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'Absolutely. The grammar mistakes covered directly affect IELTS Writing and Speaking scores. The handbook is an excellent companion for IELTS, TOEFL, Cambridge English, and Duolingo English Test preparation.',
          },
        },
        {
          '@type': 'Question',
          name: 'Is there a cheat sheet included?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'Yes. The handbook includes a printable grammar cheat sheet for quick reference and revision.',
          },
        },
      ],
    };

    const bookScript = document.createElement('script');
    bookScript.type = 'application/ld+json';
    bookScript.text = JSON.stringify(bookSchema);
    document.head.appendChild(bookScript);

    const learningScript = document.createElement('script');
    learningScript.type = 'application/ld+json';
    learningScript.text = JSON.stringify(learningResourceSchema);
    document.head.appendChild(learningScript);

    const faqScript = document.createElement('script');
    faqScript.type = 'application/ld+json';
    faqScript.text = JSON.stringify(faqSchema);
    document.head.appendChild(faqScript);

    return () => {
      if (bookScript.parentNode) document.head.removeChild(bookScript);
      if (learningScript.parentNode) document.head.removeChild(learningScript);
      if (faqScript.parentNode) document.head.removeChild(faqScript);
    };
  }, []);

  const faqItems = [
    {
      question: 'Is this PDF free?',
      answer: 'Yes. The Common English Grammar Mistakes Handbook PDF is available as a free educational resource from TypoGrammar.',
    },
    {
      question: 'How many grammar mistakes does this handbook cover?',
      answer: 'The handbook covers more than 95 common English grammar mistakes organized into six clearly labeled categories.',
    },
    {
      question: 'Is this handbook suitable for beginners?',
      answer: 'Yes. Every explanation is written in clear, learner-friendly English, making the handbook suitable for beginners, intermediate learners, and advanced students.',
    },
    {
      question: 'Does the PDF include practice activities?',
      answer: 'Yes. The handbook includes a 20-question self-test quiz with a detailed answer key and explanations to help you check your understanding.',
    },
    {
      question: 'Can I use this handbook for IELTS preparation?',
      answer: 'Absolutely. The grammar mistakes covered directly affect IELTS Writing and Speaking scores. The handbook is an excellent companion for IELTS, TOEFL, Cambridge English, and Duolingo English Test preparation.',
    },
    {
      question: 'Is there a cheat sheet included?',
      answer: 'Yes. The handbook includes a printable grammar cheat sheet for quick reference and revision.',
    },
  ];

  const sixCategories = [
    {
      color: 'blue',
      title: 'Subject-Verb Agreement',
      desc: 'Learn why the subject and verb must match in number and person, with rules for tricky cases like collective nouns, indefinite pronouns, and compound subjects.',
    },
    {
      color: 'green',
      title: 'Verb Form Errors',
      desc: 'Correct common mistakes with infinitives, gerunds, participles, irregular verbs, and tense consistency that undermine writing clarity.',
    },
    {
      color: 'purple',
      title: 'Confused Words',
      desc: 'Distinguish between frequently confused pairs such as affect/effect, lay/lie, their/there/they\'re, and dozens more that trip up even advanced learners.',
    },
    {
      color: 'amber',
      title: 'Preposition Mistakes',
      desc: 'Master the correct prepositions in common collocations, phrasal verbs, and idiomatic expressions where learners most often choose the wrong one.',
    },
    {
      color: 'rose',
      title: 'Quantifier Errors',
      desc: 'Use much, many, less, fewer, a few, a little, and other quantifiers correctly with countable and uncountable nouns.',
    },
    {
      color: 'teal',
      title: 'Redundancy',
      desc: 'Identify and eliminate unnecessary word repetition and redundant phrases that weaken your writing style and reduce your grammar score.',
    },
  ];

  const colorMap: Record<string, string> = {
    blue: 'bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 border-blue-200 dark:border-blue-700',
    green: 'bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border-green-200 dark:border-green-700',
    purple: 'bg-gradient-to-br from-purple-50 to-violet-50 dark:from-purple-900/20 dark:to-violet-900/20 border-purple-200 dark:border-purple-700',
    amber: 'bg-gradient-to-br from-amber-50 to-yellow-50 dark:from-amber-900/20 dark:to-yellow-900/20 border-amber-200 dark:border-amber-700',
    rose: 'bg-gradient-to-br from-rose-50 to-pink-50 dark:from-rose-900/20 dark:to-pink-900/20 border-rose-200 dark:border-rose-700',
    teal: 'bg-gradient-to-br from-teal-50 to-cyan-50 dark:from-teal-900/20 dark:to-cyan-900/20 border-teal-200 dark:border-teal-700',
  };

  const badgeMap: Record<string, string> = {
    blue: 'bg-blue-600',
    green: 'bg-green-600',
    purple: 'bg-purple-600',
    amber: 'bg-amber-500',
    rose: 'bg-rose-600',
    teal: 'bg-teal-600',
  };

  return (
    <div className="max-w-5xl mx-auto">
      {/* HERO SECTION */}
      <section className="mb-16">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <h1 className="font-heading text-4xl md:text-5xl lg:text-6xl font-extrabold text-slate-900 dark:text-slate-100 mb-6 leading-tight">
              Common English Grammar Mistakes{' '}
              <span className="text-blue-600 dark:text-blue-400">PDF</span>
            </h1>
            <p className="text-lg md:text-xl text-slate-600 dark:text-slate-400 mb-8 leading-relaxed">
              Identify and correct 95+ of the most frequent grammar errors in English. Clear rules, practical examples, a self-test quiz, and a printable cheat sheet — all in one free handbook.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 mb-4">
              <a
                href="/downloads/Common_English_Grammar_Mistakes.pdf"
                download
                className="inline-flex items-center justify-center px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all duration-200 text-center"
              >
                <Download className="h-5 w-5 mr-2" />
                Download Free PDF
              </a>
              <a
                href="#contents"
                className="inline-flex items-center justify-center px-8 py-4 bg-white dark:bg-slate-800 border-2 border-blue-600 dark:border-blue-500 text-blue-600 dark:text-blue-400 font-semibold rounded-lg hover:bg-blue-50 dark:hover:bg-slate-700 transition-all duration-200"
              >
                What's Inside
              </a>
            </div>
            <p className="text-sm text-slate-500 dark:text-slate-400 italic">
              Free download. No signup required.
            </p>
          </div>
          <div className="flex justify-center">
            <img
              src="/images/books/Common_English_grammar_mistakes.jpg"
              alt="Common English Grammar Mistakes Handbook PDF cover by TypoGrammar featuring a modern grammar reference book for ESL learners, IELTS, TOEFL, and English students"
              className="rounded-xl shadow-2xl max-w-full h-auto"
              loading="eager"
              decoding="async"
            />
          </div>
        </div>
      </section>

      {/* Stats Strip */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
        {[
          { icon: <AlertCircle className="h-6 w-6 text-blue-600" />, value: '95+', label: 'Grammar Mistakes' },
          { icon: <FileText className="h-6 w-6 text-green-600" />, value: '6', label: 'Categories' },
          { icon: <BookOpen className="h-6 w-6 text-violet-600" />, value: '20', label: 'Quiz Questions' },
          { icon: <Star className="h-6 w-6 text-amber-500" />, value: 'All Levels', label: 'Beginner – Advanced' },
        ].map((stat, i) => (
          <div key={i} className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-4 flex flex-col items-center text-center shadow-sm">
            {stat.icon}
            <div className="font-bold text-slate-900 dark:text-slate-100 mt-2">{stat.value}</div>
            <div className="text-xs text-slate-500 dark:text-slate-400">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* BOOK DETAILS STRIP */}
      <div className="bg-slate-50 dark:bg-slate-800 rounded-xl p-6 mb-12 border border-slate-200 dark:border-slate-700">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
          {[
            { label: 'Title', value: 'Common English Grammar Mistakes Handbook' },
            { label: 'Format', value: 'PDF' },
            { label: 'Mistakes Covered', value: '95+' },
            { label: 'Level', value: 'Beginner to Advanced' },
            { label: 'Publisher', value: 'TypoGrammar' },
            { label: 'Price', value: 'Free' },
          ].map((item, i) => (
            <div key={i}>
              <span className="font-semibold text-slate-500 dark:text-slate-400">{item.label}: </span>
              <span className="text-slate-900 dark:text-slate-100">{item.value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* ABOUT THE HANDBOOK */}
      <section className="mb-16">
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-slate-800 dark:to-slate-900 rounded-2xl p-8 md:p-12 shadow-lg">
          <h2 className="font-heading text-3xl md:text-4xl font-bold text-slate-900 dark:text-slate-100 mb-6">
            About This Handbook
          </h2>
          <div className="space-y-4 text-slate-700 dark:text-slate-300 text-lg leading-relaxed">
            <p>
              Making grammar mistakes is a natural part of learning English, but understanding and correcting those mistakes is one of the fastest ways to improve your fluency. Whether you are studying for IELTS, TOEFL, the Duolingo English Test, Cambridge English exams, or simply want to write and speak more accurately, learning from common grammar mistakes can significantly boost your confidence.
            </p>
            <p>
              The <strong>Common English Grammar Mistakes Handbook PDF</strong> from <strong>TypoGrammar</strong> is a practical reference guide that helps English learners identify, understand, and correct more than <strong>95 of the most common grammar mistakes</strong>. Rather than presenting grammar rules in isolation, this handbook focuses on the real mistakes that learners make every day and explains how to avoid them through clear rules, practical examples, memorable tips, and structured practice.
            </p>
            <p>
              This comprehensive handbook is organized into six color-coded categories, making it easy to navigate and review specific grammar topics whenever you need them. Each mistake includes an explanation of the grammar rule, examples of incorrect and correct usage, multiple example sentences, and helpful learning tips.
            </p>
          </div>
        </div>
      </section>

      {/* SIX CATEGORIES */}
      <section className="mb-16" id="contents">
        <h2 className="font-heading text-3xl md:text-4xl font-bold text-slate-900 dark:text-slate-100 mb-8">
          Six Grammar Categories
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sixCategories.map((cat, i) => (
            <div
              key={i}
              className={`rounded-xl p-6 shadow-md border-2 ${colorMap[cat.color]}`}
            >
              <div className={`inline-block px-3 py-1 rounded-full text-sm font-bold text-white mb-3 ${badgeMap[cat.color]}`}>
                Category {i + 1}
              </div>
              <h3 className="font-semibold text-xl text-slate-900 dark:text-slate-100 mb-3">{cat.title}</h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm">{cat.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* WHAT YOU'LL LEARN */}
      <section className="mb-16">
        <h2 className="font-heading text-3xl md:text-4xl font-bold text-slate-900 dark:text-slate-100 mb-8">
          What You'll Learn
        </h2>
        <div className="grid md:grid-cols-2 gap-4">
          {[
            'Subject-verb agreement mistakes',
            'Common verb form errors',
            'Frequently confused English words',
            'Preposition mistakes and correct usage',
            'Quantifier errors with much, many, less, and fewer',
            'Redundancy and unnecessary word repetition',
            'Practical grammar rules with real-life examples',
            'Grammar tips to help you avoid common mistakes',
            'Practice quiz with 20 questions',
            'Complete answer key and explanations',
            'Quick reference grammar cheat sheet',
          ].map((item, i) => (
            <div key={i} className="flex items-start bg-white dark:bg-slate-800 rounded-xl p-4 shadow-sm border border-slate-200 dark:border-slate-700">
              <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
              <span className="text-slate-700 dark:text-slate-300">{item}</span>
            </div>
          ))}
        </div>
      </section>

      {/* WHAT'S INCLUDED */}
      <section className="mb-16">
        <h2 className="font-heading text-3xl md:text-4xl font-bold text-slate-900 dark:text-slate-100 mb-8">
          What's Included
        </h2>
        <div className="bg-white dark:bg-slate-800 rounded-2xl p-8 md:p-12 shadow-lg border border-slate-200 dark:border-slate-700">
          <p className="text-slate-600 dark:text-slate-400 mb-6 text-lg">
            This PDF handbook is designed as a quick-reference guide you can use while studying, writing essays, preparing for exams, or teaching English.
          </p>
          <div className="grid md:grid-cols-2 gap-4">
            {[
              'More than 95 common English grammar mistakes',
              'Six organized grammar categories',
              'Simple rule explanations',
              'Hundreds of correct and incorrect sentence examples',
              'Easy-to-follow grammar tips',
              'A 20-question self-test quiz',
              'Detailed answer key',
              'A printable grammar cheat sheet for quick revision',
            ].map((item, i) => (
              <div key={i} className="flex items-center">
                <Check className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                <span className="text-slate-700 dark:text-slate-300">{item}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* EXAM BENEFITS */}
      <section className="mb-16">
        <h2 className="font-heading text-3xl md:text-4xl font-bold text-slate-900 dark:text-slate-100 mb-8">
          How This Handbook Helps Exam Candidates
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            {
              exam: 'IELTS',
              color: 'blue',
              icon: <Target className="h-6 w-6 text-blue-600 dark:text-blue-400" />,
              benefits: ['Writing Task 1 & Task 2 accuracy', 'Grammatical Range & Accuracy score', 'Speaking error reduction', 'Academic grammar register'],
            },
            {
              exam: 'TOEFL',
              color: 'green',
              icon: <Award className="h-6 w-6 text-green-600 dark:text-green-400" />,
              benefits: ['Integrated & Independent Writing', 'Academic sentence accuracy', 'Speaking task grammar', 'Error-free responses'],
            },
            {
              exam: 'Cambridge & Duolingo',
              color: 'purple',
              icon: <BookMarked className="h-6 w-6 text-purple-600 dark:text-purple-400" />,
              benefits: ['Use of English accuracy', 'Writing task grammar', 'Error avoidance strategies', 'Grammar range improvement'],
            },
          ].map((exam, i) => (
            <div key={i} className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow duration-200">
              <div
                className={`w-12 h-12 rounded-lg flex items-center justify-center mb-4 ${
                  exam.color === 'blue'
                    ? 'bg-blue-100 dark:bg-blue-900'
                    : exam.color === 'green'
                    ? 'bg-green-100 dark:bg-green-900'
                    : 'bg-purple-100 dark:bg-purple-900'
                }`}
              >
                {exam.icon}
              </div>
              <h3 className="font-semibold text-xl text-slate-900 dark:text-slate-100 mb-3">{exam.exam}</h3>
              <ul className="space-y-2">
                {exam.benefits.map((b, j) => (
                  <li key={j} className="flex items-center text-sm text-slate-600 dark:text-slate-400">
                    <Check className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
                    {b}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      {/* WHO IS THIS FOR */}
      <section className="mb-16">
        <h2 className="font-heading text-3xl md:text-4xl font-bold text-slate-900 dark:text-slate-100 mb-8">
          Who Is This Handbook For?
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            {
              icon: <Users className="h-6 w-6 text-blue-600 dark:text-blue-400" />,
              bg: 'bg-blue-100 dark:bg-blue-900',
              title: 'English Learners',
              desc: 'ESL and EFL learners at any level who want to eliminate common mistakes and write and speak more accurately.',
            },
            {
              icon: <Target className="h-6 w-6 text-green-600 dark:text-green-400" />,
              bg: 'bg-green-100 dark:bg-green-900',
              title: 'Exam Candidates',
              desc: 'IELTS, TOEFL, Duolingo English Test, and Cambridge English candidates who need accurate grammar for higher scores.',
            },
            {
              icon: <BookMarked className="h-6 w-6 text-purple-600 dark:text-purple-400" />,
              bg: 'bg-purple-100 dark:bg-purple-900',
              title: 'Students, Teachers & Professionals',
              desc: 'University students, self-study learners, English teachers, and professionals who want to improve their writing accuracy.',
            },
          ].map((item, i) => (
            <div key={i} className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow duration-200">
              <div className={`w-12 h-12 ${item.bg} rounded-lg flex items-center justify-center mb-4`}>
                {item.icon}
              </div>
              <h3 className="font-semibold text-xl text-slate-900 dark:text-slate-100 mb-3">{item.title}</h3>
              <p className="text-slate-600 dark:text-slate-400">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* RELATED RESOURCES */}
      <section className="mb-16">
        <h2 className="font-heading text-3xl md:text-4xl font-bold text-slate-900 dark:text-slate-100 mb-8">
          Related Grammar Resources
        </h2>
        <div className="grid md:grid-cols-3 gap-4">
          {[
            {
              title: 'Common Grammar Mistakes',
              desc: 'Browse our full collection of grammar mistake explanations with interactive examples and exercises.',
              to: '/grammar-mistakes/',
              badge: 'Guide',
              color: 'blue',
            },
            {
              title: 'Subject-Verb Agreement',
              desc: 'Master one of the most tested grammar rules with clear examples covering tricky cases.',
              to: '/topics/subject-verb-agreement/',
              badge: 'Topic',
              color: 'blue',
            },
            {
              title: 'IELTS Grammar Master Book',
              desc: 'A comprehensive grammar PDF covering all key IELTS grammar structures and common mistakes.',
              to: '/ielts/grammar-master-book/',
              badge: 'PDF',
              color: 'green',
            },
            {
              title: 'Complete English Grammar PDF',
              desc: 'Free downloadable grammar workbook covering tenses, passive voice, conditionals, and more.',
              to: '/ielts/english-grammar-pdf/',
              badge: 'PDF',
              color: 'green',
            },
            {
              title: 'Common Grammar Mistakes in IELTS Writing',
              desc: 'Targeted guide to the grammar errors that most frequently lower IELTS Writing band scores.',
              to: '/ielts/common-grammar-mistakes-ielts-writing/',
              badge: 'Article',
              color: 'amber',
            },
            {
              title: 'Reported Speech Rules and Examples PDF',
              desc: 'Free PDF covering direct and indirect speech rules, tense changes, and practice exercises.',
              to: '/downloads/reported-speech-rules-examples/',
              badge: 'PDF',
              color: 'green',
            },
          ].map((item, i) => (
            <a
              key={i}
              href={item.to}
              className="block bg-white dark:bg-slate-800 rounded-xl p-5 shadow-sm border border-slate-200 dark:border-slate-700 hover:shadow-md hover:border-blue-300 dark:hover:border-blue-600 transition-all duration-200"
            >
              <span
                className={`inline-block text-xs font-bold px-2 py-0.5 rounded-full mb-2 ${
                  item.color === 'green'
                    ? 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300'
                    : item.color === 'amber'
                    ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300'
                    : 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300'
                }`}
              >
                {item.badge}
              </span>
              <h3 className="font-semibold text-slate-900 dark:text-slate-100 mb-1">{item.title}</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400">{item.desc}</p>
            </a>
          ))}
        </div>
      </section>

      {/* FAQ */}
      <section className="mb-16">
        <h2 className="font-heading text-3xl md:text-4xl font-bold text-slate-900 dark:text-slate-100 mb-8">
          <span className="inline-flex items-center gap-2">
            <HelpCircle className="h-7 w-7 text-blue-600" />
            Frequently Asked Questions
          </span>
        </h2>
        <div className="space-y-4">
          {faqItems.map((item, index) => (
            <div key={index} className="bg-slate-50 dark:bg-slate-800 rounded-lg p-6 border border-slate-200 dark:border-slate-700">
              <h3 className="font-semibold text-lg text-slate-900 dark:text-slate-100 mb-2">{item.question}</h3>
              <p className="text-slate-700 dark:text-slate-300">{item.answer}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ABOUT TYPOGRAMMAR */}
      <section className="mb-12">
        <div className="bg-gradient-to-r from-slate-50 to-slate-100 dark:from-slate-800 dark:to-slate-900 rounded-2xl p-8 md:p-12 shadow-lg border border-slate-200 dark:border-slate-700">
          <h2 className="font-heading text-3xl md:text-4xl font-bold text-slate-900 dark:text-slate-100 mb-6">
            About TypoGrammar
          </h2>
          <p className="text-lg text-slate-700 dark:text-slate-300 mb-4 leading-relaxed">
            TypoGrammar is a comprehensive English-learning platform dedicated to mastering grammar, building academic vocabulary, and achieving success in IELTS, TOEFL, and other English proficiency exams. Our materials emphasize clear explanations, practical examples, and real-world usage.
          </p>
          <p className="text-lg text-slate-700 dark:text-slate-300 mb-6 leading-relaxed">
            Thousands of learners use TypoGrammar resources to improve their English skills and achieve their language goals.
          </p>
          <div className="flex flex-wrap gap-4">
            <a
              href="/"
              className="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors duration-200"
            >
              Visit Homepage
            </a>
            <a
              href="/ielts/academic-vocabulary-book/"
              className="inline-flex items-center px-6 py-3 bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 font-semibold rounded-lg border-2 border-blue-600 dark:border-blue-500 hover:bg-blue-50 dark:hover:bg-slate-600 transition-colors duration-200"
            >
              Explore More Free PDFs
            </a>
          </div>
        </div>
      </section>

      {/* FINAL CTA */}
      <section className="text-center mb-12">
        <div className="bg-blue-600 dark:bg-blue-700 rounded-2xl p-8 md:p-12 shadow-2xl">
          <h2 className="font-heading text-3xl md:text-4xl font-bold text-white mb-4">
            Start Correcting Your Grammar Today
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Download the Common English Grammar Mistakes Handbook and eliminate the errors that most often reduce grammar accuracy in writing and speaking.
          </p>
          <a
            href="/downloads/Common_English_Grammar_Mistakes.pdf"
            download
            className="inline-flex items-center justify-center px-10 py-5 bg-white text-blue-600 font-bold text-lg rounded-lg shadow-lg hover:shadow-xl hover:bg-blue-50 transition-all duration-200"
          >
            <Download className="h-6 w-6 mr-3" />
            Download Free PDF
          </a>
        </div>
      </section>
    </div>
  );
};

export default CommonEnglishGrammarMistakesPDFPage;
