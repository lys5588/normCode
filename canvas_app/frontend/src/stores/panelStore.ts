/**
 * Panel Store - Manages panel visibility state
 * 
 * This store enables WebSocket events to control panel visibility.
 * Panels can be opened, closed, toggled, and focused from the backend.
 */

import { create } from 'zustand';

// Panel names that can be controlled
export type PanelName = 
  | 'detail'
  | 'log'
  | 'settings'
  | 'checkpoint'
  | 'agent'
  | 'workers'
  | 'deployment'
  | 'load'
  | 'chat';

interface PanelState {
  // Visibility state for each panel
  panels: Record<PanelName, boolean>;
  
  // Currently focused panel (if any)
  focusedPanel: PanelName | null;
  
  // Actions
  openPanel: (panel: PanelName) => void;
  closePanel: (panel: PanelName) => void;
  togglePanel: (panel: PanelName) => void;
  focusPanel: (panel: PanelName) => void;
  
  // Batch operations
  setPanel: (panel: PanelName, isOpen: boolean) => void;
  setPanels: (updates: Partial<Record<PanelName, boolean>>) => void;
  
  // Check visibility
  isPanelOpen: (panel: PanelName) => boolean;
}

const DEFAULT_PANELS: Record<PanelName, boolean> = {
  detail: true,
  log: true,
  settings: false,
  checkpoint: false,
  agent: false,
  workers: false,
  deployment: false,
  load: false,
  chat: true,
};

export const usePanelStore = create<PanelState>((set, get) => ({
  panels: { ...DEFAULT_PANELS },
  focusedPanel: null,
  
  openPanel: (panel) => {
    console.log(`[PanelStore] Opening panel: ${panel}`);
    set((state) => ({
      panels: { ...state.panels, [panel]: true },
      focusedPanel: panel,
    }));
  },
  
  closePanel: (panel) => {
    console.log(`[PanelStore] Closing panel: ${panel}`);
    set((state) => ({
      panels: { ...state.panels, [panel]: false },
      focusedPanel: state.focusedPanel === panel ? null : state.focusedPanel,
    }));
  },
  
  togglePanel: (panel) => {
    const isOpen = get().panels[panel];
    console.log(`[PanelStore] Toggling panel: ${panel} (${isOpen ? 'close' : 'open'})`);
    set((state) => ({
      panels: { ...state.panels, [panel]: !isOpen },
      focusedPanel: !isOpen ? panel : (state.focusedPanel === panel ? null : state.focusedPanel),
    }));
  },
  
  focusPanel: (panel) => {
    const { panels } = get();
    console.log(`[PanelStore] Focusing panel: ${panel}`);
    set({
      // Open the panel if it's closed
      panels: panels[panel] ? panels : { ...panels, [panel]: true },
      focusedPanel: panel,
    });
  },
  
  setPanel: (panel, isOpen) => {
    set((state) => ({
      panels: { ...state.panels, [panel]: isOpen },
    }));
  },
  
  setPanels: (updates) => {
    set((state) => ({
      panels: { ...state.panels, ...updates },
    }));
  },
  
  isPanelOpen: (panel) => get().panels[panel],
}));

