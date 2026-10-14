import React from 'react';
import ChatWindow from '../ChatWindow';

export default function ChatSection() {
  return (
    <section id="chat" className="py-24 bg-slate-50 dark:bg-slate-900 relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,_var(--tw-gradient-stops))] from-blue-50 dark:from-slate-800 via-slate-50 dark:via-slate-900 to-slate-50 dark:to-slate-900" />
      
      <div className="container mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white">
            Talk to AI Sahayak
          </h2>
          <p className="mt-4 text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
            Describe your symptoms naturally using voice or text. Our intelligent agents will assess urgency, provide home-care advice, or route you to the best-equipped hospital in real-time.
          </p>
        </div>
        
        <div className="h-[600px] w-full max-w-3xl mx-auto shadow-2xl dark:shadow-black/50 rounded-3xl overflow-hidden ring-1 ring-slate-200 dark:ring-slate-700 bg-white dark:bg-slate-800">
          <ChatWindow />
        </div>
      </div>
    </section>
  );
}
