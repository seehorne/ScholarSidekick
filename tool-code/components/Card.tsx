import React, { useState, useRef, useEffect, forwardRef, useImperativeHandle } from 'react';
import { CardData, CardCategory } from '../types';
import { CARD_COLORS } from '../constants';

interface CardProps {
  cardData: CardData;
  onPosChange: (id: string, newPos: { x: number; y: number }) => void;
  onContentChange: (id: string, title: string, content: string) => void;
  onStartConnection: (fromId: string) => void;
  onEndConnection: (toId: string) => void;
  onDelete?: (id: string) => void;
  children?: React.ReactNode;
}

const Card = forwardRef<HTMLDivElement, CardProps>(({ 
  cardData, 
  onPosChange, 
  onContentChange, 
  onStartConnection, 
  onEndConnection,
  onDelete,
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
  
  // Extract hashtags from content
  const extractHashtags = (text: string): string[] => {
    const hashtagRegex = /#[\w]+/g;
    const matches = text.match(hashtagRegex);
    return matches ? [...new Set(matches)] : []; // Remove duplicates
  };
  
  // Extract deadline from content (reads from "Deadline:" or "Due:" until period)
  const extractDeadline = (text: string): string | null => {
    // Match "Deadline:" or "Due:" (case insensitive) followed by text until a period
    const pattern = /(?:deadline|due):\s*([^.]+)\./i;
    const match = text.match(pattern);
    if (match) {
      return match[1].trim();
    }
    
    // Fallback: try "by DATE" pattern
    const byPattern = /\bby\s+([^.]+)\./i;
    const byMatch = text.match(byPattern);
    if (byMatch) {
      return byMatch[1].trim();
    }
    
    return null;
  };
  
  const hashtags = extractHashtags(localContent);
  const extractedDeadline = extractDeadline(localContent);
  const deadline = cardData.deadline || extractedDeadline;
  
  const colors = CARD_COLORS[category];
  
  // Calculate minimum height based on content
  const hasDeadline = !!deadline;
  const hasHashtags = hashtags.length > 0;
  let minHeight = 220;
  if (hasDeadline) minHeight += 30; // Add space for deadline banner
  if (hasHashtags) minHeight += 20; // Add space for hashtags

  return (
    <div
      ref={cardRef}
      className={`absolute w-72 rounded-xl shadow-lg border-2 flex flex-col ${colors.bg} ${colors.border} transition-shadow hover:shadow-2xl`}
      style={{ cursor: 'default', position: 'absolute', minHeight: `${minHeight}px`, overflow: 'visible' }}
      onMouseUp={() => onEndConnection(id)}
    >
      {/* Deadline banner at the very top - outside padding */}
      {deadline && (
        <div className="px-3 py-1.5 bg-red-500 text-white rounded-t-xl overflow-hidden">
          <div className="flex items-center gap-1.5">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
            </svg>
            <span className="text-xs font-bold">Due: {deadline}</span>
          </div>
        </div>
      )}
      
      <div className="p-4 pb-3 flex-grow flex flex-col">
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
        <div className="flex items-start gap-1 pl-2 pt-1">
          {onDelete && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(id);
              }}
              className="text-gray-400 hover:text-red-500 transition-colors p-1"
              title="Delete card"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </button>
          )}
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
      
      {/* Hashtags */}
      {hashtags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-3 mb-1">
          {hashtags.map((tag, index) => (
            <span 
              key={index}
              className="text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 border border-blue-300"
            >
              {tag}
            </span>
          ))}
        </div>
      )}
      
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
    </div>
  );
});

export default Card;