"""
cli_bot.py - Interactive Placement Aptitude Practice Bot (Terminal Interface)
Features rich colored menus, practice modes, company mock tests, dynamic generators, and analytics.
"""

import sys
import time
import os

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from engine import PracticeEngine, MockTestEngine, COMPANY_PROFILES
from database import get_performance_stats, get_db_summary, init_db

# ANSI Color Codes for terminal styling
class Style:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    
    # Foreground
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    
    # Background
    BG_BLUE = "\033[44m"
    BG_GREEN = "\033[42m"
    BG_MAGENTA = "\033[45m"

def print_banner():
    banner = f"""
{Style.CYAN}{Style.BOLD}================================================================================
   ____  __                                      __      ___          __  _     __       
  / __ \/ /___ _________  ____ ___  ___  ____  / /_    /   |  ____  / /_(_)___/ /_  __  
 / /_/ / / __ `/ ___/ _ \/ __ `__ \/ _ \/ __ \/ __/   / /| | / __ \/ __/ / __  / / / /  
/ ____/ / /_/ / /__/  __/ / / / / /  __/ / / / /_    / ___ |/ /_/ / /_/ / /_/ / /_/ /   
\/_/   /_/\__,_/\___/\___/_/ /_/ /_/\___/_/ /_/\__/   /_/  |_/ .___/\__/_/\__,_/\__,_/    
                                                            /_/                          
               P R A C T I C E   B O T   (Powered by Drive Materials)
================================================================================{Style.RESET}
{Style.YELLOW}Domains: Quantitative Aptitude | Logical Reasoning | Verbal Ability | Coding & DSA{Style.RESET}
{Style.DIM}Target Companies: TCS | Infosys | Accenture | Capgemini | Cognizant | Wipro | eLitmus{Style.RESET}
"""
    print(banner)

def get_category_badge(cat: str) -> str:
    cat = cat.lower()
    if cat == 'quantitative':
        return f"{Style.BOLD}\033[33m[QUANTITATIVE]\033[0m"
    elif cat == 'logical':
        return f"{Style.BOLD}\033[36m[LOGICAL]\033[0m"
    elif cat == 'verbal':
        return f"{Style.BOLD}\033[35m[VERBAL]\033[0m"
    elif cat == 'coding':
        return f"{Style.BOLD}\033[32m[CODING / TECHNICAL]\033[0m"
    return f"{Style.BOLD}[GENERAL]{Style.RESET}"

def display_question(q: dict, q_num: int = 1, total: int = 1):
    badge = get_category_badge(q.get('category', 'general'))
    comp = q.get('company', 'General')
    topic = q.get('topic', 'General Aptitude')
    diff = q.get('difficulty', 'Medium')
    
    header = f"\n{badge} {Style.BOLD}Topic:{Style.RESET} {topic} | {Style.BOLD}Company:{Style.RESET} {comp} | {Style.BOLD}Diff:{Style.RESET} {diff}"
    if total > 1:
        header = f"\n{Style.BOLD}Question {q_num} of {total}{Style.RESET} | " + header
    print(header)
    print("-" * 80)
    
    print(f"\n{Style.BOLD}{q.get('question')}{Style.RESET}\n")
    
    code = q.get('code_snippet')
    if code:
        print(f"{Style.YELLOW}--- Code Snippet ---{Style.RESET}")
        for line in code.split('\n'):
            print(f"  {line}")
        print(f"{Style.YELLOW}--------------------{Style.RESET}\n")
        
    opts = q.get('options', {})
    for label in ['A', 'B', 'C', 'D']:
        if label in opts:
            print(f"  {Style.BOLD}({label}){Style.RESET} {opts[label]}")
    print()

def run_practice_mode():
    engine = PracticeEngine()
    print(f"\n{Style.BOLD}{Style.CYAN}--- Topic & Domain Practice Mode ---{Style.RESET}")
    print("Choose Practice Domain:")
    print("1. Quantitative Aptitude (Math, Arithmetic, Algebra)")
    print("2. Logical Reasoning (Series, Syllogisms, Blood Relations)")
    print("3. Verbal Ability (Vocabulary, Sentence Correction, Grammar)")
    print("4. Coding & Pseudocode (C/Python, Output Prediction, Complexity)")
    print("5. Mixed / All Domains")
    
    choice = input(f"{Style.BOLD}Select (1-5) [Default 5]: {Style.RESET}").strip()
    cat_map = {
        '1': 'quantitative',
        '2': 'logical',
        '3': 'verbal',
        '4': 'coding',
        '5': None
    }
    cat = cat_map.get(choice, None)
    
    streak = 0
    total_practiced = 0
    correct_count = 0

    while True:
        q = engine.get_next_question(category=cat)
        if not q:
            print("No questions available for this filter.")
            break
            
        display_question(q)
        
        start_t = time.time()
        user_input = input(f"{Style.BOLD}Your Answer (A/B/C/D) or 'H' for Hint, 'Q' to Quit: {Style.RESET}").strip().upper()
        elapsed = time.time() - start_t
        
        if user_input == 'Q':
            break
            
        if user_input == 'H':
            print(f"\n{Style.YELLOW}[HINT]{Style.RESET} Topic: {q.get('topic')} | Focus on elimination of unlikely options.")
            user_input = input(f"{Style.BOLD}Now enter your answer (A/B/C/D): {Style.RESET}").strip().upper()
            
        if user_input not in ['A', 'B', 'C', 'D']:
            print(f"{Style.YELLOW}Skipping question.{Style.RESET}")
            continue

        result = engine.evaluate_answer(q, user_input, elapsed)
        total_practiced += 1
        
        if result['is_correct']:
            streak += 1
            correct_count += 1
            print(f"\n{Style.GREEN}{Style.BOLD}CORRECT! (+1 point){Style.RESET} Time: {result['time_taken_sec']}s | Streak: {streak} 🔥")
        else:
            streak = 0
            print(f"\n{Style.RED}{Style.BOLD}INCORRECT!{Style.RESET} You chose ({user_input}), but Correct Answer is ({result['correct_answer']}). Time: {result['time_taken_sec']}s")

        print(f"\n{Style.CYAN}{Style.BOLD}Explanation:{Style.RESET}")
        print(f"{result['explanation']}\n")
        
        cont = input(f"{Style.DIM}Press Enter for Next Question, or 'Q' to return to menu...{Style.RESET}").strip().upper()
        if cont == 'Q':
            break

    if total_practiced > 0:
        acc = (correct_count / total_practiced) * 100
        print(f"\n{Style.BOLD}Session Summary: {correct_count}/{total_practiced} correct ({acc:.1f}% accuracy){Style.RESET}\n")

def run_mock_test_mode():
    print(f"\n{Style.BOLD}{Style.CYAN}--- Placement Company Mock Test Simulator ---{Style.RESET}")
    print("Available Company Test Profiles:")
    profiles = list(COMPANY_PROFILES.keys())
    for idx, comp in enumerate(profiles, 1):
        prof = COMPANY_PROFILES[comp]
        print(f"{idx}. {prof['name']} - {len(prof['sections'])} Sections ({', '.join(prof['sections'])})")

    sel = input(f"\n{Style.BOLD}Select Company (1-{len(profiles)}) [Default 1]: {Style.RESET}").strip()
    try:
        comp_key = profiles[int(sel) - 1]
    except (ValueError, IndexError):
        comp_key = "TCS"
        
    prof = COMPANY_PROFILES[comp_key]
    print(f"\n{Style.GREEN}Launching {prof['name']}!{Style.RESET}")
    print(f"{Style.DIM}{prof['description']}{Style.RESET}")
    
    q_count_str = input(f"{Style.BOLD}Number of Questions (e.g. 10, 15, 20) [Default 12]: {Style.RESET}").strip()
    try:
        q_count = int(q_count_str)
        if q_count < 4:
            q_count = 4
    except ValueError:
        q_count = 12

    mock = MockTestEngine(company=comp_key, total_questions=q_count)
    print(f"\nTest Started! You have {len(mock.questions)} questions across all key sections.")
    print("Type A, B, C, or D for each question, or S to Skip.\n")

    for idx, q in enumerate(mock.questions):
        display_question(q, idx + 1, len(mock.questions))
        
        t0 = time.time()
        ans = input(f"{Style.BOLD}[Q{idx+1}/{len(mock.questions)}] Your Answer (A/B/C/D or S to skip): {Style.RESET}").strip().upper()
        t_spent = time.time() - t0
        
        if ans in ['A', 'B', 'C', 'D']:
            mock.submit_answer(idx, ans, t_spent)
        else:
            mock.submit_answer(idx, "", t_spent)

    print(f"\n{Style.CYAN}{Style.BOLD}Submitting and evaluating test...{Style.RESET}")
    report = mock.finalize_test()

    print("\n" + "=" * 80)
    print(f"{Style.BOLD}{Style.CYAN}           MOCK TEST REPORT CARD: {report['test_title']}{Style.RESET}")
    print("=" * 80)
    print(f"Total Questions : {report['total_questions']}")
    print(f"Correct Answers : {Style.GREEN}{report['correct_count']}{Style.RESET}")
    print(f"Incorrect/Skip  : {Style.RED}{report['incorrect_count']}{Style.RESET}")
    print(f"Accuracy Rate   : {Style.BOLD}{report['accuracy_percent']}%{Style.RESET}")
    print(f"Total Time      : {report['total_time_sec']} seconds")
    print(f"Performance     : {Style.YELLOW}{Style.BOLD}{report['verdict']}{Style.RESET}")
    print("-" * 80)
    print(f"{Style.BOLD}Sectional Breakdown:{Style.RESET}")
    for sec, stats in report['sectional_breakdown'].items():
        s_tot = stats['total']
        s_cor = stats['correct']
        s_acc = (s_cor / s_tot * 100) if s_tot > 0 else 0
        print(f"  • {sec.upper():<15}: {s_cor}/{s_tot} correct ({s_acc:.1f}%)")
    print("=" * 80)

    rev = input(f"\n{Style.BOLD}Would you like to review solutions for all questions? (y/n): {Style.RESET}").strip().lower()
    if rev == 'y':
        for item in report['detailed_review']:
            status_tag = f"{Style.GREEN}[CORRECT]{Style.RESET}" if item['is_correct'] else f"{Style.RED}[INCORRECT]{Style.RESET}"
            print(f"\nQ{item['index']}: {status_tag} {item['question']}")
            if item['code_snippet']:
                print(f"Code:\n{item['code_snippet']}")
            print(f"Your Choice: {item['user_choice']} | Correct: {item['correct_answer']}")
            print(f"{Style.DIM}Explanation: {item['explanation']}{Style.RESET}")
            print("-" * 60)

def run_dynamic_generator_mode():
    engine = PracticeEngine()
    print(f"\n{Style.BOLD}{Style.CYAN}--- Infinite Dynamic Question Generator ---{Style.RESET}")
    print("Generates fresh, never-seen-before mathematical & logical problems on the fly!")
    print("1. Dynamic Quantitative Aptitude (Trains, Work, P&C, Probability, Ages)")
    print("2. Dynamic Logical Reasoning (Series, Coding-Decoding, Direction Sense)")
    print("3. Dynamic Verbal Ability (High-frequency Placement Vocabulary & Grammar)")
    print("4. Dynamic Coding & Output Tracing (Pointers, Bitwise, Recursion, Complexity)")
    
    sel = input(f"{Style.BOLD}Choose Domain (1-4): {Style.RESET}").strip()
    cat_map = {'1': 'quantitative', '2': 'logical', '3': 'verbal', '4': 'coding'}
    cat = cat_map.get(sel, 'quantitative')
    
    while True:
        q = engine.get_next_question(category=cat, generate_dynamically=True)
        display_question(q)
        
        t0 = time.time()
        ans = input(f"{Style.BOLD}Your Answer (A/B/C/D) or 'Q' to Quit: {Style.RESET}").strip().upper()
        elapsed = time.time() - t0
        
        if ans == 'Q':
            break
            
        if ans in ['A', 'B', 'C', 'D']:
            res = engine.evaluate_answer(q, ans, elapsed)
            if res['is_correct']:
                print(f"\n{Style.GREEN}{Style.BOLD}CORRECT!{Style.RESET}")
            else:
                print(f"\n{Style.RED}{Style.BOLD}INCORRECT!{Style.RESET} Correct answer is ({res['correct_answer']}).")
            print(f"\n{Style.CYAN}Step-by-Step Mathematical Explanation:{Style.RESET}")
            print(f"{res['explanation']}\n")
            
        cont = input(f"{Style.DIM}Generate another question? (Enter=Yes, Q=Quit): {Style.RESET}").strip().upper()
        if cont == 'Q':
            break

def show_analytics():
    stats = get_performance_stats()
    db_sum = get_db_summary()
    
    print("\n" + "=" * 80)
    print(f"{Style.BOLD}{Style.CYAN}               PLACEMENT BOT PERFORMANCE ANALYTICS{Style.RESET}")
    print("=" * 80)
    print(f"Total Questions in Drive Database : {db_sum['total_questions']}")
    print(f"Your Total Attempts Recorded     : {stats['total_attempts']}")
    print(f"Overall Accuracy Rate            : {stats['overall_accuracy']}%")
    print(f"Average Response Time            : {stats['avg_time_sec']} seconds")
    print("-" * 80)
    
    print(f"{Style.BOLD}Domain-Wise Accuracy:{Style.RESET}")
    for cat, c_stat in stats.get('category_stats', {}).items():
        print(f"  • {cat.capitalize():<15}: {c_stat['correct']}/{c_stat['total']} ({c_stat['accuracy']}%) | Avg Time: {c_stat['avg_time']}s")
        
    print("-" * 80)
    print(f"{Style.BOLD}Diagnostic Weak Areas & Recommendations:{Style.RESET}")
    weak = stats.get('weak_topics', [])
    if weak:
        for w in weak:
            print(f"  ⚠️  {w['topic']} ({w['category']}): {w['accuracy']}% accuracy ({w['total']} attempts)")
        print(f"\n{Style.YELLOW}[Recommendation]{Style.RESET} Prioritize the weak topics above using Practice Mode!")
    else:
        print("  🎉 No critical weak areas detected yet! Complete more practice sessions to unlock insights.")
    print("=" * 80 + "\n")

def main():
    init_db()
    print_banner()
    
    while True:
        print(f"{Style.BOLD}Main Menu:{Style.RESET}")
        print("1. 🎯 Topic-wise Practice Mode (Instant feedback & explanations)")
        print("2. 🏆 Company Placement Mock Test (TCS, Infosys, Accenture, etc.)")
        print("3. ⚡ Dynamic Infinite Question Generator (Procedural math/code questions)")
        print("4. 💻 Coding & Pseudocode Sandbox (Output prediction & complexity)")
        print("5. 📊 Performance Analytics & Weak Area Diagnosis")
        print("6. 🌐 Launch Modern Web Practice Portal (Browser Dashboard)")
        print("7. 🚪 Exit")
        
        choice = input(f"\n{Style.BOLD}Select an option (1-7): {Style.RESET}").strip()
        
        if choice == '1':
            run_practice_mode()
        elif choice == '2':
            run_mock_test_mode()
        elif choice == '3':
            run_dynamic_generator_mode()
        elif choice == '4':
            # Coding sandbox: practice mode filtered to coding
            engine = PracticeEngine()
            print(f"\n{Style.BOLD}{Style.CYAN}--- Coding & Pseudocode Practice Sandbox ---{Style.RESET}")
            while True:
                q = engine.get_next_question(category='coding')
                display_question(q)
                ans = input(f"{Style.BOLD}Your Answer (A/B/C/D) or 'Q' to return: {Style.RESET}").strip().upper()
                if ans == 'Q':
                    break
                if ans in ['A', 'B', 'C', 'D']:
                    res = engine.evaluate_answer(q, ans)
                    if res['is_correct']:
                        print(f"\n{Style.GREEN}{Style.BOLD}CORRECT!{Style.RESET}")
                    else:
                        print(f"\n{Style.RED}{Style.BOLD}INCORRECT! Correct is ({res['correct_answer']}){Style.RESET}")
                    print(f"Explanation: {res['explanation']}\n")
                if input("Next coding question? (Enter=Yes, Q=Quit): ").strip().upper() == 'Q':
                    break
        elif choice == '5':
            show_analytics()
        elif choice == '6':
            print(f"\n{Style.GREEN}Launching Placement Practice Web Portal on http://localhost:8080...{Style.RESET}")
            import subprocess
            subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "app.py")])
            print("Web server started in background! Open http://localhost:8080 in your browser.")
            time.sleep(2)
        elif choice == '7':
            print(f"\n{Style.CYAN}Thank you for preparing with Placement Aptitude Practice Bot! All the best! 🚀{Style.RESET}\n")
            sys.exit(0)
        else:
            print(f"{Style.RED}Invalid option. Please choose between 1 and 7.{Style.RESET}\n")

if __name__ == '__main__':
    main()
