/**
 * PathInput - Reusable input component for file/directory paths
 *
 * Features:
 * - Text input for manual path entry
 * - Browse button that opens DirectoryBrowserModal
 * - Drag-and-drop support with visual feedback
 * - File upload mode for importing archives (uploads to server and returns path)
 *
 * Note: In standard web browsers, dragging files/folders from the OS file explorer
 * does NOT provide the file path for security reasons. However, when `allowFileUpload`
 * is enabled (for 'file' mode), dropped files will be uploaded to the server and the
 * server path will be returned.
 */

import { useState, useCallback } from 'react';
import { FolderOpen, AlertCircle, Upload, Loader2 } from 'lucide-react';
import { DirectoryBrowserModal } from './DirectoryBrowserModal';
import { portableApi } from '../../services/api';

// =============================================================================
// Types
// =============================================================================

export interface PathInputProps {
  /** Current path value */
  value: string;
  /** Callback when path changes */
  onChange: (value: string) => void;
  /** Placeholder text */
  placeholder?: string;
  /** Browse mode: 'directory' for folders only, 'file' for files only, 'all' for both */
  browseMode: 'directory' | 'file' | 'all';
  /** File extensions to filter (for 'file' or 'all' mode) */
  fileExtensions?: string[];
  /** Whether the input is disabled */
  disabled?: boolean;
  /** Additional CSS classes for the container */
  className?: string;
  /** Blur event handler */
  onBlur?: () => void;
  /** Key down event handler */
  onKeyDown?: (e: React.KeyboardEvent<HTMLInputElement>) => void;
  /** Modal title override */
  browseTitle?: string;
  /**
   * Enable file upload on drag-drop (for 'file' mode only).
   * When enabled, dropped files will be uploaded to the server
   * and the server path will be returned.
   */
  allowFileUpload?: boolean;
}

// =============================================================================
// Component
// =============================================================================

export function PathInput({
  value,
  onChange,
  placeholder,
  browseMode,
  fileExtensions,
  disabled = false,
  className = '',
  onBlur,
  onKeyDown,
  browseTitle,
  allowFileUpload = false,
}: PathInputProps) {
  const [isBrowseModalOpen, setIsBrowseModalOpen] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const [dragDropWarning, setDragDropWarning] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  // Extract directory from current value for initial browse location
  const getInitialDirectory = useCallback(() => {
    if (!value) return undefined;

    // If browsing for directory, use current value
    if (browseMode === 'directory') {
      return value;
    }

    // If browsing for file, use parent directory
    const parts = value.split(/[\\/]/);
    if (parts.length > 1) {
      parts.pop();
      return parts.join('\\') || parts.join('/');
    }

    return undefined;
  }, [value, browseMode]);

  // Handle drag events
  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) {
      setIsDragOver(true);
    }
  }, [disabled]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) {
      setIsDragOver(true);
    }
  }, [disabled]);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    if (disabled || isUploading) return;

    // Debug: log available data types
    console.log('[PathInput] Drop event - available types:', e.dataTransfer.types);

    // Try to get path from dropped files (works in Electron/desktop contexts)
    if (e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      console.log('[PathInput] File dropped:', file.name, 'type:', file.type);

      // In Electron, file.path contains the full path
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const filePath = (file as any).path;
      if (filePath) {
        console.log('[PathInput] Using file.path:', filePath);
        onChange(filePath);
        return;
      }

      // In standard browsers, file.path doesn't exist
      // If allowFileUpload is enabled, upload the file to the server
      if (allowFileUpload && browseMode === 'file') {
        // Validate file extension if specified
        if (fileExtensions && fileExtensions.length > 0) {
          const hasValidExtension = fileExtensions.some(ext =>
            file.name.toLowerCase().endsWith(ext.toLowerCase())
          );
          if (!hasValidExtension) {
            setDragDropWarning(`Only ${fileExtensions.join(', ')} files are supported`);
            setTimeout(() => setDragDropWarning(null), 5000);
            return;
          }
        }

        // Upload the file
        console.log('[PathInput] Uploading file to server...');
        setIsUploading(true);
        setDragDropWarning(null);

        try {
          const result = await portableApi.uploadArchive(file);
          console.log('[PathInput] Upload successful:', result.file_path);
          onChange(result.file_path);
        } catch (err) {
          console.error('[PathInput] Upload failed:', err);
          setDragDropWarning(err instanceof Error ? err.message : 'Upload failed');
          setTimeout(() => setDragDropWarning(null), 5000);
        } finally {
          setIsUploading(false);
        }
        return;
      }
    }

    // Try all available data types and log them
    for (const type of e.dataTransfer.types) {
      const data = e.dataTransfer.getData(type);
      console.log(`[PathInput] Data for type "${type}":`, data);
    }

    // Fallback: try to get path from text/uri-list
    const uriList = e.dataTransfer.getData('text/uri-list');
    if (uriList) {
      // Parse file:// URIs
      const lines = uriList.split('\n').filter(line => !line.startsWith('#'));
      if (lines.length > 0) {
        let path = lines[0].trim();
        console.log('[PathInput] URI from text/uri-list:', path);
        // Convert file:// URI to path
        if (path.startsWith('file:///')) {
          // Windows: file:///C:/path -> C:/path
          path = path.slice(8);
          // Decode URL encoding
          path = decodeURIComponent(path);
          // Convert forward slashes to backslashes on Windows-style paths
          if (path.match(/^[A-Za-z]:/)) {
            path = path.replace(/\//g, '\\');
          }
          console.log('[PathInput] Converted path:', path);
          onChange(path);
          return;
        }
      }
    }

    // Fallback: try to get path from plain text
    const textData = e.dataTransfer.getData('text/plain');
    if (textData) {
      const trimmed = textData.trim();
      console.log('[PathInput] Plain text data:', trimmed);
      // Check if it looks like a path (contains path separators)
      if (trimmed.includes('/') || trimmed.includes('\\')) {
        onChange(trimmed);
        return;
      }
    }

    // If we have files but couldn't get the path and upload wasn't enabled, show warning
    if (e.dataTransfer.files.length > 0 && !allowFileUpload) {
      console.warn('[PathInput] File was dropped but path could not be extracted. In web browsers, file paths are not accessible for security reasons. Please use the Browse button or paste the path manually.');
      setDragDropWarning('Browser security prevents accessing file paths. Use the Browse button or paste the path.');
      setTimeout(() => setDragDropWarning(null), 5000);
    }
  }, [disabled, isUploading, onChange, allowFileUpload, browseMode, fileExtensions]);

  // Handle browse button click
  const handleBrowseClick = useCallback(() => {
    if (!disabled) {
      setIsBrowseModalOpen(true);
    }
  }, [disabled]);

  // Handle modal selection
  const handleSelect = useCallback((path: string) => {
    onChange(path);
    setIsBrowseModalOpen(false);
  }, [onChange]);

  return (
    <>
      <div className={className}>
        <div
          className="flex gap-2"
          onDragEnter={handleDragEnter}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <div className={`relative flex-1 ${isDragOver ? 'ring-2 ring-blue-500 rounded-lg' : ''}`}>
            <input
              type="text"
              value={value}
              onChange={(e) => onChange(e.target.value)}
              onBlur={onBlur}
              onKeyDown={onKeyDown}
              placeholder={placeholder}
              disabled={disabled || isUploading}
              className={`w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed ${
                isDragOver ? 'bg-blue-50 border-blue-400' : ''
              }`}
            />
            {isDragOver && !isUploading && (
              <div className="absolute inset-0 flex items-center justify-center bg-blue-50/90 rounded-lg pointer-events-none border-2 border-dashed border-blue-400">
                <Upload className="w-4 h-4 text-blue-600 mr-2" />
                <span className="text-blue-600 text-sm font-medium">
                  {allowFileUpload ? 'Drop file to upload' : 'Drop path here'}
                </span>
              </div>
            )}
            {isUploading && (
              <div className="absolute inset-0 flex items-center justify-center bg-blue-50/90 rounded-lg pointer-events-none border-2 border-blue-400">
                <Loader2 className="w-4 h-4 text-blue-600 mr-2 animate-spin" />
                <span className="text-blue-600 text-sm font-medium">Uploading...</span>
              </div>
            )}
          </div>
          <button
            type="button"
            onClick={handleBrowseClick}
            disabled={disabled}
            className="px-3 py-2 bg-slate-100 hover:bg-slate-200 border border-slate-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title="Browse..."
          >
            <FolderOpen className="w-4 h-4 text-slate-600" />
          </button>
        </div>
        {dragDropWarning && (
          <div className="mt-1 flex items-center gap-1 text-xs text-amber-600">
            <AlertCircle className="w-3 h-3 flex-shrink-0" />
            <span>{dragDropWarning}</span>
            <button
              onClick={() => setDragDropWarning(null)}
              className="ml-1 text-amber-500 hover:text-amber-700"
            >
              ×
            </button>
          </div>
        )}
      </div>

      <DirectoryBrowserModal
        isOpen={isBrowseModalOpen}
        onClose={() => setIsBrowseModalOpen(false)}
        onSelect={handleSelect}
        initialDirectory={getInitialDirectory()}
        mode={browseMode}
        fileExtensions={fileExtensions}
        title={browseTitle}
      />
    </>
  );
}
