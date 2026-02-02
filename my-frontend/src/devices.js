import React from 'react';
import { useNavigate } from 'react-router-dom';

function DevicesPage() {
  const navigate = useNavigate();

  return (
    <div style={{ padding: '40px', textAlign: 'center' }}>
      <h1>Welcome to the Device Management Page</h1>
      <p>Hello World! You have successfully logged in.</p>

      <div style={{ marginTop: '20px', border: '1px solid #ccc', padding: '20px' }}>
        <h3>Your Connected Devices:</h3>
        <ul style={{ listStyle: 'none', padding: 0 }}>
          <li>🟢 Smart Thermostat - Online</li>
          <li>🟢 Living Room Light - Online</li>
          <li>🔴 Garage Camera - Offline</li>
        </ul>
      </div>

      <button
        onClick={() => navigate('/')}
        style={{ marginTop: '30px', cursor: 'pointer' }}
      >
        Logout / Go Back
      </button>
    </div>
  );
}

export default DevicesPage;