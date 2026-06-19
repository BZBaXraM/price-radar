"use client";

import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import type { ChatMessage } from "@/lib/types";
import { tr } from "@/lib/i18n";
import { useAppStore } from "@/store/useAppStore";

export function ChatWidget() {
  const lang = useAppStore((s) => s.lang);
  const open = useAppStore((s) => s.chatOpen);
  const setOpen = useAppStore((s) => s.setChatOpen);
  const toggle = useAppStore((s) => s.toggleChat);

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, sending]);

  async function send(e: React.FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || sending) return;
    const history = messages.map((m) => ({ role: m.role, content: m.content }));
    setMessages((m) => [...m, { role: "user", content: text }]);
    setInput("");
    setSending(true);
    try {
      const res = await api.chat(text, lang, history);
      setMessages((m) => [...m, { role: "assistant", content: res.reply }]);
    } catch {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: "⚠︎ " + tr(lang, "loading") },
      ]);
    } finally {
      setSending(false);
    }
  }

  return (
    <>
      {/* Floating launcher */}
      <button
        onClick={toggle}
        aria-label={tr(lang, "ai_title")}
        className="fixed bottom-5 right-5 z-40 bg-ink text-paper w-14 h-14 rounded-full flex items-center justify-center text-xl hover:bg-accent transition-colors shadow-none"
      >
        {open ? "×" : "✦"}
      </button>

      {open && (
        <div className="fixed bottom-24 right-5 z-40 w-[min(92vw,380px)] h-[min(70vh,560px)] bg-paper border border-ink flex flex-col animate-fade-up">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-line">
            <div>
              <p className="font-display text-lg leading-none">{tr(lang, "ai_title")}</p>
              <p className="text-xs text-muted mt-1">{tr(lang, "ai_hint")}</p>
            </div>
            <button onClick={() => setOpen(false)} className="text-muted hover:text-ink text-xl">
              ×
            </button>
          </div>

          {/* Messages */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto thin-scroll px-4 py-4 space-y-3">
            <Bubble role="assistant" content={tr(lang, "ai_welcome")} />
            {messages.map((m, i) => (
              <Bubble key={i} role={m.role} content={m.content} />
            ))}
            {sending && (
              <div className="text-muted text-sm italic">{tr(lang, "loading")}</div>
            )}
          </div>

          {/* Input */}
          <form onSubmit={send} className="border-t border-line p-3 flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={tr(lang, "ai_placeholder")}
              className="flex-1 bg-transparent border-b border-line focus:border-ink py-2 px-1 text-sm outline-none placeholder:text-muted"
            />
            <button
              type="submit"
              disabled={sending}
              className="bg-ink text-paper text-sm px-3 py-2 hover:bg-accent transition-colors disabled:opacity-40"
            >
              {tr(lang, "ai_send")}
            </button>
          </form>
        </div>
      )}
    </>
  );
}

function Bubble({ role, content }: { role: string; content: string }) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] text-sm leading-relaxed px-3 py-2 whitespace-pre-wrap ${
          isUser
            ? "bg-ink text-paper"
            : "bg-paper-2 text-ink border border-line"
        }`}
      >
        {content}
      </div>
    </div>
  );
}
