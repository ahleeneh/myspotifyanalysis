import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

import LoginPage from './pages/LoginPage/LoginPage';
import UserPage from './pages/UserPages/UserPage';

function App() {

    return (
        <>
            <BrowserRouter>
                <main>
                    <Routes>
                        <Route path="/" element={<LoginPage />}></Route>
                        <Route path="/user" element={<UserPage />}></Route>
                    </Routes>
                </main>
            </BrowserRouter>

        </>
    );
}

export default App;
