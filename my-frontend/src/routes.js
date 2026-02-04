import {BrowserRouter as Router, Routes, Route} from 'react-router-dom';
import LocalLoginPage from './local_login';
import LocalRegisterPage from './local_register';
import Dashboard from './devices';

export const RoutePage = () => {
    return(
        <Router>
            <Routes>
                <Route path="/" element={<h1>HELLO WORLD YOU'RE IN ROOT</h1>}/>
                <Route path="/local-login" element={<LocalLoginPage/>}/>
                <Route path="/local-register" element={<LocalRegisterPage/>}/>
                <Route path="/Devices" element={<Dashboard/>}/>
                <Route path="*" element={<h1>404 MISSING WEBPAGE</h1>}/>
            </Routes>
        </Router>
    );
}

export default RoutePage;
