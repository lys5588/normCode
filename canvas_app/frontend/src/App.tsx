/**
 * Main Application Component
 * Project-based NormCode Canvas - opens like a PyCharm/IDE project
 */

import { useState, useEffect, useCallback } from 'react';
import { 
  FolderOpen, 
  Settings, 
  HelpCircle, 
  PanelRight, 
  PanelRightClose, 
  PanelBottom, 
  PanelBottomClose,
  Folder,
  RefreshCw,
  X,
  GitGraph,
  FileCode,
  Bot,
  AlertTriangle,
  Save,
  Sparkles,
  Workflow,
  Rocket,
  Globe,
  ZoomIn,
  ZoomOut,
  RotateCcw,
} from 'lucide-react';
import { GraphCanvas } from './components/graph/GraphCanvas';
import { ControlPanel } from './components/panels/ControlPanel';
import { DetailPanel } from './components/panels/DetailPanel';
import { LoadPanel } from './components/panels/LoadPanel';
import { LogPanel } from './components/panels/LogPanel';
import { SettingsPanel } from './components/panels/SettingsPanel';
import { ProjectPanel } from './components/panels/ProjectPanel';
import { EditorPanel } from './components/panels/EditorPanel';
import { CheckpointPanel } from './components/panels/CheckpointPanel';
import { AgentPanel } from './components/panels/AgentPanel';
import { WorkersPanel } from './components/panels/WorkersPanel';
import { UserInputModal } from './components/panels/UserInputModal';
import { ProjectTabs } from './components/panels/ProjectTabs';
import { ChatPanel } from './components/panels/ChatPanel';
import { DeploymentPanel } from './components/panels/DeploymentPanel';
import { ToastContainer, ResizeDivider } from './components/common';
import { useWebSocket } from './hooks/useWebSocket';
import { useGraphStore } from './stores/graphStore';
import { useExecutionStore } from './stores/executionStore';
import { useProjectStore } from './stores/projectStore';
import { useChatStore } from './stores/chatStore';
import { useNotificationStore } from './stores/notificationStore';
import { useLayoutStore, ZOOM_LIMITS } from './stores/layoutStore';
import { usePanelStore } from './stores/panelStore';

// View modes for the main content area
type ViewMode = 'canvas' | 'editor';

// Modal for editing repository paths
interface RepositoryPathsModalProps {
  currentPaths: { concepts: string; inferences: string; inputs?: string };
  onSave: (paths: { concepts: string; inferences: string; inputs?: string }) => Promise<void>;
  onClose: () => void;
}

function RepositoryPathsModal({ currentPaths, onSave, onClose }: RepositoryPathsModalProps) {
  const [concepts, setConceptsPath] = useState(currentPaths.concepts);
  const [inferences, setInferencesPath] = useState(currentPaths.inferences);
  const [inputs, setInputsPath] = useState(currentPaths.inputs || '');
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    await onSave({
      concepts,
      inferences,
      inputs: inputs || undefined,
    });
    setSaving(false);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div 
        className="bg-white rounded-lg shadow-xl w-full max-w-lg mx-4"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-200">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-yellow-500" />
            <h2 className="text-lg font-semibold text-slate-800">Edit Repository Paths</h2>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          <p className="text-sm text-slate-600">
            Update the paths to your repository files. Paths are relative to the project directory.
          </p>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Concepts File <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={concepts}
              onChange={(e) => setConceptsPath(e.target.value)}
              placeholder="e.g., repos/concepts.json"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Inferences File <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={inferences}
              onChange={(e) => setInferencesPath(e.target.value)}
              placeholder="e.g., repos/inferences.json"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Inputs File <span className="text-slate-400">(optional)</span>
            </label>
            <input
              type="text"
              value={inputs}
              onChange={(e) => setInputsPath(e.target.value)}
              placeholder="e.g., repos/inputs.json"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-2 p-4 border-t border-slate-200 bg-slate-50 rounded-b-lg">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-slate-600 hover:text-slate-800 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={!concepts || !inferences || saving}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
          >
            {saving ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Save className="w-4 h-4" />
            )}
            Save Paths
          </button>
        </div>
      </div>
    </div>
  );
}

function App() {
  // Panel visibility from panelStore (enables WebSocket control)
  const panels = usePanelStore((s) => s.panels);
  const openPanel = usePanelStore((s) => s.openPanel);
  const closePanel = usePanelStore((s) => s.closePanel);
  const togglePanel = usePanelStore((s) => s.togglePanel);
  
  // Derived panel states for cleaner usage
  const showLoadPanel = panels.load;
  const showDetailPanel = panels.detail;
  const showLogPanel = panels.log;
  const showSettingsPanel = panels.settings;
  const showCheckpointPanel = panels.checkpoint;
  const showAgentPanel = panels.agent;
  const showWorkersPanel = panels.workers;
  const showDeploymentPanel = panels.deployment;
  
  // Setter functions that work with both boolean values and toggles
  const setShowLoadPanel = useCallback((show: boolean) => show ? openPanel('load') : closePanel('load'), [openPanel, closePanel]);
  const setShowDetailPanel = useCallback((show: boolean) => show ? openPanel('detail') : closePanel('detail'), [openPanel, closePanel]);
  const setShowLogPanel = useCallback((show: boolean) => show ? openPanel('log') : closePanel('log'), [openPanel, closePanel]);
  const setShowSettingsPanel = useCallback((show: boolean) => show ? openPanel('settings') : closePanel('settings'), [openPanel, closePanel]);
  const setShowCheckpointPanel = useCallback((show: boolean) => show ? openPanel('checkpoint') : closePanel('checkpoint'), [openPanel, closePanel]);
  const setShowAgentPanel = useCallback((show: boolean) => show ? openPanel('agent') : closePanel('agent'), [openPanel, closePanel]);
  const setShowWorkersPanel = useCallback((show: boolean) => show ? openPanel('workers') : closePanel('workers'), [openPanel, closePanel]);
  const setShowDeploymentPanel = useCallback((show: boolean) => show ? openPanel('deployment') : closePanel('deployment'), [openPanel, closePanel]);
  
  const [viewMode, setViewMode] = useState<ViewMode>('canvas');
  const [detailPanelFullscreen, setDetailPanelFullscreen] = useState(false);
  const [showRepoPathsModal, setShowRepoPathsModal] = useState(false);
  
  const graphData = useGraphStore((s) => s.graphData);
  const status = useExecutionStore((s) => s.status);
  const logs = useExecutionStore((s) => s.logs);
  const wsConnected = useWebSocket();
  const showError = useNotificationStore((s) => s.showError);
  const showWarning = useNotificationStore((s) => s.showWarning);
  
  // Layout state (zoom and panel sizes)
  const zoom = useLayoutStore((s) => s.zoom);
  const zoomIn = useLayoutStore((s) => s.zoomIn);
  const zoomOut = useLayoutStore((s) => s.zoomOut);
  const resetZoom = useLayoutStore((s) => s.resetZoom);
  const panelSizes = useLayoutStore((s) => s.panelSizes);
  const setPanelSize = useLayoutStore((s) => s.setPanelSize);
  
  // Track shown error logs to avoid duplicates
  const [lastErrorLogCount, setLastErrorLogCount] = useState(0);
  
  // Chat state
  const { isOpen: isChatOpen, togglePanel: toggleChatPanel, controllerStatus } = useChatStore();
  
  // Keyboard shortcuts for zoom
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + Plus = Zoom In
      if ((e.ctrlKey || e.metaKey) && (e.key === '=' || e.key === '+')) {
        e.preventDefault();
        zoomIn();
      }
      // Ctrl/Cmd + Minus = Zoom Out
      if ((e.ctrlKey || e.metaKey) && e.key === '-') {
        e.preventDefault();
        zoomOut();
      }
      // Ctrl/Cmd + 0 = Reset Zoom
      if ((e.ctrlKey || e.metaKey) && e.key === '0') {
        e.preventDefault();
        resetZoom();
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [zoomIn, zoomOut, resetZoom]);
  
  // Panel resize handlers
  const handleDetailPanelResize = useCallback((delta: number) => {
    setPanelSize('detailPanel', Math.max(200, Math.min(600, panelSizes.detailPanel - delta)));
  }, [panelSizes.detailPanel, setPanelSize]);
  
  const handleLogPanelResize = useCallback((delta: number) => {
    setPanelSize('logPanel', Math.max(100, Math.min(500, panelSizes.logPanel - delta)));
  }, [panelSizes.logPanel, setPanelSize]);
  
  const handleWorkersPanelResize = useCallback((delta: number) => {
    setPanelSize('workersPanel', Math.max(200, Math.min(500, panelSizes.workersPanel + delta)));
  }, [panelSizes.workersPanel, setPanelSize]);
  
  const handleAgentPanelResize = useCallback((delta: number) => {
    setPanelSize('agentPanel', Math.max(200, Math.min(500, panelSizes.agentPanel + delta)));
  }, [panelSizes.agentPanel, setPanelSize]);
  
  
  // Project state
  const {
    currentProject,
    projectPath,
    isLoaded,
    repositoriesExist,
    isLoading: projectLoading,
    openTabs,
    activeTabId,
    remoteProjectTabs,
    fetchCurrentProject,
    fetchRecentProjects,
    fetchOpenTabs,
    loadProjectRepositories,
    closeProject,
    setProjectPanelOpen,
    updateRepositories,
  } = useProjectStore();
  
  // Check if current project is read-only (compiler project)
  // Remote projects are "read-only" in terms of editing, but can still be executed
  const activeTab = openTabs.find(tab => tab.id === activeTabId);
  const isReadOnlyProject = activeTab?.is_read_only ?? false;
  const isRemoteProject = activeTab?.is_remote ?? false;

  // Fetch project state on startup
  useEffect(() => {
    fetchCurrentProject();
    fetchRecentProjects();
    fetchOpenTabs();
  }, [fetchCurrentProject, fetchRecentProjects, fetchOpenTabs]);
  
  // Show toast notifications for new error/warning logs
  useEffect(() => {
    const errorLogs = logs.filter(log => log.level === 'error');
    
    // Only show toasts for new errors (not ones we've already seen)
    if (errorLogs.length > lastErrorLogCount) {
      const newErrors = errorLogs.slice(lastErrorLogCount);
      
      // Show toast for each new error (limit to avoid spam)
      newErrors.slice(0, 3).forEach((log, idx) => {
        // Slight delay between toasts for visual effect
        setTimeout(() => {
          showError(
            log.flowIndex ? `Error in ${log.flowIndex}` : 'Error',
            log.message,
          );
        }, idx * 100);
      });
      
      // If more than 3 new errors, show summary
      if (newErrors.length > 3) {
        setTimeout(() => {
          showWarning(
            'Multiple Errors',
            `${newErrors.length - 3} more errors occurred. Check the log panel for details.`,
          );
        }, 400);
      }
      
      setLastErrorLogCount(errorLogs.length);
    }
  }, [logs, lastErrorLogCount, showError, showWarning]);

  // If no project is open, show project welcome screen
  if (!currentProject) {
    return <ProjectPanel />;
  }

  return (
    <div 
      className="flex flex-col bg-slate-50" 
      style={{ 
        zoom: zoom,
        width: `${100 / zoom}vw`,
        height: `${100 / zoom}vh`,
      }}
    >
      {/* Single Unified Header */}
      <header className="bg-white border-b border-slate-200 px-3 py-2 flex items-center justify-between gap-2 overflow-hidden">
        {/* Left side: Logo + Project Info */}
        <div className="flex items-center gap-2 min-w-0 flex-shrink">
          {/* App Logo */}
          <img src="/psylens-logo.png" alt="NormCode Canvas" className="w-6 h-6 flex-shrink-0" />
          
          {/* Project Info */}
          <div className="flex items-center gap-1.5 min-w-0">
            <span className="font-medium text-slate-700 truncate max-w-[120px]" title={currentProject.name}>{currentProject.name}</span>
            {/* Remote projects show "Remote" badge instead of Load button */}
            {isRemoteProject ? (
              <span className="px-2 py-0.5 bg-cyan-100 text-cyan-700 text-xs rounded-full flex items-center gap-1">
                <Globe size={12} />
                Remote
              </span>
            ) : isLoaded ? (
              <div className="flex items-center gap-1">
                <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full flex items-center gap-1">
                  <span className="w-1.5 h-1.5 bg-green-500 rounded-full" />
                  Loaded
                </span>
                <button
                  onClick={loadProjectRepositories}
                  disabled={projectLoading}
                  className="p-1 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors disabled:opacity-50"
                  title="Reload repositories (refresh from source files)"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${projectLoading ? 'animate-spin' : ''}`} />
                </button>
                <button
                  onClick={() => setShowLoadPanel(true)}
                  className="text-xs text-slate-400 hover:text-slate-600 hover:underline transition-colors"
                  title="Load different repositories"
                >
                  (change)
                </button>
              </div>
            ) : repositoriesExist ? (
              <button
                onClick={loadProjectRepositories}
                disabled={projectLoading}
                className="px-2 py-0.5 bg-blue-100 hover:bg-blue-200 text-blue-700 text-xs rounded-full flex items-center gap-1 transition-colors"
              >
                {projectLoading ? (
                  <RefreshCw className="w-3 h-3 animate-spin" />
                ) : (
                  <FolderOpen className="w-3 h-3" />
                )}
                Load
              </button>
            ) : (
              <button
                onClick={() => setShowRepoPathsModal(true)}
                className="px-2 py-0.5 bg-yellow-100 hover:bg-yellow-200 text-yellow-700 text-xs rounded-full flex items-center gap-1 transition-colors cursor-pointer"
                title="Click to edit repository paths"
              >
                <AlertTriangle className="w-3 h-3" />
                Missing files
              </button>
            )}
          </div>
          
          {/* Config summary */}
          <span className="text-xs text-slate-400 whitespace-nowrap flex-shrink-0">
            {currentProject.execution.max_cycles} cycles
          </span>
          
          {/* View Mode Tabs */}
          <div className="w-px h-5 bg-slate-200 flex-shrink-0 hidden sm:block" />
          <div className="flex items-center bg-slate-100 rounded-lg p-0.5 flex-shrink-0">
            <button
              onClick={() => setViewMode('canvas')}
              className={`flex items-center gap-1.5 px-3 py-1 text-sm rounded-md transition-all ${
                viewMode === 'canvas'
                  ? 'bg-white text-blue-600 shadow-sm font-medium'
                  : 'text-slate-600 hover:text-slate-800'
              }`}
            >
              <GitGraph size={14} />
              Canvas
            </button>
            <button
              onClick={() => setViewMode('editor')}
              className={`flex items-center gap-1.5 px-3 py-1 text-sm rounded-md transition-all ${
                viewMode === 'editor'
                  ? 'bg-white text-blue-600 shadow-sm font-medium'
                  : 'text-slate-600 hover:text-slate-800'
              }`}
            >
              <FileCode size={14} />
              Editor
            </button>
          </div>
        </div>
        
        {/* Right side: Actions */}
        <div className="flex items-center gap-0.5 flex-shrink-0">
          {/* Left panel toggles (Workers, Agent) */}
          {viewMode === 'canvas' && (
            <>
              {/* Plans in Work Panel Toggle */}
              <button
                onClick={() => setShowWorkersPanel(!showWorkersPanel)}
                className={`p-1.5 rounded-lg transition-colors ${
                  showWorkersPanel
                    ? 'text-indigo-600 bg-indigo-50 hover:bg-indigo-100'
                    : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'
                }`}
                title="Plans in Work - View all active NormCode plans"
              >
                <Workflow size={16} />
              </button>
              
              {/* Agent Panel Toggle */}
              <button
                onClick={() => setShowAgentPanel(!showAgentPanel)}
                className={`p-1.5 rounded-lg transition-colors ${
                  showAgentPanel
                    ? 'text-purple-600 bg-purple-50 hover:bg-purple-100'
                    : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'
                }`}
                title="Agent Configuration Panel"
              >
                <Bot size={16} />
              </button>
            </>
          )}
          
          {/* Panel toggles - show in canvas mode */}
          {viewMode === 'canvas' && (
            <>
              <div className="w-px h-5 bg-slate-200 mx-0.5" />
              {/* Detail panel toggle - only when graph loaded */}
              {graphData && (
                <button
                  onClick={() => setShowDetailPanel(!showDetailPanel)}
                  className={`p-1.5 rounded-lg transition-colors ${
                    showDetailPanel 
                      ? 'text-blue-600 bg-blue-50 hover:bg-blue-100' 
                      : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'
                  }`}
                  title={showDetailPanel ? 'Hide detail panel' : 'Show detail panel'}
                >
                  {showDetailPanel ? <PanelRightClose size={16} /> : <PanelRight size={16} />}
                </button>
              )}
              {/* Log panel toggle - always available to see loading errors */}
              <button
                onClick={() => setShowLogPanel(!showLogPanel)}
                className={`p-1.5 rounded-lg transition-colors ${
                  showLogPanel 
                    ? 'text-blue-600 bg-blue-50 hover:bg-blue-100' 
                    : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'
                }`}
                title={showLogPanel ? 'Hide log panel' : 'Show log panel'}
              >
                {showLogPanel ? <PanelBottomClose size={16} /> : <PanelBottom size={16} />}
              </button>
            </>
          )}
          
          <div className="w-px h-5 bg-slate-200 mx-0.5" />
          
          {/* Zoom Controls */}
          <div className="flex items-center bg-slate-100 rounded-lg px-0.5 py-0.5">
            <button
              onClick={zoomOut}
              disabled={zoom <= ZOOM_LIMITS.min}
              className="p-1 rounded hover:bg-slate-200 text-slate-500 hover:text-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              title="Zoom out (Ctrl+-)"
            >
              <ZoomOut size={14} />
            </button>
            <button
              onClick={resetZoom}
              className="px-1.5 py-0.5 text-xs font-mono text-slate-600 hover:bg-slate-200 rounded min-w-[42px] text-center transition-colors"
              title="Click to reset zoom (Ctrl+0)"
            >
              {Math.round(zoom * 100)}%
            </button>
            <button
              onClick={zoomIn}
              disabled={zoom >= ZOOM_LIMITS.max}
              className="p-1 rounded hover:bg-slate-200 text-slate-500 hover:text-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              title="Zoom in (Ctrl++)"
            >
              <ZoomIn size={14} />
            </button>
            {zoom !== 1 && (
              <button
                onClick={resetZoom}
                className="p-1 rounded hover:bg-slate-200 text-slate-400 hover:text-slate-600 transition-colors"
                title="Reset to 100%"
              >
                <RotateCcw size={12} />
              </button>
            )}
          </div>
          
          <div className="w-px h-5 bg-slate-200 mx-0.5" />
          
          {/* Settings */}
          <button
            onClick={() => setShowSettingsPanel(!showSettingsPanel)}
            className={`p-1.5 rounded-lg transition-colors ${
              showSettingsPanel
                ? 'text-blue-600 bg-blue-50 hover:bg-blue-100'
                : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'
            }`}
            title="Execution Settings"
          >
            <Settings size={16} />
          </button>
          
          {/* Deploy */}
          <button
            onClick={() => setShowDeploymentPanel(true)}
            className="p-1.5 text-slate-500 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors"
            title="Deploy Project"
          >
            <Rocket size={16} />
          </button>
          
          {/* Project settings */}
          <button
            onClick={() => setProjectPanelOpen(true)}
            className="p-1.5 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
            title="Project Settings"
          >
            <Folder size={16} />
          </button>
          
          {/* Help */}
          <button
            onClick={() => {
              const url = 'https://www.psylensai.com';
              // In desktop app (pywebview), open in system browser to avoid losing the app
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              const pywebview = (window as any).pywebview;
              if (pywebview?.api?.open_external_url) {
                pywebview.api.open_external_url(url);
              } else {
                window.open(url, '_blank');
              }
            }}
            className="p-1.5 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
            title="Help - Visit PsylensAI"
          >
            <HelpCircle size={16} />
          </button>
          
          <div className="w-px h-5 bg-slate-200 mx-0.5" />
          
          {/* Chat Panel Toggle - compiler-driven chat */}
          <button
            onClick={toggleChatPanel}
            className={`p-1.5 rounded-lg transition-colors flex items-center gap-1 ${
              isChatOpen
                ? 'text-purple-600 bg-purple-50 hover:bg-purple-100'
                : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'
            }`}
            title="Compiler Chat"
          >
            <Sparkles size={16} />
            <span className="text-xs font-medium">Chat</span>
            {controllerStatus === 'running' && (
              <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
            )}
          </button>
          
          {/* Close project */}
          <button
            onClick={closeProject}
            className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
            title="Close Project"
          >
            <X size={16} />
          </button>
        </div>
      </header>

      {/* Settings Panel */}
      <SettingsPanel 
        isOpen={showSettingsPanel} 
        onToggle={() => setShowSettingsPanel(!showSettingsPanel)}
        onOpenAgentPanel={() => {
          setShowSettingsPanel(false);  // Close settings panel
          setShowAgentPanel(true);       // Open agent panel
        }}
      />

      {/* Main Content Area with Chat Panel */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left side: Tabs + Main Content (includes ControlPanel when in canvas mode) */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Project Tabs Bar - shows when multiple projects are open or remote tabs exist */}
          {(openTabs.length > 1 || remoteProjectTabs.length > 0) && (
            <ProjectTabs onOpenProjectPanel={() => setProjectPanelOpen(true)} />
          )}
          {/* Control Panel - show in canvas mode when graph is loaded
              Read-only projects hide the control panel UNLESS they are remote projects
              (remote projects are read-only for editing but can still be executed)
              Remote execution is handled through the unified worker system - remote proxy workers
              show up in WorkersPanel and ControlPanel uses the bound worker's API */}
          {graphData && viewMode === 'canvas' && (!isReadOnlyProject || isRemoteProject) && (
            <ControlPanel 
              onCheckpointToggle={() => setShowCheckpointPanel(!showCheckpointPanel)}
              checkpointPanelOpen={showCheckpointPanel}
            />
          )}

          {/* Checkpoint Panel - dropdown below control panel */}
          <CheckpointPanel 
            isOpen={showCheckpointPanel && viewMode === 'canvas'} 
            onToggle={() => setShowCheckpointPanel(!showCheckpointPanel)} 
          />

          {/* Main Content */}
          <main className="flex-1 flex flex-col overflow-hidden">
            {viewMode === 'editor' ? (
              // Editor View
              <EditorPanel />
            ) : (!isLoaded && !graphData) ? (
          // Show message when repositories not loaded yet AND no worker graph is loaded (Canvas mode)
          // Include LogPanel at the bottom for loading errors visibility
          <>
            <div className="flex-1 flex items-center justify-center bg-white">
              <div className="text-center p-8">
                <Folder className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                <h2 className="text-xl font-semibold text-slate-700 mb-2">Project Ready</h2>
                <p className="text-slate-500 mb-4 max-w-md">
                  {repositoriesExist 
                    ? 'Click "Load" in the header to start working with your NormCode plan.'
                    : 'Repository files not found. Make sure concepts.json and inferences.json exist in the project directory.'
                  }
                </p>
                {repositoriesExist && (
                  <button
                    onClick={loadProjectRepositories}
                    disabled={projectLoading}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg flex items-center gap-2 mx-auto transition-colors"
                  >
                    {projectLoading ? (
                      <RefreshCw className="w-4 h-4 animate-spin" />
                    ) : (
                      <FolderOpen className="w-4 h-4" />
                    )}
                    Load Repositories
                  </button>
                )}
              </div>
            </div>
            {/* Log Panel - available even before loading for error visibility */}
            {showLogPanel && <LogPanel />}
          </>
        ) : (
          // Canvas View
          <div className="flex-1 flex flex-col overflow-hidden">
            <div className="flex-1 flex overflow-hidden">
              {/* Left side panels with resize handles */}
              {showWorkersPanel && (
                <>
                  <div 
                    className="bg-white border-r border-slate-200 flex flex-col overflow-hidden"
                    style={{ width: panelSizes.workersPanel }}
                  >
                    <WorkersPanel />
                  </div>
                  <ResizeDivider direction="horizontal" onResize={handleWorkersPanelResize} />
                </>
              )}
              {showAgentPanel && (
                <>
                  <div 
                    className="bg-white border-r border-slate-200 flex flex-col overflow-hidden"
                    style={{ width: panelSizes.agentPanel }}
                  >
                    <AgentPanel />
                  </div>
                  <ResizeDivider direction="horizontal" onResize={handleAgentPanelResize} />
                </>
              )}
              
              {/* Graph Canvas */}
              <div className="flex-1 overflow-hidden">
                <GraphCanvas />
              </div>

              {/* Detail Panel with resize handle */}
              {graphData && showDetailPanel && !detailPanelFullscreen && (
                <>
                  <ResizeDivider direction="horizontal" onResize={handleDetailPanelResize} />
                  <div style={{ width: panelSizes.detailPanel }}>
                    <DetailPanel 
                      isFullscreen={false}
                      onToggleFullscreen={() => setDetailPanelFullscreen(true)}
                    />
                  </div>
                </>
              )}
            </div>

            {/* Log Panel with resize handle */}
            {graphData && showLogPanel && (
              <>
                <ResizeDivider direction="vertical" onResize={handleLogPanelResize} />
                <div style={{ height: panelSizes.logPanel }} className="flex-shrink-0 flex flex-col overflow-hidden border-t border-slate-200">
                  <LogPanel />
                </div>
              </>
            )}
          </div>
        )}
          </main>
        </div>

        {/* Chat Panel - appears on right side, independent of view mode */}
        {isChatOpen && (
          <>
            <ResizeDivider 
              direction="horizontal" 
              onResize={(delta) => setPanelSize('chatPanel', Math.max(300, Math.min(600, panelSizes.chatPanel - delta)))} 
            />
            <div style={{ width: panelSizes.chatPanel }} className="h-full flex-shrink-0">
              <ChatPanel />
            </div>
          </>
        )}
        {!isChatOpen && <ChatPanel />}
      </div>

      {/* Fullscreen Detail Panel */}
      {graphData && detailPanelFullscreen && (
        <DetailPanel 
          isFullscreen={true}
          onToggleFullscreen={() => setDetailPanelFullscreen(false)}
        />
      )}

      {/* Load Panel Modal (for loading different repositories) */}
      {showLoadPanel && (
        <LoadPanel 
          onClose={() => setShowLoadPanel(false)} 
          onOpenSettings={() => setShowSettingsPanel(true)}
        />
      )}

      {/* Project Panel Modal */}
      <ProjectPanel />

      {/* Repository Paths Modal */}
      {showRepoPathsModal && (
        <RepositoryPathsModal
          currentPaths={currentProject.repositories}
          onSave={async (paths) => {
            const success = await updateRepositories(paths);
            if (success) {
              setShowRepoPathsModal(false);
            }
          }}
          onClose={() => setShowRepoPathsModal(false)}
        />
      )}

      {/* User Input Modal (human-in-the-loop) */}
      <UserInputModal />

      {/* Deployment Panel */}
      <DeploymentPanel
        isOpen={showDeploymentPanel}
        onClose={() => setShowDeploymentPanel(false)}
      />

      {/* Toast Notifications - prominent alerts for errors/warnings */}
      <ToastContainer />

      {/* Status Bar */}
      <footer className="bg-white border-t border-slate-200 px-4 py-1 flex items-center justify-between text-xs text-slate-500">
        <div className="flex items-center gap-4">
          <span className={`flex items-center gap-1 ${
            status === 'running' ? 'text-green-600' :
            status === 'paused' ? 'text-yellow-600' :
            status === 'failed' ? 'text-red-600' :
            status === 'completed' ? 'text-green-600' :
            'text-slate-500'
          }`}>
            <span className={`w-2 h-2 rounded-full ${
              status === 'running' ? 'bg-green-500 animate-pulse' :
              status === 'paused' ? 'bg-yellow-500' :
              status === 'failed' ? 'bg-red-500' :
              status === 'completed' ? 'bg-green-500' :
              'bg-slate-400'
            }`} />
            {status === 'idle' ? 'Ready' : status.charAt(0).toUpperCase() + status.slice(1)}
          </span>
          {graphData && (
            <>
              <span>•</span>
              <span>{graphData.nodes.length} nodes</span>
              <span>•</span>
              <span>{graphData.edges.length} edges</span>
            </>
          )}
        </div>
        <div className="flex items-center gap-4">
          {/* Zoom level indicator */}
          {zoom !== 1 && (
            <span 
              className="text-slate-400 cursor-pointer hover:text-slate-600" 
              onClick={resetZoom}
              title="Click to reset zoom"
            >
              Zoom: {Math.round(zoom * 100)}%
            </span>
          )}
          <span className="text-slate-400 truncate max-w-xs" title={projectPath || ''}>
            {projectPath}
          </span>
          <span className="flex items-center gap-1">
            <span className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            {wsConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </footer>
    </div>
  );
}

export default App;
