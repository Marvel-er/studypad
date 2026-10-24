import React, { useEffect } from 'react';
import usePageMetadata from '../hooks/usePageMetadata';
import { Download, Check, BookOpen, Target, Users, HelpCircle, FileText, Award, Star, CheckCircle, BookMarked } from 'lucide-react';

const ReportedSpeechPDFPage: React.FC = () => {
  usePageMetadata({
    title: 'Reported Speech Rules and Examples PDF (Free Download) | TypoGrammar',
    description: 'Download the Reported Speech Rules and Examples PDF from TypoGrammar. Master direct and indirect speech, tense changes, reporting verbs, pronoun shifts, and practice exercises with a complete answer key.',
    canonical: 'https://typogrammar.com/downloads/reported-speech-rules-examples/',
    ogTitle: 'Reported Speech Rules and Examples PDF (Free Download) | TypoGrammar',
    ogDescription: 'Download the Reported Speech Rules and Examples PDF from TypoGrammar. Master direct and indirect speech, tense changes, reporting verbs, pronoun shifts, and practice exercises with a complete answer key.',
    ogUrl: 'https://typogrammar.com/downloads/reported-speech-rules-examples',
    ogImage: 'https://typogrammar.com/images/books/reported_speech_rules_examples.jpg',
    ogType: 'book',
    twitterCard: 'summary_large_image',
    twitterTitle: 'Reported Speech Rules and Examples PDF (Free Download) | TypoGrammar',
    twitterDescription: 'Download the Reported Speech Rules and Examples PDF from TypoGrammar. Master direct and indirect speech, tense changes, reporting verbs, pronoun shifts, and practice exercises with a complete answer key.',
    twitterImage: 'https://typogrammar.com/images/books/reported_speech_rules_examples.jpg',
  });

  useEffect(() => {
    const bookSchema = {
      '@context': 'https://schema.org',
      '@type': 'Book',
      name: 'Reported Speech Rules and Examples',
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
      url: 'https://typogrammar.com/downloads/reported-speech-rules-examples',
      image: 'https://typogrammar.com/images/books/reported_speech_rules_examples.jpg',
      description:
        'A complete grammar workbook covering reported speech rules, direct and indirect speech, reporting verbs, tense changes, pronoun shifts, time expression changes, and extensive practice exercises with a full answer key.',
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
      name: 'Reported Speech Rules and Examples PDF',
      learningResourceType: 'ebook',
      about: ['Reported speech', 'Indirect speech', 'English grammar', 'IELTS grammar', 'TOEFL grammar'],
      url: 'https://typogrammar.com/downloads/reported-speech-rules-examples',
      description:
        'Download the Reported Speech Rules and Examples PDF. Master direct and indirect speech, reporting verbs, tense changes, pronoun and time expression shifts, with hundreds of examples and practice exercises.',
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
            text: 'Yes. The Reported Speech Rules and Examples PDF is available as a free educational resource from TypoGrammar.',
          },
        },
        {
          '@type': 'Question',
          name: 'Is this workbook suitable for beginners?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'Yes. The workbook starts with the basics of direct and indirect speech and progressively covers more advanced reported speech structures.',
          },
        },
        {
          '@type': 'Question',
          name: 'Does this PDF help with IELTS preparation?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'Yes. Reported speech is an important grammar skill for IELTS Writing and Speaking. This workbook includes tips specifically for IELTS and TOEFL candidates.',
          },
        },
        {
          '@type': 'Question',
          name: 'Does the PDF include practice exercises?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'Yes. The workbook contains a wide variety of practice exercises ranging from simple sentence transformations to mixed grammar activities, all with a complete answer key.',
          },
        },
        {
          '@type': 'Question',
          name: 'What grammar topics does this PDF cover?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'The PDF covers direct vs indirect speech, reporting verbs and their patterns, tense changes, pronoun changes, time and place expression changes, reporting statements, questions, commands, requests, suggestions, and advice.',
          },
        },
        {
          '@type': 'Question',
          name: 'Can English teachers use this workbook in the classroom?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'Absolutely. The structured lessons, reference tables, and practice exercises make this workbook an ideal classroom resource for ESL and EFL teachers.',
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
      answer: 'Yes. The Reported Speech Rules and Examples PDF is available as a free educational resource from TypoGrammar.',
    },
    {
      question: 'Is this workbook suitable for beginners?',
      answer: 'Yes. The workbook starts with the basics of direct and indirect speech and progressively covers more advanced reported speech structures.',
    },
    {
      question: 'Does this PDF help with IELTS preparation?',
      answer: 'Yes. Reported speech is an important grammar skill for IELTS Writing and Speaking. This workbook includes tips specifically for IELTS and TOEFL candidates.',
    },
    {
      question: 'Does the PDF include practice exercises?',
      answer: 'Yes. The workbook contains a wide variety of practice exercises ranging from simple sentence transformations to mixed grammar activities, all with a complete answer key.',
    },
    {
      question: 'What grammar topics does this PDF cover?',
      answer: 'The PDF covers direct vs indirect speech, reporting verbs and their patterns, tense changes, pronoun changes, time and place expression changes, reporting statements, questions, commands, requests, suggestions, and advice.',
    },
    {
      question: 'Can English teachers use this workbook in the classroom?',
      answer: 'Absolutely. The structured lessons, reference tables, and practice exercises make this workbook an ideal classroom resource for ESL and EFL teachers.',
    },
  ];

  const whatYoullLearn = [
    'What reported speech is and when to use it',
    'Direct speech vs. indirect speech',
    'Common reporting verbs and their patterns',
    'Tense changes in reported speech',
    'Pronoun changes',
    'Time and place expression changes',
    'Reporting statements',
    'Reporting yes/no questions',
    'Reporting WH questions',
    'Reporting commands and requests',
    'Reporting suggestions and advice',
    'Common reported speech mistakes',
    '100 everyday reported speech examples',
    'Practice exercises with complete answers',
    'Quick reference grammar cheat sheets',
    'Reported speech tips for IELTS and TOEFL',
  ];

  return (
    <div className="max-w-5xl mx-auto">
      {/* HERO SECTION */}
      <section className="mb-16">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <h1 className="font-heading text-4xl md:text-5xl lg:text-6xl font-extrabold text-slate-900 dark:text-slate-100 mb-6 leading-tight">
              Reported Speech Rules and Examples{' '}
              <span className="text-blue-600 dark:text-blue-400">PDF</span>
            </h1>
            <p className="text-lg md:text-xl text-slate-600 dark:text-slate-400 mb-8 leading-relaxed">
              Master direct and indirect speech with clear rules, comprehensive reference tables, hundreds of examples, and practice exercises. Essential for IELTS, TOEFL, Cambridge English, and everyday communication.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 mb-4">
              <a
                href="/downloads/reported_speech_rules_examples.pdf"
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
              src="/images/books/reported_speech_rules_examples.jpg"
              alt="Reported Speech Rules and Examples PDF cover featuring direct and indirect speech grammar guide for English learners by TypoGrammar"
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
          { icon: <FileText className="h-6 w-6 text-blue-600" />, value: 'Free', label: 'PDF Download' },
          { icon: <Download className="h-6 w-6 text-green-600" />, value: '100+', label: 'Examples' },
          { icon: <BookOpen className="h-6 w-6 text-violet-600" />, value: '16', label: 'Topics Covered' },
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
            { label: 'Title', value: 'Reported Speech Rules and Examples' },
            { label: 'Format', value: 'PDF' },
            { label: 'Topic', value: 'English Grammar' },
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

      {/* ABOUT THE WORKBOOK */}
      <section className="mb-16">
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-slate-800 dark:to-slate-900 rounded-2xl p-8 md:p-12 shadow-lg">
          <h2 className="font-heading text-3xl md:text-4xl font-bold text-slate-900 dark:text-slate-100 mb-6">
            About This Grammar Workbook
          </h2>
          <div className="space-y-4 text-slate-700 dark:text-slate-300 text-lg leading-relaxed">
            <p>
              Mastering reported speech is one of the most important steps toward speaking and writing natural, fluent English. Whether you are preparing for the IELTS, TOEFL, Duolingo English Test, Cambridge English exams, or simply improving your everyday communication, understanding how to change direct speech into reported speech is an essential grammar skill.
            </p>
            <p>
              The <strong>Reported Speech Rules and Examples PDF</strong> from <strong>TypoGrammar</strong> is a complete learning guide designed to help English learners understand reported speech from the basics to advanced usage. Instead of memorizing isolated rules, this workbook explains every concept with clear definitions, simple explanations, practical examples, visual tables, and extensive practice exercises.
            </p>
            <p>
              Unlike many grammar books that focus only on theory, this PDF includes hundreds of carefully selected examples that demonstrate how reported speech is used in everyday conversations, academic writing, business communication, and English proficiency exams. Each chapter builds on the previous one, allowing beginners to develop confidence while also serving as a valuable reference for intermediate and advanced learners.
            </p>
          </div>
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
              title: 'Reported Speech',
              desc: 'Practice tense backshift, pronoun changes, and time expression shifts with interactive examples.',
              to: '/topics/reported-speech/',
              badge: 'Topic',
              color: 'blue',
            },
            {
              title: 'Direct & Indirect Speech',
              desc: 'Understand the core difference between quoting exact words and reporting what someone said.',
              to: '/topics/direct-and-indirect-speech/',
              badge: 'Topic',
              color: 'blue',
            },
            {
              title: 'Say vs. Tell',
              desc: 'Master two of the most common and most confused reporting verbs in English.',
              to: '/grammar-mistakes/say-vs-tell/',
              badge: 'Grammar',
              color: 'amber',
            },
            {
              title: 'Question Formation',
              desc: 'Learn how question word order changes when reporting yes/no and WH questions.',
              to: '/topics/question-formation/',
              badge: 'Topic',
              color: 'blue',
            },
            {
              title: 'IELTS Grammar Master Book',
              desc: 'A comprehensive grammar PDF covering all key IELTS grammar structures including reported speech.',
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

      {/* WHAT YOU'LL LEARN */}
      <section className="mb-16" id="contents">
        <h2 className="font-heading text-3xl md:text-4xl font-bold text-slate-900 dark:text-slate-100 mb-8">
          What You'll Learn
        </h2>
        <div className="grid md:grid-cols-2 gap-4">
          {whatYoullLearn.map((item, i) => (
            <div key={i} className="flex items-start bg-white dark:bg-slate-800 rounded-xl p-4 shadow-sm border border-slate-200 dark:border-slate-700">
              <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
              <span className="text-slate-700 dark:text-slate-300">{item}</span>
            </div>
          ))}
        </div>
      </section>

      {/* KEY GRAMMAR AREAS */}
      <section className="mb-16">
        <h2 className="font-heading text-3xl md:text-4xl font-bold text-slate-900 dark:text-slate-100 mb-8">
          Key Grammar Areas Covered
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            {
              color: 'blue',
              title: 'Direct vs Indirect Speech',
              desc: 'Understand the fundamental difference between quoting someone\'s exact words and reporting what they said, with clear rules and dozens of side-by-side comparisons.',
              points: ['Quotation marks vs reporting clauses', 'Backshift of tenses', 'When tenses do not change', 'Punctuation rules'],
            },
            {
              color: 'green',
              title: 'Reporting Verbs & Patterns',
              desc: 'Master the most common reporting verbs in English and learn how each verb controls the grammar structure that follows it.',
              points: ['Say vs tell vs ask', 'Verb + infinitive patterns', 'Verb + gerund patterns', 'Verb + that-clause patterns'],
            },
            {
              color: 'purple',
              title: 'Questions, Commands & Suggestions',
              desc: 'Report all types of speech acts correctly, from yes/no and WH questions to commands, requests, suggestions, and advice.',
              points: ['Yes/No questions → whether/if', 'WH questions → embedded clauses', 'Commands with infinitive', 'Suggestions with gerund or infinitive'],
            },
          ].map((section, i) => (
            <div
              key={i}
              className={`rounded-xl p-8 shadow-md border-2 ${
                section.color === 'blue'
                  ? 'bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 border-blue-200 dark:border-blue-700'
                  : section.color === 'green'
                  ? 'bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border-green-200 dark:border-green-700'
                  : 'bg-gradient-to-br from-purple-50 to-violet-50 dark:from-purple-900/20 dark:to-violet-900/20 border-purple-200 dark:border-purple-700'
              }`}
            >
              <h3 className="font-semibold text-xl text-slate-900 dark:text-slate-100 mb-3">{section.title}</h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm mb-4">{section.desc}</p>
              <ul className="space-y-1">
                {section.points.map((point, j) => (
                  <li key={j} className="flex items-center text-sm text-slate-600 dark:text-slate-400">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
                    {point}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      {/* REFERENCE TABLES */}
      <section className="mb-16">
        <h2 className="font-heading text-3xl md:text-4xl font-bold text-slate-900 dark:text-slate-100 mb-8">
          Comprehensive Reference Tables
        </h2>
        <div className="bg-white dark:bg-slate-800 rounded-2xl p-8 md:p-12 shadow-lg border border-slate-200 dark:border-slate-700">
          <p className="text-slate-600 dark:text-slate-400 mb-6 text-lg">
            The workbook includes quick-reference charts covering all major reported speech transformations so you can review grammar rules at a glance.
          </p>
          <div className="grid md:grid-cols-2 gap-4">
            {[
              'Tense change table (Present → Past, Past → Past Perfect, etc.)',
              'Reporting verb patterns reference',
              'Pronoun change chart',
              'Time expression conversion table',
              'Place expression conversion table',
              'Common reporting verbs with examples',
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
          How This Workbook Helps Exam Candidates
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            {
              exam: 'IELTS',
              color: 'blue',
              icon: <Target className="h-6 w-6 text-blue-600 dark:text-blue-400" />,
              benefits: ['Writing Task 2 accuracy', 'Speaking fluency', 'Grammatical Range score', 'Reporting academic sources'],
            },
            {
              exam: 'TOEFL',
              color: 'green',
              icon: <Award className="h-6 w-6 text-green-600 dark:text-green-400" />,
              benefits: ['Integrated Writing tasks', 'Speaking integrated tasks', 'Academic reading comprehension', 'Paraphrasing sources'],
            },
            {
              exam: 'Cambridge & Duolingo',
              color: 'purple',
              icon: <BookMarked className="h-6 w-6 text-purple-600 dark:text-purple-400" />,
              benefits: ['Use of English sections', 'Writing accuracy', 'Grammar range', 'Formal and academic register'],
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
          Who Is This PDF For?
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            {
              icon: <Users className="h-6 w-6 text-blue-600 dark:text-blue-400" />,
              bg: 'bg-blue-100 dark:bg-blue-900',
              title: 'English Learners',
              desc: 'ESL and EFL learners at any level who want to understand and use reported speech correctly in speaking and writing.',
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
              title: 'Students & Teachers',
              desc: 'High school and university students, self-study learners, and English teachers looking for a structured classroom resource.',
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
            Download the Workbook Today
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Build a stronger understanding of reported speech with clear rules, comprehensive tables, practical exercises, and hundreds of examples.
          </p>
          <a
            href="/downloads/reported_speech_rules_examples.pdf"
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

export default ReportedSpeechPDFPage;
