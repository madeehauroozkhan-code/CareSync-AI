import React, { useState, useRef } from "react";
import { Mic, MicOff } from "lucide-react";

export default function VoiceInput({ onTranscript, language = "hi-IN" }) {
  const [isListening, setIsListening] = useState(false);
  const [unsupported, setUnsupported] = useState(false);
  const recognitionRef = useRef(null);

  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setUnsupported(true);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = language;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => setIsListening(false);

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      onTranscript(transcript);
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  const stopListening = () => {
    recognitionRef.current?.stop();
    setIsListening(false);
  };

  if (unsupported) {
    return (
      <span className="text-xs text-red-500 font-medium px-2">
        Voice input unsupported.
      </span>
    );
  }

  return (
    <div className="relative">
      {isListening && (
        <span className="absolute -inset-1 rounded-full bg-red-500 opacity-30 animate-pulse-slow blur-sm"></span>
      )}
      <button
        type="button"
        onClick={isListening ? stopListening : startListening}
        className={`relative z-10 flex items-center justify-center w-10 h-10 rounded-full transition-all duration-300 ${
          isListening 
            ? "bg-red-500 text-white shadow-lg shadow-red-500/30 scale-105" 
            : "bg-slate-100 text-slate-400 hover:bg-slate-200 hover:text-slate-600"
        }`}
        aria-label={isListening ? "Stop recording" : "Start voice input"}
      >
        {isListening ? <MicOff size={18} /> : <Mic size={18} />}
      </button>
    </div>
  );
}
