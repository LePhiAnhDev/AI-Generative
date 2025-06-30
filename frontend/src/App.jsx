import React from 'react';
import AIGenerator from './components/AIGenerator';

function App() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800 text-white">
            <div className="container mx-auto px-4 py-8">
                <AIGenerator />
            </div>
        </div>
    );
}

export default App;