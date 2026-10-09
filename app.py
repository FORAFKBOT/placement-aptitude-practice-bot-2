"""
app.py - Placement Aptitude Practice Bot Web Server & REST API
Zero-dependency, high-performance web dashboard powered by Python's built-in http.server.
"""

import http.server
import socketserver
import json
import urllib.parse
import os
import sys
from typing import Dict, Any

from database import (
    init_db,
    get_db_summary,
    get_random_question,
    get_question_by_id,
    record_attempt,
    get_performance_stats,
    insert_question
)
from generator import QuestionGenerator
from engine import MockTestEngine, COMPANY_PROFILES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Store in-memory active mock test sessions
ACTIVE_MOCKS: Dict[str, MockTestEngine] = {}

class PlacementBotHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler serving static dashboard and JSON REST endpoints."""

    def end_headers(self):
        # Enable CORS and caching headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def send_json(self, data: Any, status: int = 200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        # 1. Main Home Page
        if path in ['/', '/index.html']:
            index_path = os.path.join(TEMPLATES_DIR, 'index.html')
            if os.path.exists(index_path):
                with open(index_path, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            else:
                self.send_error(404, "index.html not found")
                return

        # 2. Static Assets
        if path.startswith('/static/'):
            filename = path[len('/static/'):]
            file_path = os.path.join(STATIC_DIR, filename)
            if os.path.exists(file_path):
                ext = os.path.splitext(filename)[1].lower()
                mime_types = {
                    '.css': 'text/css; charset=utf-8',
                    '.js': 'application/javascript; charset=utf-8',
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.svg': 'image/svg+xml'
                }
                ctype = mime_types.get(ext, 'application/octet-stream')
                with open(file_path, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-Type', ctype)
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            else:
                self.send_error(404, f"Static file {filename} not found")
                return

        # 3. REST API: DB Summary
        if path == '/api/summary':
            summary = get_db_summary()
            self.send_json(summary)
            return

        # 4. REST API: Fetch Question
        if path == '/api/question':
            cat = params.get('category', [None])[0]
            comp = params.get('company', [None])[0]
            top = params.get('topic', [None])[0]
            diff = params.get('difficulty', [None])[0]

            q = get_random_question(category=cat, company=comp, topic=top, difficulty=diff)
            if not q:
                # Procedurally generate fallback
                target_cat = cat or 'quantitative'
                q = QuestionGenerator.generate_by_category(target_cat)
                qid = insert_question(q, is_generated=True)
                q['id'] = qid

            self.send_json(q)
            return

        # 5. REST API: Dynamic Procedural Generation
        if path == '/api/generate':
            cat = params.get('category', ['quantitative'])[0]
            q = QuestionGenerator.generate_by_category(cat)
            qid = insert_question(q, is_generated=True)
            q['id'] = qid
            self.send_json(q)
            return

        # 6. REST API: Mock Test Start
        if path == '/api/mock/start':
            comp = params.get('company', ['TCS'])[0]
            cnt = int(params.get('count', [16])[0])
            engine = MockTestEngine(company=comp, total_questions=cnt)
            ACTIVE_MOCKS[engine.session_id] = engine

            # Return sanitized questions (exclude answer key from client during test)
            safe_questions = []
            for q in engine.questions:
                safe_questions.append({
                    'id': q['id'],
                    'category': q['category'],
                    'company': q['company'],
                    'topic': q['topic'],
                    'difficulty': q['difficulty'],
                    'question': q['question'],
                    'code_snippet': q['code_snippet'],
                    'options': q['options']
                })

            resp = {
                'session_id': engine.session_id,
                'company': engine.company,
                'test_title': engine.profile['name'],
                'questions': safe_questions
            }
            self.send_json(resp)
            return

        # 7. REST API: Analytics
        if path == '/api/analytics':
            stats = get_performance_stats()
            self.send_json(stats)
            return

        self.send_error(404, "Endpoint not found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get('Content-Length', 0))
        raw_body = self.rfile.read(length) if length > 0 else b'{}'
        try:
            body = json.loads(raw_body.decode('utf-8'))
        except Exception:
            body = {}

        # 1. Submit Single Question Answer
        if path == '/api/submit':
            qid = body.get('question_id')
            user_choice = str(body.get('user_choice', '')).strip().upper()
            time_spent = float(body.get('time_taken_sec', 0.0))

            q = get_question_by_id(qid) if qid else None
            if not q:
                self.send_json({'error': 'Question not found'}, 404)
                return

            corr = q.get('answer', 'A').strip().upper()
            is_correct = (user_choice == corr)

            record_attempt("web_session", qid, q['category'], q['topic'],
                           user_choice, is_correct, time_spent)

            self.send_json({
                'is_correct': is_correct,
                'user_choice': user_choice,
                'correct_answer': corr,
                'explanation': q.get('explanation', 'Standard solution.')
            })
            return

        # 2. Submit Mock Test
        if path == '/api/mock/submit':
            session_id = body.get('session_id')
            user_answers = body.get('answers', {})

            engine = ACTIVE_MOCKS.get(session_id)
            if not engine:
                self.send_json({'error': 'Mock session expired or not found'}, 404)
                return

            for idx_str, choice in user_answers.items():
                try:
                    idx = int(idx_str)
                    engine.submit_answer(idx, str(choice))
                except ValueError:
                    pass

            report = engine.finalize_test()
            del ACTIVE_MOCKS[session_id]
            self.send_json(report)
            return

        self.send_error(404, "POST endpoint not found")

def run_server(port: int = 8080):
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass
    init_db()
    
    server_address = ('', port)
    for p in range(port, port + 10):
        try:
            httpd = socketserver.ThreadingTCPServer(('', p), PlacementBotHandler)
            print("=" * 70)
            print(f">> Placement Aptitude Practice Bot Web Server Running!")
            print(f">> Local URL: http://localhost:{p}")
            print(f">> Features: Practice Mode, Company Mocks, Infinite Generator, Stats")
            print("=" * 70)
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nShutting down web server...")
                httpd.server_close()
            break
        except OSError:
            continue

if __name__ == '__main__':
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run_server(port)
