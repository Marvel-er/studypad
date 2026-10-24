import React from 'react';
import ComparisonPageTemplate, { ComparisonPageData } from '../../components/comparison/ComparisonPageTemplate';

const data: ComparisonPageData = {
  metaTitle: "Jail vs. Prison: What's the Difference? | TypoGrammar",
  metaDescription: 'Jail vs prison: a "jail" is a smaller, local facility for short sentences or people awaiting trial, while a "prison" is a state or federal facility for longer sentences after conviction. See the rule, examples, and a quiz.',
  slug: 'jail-vs-prison',
  h1: "Jail vs. Prison: What's the Difference?",
  breadcrumbLabel: 'Jail vs. Prison',
  datePublished: '2026-07-05',
  dateModified: '2026-07-05',
  quickAnswer: 'A "jail" is typically a smaller, local facility (often run by a city or county) used to hold people awaiting trial or serving short sentences, usually under a year. A "prison" is a larger, state or federal facility for people who have been convicted of more serious crimes and are serving longer sentences.',
  tableColumns: ['Jail', 'Prison'],
  tableRows: [
    { feature: 'Run by', values: ['City or county (local government)', 'State or federal government'] },
    { feature: 'Who is held', values: ['People awaiting trial or serving short sentences', 'People convicted of serious crimes, serving longer sentences'] },
    { feature: 'Typical sentence length', values: ['Under a year', 'More than a year, sometimes life'] },
    { feature: 'Security level', values: ['Mixed, often lower-security, short-term', 'Often higher security, long-term facilities'] },
  ],
  terms: [
    {
      label: 'Jail',
      summary: 'A local, short-term detention facility, holding people awaiting trial or serving brief sentences, usually run by a city or county.',
      pattern: 'in jail / go to jail',
      examples: ['"He spent one night in jail after his arrest."', '"She is still in jail awaiting trial."'],
    },
    {
      label: 'Prison',
      summary: 'A state or federal facility for people convicted of serious crimes, typically serving long-term sentences.',
      pattern: 'in prison / a prison sentence',
      examples: ['"He is serving a ten-year prison sentence."', '"She was sent to prison after her conviction."'],
    },
  ],
  grammarRule: 'Use "jail" for short-term, local detention — including people who have not yet been convicted and are simply awaiting trial. Use "prison" for long-term confinement of people already convicted of a serious crime, run by state or federal authorities.',
  extraRule: 'This distinction is mainly used in American English; in British English, "prison" is often the general term for both, and terms like "remand center" may describe pre-trial detention instead.',
  mistakes: [
    { incorrect: 'He was sent to prison for one night after being arrested and is still awaiting trial.', correct: 'He was sent to jail for one night after being arrested and is still awaiting trial.', note: 'Short-term detention before trial is jail, not prison.' },
    { incorrect: 'She is serving a fifteen-year jail sentence for the conviction.', correct: 'She is serving a fifteen-year prison sentence for the conviction.', note: 'Long sentences after conviction are served in prison.' },
    { incorrect: 'Prisons are run by city police departments in most cases.', correct: 'Jails are often run by city or county authorities, while prisons are run by the state or federal government.', note: 'Local authorities typically run jails, not prisons.' },
  ],
  correctExamples: [
    'He was held in the county jail while awaiting his court date.',
    'She has been in federal prison for three years of her sentence.',
    'The suspect spent the weekend in jail before posting bail.',
    'After his conviction, he was transferred from jail to a state prison.',
    'Jails are usually smaller and hold people for shorter periods than prisons.',
    'The prison houses inmates serving sentences of ten years or more.',
  ],
  quiz: [
    { prompt: 'Choose the correct word: A person arrested last night and waiting for a bail hearing is being held in _____.', answer: 'jail', explanation: 'Short-term, pre-trial detention takes place in jail.' },
    { prompt: 'Choose the correct word: A person convicted of a serious crime and sentenced to twenty years is sent to _____.', answer: 'prison', explanation: 'Long sentences after conviction are served in prison.' },
    { prompt: 'Fix the sentence: "After his conviction, he was sentenced to five years in the county jail."', answer: 'After his conviction, he was sentenced to five years in state prison.', explanation: 'Multi-year sentences after conviction are served in prison, not jail.' },
  ],
  faqs: [
    { question: 'Is jail the same as prison in British English?', answer: 'Not exactly — British English tends to use "prison" more broadly for both short and long-term detention, and often uses other terms, like "remand center," for pre-trial holding.' },
    { question: 'Can someone go straight to prison without going to jail first?', answer: 'Typically, people are first held in jail while awaiting trial or sentencing, and only moved to prison after being convicted and given a longer sentence.' },
    { question: 'Which is more secure, jail or prison?', answer: 'Prisons generally have higher security levels overall because they hold people convicted of more serious crimes for longer periods, though security varies widely by facility.' },
  ],
  related: [
    { to: '/what-is-the-difference/hotel-vs-motel/', text: 'Hotel vs. Motel' },
    { to: '/what-is-the-difference/problem-vs-issue/', text: 'Problem vs. Issue' },
    { to: '/what-is-the-difference/fact-vs-truth/', text: 'Fact vs. Truth' },
  ],
};

const JailVsPrisonPage: React.FC = () => <ComparisonPageTemplate data={data} />;
export default JailVsPrisonPage;
