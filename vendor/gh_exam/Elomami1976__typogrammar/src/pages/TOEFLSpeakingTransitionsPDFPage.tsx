import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import usePageMetadata from '../hooks/usePageMetadata';
import { ArticleParagraph, ArticleHeading, BulletList } from '../components/ArticleComponents';
import MiniQuiz from '../components/MiniQuiz';
import { Download, FileText, Globe, GraduationCap, BookOpen, Users, CheckCircle, Sparkles, Target, RefreshCw } from 'lucide-react';

const TOEFLSpeakingTransitionsPDFPage: React.FC = () => {
  usePageMetadata({
    title: 'Top 100 TOEFL Speaking Transitions PDF (Free Download) | TypoGrammar',
    description: 'Download the free Top 100 Transitional Words & Phrases PDF to score 26+ on TOEFL Speaking. 104 pages of transitions, templates, model answers, and daily practice plans.',
    canonical: 'https://typogrammar.com/toefl/top-100-transitional-words-toefl-speaking-pdf/',
    ogTitle: 'Top 100 TOEFL Speaking Transitions PDF (Free Download) | TypoGrammar',
    ogDescription: 'Download the free Top 100 Transitional Words & Phrases PDF to score 26+ on TOEFL Speaking. 104 pages of transitions, templates, model answers, and daily practice plans.',
    ogUrl: 'https://typogrammar.com/toefl/top-100-transitional-words-toefl-speaking-pdf',
    ogImage: 'https://typogrammar.com/images/books/top-100-transitional-words-toefl-speaking-pdf-cover.webp',
    ogType: 'book',
    twitterCard: 'summary_large_image',
    twitterTitle: 'Top 100 TOEFL Speaking Transitions PDF (Free Download) | TypoGrammar',
    twitterDescription: 'Download the free Top 100 Transitional Words & Phrases PDF to score 26+ on TOEFL Speaking. 104 pages of transitions, templates, model answers, and daily practice plans.',
    twitterImage: 'https://typogrammar.com/images/books/top-100-transitional-words-toefl-speaking-pdf-cover.webp',
  });

  const faqItems = [
    {
      q: 'Is this PDF free?',
      a: 'Yes. TypoGrammar offers this ebook as a free learning resource for English learners and TOEFL candidates.',
    },
    {
      q: 'Is this suitable for beginners?',
      a: 'The guide is best suited for intermediate and advanced learners, although motivated beginners can also benefit from the structured explanations.',
    },
    {
      q: 'Does this only help TOEFL?',
      a: 'No. The transition words taught in this guide are useful for IELTS Speaking, Duolingo English Test, academic presentations, interviews, classroom discussions, and everyday English conversation.',
    },
    {
      q: 'How long is the ebook?',
      a: 'The guide contains 104 pages filled with explanations, examples, templates, practice exercises, and review materials.',
    },
    {
      q: 'Can teachers use this resource?',
      a: 'Yes. English teachers can use the exercises, examples, flashcards, and practice activities during classroom instruction for educational purposes.',
    },
  ];

  useEffect(() => {
    const bookSchema = {
      '@context': 'https://schema.org',
      '@type': 'Book',
      name: 'Top 100 Transitional Words & Phrases to Score 26+ on TOEFL Speaking',
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
      numberOfPages: '104',
      url: 'https://typogrammar.com/toefl/top-100-transitional-words-toefl-speaking-pdf',
      image: 'https://typogrammar.com/images/books/top-100-transitional-words-toefl-speaking-pdf-cover.webp',
      description:
        'A 104-page guide to the 100 most useful transitional words and phrases for TOEFL Speaking, organized by function, with natural examples, common mistakes, native speaker alternatives, high-scoring templates, band 26+ model answers, and 7/14/30-day practice plans.',
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
      name: 'Top 100 Transitional Words & Phrases to Score 26+ on TOEFL Speaking',
      learningResourceType: 'ebook',
      about: ['TOEFL Speaking', 'Transitional words', 'Discourse markers', 'English fluency', 'ESL speaking practice'],
      url: 'https://typogrammar.com/toefl/top-100-transitional-words-toefl-speaking-pdf',
      description:
        'Download the Top 100 Transitional Words & Phrases PDF. Learn how to connect ideas naturally, organize TOEFL Speaking responses, and avoid the transition mistakes that lower scores.',
    };

    const faqSchema = {
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      mainEntity: faqItems.map((item) => ({
        '@type': 'Question',
        name: item.q,
        acceptedAnswer: {
          '@type': 'Answer',
          text: item.a,
        },
      })),
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const transitionCategories = [
    'Starting ideas',
    'Adding information',
    'Giving examples',
    'Explaining reasons',
    'Showing cause and effect',
    'Comparing ideas',
    'Expressing opinions',
    'Agreeing and disagreeing',
    'Clarifying meaning',
    'Concluding responses',
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-4 text-slate-900 dark:text-slate-100">
        Top 100 Transitional Words &amp; Phrases to Score 26+ on TOEFL Speaking
      </h1>

      <p className="text-xl text-blue-600 dark:text-blue-400 font-medium mb-8">
        Master Natural English Transitions for a Higher TOEFL Speaking Score
      </p>

      <ArticleParagraph>
        Speaking fluently on the TOEFL iBT is about more than grammar and vocabulary. One of the biggest differences between average and high-scoring responses is how smoothly ideas connect. This free TypoGrammar PDF teaches you how to use transitional words and phrases naturally, helping you organize your answers, improve coherence, and sound more like a confident English speaker.
      </ArticleParagraph>
      <ArticleParagraph>
        Whether you are aiming for a TOEFL Speaking score of 26+, preparing for university admission, or simply trying to speak English more naturally, this ebook provides a practical system you can start using immediately.
      </ArticleParagraph>

      {/* Stats Strip */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 my-8">
        {[
          { icon: <FileText className="h-6 w-6 text-blue-600" />, value: 'Free', label: 'Download' },
          { icon: <Download className="h-6 w-6 text-green-600" />, value: '104 Pages', label: '2026 Edition' },
          { icon: <Globe className="h-6 w-6 text-violet-600" />, value: '100', label: 'Transition Phrases' },
          { icon: <GraduationCap className="h-6 w-6 text-amber-500" />, value: 'Score 26+', label: 'Target Speaking' },
        ].map((stat, i) => (
          <div key={i} className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-4 flex flex-col items-center text-center shadow-sm">
            {stat.icon}
            <div className="font-bold text-slate-900 dark:text-slate-100 mt-2">{stat.value}</div>
            <div className="text-xs text-slate-500 dark:text-slate-400">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Download Section */}
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border border-green-200 dark:border-green-800 rounded-xl p-8 my-10 text-center">
        <h2 className="text-2xl font-bold text-green-800 dark:text-green-200 mb-4">
          Download the Free PDF
        </h2>
        <p className="text-green-700 dark:text-green-300 mb-6">
          Improve your fluency, organize your ideas naturally, and learn exactly how high-scoring TOEFL candidates connect their thoughts.
        </p>

        <div className="flex flex-col md:flex-row items-center justify-center gap-6">
          <img
            src="/images/books/top-100-transitional-words-toefl-speaking-pdf-cover.webp"
            alt="Cover of the free TypoGrammar PDF Top 100 Transitional Words and Phrases to Score 26+ on TOEFL Speaking, featuring essential transition words, speaking templates, and fluency strategies for TOEFL iBT preparation"
            className="w-48 h-auto rounded-lg shadow-lg"
            loading="eager"
            decoding="async"
          />
          <a
            href="/downloads/toefl-speaking-transitions.pdf"
            download
            className="inline-flex items-center px-8 py-4 bg-green-600 hover:bg-green-700 text-white font-bold rounded-lg shadow-lg transition-all duration-200 hover:scale-105"
          >
            <Download className="w-6 h-6 mr-2" />
            Download Free PDF
          </a>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-8 text-sm text-left max-w-2xl mx-auto">
          <div className="bg-white/70 dark:bg-slate-800/50 rounded-lg p-3">
            <span className="block text-slate-500 dark:text-slate-400">File Format</span>
            <span className="font-semibold text-slate-800 dark:text-slate-200">PDF</span>
          </div>
          <div className="bg-white/70 dark:bg-slate-800/50 rounded-lg p-3">
            <span className="block text-slate-500 dark:text-slate-400">Pages</span>
            <span className="font-semibold text-slate-800 dark:text-slate-200">104</span>
          </div>
          <div className="bg-white/70 dark:bg-slate-800/50 rounded-lg p-3">
            <span className="block text-slate-500 dark:text-slate-400">Edition</span>
            <span className="font-semibold text-slate-800 dark:text-slate-200">2026</span>
          </div>
          <div className="bg-white/70 dark:bg-slate-800/50 rounded-lg p-3">
            <span className="block text-slate-500 dark:text-slate-400">Level</span>
            <span className="font-semibold text-slate-800 dark:text-slate-200">Intermediate-Advanced</span>
          </div>
          <div className="bg-white/70 dark:bg-slate-800/50 rounded-lg p-3">
            <span className="block text-slate-500 dark:text-slate-400">Price</span>
            <span className="font-semibold text-slate-800 dark:text-slate-200">Free</span>
          </div>
        </div>
      </div>

      {/* What You'll Learn */}
      <ArticleHeading>What You'll Learn</ArticleHeading>
      <ArticleParagraph>
        This ebook goes far beyond providing a simple vocabulary list. It explains why transitions matter, how TOEFL examiners evaluate coherence, and how native speakers naturally connect ideas during conversation.
      </ArticleParagraph>
      <ArticleParagraph>Inside you'll learn how to:</ArticleParagraph>
      <div className="grid md:grid-cols-2 gap-4 my-6">
        {[
          'Organize TOEFL Speaking responses clearly',
          'Sound more fluent and natural',
          'Connect ideas without awkward pauses',
          'Improve coherence and topic development',
          'Avoid repetitive transition words',
          'Use advanced discourse markers correctly',
          'Speak with greater confidence during the TOEFL test',
        ].map((item, index) => (
          <div key={index} className="flex items-center gap-3 p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
            <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0" />
            <span className="text-slate-700 dark:text-slate-300 font-medium">{item}</span>
          </div>
        ))}
      </div>
      <ArticleParagraph>
        The guide follows a complete learning path, beginning with TOEFL Speaking fundamentals before introducing practical transition phrases, templates, practice activities, and review materials.
      </ArticleParagraph>

      {/* What's Inside */}
      <ArticleHeading>What's Inside the PDF?</ArticleHeading>
      <ArticleParagraph>
        The ebook contains over 100 pages of structured learning material, including:
      </ArticleParagraph>

      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-6 my-6">
        <h3 className="text-xl font-bold text-blue-800 dark:text-blue-200 mb-3 flex items-center gap-2">
          <BookOpen className="h-5 w-5" /> Complete TOEFL Speaking Guide
        </h3>
        <ArticleParagraph>
          Learn how the TOEFL Speaking section is structured, what ETS evaluates, and why transitions directly influence fluency, language use, and topic development.
        </ArticleParagraph>
      </div>

      <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-xl p-6 my-6">
        <h3 className="text-xl font-bold text-purple-800 dark:text-purple-200 mb-3 flex items-center gap-2">
          <Sparkles className="h-5 w-5" /> 100 Essential Transitional Words and Phrases
        </h3>
        <ArticleParagraph>Master transitions organized into practical categories such as:</ArticleParagraph>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2 my-4">
          {transitionCategories.map((cat, i) => (
            <div key={i} className="bg-white dark:bg-slate-800 rounded-lg px-3 py-2 text-sm text-center text-purple-800 dark:text-purple-200 font-medium border border-purple-100 dark:border-purple-800">
              {cat}
            </div>
          ))}
        </div>
        <ArticleParagraph>Each transition includes:</ArticleParagraph>
        <BulletList items={[
          'Meaning and function',
          'Natural speaking example',
          'Alternative expressions',
          'Common mistakes',
          'Difficulty level',
        ]} />
      </div>

      <div className="bg-teal-50 dark:bg-teal-900/20 border border-teal-200 dark:border-teal-800 rounded-xl p-6 my-6">
        <h3 className="text-xl font-bold text-teal-800 dark:text-teal-200 mb-3 flex items-center gap-2">
          <Target className="h-5 w-5" /> High-Scoring TOEFL Speaking Templates
        </h3>
        <ArticleParagraph>
          Learn response frameworks designed for all TOEFL Speaking tasks so you always know how to organize your answers under time pressure.
        </ArticleParagraph>
      </div>

      <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl p-6 my-6">
        <h3 className="text-xl font-bold text-amber-800 dark:text-amber-200 mb-3">
          Band 26+ Model Answers
        </h3>
        <ArticleParagraph>
          Study realistic examples that demonstrate how successful candidates naturally integrate transition phrases into complete responses.
        </ArticleParagraph>
      </div>

      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-6 my-6">
        <h3 className="text-xl font-bold text-red-800 dark:text-red-200 mb-3">
          Common Transition Mistakes
        </h3>
        <ArticleParagraph>Avoid the errors that frequently reduce TOEFL Speaking scores, including:</ArticleParagraph>
        <BulletList items={[
          'Overusing the same connector',
          'Choosing the wrong transition',
          'Using formal expressions unnaturally',
          'Creating repetitive sentence patterns',
        ]} />
      </div>

      <div className="bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800 rounded-xl p-6 my-6">
        <h3 className="text-xl font-bold text-indigo-800 dark:text-indigo-200 mb-3">
          Native Speaker Alternatives
        </h3>
        <ArticleParagraph>
          Expand your vocabulary with natural alternatives that make your speaking sound less repetitive and more authentic.
        </ArticleParagraph>
      </div>

      <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl p-6 my-6">
        <h3 className="text-xl font-bold text-green-800 dark:text-green-200 mb-3 flex items-center gap-2">
          <RefreshCw className="h-5 w-5" /> Daily Practice System
        </h3>
        <ArticleParagraph>Build fluency through structured:</ArticleParagraph>
        <BulletList items={[
          '7-day practice plans',
          '14-day improvement plans',
          '30-day mastery schedules',
          'Speaking exercises',
          'Self-evaluation sheets',
          'Progress trackers',
        ]} />
      </div>

      {/* Who Should Read This */}
      <ArticleHeading>Who Should Read This Ebook?</ArticleHeading>
      <ArticleParagraph>This guide is ideal for:</ArticleParagraph>
      <BulletList items={[
        'TOEFL iBT test takers',
        'International university applicants',
        'ESL and EFL learners',
        'English teachers',
        'Academic English students',
        'Anyone preparing for English speaking exams',
        'Learners who want more natural spoken English',
      ]} />
      <ArticleParagraph>
        Whether your current speaking score is 18 or 24, mastering transitions can significantly improve the organization and clarity of your responses.
      </ArticleParagraph>

      {/* Why Transitional Words Matter */}
      <ArticleHeading>Why Transitional Words Matter</ArticleHeading>
      <ArticleParagraph>
        Many English learners focus heavily on vocabulary and grammar but overlook the importance of connecting ideas naturally.
      </ArticleParagraph>
      <ArticleParagraph>Effective transitions help you:</ArticleParagraph>
      <BulletList items={[
        'Guide the listener through your response',
        'Reduce hesitation while speaking',
        'Organize ideas logically',
        'Improve overall coherence',
        'Demonstrate advanced language ability',
        'Sound more like a native speaker',
      ]} />
      <ArticleParagraph>
        Instead of speaking in disconnected sentences, you'll learn how to build smooth, well-organized responses that are easier for TOEFL raters to follow.
      </ArticleParagraph>

      {/* What Makes This Different */}
      <ArticleHeading>What Makes This PDF Different?</ArticleHeading>
      <ArticleParagraph>
        Unlike basic vocabulary lists found online, this guide combines explanation, practice, and real TOEFL strategy. Features include:
      </ArticleParagraph>
      <div className="grid md:grid-cols-2 gap-4 my-6">
        {[
          '100 carefully selected transition phrases',
          'Practical examples for every expression',
          'TOEFL-specific speaking templates',
          'Native speaker alternatives',
          'Practice tests',
          'Flashcards',
          'Quick review sheets',
          'Speaking checklists',
          'Weekly study trackers',
          'Self-assessment forms',
        ].map((item, index) => (
          <div key={index} className="flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
            <Users className="h-4 w-4 text-blue-600 flex-shrink-0" />
            <span className="text-slate-700 dark:text-slate-300 text-sm">{item}</span>
          </div>
        ))}
      </div>
      <ArticleParagraph>
        Everything is organized into a logical learning progression that takes you from understanding transitions to using them confidently during real speaking tasks.
      </ArticleParagraph>

      {/* Related Resources */}
      <ArticleHeading>Related TOEFL Speaking Resources</ArticleHeading>
      <ArticleParagraph>Combine this PDF with these free resources to prepare faster:</ArticleParagraph>
      <BulletList items={[
        <Link to="/toefl/1000-toefl-speaking-questions/" className="text-blue-600 dark:text-blue-400 hover:underline">1000 TOEFL Speaking Questions</Link>,
        <Link to="/toefl/strategy-success/toefl-speaking-average-vs-high-scoring-answer/" className="text-blue-600 dark:text-blue-400 hover:underline">TOEFL Speaking: Average vs High-Scoring Answer</Link>,
        <Link to="/toefl/toefl-writing-pdf/" className="text-blue-600 dark:text-blue-400 hover:underline">TOEFL Writing PDF (Task 1 &amp; 2)</Link>,
        <Link to="/toefl/toefl-vocabulary-pdf/" className="text-blue-600 dark:text-blue-400 hover:underline">TOEFL Vocabulary PDF (500 Words)</Link>,
        <Link to="/toefl/toefl-writing/toefl-writing-task-2-explained/" className="text-blue-600 dark:text-blue-400 hover:underline">TOEFL Writing Task 2 Explained</Link>,
      ]} />

      {/* Final CTA */}
      <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl p-6 my-8 text-center">
        <p className="text-green-800 dark:text-green-200 font-semibold text-lg mb-2">
          Start Speaking More Fluently Today
        </p>
        <p className="text-green-700 dark:text-green-300 mb-4">
          The difference between an average TOEFL Speaking response and an excellent one often comes down to organization and coherence.
        </p>
        <a
          href="/downloads/toefl-speaking-transitions.pdf"
          download
          className="inline-flex items-center px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-bold rounded-lg shadow transition-colors"
        >
          <Download className="w-5 h-5 mr-2" />
          Download Free PDF Now
        </a>
      </div>

      {/* Mini Quiz */}
      <MiniQuiz
        title="TOEFL Speaking Transitions: Quick Self-Check"
        intro="Three sample questions in the style of what's covered inside the PDF."
        questions={[
          {
            question: 'Which transition is BEST for introducing a contrasting idea in a TOEFL Speaking response?',
            options: ['Furthermore', 'In addition', 'However', 'For example'],
            correctAnswer: 2,
            explanation: '"However" signals contrast; the other options signal addition or examples.',
          },
          {
            question: 'A candidate who repeats "and then... and then... and then..." throughout a TOEFL Speaking response is most likely to lose points for:',
            options: ['Pronunciation only', 'Coherence and topic development', 'Grammar accuracy only', 'Vocabulary range only'],
            correctAnswer: 1,
            explanation: 'Overusing the same connector signals weak organization, which lowers the coherence and topic development score.',
          },
          {
            question: 'Which phrase works best to give a reason for an opinion?',
            options: ['On the other hand', 'This is because', 'In conclusion', 'Similarly'],
            correctAnswer: 1,
            explanation: '"This is because" directly introduces a reason, which examiners look for when evaluating topic development.',
          },
        ]}
        cta={{
          to: '/toefl/1000-toefl-speaking-questions/',
          label: 'Practice with 1000 TOEFL Speaking Questions',
          subtitle: 'Apply these transitions to real speaking prompts.',
        }}
      />

      {/* FAQ Section */}
      <ArticleHeading>Frequently Asked Questions (FAQ)</ArticleHeading>
      <div className="space-y-6 my-8">
        {faqItems.map((faq, index) => (
          <div key={index} className="border border-slate-200 dark:border-slate-700 rounded-lg overflow-hidden">
            <div className="bg-slate-50 dark:bg-slate-800 px-5 py-4">
              <h3 className="font-semibold text-slate-800 dark:text-slate-200">{faq.q}</h3>
            </div>
            <div className="px-5 py-4">
              <p className="text-slate-600 dark:text-slate-400">{faq.a}</p>
            </div>
          </div>
        ))}
      </div>

      <ArticleParagraph>
        Download <strong>Top 100 Transitional Words &amp; Phrases to Score 26+ on TOEFL Speaking</strong> today and start building smoother, more organized English responses with practical strategies, real examples, and daily practice activities from TypoGrammar.
      </ArticleParagraph>
    </div>
  );
};

export default TOEFLSpeakingTransitionsPDFPage;
