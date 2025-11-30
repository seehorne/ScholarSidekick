import React, { useState, useCallback } from 'react';
import { GoogleGenAI, Type } from "@google/genai";
import { View, CardData, CardCategory, Connection } from './types';
import InputView from './components/InputView';
import ResultsView from './components/ResultsView';
import ApiKeyInput from './components/ApiKeyInput';
import { extractMeetingItems } from './services/geminiService';

const App: React.FC = () => {
  const [view, setView] = useState<View>('input');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const [apiKey, setApiKey] = useState<string>('');
  const [isApiKeySet, setIsApiKeySet] = useState<boolean>(false);

  const [transcript, setTranscript] = useState<string>('');
  const [agenda, setAgenda] = useState<string>('');
  const [meetingDate, setMeetingDate] = useState<string>(new Date().toISOString().split('T')[0]);


  const [cards, setCards] = useState<CardData[]>([]);
  const [connections, setConnections] = useState<Connection[]>([]);

  const handleExtract = useCallback(async () => {
    if (!apiKey) {
      setError('API Key is missing. Please set your API key.');
      setIsApiKeySet(false);
      return;
    }
    if (!transcript.trim()) {
      setError('Meeting transcript cannot be empty.');
      return;
    }
    setIsLoading(true);
    setError(null);

    try {
      const extractedData = await extractMeetingItems(transcript, agenda, apiKey);
      
      const newCards: CardData[] = [];
      let yOffset = 140; // Increased Y-offset to avoid overlap with header

      const createCard = (category: CardCategory, title: string, content: string) => {
        const card: CardData = {
          id: `${category}-${Date.now()}-${Math.random()}`,
          category,
          title,
          content,
          position: { x: 20, y: yOffset },
          isAIGenerated: true,
        };
        yOffset += 280; // Increased spacing for cards to accommodate deadlines + hashtags
        return card;
      };

      if (extractedData.tldr) {
        newCards.push(createCard(CardCategory.TLDR, extractedData.tldr.title, extractedData.tldr.content));
      }
      
      if (extractedData.todos?.length > 0) {
        extractedData.todos.forEach(item => {
          newCards.push(createCard(CardCategory.TODO, item.title, item.content));
        });
      } else {
         newCards.push(createCard(CardCategory.TODO, 'No TODOs Found', 'No specific action items were identified in the transcript.'));
      }

      extractedData.reflections?.forEach(item => {
        newCards.push(createCard(CardCategory.REFLECTION, item.title, item.content));
      });

      if (extractedData.unaddressed?.length > 0) {
        extractedData.unaddressed.forEach(item => {
          newCards.push(createCard(CardCategory.UNADDRESSED, item.title, item.content));
        });
      } else {
        newCards.push(createCard(CardCategory.UNADDRESSED, 'No Unaddressed Items', 'All agenda items appear to have been covered, or no agenda was provided.'));
      }
      
      setCards(newCards);
      setView('results');
    } catch (e) {
      console.error(e);
      setError('Failed to extract items. Please check if your API key is valid and has permissions, then try again.');
    } finally {
      setIsLoading(false);
    }
  }, [transcript, agenda, apiKey]);
  
  const handleReset = () => {
    setView('input');
    setTranscript('');
    setAgenda('');
    setCards([]);
    setConnections([]);
    setError(null);
    setMeetingDate(new Date().toISOString().split('T')[0]);
  };

  const handleSetApiKey = () => {
    if (apiKey.trim()) {
      setIsApiKeySet(true);
      setError(null);
    }
  };
  
  const handleChangeApiKey = () => {
    setIsApiKeySet(false);
    // Do not clear the API key itself, let the user see and edit it.
  };

  return (
    <div className="min-h-screen font-sans text-gray-800">
      {!isApiKeySet ? (
         <ApiKeyInput apiKey={apiKey} setApiKey={setApiKey} onSet={handleSetApiKey} />
      ) : view === 'input' ? (
        <InputView
          transcript={transcript}
          setTranscript={setTranscript}
          agenda={agenda}
          setAgenda={setAgenda}
          meetingDate={meetingDate}
          setMeetingDate={setMeetingDate}
          onExtract={handleExtract}
          isLoading={isLoading}
          error={error}
        />
      ) : (
        <ResultsView
          initialCards={cards}
          transcript={transcript}
          meetingDate={meetingDate}
          onReset={handleReset}
          onChangeApiKey={handleChangeApiKey}
        />
      )}
    </div>
  );
};

export default App;