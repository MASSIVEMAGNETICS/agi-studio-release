
import React, { useState, useRef, useEffect } from 'react';
import { ChevronDownIcon, SaveIcon } from './icons';

const FileMenu = () => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const menuItems = [
    { label: 'New Project', shortcut: 'Ctrl+N' },
    { label: 'Open...', shortcut: 'Ctrl+O' },
    { label: 'Save', shortcut: 'Ctrl+S', icon: <SaveIcon/> },
    { label: 'Save As...', shortcut: 'Ctrl+Shift+S' },
    { label: 'Save All', shortcut: 'Ctrl+Alt+S', highlight: true },
    { separator: true },
    { label: 'Export (All Formats)' },
    { separator: true },
    { label: 'One-click Backup' },
    { label: 'Manage Versions' },
    { separator: true },
    { label: 'Session Recovery' },
    { separator: true },
    { label: 'Exit' },
  ];

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center px-3 py-2 text-sm font-medium text-gray-300 bg-gray-900 hover:bg-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-cyan-500"
      >
        File
        <ChevronDownIcon />
      </button>

      {isOpen && (
        <div className="absolute left-0 mt-2 w-64 bg-gray-800 border border-gray-700 rounded-md shadow-lg py-1 z-50">
          {menuItems.map((item, index) => (
            item.separator ? <hr key={`sep-${index}`} className="border-t border-gray-700 my-1" /> : (
            <a
              key={item.label}
              href="#"
              className={`flex justify-between items-center px-4 py-2 text-sm text-gray-300 hover:bg-cyan-600 hover:text-white ${item.highlight ? 'text-cyan-400 font-bold' : ''}`}
            >
              <span className="flex items-center">{item.icon}{item.label}</span>
              {item.shortcut && <span className="text-gray-500 text-xs">{item.shortcut}</span>}
            </a>
          )))}
        </div>
      )}
    </div>
  );
};

export default FileMenu;
