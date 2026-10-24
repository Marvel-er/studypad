import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Resume vs. CV: What's the Difference? | TypoGrammar",
  metaDescription: "Resume vs CV: in American English, a \"resume\" is a short, targeted 1-2 page job application document, while a \"CV\" is a longer, complete record used in academia and, in British English, for all job applications. See the rule, examples, and a quiz.",
  slug: 'resume-vs-cv',
  h1: "Resume vs. CV: What's the Difference?",
  breadcrumbLabel: 'Resume vs. CV',
  datePublished: '2026-07-05',
  dateModified: '2026-07-05',
  quickAnswer: "In American English, a \"resume\" is a short (usually 1-2 page) summary of your work experience, skills, and education, tailored to a specific job. A \"CV\" (curriculum vitae) is a longer, complete document listing a person's full academic and professional history, including publications and research — used for academic, medical, and research jobs in the US, and used as the everyday word for a job application document in the UK and much of Europe.",
  tableColumns: ['Resume (US)', 'CV'],
  tableRows: [
    { feature: 'Length', values: ['Usually 1-2 pages', 'Can be several pages, no strict limit'] },
    { feature: 'Purpose', values: ['Tailored summary for one specific job', 'Complete record of academic/professional history'] },
    { feature: 'Common region', values: ['United States, Canada', 'UK, Europe, and academic/medical fields worldwide'] },
    { feature: 'Typical content', values: ['Work experience, skills, brief education', 'Publications, research, degrees, full career history'] },
  ],
  terms: [
    {
      label: 'Resume',
      summary: 'A concise, targeted document highlighting the experience and skills most relevant to a specific job, common in the US and Canada.',
      pattern: 'a/the + resume',
      examples: ['"She updated her resume before applying for the marketing job."', '"Keep your resume to one page."', '"His resume listed only his last five years of experience."'],
    },
    {
      label: 'CV (Curriculum Vitae)',
      summary: "A detailed, chronological document covering a person's entire academic and professional history; used for academic, research, or medical roles, and as the standard term for a job application in the UK and Europe.",
      pattern: 'a/the + CV',
      examples: ['"The professor\'s CV listed over forty published papers."', '"In London, most applicants send a CV, not a resume."', '"The hospital asked for a full CV."'],
    },
  ],
  grammarRule: 'In American English, use "resume" for a short document tailored to each job application, and reserve "CV" for the long-form academic or research document. In British and much of European English, "CV" is the everyday word for what Americans call a resume — there is no separate, shorter "resume" in daily use.',
  extraRule: 'When applying internationally, check which term (and format) the employer expects. A US-style one-page resume can look incomplete to a UK recruiter expecting a CV, and a UK-style CV can look far too long to a US hiring manager expecting a resume.',
  mistakes: [
    { incorrect: 'In the US, an academic applying for a professorship should send a short one-page resume.', correct: 'In the US, an academic applying for a professorship should send a full CV.', note: 'Academic and research positions in the US typically require a CV, because they need a complete record of publications and research.' },
    { incorrect: 'A UK job seeker applying to a retail store should prepare both a CV and a separate resume.', correct: 'A UK job seeker applying to a retail store should prepare just a CV.', note: 'In the UK, "CV" is the everyday term for a job application document — there is usually no separate "resume".' },
    { incorrect: "My resume includes every conference I've attended over the last fifteen years.", correct: "My CV includes every conference I've attended over the last fifteen years.", note: 'A document listing an entire career history is a CV, not a short, targeted resume.' },
  ],
  correctExamples: [
    'She trimmed her resume down to one page before applying for the marketing role.',
    "The professor's CV listed over forty published papers.",
    'In the UK, job seekers send a CV rather than a resume.',
    'His resume highlighted only the last five years of relevant experience.',
    'The hospital asked for a full CV, including all clinical rotations and research work.',
    'Recruiters recommend keeping a resume to one or two pages.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: In the US, a job seeker applying for a retail role usually sends a short _____.', answer: 'resume', explanation: 'Everyday US job applications call for a short, targeted resume, not a full CV.' },
    { prompt: 'Choose the correct word: A scientist applying for a research grant usually submits a full _____ listing all publications.', answer: 'CV', explanation: 'Academic and research roles require the complete history that a CV provides.' },
    { prompt: 'Fix the sentence: "In London, most job applicants prepare both a CV and a resume."', answer: 'In London, most job applicants prepare just a CV.', explanation: 'British English uses "CV" as the general term for a job application document.' },
  ],
  faqs: [
    { question: 'Is a CV the same as a resume everywhere?', answer: 'No. In the US and Canada, "CV" and "resume" refer to different documents (long academic record vs. short job-specific summary). In the UK, Ireland, and much of Europe, "CV" is used for all job applications, and "resume" is rarely used at all.' },
    { question: 'How long should a resume or CV be?', answer: 'A US-style resume is usually kept to one or two pages. A CV has no strict length limit — an early-career CV might be two or three pages, while a senior academic\'s CV can run to ten pages or more.' },
    { question: 'Which one should I use if applying abroad?', answer: 'Check the expectations of the country and industry you are applying to. When in doubt, look at job postings or company career pages from that region, since the expected format and term can differ significantly from your home country.' },
  ],
  related: [
    { to: '/what-is-the-difference/internship-vs-apprenticeship/', text: 'Internship vs. Apprenticeship' },
    { to: '/what-is-the-difference/job-vs-career/', text: 'Job vs. Career' },
    { to: '/what-is-the-difference/founder-vs-ceo/', text: 'Founder vs. CEO' },
  ],
};

const ResumeVsCVPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default ResumeVsCVPage;
