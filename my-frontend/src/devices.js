import React, { useState, useEffect } from 'react';
import { SliderDevice, ToggleDevice } from './control';

export default function Dashboard() {
  const [devices, setDevices] = useState([]);

  const fetchDevices = async () => {
  try {
    const res = await fetch('http://localhost:8080/devices', {
      credentials: 'include'});

    if (res.status === 401) {
      // The session is NOT active, send them back to login
      window.location.href = "/local-login";
      return;
    }

    const data = await res.json();
    setDevices(data);
  } catch (err) {
    console.error("Failed to fetch devices:", err);
  }
};

  useEffect(() => {
    fetchDevices().then(() => {
      // Logic to run after fetch succeeds
      console.log("Devices loaded");
    })
    .catch((err) => {
      // Error handling
      console.error(err);
    });
  }, []);

  const handleUpdate = async (device, newValue) => {
    try {
      await fetch('http://localhost:8080/update-device', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          apiKey: device.apiKey,
          apiSecret: device.apiSecret,
          networkId: device.networkId,
          value: newValue
        }),
      });
      // Refresh to sync with the backend confirmation
      await fetchDevices();
    } catch (err) {
      console.error("Update failed:", err);
    }
  };

  return (
    <div className="dashboard">
      {Array.isArray(devices) ? (
        devices.map(dev => {
          if (dev.type === "slider_device") {
            return <SliderDevice key={dev.id} device={dev} onUpdate={handleUpdate} />;
          } else if (dev.type === "toggle_device") {
            return <ToggleDevice key={dev.id} device={dev} onUpdate={handleUpdate} />;
          }
          return <p key={dev.id}>Unknown Device Type</p>;
        })
      ) : (
        <p>Error: Data received is not a list of devices.</p>
      )}
    </div>
  );
}