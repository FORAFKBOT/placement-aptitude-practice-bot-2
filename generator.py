"""
generator.py - Dynamic Aptitude & Technical Question Generator
Generates infinite realistic practice questions across Quantitative, Logical, Verbal,
and Coding/Pseudocode with real-time computed solutions and step-by-step explanations.
"""

import random
import math

class QuestionGenerator:
    """Algorithmic question generator adhering to TCS, Infosys, Accenture, Wipro, and Cognizant placement patterns."""

    @staticmethod
    def generate_quantitative() -> dict:
        """Generates a dynamic Quantitative Aptitude question with computed step-by-step math."""
        generators = [
            QuestionGenerator._gen_speed_time_distance,
            QuestionGenerator._gen_time_and_work,
            QuestionGenerator._gen_profit_loss,
            QuestionGenerator._gen_simple_compound_interest,
            QuestionGenerator._gen_ages_ratio,
            QuestionGenerator._gen_probability,
            QuestionGenerator._gen_permutations_combinations,
            QuestionGenerator._gen_percentages
        ]
        return random.choice(generators)()

    @staticmethod
    def _gen_speed_time_distance() -> dict:
        # Train passing a pole / platform
        speed_kmh = random.choice([36, 54, 72, 90, 108])
        length_m = random.choice([100, 150, 200, 250, 300])
        speed_ms = speed_kmh * 5 / 18
        time_sec = length_m / speed_ms
        
        q_text = (f"A train of length {length_m} meters runs at a constant speed of {speed_kmh} km/hr. "
                  f"How much time will it take to pass an electric pole completely?")
        correct_val = f"{time_sec:.0f} seconds" if time_sec.is_integer() else f"{time_sec:.1f} seconds"
        
        # Distractors
        distractors = [
            f"{time_sec + 2:.0f} seconds",
            f"{max(1, time_sec - 2):.0f} seconds",
            f"{time_sec * 1.5:.0f} seconds"
        ]
        options_list = list(set([correct_val] + distractors))
        while len(options_list) < 4:
            options_list.append(f"{random.randint(5, 40)} seconds")
        random.shuffle(options_list)
        
        opt_keys = ['A', 'B', 'C', 'D']
        options = {opt_keys[i]: options_list[i] for i in range(4)}
        correct_opt = [k for k, v in options.items() if v == correct_val][0]
        
        explanation = (
            f"Step 1: Convert speed from km/hr to m/s:\n"
            f"Speed = {speed_kmh} * (5/18) = {speed_ms:.1f} m/s.\n"
            f"Step 2: Time = Distance / Speed.\n"
            f"Here Distance = Length of the train = {length_m} meters.\n"
            f"Time = {length_m} / {speed_ms:.1f} = {correct_val}."
        )
        return {
            'category': 'quantitative',
            'company': random.choice(['TCS', 'Infosys', 'Cognizant', 'Accenture']),
            'topic': 'Speed, Time & Distance',
            'difficulty': 'Easy' if time_sec.is_integer() else 'Medium',
            'question': q_text,
            'code_snippet': '',
            'options': options,
            'answer': correct_opt,
            'explanation': explanation,
            'source': 'Dynamic Generator (Speed & Distance Pattern)'
        }

    @staticmethod
    def _gen_time_and_work() -> dict:
        # A takes X days, B takes Y days. Together?
        x = random.choice([10, 12, 15, 20, 24, 30])
        y = random.choice([15, 20, 30, 40, 60])
        total_work = math.lcm(x, y)
        rate_a = total_work // x
        rate_b = total_work // y
        combined_rate = rate_a + rate_b
        together_days = total_work / combined_rate
        
        correct_val = f"{together_days:.1f} days" if not together_days.is_integer() else f"{int(together_days)} days"
        distractors = [
            f"{math.ceil(together_days) + 2} days",
            f"{max(1, int(together_days) - 1)} days",
            f"{(x + y) // 2} days"
        ]
        opts = list(set([correct_val] + distractors))
        while len(opts) < 4:
            opts.append(f"{random.randint(4, 25)} days")
        random.shuffle(opts)
        
        opt_keys = ['A', 'B', 'C', 'D']
        options = {opt_keys[i]: opts[i] for i in range(4)}
        correct_opt = [k for k, v in options.items() if v == correct_val][0]
        
        explanation = (
            f"1 day's work of Person A = 1/{x}.\n"
            f"1 day's work of Person B = 1/{y}.\n"
            f"Combined 1 day's work = 1/{x} + 1/{y} = ({rate_a} + {rate_b})/{total_work} = {combined_rate}/{total_work}.\n"
            f"Total days required = {total_work}/{combined_rate} = {correct_val}."
        )
        return {
            'category': 'quantitative',
            'company': random.choice(['Accenture', 'Capgemini', 'Wipro']),
            'topic': 'Time & Work',
            'difficulty': 'Medium',
            'question': f"Person A can complete a project alone in {x} days, while Person B can complete the same project alone in {y} days. Working together, in how many days will they finish the project?",
            'code_snippet': '',
            'options': options,
            'answer': correct_opt,
            'explanation': explanation,
            'source': 'Dynamic Generator (Time & Work Pattern)'
        }

    @staticmethod
    def _gen_profit_loss() -> dict:
        cp = random.choice([400, 500, 600, 750, 800, 1000, 1200])
        profit_pct = random.choice([10, 15, 20, 25, 30])
        sp = int(cp * (1 + profit_pct / 100))
        
        q_text = f"An article was purchased for Rs. {cp} and sold at a profit of {profit_pct}%. What was the selling price?"
        correct_val = f"Rs. {sp}"
        distractors = [f"Rs. {sp - 50}", f"Rs. {sp + 50}", f"Rs. {int(cp * (1 + (profit_pct - 5) / 100))}"]
        
        opts = list(set([correct_val] + distractors))
        while len(opts) < 4:
            opts.append(f"Rs. {random.randint(cp, cp * 2)}")
        random.shuffle(opts)
        
        opt_keys = ['A', 'B', 'C', 'D']
        options = {opt_keys[i]: opts[i] for i in range(4)}
        correct_opt = [k for k, v in options.items() if v == correct_val][0]
        
        explanation = (
            f"Selling Price = Cost Price * (1 + Profit% / 100)\n"
            f"SP = {cp} * (1 + {profit_pct}/100) = {cp} * {1 + profit_pct/100:.2f} = Rs. {sp}."
        )
        return {
            'category': 'quantitative',
            'company': random.choice(['TCS', 'Infosys', 'Cognizant']),
            'topic': 'Profit & Loss',
            'difficulty': 'Easy',
            'question': q_text,
            'code_snippet': '',
            'options': options,
            'answer': correct_opt,
            'explanation': explanation,
            'source': 'Dynamic Generator (Profit & Loss Pattern)'
        }

    @staticmethod
    def _gen_simple_compound_interest() -> dict:
        p = random.choice([5000, 10000, 15000, 20000])
        r = random.choice([5, 8, 10, 12])
        t = random.choice([2, 3])
        si = (p * r * t) // 100
        
        q_text = f"Find the Simple Interest on a principal of Rs. {p:,} at an annual interest rate of {r}% for {t} years."
        correct_val = f"Rs. {si:,}"
        distractors = [f"Rs. {si + 200:,}", f"Rs. {max(100, si - 200):,}", f"Rs. {si * 2:,}"]
        
        opts = list(set([correct_val] + distractors))
        while len(opts) < 4:
            opts.append(f"Rs. {random.randint(500, 5000):,}")
        random.shuffle(opts)
        
        opt_keys = ['A', 'B', 'C', 'D']
        options = {opt_keys[i]: opts[i] for i in range(4)}
        correct_opt = [k for k, v in options.items() if v == correct_val][0]
        
        explanation = f"Simple Interest = (P * R * T) / 100 = ({p} * {r} * {t}) / 100 = Rs. {si:,}."
        return {
            'category': 'quantitative',
            'company': random.choice(['Capgemini', 'AMCAT', 'Wipro']),
            'topic': 'Simple & Compound Interest',
            'difficulty': 'Easy',
            'question': q_text,
            'code_snippet': '',
            'options': options,
            'answer': correct_opt,
            'explanation': explanation,
            'source': 'Dynamic Generator (Interest Pattern)'
        }

    @staticmethod
    def _gen_ages_ratio() -> dict:
        # Ratio of ages of A and B is r1:r2. After y years, sum is S.
        k = random.randint(3, 8)
        r1, r2 = 3, 5
        age_a = r1 * k
        age_b = r2 * k
        future_years = random.choice([4, 5, 6])
        future_sum = (age_a + future_years) + (age_b + future_years)
        
        q_text = (f"The ratio of the present ages of Rahul and Amit is 3:5. "
                  f"In {future_years} years, the sum of their ages will be {future_sum} years. "
                  f"What is the present age of Rahul?")
        correct_val = f"{age_a} years"
        distractors = [f"{age_b} years", f"{age_a + 4} years", f"{max(5, age_a - 4)} years"]
        
        opts = list(set([correct_val] + distractors))
        while len(opts) < 4:
            opts.append(f"{random.randint(15, 45)} years")
        random.shuffle(opts)
        
        opt_keys = ['A', 'B', 'C', 'D']
        options = {opt_keys[i]: opts[i] for i in range(4)}
        correct_opt = [k for k, v in options.items() if v == correct_val][0]
        
        explanation = (
            f"Let present ages be 3x and 5x.\n"
            f"After {future_years} years: (3x + {future_years}) + (5x + {future_years}) = {future_sum}\n"
            f"8x + {future_years * 2} = {future_sum} => 8x = {future_sum - future_years * 2} => x = {k}.\n"
            f"Rahul's present age = 3 * {k} = {age_a} years."
        )
        return {
            'category': 'quantitative',
            'company': random.choice(['Cognizant', 'eLitmus', 'TCS']),
            'topic': 'Ratios, Proportions & Ages',
            'difficulty': 'Medium',
            'question': q_text,
            'code_snippet': '',
            'options': options,
            'answer': correct_opt,
            'explanation': explanation,
            'source': 'Dynamic Generator (Ages & Ratio Pattern)'
        }

    @staticmethod
    def _gen_probability() -> dict:
        # Two dice rolled, sum equals S
        s = random.choice([7, 8, 9, 10, 11])
        # Count ways
        ways = sum(1 for d1 in range(1, 7) for d2 in range(1, 7) if d1 + d2 == s)
        g = math.gcd(ways, 36)
        num = ways // g
        den = 36 // g
        
        correct_val = f"{num}/{den}"
        distractors = [f"{num + 1}/{den}", f"{max(1, num - 1)}/{den}", f"{ways}/30"]
        opts = list(set([correct_val] + distractors))
        while len(opts) < 4:
            opts.append(f"1/{random.randint(2, 12)}")
        random.shuffle(opts)
        
        opt_keys = ['A', 'B', 'C', 'D']
        options = {opt_keys[i]: opts[i] for i in range(4)}
        correct_opt = [k for k, v in options.items() if v == correct_val][0]
        
        favorable_pairs = [(d1, d2) for d1 in range(1, 7) for d2 in range(1, 7) if d1 + d2 == s]
        explanation = (
            f"Total outcomes when two fair dice are thrown = 6 * 6 = 36.\n"
            f"Favorable outcomes summing to {s}: {favorable_pairs} (Total {ways} pairs).\n"
            f"Probability = {ways}/36 = {num}/{den}."
        )
        return {
            'category': 'quantitative',
            'company': random.choice(['TCS', 'Infosys', 'Capgemini']),
            'topic': 'Probability',
            'difficulty': 'Medium',
            'question': f"Two unbiased dice are rolled simultaneously. What is the probability of getting a sum of exactly {s}?",
            'code_snippet': '',
            'options': options,
            'answer': correct_opt,
            'explanation': explanation,
            'source': 'Dynamic Generator (Probability Pattern)'
        }

    @staticmethod
    def _gen_permutations_combinations() -> dict:
        word = random.choice(["LEADER", "DETAIL", "DESIGN", "VECTOR", "SYSTEM"])
        chars = list(word)
        n = len(chars)
        # Check repeats
        freq = {}
        for c in chars:
            freq[c] = freq.get(c, 0) + 1
        denom = 1
        for f in freq.values():
            denom *= math.factorial(f)
        total_ways = math.factorial(n) // denom
        
        correct_val = f"{total_ways:,}"
        distractors = [f"{total_ways // 2:,}", f"{total_ways * 2:,}", f"{math.factorial(n):,}"]
        opts = list(set([correct_val] + distractors))
        while len(opts) < 4:
            opts.append(f"{random.randint(120, 5000):,}")
        random.shuffle(opts)
        
        opt_keys = ['A', 'B', 'C', 'D']
        options = {opt_keys[i]: opts[i] for i in range(4)}
        correct_opt = [k for k, v in options.items() if v == correct_val][0]
        
        explanation = (
            f"The word '{word}' contains {n} letters.\n"
            f"Formula: n! / (p1! * p2!...) where p represents counts of repeating letters.\n"
            f"Total arrangements = {n}! / {denom} = {total_ways:,}."
        )
        return {
            'category': 'quantitative',
            'company': random.choice(['Infosys', 'TCS', 'eLitmus']),
            'topic': 'Permutations & Combinations',
            'difficulty': 'Medium',
            'question': f"In how many different ways can the letters of the word '{word}' be arranged?",
            'code_snippet': '',
            'options': options,
            'answer': correct_opt,
            'explanation': explanation,
            'source': 'Dynamic Generator (Permutation Pattern)'
        }

    @staticmethod
    def _gen_percentages() -> dict:
        p_increase = random.choice([20, 25, 50])
        # If price increases by P%, by how much % must consumption be reduced so expenditure remains same?
        # Formula: (P / (100 + P)) * 100
        reduction = (p_increase / (100 + p_increase)) * 100
        correct_val = f"{reduction:.2f}%" if not reduction.is_integer() else f"{int(reduction)}%"
        
        distractors = [f"{p_increase}%", f"{p_increase - 5}%", f"{reduction + 5:.1f}%"]
        opts = list(set([correct_val] + distractors))
        while len(opts) < 4:
            opts.append(f"{random.randint(10, 40)}%")
        random.shuffle(opts)
        
        opt_keys = ['A', 'B', 'C', 'D']
        options = {opt_keys[i]: opts[i] for i in range(4)}
        correct_opt = [k for k, v in options.items() if v == correct_val][0]
        
        explanation = (
            f"Standard Percentage Formula:\n"
            f"Reduction in consumption % = [r / (100 + r)] * 100\n"
            f"= [{p_increase} / (100 + {p_increase})] * 100 = [{p_increase} / {100 + p_increase}] * 100 = {correct_val}."
        )
        return {
            'category': 'quantitative',
            'company': random.choice(['Accenture', 'Cognizant', 'Capgemini']),
            'topic': 'Percentages',
            'difficulty': 'Easy',
            'question': f"If the price of sugar increases by {p_increase}%, by what percentage must a household reduce its consumption so that the total expenditure remains unchanged?",
            'code_snippet': '',
            'options': options,
            'answer': correct_opt,
            'explanation': explanation,
            'source': 'Dynamic Generator (Percentage Pattern)'
        }

    @staticmethod
    def generate_logical() -> dict:
        """Generates dynamic Logical Reasoning questions (Series, Blood Relations, Direction Sense)."""
        generators = [
            QuestionGenerator._gen_number_series,
            QuestionGenerator._gen_letter_coding,
            QuestionGenerator._gen_blood_relation,
            QuestionGenerator._gen_direction_sense,
            QuestionGenerator._gen_syllogism
        ]
        return random.choice(generators)()

    @staticmethod
    def _gen_number_series() -> dict:
        # Pattern: Squares + k or x2 + 1
        base = random.randint(2, 5)
        diff = random.choice([3, 5, 7])
        series = []
        curr = base
        for _ in range(5):
            series.append(curr)
            curr += diff
            diff += 2  # difference increases by 2
            
        next_val = curr
        q_text = f"Find the next number in the series: {', '.join(map(str, series))}, ?"
        correct_val = str(next_val)
        distractors = [str(next_val + 2), str(next_val - 3), str(next_val + 4)]
        
        opts = list(set([correct_val] + distractors))
        while len(opts) < 4:
            opts.append(str(random.randint(curr - 10, curr + 20)))
        random.shuffle(opts)
        
        opt_keys = ['A', 'B', 'C', 'D']
        options = {opt_keys[i]: opts[i] for i in range(4)}
        correct_opt = [k for k, v in options.items() if v == correct_val][0]
        
        explanation = (
            f"The differences between consecutive terms form an arithmetic progression:\n"
            f"Differences: {[series[i+1] - series[i] for i in range(len(series)-1)]}...\n"
            f"The next difference is {diff}.\n"
            f"Hence next term = {series[-1]} + {diff} = {next_val}."
        )
        return {
            'category': 'logical',
            'company': random.choice(['TCS', 'Infosys', 'Wipro']),
            'topic': 'Series & Pattern Completion',
            'difficulty': 'Medium',
            'question': q_text,
            'code_snippet': '',
            'options': options,
            'answer': correct_opt,
            'explanation': explanation,
            'source': 'Dynamic Generator (Number Series Pattern)'
        }

    @staticmethod
    def _gen_letter_coding() -> dict:
        word = random.choice(["CLOUD", "SMART", "BRAIN", "POWER", "LIGHT"])
        shift = random.choice([1, 2, 3])
        coded = "".join(chr((ord(c) - 65 + shift) % 26 + 65) for c in word)
        
        test_word = random.choice(["DREAM", "PLANT", "SOLVE", "TRACE"])
        test_coded = "".join(chr((ord(c) - 65 + shift) % 26 + 65) for c in test_word)
        
        q_text = f"In a certain code language, if '{word}' is written as '{coded}', how will '{test_word}' be written in that same code?"
        correct_val = test_coded
        distractors = [
            "".join(chr((ord(c) - 65 + shift + 1) % 26 + 65) for c in test_word),
            "".join(chr((ord(c) - 65 + shift - 1) % 26 + 65) for c in test_word),
            "".join(chr((ord(c) - 65 + shift + 2) % 26 + 65) for c in test_word)
        ]
        opts = list(set([correct_val] + distractors))
        while len(opts) < 4:
            opts.append("".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=len(test_word))))
        random.shuffle(opts)
        
        opt_keys = ['A', 'B', 'C', 'D']
        options = {opt_keys[i]: opts[i] for i in range(4)}
        correct_opt = [k for k, v in options.items() if v == correct_val][0]
        
        explanation = (
            f"Pattern Analysis:\n"
            f"Each letter in '{word}' is shifted forward by +{shift} positions in the alphabetical order.\n"
            f"Applying the +{shift} shift to '{test_word}':\n"
            f"{' -> '.join(f'{c}+{shift}={chr((ord(c)-65+shift)%26+65)}' for c in test_word)}\n"
            f"Result: {test_coded}."
        )
        return {
            'category': 'logical',
            'company': random.choice(['Capgemini', 'Cognizant', 'Accenture']),
            'topic': 'Coding & Decoding',
            'difficulty': 'Easy',
            'question': q_text,
            'code_snippet': '',
            'options': options,
            'answer': correct_opt,
            'explanation': explanation,
            'source': 'Dynamic Generator (Coding-Decoding Pattern)'
        }

    @staticmethod
    def _gen_blood_relation() -> dict:
        relations = [
            ("Pointing to a photograph, Rohit said, 'She is the daughter of my grandfather's only son.' How is Rohit related to the girl in the photograph?",
             "Brother", ["Father", "Cousin", "Uncle"],
             "Grandfather's only son is Rohit's father. The daughter of Rohit's father is Rohit's sister. Hence Rohit is her Brother."),
            ("Introducing a man, a woman said, 'His mother is the only daughter of my mother.' How is the woman related to the man?",
             "Mother", ["Sister", "Aunt", "Grandmother"],
             "The only daughter of my mother is the woman herself. Her mother is the man's mother, so she is the Mother of the man."),
            ("P is the brother of Q. R is the father of P. S is the brother of T. T is the daughter of Q. Who is the uncle of S?",
             "P", ["R", "Q", "T"],
             "Since T is the daughter of Q and S is brother of T, S is the son of Q. P is the brother of Q (parent of S). Therefore, P is the maternal/paternal uncle of S.")
        ]
        q_text, correct_val, distractors, explanation = random.choice(relations)
        opts = list(set([correct_val] + distractors))
        random.shuffle(opts)
        opt_keys = ['A', 'B', 'C', 'D']
        options = {opt_keys[i]: opts[i] for i in range(4)}
        correct_opt = [k for k, v in options.items() if v == correct_val][0]
        
        return {
            'category': 'logical',
            'company': random.choice(['Infosys', 'TCS', 'AMCAT']),
            'topic': 'Blood Relations',
            'difficulty': 'Medium',
            'question': q_text,
            'code_snippet': '',
            'options': options,
            'answer': correct_opt,
            'explanation': explanation,
            'source': 'Dynamic Generator (Blood Relations Pattern)'
        }

    @staticmethod
    def _gen_direction_sense() -> dict:
        d1 = random.choice([6, 8, 12])
        d2 = random.choice([8, 6, 9])
        hyp = int(math.hypot(d1, d2))
        
        q_text = (f"A person walks {d1} km toward North, then takes a 90-degree right turn and walks {d2} km toward East. "
                  f"How far is the person from the starting point?")
        correct_val = f"{hyp} km"
        distractors = [f"{d1 + d2} km", f"{abs(d1 - d2)} km", f"{hyp + 3} km"]
        opts = list(set([correct_val] + distractors))
        while len(opts) < 4:
            opts.append(f"{random.randint(5, 20)} km")
        random.shuffle(opts)
        
        opt_keys = ['A', 'B', 'C', 'D']
        options = {opt_keys[i]: opts[i] for i in range(4)}
        correct_opt = [k for k, v in options.items() if v == correct_val][0]
        
        explanation = (
            f"Using Pythagoras Theorem for right-angled displacement:\n"
            f"Distance = sqrt(North^2 + East^2) = sqrt({d1}^2 + {d2}^2) = sqrt({d1**2} + {d2**2}) = sqrt({d1**2 + d2**2}) = {hyp} km."
        )
        return {
            'category': 'logical',
            'company': random.choice(['Cognizant', 'Capgemini', 'Wipro']),
            'topic': 'Direction Sense Test',
            'difficulty': 'Easy',
            'question': q_text,
            'code_snippet': '',
            'options': options,
            'answer': correct_opt,
            'explanation': explanation,
            'source': 'Dynamic Generator (Direction Sense Pattern)'
        }

    @staticmethod
    def _gen_syllogism() -> dict:
        items = [
            ("Statements:\n1. All mangoes are golden.\n2. No golden things are sour.\nConclusions:\nI. All mangoes are sour.\nII. No mangoes are sour.",
             "Only Conclusion II follows",
             ["Only Conclusion I follows", "Both I and II follow", "Neither I nor II follows"],
             "All mangoes are in the subset of golden things. Since golden things have no intersection with sour things, mangoes also have zero intersection with sour things. Hence 'No mangoes are sour' definitely follows."),
            ("Statements:\n1. Some dogs are friendly.\n2. All friendly animals are loyal.\nConclusions:\nI. Some dogs are loyal.\nII. All loyal animals are dogs.",
             "Only Conclusion I follows",
             ["Only Conclusion II follows", "Both I and II follow", "Neither I nor II follows"],
             "Some dogs are friendly, and all friendly animals are loyal. Thus the dogs that are friendly must also be loyal (Some dogs are loyal). Conclusion II assumes a converse subset which is invalid.")
        ]
        q_text, correct_val, distractors, explanation = random.choice(items)
        opts = list(set([correct_val] + distractors))
        random.shuffle(opts)
        opt_keys = ['A', 'B', 'C', 'D']
        options = {opt_keys[i]: opts[i] for i in range(4)}
        correct_opt = [k for k, v in options.items() if v == correct_val][0]
        
        return {
            'category': 'logical',
            'company': random.choice(['TCS', 'Infosys', 'Accenture']),
            'topic': 'Syllogisms & Verbal Reasoning',
            'difficulty': 'Medium',
            'question': q_text,
            'code_snippet': '',
            'options': options,
            'answer': correct_opt,
            'explanation': explanation,
            'source': 'Dynamic Generator (Syllogism Pattern)'
        }

    @staticmethod
    def generate_verbal() -> dict:
        """Generates dynamic Verbal Ability questions (Synonyms, Antonyms, Spotting Errors, Sentence Fillers)."""
        vocab_items = [
            ("Choose the word that is MOST SIMILAR in meaning (Synonym) to 'EPHEMERAL':",
             "Transient", ["Eternal", "Substantial", "Enduring"],
             "'Ephemeral' means lasting for a very short time. 'Transient' is an exact synonym."),
            ("Choose the word that is MOST SIMILAR in meaning (Synonym) to 'TENACIOUS':",
             "Persistent", ["Fragile", "Timid", "Wavering"],
             "'Tenacious' means holding fast or keeping a firm grip; persistent."),
            ("Choose the word that is MOST OPPOSITE in meaning (Antonym) to 'METICULOUS':",
             "Careless", ["Diligent", "Accurate", "Fastidious"],
             "'Meticulous' means showing great attention to detail. The opposite is 'Careless'."),
            ("Choose the word that is MOST OPPOSITE in meaning (Antonym) to 'MITIGATE':",
             "Aggravate", ["Alleviate", "Assuage", "Diminish"],
             "'Mitigate' means to make less severe or serious. 'Aggravate' means to make more severe or worse."),
            ("Fill in the blank with the appropriate preposition:\n'The candidate was completely oblivious ______ the strict company policy.'",
             "to", ["with", "of", "from"],
             "The adjective 'oblivious' is standardly paired with the preposition 'to' or 'of' ('oblivious to')."),
            ("Identify the part of the sentence with a grammatical error:\n(A) Neither the manager / (B) nor the employees / (C) was present at the meeting / (D) yesterday.",
             "C", ["A", "B", "D"],
             "In 'neither... nor' constructions, the verb agrees with the closer subject. 'Employees' is plural, so it requires 'were present' instead of 'was present' (Part C)."),
            ("Choose the correctly spelt word:",
             "Accommodate", ["Acommodate", "Accomodate", "Acomodate"],
             "The correct spelling is 'Accommodate' with double 'c' and double 'm'.")
        ]
        q_text, correct_val, distractors, explanation = random.choice(vocab_items)
        opts = list(set([correct_val] + distractors))
        random.shuffle(opts)
        opt_keys = ['A', 'B', 'C', 'D']
        options = {opt_keys[i]: opts[i] for i in range(4)}
        correct_opt = [k for k, v in options.items() if v == correct_val][0]
        
        return {
            'category': 'verbal',
            'company': random.choice(['TCS', 'Infosys', 'Cognizant', 'eLitmus']),
            'topic': 'Synonyms & Antonyms' if 'SIMILAR' in q_text or 'OPPOSITE' in q_text else 'Sentence Correction & Grammar',
            'difficulty': 'Medium',
            'question': q_text,
            'code_snippet': '',
            'options': options,
            'answer': correct_opt,
            'explanation': explanation,
            'source': 'Dynamic Generator (Verbal Ability Pattern)'
        }

    @staticmethod
    def generate_coding() -> dict:
        """Generates dynamic Technical & Coding output prediction / complexity questions."""
        coding_items = [
            (
                "What will be the output of the following C code snippet?",
                "#include <stdio.h>\nint main() {\n    int a = 5;\n    int b = ++a + a++;\n    printf(\"%d, %d\", a, b);\n    return 0;\n}",
                "7, 12",
                ["6, 11", "7, 11", "6, 12"],
                "Pre-increment ++a makes a = 6 immediately. Then in a++, current value 6 is used in addition (6 + 6 = 12), and a is incremented to 7 afterwards. Hence a = 7, b = 12.",
                "Pointers & Increment Operators"
            ),
            (
                "What is the output of the following bitwise operation in C / Python?",
                "int x = 12; // binary 1100\nint y = 10; // binary 1010\nint z = x ^ y; // XOR operation\nprintf(\"%d\", z);",
                "6",
                ["2", "14", "8"],
                "Bitwise XOR (^) returns 1 where corresponding bits differ:\n1100 ^ 1010 = 0110 in binary, which is 6 in decimal.",
                "Bitwise Operators & Logic"
            ),
            (
                "What is the worst-case time complexity of searching an element in a Balanced Binary Search Tree (AVL Tree)?",
                "",
                "O(log N)",
                ["O(N)", "O(N log N)", "O(1)"],
                "In a height-balanced BST such as an AVL tree, the height is strictly bounded by O(log N). Searching traverses from root to leaf taking at most O(log N) operations.",
                "Data Structures & Complexity"
            ),
            (
                "What will be printed by the following recursive function for fun(4)?",
                "int fun(int n) {\n    if (n <= 1) return 1;\n    return n + fun(n - 1);\n}",
                "10",
                ["8", "24", "15"],
                "fun(4) = 4 + fun(3) = 4 + 3 + fun(2) = 4 + 3 + 2 + fun(1) = 4 + 3 + 2 + 1 = 10.",
                "Recursion & Call Stack"
            ),
            (
                "What is the output of the following pointer arithmetic in C?",
                "#include <stdio.h>\nint main() {\n    int arr[] = {10, 20, 30, 40};\n    int *ptr = arr;\n    printf(\"%d\", *(ptr + 2));\n    return 0;\n}",
                "30",
                ["10", "20", "40"],
                "ptr points to index 0 (10). ptr + 2 points to index 2 (arr[2]). Dereferencing *(ptr + 2) yields 30.",
                "Pointers & Memory Management"
            )
        ]
        q_text, snippet, correct_val, distractors, explanation, topic = random.choice(coding_items)
        opts = list(set([correct_val] + distractors))
        random.shuffle(opts)
        opt_keys = ['A', 'B', 'C', 'D']
        options = {opt_keys[i]: opts[i] for i in range(4)}
        correct_opt = [k for k, v in options.items() if v == correct_val][0]
        
        return {
            'category': 'coding',
            'company': random.choice(['TCS', 'Capgemini', 'Accenture', 'Infosys']),
            'topic': topic,
            'difficulty': 'Medium',
            'question': q_text,
            'code_snippet': snippet,
            'options': options,
            'answer': correct_opt,
            'explanation': explanation,
            'source': 'Dynamic Generator (Code Output Pattern)'
        }

    @staticmethod
    def generate_by_category(category: str) -> dict:
        """Route to appropriate generator by category."""
        category = category.lower()
        if category in ['quant', 'quantitative', 'math', 'arithmetic']:
            return QuestionGenerator.generate_quantitative()
        elif category in ['logical', 'reasoning', 'analytical']:
            return QuestionGenerator.generate_logical()
        elif category in ['verbal', 'english', 'reading']:
            return QuestionGenerator.generate_verbal()
        elif category in ['coding', 'pseudocode', 'technical', 'programming']:
            return QuestionGenerator.generate_coding()
        else:
            return random.choice([
                QuestionGenerator.generate_quantitative,
                QuestionGenerator.generate_logical,
                QuestionGenerator.generate_verbal,
                QuestionGenerator.generate_coding
            ])()
