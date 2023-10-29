import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
// import './App.css';

import LoginPage from './pages/LoginPage/LoginPage';
import UserHomePage from './pages/UserPages/UserHomePage';

function App() {

    return (
        <>
            <BrowserRouter>
                <main>
                    <Routes>
                        <Route path="/" element={<LoginPage />}></Route>
                        <Route path="/user" element={<UserHomePage />}></Route>
                    </Routes>
                </main>
            </BrowserRouter>

        </>
    );
}

export default App;
