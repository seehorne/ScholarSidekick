import React, { useState, useCallback, useRef, useEffect } from 'react';
import { CardData, Connection, CardCategory } from '../types';
import Card from './Card';
import { CARD_COLORS } from '../constants';

interface ResultsViewProps {
  initialCards: CardData[];
  transcript: string;
  meetingDate: string;
  onReset: () => void;
}

const ResultsView: React.FC<ResultsViewProps> = ({ initialCards, transcript, meetingDate, onReset }) => {
  const [cards, setCards] = useState<CardData[]>(initialCards);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [viewMode, setViewMode] = useState<'list' | 'workspace'>('workspace');
  const [connecting, setConnecting] = useState<{ fromId: string; fromHandlePos: { x: number; y: number } } | null>(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  const workspaceRef = useRef<HTMLDivElement>(null);
  const cardRefs = useRef<{ [key: string]: HTMLDivElement | null }>({});

  const updateCardPosition = useCallback((id: string, position: { x: number; y: number }) => {
    setCards(prev => prev.map(card => card.id === id ? { ...card, position } : card));
  }, []);
  
  const updateCardContent = useCallback((id: string, title: string, content: string) => {
    setCards(prev => prev.map(card => card.id === id ? { ...card, title, content } : card));
  }, []);

  const addNewCard = (category: CardCategory) => {
    let newX = 50;
    let newY = 50;
    
    if (workspaceRef.current) {
        const workspace = workspaceRef.current;
        const cardWidth = 288; // w-72 from Card.tsx
        const cardHeight = 224; // approx height
        newX = workspace.scrollLeft + (workspace.clientWidth / 2) - (cardWidth / 2);
        newY = workspace.scrollTop + (workspace.clientHeight / 2) - (cardHeight / 2);
    }

    const newCard: CardData = {
      id: `${category}-${Date.now()}`,
      category,
      title: `New ${category.split(' ')[0]}`,
      content: 'New item content...',
      position: { x: newX, y: newY },
      isAIGenerated: false,
    };
    setCards(prev => [...prev, newCard]);
  };

  const getHandlePosition = (cardId: string) => {
    const cardEl = cardRefs.current[cardId];
    const workspaceEl = workspaceRef.current;
    if (!cardEl || !workspaceEl) return { x: 0, y: 0, width: 0, height: 0 };
    
    const cardRect = cardEl.getBoundingClientRect();
    const workspaceRect = workspaceEl.getBoundingClientRect();
    
    return {
      x: cardRect.left - workspaceRect.left + cardRect.width,
      y: cardRect.top - workspaceRect.top + cardRect.height / 2,
      width: cardRect.width,
      height: cardRect.height,
    };
  };

  const handleStartConnection = (fromId: string) => {
    setConnecting({ fromId, fromHandlePos: getHandlePosition(fromId) });
  };
  
  const handleEndConnection = (toId: string) => {
    if (connecting && connecting.fromId !== toId) {
      setConnections(prev => [...prev, { fromId: connecting.fromId, toId }]);
    }
    setConnecting(null);
  };
  
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if(connecting && workspaceRef.current) {
        const rect = workspaceRef.current.getBoundingClientRect();
        setMousePos({ x: e.clientX - rect.left, y: e.clientY - rect.top });
      }
    };

    const handleMouseUp = () => {
      setConnecting(null);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [connecting]);
  
  const StarIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-yellow-500" viewBox="0 0 20 20" fill="currentColor">
      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
    </svg>
  );


  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-1/4 min-w-[300px] bg-white border-r border-gray-200 p-6 flex flex-col shadow-md">
        <div className="flex justify-between items-center mb-2">
          <h2 className="text-2xl font-bold text-gray-800">Extracted Items ✨</h2>
          <button onClick={onReset} className="text-sm text-purple-700 hover:text-purple-900 font-semibold">Start Over ↩️</button>
        </div>
        <p className="text-sm text-gray-500 mb-6">Meeting Date: {meetingDate}</p>
        
        <div className="mb-6">
            <div className="flex bg-gray-100 rounded-lg p-1">
                <button onClick={() => setViewMode('list')} className={`w-1/2 py-2 text-sm font-semibold rounded-md transition-colors ${viewMode === 'list' ? 'bg-white shadow text-purple-800' : 'text-gray-500'}`}>📜 Transcript</button>
                <button onClick={() => setViewMode('workspace')} className={`w-1/2 py-2 text-sm font-semibold rounded-md transition-colors ${viewMode === 'workspace' ? 'bg-white shadow text-purple-800' : 'text-gray-500'}`}>🎨 Workspace</button>
            </div>
        </div>

        <div className="flex-grow overflow-y-auto pr-2 -mr-2 space-y-4">
          {initialCards.map(card => (
            <div key={card.id} className={`${CARD_COLORS[card.category].bg} ${CARD_COLORS[card.category].border} p-3 rounded-lg border`}>
              <h3 className={`font-bold text-sm ${CARD_COLORS[card.category].title}`}>{card.title}</h3>
              <p className={`text-xs mt-1 ${CARD_COLORS[card.category].text}`}>{card.content}</p>
            </div>
          ))}
        </div>
        
        <div className="mt-auto pt-6 border-t border-gray-200">
            <h3 className="font-bold text-lg mb-4 text-gray-700">Add to Workspace ➕</h3>
            <div className="flex flex-col space-y-2">
                <button onClick={() => addNewCard(CardCategory.NOTE)} className="w-full text-left bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-2 px-4 rounded-lg transition-colors">
                    + Note 🗒️
                </button>
                <button onClick={() => addNewCard(CardCategory.TODO)} className="w-full text-left bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-2 px-4 rounded-lg transition-colors">
                    + TODO ✅
                </button>
                <button onClick={() => addNewCard(CardCategory.ROADBLOCK)} className="w-full text-left bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-2 px-4 rounded-lg transition-colors">
                    + Roadblock 🚧
                </button>
            </div>
             <div className="mt-6 p-4 bg-rose-500 rounded-lg text-sm text-white font-semibold text-center">
              <strong>AI-Generated Content:</strong> Please be aware that extracted items may contain inaccuracies. Always verify important information.
            </div>
        </div>

      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8 overflow-hidden">
        {viewMode === 'list' && (
          <div className="bg-white rounded-lg shadow p-8 h-full overflow-y-auto">
            <h1 className="text-3xl font-bold mb-6 text-gray-800">Meeting Transcript</h1>
            <pre className="whitespace-pre-wrap font-sans text-gray-700 leading-relaxed">{transcript}</pre>
          </div>
        )}

        {viewMode === 'workspace' && (
          <div ref={workspaceRef} className="relative w-full h-full bg-white rounded-lg shadow-inner border border-gray-200 overflow-auto" onClick={() => connecting && setConnecting(null)}>
            <div className="absolute top-4 left-4 text-gray-500 p-4 rounded-lg bg-white/80 backdrop-blur-sm z-20 pointer-events-none border border-gray-200">
                <h2 className="text-2xl font-bold text-gray-700">Workspace Canvas 🎨</h2>
                <p className="text-sm mt-1">Add items from the sidebar. You can move them around and draw connections between them.</p>
            </div>

            {/* SVG for connections */}
            <svg className="absolute top-0 left-0 w-full h-full pointer-events-none" style={{ minWidth: '2000px', minHeight: '2000px' }}>
              <defs>
                  <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                      <path d="M 0 0 L 10 5 L 0 10 z" fill="#9ca3af" />
                  </marker>
              </defs>
              {connections.map(({ fromId, toId }) => {
                const fromPos = getHandlePosition(fromId);
                const toPos = getHandlePosition(toId);
                const toCard = cards.find(c => c.id === toId);
                if (!toCard) return null;
                const toElPos = toCard.position;

                return <line key={`${fromId}-${toId}`} 
                  x1={fromPos.x} y1={fromPos.y} 
                  x2={toElPos.x} y2={toPos.y} 
                  stroke="#9ca3af" strokeWidth="2" markerEnd="url(#arrow)" />
              })}
              {connecting && (
                 <line x1={connecting.fromHandlePos.x} y1={connecting.fromHandlePos.y} x2={mousePos.x} y2={mousePos.y} stroke="#a855f7" strokeWidth="2" strokeDasharray="5,5" />
              )}
            </svg>

            {cards.map(card => (
              <Card
                key={card.id}
                ref={el => (cardRefs.current[card.id] = el)}
                cardData={card}
                onPosChange={updateCardPosition}
                onContentChange={updateCardContent}
                onStartConnection={handleStartConnection}
                onEndConnection={handleEndConnection}
              >
               {card.category === CardCategory.ROADBLOCK && <StarIcon />}
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default ResultsView;