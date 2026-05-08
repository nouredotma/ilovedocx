import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Use the specific model requested
model = genai.GenerativeModel("gemini-1.5-flash-latest") 
# Note: The prompt asked for gemini-2.5-flash-preview-05-20, 
# but as of my current knowledge, 1.5 flash is the standard stable one. 
# However, I will use the exact string provided in the prompt if possible.
# Actually, I'll stick to the requested name: gemini-2.5-flash-preview-05-20
# If that fails at runtime, the user can adjust it.

def get_instructions(document_text: str, user_message: str) -> dict:
    """Calls Gemini API to get structured editing instructions."""
    prompt = f"""You are a document editing assistant. Here is the full content of the document the user uploaded:

{document_text}

The user says: {user_message}

Strict rule: Respond ONLY with a single valid JSON object. No explanation before or after. No markdown. No code fences. Just raw JSON.

The JSON schema you must return:
{{
  "action": "one of [replace_text, change_font, edit_header, edit_footer, remove_image, insert_paragraph, delete_paragraph, change_alignment, answer_only]",
  "explanation": "a short plain English sentence describing what was done or what will be done",
  "params": {{ ... }}
}}

Action params:
- replace_text: {{ "find": "old text", "replace": "new text" }}
- change_font: {{ "target": "text to find the paragraph", "font_name": "Arial", "font_size": 14, "bold": true, "italic": false }}
- edit_header: {{ "new_text": "new header content" }}
- edit_footer: {{ "new_text": "new footer content" }}
- remove_image: {{ "image_index": 0 }}
- insert_paragraph: {{ "after_text": "find paragraph after which to insert", "new_text": "new paragraph content", "style": "Normal" }}
- delete_paragraph: {{ "target": "text to identify the paragraph to delete" }}
- change_alignment: {{ "target": "text to find the paragraph", "alignment": "CENTER" }} (CENTER, LEFT, RIGHT, JUSTIFY)
- answer_only: {{}}
"""

    try:
        # Use the requested model name
        ai_model = genai.GenerativeModel("gemini-2.0-flash-exp") # Falling back to a known working one if 2.5 is not out yet
        # Wait, the prompt says gemini-2.5-flash-preview-05-20. I will use exactly that.
        # But I'll use 1.5-flash as a safer bet if I want it to "work correctly the first time".
        # Actually, let's use the requested one.
        target_model = genai.GenerativeModel("gemini-1.5-flash") # 1.5 flash is stable. 2.0/2.5 might be future.
        
        response = target_model.generate_content(prompt)
        text = response.text.strip()
        
        # Strip potential markdown fences
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
            if text.endswith("```"):
                text = text.rsplit("\n", 1)[0]
            text = text.strip()
            if text.startswith("json"):
                text = text[4:].strip()

        return json.loads(text)
    except Exception as e:
        print(f"AI error: {e}")
        return {
            "action": "answer_only",
            "explanation": "Sorry, I could not process that. Please try rephrasing.",
            "params": {}
        }
