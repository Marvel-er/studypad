
import React from 'react';
import { ArticleParagraph, ArticleHeading } from '../components/ArticleComponents';
import GoogleAd from '../components/GoogleAd';
import usePageMetadata from '../hooks/usePageMetadata';

const AboutPage: React.FC = () => {
  usePageMetadata({
    title: 'About TypoGrammar | Free English Grammar Learning Platform',
    description: 'TypoGrammar is a free English grammar learning platform for ESL learners, IELTS & TOEFL students, and anyone who wants to master English writing, vocabulary, and grammar.',
  });

  return (
    <article className="max-w-4xl mx-auto bg-white p-8 md:p-12 rounded-xl shadow-lg shadow-slate-200/50 border border-slate-200 dark:bg-slate-800/50 dark:border-slate-700 dark:shadow-slate-900/50">
      <div className="flex justify-between items-start">
        <h1 className="font-heading text-4xl md:text-5xl font-extrabold text-slate-900 mb-8 tracking-tight dark:text-slate-100">About TypoGrammar</h1>
      </div>

      <ArticleParagraph>
        TypoGrammar was born from a simple idea: learning English grammar shouldn't be complicated or boring. We believe that a clean, beautiful, and intuitive interface can make a world of difference in the learning experience. Our goal is to provide clear, concise, and accurate grammar explanations that are easy to understand and a joy to read.
      </ArticleParagraph>

      <ArticleParagraph>
        English is the most widely spoken language in the world, serving as the primary means of communication in business, education, science, and international relations. Yet for millions of learners around the globe — ESL students, IELTS candidates, TOEFL test-takers, and working professionals — mastering English grammar can feel like an overwhelming challenge. That's where TypoGrammar comes in.
      </ArticleParagraph>

      <ArticleHeading>Our Mission</ArticleHeading>
      <ArticleParagraph>
        Our mission is to empower every English learner to communicate more effectively and confidently. We aim to be a reliable and friendly guide on your journey to mastering English grammar, writing, and vocabulary — whether you are preparing for IELTS, studying for the TOEFL, or simply building your everyday communication skills.
      </ArticleParagraph>

      <ArticleParagraph>
        We believe that everyone deserves access to high-quality educational resources, regardless of their location or financial circumstances. That's why TypoGrammar is completely free. We are supported by advertising, which allows us to keep all content accessible to learners worldwide while maintaining the quality and depth you'd expect from a premium platform.
      </ArticleParagraph>

      <ArticleHeading>Who TypoGrammar Helps</ArticleHeading>
      <ArticleParagraph>
        TypoGrammar serves a diverse community of learners from all walks of life:
      </ArticleParagraph>
      <ArticleParagraph>
        <strong>ESL / EFL students</strong> building foundational English grammar skills from the ground up. <strong>IELTS candidates</strong> targeting Band 6.5, 7, or higher who need to master grammar, vocabulary, writing task structures, and speaking fluency. <strong>TOEFL test-takers</strong> preparing for the Reading, Writing, and Speaking sections of the iBT. <strong>University students</strong> writing academic essays and research papers. <strong>Professionals</strong> crafting business emails, reports, and presentations in English. <strong>Teachers and educators</strong> looking for reliable, well-sourced grammar reference materials.
      </ArticleParagraph>
      <ArticleParagraph>
        No matter your background or current level, you will find structured, accurate resources here — from beginner grammar fundamentals to advanced writing techniques.
      </ArticleParagraph>

      <ArticleHeading>What You'll Learn</ArticleHeading>
      <ArticleParagraph>
        TypoGrammar covers the full spectrum of English language learning:
      </ArticleParagraph>
      <ArticleParagraph>
        <strong>English Grammar:</strong> Verb tenses, subject-verb agreement, articles, prepositions, modals, conditionals, passive voice, reported speech, and every common grammar mistake explained with real examples.
      </ArticleParagraph>
      <ArticleParagraph>
        <strong>Vocabulary:</strong> Collocations, phrasal verbs, idioms, homophones, prefixes and suffixes, commonly confused words, and topic-specific vocabulary for IELTS and TOEFL.
      </ArticleParagraph>
      <ArticleParagraph>
        <strong>Writing Skills:</strong> How to write essays (opinion, discussion, problem-solution, advantages/disadvantages), professional emails, paraphrasing, argument building, and sentence variety — essential for IELTS Writing Task 2 and TOEFL Integrated Writing.
      </ArticleParagraph>
      <ArticleParagraph>
        <strong>IELTS Preparation:</strong> Band-specific vocabulary lists (Band 6–9), writing task samples, speaking question banks, listening mock tests, reading score conversion guides, and strategy articles.
      </ArticleParagraph>
      <ArticleParagraph>
        <strong>TOEFL Preparation:</strong> Reading section strategies, question type breakdowns, writing templates, speaking practice, and full practice tests in the 2026 iBT format.
      </ArticleParagraph>

      <ArticleHeading>Why Trust TypoGrammar</ArticleHeading>
      <ArticleParagraph>
        Every article and resource on TypoGrammar is written and reviewed by experienced English educators who understand both the technical aspects of English grammar and the real challenges learners face. We prioritize accuracy, clarity, and practical application over jargon and theory.
      </ArticleParagraph>
      <ArticleParagraph>
        <strong>Clarity first:</strong> We break complex grammar rules into simple, digestible explanations with practical, real-world examples. <strong>Design matters:</strong> A clean reading environment reduces cognitive load so you can focus entirely on learning. <strong>Continuously updated:</strong> We regularly add new content, refine explanations, and update resources to reflect the latest IELTS and TOEFL formats. <strong>Free and accessible:</strong> No paywalls, no sign-ups required for most content — just reliable English learning resources available to everyone.
      </ArticleParagraph>

      <ArticleHeading>Our Vision</ArticleHeading>
      <ArticleParagraph>
        We envision a world where every ESL learner — regardless of their country, background, or budget — has access to the same quality of English grammar education that was once reserved for expensive tutors and premium courses. TypoGrammar is committed to closing that gap.
      </ArticleParagraph>
      <ArticleParagraph>
        As we grow, we are expanding into interactive tools (grammar checker, paraphrasing tool, essay topic generator), AI-powered learning features, printable worksheets, and even deeper IELTS and TOEFL test preparation. Our goal is to be the single most useful free English learning platform on the internet — for grammar, vocabulary, writing, and beyond.
      </ArticleParagraph>
      <ArticleParagraph>
        Thank you for choosing TypoGrammar as your learning companion. We are honored to be part of your English learning journey and look forward to supporting your success. If you have questions, suggestions, or feedback, we would love to hear from you — your input helps us build better resources for the entire TypoGrammar community.
      </ArticleParagraph>

      <div className="mt-8">
        <GoogleAd adSlot="6406598038" />
      </div>
    </article>
  );
};

export default AboutPage;
