"""
engine.py - Practice, Mock Test & Analytics Evaluation Engine
Orchestrates test sessions, timer management, score evaluation, and performance analysis.
"""

import time
import uuid
from typing import Dict, List, Optional, Any
from database import (
    get_random_question,
    get_mock_test_questions,
    record_attempt,
    record_session,
    get_performance_stats,
    insert_question
)
from generator import QuestionGenerator

COMPANY_PROFILES = {
    "TCS": {
        "name": "TCS NQT (National Qualifier Test)",
        "sections": ["quantitative", "logical", "verbal", "coding"],
        "default_count": 20,
        "time_limit_mins": 30,
        "description": "Standard TCS NQT pattern covering Numerical Ability, Reasoning Ability, Verbal Ability, and Coding/Hands-on concepts."
    },
    "INFOSYS": {
        "name": "Infosys Specialist / Systems Engineer Test",
        "sections": ["quantitative", "logical", "verbal", "coding"],
        "default_count": 20,
        "time_limit_mins": 35,
        "description": "Infosys assessment covering Mathematical Thinking, Logical Reasoning, Verbal Ability, and Pseudocode."
    },
    "ACCENTURE": {
        "name": "Accenture Cognitive & Technical Assessment",
        "sections": ["quantitative", "logical", "verbal", "coding"],
        "default_count": 20,
        "time_limit_mins": 30,
        "description": "Accenture pattern assessing Critical Thinking, Abstract Reasoning, English, and Common Application/Technical skills."
    },
    "COGNIZANT": {
        "name": "Cognizant GenC / GenC Next Assessment",
        "sections": ["quantitative", "logical", "verbal", "coding"],
        "default_count": 20,
        "time_limit_mins": 30,
        "description": "Cognizant placement test focusing on Quantitative, Analytical, Verbal, and Autometa/Pseudocode."
    },
    "CAPGEMINI": {
        "name": "Capgemini Placement Assessment",
        "sections": ["quantitative", "logical", "verbal", "coding"],
        "default_count": 20,
        "time_limit_mins": 30,
        "description": "Capgemini assessment with Pseudocode, Game-based / Logical reasoning, and Quantitative aptitude."
    },
    "WIPRO": {
        "name": "Wipro NLTH (Elite National Talent Hunt)",
        "sections": ["quantitative", "logical", "verbal", "coding"],
        "default_count": 20,
        "time_limit_mins": 30,
        "description": "Wipro Elite assessment evaluating Aptitude, Logical Reasoning, Verbal, and Coding Automata."
    },
    "ELITMUS": {
        "name": "eLitmus pH Test Simulation",
        "sections": ["quantitative", "logical", "verbal"],
        "default_count": 15,
        "time_limit_mins": 30,
        "description": "Rigorous eLitmus problem sets in Quantitative Aptitude, Analytical Reasoning, and Verbal Ability."
    }
}

class PracticeEngine:
    """Manages single-question practice sessions and dynamic generation."""

    def __init__(self):
        self.session_id = str(uuid.uuid4())

    def get_next_question(self, category: Optional[str] = None,
                          topic: Optional[str] = None,
                          difficulty: Optional[str] = None,
                          company: Optional[str] = None,
                          generate_dynamically: bool = False) -> Dict[str, Any]:
        """Fetches a question from the database or dynamically creates a fresh one."""
        if generate_dynamically:
            cat = category or 'quantitative'
            q = QuestionGenerator.generate_by_category(cat)
            qid = insert_question(q, is_generated=True)
            q['id'] = qid
            return q

        # Attempt to fetch from DB
        q = get_random_question(category, company, topic, difficulty)
        if not q:
            # If no match in DB, fallback to generator
            cat = category or 'quantitative'
            q = QuestionGenerator.generate_by_category(cat)
            qid = insert_question(q, is_generated=True)
            q['id'] = qid
        return q

    def evaluate_answer(self, question: Dict[str, Any], user_choice: str,
                        time_taken: float = 0.0) -> Dict[str, Any]:
        """Evaluates user answer, logs attempt in DB, and returns feedback."""
        user_choice = user_choice.strip().upper()
        correct_ans = question.get('answer', 'A').strip().upper()
        is_correct = (user_choice == correct_ans)

        # Record in DB
        qid = question.get('id', 0)
        cat = question.get('category', 'general')
        top = question.get('topic', 'General')
        record_attempt(self.session_id, qid, cat, top, user_choice, is_correct, time_taken)

        return {
            'is_correct': is_correct,
            'user_choice': user_choice,
            'correct_answer': correct_ans,
            'explanation': question.get('explanation', 'Standard solution.'),
            'time_taken_sec': round(time_taken, 1)
        }


class MockTestEngine:
    """Manages full timed placement mock test simulations."""

    def __init__(self, company: str = "TCS", total_questions: int = 20):
        self.session_id = str(uuid.uuid4())
        self.company = company.upper()
        self.profile = COMPANY_PROFILES.get(self.company, COMPANY_PROFILES["TCS"])
        self.total_questions = total_questions
        self.start_time = None
        self.end_time = None
        self.questions: List[Dict[str, Any]] = []
        self.answers: Dict[int, str] = {}
        self.question_times: Dict[int, float] = {}
        self._init_test()

    def _init_test(self):
        """Pre-loads balanced test sections."""
        per_sec = max(2, self.total_questions // len(self.profile["sections"]))
        sections = get_mock_test_questions(self.company, per_sec)
        
        flat_list = []
        for sec in self.profile["sections"]:
            sec_qs = sections.get(sec, [])
            while len(sec_qs) < per_sec:
                # Top up with dynamically generated if needed
                dyn_q = QuestionGenerator.generate_by_category(sec)
                qid = insert_question(dyn_q, is_generated=True)
                dyn_q['id'] = qid
                sec_qs.append(dyn_q)
            flat_list.extend(sec_qs[:per_sec])

        self.questions = flat_list[:self.total_questions]
        self.start_time = time.time()

    def submit_answer(self, question_index: int, choice: str, time_spent: float = 0.0):
        """Records an answer for a specific question index."""
        if 0 <= question_index < len(self.questions):
            self.answers[question_index] = choice.strip().upper()
            self.question_times[question_index] = time_spent

    def finalize_test(self) -> Dict[str, Any]:
        """Calculates final scores, sectional breakdown, accuracy, and saves session."""
        self.end_time = time.time()
        total_time = self.end_time - (self.start_time or self.end_time)

        correct_count = 0
        sectional_breakdown = {}
        detailed_review = []

        for idx, q in enumerate(self.questions):
            user_ch = self.answers.get(idx, "")
            corr_ans = q.get('answer', 'A').strip().upper()
            is_corr = (user_ch == corr_ans)
            cat = q.get('category', 'general')

            if is_corr:
                correct_count += 1

            # Update sectional breakdown
            if cat not in sectional_breakdown:
                sectional_breakdown[cat] = {'total': 0, 'correct': 0}
            sectional_breakdown[cat]['total'] += 1
            if is_corr:
                sectional_breakdown[cat]['correct'] += 1

            # Log to DB
            time_spent = self.question_times.get(idx, 0.0)
            record_attempt(self.session_id, q.get('id', 0), cat, q.get('topic', 'General'),
                           user_ch, is_corr, time_spent)

            detailed_review.append({
                'index': idx + 1,
                'category': cat,
                'topic': q.get('topic', 'General'),
                'question': q.get('question'),
                'code_snippet': q.get('code_snippet', ''),
                'options': q.get('options'),
                'user_choice': user_ch or "Skipped",
                'correct_answer': corr_ans,
                'is_correct': is_corr,
                'explanation': q.get('explanation', '')
            })

        score = float(correct_count)
        tot = len(self.questions)
        accuracy = (correct_count / tot * 100) if tot > 0 else 0.0

        # Record test session in DB
        record_session(self.session_id, f"{self.company}_MOCK", self.company,
                       score, tot, correct_count)

        # Performance assessment
        verdict = "Needs Preparation"
        if accuracy >= 80:
            verdict = "Outstanding - Placement Ready!"
        elif accuracy >= 65:
            verdict = "Good - Close to Cutoff"
        elif accuracy >= 50:
            verdict = "Average - More Practice Required"

        return {
            'session_id': self.session_id,
            'company': self.company,
            'test_title': self.profile['name'],
            'total_questions': tot,
            'correct_count': correct_count,
            'incorrect_count': tot - correct_count,
            'accuracy_percent': round(accuracy, 1),
            'total_time_sec': round(total_time, 1),
            'verdict': verdict,
            'sectional_breakdown': sectional_breakdown,
            'detailed_review': detailed_review
        }
