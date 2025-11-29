
import { GoogleGenAI, Type } from "@google/genai";

const API_KEY = process.env.API_KEY;
if (!API_KEY) {
  throw new Error("API_KEY environment variable not set");
}

const ai = new GoogleGenAI({ apiKey: API_KEY });

const schema = {
  type: Type.OBJECT,
  properties: {
    tldr: {
      type: Type.OBJECT,
      description: "A concise summary of the entire meeting.",
      properties: {
        title: { type: Type.STRING, description: "Should be 'TL;DR'" },
        content: { type: Type.STRING, description: "The summary content, 1-2 sentences." },
      },
      required: ['title', 'content'],
    },
    todos: {
      type: Type.ARRAY,
      description: "A list of all action items and tasks.",
      items: {
        type: Type.OBJECT,
        properties: {
          title: { type: Type.STRING, description: "A short, actionable title for the TODO." },
          content: { type: Type.STRING, description: "Details of the TODO item." },
        },
        required: ['title', 'content'],
      },
    },
    reflections: {
      type: Type.ARRAY,
      description: "A list of key reflections, breakthroughs, or important conclusions.",
      items: {
        type: Type.OBJECT,
        properties: {
          title: { type: Type.STRING, description: "A short title for the reflection." },
          content: { type: Type.STRING, description: "Details of the reflection." },
        },
        required: ['title', 'content'],
      },
    },
    unaddressed: {
      type: Type.ARRAY,
      description: "A list of agenda items that were not discussed.",
      items: {
        type: Type.OBJECT,
        properties: {
          title: { type: Type.STRING, description: "The unaddressed agenda item." },
          content: { type: Type.STRING, description: "A brief note why it might be unaddressed, if evident." },
        },
        required: ['title', 'content'],
      },
    },
  },
  required: ['tldr', 'todos', 'reflections', 'unaddressed'],
};

export async function extractMeetingItems(transcript: string, agenda: string): Promise<any> {
  const prompt = `
    You are an intelligent assistant for research students. Your task is to analyze a meeting transcript and an optional agenda to extract key information.

    Here is the meeting agenda:
    ---
    ${agenda || 'No agenda provided.'}
    ---

    Here is the meeting transcript:
    ---
    ${transcript}
    ---

    Please analyze the transcript and agenda and provide the following information in a structured JSON format, adhering to the provided schema.

    1.  **TL;DR**: A concise summary (1-2 sentences) of the entire meeting.
    2.  **TODOs**: A list of all action items and tasks assigned or discussed.
    3.  **Reflections**: A list of key insights, breakthroughs, or important conclusions reached during the meeting.
    4.  **Unaddressed Items**: A list of items from the agenda that were not discussed in the transcript. If no agenda was provided, this can be an empty array.
  `;

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash",
    contents: prompt,
    config: {
      responseMimeType: "application/json",
      responseSchema: schema,
    },
  });
  
  const jsonText = response.text.trim();
  try {
    return JSON.parse(jsonText);
  } catch (error) {
    console.error("Failed to parse Gemini response:", jsonText);
    throw new Error("Received invalid JSON from the API.");
  }
}