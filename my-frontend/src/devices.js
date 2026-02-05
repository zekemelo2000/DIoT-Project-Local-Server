import React, { useState, useEffect } from 'react';
import { SliderDevice, ToggleDevice } from './control';

export default function Dashboard() {
  const [devices, setDevices] = useState([]);

  // 1. Fetch the list of devices (Runs First)
  const fetchDevices = async () => {
    try {
      const res = await fetch('http://localhost:8080/devices', { credentials: 'include' });

      if (res.status === 401) {
        window.location.href = "/local-login";
        return [];
      }

      const data = await res.json();
      setDevices(data);
      return data; // Pass data to the next step
    } catch (err) {
      console.error("Failed to fetch devices:", err);
      return [];
    }
  };

  // 2. Fetch value for a single device (Runs Second, once per device)
  const refreshDevice = async (device) => {
    try {
      const res = await fetch('http://localhost:8080/get-device-value', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          apiKey: device.apiKey,
          apiSecret: device.apiSecret,
          networkId: device.networkId,
        })
      });

      if (!res.ok) throw new Error("Offline");

      const data = await res.json();

      // Update state safely using networkId
      setDevices(prev => prev.map(d =>
        d.networkId === device.networkId
          ? { ...d, value: data.value, isOffline: false }
          : d
      ));

    } catch (err) {
      // If offline, grey out just this one device
      setDevices(prev => prev.map(d =>
        d.networkId === device.networkId
          ? { ...d, isOffline: true }
          : d
      ));
    }
  };

  // 3. The Sequence Controller
  useEffect(() => {
    let isMounted = true;

    // This sequence guarantees "Fetch List" -> THEN "Fetch Values"
    fetchDevices().then((loadedDevices) => {
      if (isMounted && Array.isArray(loadedDevices)) {
        loadedDevices.forEach(dev => {
           refreshDevice(dev);
        });
      }
    });

    return () => { isMounted = false; };
  }, []); // <--- The empty array [] ensures this entire block runs exactly once.

  // 4. Handle User Updates (Sliders/Toggles)
  const handleUpdate = async (device, newValue) => {
    try {
      // 1. Update UI immediately (Optimistic Update)
      setDevices(prev => prev.map(d =>
        d.networkId === device.networkId ? { ...d, value: newValue } : d
      ));

      // 2. Send to server
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

      // NOTE: We do NOT call fetchDevices() here.
      // This prevents the double-refresh you wanted to avoid.
    } catch (err) {
      console.error("Update failed:", err);
      // Optional: Re-check status if update fails
      refreshDevice(device);
    }
  };

  return (
    <div className="dashboard">
      {Array.isArray(devices) ? (
        devices.map(dev => {
          return dev.type === "slider_device" ? (
            <SliderDevice
              key={dev.networkId}
              device={dev}
              onUpdate={handleUpdate}
              onRefresh={refreshDevice}
            />
          ) : dev.type === "toggle_device" ? (
            <ToggleDevice
              key={dev.networkId}
              device={dev}
              onUpdate={handleUpdate}
              onRefresh={refreshDevice}
            />
          ) : (
            <p key={dev.networkId}>Unknown Device Type: {dev.type}</p>
          );
        })
      ) : (
        <p>Loading devices...</p>
      )}
    </div>
  );
}