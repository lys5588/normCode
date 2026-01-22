/**
 * ZoomControls - UI controls for adjusting the global zoom level
 * Provides zoom in/out buttons, percentage display, and reset
 */

import { ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';
import { useLayoutStore, ZOOM_LIMITS } from '../../stores/layoutStore';

interface ZoomControlsProps {
  className?: string;
  compact?: boolean;
}

export function ZoomControls({ className = '', compact = false }: ZoomControlsProps) {
  const zoom = useLayoutStore((s) => s.zoom);
  const zoomIn = useLayoutStore((s) => s.zoomIn);
  const zoomOut = useLayoutStore((s) => s.zoomOut);
  const resetZoom = useLayoutStore((s) => s.resetZoom);
  const setZoom = useLayoutStore((s) => s.setZoom);

  const zoomPercent = Math.round(zoom * 100);
  const canZoomIn = zoom < ZOOM_LIMITS.max;
  const canZoomOut = zoom > ZOOM_LIMITS.min;

  // Preset zoom levels
  const presets = [50, 75, 100, 125, 150, 200];

  if (compact) {
    return (
      <div className={`flex items-center gap-1 ${className}`}>
        <button
          onClick={zoomOut}
          disabled={!canZoomOut}
          className="p-1 rounded hover:bg-slate-100 text-slate-500 hover:text-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          title="Zoom out (Ctrl+-)"
        >
          <ZoomOut size={14} />
        </button>
        
        <span 
          className="text-xs font-mono text-slate-600 min-w-[40px] text-center cursor-pointer hover:bg-slate-100 px-1 py-0.5 rounded"
          onClick={resetZoom}
          title="Click to reset to 100%"
        >
          {zoomPercent}%
        </span>
        
        <button
          onClick={zoomIn}
          disabled={!canZoomIn}
          className="p-1 rounded hover:bg-slate-100 text-slate-500 hover:text-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          title="Zoom in (Ctrl++)"
        >
          <ZoomIn size={14} />
        </button>
      </div>
    );
  }

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {/* Zoom out */}
      <button
        onClick={zoomOut}
        disabled={!canZoomOut}
        className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-500 hover:text-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        title="Zoom out (Ctrl+-)"
      >
        <ZoomOut size={16} />
      </button>

      {/* Zoom percentage with dropdown */}
      <div className="relative group">
        <button
          className="px-2 py-1 text-xs font-mono text-slate-600 bg-slate-100 hover:bg-slate-200 rounded min-w-[50px] text-center transition-colors"
          title="Click for zoom presets"
        >
          {zoomPercent}%
        </button>
        
        {/* Dropdown for presets */}
        <div className="absolute top-full left-1/2 -translate-x-1/2 mt-1 bg-white rounded-lg shadow-lg border border-slate-200 py-1 z-50 hidden group-hover:block min-w-[80px]">
          {presets.map((preset) => (
            <button
              key={preset}
              onClick={() => setZoom(preset / 100)}
              className={`w-full px-3 py-1.5 text-xs text-left hover:bg-slate-100 transition-colors ${
                zoomPercent === preset ? 'text-blue-600 font-medium bg-blue-50' : 'text-slate-600'
              }`}
            >
              {preset}%
            </button>
          ))}
        </div>
      </div>

      {/* Zoom in */}
      <button
        onClick={zoomIn}
        disabled={!canZoomIn}
        className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-500 hover:text-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        title="Zoom in (Ctrl++)"
      >
        <ZoomIn size={16} />
      </button>

      {/* Reset button */}
      {zoom !== 1 && (
        <button
          onClick={resetZoom}
          className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-500 hover:text-slate-700 transition-colors"
          title="Reset zoom to 100%"
        >
          <RotateCcw size={14} />
        </button>
      )}
    </div>
  );
}

/**
 * Floating zoom controls - positioned at a corner of the screen
 */
interface FloatingZoomControlsProps {
  position?: 'bottom-left' | 'bottom-right' | 'top-left' | 'top-right';
}

export function FloatingZoomControls({ position = 'bottom-right' }: FloatingZoomControlsProps) {
  const positionClasses = {
    'bottom-left': 'bottom-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'top-left': 'top-4 left-4',
    'top-right': 'top-4 right-4',
  };

  return (
    <div className={`fixed ${positionClasses[position]} z-40`}>
      <div className="bg-white/95 backdrop-blur-sm rounded-lg shadow-lg border border-slate-200 px-2 py-1.5">
        <ZoomControls compact />
      </div>
    </div>
  );
}

