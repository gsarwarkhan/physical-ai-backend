import React, { useState } from 'react';
import styles from './chat.module.css';

export default function Root({children}) {
  const [input, setInput] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const askAI = async () => {
    setAnswer(""); // Clear previous answer
    setLoading(true);
    try {
      const fetchUrl = "http://localhost:8000/chat";
      console.log(`[Frontend] Attempting to fetch from: ${fetchUrl}`);

      const res = await fetch(fetchUrl, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ prompt: input })
      });

      console.log(`[Frontend] Fetch response status: ${res.status}`);

      if (!res.ok) {
        let errorDetail = `HTTP error! Status: ${res.status}`;
        try {
          const errorData = await res.json();
          errorDetail = errorData.detail || JSON.stringify(errorData);
        } catch (jsonError) {
          // If response is not JSON, use status text
          errorDetail = res.statusText || 'Unknown error';
        }
        console.error(`[Frontend] Fetch failed: ${errorDetail}`);
        setAnswer(`Error: ${errorDetail}`);
      } else {
        const data = await res.json();
        console.log("[Frontend] Received data:", data);
        setAnswer(data.response);
      }
    } catch (error) {
      console.error("[Frontend] Uncaught fetch error:", error);
      setAnswer(`Failed to connect to backend: ${error.message || 'Network error'}. Check console for details.`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {children}
      <div className={styles.chatContainer}>
        <div className={styles.chatBox}>
          <p>
            {loading 
              ? "Thinking..." 
              : answer || "Ask me anything about the textbook..."}
          </p>
          <input 
            value={input} 
            onChange={(e) => setInput(e.target.value)} 
            onKeyPress={(e) => e.key === 'Enter' && askAI()}
          />
          <button onClick={askAI} disabled={loading}>
            {loading ? "Please wait" : "Ask AI"}
          </button>
        </div>
      </div>
    </>
  );
}