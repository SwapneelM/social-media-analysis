/**
 * ClaimsReview component.
 *
 * The core verification UI for reviewing extracted claims.
 * Features:
 * - 3 tabs: Needs Review, Auto-Accepted, Auto-Rejected
 * - Accept/Reject buttons for needs_review claims
 * - Reviewer notes text field
 * - localStorage persistence for human decisions
 * - Export verified claims as JSON
 */

import { useState, useEffect } from 'react';
import PlatformBadge from './PlatformBadge';
import ConfidenceBar from './ConfidenceBar';

const STORAGE_KEY = 'claims_review_decisions';

function loadDecisions() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : {};
  } catch {
    return {};
  }
}

function saveDecisions(decisions) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(decisions));
}

export default function ClaimsReview() {
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('needs_review');
  const [decisions, setDecisions] = useState(loadDecisions);

  useEffect(() => {
    fetch('/data/claims.json')
      .then((res) => {
        if (!res.ok) throw new Error('No claims data found. Run extraction first.');
        return res.json();
      })
      .then((data) => {
        setClaims(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  function getEffectiveStatus(claim, idx) {
    const key = `${claim.post_id}_${idx}`;
    if (decisions[key]?.decision) return decisions[key].decision;
    return claim.status;
  }

  function handleDecision(claim, idx, decision) {
    const key = `${claim.post_id}_${idx}`;
    const updated = {
      ...decisions,
      [key]: { ...decisions[key], decision, timestamp: new Date().toISOString() },
    };
    setDecisions(updated);
    saveDecisions(updated);
  }

  function handleNotes(claim, idx, notes) {
    const key = `${claim.post_id}_${idx}`;
    const updated = {
      ...decisions,
      [key]: { ...decisions[key], notes },
    };
    setDecisions(updated);
    saveDecisions(updated);
  }

  function exportVerified() {
    const verified = claims
      .map((claim, idx) => {
        const key = `${claim.post_id}_${idx}`;
        const effectiveStatus = getEffectiveStatus(claim, idx);
        if (effectiveStatus === 'auto_accepted' || effectiveStatus === 'accepted') {
          return {
            ...claim,
            verification: {
              final_status: effectiveStatus,
              reviewer_notes: decisions[key]?.notes || '',
              reviewed_at: decisions[key]?.timestamp || null,
            },
          };
        }
        return null;
      })
      .filter(Boolean);

    const blob = new Blob([JSON.stringify(verified, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'verified_claims.json';
    a.click();
    URL.revokeObjectURL(url);
  }

  if (loading) return <div className="loading">Loading claims...</div>;
  if (error) return <div className="error">{error}</div>;
  if (claims.length === 0) return <div className="empty">No claims extracted yet.</div>;

  const tabs = [
    { key: 'needs_review', label: 'Needs Review' },
    { key: 'auto_accepted', label: 'Auto-Accepted' },
    { key: 'auto_rejected', label: 'Auto-Rejected' },
  ];

  const filteredClaims = claims
    .map((claim, idx) => ({ claim, idx }))
    .filter(({ claim, idx }) => {
      const status = getEffectiveStatus(claim, idx);
      if (activeTab === 'needs_review') {
        return claim.status === 'needs_review' && !decisions[`${claim.post_id}_${idx}`]?.decision;
      }
      if (activeTab === 'auto_accepted') {
        return status === 'auto_accepted' || status === 'accepted';
      }
      if (activeTab === 'auto_rejected') {
        return status === 'auto_rejected' || status === 'rejected';
      }
      return true;
    });

  const needsReviewCount = claims.filter(
    (c, i) => c.status === 'needs_review' && !decisions[`${c.post_id}_${i}`]?.decision
  ).length;

  return (
    <div className="claims-review">
      <div className="claims-header">
        <h2>Claims Review ({claims.length} total)</h2>
        <button onClick={exportVerified} className="export-btn">
          Export Verified Claims
        </button>
      </div>

      <div className="tabs">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            className={`tab ${activeTab === tab.key ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.label}
            {tab.key === 'needs_review' && needsReviewCount > 0 && (
              <span className="badge">{needsReviewCount}</span>
            )}
          </button>
        ))}
      </div>

      <div className="claims-list">
        {filteredClaims.length === 0 && (
          <div className="empty">No claims in this category.</div>
        )}
        {filteredClaims.map(({ claim, idx }) => {
          const key = `${claim.post_id}_${idx}`;
          return (
            <div key={key} className="claim-card">
              <div className="claim-top">
                <PlatformBadge platform={claim.platform} />
                <ConfidenceBar confidence={claim.confidence || 0} />
              </div>

              <p className="claim-text">{claim.claim_text}</p>

              <div className="claim-details">
                <div className="detail">
                  <strong>Category:</strong> {claim.category}
                </div>
                <div className="detail">
                  <strong>Reasoning:</strong> {claim.reasoning}
                </div>
                <div className="detail source-quote">
                  <strong>Source:</strong> &ldquo;{claim.source_quote}&rdquo;
                </div>
                {claim.post_url && (
                  <a
                    href={claim.post_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="post-link"
                  >
                    View original post
                  </a>
                )}
              </div>

              {claim.status === 'needs_review' && (
                <div className="review-actions">
                  <div className="action-buttons">
                    <button
                      className="accept-btn"
                      onClick={() => handleDecision(claim, idx, 'accepted')}
                      disabled={decisions[key]?.decision === 'accepted'}
                    >
                      Accept
                    </button>
                    <button
                      className="reject-btn"
                      onClick={() => handleDecision(claim, idx, 'rejected')}
                      disabled={decisions[key]?.decision === 'rejected'}
                    >
                      Reject
                    </button>
                    {decisions[key]?.decision && (
                      <span className={`decision-label ${decisions[key].decision}`}>
                        {decisions[key].decision}
                      </span>
                    )}
                  </div>
                  <textarea
                    className="notes-input"
                    placeholder="Reviewer notes..."
                    rows={2}
                    value={decisions[key]?.notes || ''}
                    onChange={(e) => handleNotes(claim, idx, e.target.value)}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
