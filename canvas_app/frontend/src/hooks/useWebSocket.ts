/**
 * Hook for WebSocket connection and event handling
 * 
 * Supports multi-project execution by filtering events based on project_id.
 * Events from inactive projects are logged but not processed for UI updates.
 * 
 * Event handlers are organized by category for maintainability:
 * - Execution lifecycle (start, stop, pause, resume, etc.)
 * - Inference events (started, completed, failed)
 * - Breakpoint events
 * - Step/sequence progress
 * - Agent and tool call events
 * - User input events
 * - Chat events
 * - Canvas commands
 * - Remote execution events
 */

import { useEffect, useCallback, useState } from 'react';
import { wsClient } from '../services/websocket';
import { useExecutionStore, type UserInputRequest } from '../stores/executionStore';
import { useAgentStore } from '../stores/agentStore';
import { useProjectStore } from '../stores/projectStore';
import { useChatStore, type ChatInputRequest, type MessageRole, type ChatStatusType } from '../stores/chatStore';
import { useCanvasCommandStore } from '../stores/canvasCommandStore';
import { usePanelStore, type PanelName } from '../stores/panelStore';
import type { WebSocketEvent, StepProgress, RunMode, ExecutionStatus } from '../types/execution';
import type { NodeStatus } from '../types/execution';
import type { ToolCallEvent, AgentConfig } from '../stores/agentStore';
import type { ChatBufferStatus } from '../services/api';

// =============================================================================
// Type Definitions
// =============================================================================

type EventData = Record<string, unknown>;

interface EventHandlerContext {
  // Execution store actions
  setStatus: (status: ExecutionStatus) => void;
  setNodeStatus: (flowIndex: string, status: NodeStatus) => void;
  setNodeStatuses: (statuses: Record<string, NodeStatus>) => void;
  setCurrentInference: (inference: string | null) => void;
  setProgress: (completed: number, total: number, cycle?: number) => void;
  addLog: (log: { flowIndex: string; level: string; message: string }) => void;
  addBreakpoint: (flowIndex: string) => void;
  removeBreakpoint: (flowIndex: string) => void;
  setRunId: (runId: string) => void;
  setStepProgress: (flowIndex: string, progress: StepProgress) => void;
  updateStepProgress: (flowIndex: string, update: Partial<StepProgress>) => void;
  clearStepProgress: () => void;
  fetchConceptStatuses: () => void;
  setRunMode: (mode: RunMode) => void;
  addUserInputRequest: (request: UserInputRequest) => void;
  removeUserInputRequest: (requestId: string) => void;
  
  // Agent store actions
  addToolCall: (event: ToolCallEvent) => void;
  updateToolCall: (id: string, update: Partial<ToolCallEvent>) => void;
  addAgent: (agent: AgentConfig) => void;
  updateAgent: (agentId: string, update: Partial<AgentConfig>) => void;
  deleteAgent: (agentId: string) => void;
  
  // Chat store actions
  addMessageFromApi: (message: { id: string; role: MessageRole; content: string; timestamp: string; metadata?: Record<string, unknown> }) => void;
  updateControllerInfo: (info: Record<string, unknown>) => void;
  setInputRequest: (request: ChatInputRequest | null) => void;
  updateBufferStatus: (status: ChatBufferStatus) => void;
  clearBuffer: () => void;
  
  // Chat action handlers (from First Person / Hands)
  setChatInputValue: (value: string) => void;
  submitChatInput: () => void;
  respondToInputRequest: (response: string) => void;
  
  // Notification handlers (temporary status)
  showNotification: (content: string, type?: ChatStatusType) => void;
  clearNotification: () => void;
  
  // Canvas store actions
  addCanvasCommand: (type: string, params: Record<string, unknown>) => void;
  
  // Panel store actions
  openPanel: (panel: PanelName) => void;
  closePanel: (panel: PanelName) => void;
  togglePanel: (panel: PanelName) => void;
  focusPanel: (panel: PanelName) => void;
}

type EventHandler = (data: EventData, ctx: EventHandlerContext) => void;

// =============================================================================
// Execution Lifecycle Handlers
// =============================================================================

const executionHandlers: Record<string, EventHandler> = {
  'execution:loaded': (data, ctx) => {
    // Loading/resuming puts execution in idle state - ready to start
    ctx.setStatus('idle');
    ctx.setCurrentInference(null);
    
    if (data.run_id) {
      ctx.setRunId(data.run_id as string);
    }
    if (data.total_inferences !== undefined) {
      const completed = (data.completed_count as number) || 0;
      ctx.setProgress(completed, data.total_inferences as number);
    }
    if (data.node_statuses) {
      ctx.setNodeStatuses(data.node_statuses as Record<string, NodeStatus>);
    }
    ctx.fetchConceptStatuses();
  },

  'execution:started': (_data, ctx) => {
    ctx.setStatus('running');
    ctx.updateBufferStatus({
      execution_active: true,
      has_pending_request: false,
      has_buffered_message: false,
      buffered_message: null,
    });
  },

  'execution:paused': (data, ctx) => {
    ctx.setStatus('paused');
    if (data.inference) {
      ctx.setCurrentInference(data.inference as string);
    }
    ctx.fetchConceptStatuses();
  },

  'execution:resumed': (_data, ctx) => {
    ctx.setStatus('running');
    ctx.updateBufferStatus({
      execution_active: true,
      has_pending_request: false,
      has_buffered_message: false,
      buffered_message: null,
    });
  },

  'execution:completed': (data, ctx) => {
    ctx.setStatus('completed');
    ctx.setCurrentInference(null);
    if (data.completed_count !== undefined && data.total_count !== undefined) {
      ctx.setProgress(data.completed_count as number, data.total_count as number);
    }
    ctx.clearBuffer();
    ctx.updateBufferStatus({
      execution_active: false,
      has_pending_request: false,
      has_buffered_message: false,
      buffered_message: null,
    });
  },

  'execution:error': (data, ctx) => {
    ctx.setStatus('failed');
    ctx.addLog({
      flowIndex: '',
      level: 'error',
      message: data.error as string,
    });
    ctx.clearBuffer();
    ctx.updateBufferStatus({
      execution_active: false,
      has_pending_request: false,
      has_buffered_message: false,
      buffered_message: null,
    });
  },

  'execution:stopped': (_data, ctx) => {
    ctx.setStatus('idle');
    ctx.setCurrentInference(null);
    ctx.clearBuffer();
    ctx.updateBufferStatus({
      execution_active: false,
      has_pending_request: false,
      has_buffered_message: false,
      buffered_message: null,
    });
  },

  'execution:reset': (data, ctx) => {
    ctx.setStatus('idle');
    ctx.setCurrentInference(null);
    ctx.clearBuffer();
    ctx.updateBufferStatus({
      execution_active: false,
      has_pending_request: false,
      has_buffered_message: false,
      buffered_message: null,
    });
    
    if (data.run_id) {
      ctx.setRunId(data.run_id as string);
    }
    if (data.node_statuses) {
      ctx.setNodeStatuses(data.node_statuses as Record<string, NodeStatus>);
    }
    if (data.completed_count !== undefined && data.total_count !== undefined) {
      ctx.setProgress(data.completed_count as number, data.total_count as number);
    }
    ctx.clearStepProgress();
    ctx.addLog({
      flowIndex: '',
      level: 'info',
      message: data.run_id 
        ? `Execution reset with new run: ${data.run_id}` 
        : 'Execution reset - ready to run again',
    });
  },

  'execution:stepping': (_data, ctx) => {
    ctx.setStatus('stepping');
  },

  'execution:run_mode_changed': (data, ctx) => {
    if (data.mode) {
      ctx.setRunMode(data.mode as RunMode);
    }
  },

  'execution:progress': (data, ctx) => {
    if (data.completed_count !== undefined && data.total_count !== undefined) {
      ctx.setProgress(data.completed_count as number, data.total_count as number);
    }
    if (data.current_inference) {
      ctx.setCurrentInference(data.current_inference as string);
    }
  },

  'execution:partial_reset': (data, ctx) => {
    if (data.reset_nodes) {
      ctx.addLog({
        flowIndex: (data.from_flow_index as string) || '',
        level: 'info',
        message: `Partial reset: ${(data.reset_nodes as string[]).length} nodes reset from ${data.from_flow_index}`,
      });
      for (const fi of (data.reset_nodes as string[])) {
        ctx.setNodeStatus(fi, 'pending');
      }
    }
  },
};

// =============================================================================
// Inference Handlers
// =============================================================================

const inferenceHandlers: Record<string, EventHandler> = {
  'inference:started': (data, ctx) => {
    if (data.flow_index) {
      ctx.setNodeStatus(data.flow_index as string, 'running');
      ctx.setCurrentInference(data.flow_index as string);
    }
  },

  'inference:completed': (data, ctx) => {
    if (data.flow_index) {
      ctx.setNodeStatus(data.flow_index as string, 'completed');
      ctx.fetchConceptStatuses();
    }
  },

  'inference:failed': (data, ctx) => {
    if (data.flow_index) {
      ctx.setNodeStatus(data.flow_index as string, 'failed');
      ctx.addLog({
        flowIndex: data.flow_index as string,
        level: 'error',
        message: (data.error as string) || 'Inference failed',
      });
    }
  },

  'inference:retry': (data, ctx) => {
    if (data.flow_index) {
      ctx.setNodeStatus(data.flow_index as string, 'pending');
      ctx.addLog({
        flowIndex: data.flow_index as string,
        level: 'warning',
        message: `Retry scheduled: ${data.status || 'unknown status'}`,
      });
    }
  },

  'inference:updated': (data, ctx) => {
    if (data.flow_index && data.status) {
      ctx.setNodeStatus(data.flow_index as string, data.status as NodeStatus);
    }
  },
};

// =============================================================================
// Breakpoint Handlers
// =============================================================================

const breakpointHandlers: Record<string, EventHandler> = {
  'breakpoint:hit': (data, ctx) => {
    ctx.setStatus('paused');
    if (data.flow_index) {
      ctx.setCurrentInference(data.flow_index as string);
      ctx.addLog({
        flowIndex: data.flow_index as string,
        level: 'info',
        message: `Breakpoint hit at ${data.flow_index}`,
      });
    }
  },

  'breakpoint:set': (data, ctx) => {
    if (data.flow_index) {
      ctx.addBreakpoint(data.flow_index as string);
    }
  },

  'breakpoint:cleared': (data, ctx) => {
    if (data.flow_index) {
      ctx.removeBreakpoint(data.flow_index as string);
    }
  },
};

// =============================================================================
// Step/Sequence Progress Handlers
// =============================================================================

const stepProgressHandlers: Record<string, EventHandler> = {
  'step:started': (data, ctx) => {
    if (data.flow_index) {
      const flowIndex = data.flow_index as string;
      ctx.updateStepProgress(flowIndex, {
        current_step: (data.step_name as string) || null,
        current_step_index: (data.step_index as number) || 0,
        sequence_type: (data.sequence_type as string) || null,
        total_steps: (data.total_steps as number) || 0,
        steps: (data.steps as string[]) || [],
        paradigm: (data.paradigm as string) || null,
      });
    }
  },

  'step:completed': (data, ctx) => {
    if (data.flow_index && data.step_name) {
      const flowIndex = data.flow_index as string;
      const stepName = data.step_name as string;
      const currentProgress = useExecutionStore.getState().stepProgress[flowIndex];
      ctx.updateStepProgress(flowIndex, {
        completed_steps: [...(currentProgress?.completed_steps || []), stepName],
      });
    }
  },

  'sequence:started': (data, ctx) => {
    if (data.flow_index) {
      const flowIndex = data.flow_index as string;
      ctx.setStepProgress(flowIndex, {
        flow_index: flowIndex,
        sequence_type: (data.sequence_type as string) || null,
        current_step: null,
        current_step_index: 0,
        total_steps: (data.total_steps as number) || 0,
        steps: (data.steps as string[]) || [],
        completed_steps: [],
      });
    }
  },

  'sequence:completed': (data, ctx) => {
    if (data.flow_index) {
      const flowIndex = data.flow_index as string;
      const progress = useExecutionStore.getState().stepProgress[flowIndex];
      if (progress) {
        ctx.updateStepProgress(flowIndex, {
          current_step: null,
          completed_steps: progress.steps,
        });
      }
    }
  },
};

// =============================================================================
// Agent and Tool Call Handlers
// =============================================================================

const agentToolHandlers: Record<string, EventHandler> = {
  'tool:call_started': (data, ctx) => {
    ctx.addToolCall(data as unknown as ToolCallEvent);
  },

  'tool:call_completed': (data, ctx) => {
    if (data.id) {
      ctx.updateToolCall(data.id as string, data as unknown as Partial<ToolCallEvent>);
    } else {
      ctx.addToolCall(data as unknown as ToolCallEvent);
    }
  },

  'tool:call_failed': (data, ctx) => {
    if (data.id) {
      ctx.updateToolCall(data.id as string, data as unknown as Partial<ToolCallEvent>);
    } else {
      ctx.addToolCall(data as unknown as ToolCallEvent);
    }
  },

  'agent:registered': (data, ctx) => {
    ctx.addAgent(data as unknown as AgentConfig);
  },

  'agent:updated': (data, ctx) => {
    ctx.addAgent(data as unknown as AgentConfig);
  },

  'agent:deleted': (data, ctx) => {
    if (data.agent_id) {
      ctx.deleteAgent(data.agent_id as string);
    }
  },
};

// =============================================================================
// Value Modification Handlers
// =============================================================================

const modificationHandlers: Record<string, EventHandler> = {
  'value:overridden': (data, ctx) => {
    if (data.concept_name && data.stale_nodes) {
      ctx.addLog({
        flowIndex: '',
        level: 'info',
        message: `Value overridden: ${data.concept_name}. ${(data.stale_nodes as string[]).length} nodes marked stale.`,
      });
      for (const fi of (data.stale_nodes as string[])) {
        ctx.setNodeStatus(fi, 'pending');
      }
    }
  },

  'function:modified': (data, ctx) => {
    if (data.flow_index && data.modified_fields) {
      ctx.addLog({
        flowIndex: data.flow_index as string,
        level: 'info',
        message: `Function modified: ${(data.modified_fields as string[]).join(', ')}`,
      });
      ctx.setNodeStatus(data.flow_index as string, 'pending');
    }
  },
};

// =============================================================================
// User Input Handlers
// =============================================================================

const userInputHandlers: Record<string, EventHandler> = {
  'user_input:request': (data, ctx) => {
    if (data.request_id) {
      const request: UserInputRequest = {
        request_id: data.request_id as string,
        prompt: (data.prompt as string) || 'Please provide input:',
        interaction_type: (data.interaction_type as UserInputRequest['interaction_type']) || 'text_input',
        options: data.options as UserInputRequest['options'],
        created_at: data.created_at as number,
      };
      ctx.addUserInputRequest(request);
      ctx.addLog({
        flowIndex: '',
        level: 'info',
        message: `User input requested: ${request.prompt.substring(0, 50)}${request.prompt.length > 50 ? '...' : ''}`,
      });
    }
  },

  'user_input:completed': (data, ctx) => {
    if (data.request_id) {
      ctx.removeUserInputRequest(data.request_id as string);
      ctx.addLog({
        flowIndex: '',
        level: 'info',
        message: `User input completed: ${data.request_id}`,
      });
    }
  },

  'user_input:cancelled': (data, ctx) => {
    if (data.request_id) {
      ctx.removeUserInputRequest(data.request_id as string);
      ctx.addLog({
        flowIndex: '',
        level: 'warning',
        message: `User input cancelled: ${data.request_id}`,
      });
    }
  },
};

// =============================================================================
// Chat Handlers
// =============================================================================

const chatHandlers: Record<string, EventHandler> = {
  'chat:message': (data, ctx) => {
    if (data.id && data.content) {
      ctx.addMessageFromApi({
        id: data.id as string,
        role: (data.role as MessageRole) || 'compiler',
        content: data.content as string,
        timestamp: (data.timestamp as string) || new Date().toISOString(),
        metadata: data.metadata as Record<string, unknown>,
      });
    }
  },

  'chat:compiler_status': (data, ctx) => {
    ctx.updateControllerInfo({
      status: data.status,
      controller_id: data.controller_id,
      controller_name: data.controller_name,
      controller_path: data.controller_path,
      current_flow_index: data.current_flow_index,
      error: data.error,
      placeholder_mode: data.placeholder_mode,
    });
  },

  'chat:controller_status': (data, ctx) => {
    ctx.updateControllerInfo({
      status: data.status,
      controller_id: data.controller_id,
      controller_name: data.controller_name,
      controller_path: data.controller_path,
      current_flow_index: data.current_flow_index,
      error: data.error,
      placeholder_mode: data.placeholder_mode,
    });
  },

  'chat:input_request': (data, ctx) => {
    if (data.id && data.prompt) {
      ctx.setInputRequest({
        id: data.id as string,
        prompt: data.prompt as string,
        inputType: (data.input_type as 'text' | 'code' | 'confirm' | 'select') || 'text',
        options: data.options as string[] | undefined,
        placeholder: data.placeholder as string | undefined,
        source: (data.source as 'controller' | 'execution') || 'controller',
      });
    }
  },

  'chat:input_cancelled': (_data, ctx) => {
    ctx.setInputRequest(null);
  },
  
  // =========================================================================
  // Chat Action Handlers (from First Person / Hands)
  // =========================================================================
  
  'chat:type': (data, ctx) => {
    // Type text into the chat input field
    const text = data.text as string;
    if (text !== undefined) {
      ctx.setChatInputValue(text);
      console.log('[WS] Chat input set:', text.substring(0, 50) + (text.length > 50 ? '...' : ''));
    }
  },
  
  'chat:clear_input': (_data, ctx) => {
    // Clear the chat input field
    ctx.setChatInputValue('');
    console.log('[WS] Chat input cleared');
  },
  
  'chat:send': (_data, ctx) => {
    // Send the current chat input (press Enter)
    ctx.submitChatInput();
    console.log('[WS] Chat input submitted');
  },
  
  'chat:respond': (data, ctx) => {
    // Auto-respond to a pending input request
    const response = data.response as string;
    if (response !== undefined) {
      ctx.respondToInputRequest(response);
      console.log('[WS] Auto-responded to input request:', response.substring(0, 50));
    }
  },
  
  'chat:select_option': (data, ctx) => {
    // Select an option from a pending select prompt (same as respond)
    const option = data.option as string;
    if (option !== undefined) {
      ctx.respondToInputRequest(option);
      console.log('[WS] Selected option:', option);
    }
  },
  
  'chat:scroll': (data, _ctx) => {
    // Scroll chat panel - UI-only concern, log for now
    const direction = data.direction as string;
    const amount = data.amount as number;
    console.log(`[WS] Chat scroll requested: ${direction} by ${amount}`);
    // Future: could emit custom event for ChatPanel to handle
  },
  
  // =========================================================================
  // Temporary Notification Handlers (from Hands.notify/status)
  // =========================================================================
  
  'chat:notification': (data, ctx) => {
    // Temporary notification that doesn't persist in chat history
    const content = data.content as string;
    const type = (data.type as ChatStatusType) || 'info';
    if (content) {
      ctx.showNotification(content, type);
      console.log(`[WS] Notification (${type}):`, content.substring(0, 50));
    }
  },
  
  'chat:status': (data, ctx) => {
    // Status indicator (thinking, executing, generating, etc.)
    const type = data.type as ChatStatusType;
    const message = data.message as string;
    if (type || message) {
      ctx.showNotification(message || `Status: ${type}`, type || 'info');
      console.log(`[WS] Status: ${type}`, message || '');
    }
  },
};

// =============================================================================
// Canvas Command Handlers
// =============================================================================

const canvasHandlers: Record<string, EventHandler> = {
  'canvas:command': (data, ctx) => {
    if (data.type) {
      ctx.addCanvasCommand(
        data.type as string,
        (data.params as Record<string, unknown>) || {}
      );
    }
  },
};

// =============================================================================
// Panel Handlers (from First Person / Hands)
// =============================================================================

/**
 * Normalize panel name to match PanelName type.
 * Handles variations like "detail_panel" -> "detail", "detailPanel" -> "detail"
 */
function normalizePanelName(panel: string): PanelName | null {
  const normalized = panel
    .toLowerCase()
    .replace(/_panel$/, '')
    .replace(/panel$/, '')
    .replace(/_/g, '');
  
  // Map common variations
  const mapping: Record<string, PanelName> = {
    'detail': 'detail',
    'details': 'detail',
    'log': 'log',
    'logs': 'log',
    'settings': 'settings',
    'setting': 'settings',
    'checkpoint': 'checkpoint',
    'checkpoints': 'checkpoint',
    'agent': 'agent',
    'agents': 'agent',
    'workers': 'workers',
    'worker': 'workers',
    'deployment': 'deployment',
    'deploy': 'deployment',
    'load': 'load',
    'chat': 'chat',
  };
  
  return mapping[normalized] || null;
}

const panelHandlers: Record<string, EventHandler> = {
  'panel:open': (data, ctx) => {
    const panel = normalizePanelName(data.panel as string);
    if (panel) {
      ctx.openPanel(panel);
    } else {
      console.warn('[WS] Unknown panel:', data.panel);
    }
  },
  
  'panel:close': (data, ctx) => {
    const panel = normalizePanelName(data.panel as string);
    if (panel) {
      ctx.closePanel(panel);
    } else {
      console.warn('[WS] Unknown panel:', data.panel);
    }
  },
  
  'panel:toggle': (data, ctx) => {
    const panel = normalizePanelName(data.panel as string);
    if (panel) {
      ctx.togglePanel(panel);
    } else {
      console.warn('[WS] Unknown panel:', data.panel);
    }
  },
  
  'panel:focus': (data, ctx) => {
    const panel = normalizePanelName(data.panel as string);
    if (panel) {
      ctx.focusPanel(panel);
    } else {
      console.warn('[WS] Unknown panel:', data.panel);
    }
  },
};

// =============================================================================
// Remote Execution Handlers
// =============================================================================

const remoteHandlers: Record<string, EventHandler> = {
  'remote:connected': (data, ctx) => {
    console.log('[Remote] Connected to remote run stream:', data.run_id);
    ctx.addLog({ 
      level: 'info', 
      flowIndex: '', 
      message: `Connected to remote run: ${data.plan_name || data.run_id}` 
    });
  },

  'remote:run_started': (data, ctx) => {
    console.log('[Remote] Run started:', data.run_id);
    ctx.setStatus('running');
    ctx.addLog({ level: 'info', flowIndex: '', message: `Remote run started: ${data.run_id}` });
  },

  'remote:execution:paused': (data, ctx) => {
    console.log('[Remote] Run paused:', data.run_id);
    ctx.setStatus('paused');
    ctx.addLog({ level: 'info', flowIndex: '', message: `[Remote] Run paused` });
  },

  'remote:execution:resumed': (data, ctx) => {
    console.log('[Remote] Run resumed:', data.run_id);
    ctx.setStatus('running');
    ctx.addLog({ level: 'info', flowIndex: '', message: `[Remote] Run resumed` });
  },

  'remote:execution:stepping': (data, ctx) => {
    console.log('[Remote] Run stepping:', data.run_id);
    ctx.setStatus('stepping');
    ctx.addLog({ level: 'info', flowIndex: '', message: `[Remote] Stepping...` });
  },

  'remote:execution:stopped': (data, ctx) => {
    console.log('[Remote] Run stopped:', data.run_id);
    ctx.setStatus('idle');
    ctx.addLog({ level: 'info', flowIndex: '', message: `[Remote] Run stopped` });
  },

  'remote:node_statuses': (data, ctx) => {
    if (data.statuses) {
      ctx.setNodeStatuses(data.statuses as Record<string, NodeStatus>);
    }
  },

  'remote:inference_started': (data, ctx) => {
    ctx.setCurrentInference(data.flow_index as string);
    ctx.setNodeStatus(data.flow_index as string, 'running');
    ctx.addLog({ 
      level: 'info', 
      flowIndex: data.flow_index as string, 
      message: `[Remote] Executing: ${data.concept_name || data.flow_index}` 
    });
  },

  'remote:inference_completed': (data, ctx) => {
    ctx.setNodeStatus(data.flow_index as string, 'completed');
    ctx.addLog({ 
      level: 'info', 
      flowIndex: data.flow_index as string, 
      message: `[Remote] Completed in ${(data.duration as number || 0).toFixed(2)}s` 
    });
  },

  'remote:inference_failed': (data, ctx) => {
    ctx.setNodeStatus(data.flow_index as string, 'failed');
    ctx.addLog({ 
      level: 'error', 
      flowIndex: data.flow_index as string, 
      message: `[Remote] Failed: ${data.error || data.status || 'Unknown error'}` 
    });
  },

  'remote:inference_error': (data, ctx) => {
    ctx.setNodeStatus(data.flow_index as string, 'failed');
    ctx.addLog({ 
      level: 'error', 
      flowIndex: data.flow_index as string, 
      message: `[Remote] Failed: ${data.error || data.status || 'Unknown error'}` 
    });
  },

  'remote:progress': (data, ctx) => {
    ctx.setProgress(
      data.completed_count as number,
      data.total_count as number,
      data.cycle_count as number
    );
  },

  'remote:cycle_started': (data, ctx) => {
    ctx.addLog({ level: 'info', flowIndex: '', message: `[Remote] Cycle ${data.cycle} started` });
  },

  'remote:cycle_completed': (data, ctx) => {
    ctx.addLog({ level: 'info', flowIndex: '', message: `[Remote] Cycle ${data.cycle} completed` });
  },

  'remote:run_completed': (_data, ctx) => {
    ctx.setStatus('completed');
    ctx.addLog({ level: 'info', flowIndex: '', message: `[Remote] Run completed successfully` });
  },

  'remote:run_failed': (data, ctx) => {
    ctx.setStatus('failed');
    ctx.addLog({ level: 'error', flowIndex: '', message: `[Remote] Run failed: ${data.error || 'Unknown error'}` });
  },

  'remote:error': (data, ctx) => {
    ctx.addLog({ level: 'error', flowIndex: '', message: `[Remote] Error: ${data.error || 'Unknown error'}` });
  },

  'remote:unbound': (_data, ctx) => {
    ctx.addLog({ level: 'info', flowIndex: '', message: `[Remote] Disconnected from remote run` });
  },
};

// =============================================================================
// Log Handler
// =============================================================================

const logHandlers: Record<string, EventHandler> = {
  'log:entry': (data, ctx) => {
    ctx.addLog({
      flowIndex: (data.flow_index as string) || '',
      level: (data.level as string) || 'info',
      message: (data.message as string) || '',
    });
  },
};

// =============================================================================
// Combined Handler Registry
// =============================================================================

const allHandlers: Record<string, EventHandler> = {
  ...executionHandlers,
  ...inferenceHandlers,
  ...breakpointHandlers,
  ...stepProgressHandlers,
  ...agentToolHandlers,
  ...modificationHandlers,
  ...userInputHandlers,
  ...chatHandlers,
  ...canvasHandlers,
  ...panelHandlers,
  ...remoteHandlers,
  ...logHandlers,
};

// =============================================================================
// Controller Event Handlers (filtered separately)
// =============================================================================

/**
 * Handle events from the chat controller (source: 'controller')
 * These update the chat store, not the main execution store
 */
function handleControllerExecutionEvent(
  type: string, 
  data: EventData, 
  updateControllerInfo: (info: Record<string, unknown>) => void
): boolean {
  switch (type) {
    case 'execution:started':
      updateControllerInfo({ status: 'running' });
      return true;
    case 'execution:paused':
      updateControllerInfo({ 
        status: 'paused', 
        current_flow_index: data.inference as string | undefined 
      });
      return true;
    case 'execution:resumed':
      updateControllerInfo({ status: 'running' });
      return true;
    case 'execution:completed':
    case 'execution:stopped':
      updateControllerInfo({ status: 'connected', current_flow_index: undefined });
      return true;
    case 'execution:error':
      updateControllerInfo({ status: 'error', error: data.error as string | undefined });
      return true;
    case 'execution:progress':
      if (data.current_inference) {
        updateControllerInfo({ current_flow_index: data.current_inference as string });
      }
      return true;
    default:
      return false;
  }
}

// =============================================================================
// Main Hook
// =============================================================================

export function useWebSocket() {
  // Execution store actions
  const setStatus = useExecutionStore((s) => s.setStatus);
  const setNodeStatus = useExecutionStore((s) => s.setNodeStatus);
  const setCurrentInference = useExecutionStore((s) => s.setCurrentInference);
  const setProgress = useExecutionStore((s) => s.setProgress);
  const addLog = useExecutionStore((s) => s.addLog);
  const addBreakpoint = useExecutionStore((s) => s.addBreakpoint);
  const removeBreakpoint = useExecutionStore((s) => s.removeBreakpoint);
  const setRunId = useExecutionStore((s) => s.setRunId);
  const setNodeStatuses = useExecutionStore((s) => s.setNodeStatuses);
  const reset = useExecutionStore((s) => s.reset);
  const setStepProgress = useExecutionStore((s) => s.setStepProgress);
  const updateStepProgress = useExecutionStore((s) => s.updateStepProgress);
  const clearStepProgress = useExecutionStore((s) => s.clearStepProgress);
  const fetchConceptStatuses = useExecutionStore((s) => s.fetchConceptStatuses);
  const setRunMode = useExecutionStore((s) => s.setRunMode);
  const addUserInputRequest = useExecutionStore((s) => s.addUserInputRequest);
  const removeUserInputRequest = useExecutionStore((s) => s.removeUserInputRequest);

  // Agent store actions
  const addToolCall = useAgentStore((s) => s.addToolCall);
  const updateToolCall = useAgentStore((s) => s.updateToolCall);
  const addAgent = useAgentStore((s) => s.addAgent);
  const updateAgent = useAgentStore((s) => s.updateAgent);
  const deleteAgent = useAgentStore((s) => s.deleteAgent);

  // Project store
  const activeProjectId = useProjectStore((s) => s.activeTabId);
  
  // Chat store actions
  const addMessageFromApi = useChatStore((s) => s.addMessageFromApi);
  const updateControllerInfo = useChatStore((s) => s.updateControllerInfo);
  const setInputRequest = useChatStore((s) => s.setInputRequest);
  const updateBufferStatus = useChatStore((s) => s.updateBufferStatus);
  const clearBuffer = useChatStore((s) => s.clearBuffer);
  
  // Chat action handlers (from First Person / Hands)
  const setChatInputValue = useChatStore((s) => s.setInputValue);
  const respondToInputRequest = useChatStore((s) => s.respondToInputRequest);
  // submitChatInput needs to be a function that gets the current value and submits
  const submitChatInput = useCallback(() => {
    const { inputValue, submitInput } = useChatStore.getState();
    if (inputValue.trim()) {
      submitInput(inputValue);
    }
  }, []);
  
  // Notification handlers (temporary status)
  const showNotification = useChatStore((s) => s.showNotification);
  const clearNotification = useChatStore((s) => s.clearNotification);
  
  // Canvas command store actions
  const addCanvasCommand = useCanvasCommandStore((s) => s.addCommand);
  
  // Panel store actions
  const openPanel = usePanelStore((s) => s.openPanel);
  const closePanel = usePanelStore((s) => s.closePanel);
  const togglePanel = usePanelStore((s) => s.togglePanel);
  const focusPanel = usePanelStore((s) => s.focusPanel);

  // Build handler context
  const ctx: EventHandlerContext = {
    setStatus,
    setNodeStatus,
    setNodeStatuses,
    setCurrentInference,
    setProgress,
    addLog,
    addBreakpoint,
    removeBreakpoint,
    setRunId,
    setStepProgress,
    updateStepProgress,
    clearStepProgress,
    fetchConceptStatuses,
    setRunMode,
    addUserInputRequest,
    removeUserInputRequest,
    addToolCall,
    updateToolCall,
    addAgent,
    updateAgent,
    deleteAgent,
    addMessageFromApi,
    updateControllerInfo,
    setInputRequest,
    updateBufferStatus,
    clearBuffer,
    addCanvasCommand,
    openPanel,
    closePanel,
    togglePanel,
    focusPanel,
    setChatInputValue,
    submitChatInput,
    respondToInputRequest,
    showNotification,
    clearNotification,
  };

  const handleEvent = useCallback(
    (event: WebSocketEvent) => {
      const { type, data } = event;
      
      // Check if this event is from the chat controller (not the main execution)
      const eventSource = data.source as string | undefined;
      const isControllerEvent = eventSource === 'controller';
      
      // Filter controller execution events - they should NOT update main execution store
      // But allow chat:* and canvas:* events through
      if (isControllerEvent) {
        if (type.startsWith('chat:') || type.startsWith('canvas:')) {
          // Let chat/canvas events fall through to main handler
        } else if (type.startsWith('execution:')) {
          // Handle controller execution events in chat store
          handleControllerExecutionEvent(type, data, updateControllerInfo);
          return;
        } else if (type === 'inference:started' && data.flow_index) {
          // Update current flow index for controller
          updateControllerInfo({ current_flow_index: data.flow_index as string });
          return;
        } else {
          // Other controller events - skip
          return;
        }
      }
      
      // Check if this event is for the active project
      const eventProjectId = data.project_id as string | undefined;
      if (eventProjectId && activeProjectId && eventProjectId !== activeProjectId) {
        console.debug(`[WS] Event for background project ${eventProjectId}: ${type}`);
        return;
      }

      // Handle connection event specially
      if (type === 'connection:established') {
        console.log('WebSocket connected:', data.message);
        return;
      }

      // Look up and execute the handler
      const handler = allHandlers[type];
      if (handler) {
        handler(data, ctx);
      } else {
        console.log('Unknown WebSocket event:', type, data);
      }
    },
    [
      activeProjectId,
      updateControllerInfo,
      // Note: ctx contains all the actions, but since it's rebuilt each render,
      // we need to include the individual actions in deps for proper memoization
      setStatus, setNodeStatus, setNodeStatuses, setCurrentInference, setProgress,
      addLog, addBreakpoint, removeBreakpoint, setRunId, setStepProgress,
      updateStepProgress, clearStepProgress, fetchConceptStatuses, setRunMode,
      addUserInputRequest, removeUserInputRequest, addToolCall, updateToolCall,
      addAgent, updateAgent, deleteAgent, addMessageFromApi, setInputRequest,
      updateBufferStatus, clearBuffer, addCanvasCommand, reset,
      openPanel, closePanel, togglePanel, focusPanel,
      setChatInputValue, submitChatInput, respondToInputRequest,
      showNotification, clearNotification
    ]
  );

  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Connect to WebSocket
    wsClient.connect();

    // Subscribe to events
    const unsubscribe = wsClient.subscribe((event) => {
      handleEvent(event);
      setIsConnected(true);
    });

    // Check connection state periodically
    const intervalId = setInterval(() => {
      setIsConnected(wsClient.isConnected);
    }, 1000);

    // Cleanup on unmount
    return () => {
      unsubscribe();
      clearInterval(intervalId);
      wsClient.disconnect();
    };
  }, [handleEvent]);

  return isConnected;
}
