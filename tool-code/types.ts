export enum CardCategory {
  TLDR = 'TL;DR 📝',
  TODO = 'TODO ✅',
  REFLECTION = 'Reflection 🤔',
  UNADDRESSED = 'Unaddressed 📌',
  NOTE = 'Note 🗒️',
  ROADBLOCK = 'Roadblock 🚧',
}

export interface CardData {
  id: string;
  category: CardCategory;
  title: string;
  content: string;
  position: { x: number; y: number };
  isAIGenerated: boolean;
}

export interface Connection {
  fromId: string;
  toId: string;
}

export type View = 'input' | 'results';