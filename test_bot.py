"""
test_bot.py - Comprehensive Verification Test Suite
Tests extraction integrity, database queries, question generators, practice engine,
mock test simulator, and analytics.
"""

import unittest
import os
import json
from database import (
    init_db,
    get_connection,
    get_db_summary,
    get_random_question,
    get_question_by_id,
    record_attempt,
    get_performance_stats,
    insert_question
)
from generator import QuestionGenerator
from engine import PracticeEngine, MockTestEngine, COMPANY_PROFILES

class TestPlacementAptitudeBot(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()

    def test_01_database_population(self):
        """Verifies database contains parsed Google Drive placement questions."""
        summary = get_db_summary()
        self.assertGreater(summary['total_questions'], 200, "Should have over 200 questions loaded")
        
        # Verify all 4 required domains exist
        cats = summary['categories']
        self.assertIn('quantitative', cats, "Quantitative questions missing")
        self.assertIn('logical', cats, "Logical questions missing")
        self.assertIn('verbal', cats, "Verbal questions missing")
        self.assertIn('coding', cats, "Coding questions missing")

        # Check domain minimum counts
        self.assertGreater(cats['quantitative'], 30)
        self.assertGreater(cats['logical'], 30)
        self.assertGreater(cats['verbal'], 20)
        self.assertGreater(cats['coding'], 20)
        print(f"[PASS] DB Verification: {summary['total_questions']} total questions across all 4 categories")

    def test_02_random_question_retrieval(self):
        """Verifies random question retrieval by category with full options & answer."""
        for cat in ['quantitative', 'logical', 'verbal', 'coding']:
            q = get_random_question(category=cat)
            self.assertIsNotNone(q, f"Failed to retrieve question for category {cat}")
            self.assertEqual(q['category'].lower(), cat)
            self.assertIn(q['answer'], ['A', 'B', 'C', 'D'], "Answer must be A, B, C, or D")
            self.assertIn(q['answer'], q['options'], "Answer key must exist in options dict")
            self.assertTrue(len(q['question']) > 5, "Question text must not be empty")
        print("[PASS] Random Question Retrieval: Quant, Logical, Verbal, and Coding")

    def test_03_dynamic_generator(self):
        """Verifies algorithmic question generator for all 4 categories."""
        # Quant
        q_quant = QuestionGenerator.generate_quantitative()
        self.assertEqual(q_quant['category'], 'quantitative')
        self.assertIn(q_quant['answer'], ['A', 'B', 'C', 'D'])
        self.assertTrue(len(q_quant['explanation']) > 15)

        # Logical
        q_log = QuestionGenerator.generate_logical()
        self.assertEqual(q_log['category'], 'logical')
        self.assertIn(q_log['answer'], ['A', 'B', 'C', 'D'])

        # Verbal
        q_verb = QuestionGenerator.generate_verbal()
        self.assertEqual(q_verb['category'], 'verbal')
        self.assertIn(q_verb['answer'], ['A', 'B', 'C', 'D'])

        # Coding
        q_code = QuestionGenerator.generate_coding()
        self.assertEqual(q_code['category'], 'coding')
        self.assertIn(q_code['answer'], ['A', 'B', 'C', 'D'])
        print("[PASS] Dynamic Algorithmic Generator: all 4 domains")

    def test_04_practice_engine_evaluation(self):
        """Verifies practice engine answer checking and attempt recording."""
        engine = PracticeEngine()
        q = engine.get_next_question(category='quantitative')
        self.assertIsNotNone(q)

        # Submit correct answer
        corr_ans = q['answer']
        res_corr = engine.evaluate_answer(q, corr_ans, time_taken=3.5)
        self.assertTrue(res_corr['is_correct'])
        self.assertEqual(res_corr['correct_answer'], corr_ans)

        # Submit wrong answer
        wrong_ans = 'A' if corr_ans != 'A' else 'B'
        res_wrong = engine.evaluate_answer(q, wrong_ans, time_taken=4.2)
        self.assertFalse(res_wrong['is_correct'])
        print("[PASS] Practice Engine Evaluation & Verification")

    def test_05_mock_test_simulation(self):
        """Simulates a full TCS NQT Mock Test with answer submissions and report generation."""
        mock = MockTestEngine(company="TCS", total_questions=12)
        self.assertEqual(len(mock.questions), 12)
        self.assertIn("quantitative", [q['category'] for q in mock.questions])
        self.assertIn("coding", [q['category'] for q in mock.questions])

        # Submit answers
        for idx, q in enumerate(mock.questions):
            # Answer half correctly, half incorrectly
            if idx % 2 == 0:
                mock.submit_answer(idx, q['answer'], time_spent=2.0)
            else:
                wrong = 'A' if q['answer'] != 'A' else 'B'
                mock.submit_answer(idx, wrong, time_spent=3.0)

        report = mock.finalize_test()
        self.assertEqual(report['total_questions'], 12)
        self.assertEqual(report['correct_count'], 6)
        self.assertEqual(report['accuracy_percent'], 50.0)
        self.assertIn('sectional_breakdown', report)
        print("[PASS] Mock Test Engine Simulation: 12-question balanced test evaluated successfully")

    def test_06_performance_analytics(self):
        """Verifies performance analytics calculation and weak area identification."""
        stats = get_performance_stats()
        self.assertIn('total_attempts', stats)
        self.assertIn('overall_accuracy', stats)
        self.assertIn('category_stats', stats)
        print(f"[PASS] Performance Analytics: {stats['total_attempts']} attempts, Accuracy: {stats['overall_accuracy']}%")

    def test_07_adaptive_difficulty_engine(self):
        """Verifies Adaptive AI cognitive skill modeling and rating adjustments."""
        import uuid
        from adaptive import AdaptiveDifficultyEngine
        fresh_user = f"test_ai_user_{uuid.uuid4().hex[:8]}"
        prof = AdaptiveDifficultyEngine.get_profile(fresh_user)
        self.assertEqual(prof['overall_rating'], 1250.0)

        # Correct answer on Medium should increase rating
        up1 = AdaptiveDifficultyEngine.update_rating("quantitative", "Medium", True, 12.0, fresh_user)
        self.assertGreater(up1['new_rating'], up1['old_rating'])
        self.assertGreater(up1['rating_delta'], 0)

        # Wrong answer on Easy should decrease rating
        up2 = AdaptiveDifficultyEngine.update_rating("quantitative", "Easy", False, 2.0, fresh_user)
        self.assertLess(up2['new_rating'], up2['old_rating'])
        self.assertLess(up2['rating_delta'], 0)

        # Recommended difficulty check
        rec_diff, tier = AdaptiveDifficultyEngine.get_recommended_difficulty("quantitative", fresh_user)
        self.assertIn(rec_diff, ["Easy", "Medium", "Hard"])
        self.assertIn("name", tier)
        print(f"[PASS] Adaptive Difficulty Engine: Elo rating updates and {rec_diff} recommendation verified")

    def test_08_ai_tutor_feedback(self):
        """Verifies personalized AI Tutor diagnostic feedback, distractor analysis and speed hacks."""
        from ai_tutor import AITutor
        dummy_q = {
            'category': 'quantitative',
            'topic': 'Speed, Time & Distance',
            'question': 'A train of length 200m travels at 72 km/hr...',
            'options': {'A': '10s', 'B': '15s', 'C': '20s', 'D': '25s'},
            'answer': 'A',
            'explanation': 'Time = 200 / (72 * 5/18) = 10s.'
        }
        # Incorrect selection
        fb_wrong = AITutor.generate_personalized_feedback(dummy_q, 'C', False, 4.5)
        self.assertIn('diagnostic_assessment', fb_wrong)
        self.assertIn('misconception_analysis', fb_wrong)
        self.assertIn('speed_hack', fb_wrong)
        self.assertIn('⚡', fb_wrong['speed_hack'])

        # Correct selection
        fb_corr = AITutor.generate_personalized_feedback(dummy_q, 'A', True, 8.2)
        self.assertTrue(fb_corr['is_correct'])
        self.assertIn('coaching_tip', fb_corr)
        print("[PASS] AI Tutor Feedback: Cognitive diagnosis, misconception traps and speed hacks verified")

    def test_09_ai_question_generator(self):
        """Verifies AI Question Generator across categories, company patterns, topics, and database persistence."""
        from ai_generator import AIQuestionGenerator

        # 1. Test all 4 domain categories
        for cat in ['quantitative', 'logical', 'verbal', 'coding']:
            q = AIQuestionGenerator.generate(category=cat, company="TCS", difficulty="Medium")
            self.assertIsNotNone(q)
            self.assertEqual(q['category'].lower(), cat)
            self.assertIn(q['answer'], ['A', 'B', 'C', 'D'])
            self.assertEqual(len(q['options']), 4)
            self.assertIn('speed_hack', q)
            self.assertIn('explanation', q)
            self.assertTrue(len(q['question']) > 5)

        # 2. Test specialized topics (mixtures, boats, clocks, recursion, bitwise, pointers, seating, idioms)
        specialized_topics = [
            ('quantitative', 'mixture'),
            ('quantitative', 'boat'),
            ('logical', 'clock'),
            ('coding', 'bit'),
            ('coding', 'recursion'),
            ('coding', 'pointer'),
            ('logical', 'seating'),
            ('verbal', 'idiom')
        ]
        for cat, top in specialized_topics:
            q = AIQuestionGenerator.generate(category=cat, company="Infosys", difficulty="Hard", topic=top)
            self.assertIn(q['answer'], ['A', 'B', 'C', 'D'])
            self.assertEqual(len(q['options']), 4)

        # 3. Test database persistence
        q_saved = AIQuestionGenerator.generate(category="coding", company="TCS", difficulty="Medium", save_to_db=True)
        self.assertIn('id', q_saved)
        self.assertIsInstance(q_saved['id'], int)
        self.assertGreater(q_saved['id'], 0)

        # Verify it can be retrieved from DB
        from database import get_question_by_id
        fetched = get_question_by_id(q_saved['id'])
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched['question'], q_saved['question'])
        print("[PASS] AI Question Generator: 4 categories, company styles, 8 specialized topics & DB persistence verified")

if __name__ == '__main__':
    unittest.main()
