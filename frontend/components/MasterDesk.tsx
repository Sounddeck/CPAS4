
/**
 * Master Desk - Mac-native desktop interface for CPAS
 * Mission Control style view for all agents and tasks
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Cpu, 
  Brain, 
  Search, 
  Shield, 
  Mic, 
  MicOff,
  Settings,
  Activity,
  Users,
  Database,
  Globe,
  Image,
  Lock,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  Info
} from 'lucide-react';

import { TufteSpark } from './charts/TufteSpark';
import { AgentCard } from './AgentCard';
import { OSINTPanel } from './OSINTPanel';
import { VoiceInterface } from './VoiceInterface';

interface Agent {
  id: string;
  name: string;
  type: string;
  status: 'active' | 'idle' | 'busy';
  performance: number[];
  currentTask?: string;
  capabilities: string[];
}

interface Task {
  id: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  assignedAgent?: string;
  priority: 'urgent' | 'high' | 'normal' | 'low';
  createdAt: string;
  completedAt?: string;
}

interface SystemMetrics {
  cpu: number[];
  memory: number[];
  tasks: number[];
  agents: number[];
}

export const MasterDesk: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [metrics, setMetrics] = useState<SystemMetrics>({
    cpu: [],
    memory: [],
    tasks: [],
    agents: []
  });
  const [selectedView, setSelectedView] = useState<'overview' | 'agents' | 'osint' | 'tasks'>('overview');
  const [voiceActive, setVoiceActive] = useState(false);
  const [masterAgentStatus, setMasterAgentStatus] = useState<any>(null);

  useEffect(() => {
    // Initialize data
    loadSystemData();
    
    // Set up real-time updates
    const interval = setInterval(loadSystemData, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadSystemData = async () => {
    try {
      // Load agents
      const agentsResponse = await fetch('/api/v1/agents');
      if (agentsResponse.ok) {
        const agentsData = await agentsResponse.json();
        setAgents(agentsData.agents || []);
      }

      // Load master agent status
      const masterResponse = await fetch('/api/v1/master-agent/status');
      if (masterResponse.ok) {
        const masterData = await masterResponse.json();
        setMasterAgentStatus(masterData.status);
      }

      // Load orchestration status
      const orchestrationResponse = await fetch('/api/v1/master-agent/orchestration-status');
      if (orchestrationResponse.ok) {
        const orchestrationData = await orchestrationResponse.json();
        const orchestration = orchestrationData.orchestration;
        
        // Update metrics
        setMetrics(prev => ({
          cpu: [...prev.cpu.slice(-19), Math.random() * 100],
          memory: [...prev.memory.slice(-19), Math.random() * 100],
          tasks: [...prev.tasks.slice(-19), orchestration.active_tasks || 0],
          agents: [...prev.agents.slice(-19), orchestration.registered_agents?.length || 0]
        }));
      }

    } catch (error) {
      console.error('Failed to load system data:', error);
    }
  };

  const handleVoiceToggle = () => {
    setVoiceActive(!voiceActive);
  };

  const handleTaskSubmit = async (description: string, priority: string = 'normal') => {
    try {
      const response = await fetch('/api/v1/master-agent/submit-task', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          description,
          priority,
          context: {}
        }),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Task submitted:', result.task_id);
        loadSystemData(); // Refresh data
      }
    } catch (error) {
      console.error('Failed to submit task:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {/* Mac-style Menu Bar */}
      <div className="h-8 bg-gray-200 dark:bg-gray-800 border-b border-gray-300 dark:border-gray-700 flex items-center px-4">
        <div className="flex space-x-2">
          <div className="w-3 h-3 rounded-full bg-red-500"></div>
          <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
          <div className="w-3 h-3 rounded-full bg-green-500"></div>
        </div>
        <div className="flex-1 text-center text-sm font-medium text-gray-700 dark:text-gray-300">
          CPAS Master Agent System
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={handleVoiceToggle}
            className={`p-1 rounded ${voiceActive ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-600'}`}
          >
            {voiceActive ? <Mic size={12} /> : <MicOff size={12} />}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-2rem)]">
        {/* Sidebar */}
        <div className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 p-4">
          <div className="mb-6">
            <h1 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
              Master Agent
            </h1>
            <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
              <div className="w-2 h-2 rounded-full bg-green-500"></div>
              <span>Greta - Active</span>
            </div>
          </div>

          {/* Navigation */}
          <nav className="space-y-2">
            {[
              { id: 'overview', label: 'Overview', icon: Activity },
              { id: 'agents', label: 'Agents', icon: Users },
              { id: 'osint', label: 'OSINT', icon: Shield },
              { id: 'tasks', label: 'Tasks', icon: CheckCircle }
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setSelectedView(id as any)}
                className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                  selectedView === id
                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                <Icon size={18} />
                <span>{label}</span>
              </button>
            ))}
          </nav>

          {/* System Metrics */}
          <div className="mt-8">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
              System Metrics
            </h3>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-xs text-gray-600 dark:text-gray-400 mb-1">
                  <span>CPU</span>
                  <span>{metrics.cpu[metrics.cpu.length - 1]?.toFixed(1)}%</span>
                </div>
                <TufteSpark data={metrics.cpu} height={20} color="#3B82F6" />
              </div>
              <div>
                <div className="flex justify-between text-xs text-gray-600 dark:text-gray-400 mb-1">
                  <span>Memory</span>
                  <span>{metrics.memory[metrics.memory.length - 1]?.toFixed(1)}%</span>
                </div>
                <TufteSpark data={metrics.memory} height={20} color="#10B981" />
              </div>
              <div>
                <div className="flex justify-between text-xs text-gray-600 dark:text-gray-400 mb-1">
                  <span>Active Tasks</span>
                  <span>{metrics.tasks[metrics.tasks.length - 1] || 0}</span>
                </div>
                <TufteSpark data={metrics.tasks} height={20} color="#F59E0B" />
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 p-6 overflow-auto">
          <AnimatePresence mode="wait">
            {selectedView === 'overview' && (
              <motion.div
                key="overview"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                <OverviewPanel 
                  masterAgentStatus={masterAgentStatus}
                  agents={agents}
                  tasks={tasks}
                  onTaskSubmit={handleTaskSubmit}
                />
              </motion.div>
            )}

            {selectedView === 'agents' && (
              <motion.div
                key="agents"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                <AgentsPanel agents={agents} />
              </motion.div>
            )}

            {selectedView === 'osint' && (
              <motion.div
                key="osint"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                <OSINTPanel />
              </motion.div>
            )}

            {selectedView === 'tasks' && (
              <motion.div
                key="tasks"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                <TasksPanel tasks={tasks} onTaskSubmit={handleTaskSubmit} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Voice Interface */}
      {voiceActive && (
        <VoiceInterface 
          onClose={() => setVoiceActive(false)}
          onTaskSubmit={handleTaskSubmit}
        />
      )}
    </div>
  );
};

// Overview Panel Component
const OverviewPanel: React.FC<{
  masterAgentStatus: any;
  agents: Agent[];
  tasks: Task[];
  onTaskSubmit: (description: string, priority?: string) => void;
}> = ({ masterAgentStatus, agents, tasks, onTaskSubmit }) => {
  const [quickTask, setQuickTask] = useState('');

  const handleQuickSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (quickTask.trim()) {
      onTaskSubmit(quickTask);
      setQuickTask('');
    }
  };

  return (
    <div className="space-y-6">
      {/* Master Agent Status */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Master Agent Status
          </h2>
          <div className="flex items-center space-x-2">
            <Brain className="text-blue-500" size={20} />
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {masterAgentStatus?.agent_name || 'Greta (Master Agent)'}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {masterAgentStatus?.performance_metrics?.tasks_completed || 0}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Tasks Completed</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              {((masterAgentStatus?.performance_metrics?.success_rate || 0) * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Success Rate</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
              {masterAgentStatus?.active_contexts || 0}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Active Contexts</div>
          </div>
        </div>
      </div>

      {/* Quick Task Input */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Quick Task
        </h3>
        <form onSubmit={handleQuickSubmit} className="flex space-x-3">
          <input
            type="text"
            value={quickTask}
            onChange={(e) => setQuickTask(e.target.value)}
            placeholder="Ask Greta anything..."
            className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
          />
          <button
            type="submit"
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Submit
          </button>
        </form>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Active Agents
          </h3>
          <div className="space-y-3">
            {agents.slice(0, 5).map((agent) => (
              <div key={agent.id} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`w-2 h-2 rounded-full ${
                    agent.status === 'active' ? 'bg-green-500' :
                    agent.status === 'busy' ? 'bg-yellow-500' : 'bg-gray-400'
                  }`}></div>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {agent.name}
                  </span>
                </div>
                <span className="text-xs text-gray-500 dark:text-gray-400 capitalize">
                  {agent.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Recent Tasks
          </h3>
          <div className="space-y-3">
            {tasks.slice(0, 5).map((task) => (
              <div key={task.id} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`w-2 h-2 rounded-full ${
                    task.status === 'completed' ? 'bg-green-500' :
                    task.status === 'in_progress' ? 'bg-blue-500' :
                    task.status === 'failed' ? 'bg-red-500' : 'bg-gray-400'
                  }`}></div>
                  <span className="text-sm text-gray-900 dark:text-white truncate max-w-48">
                    {task.description}
                  </span>
                </div>
                <span className="text-xs text-gray-500 dark:text-gray-400 capitalize">
                  {task.status.replace('_', ' ')}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Agents Panel Component
const AgentsPanel: React.FC<{ agents: Agent[] }> = ({ agents }) => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Agent Management
        </h2>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
          Create Agent
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents.map((agent) => (
          <AgentCard key={agent.id} agent={agent} />
        ))}
      </div>
    </div>
  );
};

// Tasks Panel Component
const TasksPanel: React.FC<{
  tasks: Task[];
  onTaskSubmit: (description: string, priority?: string) => void;
}> = ({ tasks, onTaskSubmit }) => {
  const [newTask, setNewTask] = useState('');
  const [priority, setPriority] = useState('normal');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (newTask.trim()) {
      onTaskSubmit(newTask, priority);
      setNewTask('');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Task Management
        </h2>
      </div>

      {/* New Task Form */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Create New Task
        </h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <textarea
              value={newTask}
              onChange={(e) => setNewTask(e.target.value)}
              placeholder="Describe the task..."
              rows={3}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            />
          </div>
          <div className="flex items-center space-x-4">
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            >
              <option value="low">Low Priority</option>
              <option value="normal">Normal Priority</option>
              <option value="high">High Priority</option>
              <option value="urgent">Urgent</option>
            </select>
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Create Task
            </button>
          </div>
        </form>
      </div>

      {/* Tasks List */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            All Tasks
          </h3>
        </div>
        <div className="divide-y divide-gray-200 dark:divide-gray-700">
          {tasks.map((task) => (
            <div key={task.id} className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <div className={`w-3 h-3 rounded-full ${
                      task.status === 'completed' ? 'bg-green-500' :
                      task.status === 'in_progress' ? 'bg-blue-500' :
                      task.status === 'failed' ? 'bg-red-500' : 'bg-gray-400'
                    }`}></div>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      task.priority === 'urgent' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                      task.priority === 'high' ? 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200' :
                      task.priority === 'normal' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                      'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                    }`}>
                      {task.priority}
                    </span>
                  </div>
                  <p className="text-gray-900 dark:text-white font-medium mb-1">
                    {task.description}
                  </p>
                  <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                    <span>Created: {new Date(task.createdAt).toLocaleString()}</span>
                    {task.assignedAgent && (
                      <span>Assigned to: {task.assignedAgent}</span>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  <span className={`px-3 py-1 text-sm rounded-full ${
                    task.status === 'completed' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                    task.status === 'in_progress' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                    task.status === 'failed' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                    'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                  }`}>
                    {task.status.replace('_', ' ')}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
