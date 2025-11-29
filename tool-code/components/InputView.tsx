import React, { useRef, useState } from 'react';

// Make mammoth available on the window object from the script tag in index.html
declare global {
  interface Window {
    mammoth: any;
  }
}

interface InputViewProps {
  transcript: string;
  setTranscript: (value: string) => void;
  agenda: string;
  setAgenda: (value: string) => void;
  meetingDate: string;
  setMeetingDate: (value: string) => void;
  onExtract: () => void;
  isLoading: boolean;
  error: string | null;
}

const InputView: React.FC<InputViewProps> = ({
  transcript,
  setTranscript,
  agenda,
  setAgenda,
  meetingDate,
  setMeetingDate,
  onExtract,
  isLoading,
  error,
}) => {
  const [isParsing, setIsParsing] = useState(false);
  const [fileError, setFileError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.docx') && file.type !== 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
      setFileError('Please upload a valid .docx file.');
      e.target.value = '';
      return;
    }

    setIsParsing(true);
    setFileError(null);

    const reader = new FileReader();
    reader.onloadend = async (event) => {
      if (event.target?.readyState === FileReader.DONE) {
        try {
          const arrayBuffer = event.target.result as ArrayBuffer;
          const result = await window.mammoth.extractRawText({ arrayBuffer });
          setTranscript(result.value);
        } catch (err) {
          console.error("Error parsing .docx file:", err);
          setFileError('Failed to read content from .docx file.');
        } finally {
          setIsParsing(false);
        }
      }
    };
    reader.onerror = () => {
      console.error("Error reading file");
      setIsParsing(false);
      setFileError('An error occurred while reading the file.');
    };
    reader.readAsArrayBuffer(file);
    e.target.value = ''; // Reset file input to allow re-uploading the same file
  };


  return (
    <div className="container mx-auto p-4 md:p-8">
      <header className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-800">Scholar Sidekick 🎓</h1>
        <p className="text-lg text-gray-600 mt-2">Turn your meeting transcripts into an actionable workspace.</p>
      </header>
      
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 md:p-8 border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="md:col-span-2 space-y-6">
            <div>
              <label htmlFor="meetingDate" className="block text-lg font-semibold mb-2 text-gray-700">🗓️ Meeting Date</label>
              <input
                type="date"
                id="meetingDate"
                value={meetingDate}
                onChange={(e) => setMeetingDate(e.target.value)}
                className="w-full p-3 bg-white border-2 border-dotted border-gray-400 rounded-lg focus:ring-2 focus:ring-purple-300 focus:border-purple-300 transition duration-200"
              />
            </div>
            <div>
              <div className="flex justify-between items-center mb-2">
                <label htmlFor="transcript" className="text-lg font-semibold text-gray-700">Meeting Transcript</label>
                <button
                  onClick={triggerFileInput}
                  disabled={isParsing}
                  className="bg-white border-2 border-purple-300 text-purple-700 font-semibold py-1 px-3 rounded-lg hover:bg-purple-50 transition-colors disabled:bg-gray-200 disabled:cursor-wait text-sm"
                >
                  {isParsing ? '📄 Parsing...' : '📄 Upload .docx'}
                </button>
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  className="hidden"
                  accept=".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                />
              </div>
               {fileError && <p className="text-red-500 text-sm mb-2">{fileError}</p>}
              <textarea
                id="transcript"
                value={transcript}
                onChange={(e) => setTranscript(e.target.value)}
                placeholder="Paste the full transcript of your meeting here, or upload a .docx file."
                className="w-full h-80 p-4 bg-white border-2 border-dotted border-gray-400 rounded-lg focus:ring-2 focus:ring-purple-300 focus:border-purple-300 transition duration-200 resize-y"
              />
            </div>
            <div>
              <label htmlFor="agenda" className="block text-lg font-semibold mb-2 text-gray-700">Agenda Items (Optional)</label>
              <textarea
                id="agenda"
                value={agenda}
                onChange={(e) => setAgenda(e.target.value)}
                placeholder="List agenda items, one per line..."
                className="w-full h-40 p-4 bg-white border-2 border-dotted border-gray-400 rounded-lg focus:ring-2 focus:ring-purple-300 focus:border-purple-300 transition duration-200 resize-y"
              />
            </div>
          </div>
          
          <div className="bg-slate-50 p-6 rounded-lg border border-slate-200">
            <h2 className="text-xl font-bold mb-4 text-slate-800">How does Scholar Sidekick help you?</h2>
            <p className="text-slate-600 mb-6">The system will automatically generate cards for the following categories based on your transcript.</p>
            <div className="space-y-3">
              <div className="bg-purple-200 text-purple-900 p-3 rounded-md font-medium">Discussed Items (TL;DR 📝)</div>
              <div className="bg-green-200 text-green-800 p-3 rounded-md font-medium">TODOs ✅</div>
              <div className="bg-sky-200 text-sky-800 p-3 rounded-md font-medium">Reflections 🤔</div>
              <div className="bg-red-200 text-red-800 p-3 rounded-md font-medium">Unaddressed Items 📌</div>
            </div>
          </div>
        </div>

        <div className="mt-8 text-center">
          {error && <p className="text-red-500 mb-4">{error}</p>}
          <button
            onClick={onExtract}
            disabled={isLoading}
            className="bg-purple-300 text-purple-900 font-bold py-3 px-10 rounded-lg hover:bg-purple-400 focus:outline-none focus:ring-4 focus:ring-purple-100 transition-transform transform hover:scale-105 disabled:bg-gray-400 disabled:cursor-not-allowed disabled:scale-100"
          >
            {isLoading ? (
              <div className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </div>
            ) : 'Generate Workspace 🚀'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default InputView;