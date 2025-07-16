import React, { useState, useRef } from 'react';
import { UploadIcon, DocumentTextIcon, TrashIcon } from '../components/icons';

const StatCard = ({ title, value, change, changeType }: { title: string, value: string, change: string, changeType: 'up' | 'down' }) => (
    <div className="bg-gray-800 p-4 rounded-lg shadow-lg">
        <h3 className="text-sm text-gray-400">{title}</h3>
        <p className="text-2xl font-bold text-white">{value}</p>
        <p className={`text-sm flex items-center ${changeType === 'up' ? 'text-green-400' : 'text-red-400'}`}>
            {changeType === 'up' ? 
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 15l7-7 7 7" /></svg> :
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7 7" /></svg>
            }
            {change}
        </p>
    </div>
);

const DatasetManager = () => {
  const [datasets, setDatasets] = useState([
    'ImageNet-100K (Pre-loaded)', 
    'Custom Synthetic (Generated)'
  ]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      const newFiles = Array.from(event.target.files).map(file => file.name);
      setDatasets(prev => [...new Set([...prev, ...newFiles])]); // Use Set to avoid duplicates
      if(event.target) {
        event.target.value = ''; // Allow re-loading the same file
      }
    }
  };

  const handleLoadClick = () => {
    fileInputRef.current?.click();
  };

  const removeDataset = (nameToRemove: string) => {
    setDatasets(prev => prev.filter(name => name !== nameToRemove));
  };
  
  const isPreloaded = (name: string) => name.includes('(Pre-loaded)') || name.includes('(Generated)');

  return (
    <div>
      <p className="font-semibold text-cyan-400 mb-2">Datasets</p>
      <div className="space-y-2 bg-gray-900/50 p-2 rounded-md max-h-48 overflow-y-auto">
        {datasets.map((name, index) => (
          <div key={`${name}-${index}`} className="flex items-center justify-between bg-gray-700 p-2 rounded-md">
            <div className="flex items-center gap-2 truncate">
              <DocumentTextIcon className="w-4 h-4 text-gray-400 flex-shrink-0" />
              <span className="text-white truncate" title={name}>{name}</span>
            </div>
            <button 
              onClick={() => removeDataset(name)} 
              disabled={isPreloaded(name)}
              className="text-gray-500 hover:text-red-400 transition-colors p-1 rounded-full disabled:opacity-30 disabled:cursor-not-allowed"
              title={isPreloaded(name) ? 'Cannot remove pre-loaded dataset' : 'Remove dataset'}
            >
              <TrashIcon className="w-4 h-4" />
            </button>
          </div>
        ))}
         {datasets.length === 0 && (
            <p className="text-gray-500 text-center py-4">No datasets loaded.</p>
        )}
      </div>
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        multiple
        accept=".txt,.json,.jsonl"
        className="hidden"
      />
      <button onClick={handleLoadClick} className="mt-3 w-full flex items-center justify-center gap-2 bg-cyan-600 hover:bg-cyan-700 text-white font-bold py-2 px-4 rounded-lg transition-colors">
        <UploadIcon className="w-5 h-5" />
        Load Dataset(s)
      </button>
    </div>
  );
};

const AgiTrainer = () => {
  return (
    <div className="h-full w-full flex flex-col bg-gray-900 text-white overflow-y-auto p-4 md:p-6 space-y-6">
      {/* Header Controls */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-cyan-400">Training Dashboard: AGI_Omega_v7</h1>
        <div className="flex space-x-2">
          <button className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-lg transition-colors">STOP TRAINING</button>
          <button className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition-colors">PAUSE</button>
        </div>
      </div>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard title="Overall Loss" value="0.0134" change="-2.5%" changeType="down" />
          <StatCard title="Accuracy" value="99.87%" change="+0.1%" changeType="up" />
          <StatCard title="Epoch" value="42 / 100" change="3h remaining" changeType="up" />
          <StatCard title="Cluster Utilization" value="98.5%" change="-0.2%" changeType="down" />
      </div>

      {/* Main Content Area */}
      <div className="flex-grow grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Panel: Visualizations */}
        <div className="lg:col-span-2 bg-gray-800 p-4 rounded-lg shadow-lg flex flex-col">
            <h2 className="text-lg font-bold mb-4">Live Metrics</h2>
            <div className="flex-grow bg-gray-900 rounded-md p-2 relative">
                <p className="absolute top-2 left-2 text-xs text-gray-500">Loss vs. Epoch (Live)</p>
                {/* Placeholder for a chart */}
                <div className="w-full h-full border-2 border-dashed border-gray-700 rounded-md flex items-center justify-center">
                    <p className="text-gray-600">Live Chart Visualization Area</p>
                </div>
            </div>
            <div className="flex-grow bg-gray-900 rounded-md p-2 mt-4 relative">
                <p className="absolute top-2 left-2 text-xs text-gray-500">Synthetic Data Generation Rate</p>
                <div className="w-full h-full border-2 border-dashed border-gray-700 rounded-md flex items-center justify-center">
                    <p className="text-gray-600">Data Rate Monitor</p>
                </div>
            </div>
        </div>

        {/* Right Panel: Controls & Logs */}
        <div className="bg-gray-800 p-4 rounded-lg shadow-lg flex flex-col space-y-4">
          <div>
            <h2 className="text-lg font-bold mb-2">Training Pipeline Control</h2>
            <div className="space-y-4 text-sm">
                <DatasetManager />
                <div>
                  <p className="font-semibold text-cyan-400 mb-2">Configuration</p>
                  <div className="space-y-1 bg-gray-900/50 p-2 rounded-md">
                    <p><span className="font-semibold text-gray-400">Curriculum:</span> Stage 3 - Adversarial Hardening</p>
                    <p><span className="font-semibold text-gray-400">Optimizer:</span> AdamW + Lookahead</p>
                  </div>
                </div>
            </div>
          </div>
          <div className="flex-grow flex flex-col">
            <h2 className="text-lg font-bold mb-2">Training Log</h2>
            <div className="flex-grow bg-black font-mono text-xs p-2 rounded-md overflow-y-auto">
                <p><span className="text-green-400">[INFO]</span> Epoch 42 started. Learning rate: 1e-5.</p>
                <p><span className="text-green-400">[INFO]</span> Step 1200/2500, Loss: 0.0138</p>
                <p><span className="text-yellow-400">[WARN]</span> Anomaly detected in dataset batch #8921. Confidence: 85%. Isolating...</p>
                <p><span className="text-green-400">[INFO]</span> Step 1201/2500, Loss: 0.0135</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgiTrainer;