/**
 * PostsTable component.
 *
 * Displays collected posts from data/posts.json in a filterable,
 * sortable table. Can filter by platform and sort by date or engagement.
 */

import { useState, useEffect } from 'react';
import PlatformBadge from './PlatformBadge';

export default function PostsTable() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [platformFilter, setPlatformFilter] = useState('all');
  const [sortBy, setSortBy] = useState('date');

  useEffect(() => {
    fetch('/data/posts.json')
      .then((res) => {
        if (!res.ok) throw new Error('No posts data found. Run collection first.');
        return res.json();
      })
      .then((data) => {
        setPosts(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="loading">Loading posts...</div>;
  if (error) return <div className="error">{error}</div>;
  if (posts.length === 0) return <div className="empty">No posts collected yet.</div>;

  const filtered =
    platformFilter === 'all'
      ? posts
      : posts.filter((p) => p.platform === platformFilter);

  const sorted = [...filtered].sort((a, b) => {
    if (sortBy === 'date') {
      return (b.timestamp || '').localeCompare(a.timestamp || '');
    }
    if (sortBy === 'likes') {
      return (b.engagement?.likes || 0) - (a.engagement?.likes || 0);
    }
    if (sortBy === 'shares') {
      return (b.engagement?.shares || 0) - (a.engagement?.shares || 0);
    }
    return 0;
  });

  const platforms = [...new Set(posts.map((p) => p.platform))];

  return (
    <div className="posts-table">
      <h2>Collected Posts ({posts.length})</h2>

      <div className="table-controls">
        <div className="filter-group">
          <label>Platform:</label>
          <select
            value={platformFilter}
            onChange={(e) => setPlatformFilter(e.target.value)}
          >
            <option value="all">All ({posts.length})</option>
            {platforms.map((p) => (
              <option key={p} value={p}>
                {p} ({posts.filter((post) => post.platform === p).length})
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Sort by:</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="date">Date (newest)</option>
            <option value="likes">Likes</option>
            <option value="shares">Shares</option>
          </select>
        </div>
      </div>

      <div className="posts-list">
        {sorted.map((post, idx) => (
          <div key={post.id || idx} className="post-card">
            <div className="post-header">
              <PlatformBadge platform={post.platform} />
              <span className="post-author">@{post.author}</span>
              <span className="post-date">
                {post.timestamp
                  ? new Date(post.timestamp).toLocaleDateString()
                  : ''}
              </span>
            </div>
            <p className="post-text">{post.text}</p>
            <div className="post-engagement">
              <span>{post.engagement?.likes || 0} likes</span>
              <span>{post.engagement?.shares || 0} shares</span>
              <span>{post.engagement?.comments || 0} comments</span>
              {post.url && (
                <a href={post.url} target="_blank" rel="noopener noreferrer">
                  View original
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
