/**
 * DirectoryBrowserModal - Modal for browsing and selecting directories or files
 *
 * Features:
 * - Directory navigation (click to enter, up button for parent)
 * - Mode filtering: directory-only, file-only, or all
 * - Manual path input for quick navigation
 * - File extension filtering
 */

import { useState, useEffect, useCallback } from 'react';
import {
  X,
  Folder,
  File,
  ArrowUp,
  RefreshCw,
  ChevronRight,
  HardDrive,
} from 'lucide-react';
import { editorApi } from '../../services/editorApi';
import type { FileInfo } from '../../types/editor';

// =============================================================================
// Types
// =============================================================================

export interface DirectoryBrowserModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (path: string) => void;
  initialDirectory?: string;
  title?: string;
  mode: 'directory' | 'file' | 'all';
  fileExtensions?: string[];
}

interface FileEntry {
  name: string;
  path: string;
  is_dir: boolean;
  size?: number;
}

// =============================================================================
// Component
// =============================================================================

export function DirectoryBrowserModal({
  isOpen,
  onClose,
  onSelect,
  initialDirectory,
  title,
  mode,
  fileExtensions,
}: DirectoryBrowserModalProps) {
  const [currentDir, setCurrentDir] = useState(initialDirectory || '');
  const [inputPath, setInputPath] = useState(initialDirectory || '');
  const [files, setFiles] = useState<FileEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedItem, setSelectedItem] = useState<string | null>(null);

  // Get default title based on mode
  const modalTitle = title || (mode === 'directory' ? 'Select Directory' : mode === 'file' ? 'Select File' : 'Select Path');

  // Load directory contents
  const loadDirectory = useCallback(async (dir: string) => {
    if (!dir.trim()) {
      setError('Please enter a directory path');
      return;
    }

    setLoading(true);
    setError(null);
    setSelectedItem(null);

    try {
      const result = await editorApi.listFiles(dir, false);

      // Map and filter based on mode
      let entries: FileEntry[] = result.files.map((f: FileInfo) => ({
        name: f.name,
        path: f.path,
        is_dir: f.is_dir ?? false,
        size: f.size,
      }));

      // Filter by mode
      if (mode === 'directory') {
        entries = entries.filter(e => e.is_dir);
      } else if (mode === 'file') {
        entries = entries.filter(e => !e.is_dir);
      }

      // Filter by file extensions if provided (only for files)
      if (fileExtensions && fileExtensions.length > 0) {
        entries = entries.filter(e => {
          if (e.is_dir) return true; // Always show directories for navigation
          return fileExtensions.some(ext =>
            e.name.toLowerCase().endsWith(ext.toLowerCase())
          );
        });
      }

      // Sort: directories first, then alphabetically
      entries.sort((a, b) => {
        if (a.is_dir && !b.is_dir) return -1;
        if (!a.is_dir && b.is_dir) return 1;
        return a.name.localeCompare(b.name);
      });

      setFiles(entries);
      setCurrentDir(dir);
      setInputPath(dir);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load directory');
      setFiles([]);
    } finally {
      setLoading(false);
    }
  }, [mode, fileExtensions]);

  // Load initial directory when modal opens
  useEffect(() => {
    if (isOpen && initialDirectory) {
      loadDirectory(initialDirectory);
    } else if (isOpen && !initialDirectory) {
      // Try common default paths
      const defaultPaths = ['C:\\', 'C:\\Users', '/home', '/'];
      setInputPath(defaultPaths[0]);
    }
  }, [isOpen, initialDirectory, loadDirectory]);

  // Navigate to parent directory
  const navigateUp = () => {
    const parts = currentDir.replace(/[\\/]+$/, '').split(/[\\/]/);
    if (parts.length > 1) {
      parts.pop();
      // Handle Windows drive root (e.g., "C:")
      let parentDir = parts.join('\\');
      if (parentDir.match(/^[A-Za-z]:$/)) {
        parentDir += '\\';
      } else if (!parentDir) {
        parentDir = '/';
      }
      loadDirectory(parentDir);
    }
  };

  // Handle item click
  const handleItemClick = (item: FileEntry) => {
    if (item.is_dir) {
      // For directories: navigate into them
      loadDirectory(item.path);
    } else {
      // For files: select them
      setSelectedItem(item.path);
    }
  };

  // Handle item double-click (for directory selection mode)
  const handleItemDoubleClick = (item: FileEntry) => {
    if (item.is_dir && mode === 'directory') {
      // In directory mode, double-click selects the directory
      onSelect(item.path);
      onClose();
    } else if (!item.is_dir) {
      // For files, double-click selects
      onSelect(item.path);
      onClose();
    }
  };

  // Handle select button click
  const handleSelect = () => {
    if (mode === 'directory') {
      // In directory mode, select the current directory
      onSelect(currentDir);
    } else if (selectedItem) {
      // In file/all mode, select the selected item
      onSelect(selectedItem);
    }
    onClose();
  };

  // Handle manual path navigation
  const handleGoToPath = () => {
    if (inputPath.trim()) {
      loadDirectory(inputPath.trim());
    }
  };

  // Handle keyboard events
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleGoToPath();
    } else if (e.key === 'Escape') {
      onClose();
    }
  };

  // Parse path into breadcrumb segments
  const getBreadcrumbs = (): { name: string; path: string }[] => {
    if (!currentDir) return [];

    const parts = currentDir.split(/[\\/]/).filter(Boolean);
    const breadcrumbs: { name: string; path: string }[] = [];

    // Handle Windows drive letter
    if (currentDir.match(/^[A-Za-z]:/)) {
      let accPath = parts[0] + '\\';
      breadcrumbs.push({ name: parts[0], path: accPath });

      for (let i = 1; i < parts.length; i++) {
        accPath += parts[i] + '\\';
        breadcrumbs.push({ name: parts[i], path: accPath.replace(/\\+$/, '') });
      }
    } else {
      // Unix-style paths
      let accPath = '/';
      breadcrumbs.push({ name: '/', path: '/' });

      for (const part of parts) {
        accPath += part + '/';
        breadcrumbs.push({ name: part, path: accPath.replace(/\/+$/, '') });
      }
    }

    return breadcrumbs;
  };

  if (!isOpen) return null;

  const breadcrumbs = getBreadcrumbs();
  const canSelect = mode === 'directory' ? !!currentDir : !!selectedItem;

  return (
    <div
      className="fixed inset-0 bg-black/30 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg shadow-xl w-[600px] max-h-[80vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-200">
          <div className="flex items-center gap-2">
            <HardDrive className="w-5 h-5 text-slate-500" />
            <h2 className="text-lg font-semibold text-slate-800">{modalTitle}</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-slate-100 rounded text-slate-400 hover:text-slate-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Path input */}
        <div className="p-3 border-b border-slate-100">
          <div className="flex gap-2">
            <input
              type="text"
              value={inputPath}
              onChange={(e) => setInputPath(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Enter path..."
              className="flex-1 px-3 py-2 bg-white border border-slate-300 rounded-lg text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <button
              onClick={handleGoToPath}
              disabled={loading || !inputPath.trim()}
              className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Go
            </button>
          </div>
        </div>

        {/* Breadcrumb navigation */}
        <div className="flex items-center gap-1 px-3 py-2 bg-slate-50 border-b border-slate-100 overflow-x-auto">
          <button
            onClick={navigateUp}
            disabled={loading || !currentDir || breadcrumbs.length <= 1}
            className="p-1 hover:bg-slate-200 rounded disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
            title="Go to parent directory"
          >
            <ArrowUp className="w-4 h-4 text-slate-600" />
          </button>
          <div className="flex items-center gap-0.5 text-sm overflow-x-auto flex-1">
            {breadcrumbs.map((crumb, index) => (
              <span key={crumb.path} className="flex items-center flex-shrink-0">
                {index > 0 && <ChevronRight className="w-3 h-3 text-slate-400 mx-0.5" />}
                <button
                  onClick={() => loadDirectory(crumb.path)}
                  className="px-1.5 py-0.5 hover:bg-slate-200 rounded text-slate-600 hover:text-slate-800 truncate max-w-[120px]"
                  title={crumb.path}
                >
                  {crumb.name}
                </button>
              </span>
            ))}
          </div>
          <button
            onClick={() => loadDirectory(currentDir)}
            disabled={loading}
            className="p-1 hover:bg-slate-200 rounded flex-shrink-0"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 text-slate-500 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {/* File list */}
        <div className="flex-1 overflow-auto min-h-[300px]">
          {error && (
            <div className="p-4 text-sm text-red-600 bg-red-50 border-b border-red-100">
              {error}
            </div>
          )}

          {loading ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-500">
              <RefreshCw className="w-6 h-6 animate-spin mb-2" />
              <span className="text-sm">Loading...</span>
            </div>
          ) : files.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-400">
              <Folder className="w-8 h-8 mb-2" />
              <span className="text-sm">
                {mode === 'directory' ? 'No subdirectories' : 'No files found'}
              </span>
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {files.map((file) => (
                <div
                  key={file.path}
                  onClick={() => handleItemClick(file)}
                  onDoubleClick={() => handleItemDoubleClick(file)}
                  className={`flex items-center gap-3 px-4 py-2.5 hover:bg-slate-50 cursor-pointer transition-colors ${
                    selectedItem === file.path ? 'bg-blue-50 border-l-2 border-blue-500' : ''
                  }`}
                >
                  {file.is_dir ? (
                    <Folder className="w-5 h-5 text-amber-500 flex-shrink-0" />
                  ) : (
                    <File className="w-5 h-5 text-slate-400 flex-shrink-0" />
                  )}
                  <span className="flex-1 text-sm text-slate-700 truncate" title={file.name}>
                    {file.name}
                  </span>
                  {!file.is_dir && file.size !== undefined && (
                    <span className="text-xs text-slate-400 flex-shrink-0">
                      {file.size < 1024
                        ? `${file.size} B`
                        : file.size < 1024 * 1024
                          ? `${(file.size / 1024).toFixed(1)} KB`
                          : `${(file.size / 1024 / 1024).toFixed(1)} MB`
                      }
                    </span>
                  )}
                  {file.is_dir && (
                    <ChevronRight className="w-4 h-4 text-slate-300 flex-shrink-0" />
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-4 border-t border-slate-200 bg-slate-50 rounded-b-lg">
          <div className="text-xs text-slate-500 truncate flex-1 mr-4">
            {mode === 'directory' && currentDir && (
              <span>Selected: <span className="font-medium text-slate-700">{currentDir}</span></span>
            )}
            {mode !== 'directory' && selectedItem && (
              <span>Selected: <span className="font-medium text-slate-700">{selectedItem.split(/[\\/]/).pop()}</span></span>
            )}
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm text-slate-600 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSelect}
              disabled={!canSelect}
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Select
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
