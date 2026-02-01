import React, { useState } from 'react';

function LocalRegisterPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleRegister = async (e) => {
    e.preventDefault();

    const response = await fetch('/local-register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
      // Essential for session cookies to work across origins/requests
      credentials: 'include'
    });

    if (response.ok) {
      alert("Successfully registered user");
      // Redirect user or update global state here
    } else {
      alert("Registration failed");
    }
  };

  return (
    <form onSubmit={handleRegister}>
        <div>registration form</div>
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

export default LocalRegisterPage;