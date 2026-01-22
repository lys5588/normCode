/**
 * ResizablePanel - A panel component with draggable resize handles
 * Supports horizontal and vertical resizing with min/max constraints
 */

import { useState, useRef, useCallback, useEffect, ReactNode } from 'react';

export type ResizeDirection = 'left' | 'right' | 'top' | 'bottom';

interface ResizablePanelProps {
  children: ReactNode;
  direction: ResizeDirection;
  defaultSize: number;
  minSize?: number;
  maxSize?: number;
  onResize?: (size: number) => void;
  className?: string;
  handleClassName?: string;
  storageKey?: string; // For persisting size to localStorage
}

export function ResizablePanel({
  children,
  direction,
  defaultSize,
  minSize = 100,
  maxSize = 800,
  onResize,
  className = '',
  handleClassName = '',
  storageKey,
}: ResizablePanelProps) {
  // Load initial size from localStorage if storageKey provided
  const getInitialSize = () => {
    if (storageKey) {
      const saved = localStorage.getItem(`panel-size-${storageKey}`);
      if (saved) {
        const parsed = parseInt(saved, 10);
        if (!isNaN(parsed) && parsed >= minSize && parsed <= maxSize) {
          return parsed;
        }
      }
    }
    return defaultSize;
  };

  const [size, setSize] = useState(getInitialSize);
  const [isResizing, setIsResizing] = useState(false);
  const panelRef = useRef<HTMLDivElement>(null);
  const startPosRef = useRef(0);
  const startSizeRef = useRef(0);

  // Determine if this is a horizontal or vertical resize
  const isHorizontal = direction === 'left' || direction === 'right';

  // Save size to localStorage when it changes
  useEffect(() => {
    if (storageKey) {
      localStorage.setItem(`panel-size-${storageKey}`, size.toString());
    }
  }, [size, storageKey]);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
    startPosRef.current = isHorizontal ? e.clientX : e.clientY;
    startSizeRef.current = size;
  }, [isHorizontal, size]);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isResizing) return;

    const currentPos = isHorizontal ? e.clientX : e.clientY;
    const delta = currentPos - startPosRef.current;

    // Calculate new size based on direction
    let newSize: number;
    if (direction === 'right' || direction === 'bottom') {
      newSize = startSizeRef.current - delta;
    } else {
      newSize = startSizeRef.current + delta;
    }

    // Clamp to min/max
    newSize = Math.max(minSize, Math.min(maxSize, newSize));

    setSize(newSize);
    onResize?.(newSize);
  }, [isResizing, isHorizontal, direction, minSize, maxSize, onResize]);

  const handleMouseUp = useCallback(() => {
    setIsResizing(false);
  }, []);

  // Add/remove global mouse listeners
  useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = isHorizontal ? 'col-resize' : 'row-resize';
      document.body.style.userSelect = 'none';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizing, handleMouseMove, handleMouseUp, isHorizontal]);

  // Generate style based on direction
  const panelStyle: React.CSSProperties = {
    ...(isHorizontal ? { width: size } : { height: size }),
    flexShrink: 0,
  };

  // Handle position classes
  const handlePositionClasses = {
    left: 'left-0 top-0 bottom-0 w-1 cursor-col-resize hover:bg-blue-400',
    right: 'right-0 top-0 bottom-0 w-1 cursor-col-resize hover:bg-blue-400',
    top: 'top-0 left-0 right-0 h-1 cursor-row-resize hover:bg-blue-400',
    bottom: 'bottom-0 left-0 right-0 h-1 cursor-row-resize hover:bg-blue-400',
  };

  return (
    <div
      ref={panelRef}
      className={`relative ${className}`}
      style={panelStyle}
    >
      {children}
      
      {/* Resize handle */}
      <div
        className={`absolute z-30 transition-colors ${handlePositionClasses[direction]} ${
          isResizing ? 'bg-blue-500' : 'bg-transparent'
        } ${handleClassName}`}
        onMouseDown={handleMouseDown}
      >
        {/* Wider invisible hit area */}
        <div 
          className={`absolute ${
            isHorizontal 
              ? 'w-3 h-full -left-1' 
              : 'h-3 w-full -top-1'
          }`}
        />
      </div>
    </div>
  );
}

/**
 * Horizontal resize divider - a standalone divider between two horizontal panels
 */
interface ResizeDividerProps {
  onResize: (delta: number) => void;
  direction: 'horizontal' | 'vertical';
  className?: string;
}

export function ResizeDivider({ onResize, direction, className = '' }: ResizeDividerProps) {
  const [isResizing, setIsResizing] = useState(false);
  const startPosRef = useRef(0);

  const isHorizontal = direction === 'horizontal';

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
    startPosRef.current = isHorizontal ? e.clientX : e.clientY;
  }, [isHorizontal]);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isResizing) return;

    const currentPos = isHorizontal ? e.clientX : e.clientY;
    const delta = currentPos - startPosRef.current;
    startPosRef.current = currentPos;

    onResize(delta);
  }, [isResizing, isHorizontal, onResize]);

  const handleMouseUp = useCallback(() => {
    setIsResizing(false);
  }, []);

  useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = isHorizontal ? 'col-resize' : 'row-resize';
      document.body.style.userSelect = 'none';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizing, handleMouseMove, handleMouseUp, isHorizontal]);

  return (
    <div
      className={`flex-shrink-0 ${
        isHorizontal ? 'w-1 cursor-col-resize' : 'h-1 cursor-row-resize'
      } ${isResizing ? 'bg-blue-500' : 'bg-slate-200 hover:bg-blue-400'} transition-colors ${className}`}
      onMouseDown={handleMouseDown}
    />
  );
}

