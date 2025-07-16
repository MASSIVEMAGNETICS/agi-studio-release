
import React, { useState, useRef, useEffect, useCallback } from 'react';
import { PlayIcon, StopIcon, RefreshIcon } from '../components/icons';

// --- TYPE DEFINITIONS ---
type NodeStatus = 'idle' | 'running' | 'success' | 'error';
type NodeExecutionState = {
    status: NodeStatus;
    output: string;
    log: string;
    file?: File;
};
interface NodeData extends NodeExecutionState {
    id: string;
    label: string;
    type: 'input' | 'core' | 'output' | 'custom';
    x: number;
    y: number;
}
interface Edge {
    id: string;
    from: string;
    to: string;
}
type Nodes = { [id: string]: NodeData };

// --- INITIAL STATE ---
const initialNodes: Nodes = {
  'node-1': { id: 'node-1', type: 'input', label: 'Sensory Input: Vision', x: 50, y: 150, status: 'idle', output: '1024x1024x3 @ 60fps', log: 'Initialized.' },
  'node-2': { id: 'node-2', type: 'core', label: 'Core: Fractal Cortex-A7', x: 400, y: 100, status: 'idle', output: 'Weights: 175B', log: 'Awaiting input...' },
  'node-3': { id: 'node-3', type: 'core', label: 'Core: Associative Memory', x: 400, y: 300, status: 'idle', output: 'Vector Store: 10T', log: 'Awaiting input...' },
  'node-4': { id: 'node-4', type: 'output', label: 'Output: Language Model', x: 750, y: 200, status: 'idle', output: 'GPT-5 Variant', log: 'Ready.' },
};
const initialEdges: Edge[] = [
  { id: 'e1-2', from: 'node-1', to: 'node-2' },
  { id: 'e1-3', from: 'node-1', to: 'node-3' },
  { id: 'e2-4', from: 'node-2', to: 'node-4' },
  { id: 'e3-4', from: 'node-3', to: 'node-4' },
];

// --- SUB-COMPONENTS ---

const FlowControls = ({ onRun, onStop, onReset, running }: { onRun: () => void, onStop: () => void, onReset: () => void, running: boolean }) => (
    <div className="flex gap-2 p-2 bg-gray-900/80 border border-gray-700 rounded-lg shadow-xl fixed top-20 right-6 z-50 backdrop-blur-sm">
        <button onClick={onRun} disabled={running} className="flex items-center gap-2 px-4 py-2 text-sm font-bold text-white bg-green-600 hover:bg-green-500 rounded-md disabled:bg-gray-600 disabled:cursor-not-allowed transition-all">
            <PlayIcon className="w-5 h-5" /> RUN PIPELINE
        </button>
        <button onClick={onStop} disabled={!running} className="flex items-center gap-2 px-4 py-2 text-sm font-bold text-white bg-red-600 hover:bg-red-500 rounded-md disabled:bg-gray-600 disabled:cursor-not-allowed transition-all">
            <StopIcon className="w-5 h-5" /> STOP
        </button>
        <button onClick={onReset} className="flex items-center gap-2 p-2 text-sm font-bold text-gray-300 hover:bg-gray-700 rounded-md transition-all">
            <RefreshIcon className="w-5 h-5" />
        </button>
    </div>
);

const NodeComponent = React.memo(({ data, onMove, onFileLoad, onRun, onStop, onContextMenu, onMouseDown, isSelected }: { data: NodeData, onMove: (id: string, x: number, y: number) => void, onFileLoad: (id: string, file: File) => void, onRun: (id: string) => void, onStop: (id: string) => void, onContextMenu: (e: React.MouseEvent, nodeId: string) => void, onMouseDown: (e: React.MouseEvent, nodeId: string) => void, isSelected: boolean }) => {
    const nodeRef = useRef<HTMLDivElement>(null);
    const typeColor = {
        input: 'border-blue-500',
        core: 'border-purple-500',
        output: 'border-green-500',
        custom: 'border-amber-500'
    };
    const statusColor = {
        idle: 'bg-gray-500',
        running: 'bg-cyan-500 animate-pulse',
        success: 'bg-green-500',
        error: 'bg-red-500'
    };

    return (
        <div
            ref={nodeRef}
            className={`absolute bg-gray-800 rounded-lg shadow-2xl border-2 ${typeColor[data.type]} ${isSelected ? 'ring-2 ring-cyan-400 ring-offset-4 ring-offset-gray-900' : ''} transition-all duration-150`}
            style={{ left: data.x, top: data.y, width: 280 }}
            onMouseDown={(e) => onMouseDown(e, data.id)}
            onContextMenu={(e) => onContextMenu(e, data.id)}
        >
            <div className="flex justify-between items-center p-2 bg-gray-900 rounded-t-md">
                <span className="font-bold text-sm text-white truncate">{data.label}</span>
                <span className={`px-2 py-0.5 rounded-full text-xs font-mono text-white ${statusColor[data.status]}`}>
                    {data.status.toUpperCase()}
                </span>
            </div>
            <div className="p-3 space-y-2">
                <div className="flex gap-1">
                    <input
                        type="file"
                        id={`file-${data.id}`}
                        onChange={e => e.target.files && onFileLoad(data.id, e.target.files[0])}
                        className="hidden"
                    />
                    <label htmlFor={`file-${data.id}`} className="flex-grow text-center text-xs bg-gray-700 hover:bg-gray-600 p-1 rounded-md cursor-pointer truncate">
                        {data.file ? data.file.name : 'Load File...'}
                    </label>
                </div>
                <div className="flex gap-1">
                    <button onClick={() => onRun(data.id)} disabled={data.status === 'running'} className="w-1/2 text-xs bg-gray-700 hover:bg-green-600 disabled:bg-gray-600/50 p-1 rounded-md">Run Node</button>
                    <button onClick={() => onStop(data.id)} disabled={data.status !== 'running'} className="w-1/2 text-xs bg-gray-700 hover:bg-red-600 disabled:bg-gray-600/50 p-1 rounded-md">Stop Node</button>
                </div>
                <div className="text-xs bg-black p-2 rounded max-h-20 overflow-y-auto font-mono">
                    <b className="text-cyan-400">Output:</b> <span className="text-gray-300">{data.output}</span>
                </div>
                <div className="text-xs text-gray-400 bg-black p-2 rounded max-h-20 overflow-y-auto font-mono">
                    <b className="text-yellow-400">Log:</b> <span className="text-gray-300">{data.log}</span>
                </div>
            </div>
        </div>
    );
});

// --- MAIN COMPONENT ---
const AgiBuilder = () => {
    const [nodes, setNodes] = useState<Nodes>(initialNodes);
    const [edges, setEdges] = useState<Edge[]>(initialEdges);
    const [transform, setTransform] = useState({ x: 0, y: 0, scale: 1 });
    const [pipelineStatus, setPipelineStatus] = useState<'idle' | 'running'>('idle');
    const [contextMenu, setContextMenu] = useState<{ x: number, y: number, nodeId: string } | null>(null);

    const canvasRef = useRef<HTMLDivElement>(null);
    const dragInfo = useRef<{ activeNodeId: string | null, startX: number, startY: number, isPanning: boolean, panStartX: number, panStartY: number }>({ activeNodeId: null, startX: 0, startY: 0, isPanning: false, panStartX: 0, panStartY: 0 });

    const handleWheel = (e: React.WheelEvent) => {
        e.preventDefault();
        const scaleAmount = -e.deltaY * 0.001;
        const newScale = Math.min(Math.max(0.2, transform.scale + scaleAmount), 2);
        
        const rect = canvasRef.current!.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        
        const newX = transform.x + (mouseX - transform.x) * (1 - newScale / transform.scale);
        const newY = transform.y + (mouseY - transform.y) * (1 - newScale / transform.scale);

        setTransform({ x: newX, y: newY, scale: newScale });
    };

    const handleMouseDown = useCallback((e: React.MouseEvent, nodeId?: string) => {
        if (nodeId) {
            dragInfo.current = { ...dragInfo.current, activeNodeId: nodeId, startX: e.clientX, startY: e.clientY };
        } else if (e.button === 0) { // Left-click on canvas
            dragInfo.current = { ...dragInfo.current, isPanning: true, panStartX: e.clientX - transform.x, panStartY: e.clientY - transform.y };
        }
        setContextMenu(null);
    }, [transform.x, transform.y]);

    const handleMouseMove = useCallback((e: React.MouseEvent) => {
        const { activeNodeId, startX, startY, isPanning, panStartX, panStartY } = dragInfo.current;
        if (activeNodeId) {
            const dx = (e.clientX - startX) / transform.scale;
            const dy = (e.clientY - startY) / transform.scale;
            
            setNodes(prevNodes => {
                const node = prevNodes[activeNodeId];
                return { ...prevNodes, [activeNodeId]: { ...node, x: node.x + dx, y: node.y + dy } };
            });
            dragInfo.current.startX = e.clientX;
            dragInfo.current.startY = e.clientY;

        } else if (isPanning) {
            const newX = e.clientX - panStartX;
            const newY = e.clientY - panStartY;
            setTransform(prev => ({ ...prev, x: newX, y: newY }));
        }
    }, [transform.scale]);

    const handleMouseUp = useCallback(() => {
        dragInfo.current.activeNodeId = null;
        dragInfo.current.isPanning = false;
    }, []);

    useEffect(() => {
        const up = (e: MouseEvent) => handleMouseUp();
        const move = (e: MouseEvent) => handleMouseMove(e as any);
        window.addEventListener('mouseup', up);
        window.addEventListener('mousemove', move);
        return () => {
            window.removeEventListener('mouseup', up);
            window.removeEventListener('mousemove', move);
        }
    }, [handleMouseUp, handleMouseMove]);
    
    // Node/Pipeline actions
    const updateNodeState = (id: string, updates: Partial<NodeExecutionState>) => {
        setNodes(prev => ({ ...prev, [id]: { ...prev[id], ...updates } }));
    };

    const runNode = (id: string) => {
        updateNodeState(id, { status: 'running', log: 'Execution started...' });
        setTimeout(() => {
            const success = Math.random() > 0.2;
            updateNodeState(id, {
                status: success ? 'success' : 'error',
                output: success ? `Result: ${Math.random().toFixed(4)}` : 'Execution Failed',
                log: success ? 'Completed successfully.' : 'Error: Tensor mismatch.'
            });
        }, 2000 + Math.random() * 2000);
    };

    const stopNode = (id: string) => updateNodeState(id, { status: 'idle', log: 'Execution stopped by user.' });
    
    const runPipeline = () => {
        setPipelineStatus('running');
        Object.keys(nodes).forEach((id, index) => {
            setTimeout(() => runNode(id), index * 300);
        });
        setTimeout(() => setPipelineStatus('idle'), Object.keys(nodes).length * 300 + 3000);
    };

    const stopPipeline = () => {
        setPipelineStatus('idle');
        Object.keys(nodes).forEach(id => stopNode(id));
    };

    const resetPipeline = () => {
        setNodes(prev => {
            const newNodes = { ...prev };
            Object.keys(newNodes).forEach(id => {
                newNodes[id] = { ...newNodes[id], status: 'idle', output: 'N/A', log: 'Reset.' };
            });
            return newNodes;
        });
    };
    
    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        const nodeType = e.dataTransfer.getData('application/node-type');
        if (!nodeType || !canvasRef.current) return;
        
        const rect = canvasRef.current.getBoundingClientRect();
        const x = (e.clientX - rect.left - transform.x) / transform.scale;
        const y = (e.clientY - rect.top - transform.y) / transform.scale;
        
        const newNodeId = `node-${Date.now()}`;
        const newNode: NodeData = {
            id: newNodeId,
            label: `${nodeType} Node`,
            type: 'custom',
            x,
            y,
            status: 'idle',
            output: 'Newly added',
            log: 'Awaiting configuration'
        };
        setNodes(prev => ({ ...prev, [newNodeId]: newNode }));
    };

    const handleContextMenu = (e: React.MouseEvent, nodeId: string) => {
        e.preventDefault();
        e.stopPropagation();
        setContextMenu({ x: e.clientX, y: e.clientY, nodeId });
    };

    const deleteNode = (nodeId: string) => {
        setNodes(prev => {
            const newNodes = { ...prev };
            delete newNodes[nodeId];
            return newNodes;
        });
        setEdges(prev => prev.filter(edge => edge.from !== nodeId && edge.to !== nodeId));
        setContextMenu(null);
    };

    const duplicateNode = (nodeId: string) => {
        const original = nodes[nodeId];
        const newId = `node-${Date.now()}`;
        const newNode: NodeData = {
            ...original,
            id: newId,
            x: original.x + 30,
            y: original.y + 30,
            status: 'idle',
            log: 'Duplicated from ' + original.label,
        };
        setNodes(prev => ({ ...prev, [newId]: newNode }));
        setContextMenu(null);
    };
    
    const exportGraph = () => {
        const data = JSON.stringify({ nodes, edges }, null, 2);
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'agi-graph.json';
        a.click();
        URL.revokeObjectURL(url);
    };
    
    const importGraph = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const { nodes: importedNodes, edges: importedEdges } = JSON.parse(event.target?.result as string);
                setNodes(importedNodes);
                setEdges(importedEdges);
            } catch (err) {
                alert("Failed to import graph: Invalid file format.");
            }
        };
        reader.readAsText(file);
    };


  return (
    <div className="h-full w-full flex bg-gray-900 text-white overflow-hidden">
      {/* Sidebar */}
      <div className="w-72 bg-gray-800 p-4 border-r border-gray-700 flex flex-col z-20">
        <h2 className="text-lg font-bold mb-4 text-cyan-400">Node Library</h2>
        <div className="space-y-2">
            {['Core Logic', 'Memory', 'Sensory Input', 'Actuator Output', 'Custom Layer'].map(item => (
                <div key={item} className="bg-gray-700 p-3 rounded-md cursor-grab active:cursor-grabbing hover:bg-gray-600 transition-colors" draggable onDragStart={(e) => e.dataTransfer.setData('application/node-type', item)}>
                    <p className="font-semibold">{item}</p>
                </div>
            ))}
        </div>
        <hr className="my-4 border-gray-600" />
        <h2 className="text-lg font-bold mb-4 text-cyan-400">Graph Actions</h2>
        <div className="space-y-2">
            <button onClick={exportGraph} className="w-full text-center text-sm bg-gray-700 hover:bg-cyan-600 p-2 rounded-md">Export Graph</button>
            <input type="file" id="import-graph" className="hidden" onChange={importGraph} accept=".json" />
            <label htmlFor="import-graph" className="block w-full text-center text-sm bg-gray-700 hover:bg-cyan-600 p-2 rounded-md cursor-pointer">Import Graph</label>
        </div>
      </div>
      
      {/* Main Canvas */}
      <div ref={canvasRef} className="flex-1 relative overflow-hidden bg-gray-900" onWheel={handleWheel} onMouseDown={(e) => handleMouseDown(e)} onDrop={handleDrop} onDragOver={e => e.preventDefault()}>
        <div className="absolute inset-0 bg-[radial-gradient(#374151_1px,transparent_1px)] [background-size:32px_32px]" style={{ transform: `translate(${transform.x}px, ${transform.y}px) scale(${transform.scale})` }}></div>
        <FlowControls onRun={runPipeline} onStop={stopPipeline} onReset={resetPipeline} running={pipelineStatus === 'running'} />
        <svg className="absolute w-full h-full pointer-events-none" style={{ transform: `translate(${transform.x}px, ${transform.y}px) scale(${transform.scale})` }}>
            <defs>
                <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                    <path d="M 0 0 L 10 5 L 0 10 z" fill="#6b7280" />
                </marker>
            </defs>
            {edges.map(edge => {
                const fromNode = nodes[edge.from];
                const toNode = nodes[edge.to];
                if (!fromNode || !toNode) return null;
                const startX = fromNode.x + 280; // node width
                const startY = fromNode.y + 75; // approx half height
                const endX = toNode.x;
                const endY = toNode.y + 75;
                const d = `M ${startX} ${startY} C ${startX + 100} ${startY}, ${endX - 100} ${endY}, ${endX} ${endY}`;
                return <path key={edge.id} d={d} stroke="#6b7280" strokeWidth="3" fill="none" markerEnd="url(#arrow)" />;
            })}
        </svg>

        <div className="absolute top-0 left-0 w-full h-full pointer-events-none" style={{ transform: `translate(${transform.x}px, ${transform.y}px) scale(${transform.scale})` }}>
            {Object.values(nodes).map(node => (
                <div key={node.id} className="pointer-events-auto">
                    <NodeComponent 
                        data={node} 
                        onMove={() => {}} 
                        onFileLoad={(id, file) => updateNodeState(id, { file })}
                        onRun={runNode}
                        onStop={stopNode}
                        onContextMenu={handleContextMenu}
                        onMouseDown={handleMouseDown}
                        isSelected={dragInfo.current.activeNodeId === node.id}
                    />
                </div>
            ))}
        </div>
         {contextMenu && (
            <div
                className="absolute bg-gray-800 border border-gray-600 rounded-md shadow-lg py-1 z-50 text-sm"
                style={{ top: contextMenu.y, left: contextMenu.x }}
            >
                <button onClick={() => duplicateNode(contextMenu.nodeId)} className="block w-full text-left px-4 py-2 text-gray-300 hover:bg-cyan-600">Duplicate</button>
                <button onClick={() => deleteNode(contextMenu.nodeId)} className="block w-full text-left px-4 py-2 text-red-400 hover:bg-red-600 hover:text-white">Delete</button>
            </div>
        )}
      </div>
    </div>
  );
};

export default AgiBuilder;
