"use client";

import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Calendar, Clock, Users, Link as LinkIcon, Copy, Check, ArrowRight, History } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

// Types
interface ParseResult {
  summary: string;
  start_time: string;
  end_time: string;
  time_zone: string;
  attendees: string[];
}

interface ScheduledEvent {
  eventId: string;
  htmlLink: string;
  meetLink: string;
  summary: string;
  start: string;
  end: string;
  attendees: string[];
}

interface HistoryEvent {
  id: number;
  summary: string;
  start_time: string;
  meet_link: string;
  attendees_count: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [command, setCommand] = useState("");
  const [parsed, setParsed] = useState<ParseResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [scheduling, setScheduling] = useState(false);
  const [scheduled, setScheduled] = useState<ScheduledEvent | null>(null);
  const [history, setHistory] = useState<HistoryEvent[]>([]);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [checkingAuth, setCheckingAuth] = useState(true);

  // Check Auth
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Check for connected query param
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('connected') === 'true') {
            toast.success("Successfully connected to Google Calendar!");
            window.history.replaceState({}, document.title, "/");
        }

        const res = await axios.get(`${API_BASE}/auth/status`, { withCredentials: true });
        setIsAuthenticated(res.data.isAuthenticated);
      } catch (e) {
        console.error(e);
      } finally {
        setCheckingAuth(false);
      }
    };
    checkAuth();
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/history`, { withCredentials: true });
      setHistory(res.data);
    } catch (e) {
      console.error("Failed to fetch history");
    }
  };

  // Debounced Parse
  useEffect(() => {
    const timer = setTimeout(async () => {
      if (!command.trim()) {
        setParsed(null);
        return;
      }
      setLoading(true);
      try {
        const res = await axios.post(`${API_BASE}/api/parse`, { command });
        setParsed(res.data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [command]);

  const handleSchedule = async () => {
    if (!parsed) return;
    setScheduling(true);
    try {
      const res = await axios.post(`${API_BASE}/api/schedule`, { command }, { withCredentials: true });
      setScheduled(res.data);
      toast.success("Event scheduled successfully!");
      setCommand("");
      setParsed(null);
      fetchHistory();
    } catch (e: any) {
      if (e.response?.status === 401) {
        toast.error("Please connect your Google Account first.");
        setIsAuthenticated(false);
      } else {
        toast.error("Failed to schedule event.");
      }
    } finally {
      setScheduling(false);
    }
  };

  const handleLogin = () => {
    window.location.href = `${API_BASE}/auth/start`;
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard!");
  };

  if (checkingAuth) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  return (
    <main className="min-h-screen p-4 md:p-24 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      <div className="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12">
        
        {/* Left Panel: Input */}
        <div className="space-y-8">
          <div className="space-y-2">
            <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">
              AI Scheduler
            </h1>
            <p className="text-gray-500 dark:text-gray-400">
              Describe your meeting naturally. I'll handle the rest.
            </p>
          </div>

          {!isAuthenticated ? (
            <div className="p-6 border rounded-xl bg-white dark:bg-gray-800 shadow-sm">
              <h3 className="text-lg font-semibold mb-2">Connect Google Calendar</h3>
              <p className="text-sm text-gray-500 mb-4">
                To schedule events, we need access to your calendar.
              </p>
              <button
                onClick={handleLogin}
                className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
              >
                <img src="https://www.svgrepo.com/show/475656/google-color.svg" className="w-5 h-5" alt="Google" />
                Connect with Google
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="relative">
                <textarea
                  value={command}
                  onChange={(e) => setCommand(e.target.value)}
                  placeholder="e.g., Schedule a 30 min sync with alice@example.com tomorrow at 2pm"
                  className="w-full h-32 p-4 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none shadow-sm transition-all"
                />
                {loading && (
                  <div className="absolute bottom-4 right-4">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                  </div>
                )}
              </div>

              <AnimatePresence>
                {parsed && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    className="p-6 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-lg"
                  >
                    <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-4">Preview</h3>
                    
                    <div className="space-y-3">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg text-blue-600">
                          <Calendar className="w-5 h-5" />
                        </div>
                        <div>
                          <p className="font-medium">{parsed.summary}</p>
                          <p className="text-sm text-gray-500">
                            {new Date(parsed.start_time).toLocaleString()}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg text-purple-600">
                          <Clock className="w-5 h-5" />
                        </div>
                        <div>
                          <p className="text-sm">
                            {Math.round((new Date(parsed.end_time).getTime() - new Date(parsed.start_time).getTime()) / 60000)} minutes
                          </p>
                        </div>
                      </div>

                      {parsed.attendees.length > 0 && (
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg text-green-600">
                            <Users className="w-5 h-5" />
                          </div>
                          <div className="flex flex-wrap gap-2">
                            {parsed.attendees.map((email) => (
                              <span key={email} className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded-full">
                                {email}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    <button
                      onClick={handleSchedule}
                      disabled={scheduling}
                      className="mt-6 w-full py-2 px-4 bg-black dark:bg-white text-white dark:text-black rounded-lg font-medium hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                      {scheduling ? "Scheduling..." : "Schedule Event"}
                      {!scheduling && <ArrowRight className="w-4 h-4" />}
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}
        </div>

        {/* Right Panel: Results & History */}
        <div className="space-y-8">
          <AnimatePresence>
            {scheduled && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="p-6 rounded-xl bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border border-green-200 dark:border-green-800"
              >
                <div className="flex items-center gap-2 text-green-700 dark:text-green-400 mb-4">
                  <Check className="w-5 h-5" />
                  <span className="font-semibold">Scheduled Successfully</span>
                </div>

                <h2 className="text-xl font-bold mb-2">{scheduled.summary}</h2>
                <p className="text-gray-600 dark:text-gray-300 mb-6">
                  {new Date(scheduled.start).toLocaleString()}
                </p>

                <div className="space-y-3">
                  {scheduled.meetLink && (
                    <div className="flex items-center gap-2 p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                      <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded text-blue-600">
                        <LinkIcon className="w-4 h-4" />
                      </div>
                      <div className="flex-1 truncate text-sm font-medium text-blue-600">
                        {scheduled.meetLink}
                      </div>
                      <button
                        onClick={() => copyToClipboard(scheduled.meetLink)}
                        className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                      >
                        <Copy className="w-4 h-4 text-gray-500" />
                      </button>
                    </div>
                  )}
                  
                  <a
                    href={scheduled.htmlLink}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block w-full text-center py-2 text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100"
                  >
                    Open in Google Calendar
                  </a>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="space-y-4">
            <div className="flex items-center gap-2 text-gray-500">
              <History className="w-4 h-4" />
              <h3 className="text-sm font-medium uppercase tracking-wider">Recent History</h3>
            </div>
            
            <div className="space-y-3">
              {history.map((event) => (
                <div key={event.id} className="p-4 rounded-lg bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-medium truncate flex-1">{event.summary}</h4>
                    <span className="text-xs text-gray-500 whitespace-nowrap ml-2">
                      {new Date(event.start_time).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500">
                      {event.attendees_count} attendees
                    </span>
                    {event.meet_link && (
                      <button
                        onClick={() => copyToClipboard(event.meet_link)}
                        className="text-xs text-blue-600 hover:underline flex items-center gap-1"
                      >
                        <LinkIcon className="w-3 h-3" />
                        Copy Link
                      </button>
                    )}
                  </div>
                </div>
              ))}
              {history.length === 0 && (
                <p className="text-sm text-gray-400 italic">No recent events</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
