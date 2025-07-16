
import React from 'react';

export enum TabId {
  AGI_BUILDER,
  AGI_TRAINER,
  THE_LAB,
  TRANSFORMER_BUILDER,
  PIPELINE_CREATOR,
  MEMORY_MAP,
  DIRECTIVE_CONSOLE,
  PERSONA_DESIGNER,
  ANALYTICS,
  KNOWLEDGE_BASE,
}

export interface Tab {
  id: TabId;
  label: string;
  icon: React.ReactNode;
}
