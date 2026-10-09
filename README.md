# 🚀 Placement Aptitude Practice Bot

An intelligent, full-stack Placement Aptitude Practice Bot built in Python that generates and assesses **Quantitative Aptitude**, **Logical Reasoning**, **Verbal Ability**, and **Coding & Technical** questions.

The bot utilizes the official placement repository from Google Drive:
`https://drive.google.com/drive/folders/1NC5wLHUMUye5_5zHzSgTgXDUdVmh43ZU`

---

## 🌟 Key Features

1. **Multi-Domain Practice Engine**:
   - 📐 **Quantitative Aptitude**: Time & Work, Speed-Time-Distance, Profit & Loss, Percentages, P&C, Probability, Simple/Compound Interest, Ratios & Ages, Numbers.
   - 🧩 **Logical Reasoning**: Number & Letter Series, Syllogisms, Blood Relations, Direction Sense, Coding-Decoding, Seating & Ordering.
   - 📖 **Verbal Ability**: High-frequency Placement Vocabulary, Synonyms & Antonyms, Sentence Correction, Spotting Errors, Fill in the Blanks.
   - 💻 **Coding & Pseudocode**: C/Python/Java Output Tracing, Pointers, Bitwise Logic, Recursion, Time & Space Complexity, Data Structures.

2. **Google Drive Database Ingestion**:
   - Direct automated ingestion pipeline (`extractor.py`) parses questions, options, answer keys, and step-by-step explanations from TCS, Infosys, Accenture, Cognizant, Capgemini, Wipro, eLitmus, and AMCAT placement tests.
   - Stores all questions in indexed SQLite (`data/questions.db`) and JSON (`data/questions.json`).

3. **⚡ Infinite Algorithmic Question Generator (`generator.py`)**:
   - Beyond the database, the bot includes a procedural math & logic generator that creates never-seen-before questions with dynamic variables, mathematically computed solutions, and step-by-step explanations on the fly.

4. **🏆 Company-Specific Placement Mock Tests**:
   - Timed mock simulations modeled after major campus placement tests:
     - **TCS NQT** (Numerical, Reasoning, Verbal, Coding)
     - **Infosys Specialist / SE** (Mathematical Critical Thinking, Analytical, Pseudocode)
     - **Accenture Cognitive & Technical** (Abstract Reasoning, Critical Thinking, Tech)
     - **Cognizant GenC / GenC Next**
     - **Capgemini Assessment**
     - **Wipro NLTH**
     - **eLitmus pH Test**
   - Live timer, question palette, sectional breakdown, accuracy rate, cutoff readiness assessment, and solution review.

5. **📊 Diagnostic Analytics & Weak Area Diagnosis**:
   - Tracks every user attempt, speed per question, and sectional accuracy.
   - Automatically detects topics where accuracy falls below 60% and suggests personalized practice recommendations.

6. **Dual User Interface**:
   - **Interactive Terminal Bot (CLI)**: Beautiful ANSI colored terminal UI (`cli_bot.py`).
   - **Modern Web Dashboard**: Zero-dependency browser portal with dark theme, live timer, and instant feedback (`app.py` at `http://localhost:8080`).

---

## 📁 Project Structure

```
placement_aptitude_bot/
├── data/
│   ├── sample_pdfs/          # Downloaded PDF materials from Google Drive
│   ├── questions.db          # SQLite relational database (indexed questions & attempts)
│   ├── questions.json        # Curated questions database (JSON export)
│   └── drive_catalog.json    # Catalog of Google Drive folder hierarchy
├── extractor.py              # Automated PDF extractor and parsing pipeline
├── generator.py              # Dynamic algorithmic question generator
├── database.py               # SQLite schema, queries, attempt logging & analytics
├── engine.py                 # Practice sessions, company mock test simulator, report cards
├── cli_bot.py                # Interactive Terminal Bot
├── app.py                    # Lightweight Web server & REST API
├── static/
│   ├── style.css             # Modern dark-mode styling
│   └── app.js                # Frontend logic for quiz, mock tests, and analytics
├── templates/
│   └── index.html            # Web dashboard interface
├── test_bot.py               # Automated unit test suite
└── run_bot.bat               # Windows one-click launcher
```

---

## 🚀 Getting Started

### 1. Launch the Interactive Terminal Bot (CLI)
```bash
python cli_bot.py
```
Provides an interactive menu for:
- Topic-wise practice
- Company mock tests
- Infinite question generator
- Coding sandbox
- Diagnostic analytics

### 2. Launch the Web Browser Dashboard
```bash
python app.py
```
Then open **[http://localhost:8080](http://localhost:8080)** in any browser.

### 3. One-Click Launcher (Windows)
Double-click `run_bot.bat` or run:
```bat
run_bot.bat
```

### 4. Run the Test Suite
```bash
python test_bot.py
```

### 5. Re-Sync or Re-Extract Drive Questions
To re-process or update the question bank from the downloaded Google Drive files:
```bash
python extractor.py
python database.py
```

---

## 🛠️ Database Schema

### `questions` Table
- `id`: Unique Question ID
- `category`: `quantitative`, `logical`, `verbal`, or `coding`
- `company`: `TCS`, `Infosys`, `Accenture`, `Cognizant`, `Capgemini`, `Wipro`, `eLitmus`, `AMCAT`
- `topic`: e.g., "Speed, Time & Distance", "Blood Relations", "Pointers", etc.
- `difficulty`: `Easy`, `Medium`, `Hard`
- `question_text`: Complete problem statement
- `code_snippet`: Code block for technical/output questions
- `option_a`, `option_b`, `option_c`, `option_d`: Multiple-choice options
- `correct_answer`: `A`, `B`, `C`, or `D`
- `explanation`: Step-by-step mathematical or logical solution
- `source_file`: Originating document from the Google Drive repository
- `is_generated`: Flag (0 = Drive material, 1 = Dynamically generated)

### `user_attempts` & `test_sessions` Tables
- Store user responses, timestamps, response time in seconds, session IDs, sectional scores, and weak area indicators.
