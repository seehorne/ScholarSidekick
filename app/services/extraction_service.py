"""
Extraction Service - LLM-powered card extraction from meeting transcripts.

Uses Google Gemini API (REST) for intelligent extraction of:
- Meeting summaries (TL;DR)
- Action items and TODOs
- Decisions made
- Questions raised
- Discussion points
- Follow-up items
"""

import os
import json
import logging
import requests
from typing import List, Dict, Optional

from app.models import CardType

logger = logging.getLogger(__name__)

# Gemini API endpoint
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


class ExtractionService:
    """
    Service for extracting cards from meeting transcripts using Google Gemini REST API.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API key is required. "
                "Set GEMINI_API_KEY environment variable or pass api_key parameter."
            )
        logger.info("ExtractionService initialized with Gemini API")

    def extract_cards(
        self,
        transcript: str,
        agenda_items: Optional[List[str]],
        requested_types: List[CardType],
    ) -> List[Dict]:
        type_instructions = "\n".join(f"- {ct.value}" for ct in requested_types)
        agenda_section = (
            "\nAgenda Items:\n" + "\n".join(f"- {a}" for a in agenda_items)
            if agenda_items else ""
        )

        prompt = f"""You are an AI assistant that extracts structured information from meeting transcripts.

You MUST extract ONLY the following card types:
{type_instructions}

Card type definitions:
- tldr: A brief summary of the entire meeting (1-3 sentences capturing key points)
- todo: General tasks that need to be done
- action_item: Specific tasks assigned to someone with clear deliverables
- decision: Decisions that were made during the meeting
- question: Questions raised that may need answers
- discussion_point: Important topics that were discussed
- follow_up: Items that need follow-up in future meetings

For each card, return a JSON object with:
- type: the card type (MUST match one of the requested types above)
- title: short descriptive title (max 50 chars)
- content: the extracted information
- segment: exact quote from transcript supporting this (empty string "" for tldr type)

Transcript:
\"\"\"{transcript}\"\"\"
{agenda_section}

Return ONLY a valid JSON array with the requested card types. No markdown code blocks, no explanation."""

        try:
            response_text = self._call_gemini(prompt)
            cards = self._parse_json_response(response_text)
            
            if not isinstance(cards, list):
                logger.error(f"Expected list, got {type(cards)}")
                return []
            
            valid_cards = []
            for i, card in enumerate(cards):
                if isinstance(card, dict) and all(k in card for k in ["type", "title", "content"]):
                    card["position_x"] = (i % 3) * 300
                    card["position_y"] = (i // 3) * 200
                    card.setdefault("segment", "")
                    valid_cards.append(card)
            
            logger.info(f"Extracted {len(valid_cards)} cards from transcript")
            return valid_cards
            
        except Exception as e:
            logger.error(f"Card extraction failed: {e}")
            return []

    def find_uncovered_agenda_items(
        self,
        agenda_items: List[str],
        transcript: str
    ) -> List[str]:
        if not agenda_items:
            return []

        prompt = f"""Analyze the meeting transcript and identify which agenda items were NOT discussed or covered.

Agenda Items:
{json.dumps(agenda_items, indent=2)}

Transcript:
\"\"\"{transcript}\"\"\"

Return ONLY a JSON array of the agenda item strings that were NOT covered in the meeting.
If all items were covered, return an empty array [].
No markdown, no explanation, just the JSON array."""

        try:
            response_text = self._call_gemini(prompt)
            uncovered = self._parse_json_response(response_text)
            
            if not isinstance(uncovered, list):
                return []
            
            valid_uncovered = [item for item in uncovered if item in agenda_items]
            logger.info(f"Found {len(valid_uncovered)} uncovered agenda items")
            return valid_uncovered
            
        except Exception as e:
            logger.error(f"Agenda analysis failed: {e}")
            return []

    def extract_segment_for_card(
        self,
        transcript: str,
        card_content: str
    ) -> Optional[str]:
        prompt = f"""Find the exact snippet in the transcript that best supports or relates to the following card content.

Card Content:
\"\"\"{card_content}\"\"\"

Transcript:
\"\"\"{transcript}\"\"\"

Return ONLY the matching snippet from the transcript as a plain string.
If no relevant snippet is found, return an empty string.
No JSON, no quotes, no explanation."""

        try:
            response_text = self._call_gemini(prompt)
            segment = response_text.strip()
            return segment if segment else None
        except Exception as e:
            logger.error(f"Segment extraction failed: {e}")
            return None

    def _call_gemini(self, prompt: str) -> str:
        url = f"{GEMINI_API_URL}?key={self.api_key}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "topP": 0.8,
                "topK": 40,
                "maxOutputTokens": 8192,
            }
        }
        
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        if "candidates" in result and len(result["candidates"]) > 0:
            candidate = result["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                parts = candidate["content"]["parts"]
                if len(parts) > 0 and "text" in parts[0]:
                    return parts[0]["text"]
        
        raise ValueError("Unexpected Gemini API response format")

    def _parse_json_response(self, text: str) -> any:
        cleaned = text.strip()
        
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines)
        
        cleaned = cleaned.strip()
        
        if not cleaned.startswith('[') and not cleaned.startswith('{'):
            arr_start = cleaned.find('[')
            obj_start = cleaned.find('{')
            
            if arr_start >= 0 and (obj_start < 0 or arr_start < obj_start):
                cleaned = cleaned[arr_start:]
            elif obj_start >= 0:
                cleaned = cleaned[obj_start:]
        
        if cleaned.startswith('['):
            bracket_count = 0
            for i, char in enumerate(cleaned):
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        cleaned = cleaned[:i+1]
                        break
        elif cleaned.startswith('{'):
            brace_count = 0
            for i, char in enumerate(cleaned):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        cleaned = cleaned[:i+1]
                        break
        
        return json.loads(cleaned)
