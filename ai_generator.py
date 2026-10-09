"""
ai_generator.py - Advanced AI Question Generator Engine for Placement Aptitude Practice Bot
Supports dynamic LLM generation (via Google Gemini) for TCS, Infosys, Accenture, Cognizant,
Capgemini, and Wipro patterns, coupled with an offline cognitive procedural question generator.
"""

import os
import json
import random
import math
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List

from generator import QuestionGenerator
from database import insert_question

class AIQuestionGenerator:
    """
    Hybrid AI Question Generation Engine:
    1. Live Gemini LLM Generation (custom topics, company exam patterns, precise difficulty).
    2. Zero-dependency Offline Cognitive Heuristics Generator (algebraic, logical, and code templates).
    """

    SUPPORTED_COMPANIES = [
        "TCS", "Infosys", "Accenture", "Cognizant", "Capgemini", "Wipro", "eLitmus", "AMCAT", "General"
    ]

    SUPPORTED_CATEGORIES = [
        "quantitative", "logical", "verbal", "coding"
    ]

    COMPANY_STYLE_PROFILES = {
        "TCS": "TCS NQT style: focus on advanced quantitative aptitude, numerical analysis, bitwise/pointer pseudocode, and formal business communication.",
        "Infosys": "Infosys SP/DSE style: cryptarithmetic logic, data sufficiency, puzzle-based deduction, Python/C++ code traces, and reading inference.",
        "Accenture": "Accenture Critical Thinking style: syllogisms, flowcharts, abstract reasoning, coding fundamentals, and grammatical sentence correction.",
        "Cognizant": "Cognizant GenC/GenC Next style: automata fix/debugging, algorithmic logic, time-speed-distance, probability, and contextual vocabulary.",
        "Capgemini": "Capgemini style: inductive reasoning, game-based logic patterns, pseudo code tracing, and core computer science concepts.",
        "Wipro": "Wipro NLTH/Elite style: profit-loss, speed-distance, recursive code trace, error spotting, and logical series.",
        "General": "Standard IT campus recruitment aptitude benchmark covering essential placement problem patterns."
    }

    @staticmethod
    def get_api_key() -> Optional[str]:
        """Retrieves Gemini API Key from environment."""
        return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    @classmethod
    def generate(cls,
                 category: str = "quantitative",
                 company: str = "TCS",
                 difficulty: str = "Medium",
                 topic: Optional[str] = None,
                 custom_prompt: Optional[str] = None,
                 use_llm: bool = True,
                 save_to_db: bool = False) -> Dict[str, Any]:
        """
        Generates an aptitude or technical coding question.
        Attempts Gemini LLM first if API key is present and use_llm is True;
        otherwise falls back seamlessly to the offline cognitive generator.
        """
        category = category.lower().strip()
        if category not in cls.SUPPORTED_CATEGORIES:
            category = "quantitative"

        if company not in cls.SUPPORTED_COMPANIES:
            company = "General"

        difficulty = difficulty.capitalize() if difficulty else "Medium"
        if difficulty not in ["Easy", "Medium", "Hard"]:
            difficulty = "Medium"

        api_key = cls.get_api_key() if use_llm else None
        question = None

        if api_key and use_llm:
            try:
                question = cls._generate_via_gemini(
                    api_key=api_key,
                    category=category,
                    company=company,
                    difficulty=difficulty,
                    topic=topic,
                    custom_prompt=custom_prompt
                )
            except Exception as e:
                # Fallback silently to offline generator
                question = None

        if not question:
            question = cls._generate_offline(
                category=category,
                company=company,
                difficulty=difficulty,
                topic=topic
            )

        # Standardize structure
        if "speed_hack" not in question:
            question["speed_hack"] = "Eliminate extreme distractors and test boundary cases first."

        if save_to_db:
            try:
                new_id = insert_question(question, is_generated=True)
                question["id"] = new_id
            except Exception:
                pass

        return question

    @classmethod
    def _generate_via_gemini(cls,
                             api_key: str,
                             category: str,
                             company: str,
                             difficulty: str,
                             topic: Optional[str],
                             custom_prompt: Optional[str]) -> Optional[Dict[str, Any]]:
        """Generates a question using Google Gemini REST API."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

        style_guide = cls.COMPANY_STYLE_PROFILES.get(company, cls.COMPANY_STYLE_PROFILES["General"])
        topic_clause = f"Topic focus: {topic}." if topic else "Topic: choose a high-yield placement topic."
        custom_clause = f"Additional instruction: {custom_prompt}." if custom_prompt else ""

        system_prompt = f"""
You are an expert Question Designer for Campus Placements at top IT companies ({company}).
Create 1 authentic, highly realistic multiple-choice question for:
- Category: {category}
- Company Pattern: {company} ({style_guide})
- Difficulty: {difficulty}
- {topic_clause}
{custom_clause}

Requirements:
1. Question must be self-contained, clear, and challenging for university graduates.
2. If category is 'coding', include a code snippet in C, C++, Java, or Python (clean text, no markdown backticks inside JSON string).
3. Options must be exactly 4 keys: "A", "B", "C", "D".
4. Answer must be one of "A", "B", "C", "D".
5. Distractors (incorrect choices) must reflect realistic calculation errors or cognitive traps.
6. Explanation must provide clear, step-by-step mathematical or algorithmic steps to reach the correct answer.
7. Speed Hack must be a concise, 1-2 sentence placement mental trick or formula shortcut.

Respond ONLY with valid JSON following this exact schema:
{{
  "category": "{category}",
  "company": "{company}",
  "topic": "Specific Topic Name",
  "difficulty": "{difficulty}",
  "question": "The question text statement",
  "code_snippet": "Optional code block or empty string",
  "options": {{
    "A": "Option A text",
    "B": "Option B text",
    "C": "Option C text",
    "D": "Option D text"
  }},
  "answer": "A",
  "explanation": "Step-by-step clear explanation",
  "speed_hack": "Placement shortcut or mental formula",
  "source": "AI Generated ({company} Pattern)"
}}
"""

        payload = {
            "contents": [{"parts": [{"text": system_prompt}]}],
            "generationConfig": {
                "temperature": 0.4,
                "response_mime_type": "application/json"
            }
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            candidate = data.get("candidates", [])[0]
            raw_text = candidate.get("content", {}).get("parts", [])[0].get("text", "")
            parsed = json.loads(raw_text)

            # Sanity checks
            opts = parsed.get("options", {})
            if len(opts) == 4 and parsed.get("answer") in ["A", "B", "C", "D"]:
                parsed["ai_engine"] = "Gemini LLM (Live)"
                return parsed

        return None

    @classmethod
    def _generate_offline(cls,
                           category: str,
                           company: str,
                           difficulty: str,
                           topic: Optional[str]) -> Dict[str, Any]:
        """
        Rich offline procedural generator covering 20+ placement problem templates.
        Guarantees instant, zero-dependency, computed questions with guaranteed accuracy.
        """
        # Specialized templates based on topic keywords if specified
        topic_lower = (topic or "").lower()

        # Check for specialized procedural templates
        if "mixture" in topic_lower or "alligation" in topic_lower:
            q = cls._gen_mixture_alligation()
        elif "boat" in topic_lower or "stream" in topic_lower:
            q = cls._gen_boats_and_streams()
        elif "clock" in topic_lower or "angle" in topic_lower:
            q = cls._gen_clocks_and_angles()
        elif "lcm" in topic_lower or "hcf" in topic_lower or "remainder" in topic_lower:
            q = cls._gen_lcm_hcf()
        elif "bit" in topic_lower:
            q = cls._gen_bit_manipulation()
        elif "recursion" in topic_lower or "stack" in topic_lower:
            q = cls._gen_recursion_trace()
        elif "pointer" in topic_lower:
            q = cls._gen_pointer_arithmetic()
        elif "seating" in topic_lower or "arrangement" in topic_lower:
            q = cls._gen_seating_arrangement()
        elif "idiom" in topic_lower or "phrase" in topic_lower:
            q = cls._gen_idioms_phrases()
        else:
            # Dispatch to comprehensive procedural generator in generator.py
            q = QuestionGenerator.generate_by_category(category)

        # Apply user's selected company, difficulty, and tag
        q["company"] = company if company != "General" else q.get("company", "General")
        q["difficulty"] = difficulty
        q["ai_engine"] = "Cognitive Heuristics (Offline)"
        q["source"] = f"AI Generated ({company} Pattern)"

        # Ensure speed hack
        if "speed_hack" not in q:
            from ai_tutor import AITutor
            q["speed_hack"] = AITutor._get_speed_hack(q.get("category", category), q.get("topic", "General"), q.get("question", ""))

        return q

    # -------------------------------------------------------------
    # High-Yield Placement Procedural Templates (Computed Real-Time)
    # -------------------------------------------------------------

    @staticmethod
    def _gen_mixture_alligation() -> Dict[str, Any]:
        """Mixture & Alligation template - favorite in TCS and Cognizant."""
        c1 = random.choice([20, 25, 30, 40])
        c2 = random.choice([50, 60, 70, 80])
        ratio_1 = random.choice([1, 2, 3])
        ratio_2 = random.choice([1, 2, 3])
        mean_price = round((c1 * ratio_1 + c2 * ratio_2) / (ratio_1 + ratio_2), 2)

        q_text = (f"In what ratio must tea costing Rs. {c1} per kg be mixed with tea costing Rs. {c2} per kg "
                  f"so that the resulting mixture is worth Rs. {mean_price:.2f} per kg?")
        correct_val = f"{ratio_1}:{ratio_2}"
        distractors = [f"{ratio_2}:{ratio_1}", f"{ratio_1 + 1}:{ratio_2}", f"{ratio_1}:{ratio_2 + 1}"]

        opts_list = list(set([correct_val] + distractors))
        while len(opts_list) < 4:
            opts_list.append(f"{random.randint(1, 4)}:{random.randint(1, 4)}")
        random.shuffle(opts_list)

        opt_keys = ["A", "B", "C", "D"]
        options = {opt_keys[i]: opts_list[i] for i in range(4)}
        correct_opt = [k for k, v in options.items() if v == correct_val][0]

        explanation = (
            f"Rule of Alligation:\n"
            f"(Cheaper Quantity) / (Dearer Quantity) = (Price of Dearer - Mean Price) / (Mean Price - Price of Cheaper)\n"
            f"= ({c2} - {mean_price:.2f}) / ({mean_price:.2f} - {c1}) = {ratio_1} / {ratio_2} = {correct_val}."
        )

        return {
            "category": "quantitative",
            "company": "TCS",
            "topic": "Mixtures & Alligations",
            "difficulty": "Medium",
            "question": q_text,
            "code_snippet": "",
            "options": options,
            "answer": correct_opt,
            "explanation": explanation,
            "speed_hack": "⚡ Speed Hack: Cross-subtraction: (Dearer - Mean) : (Mean - Cheaper) gives the mixing ratio directly without equations.",
            "source": "AI Cognitive Generator (Alligation Pattern)"
        }

    @staticmethod
    def _gen_boats_and_streams() -> Dict[str, Any]:
        """Boats and Streams template - common in Infosys and Wipro."""
        boat_speed = random.choice([12, 15, 18, 20])
        stream_speed = random.choice([2, 3, 4, 5])
        distance = (boat_speed - stream_speed) * random.choice([2, 3, 4])

        time_upstream = distance / (boat_speed - stream_speed)
        time_downstream = distance / (boat_speed + stream_speed)

        q_text = (f"A boat can travel at {boat_speed} km/h in still water. If the velocity of the water current is {stream_speed} km/h, "
                  f"how much time will it take to travel {distance} km downstream?")
        correct_val = f"{time_downstream:.1f} hours" if not time_downstream.is_integer() else f"{int(time_downstream)} hours"
        distractors = [
            f"{time_upstream:.1f} hours" if not time_upstream.is_integer() else f"{int(time_upstream)} hours",
            f"{distance / boat_speed:.1f} hours",
            f"{time_downstream + 1:.0f} hours"
        ]

        opts_list = list(set([correct_val] + distractors))
        while len(opts_list) < 4:
            opts_list.append(f"{random.randint(2, 10)} hours")
        random.shuffle(opts_list)

        opt_keys = ["A", "B", "C", "D"]
        options = {opt_keys[i]: opts_list[i] for i in range(4)}
        correct_opt = [k for k, v in options.items() if v == correct_val][0]

        explanation = (
            f"Downstream Speed = Boat Speed + Stream Speed = {boat_speed} + {stream_speed} = {boat_speed + stream_speed} km/h.\n"
            f"Time Downstream = Distance / Downstream Speed = {distance} / {boat_speed + stream_speed} = {correct_val}."
        )

        return {
            "category": "quantitative",
            "company": "Infosys",
            "topic": "Boats & Streams",
            "difficulty": "Easy",
            "question": q_text,
            "code_snippet": "",
            "options": options,
            "answer": correct_opt,
            "explanation": explanation,
            "speed_hack": "⚡ Speed Hack: Downstream = u + v, Upstream = u - v. Boat in still water = (Downstream + Upstream) / 2.",
            "source": "AI Cognitive Generator (Boats & Streams Pattern)"
        }

    @staticmethod
    def _gen_clocks_and_angles() -> Dict[str, Any]:
        """Clocks and Angles template - frequent in Accenture and Capgemini."""
        hour = random.choice([3, 4, 5, 7, 8, 9, 10])
        minute = random.choice([15, 20, 30, 40, 50])

        angle = abs((30 * hour) - (11 / 2 * minute))
        if angle > 180:
            angle = 360 - angle

        angle_val = f"{angle:.1f}°" if not angle.is_integer() else f"{int(angle)}°"
        q_text = f"What is the angle between the hour hand and the minute hand of a clock at {hour}:{minute:02d}?"
        correct_val = angle_val
        distractors = [f"{abs(angle - 30):.0f}°", f"{(angle + 25) % 180:.0f}°", f"{abs(180 - angle):.0f}°"]

        opts_list = list(set([correct_val] + distractors))
        while len(opts_list) < 4:
            opts_list.append(f"{random.randint(10, 175)}°")
        random.shuffle(opts_list)

        opt_keys = ["A", "B", "C", "D"]
        options = {opt_keys[i]: opts_list[i] for i in range(4)}
        correct_opt = [k for k, v in options.items() if v == correct_val][0]

        explanation = (
            f"Clock Angle Formula: |30*H - (11/2)*M|\n"
            f"= |30*{hour} - (11/2)*{minute}| = |{30 * hour} - {5.5 * minute}| = {angle_val}."
        )

        return {
            "category": "logical",
            "company": "Accenture",
            "topic": "Clocks & Calendars",
            "difficulty": "Medium",
            "question": q_text,
            "code_snippet": "",
            "options": options,
            "answer": correct_opt,
            "explanation": explanation,
            "speed_hack": "⚡ Speed Hack: Remember the standard angle formula θ = |30H - 5.5M|. If θ > 180°, subtract from 360° for the smaller angle.",
            "source": "AI Cognitive Generator (Clocks Pattern)"
        }

    @staticmethod
    def _gen_lcm_hcf() -> Dict[str, Any]:
        """LCM & HCF remainder problem - ubiquitous in TCS NQT."""
        div1, div2, div3 = 12, 15, 20
        lcm_val = math.lcm(div1, div2, div3)
        rem = random.choice([3, 5, 7])
        ans_num = lcm_val + rem

        q_text = (f"Find the smallest positive integer which when divided by {div1}, {div2}, and {div3} "
                  f"leaves a remainder of {rem} in each case.")
        correct_val = str(ans_num)
        distractors = [str(lcm_val), str(ans_num + div1), str(ans_num - div1)]

        opts_list = list(set([correct_val] + distractors))
        while len(opts_list) < 4:
            opts_list.append(str(ans_num + random.randint(10, 50)))
        random.shuffle(opts_list)

        opt_keys = ["A", "B", "C", "D"]
        options = {opt_keys[i]: opts_list[i] for i in range(4)}
        correct_opt = [k for k, v in options.items() if v == correct_val][0]

        explanation = (
            f"Step 1: Compute LCM({div1}, {div2}, {div3}) = {lcm_val}.\n"
            f"Step 2: Required number = LCM + Remainder = {lcm_val} + {rem} = {ans_num}."
        )

        return {
            "category": "quantitative",
            "company": "TCS",
            "topic": "LCM, HCF & Number Systems",
            "difficulty": "Easy",
            "question": q_text,
            "code_snippet": "",
            "options": options,
            "answer": correct_opt,
            "explanation": explanation,
            "speed_hack": "⚡ Speed Hack: Test options by subtracting the remainder and checking divisibility by the largest divisor.",
            "source": "AI Cognitive Generator (LCM Pattern)"
        }

    @staticmethod
    def _gen_bit_manipulation() -> Dict[str, Any]:
        """Bitwise trick template - core TCS and Cognizant pseudocode."""
        n = random.choice([12, 14, 24, 40, 48])
        result = n & (n - 1)

        q_text = "What is the evaluated output of the expression `n & (n - 1)` when `n = " + str(n) + "`?"
        code_snip = f"int n = {n};\nint res = n & (n - 1);\nprintf(\"%d\", res);"
        correct_val = str(result)
        distractors = [str(n - 1), str(n), str(n | (n - 1))]

        opts_list = list(set([correct_val] + distractors))
        while len(opts_list) < 4:
            opts_list.append(str(random.randint(0, 32)))
        random.shuffle(opts_list)

        opt_keys = ["A", "B", "C", "D"]
        options = {opt_keys[i]: opts_list[i] for i in range(4)}
        correct_opt = [k for k, v in options.items() if v == correct_val][0]

        explanation = (
            f"Binary of {n}: {bin(n)[2:]}\n"
            f"Binary of {n - 1}: {bin(n - 1)[2:]}\n"
            f"Bitwise AND (`&`) clears the lowest set bit (rightmost 1-bit) of `n`.\n"
            f"Result in decimal = {result}."
        )

        return {
            "category": "coding",
            "company": "TCS",
            "topic": "Bitwise Manipulation",
            "difficulty": "Medium",
            "question": q_text,
            "code_snippet": code_snip,
            "options": options,
            "answer": correct_opt,
            "explanation": explanation,
            "speed_hack": "⚡ Speed Hack: `n & (n - 1)` always turns off the rightmost set bit of `n`. If `n & (n - 1) == 0`, `n` is a power of 2.",
            "source": "AI Cognitive Generator (Bitwise Pattern)"
        }

    @staticmethod
    def _gen_recursion_trace() -> Dict[str, Any]:
        """Recursive execution tree trace."""
        n = random.choice([3, 4, 5])
        # Function: f(n) = n + f(n - 2) if n > 0 else 0
        def solve(x):
            if x <= 0:
                return 0
            return x + solve(x - 2)

        ans = solve(n)
        code_snip = "int solve(int n) {\n    if (n <= 0) return 0;\n    return n + solve(n - 2);\n}"
        q_text = f"What will be returned by the recursive call `solve({n})`?"
        correct_val = str(ans)
        distractors = [str(ans + 2), str(max(1, ans - 2)), str(n * (n + 1) // 2)]

        opts_list = list(set([correct_val] + distractors))
        while len(opts_list) < 4:
            opts_list.append(str(random.randint(4, 20)))
        random.shuffle(opts_list)

        opt_keys = ["A", "B", "C", "D"]
        options = {opt_keys[i]: opts_list[i] for i in range(4)}
        correct_opt = [k for k, v in options.items() if v == correct_val][0]

        calls = []
        curr = n
        while curr > 0:
            calls.append(str(curr))
            curr -= 2
        calls.append("0")

        explanation = (
            f"Unwinding the recursion stack:\n"
            f"solve({n}) = {' + '.join(calls)} = {ans}."
        )

        return {
            "category": "coding",
            "company": "Infosys",
            "topic": "Recursion & Call Stack",
            "difficulty": "Medium",
            "question": q_text,
            "code_snippet": code_snip,
            "options": options,
            "answer": correct_opt,
            "explanation": explanation,
            "speed_hack": "⚡ Speed Hack: Identify the step size in recursive calls (here decrement by 2) to quickly sum the arithmetic sequence without a full tree.",
            "source": "AI Cognitive Generator (Recursion Pattern)"
        }

    @staticmethod
    def _gen_pointer_arithmetic() -> Dict[str, Any]:
        """Pointers and Array manipulation in C."""
        arr = [random.randint(10, 50) for _ in range(5)]
        idx = random.choice([1, 2, 3])
        correct_val = str(arr[idx])

        code_snip = (
            f"int arr[] = {{{', '.join(map(str, arr))}}};\n"
            f"int *p = arr;\n"
            f"printf(\"%d\", *(p + {idx}));"
        )
        q_text = "What will be printed when the following C snippet is executed?"
        distractors = [str(arr[idx - 1]), str(arr[0]), str(arr[idx] + idx)]

        opts_list = list(set([correct_val] + distractors))
        while len(opts_list) < 4:
            opts_list.append(str(random.randint(10, 60)))
        random.shuffle(opts_list)

        opt_keys = ["A", "B", "C", "D"]
        options = {opt_keys[i]: opts_list[i] for i in range(4)}
        correct_opt = [k for k, v in options.items() if v == correct_val][0]

        explanation = (
            f"`arr` decays into a pointer to the 0th element `arr[0]` = {arr[0]}.\n"
            f"`p + {idx}` points to element at index {idx}.\n"
            f"Dereferencing `*(p + {idx})` produces `arr[{idx}]` = {correct_val}."
        )

        return {
            "category": "coding",
            "company": "Capgemini",
            "topic": "Pointers & Memory",
            "difficulty": "Medium",
            "question": q_text,
            "code_snippet": code_snip,
            "options": options,
            "answer": correct_opt,
            "explanation": explanation,
            "speed_hack": "⚡ Speed Hack: Pointer equivalence in C: `*(p + i)` is exactly identical to `p[i]`.",
            "source": "AI Cognitive Generator (Pointers Pattern)"
        }

    @staticmethod
    def _gen_seating_arrangement() -> Dict[str, Any]:
        """Logical Reasoning: Linear Seating Arrangement."""
        names = ["A", "B", "C", "D", "E"]
        # A, B, C, D, E in a row facing North
        # C is in the middle. B is to the immediate right of C. A is at the left extreme.
        q_text = (
            "Five friends (A, B, C, D, and E) are sitting in a row facing North.\n"
            "- C is sitting in the exact middle.\n"
            "- A is sitting at the extreme left end.\n"
            "- B is sitting immediately to the right of C.\n"
            "- D is between A and C.\n"
            "Who is sitting at the extreme right end?"
        )
        correct_val = "E"
        distractors = ["B", "D", "C"]

        opts_list = list(set([correct_val] + distractors))
        random.shuffle(opts_list)

        opt_keys = ["A", "B", "C", "D"]
        options = {opt_keys[i]: opts_list[i] for i in range(4)}
        correct_opt = [k for k, v in options.items() if v == correct_val][0]

        explanation = (
            "Total positions: 1, 2, 3, 4, 5 (from Left to Right)\n"
            "- Middle position 3 is C.\n"
            "- Position 1 is A.\n"
            "- D is between A (1) and C (3), so position 2 is D.\n"
            "- B is immediately to the right of C, so position 4 is B.\n"
            "- The only remaining person E must be at position 5 (extreme right)."
        )

        return {
            "category": "logical",
            "company": "Cognizant",
            "topic": "Seating Arrangement",
            "difficulty": "Medium",
            "question": q_text,
            "code_snippet": "",
            "options": options,
            "answer": correct_opt,
            "explanation": explanation,
            "speed_hack": "⚡ Speed Hack: Draw slots 1 to 5 and lock fixed anchor clues first (like middle or extremes).",
            "source": "AI Cognitive Generator (Seating Pattern)"
        }

    @staticmethod
    def _gen_idioms_phrases() -> Dict[str, Any]:
        """Verbal: Idioms and contextual English."""
        idioms = [
            (
                "What does the idiom 'Bite the bullet' mean?",
                "Face a painful situation with courage and fortitude",
                ["Avoid responsibility at all costs", "Express extreme anger violently", "Waste valuable time on trivial matters"],
                "'Bite the bullet' historically comes from soldiers biting a lead bullet to endure surgery without anesthesia. It means facing hardship bravely."
            ),
            (
                "What does the idiom 'Burn the midnight oil' mean?",
                "Work or study late into the night",
                ["Waste natural resources recklessly", "Ignite conflict between colleagues", "Wake up early at dawn"],
                "'Burn the midnight oil' means working late by the light of an oil lamp."
            ),
            (
                "What does the idiom 'At the eleventh hour' mean?",
                "At the very last possible moment",
                ["Before noon sharp", "During the start of an exam", "Prematurely without preparation"],
                "'At the eleventh hour' refers to doing something at the very last moment before a deadline."
            )
        ]
        q_text, correct_val, distractors, explanation = random.choice(idioms)

        opts_list = list(set([correct_val] + distractors))
        random.shuffle(opts_list)

        opt_keys = ["A", "B", "C", "D"]
        options = {opt_keys[i]: opts_list[i] for i in range(4)}
        correct_opt = [k for k, v in options.items() if v == correct_val][0]

        return {
            "category": "verbal",
            "company": "Accenture",
            "topic": "Idioms & Phrases",
            "difficulty": "Easy",
            "question": q_text,
            "code_snippet": "",
            "options": options,
            "answer": correct_opt,
            "explanation": explanation,
            "speed_hack": "⚡ Speed Hack: Look for metaphorical meaning rather than literal physical interpretation of idioms.",
            "source": "AI Cognitive Generator (Idioms Pattern)"
        }
