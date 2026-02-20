/**
 * ConfidenceBar component.
 *
 * Displays a horizontal bar colored by confidence threshold:
 * - Green (>= 0.85): auto-accepted
 * - Yellow (0.60-0.85): needs review
 * - Red (< 0.60): auto-rejected
 */

function getColor(confidence) {
  if (confidence >= 0.85) return '#22c55e';
  if (confidence >= 0.60) return '#eab308';
  return '#ef4444';
}

export default function ConfidenceBar({ confidence }) {
  const pct = Math.round(confidence * 100);
  const color = getColor(confidence);

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <div
        style={{
          width: '100px',
          height: '8px',
          backgroundColor: '#e5e7eb',
          borderRadius: '4px',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            width: `${pct}%`,
            height: '100%',
            backgroundColor: color,
            borderRadius: '4px',
            transition: 'width 0.3s',
          }}
        />
      </div>
      <span style={{ fontSize: '12px', color: '#6b7280', minWidth: '36px' }}>
        {pct}%
      </span>
    </div>
  );
}
