
import React from 'react';
import { SparklesIcon } from './icons';

const Footer = () => {
    return (
        <footer className="bg-gray-800 border-t border-gray-700 text-xs text-gray-400 px-4 py-1 flex justify-between items-center z-20">
            <div className="flex items-center space-x-4">
                <span><span className="text-green-400">●</span> Connected</span>
                <span>Branch: <span className="text-white">feature/sentience-tuning</span></span>
                <span>Last Save: <span className="text-white">Just now (Autosaved)</span></span>
            </div>
            <div className="flex items-center space-x-4">
                <div className="h-4 w-px bg-gray-600"></div>
                <span>Compute: <span className="text-white">98%</span></span>
                <span>Memory: <span className="text-white">76%</span></span>
                <span>Network: <span className="text-white">1.2 PB/s</span></span>
                 <div className="h-4 w-px bg-gray-600"></div>
                <button className="flex items-center text-cyan-400 hover:text-cyan-300">
                    <SparklesIcon className="h-4 w-4 mr-1"/>
                    <span>AI Co-Pilot: Active</span>
                </button>
            </div>
        </footer>
    );
};

export default Footer;
