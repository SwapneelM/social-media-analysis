/**
 * PlatformBadge component.
 *
 * Displays a colored badge indicating the social media platform.
 * Twitter = blue, Meta = dark blue, TikTok = pink/black.
 */

const PLATFORM_STYLES = {
  twitter: {
    backgroundColor: '#1DA1F2',
    color: '#fff',
    label: 'Twitter/X',
  },
  meta: {
    backgroundColor: '#1877F2',
    color: '#fff',
    label: 'Facebook',
  },
  tiktok: {
    backgroundColor: '#010101',
    color: '#fe2c55',
    label: 'TikTok',
  },
};

export default function PlatformBadge({ platform }) {
  const style = PLATFORM_STYLES[platform] || {
    backgroundColor: '#666',
    color: '#fff',
    label: platform || 'Unknown',
  };

  return (
    <span
      style={{
        display: 'inline-block',
        padding: '2px 8px',
        borderRadius: '4px',
        fontSize: '12px',
        fontWeight: '600',
        backgroundColor: style.backgroundColor,
        color: style.color,
      }}
    >
      {style.label}
    </span>
  );
}
