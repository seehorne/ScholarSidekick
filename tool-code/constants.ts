import { CardCategory } from './types';

export const CARD_COLORS: { [key in CardCategory]: { bg: string; border: string; text: string; title: string; tagBg: string; tagText: string } } = {
  [CardCategory.TLDR]: {
    bg: 'bg-purple-100',
    border: 'border-purple-300',
    text: 'text-purple-800',
    title: 'text-purple-900',
    tagBg: 'bg-purple-200',
    tagText: 'text-purple-900',
  },
  [CardCategory.TODO]: {
    bg: 'bg-green-100',
    border: 'border-green-300',
    text: 'text-green-800',
    title: 'text-green-900',
    tagBg: 'bg-green-200',
    tagText: 'text-green-900',
  },
  [CardCategory.REFLECTION]: {
    bg: 'bg-sky-100',
    border: 'border-sky-300',
    text: 'text-sky-800',
    title: 'text-sky-900',
    tagBg: 'bg-sky-200',
    tagText: 'text-sky-900',
  },
  [CardCategory.UNADDRESSED]: {
    bg: 'bg-red-100',
    border: 'border-red-300',
    text: 'text-red-800',
    title: 'text-red-900',
    tagBg: 'bg-red-200',
    tagText: 'text-red-900',
  },
  [CardCategory.NOTE]: {
    bg: 'bg-sky-100',
    border: 'border-sky-300',
    text: 'text-sky-800',
    title: 'text-sky-900',
    tagBg: 'bg-sky-200',
    tagText: 'text-sky-900',
  },
  [CardCategory.ROADBLOCK]: {
    bg: 'bg-orange-100',
    border: 'border-orange-300',
    text: 'text-orange-800',
    title: 'text-orange-900',
    tagBg: 'bg-orange-200',
    tagText: 'text-orange-900',
  },
};