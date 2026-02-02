import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function LocalLoginPage() {const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();

    const response = await fetch('/local-login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
      // Essential for session cookies to work across origins/requests
      credentials: 'include'
    });

    const data = await response.json()

    if (response.ok && data.status === "success") {
        navigate('/devices');
    } else {
      alert("Login failed");
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Username"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      <button type="submit">Login</button>
    </form>
  );
}

export default LocalLoginPage;