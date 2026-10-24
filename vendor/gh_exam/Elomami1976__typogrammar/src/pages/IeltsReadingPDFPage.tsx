import React, { useEffect } from 'react';
import usePageMetadata from '../hooks/usePageMetadata';
import { Download, Check, Target, Users, TrendingUp, HelpCircle, FileText, Award, Star, CheckCircle, Clock, Layers, AlertTriangle } from 'lucide-react';

const IeltsReadingPDFPage: React.FC = () => {
  usePageMetadata({
    title: 'IELTS Reading PDF (Free Download) — Academic & General Training Guide | TypoGrammar',
    description: 'Download the free IELTS Reading PDF from TypoGrammar. A 48-page guide covering all 14 question types, skimming and scanning, paraphrase recognition, time management, practice passages, and a four-week study plan.',
    canonical: 'https://typogrammar.com/downloads/ielts-reading-practice-pdf/',
    ogTitle: 'IELTS Reading PDF (Free Download) — Academic & General Training Guide | TypoGrammar',
    ogDescription: 'Download the free IELTS Reading PDF from TypoGrammar. A 48-page guide covering all 14 question types, skimming and scanning, paraphrase recognition, time management, practice passages, and a four-week study plan.',
    ogUrl: 'https://typogrammar.com/downloads/ielts-reading-practice-pdf',
    ogImage: 'https://typogrammar.com/images/books/IELTS-reading.jpg',
    ogType: 'book',
    twitterCard: 'summary_large_image',
    twitterTitle: 'IELTS Reading PDF (Free Download) — Academic & General Training Guide | TypoGrammar',
    twitterDescription: 'Download the free IELTS Reading PDF from TypoGrammar. A 48-page guide covering all 14 question types, skimming and scanning, paraphrase recognition, time management, practice passages, and a four-week study plan.',
    twitterImage: 'https://typogrammar.com/images/books/IELTS-reading.jpg',
  });

  useEffect(() => {
    const bookSchema = {
      '@context': 'https://schema.org',
      '@type': 'Book',
      name: 'IELTS Reading: Academic & General Training',
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
      numberOfPages: 48,
      url: 'https://typogrammar.com/downloads/ielts-reading-practice-pdf',
      image: 'https://typogrammar.com/images/books/IELTS-reading.jpg',
      description:
        'A complete preparation guide for IELTS Reading, covering both Academic and General Training modules: all 14 question types, core reading skills, time management strategy, vocabulary and paraphrase, common mistakes, band descriptors, two full practice passages with answer walk-throughs, and a four-week study plan.',
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
      name: 'IELTS Reading PDF',
      learningResourceType: 'ebook',
      about: ['IELTS Reading', 'IELTS Academic', 'IELTS General Training', 'English reading comprehension', 'Test preparation'],
      url: 'https://typogrammar.com/downloads/ielts-reading-practice-pdf',
      description:
        'Download the IELTS Reading PDF. Master all 14 question types, skimming and scanning, paraphrase recognition, and time management for both Academic and General Training Reading modules.',
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
            text: 'Yes. The IELTS Reading PDF is available as a free educational resource from TypoGrammar.',
          },
        },
        {
          '@type': 'Question',
          name: 'How many pages does the guide contain?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'The PDF contains 48 pages covering strategy, skills, practice passages, and a study plan for IELTS Reading.',
          },
        },
        {
          '@type': 'Question',
          name: 'Does it cover both Academic and General Training?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'Yes. Separate chapters explain the Academic Reading module and the General Training Reading module, including how their source material and difficulty progression differ.',
          },
        },
        {
          '@type': 'Question',
          name: 'Does the PDF include practice passages?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'Yes. It includes one full Academic practice passage and one full General Training practice passage, each with questions, a detailed answer walk-through, and a scoring guide.',
          },
        },
        {
          '@type': 'Question',
          name: 'What question types are covered?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'All 14 IELTS Reading question types are covered, including Multiple Choice, True/False/Not Given, Yes/No/Not Given, Matching Headings, Matching Information, Matching Features, Sentence Completion, Summary Completion, Diagram Labelling, and Short-Answer Questions.',
          },
        },
        {
          '@type': 'Question',
          name: 'Is there a study plan included?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'Yes. The final chapter provides a four-week study plan designed to take a Band 6 reader to Band 7, with guidance on adjusting the plan for lower or higher starting bands.',
          },
        },
        {
          '@type': 'Question',
          name: 'What band score is this guide aimed at?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'The guide is written for test-takers aiming for Band 6.5 and above, with detailed band descriptors from Band 5 through Band 9 so you can self-assess your current level.',
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

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) element.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const faqItems = [
    {
      question: 'Is this PDF free?',
      answer: 'Yes. The IELTS Reading PDF is available as a free educational resource from TypoGrammar.',
    },
    {
      question: 'How many pages does the guide contain?',
      answer: 'The PDF contains 48 pages covering strategy, skills, practice passages, and a study plan for IELTS Reading.',
    },
    {
      question: 'Does it cover both Academic and General Training?',
      answer: 'Yes. Separate chapters explain the Academic Reading module and the General Training Reading module, including how their source material and difficulty progression differ.',
    },
    {
      question: 'Does the PDF include practice passages?',
      answer: 'Yes. It includes one full Academic practice passage and one full General Training practice passage, each with questions, a detailed answer walk-through, and a scoring guide.',
    },
    {
      question: 'What question types are covered?',
      answer: 'All 14 IELTS Reading question types are covered, including Multiple Choice, True/False/Not Given, Yes/No/Not Given, Matching Headings, Matching Information, Matching Features, Sentence Completion, Summary Completion, Diagram Labelling, and Short-Answer Questions.',
    },
    {
      question: 'Is there a study plan included?',
      answer: 'Yes. The final chapter provides a four-week study plan designed to take a Band 6 reader to Band 7, with guidance on adjusting the plan for lower or higher starting bands.',
    },
    {
      question: 'What band score is this guide aimed at?',
      answer: 'The guide is written for test-takers aiming for Band 6.5 and above, with detailed band descriptors from Band 5 through Band 9 so you can self-assess your current level.',
    },
  ];

  return (
    <div className="max-w-5xl mx-auto">
      {/* HERO SECTION */}
      <section className="mb-16">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <h1 className="font-heading text-4xl md:text-5xl lg:text-6xl font-extrabold text-slate-900 dark:text-slate-100 mb-6 leading-tight">
              IELTS Reading{' '}
              <span className="text-blue-600 dark:text-blue-400">PDF</span>
            </h1>
            <p className="text-lg md:text-xl text-slate-600 dark:text-slate-400 mb-8 leading-relaxed">
              A complete preparation guide for both Academic and General Training Reading. 48 pages covering all 14 question types, skimming and scanning, paraphrase recognition, time management, two full practice passages, and a four-week study plan.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 mb-4">
              <a
                href="/downloads/IELTS-Reading.pdf"
                download
                className="inline-flex items-center justify-center px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all duration-200 text-center"
              >
                <Download className="h-5 w-5 mr-2" />
                Download Free PDF
              </a>
              <button
                onClick={() => scrollToSection('contents')}
                className="inline-flex items-center justify-center px-8 py-4 bg-white dark:bg-slate-800 border-2 border-blue-600 dark:border-blue-500 text-blue-600 dark:text-blue-400 font-semibold rounded-lg hover:bg-blue-50 dark:hover:bg-slate-700 transition-all duration-200"
              >
                What's Inside
              </button>
            </div>
            <p className="text-sm text-slate-500 dark:text-slate-400 italic">
              Free download. No signup required.
            </p>
          </div>
          <div className="flex justify-center">
            <img
              src="/images/books/IELTS-reading.jpg"
              alt="IELTS Reading PDF by TypoGrammar covering Academic and General Training question types, strategies, and practice passages."
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
          { icon: <FileText className="h-6 w-6 text-blue-600" />, value: '48', label: 'Pages' },
          { icon: <Download className="h-6 w-6 text-green-600" />, value: 'Free', label: 'PDF Download' },
          { icon: <Layers className="h-6 w-6 text-violet-600" />, value: '14', label: 'Question Types' },
          { icon: <Star className="h-6 w-6 text-amber-500" />, value: 'Band 6.5+', label: 'Target Level' },
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
            { label: 'Title', value: 'IELTS Reading: Academic & General Training' },
            { label: 'Format', value: 'PDF' },
            { label: 'Pages', value: '48' },
            { label: 'Level', value: 'Band 5 to Band 9' },
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

      {/* WHAT YOU'LL GET */}
      <section className="mb-16">
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-slate-800 dark:to-slate-900 rounded-2xl p-8 md:p-12 shadow-lg">
          <h2 className="font-heading text-3xl md:text-4xl font-bold text-slate-900 dark:text-slate-100 mb-8">
            What This Guide Covers
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            {[
              { title: 'All 14 Question Types', desc: 'Clear explanations and tactics for every question type that appears in IELTS Reading.' },
              { title: 'Academic & General Training', desc: 'Dedicated chapters for both test versions, covering source material and difficulty progression.' },
              { title: 'Skimming, Scanning & Inference', desc: 'The three reading modes explained, plus how to recognise paraphrase and read between the lines.' },
              { title: 'The 20-20-15-5 Framework', desc: 'A per-passage time management strategy for the sixty-minute, forty-question test.' },
              { title: 'Two Full Practice Passages', desc: 'One Academic and one General Training passage, each with questions and a worked answer walk-through.' },
              { title: 'Band Descriptors Decoded', desc: 'What separates Band 5 from Band 9 readers, so you can self-assess and target your next band.' },
            ].map((item, i) => (
              <div key={i} className="flex items-start">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center mr-4 mt-1">
                  <Check className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg text-slate-900 dark:text-slate-100 mb-1">{item.title}</h3>
                  <p className="text-slate-600 dark:text-slate-400">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* WHAT'S INSIDE (TABLE OF CONTENTS) */}
      <section className="mb-16" id="contents">
        <h2 className="font-heading text-3xl md:text-4xl font-bold text-slate-900 dark:text-slate-100 mb-8">
          What's Inside
        </h2>
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {[
            {
              part: 'Part 1',
              title: 'Foundations',
              color: 'green',
              desc: 'Understand what IELTS Reading actually tests, how Academic and General Training differ, and how the band score is calculated.',
              topics: ['Introduction to IELTS Reading', 'Academic Reading in Detail', 'General Training Reading in Detail', 'The Fourteen Question Types'],
            },
            {
              part: 'Part 2',
              title: 'Skills & Strategy',
              color: 'blue',
              desc: 'Build the core reading skills and exam technique that lift your score independently of vocabulary size.',
              topics: ['Core Reading Skills', 'Time Management & Test Strategy', 'Vocabulary & Paraphrase', 'Common Mistakes and How to Avoid Them'],
            },
            {
              part: 'Part 3',
              title: 'Practice & Plan',
              color: 'purple',
              desc: 'Apply what you have learned to real passages, then follow a structured plan to your target band.',
              topics: ['Band Descriptors Decoded', 'Practice Passage: Academic', 'Practice Passage: General Training', 'Four-Week Study Plan'],
            },
          ].map((part, i) => (
            <div
              key={i}
              className={`rounded-xl p-8 shadow-md border-2 ${
                part.color === 'green'
                  ? 'bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border-green-200 dark:border-green-700'
                  : part.color === 'blue'
                  ? 'bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 border-blue-200 dark:border-blue-700'
                  : 'bg-gradient-to-br from-purple-50 to-violet-50 dark:from-purple-900/20 dark:to-violet-900/20 border-purple-200 dark:border-purple-700'
              }`}
            >
              <div
                className={`inline-block px-3 py-1 rounded-full text-sm font-bold mb-3 ${
                  part.color === 'green'
                    ? 'bg-green-600 text-white'
                    : part.color === 'blue'
                    ? 'bg-blue-600 text-white'
                    : 'bg-purple-600 text-white'
                }`}
              >
                {part.part}
              </div>
              <h3 className="font-semibold text-xl text-slate-900 dark:text-slate-100 mb-3">{part.title}</h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm mb-4">{part.desc}</p>
              <ul className="space-y-1">
                {part.topics.map((topic, j) => (
                  <li key={j} className="flex items-center text-sm text-slate-600 dark:text-slate-400">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
                    {topic}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      {/* QUESTION TYPES */}
      <section className="mb-16">
        <h2 className="font-heading text-3xl md:text-4xl font-bold text-slate-900 dark:text-slate-100 mb-8">
          All 14 Question Types, Explained
        </h2>
        <div className="bg-white dark:bg-slate-800 rounded-2xl p-8 md:p-12 shadow-lg border border-slate-200 dark:border-slate-700">
          <p className="text-slate-600 dark:text-slate-400 mb-6 text-lg">
            Every question type that can appear in IELTS Reading gets its own strategy, with worked examples and common pitfalls.
          </p>
          <div className="grid md:grid-cols-2 gap-3">
            {[
              'Multiple Choice',
              'Identifying Information (True / False / Not Given)',
              "Identifying Writer's Views (Yes / No / Not Given)",
              'Matching Information',
              'Matching Headings',
              'Matching Features',
              'Matching Sentence Endings',
              'Sentence Completion',
              'Summary, Notes, Table & Flow-Chart Completion',
              'Diagram Label Completion',
              'Short-Answer Questions',
            ].map((item, i) => (
              <div key={i} className="flex items-center">
                <CheckCircle className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                <span className="text-slate-700 dark:text-slate-300">{item}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* TIME MANAGEMENT */}
      <section className="mb-16">
        <h2 className="font-heading text-3xl md:text-4xl font-bold text-slate-900 dark:text-slate-100 mb-8">
          The 20-20-15-5 Time Management Framework
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            { icon: <Clock className="h-6 w-6 text-blue-600 dark:text-blue-400" />, title: 'The Sixty-Minute Reality', desc: 'Forty questions, sixty minutes, no extra transfer time. Reading is the most time-pressured module in the exam.' },
            { icon: <Target className="h-6 w-6 text-green-600 dark:text-green-400" />, title: 'Per-Passage Pacing', desc: 'A repeatable rhythm for each passage: skim for structure, scan for keywords, then intensive-read only what matters.' },
            { icon: <AlertTriangle className="h-6 w-6 text-amber-500" />, title: 'Skip-and-Return Discipline', desc: 'Never spend more than three minutes on one question. Mark it, move on, and return if time allows.' },
          ].map((item, i) => (
            <div key={i} className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow duration-200">
              <div className="w-12 h-12 bg-slate-100 dark:bg-slate-700 rounded-lg flex items-center justify-center mb-4">
                {item.icon}
              </div>
              <h3 className="font-semibold text-xl text-slate-900 dark:text-slate-100 mb-3">{item.title}</h3>
              <p className="text-slate-600 dark:text-slate-400">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* COMMON MISTAKES */}
      <section className="mb-16">
        <h2 className="font-heading text-3xl md:text-4xl font-bold text-slate-900 dark:text-slate-100 mb-8">
          The Twelve Mistakes That Cost the Most Marks
        </h2>
        <div className="bg-white dark:bg-slate-800 rounded-2xl p-8 md:p-12 shadow-lg border border-slate-200 dark:border-slate-700">
          <p className="text-slate-600 dark:text-slate-400 mb-6 text-lg">
            The PDF diagnoses the errors that repeatedly cost candidates marks, and shows exactly how to fix each one.
          </p>
          <div className="grid md:grid-cols-2 gap-4">
            {[
              'Confusing Not Given with False',
              'Confusing Not Given with True',
              'Reading the full passage before the questions',
              'Treating every question as intensive reading',
              'Keyword matching without comprehension',
              'Choosing headings based on detail, not main idea',
              'Paraphrasing sentence completion answers',
              'Exceeding the word limit',
              'Spending too long on hard questions',
              'Misaligning answers on the answer sheet',
              'Misspelling answers',
              'Leaving blanks',
            ].map((item, i) => (
              <div key={i} className="flex items-center">
                <CheckCircle className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                <span className="text-slate-700 dark:text-slate-300">{item}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* WHO THIS IS FOR */}
      <section className="mb-16">
        <h2 className="font-heading text-3xl md:text-4xl font-bold text-slate-900 dark:text-slate-100 mb-8">
          Who Should Download This PDF?
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            { icon: <Users className="h-6 w-6 text-blue-600 dark:text-blue-400" />, bg: 'bg-blue-100 dark:bg-blue-900', title: 'IELTS Candidates', desc: 'Academic and General Training candidates preparing for the Reading module.' },
            { icon: <TrendingUp className="h-6 w-6 text-green-600 dark:text-green-400" />, bg: 'bg-green-100 dark:bg-green-900', title: 'Band 6 → Band 7 Learners', desc: 'Test-takers with a solid vocabulary base who need sharper strategy and time management.' },
            { icon: <Award className="h-6 w-6 text-purple-600 dark:text-purple-400" />, bg: 'bg-purple-100 dark:bg-purple-900', title: 'Teachers & Self-Study Learners', desc: 'IELTS instructors and independent learners who want a structured, exam-realistic reference.' },
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

      {/* STUDY PLAN */}
      <section className="mb-16">
        <h2 className="font-heading text-3xl md:text-4xl font-bold text-slate-900 dark:text-slate-100 mb-8">
          Four-Week Study Plan: Band 6 to Band 7
        </h2>
        <div className="bg-white dark:bg-slate-800 rounded-2xl p-8 md:p-12 shadow-lg">
          <ol className="space-y-6">
            {[
              { step: '1', title: 'Week 1: Diagnostic and Foundation', desc: 'Take one full timed practice test, audit every wrong answer, and identify your two biggest weaknesses.' },
              { step: '2', title: 'Week 2: Skill Building', desc: 'Focused daily drills on your two priority weaknesses, interleaved with reading on question types, core skills, and time management.' },
              { step: '3', title: 'Week 3: Full Practice', desc: 'Three full timed practice tests on alternate days, each followed by a detailed audit and remediation session.' },
              { step: '4', title: 'Week 4: Rehearsal and Taper', desc: 'A final practice test, review of priority weaknesses, a half-length rehearsal, a full rest day, and then test day.' },
            ].map((item) => (
              <li key={item.step} className="flex items-start">
                <div className="flex-shrink-0 w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-lg mr-4">
                  {item.step}
                </div>
                <div className="pt-1">
                  <h3 className="font-semibold text-xl text-slate-900 dark:text-slate-100 mb-2">{item.title}</h3>
                  <p className="text-slate-600 dark:text-slate-400">{item.desc}</p>
                </div>
              </li>
            ))}
          </ol>
          <p className="text-slate-600 dark:text-slate-400 mt-6 text-sm">
            Starting from Band 5? The guide shows how to extend the plan to six weeks. Targeting Band 8 from Band 7? It shows how to compress it to three.
          </p>
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
            TypoGrammar is a comprehensive English-learning platform dedicated to mastering grammar, building academic vocabulary, and achieving success in IELTS, TOEFL, and the Duolingo English Test. Our materials emphasize clear explanations, practical examples, and exam-realistic practice.
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
              href="/ielts/tests/"
              className="inline-flex items-center px-6 py-3 bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 font-semibold rounded-lg border-2 border-blue-600 dark:border-blue-500 hover:bg-blue-50 dark:hover:bg-slate-600 transition-colors duration-200"
            >
              Explore More IELTS Resources
            </a>
          </div>
        </div>
      </section>

      {/* FINAL CTA */}
      <section className="text-center mb-12">
        <div className="bg-blue-600 dark:bg-blue-700 rounded-2xl p-8 md:p-12 shadow-2xl">
          <h2 className="font-heading text-3xl md:text-4xl font-bold text-white mb-4">
            Start Mastering IELTS Reading Today
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Download the IELTS Reading PDF and follow a proven strategy to your target band.
          </p>
          <a
            href="/downloads/IELTS-Reading.pdf"
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

export default IeltsReadingPDFPage;
