
import React from 'react';
import { Link } from 'react-router-dom';
import LanguageSwitcher from './LanguageSwitcher';

const productLinks = [
  { to: '/grammar-checker/', label: 'AI Grammar Checker' },
  { to: '/paraphrasing-tool/', label: 'AI Paraphrasing' },
  { to: '/english-level-test/', label: 'English Level Test' },
];

const companyLinks = [
  { to: '/about/', label: 'About' },
  { to: '/blog/', label: 'Blog' },
  { to: '/educators/', label: 'Educators Network' },
  { to: '/contact/', label: 'Contact' },
];

const legalLinks = [
  { to: '/faq/', label: 'FAQ' },
  { to: '/privacy-policy/', label: 'Privacy & Policy' },
  { to: '/terms-of-service/', label: 'Terms of Service' },
];

const linkClass = 'font-body text-sm text-slate-400 hover:text-white transition-colors';

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-slate-950 text-slate-400 border-t border-slate-800 mt-auto">
      <div className="max-w-screen-2xl mx-auto px-6 md:px-10 py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 lg:gap-12">
          {/* Brand */}
          <div className="col-span-2 md:col-span-1">
            <Link to="/" className="inline-block" aria-label="TypoGrammar home">
              <span className="font-heading text-2xl font-extrabold text-white tracking-tight">
                Typo<span className="text-blue-500">Grammar</span>
              </span>
            </Link>
            <p className="mt-3 font-body text-sm text-slate-400 leading-relaxed max-w-xs">
              From Confused to Confident in English. Free grammar lessons, IELTS &amp; TOEFL prep, and AI writing tools.
            </p>
            <a
              href="https://chromewebstore.google.com/detail/typogrammar-write/efdcbgkkccmclmfifkhpkampenagicki?utm_source=typogrammar"
              target="_blank"
              rel="noopener noreferrer"
              className="mt-4 inline-flex items-center gap-2 font-body text-sm text-slate-300 hover:text-white transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" className="w-5 h-5" aria-hidden="true">
                <path fill="#fff" d="M24 14a10 10 0 1 0 0 20 10 10 0 0 0 0-20Z" />
                <path fill="#EA4335" d="M24 4a20 20 0 0 1 17.32 10H24a10 10 0 0 0-9.43 6.67L6.66 14A20 20 0 0 1 24 4Z" />
                <path fill="#34A853" d="M14 24a10 10 0 0 0 18.86 4.67L24.93 44A20 20 0 0 1 6.66 14L14.57 20.67A9.96 9.96 0 0 0 14 24Z" />
                <path fill="#4285F4" d="M44 24a20 20 0 0 1-19.07 20l7.93-15.33A9.96 9.96 0 0 0 34 24a10 10 0 0 0-1.18-4.67L41.32 14A19.92 19.92 0 0 1 44 24Z" />
                <path fill="#FBBC05" d="M24 14h17.32l-8.5 5.33A10 10 0 0 0 14 24a9.96 9.96 0 0 0 .57 3.33L6.66 14A20 20 0 0 1 24 4v10Z" />
                <circle cx="24" cy="24" r="6" fill="#4285F4" />
              </svg>
              TypoGrammar Write Extension
            </a>
          </div>

          {/* Products */}
          <div>
            <h3 className="font-heading font-semibold text-white text-sm uppercase tracking-wider mb-4">
              Products
            </h3>
            <ul className="space-y-3">
              {productLinks.map((l) => (
                <li key={l.to}>
                  <Link to={l.to} className={linkClass}>{l.label}</Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Company */}
          <div>
            <h3 className="font-heading font-semibold text-white text-sm uppercase tracking-wider mb-4">
              Company
            </h3>
            <ul className="space-y-3">
              {companyLinks.map((l) => (
                <li key={l.to}>
                  <Link to={l.to} className={linkClass}>{l.label}</Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="font-heading font-semibold text-white text-sm uppercase tracking-wider mb-4">
              Legal
            </h3>
            <ul className="space-y-3">
              {legalLinks.map((l) => (
                <li key={l.to}>
                  <Link to={l.to} className={linkClass}>{l.label}</Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom bar — kept left-aligned so the fixed bottom-right chat widget
            never overlaps the language switcher or support button. */}
        <div className="mt-10 pt-6 border-t border-slate-800 flex flex-col sm:flex-row sm:items-center gap-4">
          <p className="font-body text-sm text-slate-500 text-center sm:text-left">
            &copy; {currentYear} TypoGrammar. All Rights Reserved.
          </p>
          <div className="flex items-center justify-center gap-3">
            <a
              href="https://buymeacoffee.com/quiztarek2k"
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 rounded-full text-slate-400 hover:text-pink-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-950 focus:ring-blue-500 transition-colors"
              aria-label="Support the creator"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
              </svg>
            </a>
            <LanguageSwitcher />
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;