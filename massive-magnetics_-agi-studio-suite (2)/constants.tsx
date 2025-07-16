
import React from 'react';
import { TabId, Tab } from './types';
import { 
    BrainCircuitIcon, TrainingIcon, LabIcon, TransformerIcon, 
    PipelineIcon, MemoryIcon, ConsoleIcon, PersonaIcon, 
    AnalyticsIcon, KnowledgeIcon 
} from './components/icons';

export const TABS: Tab[] = [
  { id: TabId.AGI_BUILDER, label: 'AGI Builder', icon: <BrainCircuitIcon /> },
  { id: TabId.AGI_TRAINER, label: 'AGI Trainer', icon: <TrainingIcon /> },
  { id: TabId.THE_LAB, label: 'The Lab', icon: <LabIcon /> },
  { id: TabId.TRANSFORMER_BUILDER, label: 'Transformer Builder', icon: <TransformerIcon /> },
  { id: TabId.PIPELINE_CREATOR, label: 'Pipeline Creator', icon: <PipelineIcon /> },
  { id: TabId.MEMORY_MAP, label: 'Memory Map', icon: <MemoryIcon /> },
  { id: TabId.DIRECTIVE_CONSOLE, label: 'Directive Console', icon: <ConsoleIcon /> },
  { id: TabId.PERSONA_DESIGNER, label: 'Persona Designer', icon: <PersonaIcon /> },
  { id: TabId.ANALYTICS, label: 'Analytics', icon: <AnalyticsIcon /> },
  { id: TabId.KNOWLEDGE_BASE, label: 'Knowledge Base', icon: <KnowledgeIcon /> },
];
