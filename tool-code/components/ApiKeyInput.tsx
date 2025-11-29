import React from 'react';

interface ApiKeyInputProps {
  apiKey: string;
  setApiKey: (key: string) => void;
  onSet: () => void;
}

const ApiKeyInput: React.FC<ApiKeyInputProps> = ({ apiKey, setApiKey, onSet }) => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSet();
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-slate-50">
      <div className="w-full max-w-md p-8 space-y-6 bg-white rounded-2xl shadow-lg border border-gray-200">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-800">Scholar Sidekick 🎓</h1>
          <p className="mt-2 text-gray-600">Please enter your Google AI API Key to begin.</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="apiKey" className="sr-only">API Key</label>
            <input
              id="apiKey"
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Enter your API Key"
              className="w-full px-4 py-3 bg-white border-2 border-dotted border-gray-400 rounded-lg focus:ring-2 focus:ring-purple-300 focus:border-purple-300 transition duration-200"
              autoComplete="off"
            />
          </div>
          <button
            type="submit"
            disabled={!apiKey.trim()}
            className="w-full bg-purple-300 text-purple-900 font-bold py-3 px-10 rounded-lg hover:bg-purple-400 focus:outline-none focus:ring-4 focus:ring-purple-100 transition-transform transform hover:scale-105 disabled:bg-gray-400 disabled:cursor-not-allowed disabled:scale-100"
          >
            Save & Continue
          </button>
        </form>
        <p className="text-xs text-center text-gray-500">
          You can get your API key from{' '}
          <a href="https://ai.google.dev/gemini-api/docs/api-key" target="_blank" rel="noopener noreferrer" className="font-semibold text-purple-600 hover:underline">
            Google AI Studio
          </a>.
        </p>
      </div>
    </div>
  );
};

export default ApiKeyInput;
