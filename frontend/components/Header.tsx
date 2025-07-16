
import React from 'react';
import FileMenu from './FileMenu';
import { TabId, Tab } from '../types';
import { TABS } from '../constants';
import { UserCircleIcon, PlusIcon } from './icons';

interface HeaderProps {
  activeTab: TabId;
  setActiveTab: (tab: TabId) => void;
}

const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab }) => {
  return (
    <header className="bg-gray-800 border-b border-gray-700 shadow-md sticky top-0 z-40">
      <div className="px-2 sm:px-4">
        <div className="flex items-center justify-between h-16">
          {/* Left Section: File Menu and Project Title */}
          <div className="flex items-center space-x-4">
            <FileMenu />
            <div className="hidden md:block">
              <span className="text-gray-500">Project:</span>
              <span className="font-semibold text-white ml-2">AGI_Omega_v7</span>
            </div>
          </div>

          {/* Center Section: Tab System */}
          <div className="flex-1 min-w-0 flex justify-center items-center">
             <div className="flex items-center space-x-1 overflow-x-auto pb-1">
              {TABS.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center px-3 py-2 text-xs sm:text-sm font-medium rounded-t-lg border-b-2 whitespace-nowrap transition-colors duration-150
                    ${activeTab === tab.id
                      ? 'border-cyan-400 text-white bg-gray-900'
                      : 'border-transparent text-gray-400 hover:text-white hover:bg-gray-700'
                    }`}
                  title={tab.label}
                >
                  {tab.icon}
                  <span className="hidden lg:inline">{tab.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Right Section: Collaboration and User */}
          <div className="flex items-center space-x-4">
             <div className="flex items-center -space-x-2">
                 <UserCircleIcon className="h-8 w-8 text-indigo-400 rounded-full ring-2 ring-gray-800" />
                 <UserCircleIcon className="h-8 w-8 text-teal-400 rounded-full ring-2 ring-gray-800" />
                 <div className="h-8 w-8 rounded-full bg-gray-700 flex items-center justify-center ring-2 ring-gray-800 cursor-pointer hover:bg-gray-600">
                    <PlusIcon />
                 </div>
             </div>
             <div className="w-px h-8 bg-gray-700"></div>
             <button className="flex items-center">
                <span className="text-sm font-medium text-white hidden sm:block">Operator-01</span>
                <UserCircleIcon className="h-8 w-8 text-gray-300 ml-2"/>
             </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
