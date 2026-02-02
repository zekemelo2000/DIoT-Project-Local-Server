import React, {useEffect, useState} from 'react';
import { useNavigate } from 'react-router-dom';

function DevicesPage() {
  const navigate = useNavigate();
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() =>{
      const verifySession = async() => {
          try{
              const response = await fetch('/check-session',{
                  method:'GET',
                  credentials: 'include'
              });

              if (response.ok) {
                  const data=  await response.json();
                  setDevices(data.devices);
                  setLoading(false);
              }
              else{
                  navigate('/');
              }
          } catch(error){
              navigate('/');
          }
      };

      verifySession().catch(console.error);

      const interval = setInterval(verifySession,30000);
      return () => clearInterval(interval);
  }, [navigate]);

  if (loading) return <p>Loading your dashboard...</p>

  return (
    <div style={{ padding: '40px', textAlign: 'center' }}>
      <h1>Welcome to the Device Management Page</h1>
      <p>Hello World! You have successfully logged in.</p>

      <div style={{ marginTop: '20px', border: '1px solid #ccc', padding: '20px' }}>
        <h3>Your Connected Devices:</h3>
        <ul style={{ listStyle: 'none', padding: 0 }}>
          <li>🟢 Smart Thermostat - Online</li>
          <li>🟢 Living Room Light - Online</li>a
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