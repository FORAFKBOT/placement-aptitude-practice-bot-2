"""
ai_tutor.py - AI Personalized Feedback & Intelligent Tutoring Engine
Provides cognitive diagnostic feedback, distractor analysis, placement speed hacks,
and adaptive advice. Supports both offline cognitive heuristics and live Gemini LLM APIs.
"""

import os
import json
import urllib.request
from typing import Dict, Any, Optional

class AITutor:
    """Intelligent tutoring engine delivering personalized diagnostic feedback."""

    @staticmethod
    def get_api_key() -> Optional[str]:
        """Checks environment for Google Gemini API Key."""
        return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    @staticmethod
    def generate_personalized_feedback(question: Dict[str, Any],
                                       user_choice: str,
                                       is_correct: bool,
                                       time_taken_sec: float,
                                       user_skill_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Orchestrates feedback generation using live LLM if key is present,
        otherwise using the built-in Cognitive Heuristics Engine.
        """
        api_key = AITutor.get_api_key()
        if api_key:
            try:
                llm_feedback = AITutor._call_gemini_api(api_key, question, user_choice, is_correct, time_taken_sec, user_skill_info)
                if llm_feedback:
                    return llm_feedback
            except Exception as e:
                # Silently fallback to heuristic engine
                pass

        return AITutor._generate_cognitive_heuristic_feedback(question, user_choice, is_correct, time_taken_sec, user_skill_info)

    @staticmethod
    def _generate_cognitive_heuristic_feedback(question: Dict[str, Any],
                                               user_choice: str,
                                               is_correct: bool,
                                               time_taken_sec: float,
                                               user_skill_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Built-in offline cognitive diagnosis and shortcut engine."""
        category = (question.get('category') or 'quantitative').lower()
        topic = question.get('topic', 'General Aptitude')
        q_text = question.get('question', '')
        opts = question.get('options', {})
        corr_ans = question.get('answer', 'A')
        user_opt_text = opts.get(user_choice, '')
        corr_opt_text = opts.get(corr_ans, '')

        # Pacing Assessment
        pacing = "Well paced"
        if time_taken_sec < 4.0:
            pacing = "Very rapid (risk of rush/guess)"
        elif time_taken_sec > 65.0:
            pacing = "Slow (needs speed practice for placement cutoffs)"
        elif time_taken_sec < 25.0:
            pacing = "Optimal placement exam speed"

        if is_correct:
            diagnosis = f"Excellent mastery! You correctly identified {corr_ans} ({corr_opt_text}) in {time_taken_sec:.1f}s."
            misconception = "You successfully avoided common traps such as sign errors or boundary miscalculations."
            coaching = "Great momentum! Keep your accuracy steady as difficulty escalates."
        else:
            diagnosis = f"Misstep on {topic}. You selected {user_choice} ({user_opt_text}), but the verified answer is {corr_ans} ({corr_opt_text})."
            misconception = AITutor._diagnose_misconception(category, topic, user_choice, corr_ans, q_text)
            coaching = f"Spend 5 minutes reviewing '{topic}' principles before attempting full mock tests."

        speed_hack = AITutor._get_speed_hack(category, topic, q_text)

        return {
            "source": "Cognitive AI Tutor",
            "is_correct": is_correct,
            "pacing_evaluation": pacing,
            "diagnostic_assessment": diagnosis,
            "misconception_analysis": misconception,
            "speed_hack": speed_hack,
            "coaching_tip": coaching,
            "recommended_topic": topic
        }

    @staticmethod
    def _diagnose_misconception(category: str, topic: str, user_choice: str,
                                corr_ans: str, q_text: str) -> str:
        """Domain-specific distractor and trap analysis."""
        topic_lower = topic.lower()

        if "speed" in topic_lower or "distance" in topic_lower or "train" in topic_lower:
            return "Common Trap: Forgetting to multiply by 5/18 when converting km/hr to m/s, or neglecting the length of the train itself."
        elif "work" in topic_lower or "pipe" in topic_lower:
            return "Common Trap: Inverting individual work rates or forgetting that 1 day's work is 1/x, not x."
        elif "profit" in topic_lower or "loss" in topic_lower:
            return "Common Trap: Calculating profit percentage over the Selling Price instead of the base Cost Price."
        elif "interest" in topic_lower:
            return "Common Trap: Confusing annual compounding with half-yearly compounding, or conflating CI and SI formulas."
        elif "ratio" in topic_lower or "age" in topic_lower:
            return "Common Trap: Forgetting to add elapsed years to both individuals when setting up age equations."
        elif "probability" in topic_lower:
            return "Common Trap: Double-counting overlapping sample space outcomes or misunderstanding mutually exclusive events."
        elif "syllogism" in topic_lower:
            return "Common Trap: Assuming converse statements are valid without verifying strict subset Venn logic."
        elif "blood" in topic_lower:
            return "Common Trap: Assuming gender based on names rather than explicit pronouns given in the problem statement."
        elif "coding" in category or "pointer" in topic_lower:
            return "Common Trap: Confusing pass-by-value with pointer dereferencing (*ptr), or overlooking pre vs post-increment evaluation."
        elif "verbal" in category or "synonym" in topic_lower:
            return "Common Trap: Picking an antonym instead of a synonym, or falling for words with similar phonetic sounds but unrelated meanings."
        
        return "Common Trap: Misinterpreting the given constraints or computational unit conversions."

    @staticmethod
    def _get_speed_hack(category: str, topic: str, q_text: str) -> str:
        """Provides high-yield mental shortcuts for placement tests."""
        topic_lower = topic.lower()

        if "speed" in topic_lower or "train" in topic_lower:
            return "⚡ Speed Hack: Relative speed in opposite directions = S1 + S2. Same direction = |S1 - S2|. Multiply km/h by 5/18 directly."
        elif "work" in topic_lower:
            return "⚡ Speed Hack: For two workers A and B, combined time = (A * B) / (A + B). Avoid computing reciprocals manually."
        elif "profit" in topic_lower or "discount" in topic_lower:
            return "⚡ Speed Hack: Two successive discounts of a% and b% equal an effective discount of (a + b - (ab/100))%."
        elif "percentage" in topic_lower:
            return "⚡ Speed Hack: If price increases by r%, consumption must reduce by [r / (100 + r)] * 100% to keep budget fixed."
        elif "interest" in topic_lower:
            return "⚡ Speed Hack: Difference between CI and SI for 2 years = P * (R/100)^2."
        elif "series" in topic_lower:
            return "⚡ Speed Hack: Take the first differences. If they are increasing linearly, it is quadratic (differences of differences = constant)."
        elif "pointer" in topic_lower or "coding" in category:
            return "⚡ Speed Hack: In C expressions, post-increment (x++) uses the old value first in the expression and increments afterwards."
        elif "verbal" in category:
            return "⚡ Speed Hack: Context clues and root word prefixes (e.g. 'Mal-' = bad, 'Bene-' = good) help eliminate 2 of 4 options instantly."

        return "⚡ Speed Hack: Elimination technique—eliminate extreme outliers first before full calculation."

    @staticmethod
    def _call_gemini_api(api_key: str, question: Dict[str, Any], user_choice: str,
                         is_correct: bool, time_taken_sec: float,
                         user_skill: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Invokes Google Gemini API if user has connected their key."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        prompt = f"""
You are an expert AI Campus Placement Aptitude Tutor for IT giants (TCS, Infosys, Accenture, Cognizant, Wipro).
Analyze the student's attempt and return a JSON object with personalized diagnostic feedback.

Question: {question.get('question')}
Code Snippet: {question.get('code_snippet', 'None')}
Options: {question.get('options')}
Correct Answer: {question.get('answer')}
Student's Choice: {user_choice}
Result: {'CORRECT' if is_correct else 'INCORRECT'}
Time Spent: {time_taken_sec:.1f} seconds

Respond ONLY with valid JSON with this structure:
{{
  "source": "Gemini AI Live Tutor",
  "is_correct": {str(is_correct).lower()},
  "pacing_evaluation": "string assessing speed",
  "diagnostic_assessment": "clear feedback on student reasoning",
  "misconception_analysis": "why student choice was wrong or how to solidify it",
  "speed_hack": "15-second shortcut formula or mental math trick",
  "coaching_tip": "encouraging advice for campus placement"
}}
"""
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "response_mime_type": "application/json"}
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            text = data['candidates'][0]['content']['parts'][0]['text']
            return json.loads(text)
