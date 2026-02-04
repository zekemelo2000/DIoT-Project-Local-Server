import React, { useState, useEffect } from 'react';

// --- SLIDER COMPONENT ---
export const SliderDevice = ({ device, onUpdate }) => {
  const [tempValue, setTempValue] = useState(device.value);

  useEffect(() => {
    const handler = setTimeout(() => {
      if (tempValue !== device.value) onUpdate(device, tempValue);
    }, 500);
    return () => clearTimeout(handler);
  }, [tempValue]);

  return (
    <div className="device-card">
      <h4>{device.name} (Slider)</h4>
      <input
        type="range"
        value={tempValue}
        onChange={(e) => setTempValue(parseInt(e.target.value))}
      />
      <span>{tempValue}%</span>
    </div>
  );
};

// --- TOGGLE COMPONENT ---
export const ToggleDevice = ({ device, onUpdate }) => {
  const handleToggle = () => {
    const newValue = device.value === 1 ? 0 : 1;
    onUpdate(device, newValue);
  };

  return (
    <div className="device-card">
      <h4>{device.name} (Switch)</h4>
      <button onClick={handleToggle}>
        {device.value === 1 ? "ON" : "OFF"}
      </button>
    </div>
  );
};