
/**
 * OSINT Intelligence Panel
 * Interface for Open Source Intelligence gathering operations
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Shield,
  Search,
  Globe,
  User,
  Image,
  Database,
  AlertTriangle,
  CheckCircle,
  Clock,
  Eye,
  MapPin,
  Mail,
  Phone,
  Calendar,
  ExternalLink,
  Download,
  Play,
  Pause
} from 'lucide-react';

import { TufteSpark, TufteSmallMultiples } from './charts/TufteSpark';

interface Investigation {
  id: string;
  type: string;
  target: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  confidence_score: number;
  results: any;
  timestamp: string;
}

interface OSINTModule {
  name: string;
  description: string;
  capabilities: string[];
  status: 'active' | 'inactive';
}

export const OSINTPanel: React.FC = () => {
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [modules, setModules] = useState<OSINTModule[]>([]);
  const [selectedTab, setSelectedTab] = useState<'investigate' | 'results' | 'modules'>('investigate');
  const [investigationForm, setInvestigationForm] = useState({
    target: '',
    type: 'comprehensive',
    includeVoice: false
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadOSINTData();
  }, []);

  const loadOSINTData = async () => {
    try {
      // Load OSINT modules
      const modulesResponse = await fetch('/api/v1/osint/modules');
      if (modulesResponse.ok) {
        const modulesData = await modulesResponse.json();
        setModules(Object.entries(modulesData.modules).map(([key, module]: [string, any]) => ({
          name: module.name,
          description: module.description,
          capabilities: module.capabilities,
          status: 'active'
        })));
      }

      // Load OSINT status
      const statusResponse = await fetch('/api/v1/osint/status');
      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        // Update with any active investigations
      }
    } catch (error) {
      console.error('Failed to load OSINT data:', error);
    }
  };

  const handleInvestigation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!investigationForm.target.trim()) return;

    setLoading(true);
    try {
      const endpoint = investigationForm.type === 'person' ? '/api/v1/osint/investigate/person' :
                     investigationForm.type === 'domain' ? '/api/v1/osint/investigate/domain' :
                     investigationForm.type === 'image' ? '/api/v1/osint/investigate/image' :
                     '/api/v1/osint/investigate';

      const payload = investigationForm.type === 'person' ? 
        { identifier: investigationForm.target, include_voice: investigationForm.includeVoice } :
        investigationForm.type === 'domain' ?
        { domain: investigationForm.target, include_voice: investigationForm.includeVoice } :
        investigationForm.type === 'image' ?
        { image_source: investigationForm.target, include_voice: investigationForm.includeVoice } :
        { target: investigationForm.target, investigation_type: investigationForm.type, include_voice: investigationForm.includeVoice };

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setInvestigations(prev => [result, ...prev]);
          setInvestigationForm({ target: '', type: 'comprehensive', includeVoice: false });
          setSelectedTab('results');
        }
      }
    } catch (error) {
      console.error('Investigation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Shield className="text-red-600" size={28} />
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              OSINT Intelligence
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Open Source Intelligence Gathering
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-green-500"></div>
          <span className="text-sm text-gray-600 dark:text-gray-400">
            All modules operational
          </span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="flex space-x-8">
          {[
            { id: 'investigate', label: 'Investigate', icon: Search },
            { id: 'results', label: 'Results', icon: Database },
            { id: 'modules', label: 'Modules', icon: Shield }
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setSelectedTab(id as any)}
              className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                selectedTab === id
                  ? 'border-red-500 text-red-600 dark:text-red-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              <Icon size={16} />
              <span>{label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        {selectedTab === 'investigate' && (
          <motion.div
            key="investigate"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <InvestigateTab
              form={investigationForm}
              setForm={setInvestigationForm}
              onSubmit={handleInvestigation}
              loading={loading}
            />
          </motion.div>
        )}

        {selectedTab === 'results' && (
          <motion.div
            key="results"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <ResultsTab investigations={investigations} />
          </motion.div>
        )}

        {selectedTab === 'modules' && (
          <motion.div
            key="modules"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <ModulesTab modules={modules} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// Investigate Tab Component
const InvestigateTab: React.FC<{
  form: any;
  setForm: (form: any) => void;
  onSubmit: (e: React.FormEvent) => void;
  loading: boolean;
}> = ({ form, setForm, onSubmit, loading }) => {
  return (
    <div className="space-y-6">
      {/* Investigation Form */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Start New Investigation
        </h3>
        
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Target
            </label>
            <input
              type="text"
              value={form.target}
              onChange={(e) => setForm({ ...form, target: e.target.value })}
              placeholder="Enter username, email, domain, or image URL..."
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              disabled={loading}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Investigation Type
            </label>
            <select
              value={form.type}
              onChange={(e) => setForm({ ...form, type: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              disabled={loading}
            >
              <option value="comprehensive">Comprehensive Investigation</option>
              <option value="person">Person Investigation</option>
              <option value="domain">Domain Investigation</option>
              <option value="image">Image Investigation</option>
              <option value="social">Social Media Only</option>
              <option value="technical">Technical Only</option>
              <option value="breach">Breach Data Only</option>
            </select>
          </div>

          <div className="flex items-center space-x-3">
            <input
              type="checkbox"
              id="includeVoice"
              checked={form.includeVoice}
              onChange={(e) => setForm({ ...form, includeVoice: e.target.checked })}
              className="w-4 h-4 text-red-600 bg-gray-100 border-gray-300 rounded focus:ring-red-500 dark:focus:ring-red-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
              disabled={loading}
            />
            <label htmlFor="includeVoice" className="text-sm text-gray-700 dark:text-gray-300">
              Include voice response from Greta
            </label>
          </div>

          <button
            type="submit"
            disabled={loading || !form.target.trim()}
            className="w-full px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Investigating...</span>
              </>
            ) : (
              <>
                <Search size={16} />
                <span>Start Investigation</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { type: 'person', icon: User, label: 'Person Lookup', description: 'Social media, breaches, digital footprint' },
          { type: 'domain', icon: Globe, label: 'Domain Analysis', description: 'DNS, SSL, subdomains, reputation' },
          { type: 'image', icon: Image, label: 'Image Investigation', description: 'Reverse search, metadata, forensics' },
          { type: 'breach', icon: AlertTriangle, label: 'Breach Check', description: 'Data breaches, credential exposure' }
        ].map(({ type, icon: Icon, label, description }) => (
          <button
            key={type}
            onClick={() => setForm({ ...form, type })}
            className={`p-4 rounded-lg border-2 transition-all text-left ${
              form.type === type
                ? 'border-red-500 bg-red-50 dark:bg-red-900/20'
                : 'border-gray-200 dark:border-gray-700 hover:border-red-300 dark:hover:border-red-600'
            }`}
          >
            <Icon className={`mb-2 ${form.type === type ? 'text-red-600' : 'text-gray-400'}`} size={20} />
            <h4 className="font-medium text-gray-900 dark:text-white text-sm">{label}</h4>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">{description}</p>
          </button>
        ))}
      </div>
    </div>
  );
};

// Results Tab Component
const ResultsTab: React.FC<{ investigations: Investigation[] }> = ({ investigations }) => {
  const [selectedInvestigation, setSelectedInvestigation] = useState<Investigation | null>(null);

  return (
    <div className="space-y-6">
      {investigations.length === 0 ? (
        <div className="text-center py-12">
          <Database className="mx-auto text-gray-400 mb-4" size={48} />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No investigations yet
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            Start your first OSINT investigation to see results here.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Investigations List */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Recent Investigations
            </h3>
            {investigations.map((investigation) => (
              <div
                key={investigation.id}
                onClick={() => setSelectedInvestigation(investigation)}
                className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700 cursor-pointer hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <div className={`w-2 h-2 rounded-full ${
                      investigation.status === 'completed' ? 'bg-green-500' :
                      investigation.status === 'in_progress' ? 'bg-blue-500' :
                      investigation.status === 'failed' ? 'bg-red-500' : 'bg-gray-400'
                    }`}></div>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {investigation.target}
                    </span>
                  </div>
                  <span className="text-xs text-gray-500 dark:text-gray-400 capitalize">
                    {investigation.type}
                  </span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {new Date(investigation.timestamp).toLocaleString()}
                  </span>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-gray-500">Confidence:</span>
                    <div className="w-16 h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                      <div
                        className="h-2 bg-green-500 rounded-full"
                        style={{ width: `${investigation.confidence_score * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-xs text-gray-600 dark:text-gray-400">
                      {(investigation.confidence_score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Investigation Details */}
          <div>
            {selectedInvestigation ? (
              <InvestigationDetails investigation={selectedInvestigation} />
            ) : (
              <div className="bg-white dark:bg-gray-800 rounded-lg p-8 shadow-sm border border-gray-200 dark:border-gray-700 text-center">
                <Eye className="mx-auto text-gray-400 mb-4" size={48} />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  Select an Investigation
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Click on an investigation to view detailed results.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// Investigation Details Component
const InvestigationDetails: React.FC<{ investigation: Investigation }> = ({ investigation }) => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Investigation Results
          </h3>
          <button className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
            <Download size={16} />
          </button>
        </div>
        <div className="mt-2 flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
          <span>Target: {investigation.target}</span>
          <span>Type: {investigation.type}</span>
          <span>Confidence: {(investigation.confidence_score * 100).toFixed(0)}%</span>
        </div>
      </div>

      <div className="p-6 space-y-4 max-h-96 overflow-y-auto">
        {Object.entries(investigation.results || {}).map(([module, result]: [string, any]) => (
          <div key={module} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-gray-900 dark:text-white capitalize">
                {module} Intelligence
              </h4>
              <div className={`px-2 py-1 text-xs rounded-full ${
                result?.success ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
              }`}>
                {result?.success ? 'Success' : 'Failed'}
              </div>
            </div>
            
            {result?.success && (
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {module === 'social' && result.profiles_found && (
                  <p>Found {result.profiles_found} social media profiles</p>
                )}
                {module === 'technical' && result.domain_info && (
                  <p>Technical analysis completed</p>
                )}
                {module === 'breach' && result.breach_count !== undefined && (
                  <p>Found {result.breach_count} data breaches</p>
                )}
                {module === 'media' && result.total_results !== undefined && (
                  <p>Found {result.total_results} similar images</p>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

// Modules Tab Component
const ModulesTab: React.FC<{ modules: OSINTModule[] }> = ({ modules }) => {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {modules.map((module, index) => (
          <div
            key={index}
            className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                {module.name}
              </h3>
              <div className={`px-3 py-1 text-xs rounded-full ${
                module.status === 'active' 
                  ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                  : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
              }`}>
                {module.status}
              </div>
            </div>
            
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              {module.description}
            </p>
            
            <div>
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                Capabilities
              </h4>
              <div className="flex flex-wrap gap-2">
                {module.capabilities.map((capability, capIndex) => (
                  <span
                    key={capIndex}
                    className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded"
                  >
                    {capability.replace('_', ' ')}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
