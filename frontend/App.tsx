
import React, { useState } from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import AgiBuilder from './tabs/AgiBuilder';
import AgiTrainer from './tabs/AgiTrainer';
import TheLab from './tabs/TheLab';
import { 
    TransformerBuilder, PipelineCreator, MemoryMap, DirectiveConsole, 
    PersonaDesigner, Analytics, KnowledgeBase 
} from './tabs/OtherTabs';
import { TabId } from './types';
import { TABS } from './constants';

const App = () => {
  const [activeTab, setActiveTab] = useState<TabId>(TABS[0].id);

  const renderActiveTab = () => {
    switch (activeTab) {
      case TabId.AGI_BUILDER:
        return <AgiBuilder />;
      case TabId.AGI_TRAINER:
        return <AgiTrainer />;
      case TabId.THE_LAB:
        return <TheLab />;
      case TabId.TRANSFORMER_BUILDER:
        return <TransformerBuilder />;
      case TabId.PIPELINE_CREATOR:
        return <PipelineCreator />;
      case TabId.MEMORY_MAP:
        return <MemoryMap />;
      case TabId.DIRECTIVE_CONSOLE:
        return <DirectiveConsole />;
      case TabId.PERSONA_DESIGNER:
        return <PersonaDesigner />;
      case TabId.ANALYTICS:
        return <Analytics />;
      case TabId.KNOWLEDGE_BASE:
        return <KnowledgeBase />;
      default:
        return <div className="p-8">Select a tab</div>;
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-gray-200">
      <Header activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="flex-1 overflow-hidden">
        {renderActiveTab()}
      </main>
      <Footer />
    </div>
  );
};

export default App;
