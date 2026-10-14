import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, User, Bot } from "lucide-react";
import VoiceInput from "./VoiceInput.jsx";
import StatusTracker from "./StatusTracker.jsx";
import { sendChatMessage } from "../services/api.js";
 
const URGENCY_STYLES = {
  Critical: "bg-red-500/10 dark:bg-red-900/20 text-red-600 dark:text-red-400 border-red-500/30 dark:border-red-800/50",
  Urgent: "bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400 border-amber-300 dark:border-amber-700/50",
  Routine: "bg-teal-500/10 dark:bg-teal-900/20 text-teal-600 dark:text-teal-400 border-teal-500/30 dark:border-teal-800/50",
};
 
const DEFAULT_LOCATION = { lat: 25.6, lng: 85.13 }; // Patna, used as demo default
 
export default function ChatWindow() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      type: "text",
      text: "Namaste. I am AI Sahayak, your intelligent healthcare coordinator. Please describe your symptoms or medical emergency using text or voice, and I will assist you immediately.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const containerRef = useRef(null);
 
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [messages]);
 
  const handleSend = async (textOverride) => {
    const text = (textOverride ?? input).trim();
    if (!text || isLoading) return;
 
    setMessages((prev) => [...prev, { role: "user", type: "text", text }]);
    setInput("");
    setIsLoading(true);
 
    try {
      const result = await sendChatMessage({
        message: text,
        lat: DEFAULT_LOCATION.lat,
        lng: DEFAULT_LOCATION.lng,
      });
 
      // The reply field contains the plain-language message
      const replyText = result.reply || result.human_response || "I could not process the response.";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", type: "text", text: replyText },
      ]);
      
      const isGreeting = result.state?.workflow_objective === "GREETING" || result.is_greeting;
      const triage = result.state?.triage_data || result.triage;
      
      if (isGreeting || !triage) {
        setIsLoading(false);
        return;
      }
 
      const urgency = triage.urgency;
 
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          type: "triage",
          urgency,
          confidence: triage.confidence,
          reasons: triage.reasons || triage.clinical_reasons || [],
        },
      ]);
 
      if (urgency === "Routine") {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", type: "advice", advice: result.state?.routine_advice || result.routine_advice || replyText },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", type: "coordination", coordinationResult: result.state?.care_coordination_data || result.care_coordination },
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", type: "text", text: `Something went wrong reaching the server: ${err.message}` },
      ]);
    } finally {
      setIsLoading(false);
    }
  };
 
  return (
    <div className="relative flex flex-col h-full max-w-2xl mx-auto rounded-2xl p-[2px] overflow-hidden shadow-[0_0_50px_rgba(6,182,212,0.4),0_0_15px_rgba(59,130,246,0.5)] bg-slate-900 group">
      {/* Animated glowing border background */}
      <div className="absolute top-1/2 left-1/2 h-[200%] w-[200%] -translate-x-1/2 -translate-y-1/2 bg-[conic-gradient(from_0deg,transparent_0_320deg,#06b6d4_360deg)] animate-[spin_3s_linear_infinite]" />
      <div className="absolute top-1/2 left-1/2 h-[200%] w-[200%] -translate-x-1/2 -translate-y-1/2 bg-[conic-gradient(from_180deg,transparent_0_320deg,#3b82f6_360deg)] animate-[spin_3s_linear_infinite]" />
      
      {/* Absolute blur for inner neon glow (reduced opacity to fix overpowering blue effect) */}
      <div className="absolute inset-0 bg-blue-500/5 blur-xl z-0 rounded-2xl pointer-events-none" />
      {/* Inner Chat Container */}
      <div className="relative z-10 flex flex-col h-full w-full bg-white dark:bg-slate-900 rounded-xl overflow-hidden flex-1">
        <div ref={containerRef} className="flex-1 overflow-y-auto p-4 space-y-3 scroll-smooth bg-white dark:bg-slate-900">
          <AnimatePresence initial={false}>
            {messages.map((msg, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className={msg.role === "user" ? "flex justify-end items-end" : "flex justify-start items-end"}
              >
                {msg.role === "assistant" && msg.type === "text" && (
                  <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/40 flex items-center justify-center mr-2 shrink-0 border border-blue-200 dark:border-blue-800 overflow-hidden mb-1">
                    <img src="/logo.png" alt="Bot Logo" className="w-full h-full object-cover" />
                  </div>
                )}

                {msg.type === "text" && (
                  <div
                    className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm whitespace-pre-wrap leading-relaxed shadow-sm relative ${
                      msg.role === "user" ? "bg-blue-600 dark:bg-blue-500 text-white rounded-br-none" : "bg-gray-100 dark:bg-slate-800 text-gray-800 dark:text-slate-200 rounded-bl-none border border-gray-200 dark:border-slate-700"
                    }`}
                  >
                    {/* Basic markdown bold support for rendering **Hospital Name** */}
                    {msg.text.split('**').map((part, index) => 
                      index % 2 === 1 ? <strong key={index}>{part}</strong> : part
                    )}
                  </div>
                )}

                {msg.role === "user" && msg.type === "text" && (
                  <div className="w-8 h-8 rounded-full bg-blue-50 dark:bg-blue-900/30 flex items-center justify-center ml-2 shrink-0 border border-blue-100 dark:border-blue-800/50 mb-1">
                    <User size={16} className="text-blue-600 dark:text-blue-400" />
                  </div>
                )}
  
                {msg.type === "triage" && (
                  <div className={`ml-10 max-w-[80%] w-full rounded-xl border px-4 py-3 shadow-sm ${URGENCY_STYLES[msg.urgency]}`}>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="font-bold text-sm tracking-wide uppercase">{msg.urgency}</span>
                      <span className="text-[10px] font-bold opacity-80 bg-black/5 px-2 py-0.5 rounded-full">{Math.round(msg.confidence * 100)}% CONFIDENCE</span>
                    </div>
                    <ul className="text-xs space-y-1 opacity-90 font-medium">
                      {msg.reasons.map((r, idx) => (
                        <li key={idx} className="flex items-start gap-1.5">
                          <span className="mt-1 flex-shrink-0 h-1 w-1 rounded-full bg-current opacity-60"></span>
                          {r}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
  
                {msg.type === "advice" && (
                  <div className="ml-10 max-w-[80%] w-full bg-teal-500/5 dark:bg-teal-900/10 border border-teal-500/20 dark:border-teal-800/30 rounded-xl px-4 py-3 shadow-sm">
                    <p className="text-xs font-bold text-teal-600 dark:text-teal-400 mb-2 uppercase tracking-wide">Recommended Home-Care</p>
                    <ul className="text-sm text-gray-700 dark:text-gray-300 space-y-1.5">
                      {msg.advice.map((line, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <span className="mt-1.5 flex-shrink-0 h-1.5 w-1.5 rounded-full bg-teal-500/40 dark:bg-teal-500/60"></span>
                          <span className="leading-snug">{line}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
  
                {msg.type === "coordination" && (
                  <div className="ml-10 w-full max-w-[80%]">
                    <StatusTracker coordinationResult={msg.coordinationResult} />
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
  
          {isLoading && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-xs text-gray-400 dark:text-gray-500 pl-1">
              AI Sahayak is thinking…
            </motion.div>
          )}
        </div>
  
        <div className="border-t border-gray-100 dark:border-slate-800 p-3 flex items-center gap-2 bg-white dark:bg-slate-900">
          <VoiceInput onTranscript={(text) => handleSend(text)} />
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Apni problem yahan likhein..."
            className="flex-1 border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-900 dark:text-white rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 placeholder-gray-400 dark:placeholder-gray-500"
          />
          <button
            onClick={() => handleSend()}
            disabled={isLoading}
            className="flex items-center justify-center w-10 h-10 rounded-full bg-blue-600 text-white hover:bg-blue-700 transition-colors disabled:opacity-50"
            aria-label="Send message"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
