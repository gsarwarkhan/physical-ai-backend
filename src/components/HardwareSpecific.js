import React from 'react';

export default function HardwareSpecific({ type, children }) {
  // In a real app, 'userHardware' would come from your Better-Auth session
  const userHardware = "Jetson Nano"; 

  if (userHardware === type) {
    return (
      <div style={{ border: '2px solid #4facfe', padding: '10px', borderRadius: '8px' }}>
        <strong>🚀 Personalized for your {type}:</strong>
        {children}
      </div>
    );
  }
  return null;
}