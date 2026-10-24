'use client'

import { NavBar, Footer } from '@/components/nav-bar'
import { MobileTabBar } from '@/components/mobile-tab-bar'
import { AchievementUnlockDetector } from '@/components/achievement-unlock-detector'
import { DataLoadingIndicator } from '@/components/data-loading-indicator'
import { useUIStore } from '@/store/ui'
import { HomeView } from '@/components/views/home-view'
import { BrowseView } from '@/components/views/browse-view'
import { StudyView } from '@/components/views/study-view'
import { QuizView } from '@/components/views/quiz-view'
import { SpellingView } from '@/components/views/spelling-view'
import { ClozeView } from '@/components/views/cloze-view'
import { ReviewView } from '@/components/views/review-view'
import { FavoritesView } from '@/components/views/favorites-view'
import { SettingsView } from '@/components/views/settings-view'
import { WordDetailView } from '@/components/views/word-detail-view'

export default function Home() {
  const view = useUIStore((s) => s.view)

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <NavBar />
      <main className="flex-1 container mx-auto max-w-7xl px-4 py-5 sm:py-6 pb-20 sm:pb-6 w-full">
        {view === 'home' && <HomeView />}
        {view === 'browse' && <BrowseView />}
        {view === 'study' && <StudyView />}
        {view === 'quiz' && <QuizView />}
        {view === 'spelling' && <SpellingView />}
        {view === 'cloze' && <ClozeView />}
        {view === 'review' && <ReviewView />}
        {view === 'favorites' && <FavoritesView />}
        {view === 'settings' && <SettingsView />}
        {view === 'word' && <WordDetailView />}
      </main>
      <Footer />
      <MobileTabBar />
      <AchievementUnlockDetector />
      <DataLoadingIndicator />
    </div>
  )
}
