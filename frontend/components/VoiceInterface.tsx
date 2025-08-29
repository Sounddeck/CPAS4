
/**
 * Voice Interface Component
 * German-accented voice interaction with Greta
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Send,
  X,
  Settings,
  Play,
  Pause,
  RotateCcw
} from 'lucide-react';

interface VoiceInterfaceProps {
  onClose: () => void;
  onTaskSubmit: (description: string, priority?: string) => void;
}

interface VoiceSettings {
  rate: number;
  volume: number;
  personality_traits: string[];
}

export const VoiceInterface: React.FC<VoiceInterfaceProps> = ({
  onClose,
  onTaskSubmit
}) => {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [voiceSettings, setVoiceSettings] = useState<VoiceSettings>({
    rate: 180,
    volume: 0.8,
    personality_traits: ['precise', 'analytical', 'warm', 'intelligent']
  });

  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      if (recognitionRef.current) {
        recognitionRef.current.continuous = true;
        recognitionRef.current.interimResults = true;
        recognitionRef.current.lang = 'en-US';

        recognitionRef.current.onresult = (event) => {
          let finalTranscript = '';
          let interimTranscript = '';

          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              finalTranscript += transcript;
            } else {
              interimTranscript += transcript;
            }
          }

          setTranscript(finalTranscript || interimTranscript);
        };

        recognitionRef.current.onend = () => {
          setIsListening(false);
        };

        recognitionRef.current.onerror = (event) => {
          console.error('Speech recognition error:', event.error);
          setIsListening(false);
        };
      }
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      setTranscript('');
      setResponse('');
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  const handleSubmit = async (text: string = transcript) => {
    if (!text.trim()) return;

    try {
      // Submit to Master Agent
      const response = await fetch('/api/v1/master-agent/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          input: text,
          context: { voice_interface: true },
          priority: 'normal'
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setResponse(result.response);

        // Generate voice response
        await generateVoiceResponse(result);

        // If it's a task, submit it
        if (text.toLowerCase().includes('task') || text.toLowerCase().includes('do')) {
          onTaskSubmit(text);
        }
      }
    } catch (error) {
      console.error('Failed to process voice input:', error);
      setResponse('Entschuldigung, I encountered an error processing your request.');
    }
  };

  const generateVoiceResponse = async (responseData: any) => {
    try {
      const voiceResponse = await fetch('/api/v1/osint/voice/speak', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: responseData.response,
          context: responseData.reasoning_level || 'general',
          include_accent: true
        }),
      });

      if (voiceResponse.ok) {
        const voiceResult = await voiceResponse.json();
        if (voiceResult.success && voiceResult.audio_file) {
          setAudioUrl(voiceResult.audio_file);
          playAudio(voiceResult.audio_file);
        }
      }
    } catch (error) {
      console.error('Failed to generate voice response:', error);
    }
  };

  const playAudio = (url: string) => {
    if (audioRef.current) {
      audioRef.current.src = url;
      audioRef.current.play();
      setIsSpeaking(true);
    }
  };

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsSpeaking(false);
    }
  };

  const updateVoiceSettings = async (newSettings: Partial<VoiceSettings>) => {
    try {
      const response = await fetch('/api/v1/osint/voice/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newSettings),
      });

      if (response.ok) {
        setVoiceSettings(prev => ({ ...prev, ...newSettings }));
      }
    } catch (error) {
      console.error('Failed to update voice settings:', error);
    }
  };

  const testVoice = async () => {
    try {
      const response = await fetch('/api/v1/osint/voice/test', {
        method: 'POST',
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success && result.voice_test.audio_file) {
          playAudio(result.voice_test.audio_file);
        }
      }
    } catch (error) {
      console.error('Voice test failed:', error);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-white dark:bg-gray-800 rounded-2xl p-6 w-full max-w-md mx-4 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <span className="text-white font-semibold text-sm">G</span>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Greta
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Master Agent Voice Interface
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <Settings size={16} />
            </button>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <X size={16} />
            </button>
          </div>
        </div>

        {/* Settings Panel */}
        <AnimatePresence>
          {showSettings && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg overflow-hidden"
            >
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
                Voice Settings
              </h4>
              
              <div className="space-y-3">
                <div>
                  <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
                    Speaking Rate: {voiceSettings.rate} WPM
                  </label>
                  <input
                    type="range"
                    min="120"
                    max="250"
                    value={voiceSettings.rate}
                    onChange={(e) => updateVoiceSettings({ rate: parseInt(e.target.value) })}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-600"
                  />
                </div>
                
                <div>
                  <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
                    Volume: {Math.round(voiceSettings.volume * 100)}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={voiceSettings.volume}
                    onChange={(e) => updateVoiceSettings({ volume: parseFloat(e.target.value) })}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-600"
                  />
                </div>
                
                <button
                  onClick={testVoice}
                  className="w-full px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                >
                  Test Voice
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Voice Visualization */}
        <div className="mb-6 text-center">
          <div className={`w-24 h-24 mx-auto rounded-full flex items-center justify-center transition-all duration-300 ${
            isListening ? 'bg-red-100 dark:bg-red-900/30 animate-pulse' :
            isSpeaking ? 'bg-blue-100 dark:bg-blue-900/30 animate-pulse' :
            'bg-gray-100 dark:bg-gray-700'
          }`}>
            {isListening ? (
              <Mic className="text-red-600 dark:text-red-400" size={32} />
            ) : isSpeaking ? (
              <Volume2 className="text-blue-600 dark:text-blue-400" size={32} />
            ) : (
              <MicOff className="text-gray-400" size={32} />
            )}
          </div>
          
          <div className="mt-3">
            {isListening && (
              <div className="flex justify-center space-x-1">
                {[...Array(5)].map((_, i) => (
                  <div
                    key={i}
                    className="w-1 bg-red-500 rounded-full animate-pulse"
                    style={{
                      height: `${Math.random() * 20 + 10}px`,
                      animationDelay: `${i * 0.1}s`
                    }}
                  />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Transcript */}
        {transcript && (
          <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">You said:</div>
            <div className="text-sm text-gray-900 dark:text-white">{transcript}</div>
          </div>
        )}

        {/* Response */}
        {response && (
          <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/30 rounded-lg">
            <div className="text-xs text-blue-600 dark:text-blue-400 mb-1">Greta responds:</div>
            <div className="text-sm text-gray-900 dark:text-white">{response}</div>
          </div>
        )}

        {/* Controls */}
        <div className="flex items-center justify-center space-x-4">
          {!isListening ? (
            <button
              onClick={startListening}
              className="px-6 py-3 bg-red-600 text-white rounded-full hover:bg-red-700 transition-colors flex items-center space-x-2"
            >
              <Mic size={20} />
              <span>Start Listening</span>
            </button>
          ) : (
            <button
              onClick={stopListening}
              className="px-6 py-3 bg-gray-600 text-white rounded-full hover:bg-gray-700 transition-colors flex items-center space-x-2"
            >
              <MicOff size={20} />
              <span>Stop Listening</span>
            </button>
          )}

          {transcript && (
            <button
              onClick={() => handleSubmit()}
              className="px-4 py-3 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors"
            >
              <Send size={20} />
            </button>
          )}

          {isSpeaking && (
            <button
              onClick={stopAudio}
              className="px-4 py-3 bg-orange-600 text-white rounded-full hover:bg-orange-700 transition-colors"
            >
              <VolumeX size={20} />
            </button>
          )}
        </div>

        {/* Manual Input */}
        <div className="mt-4">
          <div className="flex space-x-2">
            <input
              type="text"
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              placeholder="Or type your message here..."
              className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white text-sm"
              onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
            />
            <button
              onClick={() => handleSubmit()}
              disabled={!transcript.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send size={16} />
            </button>
          </div>
        </div>

        {/* Audio Element */}
        <audio
          ref={audioRef}
          onEnded={() => setIsSpeaking(false)}
          onError={() => setIsSpeaking(false)}
          style={{ display: 'none' }}
        />

        {/* Status */}
        <div className="mt-4 text-center">
          <div className="text-xs text-gray-500 dark:text-gray-400">
            {isListening ? 'Listening...' :
             isSpeaking ? 'Greta is speaking...' :
             'Ready to assist you'}
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

// Voice Status Indicator Component
export const VoiceStatusIndicator: React.FC<{
  isActive: boolean;
  isListening: boolean;
  isSpeaking: boolean;
}> = ({ isActive, isListening, isSpeaking }) => {
  return (
    <div className="flex items-center space-x-2">
      <div className={`w-2 h-2 rounded-full ${
        !isActive ? 'bg-gray-400' :
        isListening ? 'bg-red-500 animate-pulse' :
        isSpeaking ? 'bg-blue-500 animate-pulse' :
        'bg-green-500'
      }`}></div>
      <span className="text-xs text-gray-600 dark:text-gray-400">
        {!isActive ? 'Voice Inactive' :
         isListening ? 'Listening' :
         isSpeaking ? 'Speaking' :
         'Voice Ready'}
      </span>
    </div>
  );
};

// Declare global interfaces for speech recognition
declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}
