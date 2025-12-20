import React, { useState } from 'react';
import styles from './chat.module.css';

export default function Root({children}) {
  const [input, setInput] = useState("");
  const [answer, setAnswer] = useState("");

  const askAI = async () => {
    const res = await fetch("http://127.0.0.1:8000/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: input })
    });
    const data = await res.json();
    setAnswer(data.answer);
  };

  return (
    <>
      {children}
      <div className={styles.chatContainer}>
        <div className={styles.chatBox}>
          <p>{answer || "Ask me anything about the textbook..."}</p>
          <input value={input} onChange={(e) => setInput(e.target.value)} />
          <button onClick={askAI}>Ask AI</button>
        </div>
      </div>
    </>
  );
}