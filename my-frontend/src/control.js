import React, { useState, useEffect } from 'react';

// --- SLIDER COMPONENT ---
export const SliderDevice = ({ device, onUpdate, onRefresh }) => {
  const [tempValue, setTempValue] = useState(device.value);
  const isOffline = device.isOffline;

  // Sync internal slider state if external device data changes
  useEffect(() => {
    setTempValue(device.value);
  }, [device.value]);

  useEffect(() => {
    const handler = setTimeout(() => {
      if (tempValue !== device.value && !isOffline) {
        onUpdate(device, tempValue);
      }
    }, 500);
    return () => clearTimeout(handler);
  }, [tempValue]);

  return (
    <div className={`device-card ${isOffline ? 'offline-mode' : ''}`}>
      <h4>{device.name} {isOffline && <span className="error-tag">(OFFLINE)</span>}</h4>
      <input
        type="range"
        disabled={isOffline}
        value={tempValue}
        onChange={(e) => setTempValue(parseInt(e.target.value))}
      />
      <span>{tempValue}%</span>
      <button className="refresh-btn" onClick={() => onRefresh(device)}>Refresh</button>
    </div>
  );
};

// --- TOGGLE COMPONENT ---
export const ToggleDevice = ({ device, onUpdate, onRefresh }) => {
  const isOffline = device.isOffline;

  const handleToggle = () => {
    if (isOffline) return;
    const newValue = device.value === 1 ? 0 : 1;
    onUpdate(device, newValue);
  };

  return (
    <div className={`device-card ${isOffline ? 'offline-mode' : ''}`}>
      <h4>{device.name} {isOffline && <span className="error-tag">(OFFLINE)</span>}</h4>
      <button
        disabled={isOffline}
        onClick={handleToggle}
        className={device.value === 1 ? "btn-on" : "btn-off"}
      >
        {device.value === 1 ? "ON" : "OFF"}
      </button>
      <button className="refresh-btn" onClick={() => onRefresh(device)}>Refresh</button>
    </div>
  );
};