import logo from './logo.svg';
import './App.css';
import LocalLoginPage from './local_login';
import LocalRegisterPage from "./local_register";

function App() {
  return (
    <div className="App">
      <LocalLoginPage />
        <LocalRegisterPage/>
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

export default App;
