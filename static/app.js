// app.js - Placement Aptitude Practice Bot Frontend Logic

let currentPracticeQuestion = null;
let practiceTimerInterval = null;
let practiceTimeSpent = 0.0;
let streak = 0;
let score = 0;

// Mock Test State
let activeMockData = null;
let currentMockIndex = 0;
let mockTimerInterval = null;
let mockTimeRemaining = 1800; // 30 mins in sec
let mockAnswers = {};

document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  loadDBSummary();
  loadNextPracticeQuestion();
  initMockEventListeners();
  initGeneratorEventListeners();
  initCodingSandbox();
});

// Navigation Tabs
function initNavigation() {
  const navItems = document.querySelectorAll('.nav-item');
  const panels = document.querySelectorAll('.tab-panel');
  const title = document.getElementById('pageTitle');

  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const tab = item.getAttribute('data-tab');
      navItems.forEach(n => n.classList.remove('active'));
      panels.forEach(p => p.classList.remove('active'));

      item.classList.add('active');
      const targetPanel = document.getElementById(`tab-${tab}`);
      if (targetPanel) targetPanel.classList.add('active');

      const titles = {
        practice: 'Practice Mode',
        mock: 'Company Placement Mock Tests',
        generator: 'Infinite Dynamic Generator',
        coding: 'Coding & Pseudocode Sandbox',
        analytics: 'Performance & Diagnostic Analytics'
      };
      if (title) title.innerText = titles[tab] || 'PlacementBot';

      if (tab === 'analytics') loadAnalytics();
      if (tab === 'coding' && !window.codingInitialized) loadNextCodingQuestion();
    });
  });

  document.getElementById('btnNextPractice')?.addEventListener('click', loadNextPracticeQuestion);
  document.getElementById('practiceCategorySelect')?.addEventListener('change', loadNextPracticeQuestion);
  document.getElementById('practiceCompanySelect')?.addEventListener('change', loadNextPracticeQuestion);
}

// Database Summary
async function loadDBSummary() {
  try {
    const res = await fetch('/api/summary');
    const data = await res.json();
    const countEl = document.getElementById('totalQuestionsCount');
    if (countEl && data.total_questions) {
      countEl.innerText = `${data.total_questions} Questions`;
    }
  } catch (e) {
    console.error('Error loading DB summary:', e);
  }
}

// PRACTICE MODE
async function loadNextPracticeQuestion() {
  clearInterval(practiceTimerInterval);
  practiceTimeSpent = 0.0;
  updatePracticeTimer();

  const cat = document.getElementById('practiceCategorySelect')?.value || '';
  const comp = document.getElementById('practiceCompanySelect')?.value || '';

  const expBox = document.getElementById('explanationBox');
  if (expBox) expBox.style.display = 'none';

  try {
    const res = await fetch(`/api/question?category=${encodeURIComponent(cat)}&company=${encodeURIComponent(comp)}`);
    const q = await res.json();
    currentPracticeQuestion = q;
    renderPracticeQuestion(q);

    practiceTimerInterval = setInterval(() => {
      practiceTimeSpent += 0.1;
      updatePracticeTimer();
    }, 100);
  } catch (e) {
    console.error('Error loading question:', e);
  }
}

function updatePracticeTimer() {
  const tEl = document.getElementById('questionTimer');
  if (tEl) tEl.innerText = `${practiceTimeSpent.toFixed(1)}s`;
}

function renderPracticeQuestion(q) {
  document.getElementById('qBadgeCategory').innerText = (q.category || 'GENERAL').toUpperCase();
  document.getElementById('qPillTopic').innerText = q.topic || 'General Aptitude';
  document.getElementById('qPillCompany').innerText = q.company || 'General';
  document.getElementById('qText').innerText = q.question || '';

  // Code snippet
  const codeBox = document.getElementById('qCodeBox');
  const codeText = document.getElementById('qCodeText');
  if (q.code_snippet && q.code_snippet.trim() !== '') {
    codeBox.style.display = 'block';
    codeText.innerText = q.code_snippet;
  } else {
    codeBox.style.display = 'none';
  }

  // Options
  const grid = document.getElementById('optionsGrid');
  grid.innerHTML = '';
  const opts = q.options || {};

  ['A', 'B', 'C', 'D'].forEach(key => {
    if (opts[key]) {
      const btn = document.createElement('button');
      btn.className = 'option-btn';
      btn.innerHTML = `<span class="option-key">${key}</span><span class="option-text">${opts[key]}</span>`;
      btn.onclick = () => submitPracticeAnswer(key, btn);
      grid.appendChild(btn);
    }
  });
}

async function submitPracticeAnswer(choice, btnElement) {
  if (!currentPracticeQuestion) return;
  clearInterval(practiceTimerInterval);

  // Disable all option buttons
  const allBtns = document.querySelectorAll('#optionsGrid .option-btn');
  allBtns.forEach(b => b.classList.add('disabled'));

  try {
    const res = await fetch('/api/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question_id: currentPracticeQuestion.id,
        user_choice: choice,
        time_taken_sec: practiceTimeSpent
      })
    });
    const result = await res.json();

    const expBox = document.getElementById('explanationBox');
    const expHead = document.getElementById('expHeader');
    const expBody = document.getElementById('expText');

    if (result.is_correct) {
      btnElement.classList.add('correct');
      streak++;
      score += 10;
      expHead.innerHTML = `✅ Correct! (Option ${result.correct_answer})`;
      expHead.style.color = '#22c55e';
    } else {
      btnElement.classList.add('wrong');
      streak = 0;
      // Highlight the correct one
      allBtns.forEach(b => {
        if (b.querySelector('.option-key').innerText === result.correct_answer) {
          b.classList.add('correct');
        }
      });
      expHead.innerHTML = `❌ Incorrect! Correct Answer: Option ${result.correct_answer}`;
      expHead.style.color = '#ef4444';
    }

    document.getElementById('streakCount').innerText = streak;
    document.getElementById('scoreCount').innerText = score;

    expBody.innerText = result.explanation || 'Refer to the standard placement problem solution.';
    expBox.style.display = 'block';
  } catch (e) {
    console.error('Error submitting answer:', e);
  }
}

// COMPANY MOCK TESTS
function initMockEventListeners() {
  document.querySelectorAll('.start-mock-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const comp = btn.getAttribute('data-comp');
      startMockTest(comp);
    });
  });

  document.getElementById('btnMockNext')?.addEventListener('click', () => {
    if (activeMockData && currentMockIndex < activeMockData.questions.length - 1) {
      currentMockIndex++;
      renderMockQuestion();
    }
  });

  document.getElementById('btnMockPrev')?.addEventListener('click', () => {
    if (activeMockData && currentMockIndex > 0) {
      currentMockIndex--;
      renderMockQuestion();
    }
  });

  document.getElementById('btnFinishMock')?.addEventListener('click', () => {
    if (confirm('Are you sure you want to finish and submit the test?')) {
      finishMockTest();
    }
  });

  document.getElementById('btnExitMock')?.addEventListener('click', () => {
    document.getElementById('mockResultView').style.display = 'none';
    document.getElementById('mockActiveView').style.display = 'none';
    document.getElementById('mockSetupView').style.display = 'block';
  });

  document.getElementById('btnReviewMock')?.addEventListener('click', () => {
    const revBox = document.getElementById('mockReviewContainer');
    revBox.style.display = revBox.style.display === 'none' ? 'block' : 'none';
  });
}

async function startMockTest(company) {
  try {
    const res = await fetch(`/api/mock/start?company=${company}&count=16`);
    const data = await res.json();
    activeMockData = data;
    currentMockIndex = 0;
    mockAnswers = {};

    document.getElementById('mockSetupView').style.display = 'none';
    document.getElementById('mockResultView').style.display = 'none';
    document.getElementById('mockActiveView').style.display = 'block';

    document.getElementById('mockTitleText').innerText = data.test_title || `${company} Mock Test`;

    // Start 30-min countdown
    mockTimeRemaining = 30 * 60;
    clearInterval(mockTimerInterval);
    mockTimerInterval = setInterval(() => {
      mockTimeRemaining--;
      const mins = Math.floor(mockTimeRemaining / 60);
      const secs = mockTimeRemaining % 60;
      document.getElementById('mockCountdownTimer').innerText = `⏳ ${mins}:${secs < 10 ? '0' : ''}${secs}`;
      if (mockTimeRemaining <= 0) {
        clearInterval(mockTimerInterval);
        finishMockTest();
      }
    }, 1000);

    renderMockPalette();
    renderMockQuestion();
  } catch (e) {
    console.error('Error starting mock test:', e);
  }
}

function renderMockPalette() {
  const grid = document.getElementById('mockPaletteGrid');
  grid.innerHTML = '';
  if (!activeMockData) return;

  activeMockData.questions.forEach((q, idx) => {
    const btn = document.createElement('button');
    btn.className = 'palette-btn';
    btn.innerText = idx + 1;
    if (idx === currentMockIndex) btn.classList.add('current');
    if (mockAnswers[idx]) btn.classList.add('answered');

    btn.onclick = () => {
      currentMockIndex = idx;
      renderMockQuestion();
    };
    grid.appendChild(btn);
  });
}

function renderMockQuestion() {
  if (!activeMockData) return;
  const q = activeMockData.questions[currentMockIndex];

  document.getElementById('mockBadgeCategory').innerText = (q.category || 'GENERAL').toUpperCase();
  document.getElementById('mockPillTopic').innerText = q.topic || 'Aptitude';
  document.getElementById('mockQuestionNumber').innerText = `Question ${currentMockIndex + 1} of ${activeMockData.questions.length}`;
  document.getElementById('mockQText').innerText = q.question;

  const codeBox = document.getElementById('mockCodeBox');
  const codeText = document.getElementById('mockCodeText');
  if (q.code_snippet && q.code_snippet.trim() !== '') {
    codeBox.style.display = 'block';
    codeText.innerText = q.code_snippet;
  } else {
    codeBox.style.display = 'none';
  }

  // Options
  const grid = document.getElementById('mockOptionsGrid');
  grid.innerHTML = '';
  const opts = q.options || {};

  ['A', 'B', 'C', 'D'].forEach(key => {
    if (opts[key]) {
      const btn = document.createElement('button');
      btn.className = 'option-btn';
      if (mockAnswers[currentMockIndex] === key) {
        btn.style.borderColor = '#38bdf8';
        btn.style.background = 'rgba(56, 189, 248, 0.15)';
      }
      btn.innerHTML = `<span class="option-key">${key}</span><span class="option-text">${opts[key]}</span>`;
      btn.onclick = () => {
        mockAnswers[currentMockIndex] = key;
        renderMockPalette();
        renderMockQuestion();
      };
      grid.appendChild(btn);
    }
  });

  renderMockPalette();
}

async function finishMockTest() {
  clearInterval(mockTimerInterval);
  if (!activeMockData) return;

  try {
    const res = await fetch('/api/mock/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: activeMockData.session_id,
        company: activeMockData.company,
        answers: mockAnswers
      })
    });
    const report = await res.json();
    renderMockReport(report);
  } catch (e) {
    console.error('Error submitting mock test:', e);
  }
}

function renderMockReport(report) {
  document.getElementById('mockActiveView').style.display = 'none';
  document.getElementById('mockResultView').style.display = 'block';

  document.getElementById('resAccuracy').innerText = `${report.accuracy_percent}%`;
  document.getElementById('resCorrect').innerText = `${report.correct_count} / ${report.total_questions}`;
  document.getElementById('resTime').innerText = `${Math.round(report.total_time_sec)}s`;
  document.getElementById('resVerdict').innerText = report.verdict || 'Completed';

  // Sectional Table
  const tbody = document.getElementById('sectionalTableBody');
  tbody.innerHTML = '';
  for (const [sec, stats] of Object.entries(report.sectional_breakdown || {})) {
    const acc = stats.total > 0 ? ((stats.correct / stats.total) * 100).toFixed(1) : 0;
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${sec.toUpperCase()}</strong></td>
      <td>${stats.correct} / ${stats.total}</td>
      <td><span style="color:${acc >= 60 ? '#22c55e' : '#ef4444'}">${acc}%</span></td>
    `;
    tbody.appendChild(tr);
  }

  // Detailed Review
  const revCont = document.getElementById('mockReviewContainer');
  revCont.innerHTML = '<h3>Question by Question Solutions</h3>';
  (report.detailed_review || []).forEach(item => {
    const div = document.createElement('div');
    div.className = 'question-container';
    div.style.marginBottom = '16px';
    div.innerHTML = `
      <div class="question-meta-bar">
        <span class="badge">${item.category.toUpperCase()}</span>
        <span class="pill">${item.topic}</span>
        <span class="pill" style="color:${item.is_correct ? '#22c55e' : '#ef4444'}">
          ${item.is_correct ? '✅ Correct' : '❌ Incorrect'}
        </span>
      </div>
      <p style="font-weight:600; margin-bottom:8px;">${item.index}. ${item.question}</p>
      ${item.code_snippet ? `<div class="code-box"><pre><code>${item.code_snippet}</code></pre></div>` : ''}
      <p style="font-size:13px; color:#94a3b8; margin-bottom:8px;">
        Your Answer: <strong>${item.user_choice}</strong> | Correct: <strong style="color:#22c55e">${item.correct_answer}</strong>
      </p>
      <div class="explanation-box">
        <div class="exp-header">Step-by-Step Explanation</div>
        <div class="exp-body">${item.explanation}</div>
      </div>
    `;
    revCont.appendChild(div);
  });
}

// INFINITE GENERATOR
function initGeneratorEventListeners() {
  document.querySelectorAll('.generator-controls .btn-accent').forEach(btn => {
    btn.addEventListener('click', async () => {
      const cat = btn.getAttribute('data-gencat');
      try {
        const res = await fetch(`/api/generate?category=${cat}`);
        const q = await res.json();
        renderGeneratorQuestion(q);
      } catch (e) {
        console.error('Error generating question:', e);
      }
    });
  });
}

function renderGeneratorQuestion(q) {
  const card = document.getElementById('generatorQuestionCard');
  card.style.display = 'block';

  document.getElementById('genBadgeCategory').innerText = (q.category || 'QUANTITATIVE').toUpperCase();
  document.getElementById('genPillTopic').innerText = q.topic || 'Algorithmic Problem';
  document.getElementById('genQText').innerText = q.question;

  const codeBox = document.getElementById('genCodeBox');
  if (q.code_snippet && q.code_snippet.trim() !== '') {
    codeBox.style.display = 'block';
    document.getElementById('genCodeText').innerText = q.code_snippet;
  } else {
    codeBox.style.display = 'none';
  }

  const grid = document.getElementById('genOptionsGrid');
  grid.innerHTML = '';
  const expBox = document.getElementById('genExplanationBox');
  expBox.style.display = 'none';

  ['A', 'B', 'C', 'D'].forEach(key => {
    if (q.options && q.options[key]) {
      const btn = document.createElement('button');
      btn.className = 'option-btn';
      btn.innerHTML = `<span class="option-key">${key}</span><span class="option-text">${q.options[key]}</span>`;
      btn.onclick = () => {
        if (key === q.answer) {
          btn.classList.add('correct');
        } else {
          btn.classList.add('wrong');
          // Highlight correct
          grid.querySelectorAll('.option-btn').forEach(b => {
            if (b.querySelector('.option-key').innerText === q.answer) b.classList.add('correct');
          });
        }
        document.getElementById('genExpHeader').innerText = `Solution (Correct: Option ${q.answer})`;
        document.getElementById('genExpText').innerText = q.explanation;
        expBox.style.display = 'block';
      };
      grid.appendChild(btn);
    }
  });
}

// CODING SANDBOX
function initCodingSandbox() {
  document.getElementById('btnNextCoding')?.addEventListener('click', loadNextCodingQuestion);
}

async function loadNextCodingQuestion() {
  window.codingInitialized = true;
  try {
    const res = await fetch('/api/question?category=coding');
    const q = await res.json();
    renderCodingQuestion(q);
  } catch (e) {
    console.error('Error loading coding question:', e);
  }
}

function renderCodingQuestion(q) {
  document.getElementById('codingPillTopic').innerText = q.topic || 'C Logic & Output';
  document.getElementById('codingPillCompany').innerText = q.company || 'Placement';
  document.getElementById('codingQText').innerText = q.question;

  const codeBox = document.getElementById('codingCodeBox');
  if (q.code_snippet && q.code_snippet.trim() !== '') {
    codeBox.style.display = 'block';
    document.getElementById('codingCodeText').innerText = q.code_snippet;
  } else {
    codeBox.style.display = 'none';
  }

  const grid = document.getElementById('codingOptionsGrid');
  grid.innerHTML = '';
  const expBox = document.getElementById('codingExplanationBox');
  expBox.style.display = 'none';

  ['A', 'B', 'C', 'D'].forEach(key => {
    if (q.options && q.options[key]) {
      const btn = document.createElement('button');
      btn.className = 'option-btn';
      btn.innerHTML = `<span class="option-key">${key}</span><span class="option-text">${q.options[key]}</span>`;
      btn.onclick = () => {
        if (key === q.answer) {
          btn.classList.add('correct');
        } else {
          btn.classList.add('wrong');
          grid.querySelectorAll('.option-btn').forEach(b => {
            if (b.querySelector('.option-key').innerText === q.answer) b.classList.add('correct');
          });
        }
        document.getElementById('codingExpHeader').innerText = `Answer: Option ${q.answer}`;
        document.getElementById('codingExpText').innerText = q.explanation;
        expBox.style.display = 'block';
      };
      grid.appendChild(btn);
    }
  });
}

// ANALYTICS
async function loadAnalytics() {
  try {
    const res = await fetch('/api/analytics');
    const data = await res.json();

    document.getElementById('statOverallAcc').innerText = `${data.overall_accuracy}%`;
    document.getElementById('statTotalAttempts').innerText = data.total_attempts;
    document.getElementById('statCorrectAttempts').innerText = data.correct_attempts;
    document.getElementById('statAvgTime').innerText = `${data.avg_time_sec}s`;

    // Category list
    const catList = document.getElementById('analyticsCategoryList');
    catList.innerHTML = '';
    const cats = data.category_stats || {};
    if (Object.keys(cats).length === 0) {
      catList.innerHTML = '<p style="color:#94a3b8;">No attempts recorded yet. Practice a few questions!</p>';
    } else {
      for (const [c, s] of Object.entries(cats)) {
        const div = document.createElement('div');
        div.style.marginBottom = '12px';
        div.innerHTML = `
          <div style="display:flex; justify-content:space-between; margin-bottom:4px; font-size:13px;">
            <span><strong>${c.toUpperCase()}</strong> (${s.correct}/${s.total})</span>
            <span style="font-weight:700; color:${s.accuracy >= 65 ? '#22c55e' : '#f59e0b'}">${s.accuracy}%</span>
          </div>
          <div style="background:#1e293b; height:6px; border-radius:3px; overflow:hidden;">
            <div style="background:#38bdf8; width:${s.accuracy}%; height:100%;"></div>
          </div>
        `;
        catList.appendChild(div);
      }
    }

    // Weak topics
    const weakList = document.getElementById('analyticsWeakList');
    weakList.innerHTML = '';
    const weak = data.weak_topics || [];
    if (weak.length === 0) {
      weakList.innerHTML = '<p style="color:#22c55e;">🎉 No critical weaknesses detected! Keep practicing!</p>';
    } else {
      weak.forEach(w => {
        const div = document.createElement('div');
        div.style.padding = '8px 12px';
        div.style.background = 'rgba(239, 68, 68, 0.1)';
        div.style.borderLeft = '3px solid #ef4444';
        div.style.borderRadius = '4px';
        div.style.marginBottom = '8px';
        div.innerHTML = `
          <strong>${w.topic}</strong> (${w.category})<br>
          <span style="font-size:12px; color:#fca5a5;">Accuracy: ${w.accuracy}% over ${w.total} attempts.</span>
        `;
        weakList.appendChild(div);
      });
    }
  } catch (e) {
    console.error('Error loading analytics:', e);
  }
}
