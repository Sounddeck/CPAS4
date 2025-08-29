
/**
 * Agent Card Component
 * Displays individual agent information and controls
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Bot,
  Brain,
  Search,
  Palette,
  Code,
  Calendar,
  Activity,
  Settings,
  Play,
  Pause,
  MoreVertical,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

import { TufteSpark } from './charts/TufteSpark';

interface Agent {
  id: string;
  name: string;
  type: string;
  status: 'active' | 'idle' | 'busy';
  performance: number[];
  currentTask?: string;
  capabilities: string[];
  tasksCompleted?: number;
  successRate?: number;
  averageResponseTime?: number;
  lastActivity?: string;
}

interface AgentCardProps {
  agent: Agent;
  onStart?: (agentId: string) => void;
  onStop?: (agentId: string) => void;
  onConfigure?: (agentId: string) => void;
  onViewDetails?: (agentId: string) => void;
}

const getAgentIcon = (type: string) => {
  switch (type.toLowerCase()) {
    case 'master':
    case 'master_agent':
      return Brain;
    case 'research':
    case 'research_agent':
      return Search;
    case 'creative':
    case 'creative_agent':
      return Palette;
    case 'technical':
    case 'technical_agent':
      return Code;
    case 'personal':
    case 'personal_assistant':
      return Calendar;
    default:
      return Bot;
  }
};

const getAgentColor = (type: string) => {
  switch (type.toLowerCase()) {
    case 'master':
    case 'master_agent':
      return 'blue';
    case 'research':
    case 'research_agent':
      return 'green';
    case 'creative':
    case 'creative_agent':
      return 'purple';
    case 'technical':
    case 'technical_agent':
      return 'orange';
    case 'personal':
    case 'personal_assistant':
      return 'pink';
    default:
      return 'gray';
  }
};

export const AgentCard: React.FC<AgentCardProps> = ({
  agent,
  onStart,
  onStop,
  onConfigure,
  onViewDetails
}) => {
  const [showMenu, setShowMenu] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const Icon = getAgentIcon(agent.type);
  const color = getAgentColor(agent.type);

  const colorClasses = {
    blue: {
      bg: 'bg-blue-50 dark:bg-blue-900/20',
      border: 'border-blue-200 dark:border-blue-800',
      icon: 'text-blue-600 dark:text-blue-400',
      accent: 'bg-blue-600',
      text: 'text-blue-700 dark:text-blue-300'
    },
    green: {
      bg: 'bg-green-50 dark:bg-green-900/20',
      border: 'border-green-200 dark:border-green-800',
      icon: 'text-green-600 dark:text-green-400',
      accent: 'bg-green-600',
      text: 'text-green-700 dark:text-green-300'
    },
    purple: {
      bg: 'bg-purple-50 dark:bg-purple-900/20',
      border: 'border-purple-200 dark:border-purple-800',
      icon: 'text-purple-600 dark:text-purple-400',
      accent: 'bg-purple-600',
      text: 'text-purple-700 dark:text-purple-300'
    },
    orange: {
      bg: 'bg-orange-50 dark:bg-orange-900/20',
      border: 'border-orange-200 dark:border-orange-800',
      icon: 'text-orange-600 dark:text-orange-400',
      accent: 'bg-orange-600',
      text: 'text-orange-700 dark:text-orange-300'
    },
    pink: {
      bg: 'bg-pink-50 dark:bg-pink-900/20',
      border: 'border-pink-200 dark:border-pink-800',
      icon: 'text-pink-600 dark:text-pink-400',
      accent: 'bg-pink-600',
      text: 'text-pink-700 dark:text-pink-300'
    },
    gray: {
      bg: 'bg-gray-50 dark:bg-gray-800',
      border: 'border-gray-200 dark:border-gray-700',
      icon: 'text-gray-600 dark:text-gray-400',
      accent: 'bg-gray-600',
      text: 'text-gray-700 dark:text-gray-300'
    }
  };

  const classes = colorClasses[color as keyof typeof colorClasses];

  return (
    <motion.div
      layout
      className={`${classes.bg} ${classes.border} border rounded-xl p-6 shadow-sm hover:shadow-md transition-all duration-200 relative`}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-lg ${classes.accent} bg-opacity-10`}>
            <Icon className={classes.icon} size={20} />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white">
              {agent.name}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 capitalize">
              {agent.type.replace('_', ' ')}
            </p>
          </div>
        </div>

        {/* Status and Menu */}
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${
            agent.status === 'active' ? 'bg-green-500' :
            agent.status === 'busy' ? 'bg-yellow-500' : 'bg-gray-400'
          }`}></div>
          
          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
            >
              <MoreVertical size={16} className="text-gray-400" />
            </button>

            {showMenu && (
              <div className="absolute right-0 top-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-10 min-w-32">
                {agent.status === 'active' ? (
                  <button
                    onClick={() => {
                      onStop?.(agent.id);
                      setShowMenu(false);
                    }}
                    className="w-full px-3 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-2"
                  >
                    <Pause size={14} />
                    <span>Stop</span>
                  </button>
                ) : (
                  <button
                    onClick={() => {
                      onStart?.(agent.id);
                      setShowMenu(false);
                    }}
                    className="w-full px-3 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-2"
                  >
                    <Play size={14} />
                    <span>Start</span>
                  </button>
                )}
                
                <button
                  onClick={() => {
                    onConfigure?.(agent.id);
                    setShowMenu(false);
                  }}
                  className="w-full px-3 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-2"
                >
                  <Settings size={14} />
                  <span>Configure</span>
                </button>
                
                <button
                  onClick={() => {
                    onViewDetails?.(agent.id);
                    setShowMenu(false);
                  }}
                  className="w-full px-3 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-2"
                >
                  <Activity size={14} />
                  <span>Details</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Current Task */}
      {agent.currentTask && (
        <div className="mb-4 p-3 bg-white dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
          <div className="flex items-center space-x-2 mb-1">
            <Clock size={14} className="text-blue-500" />
            <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
              Current Task
            </span>
          </div>
          <p className="text-sm text-gray-900 dark:text-white">
            {agent.currentTask}
          </p>
        </div>
      )}

      {/* Performance Metrics */}
      <div className="space-y-3 mb-4">
        {/* Performance Chart */}
        {agent.performance && agent.performance.length > 0 && (
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
                Performance
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-500">
                {agent.performance[agent.performance.length - 1]?.toFixed(1)}%
              </span>
            </div>
            <TufteSpark
              data={agent.performance}
              height={30}
              color={classes.accent.replace('bg-', '#')}
              showLast={true}
            />
          </div>
        )}

        {/* Key Metrics */}
        <div className="grid grid-cols-3 gap-3 text-center">
          <div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {agent.tasksCompleted || 0}
            </div>
            <div className="text-xs text-gray-600 dark:text-gray-400">Tasks</div>
          </div>
          <div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {agent.successRate ? `${(agent.successRate * 100).toFixed(0)}%` : '0%'}
            </div>
            <div className="text-xs text-gray-600 dark:text-gray-400">Success</div>
          </div>
          <div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {agent.averageResponseTime ? `${agent.averageResponseTime.toFixed(1)}s` : '0s'}
            </div>
            <div className="text-xs text-gray-600 dark:text-gray-400">Avg Time</div>
          </div>
        </div>
      </div>

      {/* Capabilities */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
            Capabilities
          </span>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
          >
            {isExpanded ? 'Less' : 'More'}
          </button>
        </div>
        
        <div className="flex flex-wrap gap-1">
          {(isExpanded ? agent.capabilities : agent.capabilities.slice(0, 3)).map((capability, index) => (
            <span
              key={index}
              className={`px-2 py-1 text-xs rounded ${classes.text} bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600`}
            >
              {capability.replace('_', ' ')}
            </span>
          ))}
          {!isExpanded && agent.capabilities.length > 3 && (
            <span className="px-2 py-1 text-xs text-gray-500 dark:text-gray-400">
              +{agent.capabilities.length - 3} more
            </span>
          )}
        </div>
      </div>

      {/* Last Activity */}
      {agent.lastActivity && (
        <div className="text-xs text-gray-500 dark:text-gray-400 flex items-center space-x-1">
          <Clock size={12} />
          <span>Last active: {agent.lastActivity}</span>
        </div>
      )}

      {/* Status Indicator */}
      <div className="absolute top-2 right-2">
        {agent.status === 'active' && (
          <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
        )}
        {agent.status === 'busy' && (
          <div className="w-3 h-3 bg-yellow-500 rounded-full animate-pulse"></div>
        )}
      </div>
    </motion.div>
  );
};

// Agent Grid Component for displaying multiple agents
export const AgentGrid: React.FC<{
  agents: Agent[];
  onAgentAction?: (action: string, agentId: string) => void;
}> = ({ agents, onAgentAction }) => {
  const handleAgentAction = (action: string, agentId: string) => {
    onAgentAction?.(action, agentId);
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {agents.map((agent) => (
        <AgentCard
          key={agent.id}
          agent={agent}
          onStart={(id) => handleAgentAction('start', id)}
          onStop={(id) => handleAgentAction('stop', id)}
          onConfigure={(id) => handleAgentAction('configure', id)}
          onViewDetails={(id) => handleAgentAction('view_details', id)}
        />
      ))}
    </div>
  );
};

// Agent Performance Summary Component
export const AgentPerformanceSummary: React.FC<{ agents: Agent[] }> = ({ agents }) => {
  const totalTasks = agents.reduce((sum, agent) => sum + (agent.tasksCompleted || 0), 0);
  const averageSuccessRate = agents.reduce((sum, agent) => sum + (agent.successRate || 0), 0) / agents.length;
  const activeAgents = agents.filter(agent => agent.status === 'active').length;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Agent Performance Summary
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
            {agents.length}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Total Agents</div>
        </div>
        
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600 dark:text-green-400">
            {activeAgents}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Active</div>
        </div>
        
        <div className="text-center">
          <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
            {totalTasks}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Tasks Completed</div>
        </div>
        
        <div className="text-center">
          <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
            {(averageSuccessRate * 100).toFixed(0)}%
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Avg Success Rate</div>
        </div>
      </div>
    </div>
  );
};
