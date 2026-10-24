
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import DesktopNav from './DesktopNav';

interface HeaderProps {
  onMenuClick: () => void;
}

const Header: React.FC<HeaderProps> = ({ onMenuClick }) => {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 8);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header className={`bg-white/90 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-20 transition-shadow duration-200 dark:bg-slate-900/90 dark:border-slate-700 ${scrolled ? 'shadow-md shadow-slate-300/40 dark:shadow-slate-900/60' : ''}`}>
      <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 md:px-4 flex justify-between items-center h-[69px]">
        <div className="flex items-center gap-4">
          <div className="lg:hidden">
            <button
              onClick={onMenuClick}
              className="p-2 rounded-md text-slate-600 hover:bg-slate-200/60 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:text-slate-400 dark:hover:bg-slate-800"
              aria-label="Open navigation menu"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
          <Link to="/" className="logo-link group" aria-label="TypoGrammar home">
            <div>
              <span className="font-heading text-3xl font-extrabold text-slate-800 tracking-tight dark:text-slate-200 block">
                <span className="relative inline-block transition-transform duration-300 group-hover:scale-105">
                  Typo<span className="text-blue-600 dark:text-blue-500 transition-colors duration-300 group-hover:text-blue-700 dark:group-hover:text-blue-400">Grammar</span>
                </span>
              </span>
              <p className="font-body text-xs text-slate-500 dark:text-slate-400 mt-1 hidden sm:block transition-colors duration-300 group-hover:text-blue-600 dark:group-hover:text-blue-400">
                From Confused to Confident in English
              </p>
            </div>
          </Link>
        </div>
        <DesktopNav />
        <div className="flex items-center gap-2">
          <Link
            to="/getting-started/"
            className="hidden sm:inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 text-white text-sm font-bold rounded-lg hover:bg-blue-700 transition-colors duration-150 shadow-sm"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
            Start Here
          </Link>
        </div>
      </div>
    </header>
  );
};

export default Header;