import React from "react";
import { motion } from "framer-motion";
import ChatWindow from "../components/ChatWindow.jsx";

export default function ChatPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-10 relative overflow-hidden">
      {/* Decorative background blobs */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-teal/20 rounded-full blur-[100px] animate-blob"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-navy-300/30 rounded-full blur-[100px] animate-blob" style={{ animationDelay: '2s' }}></div>
      <div className="absolute top-[20%] right-[10%] w-[20%] h-[20%] bg-coral/10 rounded-full blur-[80px] animate-blob" style={{ animationDelay: '4s' }}></div>

      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="text-center mb-8 relative z-10"
      >
        <h1 className="text-4xl md:text-5xl font-display font-bold text-navy-800 tracking-tight">
          AI <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal to-navy">Sahayak</span>
        </h1>
        <p className="text-base text-navy-600/80 mt-3 max-w-md mx-auto font-medium">
          Healthcare coordination at your fingertips. Describe your symptoms to get started.
        </p>
      </motion.div>

      <div className="w-full max-w-3xl h-[75vh] relative z-10">
        <ChatWindow />
      </div>
    </div>
  );
}
