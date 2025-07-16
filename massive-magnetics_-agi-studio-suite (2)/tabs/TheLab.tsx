
import React from 'react';

const LabPanel = ({ title, children }: { title: string, children: React.ReactNode }) => (
    <div className="bg-gray-800 rounded-lg shadow-lg flex flex-col h-full">
        <h2 className="text-md font-bold p-3 bg-gray-700 rounded-t-lg text-cyan-400">{title}</h2>
        <div className="p-4 flex-grow overflow-y-auto">
            {children}
        </div>
    </div>
);

const TheLab = () => {
    return (
        <div className="h-full w-full grid grid-cols-1 lg:grid-cols-3 grid-rows-2 gap-4 p-4 bg-gray-900">
            <div className="lg:col-span-2 row-span-2">
                <LabPanel title="Live Experiment: Agent-to-Agent Combat (Sim #42)">
                    <div className="w-full h-full border-2 border-dashed border-gray-700 rounded-md flex items-center justify-center relative bg-gray-900">
                        <p className="text-gray-600 text-lg">3D Combat Simulation Visualization</p>
                        <div className="absolute top-2 left-2 text-xs">
                            <span className="bg-red-500 px-2 py-1 rounded">Agent 'Loki'</span> vs <span className="bg-blue-500 px-2 py-1 rounded">Agent 'Athena'</span>
                        </div>
                    </div>
                </LabPanel>
            </div>
            
            <div className="row-span-1">
                <LabPanel title="Prompt Engineering">
                    <textarea 
                        className="w-full h-full bg-black font-mono text-sm p-2 rounded-md border border-gray-600 focus:ring-cyan-500 focus:border-cyan-500"
                        defaultValue="Directive: Analyze the combat simulation. Identify novel evasion tactics employed by Agent 'Loki' and formulate a counter-strategy for Agent 'Athena'. Output in JSON format."
                    />
                </LabPanel>
            </div>

            <div className="row-span-1">
                <LabPanel title="Adversarial Attacks & Stress Tests">
                    <ul className="space-y-2">
                        <li className="flex justify-between items-center p-2 bg-gray-700 rounded hover:bg-gray-600">
                            <span>Conceptual Jailbreak</span>
                            <button className="text-xs bg-red-600 px-2 py-1 rounded">RUN</button>
                        </li>
                        <li className="flex justify-between items-center p-2 bg-gray-700 rounded hover:bg-gray-600">
                            <span>Recursive Memory Overload</span>
                            <button className="text-xs bg-red-600 px-2 py-1 rounded">RUN</button>
                        </li>
                        <li className="flex justify-between items-center p-2 bg-gray-700 rounded hover:bg-gray-600">
                            <span>Multiverse Contradiction Test</span>
                            <button className="text-xs bg-yellow-500 px-2 py-1 rounded">QUEUED</button>
                        </li>
                    </ul>
                </LabPanel>
            </div>
        </div>
    );
};

export default TheLab;
