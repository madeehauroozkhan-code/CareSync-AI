import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Activity, Navigation, Loader2 } from 'lucide-react';
import { sendChatMessage } from '../../services/api';

export default function PatientIntake() {
  const [messages, setMessages] = useState([
    { role: 'system', content: 'Namaste! Main AI Sahayak hoon. Kripya apne symptoms ya pareshani bataein.' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userText = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userText }]);
    setLoading(true);

    try {
      // Simulate sequential AI agent thinking while the backend runs the LangGraph orchestrator
      setMessages(prev => [...prev, { role: 'system', content: 'AI Agents are analyzing your request in parallel...', isAgent: true }]);
      
      const data = await sendChatMessage({ message: userText, lat: 25.61, lng: 85.14 });
      
      const intakeData = data.intake_data || {};
      const triageData = data.triage_data || {};
      const careData = data.care_coordination_data || {};

      setLoading(false);
      setResult({ intake: intakeData, triage: triageData, care: careData });
      setMessages(prev => [...prev, { 
        role: 'system', 
        content: data.response_text || `Analysis Complete! Urgency: ${triageData.urgency?.toUpperCase() || 'UNKNOWN'}.\nRecommended Hospital: ${careData.recommended_hospital?.hospital_name || 'N/A'}.`
      }]);

    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: 'system', content: 'Sorry, there was an error processing your request. Please ensure the backend is running.' }]);
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white/80 backdrop-blur-md rounded-xl border border-slate-200 shadow-xl overflow-hidden">
      {/* Header */}
      <div className="bg-primary/10 border-b border-primary/20 p-4 flex items-center gap-3">
        <div className="w-10 h-10 rounded-full overflow-hidden flex items-center justify-center">
          <img src="/logo.png" alt="AI Sahayak Logo" className="w-full h-full object-cover" />
        </div>
        <div>
          <h3 className="font-bold text-slate-800">AI Sahayak Agent</h3>
          <p className="text-xs text-primary font-medium">Live Coordination Mode</p>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 p-4 overflow-y-auto flex flex-col gap-3 min-h-[250px] max-h-[350px]">
        <AnimatePresence>
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`max-w-[85%] p-3 rounded-2xl text-sm ${
                msg.role === 'user' 
                  ? 'bg-primary text-white self-end rounded-br-none' 
                  : msg.isAgent 
                    ? 'bg-slate-100 text-slate-500 self-start text-xs font-mono border border-slate-200'
                    : 'bg-slate-100 text-slate-800 self-start rounded-bl-none'
              }`}
            >
              {msg.content}
            </motion.div>
          ))}
          {loading && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="self-start text-primary">
              <Loader2 className="animate-spin w-5 h-5" />
            </motion.div>
          )}
        </AnimatePresence>
        
        {/* Result Card */}
        {result && (
          <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="mt-2 p-4 bg-blue-50 border border-blue-100 rounded-xl">
            <h4 className="font-bold text-blue-900 mb-2">Hospital Recommendation</h4>
            <div className="text-sm space-y-2 text-slate-700">
              <p><strong>Hospital:</strong> {result.care.recommended_hospital?.hospital_name}</p>
              <p><strong>Score:</strong> {result.care.recommended_hospital?.total_score}/100</p>
              <p className="text-xs text-slate-500">{result.care.explanation}</p>
              
              {result.care.ambulance_dispatched && (
                <div className="mt-3 bg-red-100 text-red-700 p-2 rounded flex items-center gap-2">
                  <Activity size={16} /> Ambulance Dispatched (ETA: {result.care.ambulance_eta_minutes} mins)
                </div>
              )}
            </div>
          </motion.div>
        )}
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="p-3 border-t border-slate-200 bg-slate-50 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Apne symptoms batayein..."
          disabled={loading}
          className="flex-1 px-4 py-2 rounded-full border border-slate-300 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary text-sm"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center hover:bg-primary/90 disabled:opacity-50 transition-colors"
        >
          <Send size={16} className="ml-1" />
        </button>
      </form>
    </div>
  );
}
