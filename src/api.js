// src/api.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8001";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatWithAI = async (message, sessionId = null) => {
  try {
    const response = await api.post('/chat', {
      session_id: sessionId,
      message: message,
    });

    const data = response.data; // Axios automatically parses JSON

    if (data.status === "success") {
      return {
        response: data.data.response,
        session_id: data.data.session_id
      };
    } else {
      // This case should ideally not be hit if backend always returns success on 2xx
      // but handles unexpected data format
      throw new Error(data.message || "API returned an unexpected success status with no data.");
    }
  } catch (error) {
    let errorMsg = "Network Error. Please try again.";
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      errorMsg = error.response.data.message || `Server Error: ${error.response.status}`;
    } else if (error.request) {
      // The request was made but no response was received
      errorMsg = "No response from server. Backend might be down.";
    } else {
      // Something else happened while setting up the request
      errorMsg = error.message;
    }
    throw new Error(errorMsg);
  }
};
