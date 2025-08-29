
# Voice Activation & Wake-Word Customization Guide

## Overview

Greta supports advanced voice activation features including:
- Customizable wake words
- Continuous or on-demand listening
- Multiple voice engines
- Personality-based speech patterns
- Multi-language support

## Quick Setup

### Enable Voice Activation

1. **Open Configuration File**:
   ```bash
   nano ~/Applications/CPAS/cpas-master-agent-main/config/greta_config.yaml
   ```

2. **Enable Voice Features**:
   ```yaml
   voice:
     wake_word_enabled: true
     wake_word: "Greta"
     continuous_listening: false
     voice_feedback: true
   ```

3. **Save and Restart**: `Ctrl+X`, `Y`, `Enter`, then restart Greta

### Grant Microphone Permissions

macOS will prompt for microphone access. If you need to enable it manually:

1. System Preferences → Security & Privacy → Privacy
2. Select "Microphone" from the left sidebar
3. Check the box next to "Greta" or your Terminal application

## Advanced Configuration

### Custom Wake Words

You can set multiple wake words for flexibility:

```yaml
voice:
  wake_word: "Greta"              # Primary wake word
  wake_word_enabled: true
  
# Alternative wake words
wake_words:
  - "Hey Greta"
  - "Computer"
  - "Assistant"
  - "AI Helper"
  - "Jarvis"                      # Popular choice!
```

### Voice Engine Options

Choose from different text-to-speech engines:

```yaml
voice:
  tts_engine: "piper"             # Options: piper, system, openai
  voice_speed: 1.0                # 0.5 - 2.0 (speech rate)
  voice_volume: 0.8               # 0.0 - 1.0 (volume level)
  voice_accent: "german"          # german, british, american, australian
```

### Listening Modes

Configure how Greta listens for commands:

```yaml
voice:
  continuous_listening: false     # Always listening vs. wake-word activation
  listen_timeout: 30             # Seconds to listen after wake word
  silence_threshold: 0.5         # Sensitivity to background noise
  phrase_timeout: 5              # Max seconds for a single phrase
```

## Personality-Based Voice Settings

### German Accent (Default)

```yaml
agent:
  name: "Greta"
  personality: "professional"
  voice_accent: "german"
  
voice:
  tts_engine: "piper"
  voice_speed: 0.9               # Slightly slower for accent clarity
  response_style: "detailed"
```

### Friendly Assistant

```yaml
agent:
  name: "Alex"
  personality: "friendly"
  voice_accent: "american"
  
voice:
  tts_engine: "system"
  voice_speed: 1.1               # Slightly faster, more energetic
  response_style: "conversational"
```

### Formal Butler

```yaml
agent:
  name: "Jeeves"
  personality: "formal"
  voice_accent: "british"
  
voice:
  tts_engine: "openai"           # Requires OpenAI API key
  voice_speed: 0.8               # Measured, deliberate pace
  response_style: "brief"
```

## Voice Commands

### Basic Commands

Once voice activation is enabled, try these commands:

**Wake Up**:
- "Greta" (or your custom wake word)
- "Hey Greta, are you there?"

**Information Queries**:
- "What time is it?"
- "What's the weather like?"
- "Tell me about [topic]"

**OSINT Operations**:
- "Search for information about [company/person]"
- "Analyze this domain: example.com"
- "What can you find about [IP address]?"

**System Control**:
- "Check system status"
- "Show running processes"
- "Open applications folder"

**Conversation Control**:
- "Stop listening" / "Go to sleep"
- "Repeat that"
- "Speak louder" / "Speak softer"

### Advanced Voice Commands

**Memory Operations**:
- "Remember that [information]"
- "What do you remember about [topic]?"
- "Forget about [topic]"

**Agent Management**:
- "Switch to [agent name]"
- "List available agents"
- "Create new agent for [purpose]"

**Workflow Control**:
- "Start workflow [name]"
- "Show workflow status"
- "Cancel current task"

## Customizing Voice Responses

### Response Styles

Configure how Greta responds to voice commands:

```yaml
voice:
  response_style: "conversational"  # Options below
  
# Response style options:
# - "brief": Short, direct answers
# - "detailed": Comprehensive responses
# - "conversational": Natural, friendly tone
# - "technical": Precise, technical language
```

### Personality Traits

Adjust Greta's speaking personality:

```yaml
agent:
  personality_traits:
    formality: 0.7                # 0.0 = casual, 1.0 = very formal
    enthusiasm: 0.5               # 0.0 = monotone, 1.0 = very excited
    verbosity: 0.6                # 0.0 = terse, 1.0 = very detailed
    humor: 0.3                    # 0.0 = serious, 1.0 = joke-heavy
```

## Multi-Language Support

### Supported Languages

Greta can understand and respond in multiple languages:

```yaml
voice:
  primary_language: "en-US"       # Primary language
  supported_languages:
    - "en-US"                     # English (US)
    - "en-GB"                     # English (UK)
    - "de-DE"                     # German
    - "fr-FR"                     # French
    - "es-ES"                     # Spanish
    - "it-IT"                     # Italian
```

### Language-Specific Wake Words

Set different wake words for different languages:

```yaml
wake_words_multilang:
  "en-US": ["Greta", "Computer", "Assistant"]
  "de-DE": ["Greta", "Computer", "Assistent"]
  "fr-FR": ["Greta", "Ordinateur", "Assistant"]
  "es-ES": ["Greta", "Computadora", "Asistente"]
```

## Troubleshooting Voice Issues

### Common Problems

| Issue | Cause | Solution |
|-------|-------|----------|
| Wake word not recognized | Microphone permissions | Check Privacy settings |
| Voice too quiet/loud | Volume settings | Adjust `voice_volume` in config |
| Accent hard to understand | Wrong TTS engine | Try different `tts_engine` |
| Commands not understood | Language mismatch | Check `primary_language` setting |
| Continuous false triggers | Sensitivity too high | Increase `silence_threshold` |

### Testing Voice Setup

Use these commands to test your voice configuration:

```bash
# Test microphone input
python3 -c "
import speech_recognition as sr
r = sr.Recognizer()
with sr.Microphone() as source:
    print('Say something...')
    audio = r.listen(source, timeout=5)
    try:
        print('You said:', r.recognize_google(audio))
    except:
        print('Could not understand audio')
"

# Test text-to-speech
python3 -c "
import pyttsx3
engine = pyttsx3.init()
engine.say('Hello, this is a voice test')
engine.runAndWait()
"
```

### Debug Mode

Enable verbose logging for voice features:

```yaml
advanced:
  log_level: "DEBUG"
  voice_debug: true
```

Then check the logs:

```bash
tail -f ~/Library/Logs/Greta/voice.log
```

## Privacy and Security

### Local Processing

For maximum privacy, enable local-only processing:

```yaml
privacy:
  local_processing_only: true     # No cloud APIs
  store_voice_data: false         # Don't save audio
  encrypt_storage: true           # Encrypt stored data
```

### Voice Data Handling

Configure how voice data is handled:

```yaml
voice:
  save_recordings: false          # Don't save audio files
  transcription_only: true        # Only store text transcriptions
  auto_delete_after: 24          # Hours to keep transcriptions
```

## Performance Optimization

### Resource Usage

Optimize voice processing for your system:

```yaml
voice:
  processing_threads: 2           # CPU threads for voice processing
  buffer_size: 1024              # Audio buffer size
  sample_rate: 16000             # Audio sample rate (Hz)
  chunk_duration: 0.1            # Audio chunk duration (seconds)
```

### Battery Optimization

For laptops, optimize battery usage:

```yaml
voice:
  continuous_listening: false     # Use wake words instead
  sleep_when_idle: true          # Sleep voice processing when idle
  idle_timeout: 300              # Seconds before sleeping
```

## Integration with Other Apps

### Shortcuts Integration

Create macOS Shortcuts that trigger Greta commands:

1. Open Shortcuts app
2. Create new shortcut
3. Add "Run Shell Script" action
4. Use this script:

```bash
curl -X POST "http://localhost:8000/api/voice/command" \
  -H "Content-Type: application/json" \
  -d '{"command": "YOUR_COMMAND_HERE"}'
```

### Alfred Integration

Create Alfred workflows for voice commands:

1. Create new workflow in Alfred
2. Add keyword trigger
3. Connect to "Run Script" action
4. Use the same curl command as above

## Advanced Features

### Voice Macros

Create custom voice macros for complex operations:

```yaml
voice_macros:
  "morning briefing":
    - "What's the weather?"
    - "Check my calendar"
    - "Any new emails?"
    - "System status report"
  
  "security scan":
    - "Check system vulnerabilities"
    - "Scan network for threats"
    - "Review access logs"
```

### Contextual Responses

Configure context-aware responses:

```yaml
voice:
  context_awareness: true
  remember_conversation: true
  context_timeout: 300           # Seconds to remember context
```

### Voice Biometrics

Enable voice recognition for security:

```yaml
security:
  voice_biometrics: true
  authorized_voices: ["user1", "user2"]
  voice_training_required: true
```

---

*For more advanced voice customization options, see the full API documentation at https://docs.cpas-project.com/voice-api*
