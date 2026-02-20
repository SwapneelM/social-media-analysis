/**
 * InputForm component.
 *
 * Provides text areas for Twitter keywords, Facebook URLs, and TikTok URLs.
 * Generates a CLI command that the user can copy-paste into their terminal
 * to run data collection.
 */

import { useState } from 'react';

export default function InputForm() {
  const [twitterKeywords, setTwitterKeywords] = useState('');
  const [metaUrls, setMetaUrls] = useState('');
  const [tiktokUrls, setTiktokUrls] = useState('');
  const [copied, setCopied] = useState(false);

  function buildCommand() {
    const parts = ['python -m collectors.run_collection'];

    if (twitterKeywords.trim()) {
      const keywords = twitterKeywords
        .split('\n')
        .map((k) => k.trim())
        .filter(Boolean)
        .map((k) => `"${k}"`)
        .join(' ');
      if (keywords) parts.push(`--twitter-keywords ${keywords}`);
    }

    if (metaUrls.trim()) {
      const urls = metaUrls
        .split('\n')
        .map((u) => u.trim())
        .filter(Boolean)
        .map((u) => `"${u}"`)
        .join(' ');
      if (urls) parts.push(`--meta-urls ${urls}`);
    }

    if (tiktokUrls.trim()) {
      const urls = tiktokUrls
        .split('\n')
        .map((u) => u.trim())
        .filter(Boolean)
        .map((u) => `"${u}"`)
        .join(' ');
      if (urls) parts.push(`--tiktok-urls ${urls}`);
    }

    return parts.join(' \\\n  ');
  }

  function handleCopy() {
    navigator.clipboard.writeText(buildCommand());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  const hasInput =
    twitterKeywords.trim() || metaUrls.trim() || tiktokUrls.trim();

  return (
    <div className="input-form">
      <h2>Data Collection</h2>
      <p className="description">
        Enter your search parameters below, then copy the generated command to
        run in your terminal.
      </p>

      <div className="form-grid">
        <div className="form-group">
          <label>Twitter Keywords (one per line)</label>
          <textarea
            rows={4}
            placeholder={"AI impact\nmachine learning\nIndia AI Summit"}
            value={twitterKeywords}
            onChange={(e) => setTwitterKeywords(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label>Facebook Page URLs (one per line)</label>
          <textarea
            rows={4}
            placeholder="https://facebook.com/page-name"
            value={metaUrls}
            onChange={(e) => setMetaUrls(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label>TikTok Account URLs (one per line)</label>
          <textarea
            rows={4}
            placeholder="https://tiktok.com/@username"
            value={tiktokUrls}
            onChange={(e) => setTiktokUrls(e.target.value)}
          />
        </div>
      </div>

      {hasInput && (
        <div className="command-output">
          <div className="command-header">
            <span>Generated Command</span>
            <button onClick={handleCopy} className="copy-btn">
              {copied ? 'Copied!' : 'Copy'}
            </button>
          </div>
          <pre>{buildCommand()}</pre>
        </div>
      )}
    </div>
  );
}
