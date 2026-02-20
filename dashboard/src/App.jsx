/**
 * App component — main entry point for the Social Media Analysis Dashboard.
 *
 * Provides tab navigation between:
 * - Collect Data: InputForm for generating CLI commands
 * - Posts: PostsTable showing collected social media posts
 * - Claims Review: ClaimsReview for human verification of extracted claims
 */

import { useState } from 'react';
import InputForm from './components/InputForm';
import PostsTable from './components/PostsTable';
import ClaimsReview from './components/ClaimsReview';
import './App.css';

const TABS = [
  { key: 'collect', label: 'Collect Data' },
  { key: 'posts', label: 'Posts' },
  { key: 'claims', label: 'Claims Review' },
];

function App() {
  const [activeTab, setActiveTab] = useState('collect');

  return (
    <div className="app">
      <header className="app-header">
        <h1>Social Media Analysis Dashboard</h1>
        <p>Collect posts, extract claims, verify facts</p>
      </header>

      <nav className="app-nav">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            className={`nav-tab ${activeTab === tab.key ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      <main className="app-main">
        {activeTab === 'collect' && <InputForm />}
        {activeTab === 'posts' && <PostsTable />}
        {activeTab === 'claims' && <ClaimsReview />}
      </main>
    </div>
  );
}

export default App;
