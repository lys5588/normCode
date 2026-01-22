/**
 * Layout Store - Manages panel dimensions and zoom level
 * Persists settings to localStorage for user preference retention
 */

import { create } from 'zustand';

interface PanelSizes {
  detailPanel: number;
  logPanel: number;
  workersPanel: number;
  agentPanel: number;
  chatPanel: number;
}

interface LayoutState {
  // Zoom level (1.0 = 100%)
  zoom: number;
  
  // Panel sizes (in pixels)
  panelSizes: PanelSizes;
  
  // Actions
  setZoom: (zoom: number) => void;
  zoomIn: () => void;
  zoomOut: () => void;
  resetZoom: () => void;
  
  setPanelSize: (panel: keyof PanelSizes, size: number) => void;
  resetPanelSizes: () => void;
  
  // Load from localStorage
  loadFromStorage: () => void;
}

const STORAGE_KEY = 'normcode-layout';
const ZOOM_STEP = 0.1;
const MIN_ZOOM = 0.5;
const MAX_ZOOM = 2.0;

const DEFAULT_PANEL_SIZES: PanelSizes = {
  detailPanel: 320,
  logPanel: 200,
  workersPanel: 280,
  agentPanel: 300,
  chatPanel: 400,
};

// Load initial state from localStorage
const loadInitialState = (): { zoom: number; panelSizes: PanelSizes } => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      const parsed = JSON.parse(saved);
      return {
        zoom: Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, parsed.zoom ?? 1)),
        panelSizes: { ...DEFAULT_PANEL_SIZES, ...parsed.panelSizes },
      };
    }
  } catch (e) {
    console.warn('Failed to load layout from storage:', e);
  }
  return { zoom: 1, panelSizes: DEFAULT_PANEL_SIZES };
};

const saveToStorage = (state: { zoom: number; panelSizes: PanelSizes }) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch (e) {
    console.warn('Failed to save layout to storage:', e);
  }
};

export const useLayoutStore = create<LayoutState>((set, get) => {
  const initial = loadInitialState();
  
  return {
    zoom: initial.zoom,
    panelSizes: initial.panelSizes,

    setZoom: (zoom) => {
      const clamped = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, zoom));
      set({ zoom: clamped });
      saveToStorage({ zoom: clamped, panelSizes: get().panelSizes });
    },

    zoomIn: () => {
      const newZoom = Math.min(MAX_ZOOM, get().zoom + ZOOM_STEP);
      set({ zoom: newZoom });
      saveToStorage({ zoom: newZoom, panelSizes: get().panelSizes });
    },

    zoomOut: () => {
      const newZoom = Math.max(MIN_ZOOM, get().zoom - ZOOM_STEP);
      set({ zoom: newZoom });
      saveToStorage({ zoom: newZoom, panelSizes: get().panelSizes });
    },

    resetZoom: () => {
      set({ zoom: 1 });
      saveToStorage({ zoom: 1, panelSizes: get().panelSizes });
    },

    setPanelSize: (panel, size) => {
      const newSizes = { ...get().panelSizes, [panel]: size };
      set({ panelSizes: newSizes });
      saveToStorage({ zoom: get().zoom, panelSizes: newSizes });
    },

    resetPanelSizes: () => {
      set({ panelSizes: DEFAULT_PANEL_SIZES });
      saveToStorage({ zoom: get().zoom, panelSizes: DEFAULT_PANEL_SIZES });
    },

    loadFromStorage: () => {
      const loaded = loadInitialState();
      set({ zoom: loaded.zoom, panelSizes: loaded.panelSizes });
    },
  };
});

// Export constants for use in components
export const ZOOM_LIMITS = { min: MIN_ZOOM, max: MAX_ZOOM, step: ZOOM_STEP };
export const DEFAULT_SIZES = DEFAULT_PANEL_SIZES;

