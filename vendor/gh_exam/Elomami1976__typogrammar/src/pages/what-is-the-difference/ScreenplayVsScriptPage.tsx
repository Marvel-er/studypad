import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Screenplay vs. Script: What's the Difference? | TypoGrammar",
  metaDescription: 'Screenplay vs script: a "screenplay" specifically means the formatted written text for film or TV, while "script" broadly covers the written text of any performance. See the rule, examples, and a quiz.',
  slug: 'screenplay-vs-script',
  h1: "Screenplay vs. Script: What's the Difference?",
  breadcrumbLabel: 'Screenplay vs. Script',
  datePublished: '2026-07-05',
  dateModified: '2026-07-05',
  quickAnswer: 'A "screenplay" specifically refers to the written text for a film or television production, formatted with specific industry conventions for scenes, dialogue, and action. A "script" is a broader term for the written text of any performance — film, television, theater, radio, or even a podcast — and is often used as a general synonym for screenplay in casual speech.',
  tableColumns: ['Screenplay', 'Script'],
  tableRows: [
    { feature: 'Scope', values: ['Specific — film/TV writing format', 'Broad — any performance writing (film, TV, theater, radio, etc.)'] },
    { feature: 'Format', values: ['Specific industry formatting (scene headings, action lines)', 'Varies by medium (e.g., stage directions for plays)'] },
    { feature: 'Common use', values: ['"He wrote a screenplay for an indie film."', '"She wrote the script for the school play."'] },
    { feature: 'Casual overlap', values: ['Often just called a script casually', 'Can refer to a screenplay casually'] },
  ],
  terms: [
    {
      label: 'Screenplay',
      summary: 'The specifically formatted written text for a film or television production, including scene headings, action, and dialogue.',
      pattern: 'a screenplay (for + film/show)',
      examples: ['"She sold her first screenplay to a major studio."', '"The screenplay went through several drafts."'],
    },
    {
      label: 'Script',
      summary: 'The general written text of any performance, including film, television, theater, radio, or other media — sometimes used interchangeably with "screenplay" in casual speech.',
      pattern: 'a script (for + production)',
      examples: ['"He memorized his lines from the script."', '"The radio drama\'s script was written by a team of writers."'],
    },
  ],
  grammarRule: 'Use "screenplay" specifically for the formatted written text of a film or TV production. Use "script" as the broader term covering the written text of any performance, including plays, radio dramas, and podcasts — and note that in everyday speech, "script" is often used loosely to mean "screenplay" as well.',
  extraRule: 'Every screenplay is technically a script, but not every script is a screenplay — a stage play\'s script, for example, uses different formatting conventions than a film screenplay.',
  mistakes: [
    { incorrect: 'The playwright finished the screenplay for the new stage production.', correct: 'The playwright finished the script for the new stage production.', note: 'Written text for a stage play is a script, not a screenplay.' },
    { incorrect: 'A screenplay can refer to the written text of a radio drama, a play, or a film.', correct: 'A script can refer to the written text of a radio drama, a play, or a film.', note: '"Script" is the broader term covering multiple media.' },
    { incorrect: 'Screenplays and scripts always follow identical formatting rules regardless of medium.', correct: 'Screenplays follow specific film/TV formatting rules, while scripts for other media follow their own conventions.', note: 'Formatting conventions differ by medium.' },
  ],
  correctExamples: [
    'He spent a year writing the screenplay for his first feature film.',
    'The actors rehearsed their lines from the script every afternoon.',
    'Her screenplay was praised for its sharp, realistic dialogue.',
    'The podcast script included cues for sound effects.',
    'The director requested several rewrites of the screenplay.',
    'The students performed the play using a script written by their teacher.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: The formatted written text for an upcoming feature film is called a _____.', answer: 'screenplay', explanation: 'Film-specific formatted writing is a screenplay.' },
    { prompt: 'Choose the correct word: The written text for a school play, including stage directions, is called a _____.', answer: 'script', explanation: 'Written text for a stage play is a script.' },
    { prompt: 'Fix the sentence: "The radio drama\'s screenplay included sound effect cues instead of camera directions."', answer: "The radio drama's script included sound effect cues instead of camera directions.", explanation: 'Radio drama writing is a script, since "screenplay" specifically applies to film and TV.' },
  ],
  faqs: [
    { question: 'Is "script" always correct instead of "screenplay"?', answer: 'In casual speech, yes, "script" is often used loosely to mean "screenplay," though in professional film and TV settings, "screenplay" is the more precise term.' },
    { question: 'Do TV shows use screenplays or scripts?', answer: 'TV writing is often called either a "screenplay" or a "script" (sometimes a "teleplay" specifically for television), since television is a specific type of screen-based production.' },
    { question: 'What software do screenwriters use to format a screenplay?', answer: 'Dedicated screenwriting software automatically applies the standard industry formatting for scene headings, action, and dialogue, saving writers from formatting everything manually.' },
  ],
  related: [
    { to: '/what-is-the-difference/vlog-vs-blog/', text: 'Vlog vs. Blog' },
    { to: '/what-is-the-difference/photo-vs-picture-vs-image/', text: 'Photo vs. Picture vs. Image' },
    { to: '/what-is-the-difference/job-vs-career/', text: 'Job vs. Career' },
  ],
};

const ScreenplayVsScriptPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default ScreenplayVsScriptPage;
