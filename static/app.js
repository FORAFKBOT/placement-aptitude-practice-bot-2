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
  loadUserSkillProfile();
  loadNextPracticeQuestion();
  initMockEventListeners();
  initGeneratorEventListeners();
  initCodingSandbox();
  initAISettingsModal();
});

// Load User Adaptive Skill Profile
async function loadUserSkillProfile() {
  try {
    const res = await fetch('/api/profile');
    const prof = await res.json();
    const tier = prof.tier || {};
    const badge = document.getElementById('headerTierBadge');
    if (badge && tier.name) {
      badge.innerText = `${tier.icon || '🎯'} ${tier.name} (${tier.rating || prof.overall_rating})`;
    }
  } catch (e) {
    console.error('Error loading skill profile:', e);
  }
}

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
  document.getElementById('practiceDifficultySelect')?.addEventListener('change', loadNextPracticeQuestion);
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
  const diffVal = document.getElementById('practiceDifficultySelect')?.value || 'adaptive';
  const comp = document.getElementById('practiceCompanySelect')?.value || '';

  let url = `/api/question?category=${encodeURIComponent(cat)}&company=${encodeURIComponent(comp)}`;
  if (diffVal === 'adaptive') {
    url += '&adaptive=true';
  } else {
    url += `&difficulty=${encodeURIComponent(diffVal)}&adaptive=false`;
  }

  const expBox = document.getElementById('explanationBox');
  if (expBox) expBox.style.display = 'none';

  try {
    const res = await fetch(url);
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
  
  const diffPill = document.getElementById('qPillDifficulty');
  if (diffPill) diffPill.innerText = q.difficulty || 'Medium';

  const aiPill = document.getElementById('qPillAITier');
  if (aiPill) {
    if (q.ai_tier) {
      aiPill.style.display = 'inline-block';
      aiPill.innerText = `🤖 ${q.ai_tier.name}`;
    } else {
      aiPill.style.display = 'none';
    }
  }

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

    // AI Tutor Diagnostic Feedback Display
    const aiFb = result.ai_feedback || {};
    const skill = result.skill_update || {};

    const sourceEl = document.getElementById('aiTutorSource');
    if (sourceEl) sourceEl.innerText = aiFb.source || 'AI Tutor Diagnostic Feedback';

    const deltaPill = document.getElementById('aiRatingDeltaPill');
    if (deltaPill && skill.rating_delta !== undefined) {
      const d = skill.rating_delta;
      deltaPill.innerText = (d >= 0 ? `+${d}` : `${d}`) + ' Elo Rating';
      deltaPill.className = 'rating-delta-pill' + (d < 0 ? ' neg' : '');
    }

    if (skill.tier) {
      const badge = document.getElementById('headerTierBadge');
      if (badge) badge.innerText = `${skill.tier.icon || '🎯'} ${skill.tier.name} (${skill.tier.rating})`;
    }

    document.getElementById('aiDiagnosisText').innerText = aiFb.diagnostic_assessment || 'Analyzing student reasoning...';
    
    const trapRow = document.getElementById('aiTrapRow');
    const trapText = document.getElementById('aiTrapText');
    if (aiFb.misconception_analysis && !result.is_correct) {
      trapRow.style.display = 'block';
      trapText.innerText = aiFb.misconception_analysis;
    } else {
      trapRow.style.display = 'none';
    }

    document.getElementById('aiHackText').innerText = aiFb.speed_hack || '';
    document.getElementById('aiCoachingText').innerText = aiFb.coaching_tip || '';

    expBody.innerText = result.explanation || 'Refer to the standard placement problem solution.';
    expBox.style.display = 'block';
  } catch (e) {
    console.error('Error submitting answer:', e);
  }
}

// AI Settings Modal
function initAISettingsModal() {
  const modal = document.getElementById('aiSettingsModal');
  const btnOpen = document.getElementById('btnOpenAISettings');
  const btnClose = document.getElementById('btnCloseAISettings');
  const btnSave = document.getElementById('btnSaveApiKey');
  const input = document.getElementById('geminiApiKeyInput');
  const statusMsg = document.getElementById('apiKeyStatusMsg');

  btnOpen?.addEventListener('click', async () => {
    modal.style.display = 'flex';
    try {
      const res = await fetch('/api/config/key');
      const data = await res.json();
      if (data.has_key) {
        statusMsg.innerHTML = '<span style="color:#22c55e;">Active: Custom Gemini API key is configured.</span>';
      } else {
        statusMsg.innerHTML = '<span style="color:#94a3b8;">Active: Using Built-in Cognitive AI Diagnosis Engine (Offline).</span>';
      }
    } catch (e) {}
  });

  btnClose?.addEventListener('click', () => {
    modal.style.display = 'none';
  });

  btnSave?.addEventListener('click', async () => {
    const key = input.value.trim();
    try {
      const res = await fetch('/api/config/key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: key })
      });
      const data = await res.json();
      statusMsg.innerHTML = `<span style="color:#22c55e;">${data.message}</span>`;
      setTimeout(() => { modal.style.display = 'none'; }, 1000);
    } catch (e) {
      statusMsg.innerHTML = '<span style="color:#ef4444;">Error saving API key.</span>';
    }
  });
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

// AI QUESTION GENERATOR STUDIO
let currentGeneratedQuestion = null;
let selectedGenChoice = null;

async function checkAIEngineStatus() {
  try {
    const res = await fetch('/api/config/key');
    const data = await res.json();
    const lbl = document.getElementById('genEngineName');
    if (lbl) {
      if (data.has_key) {
        lbl.innerText = 'Gemini 2.5 Flash LLM (Live)';
        lbl.style.color = '#38bdf8';
      } else {
        lbl.innerText = 'Cognitive Heuristics (Offline)';
        lbl.style.color = '#a78bfa';
      }
    }
  } catch (e) {
    console.error('Error checking key status:', e);
  }
}

function initGeneratorEventListeners() {
  checkAIEngineStatus();

  // Generate Button Click
  const btnGen = document.getElementById('btnAIGenerate');
  if (btnGen) {
    btnGen.addEventListener('click', async () => {
      const cat = document.getElementById('aiGenCategory')?.value || 'quantitative';
      const comp = document.getElementById('aiGenCompany')?.value || 'TCS';
      const diff = document.getElementById('aiGenDifficulty')?.value || 'Medium';
      const topic = document.getElementById('aiGenTopic')?.value?.trim() || '';
      const prompt = document.getElementById('aiGenPrompt')?.value?.trim() || '';

      const spinner = document.getElementById('genBtnSpinner');
      const btnText = document.getElementById('genBtnText');
      if (spinner) spinner.style.display = 'inline';
      if (btnText) btnText.innerText = 'Generating with AI...';
      btnGen.disabled = true;

      try {
        const res = await fetch('/api/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            category: cat,
            company: comp,
            difficulty: diff,
            topic: topic || null,
            prompt: prompt || null,
            use_llm: true,
            save_to_db: true
          })
        });
        const q = await res.json();
        renderGeneratorQuestion(q);
      } catch (e) {
        console.error('Error generating question:', e);
      } finally {
        if (spinner) spinner.style.display = 'none';
        if (btnText) btnText.innerText = '✨ Generate Question with AI';
        btnGen.disabled = false;
      }
    });
  }

  // Quick Preset Topic Chips
  document.querySelectorAll('.topic-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const cat = chip.getAttribute('data-cat');
      const comp = chip.getAttribute('data-comp');
      const top = chip.getAttribute('data-topic');

      if (cat) document.getElementById('aiGenCategory').value = cat;
      if (comp) document.getElementById('aiGenCompany').value = comp;
      if (top) document.getElementById('aiGenTopic').value = top;

      document.getElementById('btnAIGenerate')?.click();
    });
  });

  // Regenerate Button Click
  document.getElementById('btnRegenerateAI')?.addEventListener('click', () => {
    document.getElementById('btnAIGenerate')?.click();
  });

  // Submit Answer to Generated Question
  const btnSubmit = document.getElementById('btnSubmitGenAnswer');
  if (btnSubmit) {
    btnSubmit.addEventListener('click', async () => {
      if (!currentGeneratedQuestion || !selectedGenChoice) return;
      btnSubmit.disabled = true;

      const allBtns = document.querySelectorAll('#genOptionsGrid .option-btn');
      allBtns.forEach(b => b.classList.add('disabled'));

      try {
        const res = await fetch('/api/submit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            question_id: currentGeneratedQuestion.id,
            user_choice: selectedGenChoice,
            time_taken_sec: 12.0
          })
        });
        const result = await res.json();

        // Highlight options
        allBtns.forEach(b => {
          const k = b.querySelector('.option-key')?.innerText;
          if (k === result.correct_answer) {
            b.classList.add('correct');
          } else if (k === selectedGenChoice && !result.is_correct) {
            b.classList.add('wrong');
          }
        });

        // Show AI Diagnostics & Solution Box
        const expBox = document.getElementById('genExplanationBox');
        const expHead = document.getElementById('genExpHeader');
        const aiAssess = document.getElementById('genAIAssess');
        const aiSpeedHack = document.getElementById('genAISpeedHack');
        const aiTrap = document.getElementById('genAITrap');
        const expText = document.getElementById('genExpText');

        if (result.is_correct) {
          expHead.innerHTML = `✅ Correct! (Option ${result.correct_answer})`;
          expHead.style.color = '#22c55e';
          streak++;
          score += 10;
        } else {
          expHead.innerHTML = `❌ Incorrect! Correct Answer: Option ${result.correct_answer}`;
          expHead.style.color = '#ef4444';
          streak = 0;
        }

        document.getElementById('streakCount').innerText = streak;
        document.getElementById('scoreCount').innerText = score;

        const fb = result.ai_feedback || {};
        aiAssess.innerText = fb.diagnostic_assessment || (result.is_correct ? 'Great reasoning!' : 'Review this concept.');
        aiSpeedHack.innerText = fb.speed_hack || currentGeneratedQuestion.speed_hack || '⚡ Speed Hack: Test boundary conditions and eliminate extreme options.';

        if (!result.is_correct && fb.misconception_analysis) {
          aiTrap.style.display = 'block';
          aiTrap.innerText = fb.misconception_analysis;
        } else {
          aiTrap.style.display = 'none';
        }

        expText.innerText = result.explanation || currentGeneratedQuestion.explanation || 'No step-by-step explanation available.';
        expBox.style.display = 'block';

        // Update skill profile in header
        loadUserSkillProfile();
      } catch (e) {
        console.error('Error submitting answer:', e);
      }
    });
  }
}

function renderGeneratorQuestion(q) {
  currentGeneratedQuestion = q;
  selectedGenChoice = null;

  const card = document.getElementById('generatorQuestionCard');
  card.style.display = 'block';

  document.getElementById('genBadgeCategory').innerText = (q.category || 'QUANTITATIVE').toUpperCase();
  document.getElementById('genPillTopic').innerText = q.topic || 'Algorithmic Problem';
  document.getElementById('genPillCompany').innerText = q.company || 'TCS';
  document.getElementById('genPillDifficulty').innerText = q.difficulty || 'Medium';
  document.getElementById('genPillEngine').innerText = q.ai_engine || (q.source?.includes('Gemini') ? '⚡ Gemini Live' : '🧠 Cognitive Offline');
  document.getElementById('genPillSaved').innerText = `💾 Saved to Bank (#${q.id || 'Active'})`;

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

  const btnSubmit = document.getElementById('btnSubmitGenAnswer');
  if (btnSubmit) btnSubmit.disabled = true;

  ['A', 'B', 'C', 'D'].forEach(key => {
    if (q.options && q.options[key]) {
      const btn = document.createElement('button');
      btn.className = 'option-btn';
      btn.innerHTML = `<span class="option-key">${key}</span><span class="option-text">${q.options[key]}</span>`;
      btn.onclick = () => {
        grid.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        selectedGenChoice = key;
        if (btnSubmit) btnSubmit.disabled = false;
      };
      grid.appendChild(btn);
    }
  });

  // Smooth scroll down to generated question card
  card.scrollIntoView({ behavior: 'smooth', block: 'start' });
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
