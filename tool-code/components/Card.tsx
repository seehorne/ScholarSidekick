import React, { useState, useRef, useEffect, forwardRef, useImperativeHandle } from 'react';
import { CardData, CardCategory } from '../types';
import { CARD_COLORS } from '../constants';

interface CardProps {
  cardData: CardData;
  onPosChange: (id: string, newPos: { x: number; y: number }) => void;
  onContentChange: (id: string, title: string, content: string) => void;
  onStartConnection: (fromId: string) => void;
  onEndConnection: (toId: string) => void;
  children?: React.ReactNode;
}

const Card = forwardRef<HTMLDivElement, CardProps>(({ 
  cardData, 
  onPosChange, 
  onContentChange, 
  onStartConnection, 
  onEndConnection,
  children 
}, ref) => {
  const { id, category, title, content, position, isAIGenerated } = cardData;
  const cardRef = useRef<HTMLDivElement>(null);
  const dragInfo = useRef({ isDragging: false, startX: 0, startY: 0, initialX: 0, initialY: 0 });

  const [localTitle, setLocalTitle] = useState(title);
  const [localContent, setLocalContent] = useState(content);

  useImperativeHandle(ref, () => cardRef.current!);
  
  const handleMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    // Prevent drag on input/textarea focus
    if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
    }
    dragInfo.current = {
      isDragging: true,
      startX: e.clientX,
      startY: e.clientY,
      initialX: position.x,
      initialY: position.y,
    };
    e.stopPropagation();
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!dragInfo.current.isDragging || !cardRef.current) return;
      const dx = e.clientX - dragInfo.current.startX;
      const dy = e.clientY - dragInfo.current.startY;
      const newX = dragInfo.current.initialX + dx;
      const newY = dragInfo.current.initialY + dy;
      cardRef.current.style.transform = `translate(${newX}px, ${newY}px)`;
    };

    const handleMouseUp = (e: MouseEvent) => {
      if (!dragInfo.current.isDragging) return;
      const dx = e.clientX - dragInfo.current.startX;
      const dy = e.clientY - dragInfo.current.startY;
      onPosChange(id, { x: dragInfo.current.initialX + dx, y: dragInfo.current.initialY + dy });
      dragInfo.current.isDragging = false;
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    
    if (cardRef.current) {
        cardRef.current.style.transform = `translate(${position.x}px, ${position.y}px)`;
        cardRef.current.style.left = `0px`;
        cardRef.current.style.top = `0px`;
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [id, onPosChange, position.x, position.y]);

  const handleContentBlur = () => {
    onContentChange(id, localTitle, localContent);
  };
  
  const colors = CARD_COLORS[category];

  return (
    <div
      ref={cardRef}
      className={`absolute w-72 p-4 rounded-xl shadow-lg border-2 flex flex-col ${colors.bg} ${colors.border} transition-shadow hover:shadow-2xl`}
      style={{ cursor: 'default', position: 'absolute' }}
      onMouseUp={() => onEndConnection(id)}
    >
      <div 
        className="card-header flex justify-between items-start pb-2 cursor-move"
        onMouseDown={handleMouseDown}
      >
        <div className="flex-grow">
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <span className={`text-xs font-semibold px-2 py-1 rounded-full ${colors.tagBg} ${colors.tagText}`}>
              {category}
            </span>
            {isAIGenerated && (
              <span className="text-xs font-semibold px-2 py-1 rounded-full bg-gray-200 text-gray-700">
                AI Generated
              </span>
            )}
          </div>
          <input 
            type="text"
            value={localTitle}
            onChange={(e) => setLocalTitle(e.target.value)}
            onBlur={handleContentBlur}
            className={`bg-white border-2 border-dotted border-gray-400 rounded-md px-2 py-1 w-full font-bold text-lg ${colors.title} focus:ring-1 focus:ring-purple-400 focus:outline-none`}
            onMouseDown={(e) => e.stopPropagation()}
          />
        </div>
        <div className="pl-2 pt-1">
          {children}
        </div>
      </div>

      <textarea
        value={localContent}
        onChange={(e) => setLocalContent(e.target.value)}
        onBlur={handleContentBlur}
        className={`bg-white border-2 border-dotted border-gray-400 rounded-md p-2 mt-2 w-full h-24 text-sm resize-y ${colors.text} focus:ring-1 focus:ring-purple-400 focus:outline-none`}
        onMouseDown={(e) => e.stopPropagation()}
      />
      
      <div 
        className="absolute -right-1.5 top-1/2 -translate-y-1/2 w-3 h-3 bg-white border-2 border-gray-400 rounded-full cursor-pointer hover:bg-purple-300 hover:border-purple-500 z-50"
        onMouseDown={(e) => {
            e.stopPropagation();
            e.preventDefault();
            onStartConnection(id);
        }}
        style={{ pointerEvents: 'auto' }}
      />
    </div>
  );
});

export default Card;