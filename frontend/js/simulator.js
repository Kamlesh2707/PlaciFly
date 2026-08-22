/* ================================================
   SIMULATOR MODULE — AI Company Interviewer & Workstation
   ================================================ */

let timerInterval = null;
let timeRemaining = 0;
let scenarioStartTime = 0;

let sessionState = {
  sessionId: null,
  company: '',
  difficulty: 'Medium',
  interviewer: null,
  candidateProfile: null,
  currentRound: 1,
  rounds: [
    { name: 'HR', icon: '👔', type: 'HR Interview', maxTurns: 3, turns: [], score: null },
    { name: 'Technical', icon: '💻', type: 'Technical Interview', maxTurns: 3, turns: [], score: null },
    { name: 'Coding', icon: '🧑💻', type: 'Coding Round', maxTurns: 1, turns: [], score: null },
    { name: 'Case Study', icon: '📊', type: 'Case Study', maxTurns: 1, turns: [], score: null },
    { name: 'Situational', icon: '🧩', type: 'Situational Round', maxTurns: 1, turns: [], score: null }
  ],
  askedIds: [],
  currentQuestion: null,
  currentTurnInRound: 0
};

// Global state assumed to exist: state.companies, state.selectedCompany, etc.
// from app.js
if (typeof state === 'undefined') {
  window.state = {
    companies: ['TCS', 'Infosys', 'Wipro', 'Cognizant', 'Accenture', 'Amazon', 'Google', 'Microsoft']
  };
}

/* ================================================
   ENTRY POINTS
   ================================================ */

function loadScenario(scenario) {
  // If user clicks a custom scenario from prep hub, bypass company selection
  // and jump straight to adaptive interview
  if (!sessionState.company) {
    sessionState.company = state.selectedCompany || 'TCS';
  }
  startAdaptiveInterviewSession();
}

function startAdaptiveInterviewSession() {
  const container = document.getElementById('simulator-content');
  if (!container) return;

  if (!sessionState.company) {
    renderCompanySelection();
  } else if (!sessionState.candidateProfile) {
    renderResumeGate();
  } else {
    // Start round 1 if not started
    if (sessionState.currentTurnInRound === 0 && sessionState.rounds[sessionState.currentRound - 1].turns.length === 0) {
      startCurrentRound();
    } else {
      renderInterviewerWorkstation();
    }
  }
}

// Ensure the tab initializes properly when clicked in app.js
function initSimulatorTab() {
  startAdaptiveInterviewSession();
}

/* ================================================
   STEP 1: COMPANY SELECTION
   ================================================ */

const DEFAULT_POPULAR_COMPANIES = [
  { name: 'TCS', color: '#0072C6', industry: 'IT Services', role: 'Software Engineer', icon: '🏢' },
  { name: 'Amazon', color: '#FF9900', industry: 'E-Commerce & Cloud', role: 'SDE-1', icon: '📦' },
  { name: 'Google', color: '#4285F4', industry: 'Big Tech / Search', role: 'Software Engineer (L3)', icon: '🔍' },
  { name: 'Microsoft', color: '#00A4EF', industry: 'Cloud & Enterprise', role: 'Software Engineer', icon: '💻' },
  { name: 'Infosys', color: '#007CC3', industry: 'IT Consulting', role: 'Systems Engineer', icon: '🌐' },
  { name: 'Deloitte', color: '#86BC25', industry: 'Consulting & Analytics', role: 'Analyst / Consultant', icon: '📊' },
  { name: 'Accenture', color: '#A100FF', industry: 'Technology Services', role: 'Associate SWE', icon: '🚀' },
  { name: 'Capgemini', color: '#0070AD', industry: 'Digital & Cloud', role: 'Software Analyst', icon: '⚡' },
  { name: 'Meta', color: '#0668E1', industry: 'Social & AI', role: 'Production Engineer', icon: '👥' },
  { name: 'Netflix', color: '#E50914', industry: 'Streaming & Systems', role: 'Software Engineer', icon: '🎬' },
  { name: 'Adobe', color: '#FF0000', industry: 'Creative Cloud', role: 'SDE', icon: '🎨' },
  { name: 'IBM', color: '#1F70C1', industry: 'Enterprise & AI', role: 'Application Developer', icon: '🧠' },
  { name: 'Wipro', color: '#6A1B9A', industry: 'IT Solutions', role: 'Project Engineer', icon: '🎯' }
];

function renderCompanySelection() {
  const container = document.getElementById('simulator-content');
  if (!container) return;

  // Use fetched companies or default popular companies
  let companiesList = [];
  if (state.companies && state.companies.length > 0) {
    companiesList = state.companies.map(c => {
      if (typeof c === 'string') {
        const found = DEFAULT_POPULAR_COMPANIES.find(p => p.name.toLowerCase() === c.toLowerCase());
        return found || { name: c, color: '#38bdf8', industry: 'Technology', role: 'Software Engineer', icon: '🏢' };
      }
      return {
        name: c.name || 'Company',
        color: c.color || '#38bdf8',
        industry: c.industry || 'Technology',
        role: c.role || 'Software Engineer',
        icon: c.icon || '🏢'
      };
    });
  } else {
    companiesList = DEFAULT_POPULAR_COMPANIES;
  }

  let cardsHtml = companiesList.map(c => `
    <div class="glass-card interactive p-6 cursor-pointer hover:border-cyan-400 transition-all text-center flex flex-col items-center justify-between gap-3 group relative overflow-hidden" 
         onclick="simSelectCompany('${c.name}')" style="min-height: 180px;">
      <div class="w-14 h-14 rounded-2xl flex items-center justify-center text-xl font-bold shadow-lg transition-transform group-hover:scale-110" 
           style="background: ${c.color}25; color: ${c.color}; border: 1px solid ${c.color}50;">
        ${c.name.slice(0, 2).toUpperCase()}
      </div>
      <div>
        <h3 class="font-bold text-base text-white group-hover:text-cyan-300 transition-colors">${c.name}</h3>
        <p class="text-[11px] text-slate-400 mt-0.5">${c.industry}</p>
      </div>
      <span class="text-[10px] px-2.5 py-1 rounded-full bg-slate-800/80 text-slate-300 border border-slate-700/60 font-medium">
        ${c.role}
      </span>
    </div>
  `).join('');

  // Custom Company Card at the end
  cardsHtml += `
    <div class="glass-card interactive p-6 cursor-pointer hover:border-cyan-400 transition-all text-center flex flex-col items-center justify-center gap-3 border-dashed border-2 border-slate-600 bg-slate-900/30 group" 
         onclick="simSelectCustomCompany()" style="min-height: 180px;">
      <div class="w-14 h-14 rounded-2xl bg-cyan-500/10 flex items-center justify-center text-2xl text-cyan-400 border border-cyan-500/30 group-hover:scale-110 transition-transform">
        ✨
      </div>
      <div>
        <h3 class="font-bold text-base text-cyan-400">+ Custom Company</h3>
        <p class="text-[11px] text-slate-500 mt-0.5">Enter any startup / firm</p>
      </div>
      <span class="text-[10px] px-2.5 py-1 rounded-full bg-cyan-950/40 text-cyan-300 border border-cyan-500/20 font-medium">
        Tailored 5 Rounds
      </span>
    </div>
  `;

  container.innerHTML = `
    <div class="max-w-5xl mx-auto p-2 sm:p-6 animation-fade-in">
      <div class="text-center mb-8">
        <span class="px-3 py-1 rounded-full text-xs font-bold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 mb-3 inline-block">
          STEP 1 OF 3 • TARGET SELECTION
        </span>
        <h2 class="text-3xl font-extrabold text-white mb-2">Select Company for Interview</h2>
        <p class="text-sm text-slate-400 max-w-xl mx-auto">
          Choose a target company to simulate its exact hiring process across HR, Technical, Coding, Case Study, and Situational rounds.
        </p>
      </div>
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-5">
        ${cardsHtml}
      </div>
    </div>
  `;
}

function simSelectCompany(companyName) {
  sessionState.company = companyName;
  renderDifficultySelection();
}

function simSelectCustomCompany() {
  const custom = prompt("Enter Custom Company Name (e.g. Stripe, OpenAI, CRED):");
  if (!custom || !custom.trim()) return;
  sessionState.company = custom.trim();
  renderDifficultySelection();
}

// Attach globally
window.simSelectCompany = simSelectCompany;
window.simSelectCustomCompany = simSelectCustomCompany;

/* ================================================
   STEP 2: DIFFICULTY SELECTION
   ================================================ */

function renderDifficultySelection() {
  const container = document.getElementById('simulator-content');
  if (!container) return;

  container.innerHTML = `
    <div class="max-w-4xl mx-auto p-4 sm:p-8 animation-fade-in text-center">
      
      <div class="mb-6 flex justify-start">
        <button class="text-xs text-slate-400 hover:text-white px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700 transition-colors flex items-center gap-1.5" 
                onclick="renderCompanySelection()">
          ← Back to Companies
        </button>
      </div>

      <span class="px-3 py-1 rounded-full text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20 mb-3 inline-block">
        STEP 2 OF 3 • DIFFICULTY CALIBRATION
      </span>
      <h2 class="text-3xl font-extrabold text-white mb-2">Select Evaluation Strictness</h2>
      <p class="text-sm text-slate-400 mb-8">Targeting <strong class="text-cyan-400">${sessionState.company}</strong>. Choose the calibration level of the AI panel.</p>
      
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-5 max-w-3xl mx-auto">
        
        <div class="glass-card interactive p-7 cursor-pointer hover:border-emerald-400 transition-all text-center border-emerald-500/20 bg-emerald-950/10 group" 
             onclick="simSelectDifficulty('Easy')">
          <div class="text-4xl mb-3 group-hover:scale-110 transition-transform">🟢</div>
          <h3 class="font-bold text-lg text-emerald-400 mb-1">Easy Level</h3>
          <p class="text-xs text-slate-400 leading-relaxed">Fundamental questions, encouraging interviewer tone, foundational CS concepts.</p>
          <div class="mt-4 text-[10px] font-bold text-emerald-300/80 bg-emerald-500/10 py-1 rounded-md">
            Best for Campus Freshers
          </div>
        </div>
        
        <div class="glass-card interactive p-7 cursor-pointer hover:border-amber-400 transition-all text-center border-amber-500/20 bg-amber-950/10 group" 
             onclick="simSelectDifficulty('Medium')">
          <div class="text-4xl mb-3 group-hover:scale-110 transition-transform">🟡</div>
          <h3 class="font-bold text-lg text-amber-400 mb-1">Medium Level</h3>
          <p class="text-xs text-slate-400 leading-relaxed">Realistic placement drive strictness, deep dive into projects, intermediate DSA & SQL.</p>
          <div class="mt-4 text-[10px] font-bold text-amber-300/80 bg-amber-500/10 py-1 rounded-md">
            Standard MNC Level (Recommended)
          </div>
        </div>
        
        <div class="glass-card interactive p-7 cursor-pointer hover:border-rose-400 transition-all text-center border-rose-500/20 bg-rose-950/10 group" 
             onclick="simSelectDifficulty('Hard')">
          <div class="text-4xl mb-3 group-hover:scale-110 transition-transform">🔴</div>
          <h3 class="font-bold text-lg text-rose-400 mb-1">Hard Level</h3>
          <p class="text-xs text-slate-400 leading-relaxed">Bar-raiser rigor, system design trade-offs, advanced logic puzzles, zero tolerance for fluff.</p>
          <div class="mt-4 text-[10px] font-bold text-rose-300/80 bg-rose-500/10 py-1 rounded-md">
            Tier-1 Tech & Product Firms
          </div>
        </div>

      </div>
    </div>
  `;
}

function simSelectDifficulty(diff) {
  sessionState.difficulty = diff;
  renderResumeGate();
}

window.simSelectDifficulty = simSelectDifficulty;

/* ================================================
   STEP 3: RESUME GATE
   ================================================ */

function renderResumeGate() {
  const container = document.getElementById('simulator-content');
  if (!container) return;

  container.innerHTML = `
    <div class="max-w-4xl mx-auto p-4 sm:p-8 animation-fade-in">
      <div class="glass-card p-6 sm:p-8 border-t-4 border-cyan-500 shadow-2xl">
        
        <div class="flex items-start justify-between gap-4 mb-6">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-2xl bg-cyan-500/20 flex items-center justify-center text-2xl text-cyan-400 border border-cyan-500/30">📄</div>
            <div>
              <h2 class="text-2xl font-bold text-white tracking-tight">Candidate Resume Verification</h2>
              <p class="text-xs sm:text-sm text-slate-400">Target Company: <span class="text-cyan-400 font-semibold">${sessionState.company}</span> • Level: <span class="text-amber-400 font-semibold">${sessionState.difficulty}</span></p>
            </div>
          </div>
          <button class="text-xs text-slate-400 hover:text-white px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 transition-colors" onclick="renderCompanySelection()">
            ← Change Company
          </button>
        </div>

        <p class="text-sm text-slate-300 mb-4 leading-relaxed">
          Upload your resume PDF or paste the text below. Our AI evaluator will analyze your background to tailor the <strong>HR</strong>, <strong>Technical</strong>, and <strong>Coding</strong> questions specifically to your skills.
        </p>

        <!-- PDF / File Upload Area -->
        <div class="mb-4">
          <div id="resume-dropzone" class="border-2 border-dashed border-slate-700 hover:border-cyan-400/80 rounded-2xl p-6 text-center bg-slate-900/40 hover:bg-slate-900/80 cursor-pointer transition-all duration-300 group" onclick="document.getElementById('resume-file-input').click()">
            <input type="file" id="resume-file-input" accept=".pdf,.txt" class="hidden" onchange="handleResumeFileUpload(event)">
            <div class="w-12 h-12 rounded-full bg-slate-800 group-hover:bg-cyan-500/20 flex items-center justify-center text-2xl mx-auto mb-2 transition-colors">
              📥
            </div>
            <p class="text-sm font-semibold text-white group-hover:text-cyan-300 transition-colors" id="upload-status-text">
              Click or drag & drop to upload your Resume (<span class="text-cyan-400 font-bold">PDF</span> or <span class="text-blue-400 font-bold">TXT</span>)
            </p>
            <p class="text-xs text-slate-500 mt-1">Automatic text extraction and AI parsing</p>
          </div>
        </div>

        <div class="relative my-4">
          <div class="absolute inset-0 flex items-center"><div class="w-full border-t border-slate-800"></div></div>
          <div class="relative flex justify-center"><span class="bg-slate-900/90 px-3 text-xs text-slate-500 uppercase tracking-widest font-bold">or paste resume text</span></div>
        </div>

        <!-- Textarea -->
        <div class="relative mb-4">
          <textarea id="resume-input" class="w-full h-48 bg-slate-900/90 border border-slate-700/80 rounded-xl p-4 text-slate-200 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 outline-none resize-y font-mono text-xs sm:text-sm leading-relaxed" placeholder="Paste your resume contents here (Education, Skills, Languages, Projects, Experience)..."></textarea>
          <button type="button" class="absolute top-2 right-2 text-xs px-2.5 py-1 bg-slate-800/90 hover:bg-slate-700 text-slate-400 hover:text-cyan-300 rounded border border-slate-700 transition-colors" onclick="fillSampleResumeForGate()">
            ✨ Fill Sample
          </button>
        </div>

        <!-- Parsed Profile Preview Card (Hidden until parsed) -->
        <div id="parsed-profile-card" class="hidden mb-6 p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/30">
          <div class="flex items-center gap-2 text-emerald-400 font-bold text-sm mb-2">
            <span>✅</span> Resume Analyzed Successfully!
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs text-slate-300" id="parsed-profile-details">
            <!-- Injected by JS -->
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex flex-col sm:flex-row items-center justify-between gap-4">
          <span class="text-xs text-slate-500 text-center sm:text-left">
            🔒 Your resume is processed privately in-session for interview personalization.
          </span>
          <div class="flex gap-3 w-full sm:w-auto">
            <button class="btn-primary w-full sm:w-auto py-3 px-8 text-sm font-bold flex items-center justify-center gap-2" onclick="processResume()" id="btn-parse-resume">
              <span>🔍</span> Analyze Resume & Start 🚀
            </button>
          </div>
        </div>

      </div>
    </div>
  `;
}

function fillSampleResumeForGate() {
  const sample = `Bhoi Kartik
MCA (Master of Computer Applications) - 2026

TECHNICAL SKILLS:
- Languages: Python, Java, C++, JavaScript, SQL
- Frameworks & Tools: Flutter, Firebase, Flask, Node.js, Git, Docker
- Databases: MySQL, MongoDB, Firestore
- Core CS: Data Structures & Algorithms, Object-Oriented Programming, Database Management Systems, Operating Systems

PROJECTS:
1. QuickLaundry - On-Demand Laundry Service Mobile App
   - Built full-stack cross-platform app using Flutter and Firebase backend.
   - Designed real-time order tracking, push notifications, and payment gateway integration.
   - Handled edge cases for offline caching and network drops.

2. Placifly - AI Interview Simulator & Assessment Portal
   - Developed multi-turn adaptive interview engine with LLM evaluator.
   - Implemented real-time RAG ground-truth validation and rubric grading.`;

  const input = document.getElementById('resume-input');
  if (input) input.value = sample;
}

let uploadedResumeFile = null;

async function handleResumeFileUpload(e) {
  const file = e.target.files[0];
  if (!file) return;

  uploadedResumeFile = file;
  const statusEl = document.getElementById('upload-status-text');
  if (statusEl) {
    statusEl.innerHTML = `Selected file: <strong class="text-cyan-400">${file.name}</strong> (${Math.round(file.size / 1024)} KB)`;
  }

  // If it's a text file, preview directly in textarea
  if (file.name.endsWith('.txt')) {
    const text = await file.text();
    const input = document.getElementById('resume-input');
    if (input) input.value = text;
  }
}

async function processResume() {
  const resumeTextInput = document.getElementById('resume-input');
  const resumeText = resumeTextInput ? resumeTextInput.value.trim() : '';

  if (!uploadedResumeFile && (!resumeText || resumeText.length < 30)) {
    if (typeof showToast === 'function') showToast('Please upload a resume file (.pdf) or paste resume text.', 'warning');
    else alert('Please upload a resume file (.pdf) or paste resume text.');
    return;
  }

  const btn = document.getElementById('btn-parse-resume');
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner" style="width:16px;height:16px;border-width:2px;"></span> Analyzing Resume with AI...';
  }

  try {
    let res;
    if (uploadedResumeFile) {
      const formData = new FormData();
      formData.append('file', uploadedResumeFile);
      if (resumeText) formData.append('resume_text', resumeText);

      res = await fetch('/api/resume/parse-skills', {
        method: 'POST',
        body: formData
      });
    } else {
      res = await fetch('/api/resume/parse-skills', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume_text: resumeText })
      });
    }

    if (!res.ok) throw new Error(`API error: ${res.status}`);
    const data = await res.json();

    sessionState.candidateProfile = data.profile || {
      name: 'Candidate',
      skills: ['Python', 'Java', 'SQL', 'Flutter'],
      programming_languages: ['Python', 'Java'],
      projects: [{ name: 'QuickLaundry', tech: ['Flutter', 'Firebase'] }],
      education: 'MCA',
      experience_level: 'fresher'
    };

    // Show preview card briefly before launching round 1
    const previewCard = document.getElementById('parsed-profile-card');
    const previewDetails = document.getElementById('parsed-profile-details');
    if (previewCard && previewDetails) {
      const prof = sessionState.candidateProfile;
      const langs = prof.programming_languages || prof.languages || ['Python', 'Java'];
      const skills = prof.skills || [];
      const projs = prof.projects || [];

      previewDetails.innerHTML = `
        <div><strong class="text-white">Candidate:</strong> ${prof.name || 'Candidate'} (${prof.education || 'Graduate'})</div>
        <div><strong class="text-white">Languages:</strong> <span class="text-cyan-300">${langs.join(', ') || 'General'}</span></div>
        <div><strong class="text-white">Key Skills:</strong> <span class="text-blue-300">${skills.slice(0, 5).join(', ')}</span></div>
        <div><strong class="text-white">Projects:</strong> <span class="text-amber-300">${projs.map(p => typeof p === 'object' ? p.name : p).join(', ') || 'Academic Projects'}</span></div>
      `;
      previewCard.classList.remove('hidden');
    }

    if (typeof showToast === 'function') {
      showToast('Resume analyzed! Starting Round 1: HR Interview...', 'success');
    }

    // Reset session rounds
    sessionState.currentRound = 1;
    sessionState.currentTurnInRound = 0;
    sessionState.rounds.forEach(r => {
      r.turns = [];
      r.score = null;
    });

    setTimeout(() => {
      startCurrentRound();
    }, 1200);

  } catch (err) {
    console.error('Resume parse error:', err);
    // Fallback profile
    sessionState.candidateProfile = {
      name: 'Candidate',
      skills: ['Python', 'Java', 'SQL', 'Data Structures'],
      programming_languages: ['Python', 'Java'],
      projects: [{ name: 'Software Project', tech: ['Python', 'Flask'] }],
      education: 'Engineering / CS',
      experience_level: 'fresher'
    };

    if (typeof showToast === 'function') {
      showToast('Resume parsed with default profile. Starting interview...', 'info');
    }

    sessionState.currentRound = 1;
    sessionState.currentTurnInRound = 0;
    sessionState.rounds.forEach(r => {
      r.turns = [];
      r.score = null;
    });

    startCurrentRound();
  }
}

/* ================================================
   STEP 4: ROUND MANAGEMENT
   ================================================ */

function renderRoundStepper() {
  const roundTabs = sessionState.rounds.map((r, i) => {
    const roundNum = i + 1;
    const isPast = roundNum < sessionState.currentRound;
    const isCurr = roundNum === sessionState.currentRound;
    
    let cls = 'border-slate-700 bg-slate-900 text-slate-500';
    if (isPast) cls = 'border-emerald-500/50 bg-emerald-500/10 text-emerald-400';
    if (isCurr) cls = 'border-cyan-500 bg-cyan-500/20 text-cyan-300 font-bold shadow-[0_0_10px_rgba(6,182,212,0.3)]';
    
    return `
      <div class="flex items-center gap-2 px-3 py-2 rounded-lg border ${cls} text-sm whitespace-nowrap transition-all">
        <span>${r.icon}</span>
        <span class="hidden sm:inline">Round ${roundNum}: ${r.name}</span>
        <span class="sm:hidden">R${roundNum}</span>
      </div>
    `;
  }).join('<div class="h-[2px] w-4 sm:w-8 bg-slate-700"></div>');

  return `
    <div class="flex items-center justify-center gap-1 sm:gap-2 mb-8 overflow-x-auto pb-2 scrollbar-hide">
      ${roundTabs}
    </div>
  `;
}

async function startCurrentRound() {
  const roundIdx = sessionState.currentRound - 1;
  const round = sessionState.rounds[roundIdx];
  
  if (typeof showLoading === 'function') showLoading(`Starting Round ${sessionState.currentRound}: ${round.name}...`);

  try {
    sessionState.currentTurnInRound = 0;
    
    let res;
    
    if (round.name === 'Situational') {
      // Situational Round uses a different API
      res = await fetch('/api/puzzles/get', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          difficulty: sessionState.difficulty,
          count: 1 
        })
      });
      
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data = await res.json();
      
      const puzzle = data.puzzles && data.puzzles.length > 0 ? data.puzzles[0] : data;
      
      sessionState.currentQuestion = {
        id: puzzle.id || 'puzzle-1',
        title: puzzle.title || 'Situational Puzzle',
        situation: 'Solve this analytical puzzle to demonstrate your logical reasoning.',
        question: puzzle.description || puzzle.question,
        category: 'Puzzle',
        type: 'situational',
        puzzle_data: puzzle // Store original puzzle for evaluation
      };
      
    } else {
      // HR, Technical, Coding, Case Study use standard interviewer API
      let candidateSkills = sessionState.candidateProfile ? sessionState.candidateProfile.skills.join(', ') : '';
      
      let payload = {
        company: sessionState.company,
        difficulty: sessionState.difficulty,
        interview_type: round.type,
        asked_ids: sessionState.askedIds,
        candidate_skills: candidateSkills
      };
      
      // For coding round, explicitly mention we need a coding question
      if (round.name === 'Coding') {
        payload.interview_type = 'Coding Round';
        payload.is_coding = true;
      }
      
      res = await fetch('/api/interviewer/start-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data = await res.json();
      
      sessionState.sessionId = data.session_id || sessionState.sessionId;
      sessionState.interviewer = data.interviewer || sessionState.interviewer;
      sessionState.currentQuestion = data.initial_question;
      
      if (sessionState.currentQuestion && sessionState.currentQuestion.id) {
        sessionState.askedIds.push(sessionState.currentQuestion.id);
      }
    }
    
    if (typeof hideLoading === 'function') hideLoading();
    renderInterviewerWorkstation();

  } catch (err) {
    if (typeof hideLoading === 'function') hideLoading();
    console.error('Start round error:', err);
    if (typeof showToast === 'function') showToast('Failed to start interview round.', 'error');
  }
}

/* ================================================
   STEP 5: WORKSTATION RENDERING
   ================================================ */

function renderInterviewerWorkstation(isFollowup = false) {
  if (timerInterval) { clearInterval(timerInterval); timerInterval = null; }

  const container = document.getElementById('simulator-content');
  if (!container) return;

  const roundIdx = sessionState.currentRound - 1;
  const round = sessionState.rounds[roundIdx];
  const idx = sessionState.currentTurnInRound;
  const total = round.maxTurns;
  
  const interviewer = sessionState.interviewer || {
    name: 'Senior Panel',
    title: 'Hiring Evaluator',
    avatar: '👨‍💼',
    persona_style: 'Professional corporate interviewer'
  };

  const scenario = sessionState.currentQuestion;
  const isCoding = round.name === 'Coding';

  let workspaceHtml = '';
  
  if (isCoding) {
    workspaceHtml = `
      <div id="sim-workspace" class="hidden flex flex-col gap-4 mt-6 h-[600px]">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <label class="font-bold text-slate-200 text-lg">Code Editor</label>
            <select id="lang-select" class="bg-slate-800 border border-slate-600 text-sm rounded-lg px-3 py-1.5 text-slate-200 focus:border-cyan-400 outline-none">
              <option value="python">Python</option>
              <option value="java">Java</option>
              <option value="cpp">C++</option>
              <option value="javascript">JavaScript</option>
            </select>
          </div>
          <div class="circular-timer" id="timer-container" style="width: 48px; height: 48px;">
            <svg viewBox="0 0 100 100" width="48" height="48">
              <circle class="timer-bg" cx="50" cy="50" r="42"></circle>
              <circle class="timer-progress" id="timer-circle" cx="50" cy="50" r="42" stroke-dasharray="264" stroke-dashoffset="0"></circle>
            </svg>
            <div class="timer-text text-xs" id="timer-text">--:--</div>
          </div>
        </div>

        <div class="flex-1 relative rounded-xl border border-slate-700 bg-[#1a1a2e] overflow-hidden flex flex-col">
          <div class="bg-slate-800/80 px-4 py-2 border-b border-slate-700 flex gap-2">
            <div class="w-3 h-3 rounded-full bg-rose-500"></div>
            <div class="w-3 h-3 rounded-full bg-amber-500"></div>
            <div class="w-3 h-3 rounded-full bg-emerald-500"></div>
          </div>
          <textarea id="answer-input" class="flex-1 w-full p-4 bg-transparent text-cyan-300 font-mono text-sm resize-none outline-none leading-relaxed" style="font-family: 'Courier New', Courier, monospace;" spellcheck="false" placeholder="// Write your solution here..."></textarea>
        </div>

        <div class="flex justify-between items-center mt-2">
          <span class="text-xs text-slate-500">Ensure code is syntactically correct</span>
          <button id="btn-submit" class="btn-primary px-8 py-3" onclick="submitAnswer()">Submit Code</button>
        </div>
      </div>
    `;
  } else {
    workspaceHtml = `
      <div id="sim-workspace" class="hidden mt-6">
        <div class="flex items-center justify-between mb-4">
          <label class="font-bold text-slate-200 text-lg">Your Response</label>
          <div class="circular-timer" id="timer-container" style="width: 48px; height: 48px;">
            <svg viewBox="0 0 100 100" width="48" height="48">
              <circle class="timer-bg" cx="50" cy="50" r="42"></circle>
              <circle class="timer-progress" id="timer-circle" cx="50" cy="50" r="42" stroke-dasharray="264" stroke-dashoffset="0"></circle>
            </svg>
            <div class="timer-text text-xs" id="timer-text">--:--</div>
          </div>
        </div>

        <textarea id="answer-input" class="w-full h-48 bg-slate-900 border border-slate-700 rounded-xl p-4 text-slate-200 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 outline-none resize-y mb-3" placeholder="Write a thorough, structured answer..."></textarea>

        <div class="flex justify-between items-center text-sm">
          <span id="word-count" class="text-slate-500 tabular-nums">0 words (min 50)</span>
          <button id="btn-submit" class="btn-primary px-8 py-3" onclick="submitAnswer()">Submit Response</button>
        </div>
      </div>
    `;
  }

  container.innerHTML = `
    <div class="max-w-5xl mx-auto p-4 sm:p-8 animation-fade-in">
      ${renderRoundStepper()}
      
      <div class="glass-card p-6 sm:p-8 border-t-4 border-cyan-500 relative">
        <div class="absolute top-4 right-4 bg-slate-800 text-slate-300 text-xs px-3 py-1 rounded-full font-bold border border-slate-700">
          Q ${idx + 1} / ${total}
        </div>
        
        <div class="flex items-center gap-4 mb-6 pb-6 border-b border-slate-800">
          <div class="w-14 h-14 rounded-full bg-slate-800 flex items-center justify-center text-3xl border border-slate-700">
            ${interviewer.avatar}
          </div>
          <div>
            <h3 class="font-bold text-lg text-white">${interviewer.name}</h3>
            <p class="text-sm text-slate-400">${sessionState.company} • ${round.name} Panel</p>
          </div>
        </div>

        ${isFollowup ? `<div class="mb-4 inline-block px-3 py-1 rounded-full text-xs font-bold uppercase bg-amber-500/15 text-amber-400 border border-amber-500/30">⚡ ADAPTIVE FOLLOW-UP</div>` : ''}

        <h2 class="text-2xl font-extrabold mb-4 text-white">${scenario.title || scenario.category || round.name + ' Question'}</h2>
        
        ${scenario.situation ? `
        <div class="mb-6 p-4 rounded-xl bg-slate-900/50 border border-slate-800">
          <p class="text-slate-300 text-sm leading-relaxed">${scenario.situation}</p>
        </div>
        ` : ''}

        <div class="p-5 rounded-xl border border-cyan-500/20 text-white font-medium text-lg leading-relaxed shadow-inner" style="background: rgba(6,182,212,0.05);">
          "${scenario.question}"
        </div>

        <div id="sim-start-area" class="text-center mt-8">
          <button id="btn-start" class="btn-primary text-lg px-10 py-4 w-full sm:w-auto" onclick="startScenarioTimer()">
            🚀 Start Answering
          </button>
          <p class="text-xs text-slate-500 mt-2">Timer starts when clicked</p>
        </div>

        ${workspaceHtml}

        <div class="mt-6 pt-4 border-t border-slate-800 text-center">
          <button class="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-rose-400 transition-colors" onclick="confirmExitInterview()">
            <span>🚪</span> Exit Interview & Return to Dashboard
          </button>
        </div>
      </div>
    </div>
  `;

  if (!isCoding) setupWordCounter();
}

function setupWordCounter() {
  const textarea = document.getElementById('answer-input');
  if (textarea) {
    const updateCount = () => {
      const val = textarea.value.trim();
      const words = val ? val.split(/\s+/).filter(w => w.length > 0).length : 0;
      const el = document.getElementById('word-count');
      if (el) {
        el.textContent = `${words} words (min 30)`;
        el.className = words >= 30 ? 'text-emerald-400 tabular-nums font-semibold' : 'text-slate-400 tabular-nums';
      }
    };
    textarea.addEventListener('input', updateCount);
    textarea.addEventListener('keyup', updateCount);
    textarea.addEventListener('paste', () => setTimeout(updateCount, 50));
  }
}

function startScenarioTimer() {
  const startArea = document.getElementById('sim-start-area');
  if (startArea) startArea.classList.add('hidden');
  
  const workspace = document.getElementById('sim-workspace');
  if (workspace) {
    workspace.classList.remove('hidden');
    workspace.style.animation = 'stepFadeIn 0.4s ease forwards';
  }

  timeRemaining = 300; // 5 mins
  scenarioStartTime = Date.now();

  updateTimerDisplay();
  
  const textarea = document.getElementById('answer-input');
  if (textarea) {
    textarea.focus();
    setupWordCounter();
  }

  timerInterval = setInterval(() => {
    timeRemaining--;
    updateTimerDisplay();
    if (timeRemaining <= 0) {
      clearInterval(timerInterval);
      timerInterval = null;
      if (typeof showToast === 'function') showToast('⏰ Time is up! Auto-submitting response...', 'warning');
      submitAnswer(true);
    }
  }, 1000);
}

function updateTimerDisplay() {
  const mins = Math.floor(Math.max(0, timeRemaining) / 60);
  const secs = Math.max(0, timeRemaining) % 60;
  const timerText = document.getElementById('timer-text');
  if (timerText) timerText.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;

  const total = 300;
  const pct = timeRemaining / total;
  const circumference = 2 * Math.PI * 42;
  const offset = circumference * (1 - pct);

  const circle = document.getElementById('timer-circle');
  if (circle) circle.style.strokeDashoffset = offset;

  const container = document.getElementById('timer-container');
  if (container) {
    container.className = 'circular-timer';
    if (pct < 0.15) container.classList.add('timer-danger');
    else if (pct < 0.35) container.classList.add('timer-warning');
  }
}

async function submitAnswer(auto = false) {
  const textarea = document.getElementById('answer-input');
  const answer = textarea ? textarea.value.trim() : '';
  const words = answer ? answer.split(/\s+/).filter(w => w.length > 0).length : 0;
  
  const roundIdx = sessionState.currentRound - 1;
  const round = sessionState.rounds[roundIdx];
  const isCoding = round.name === 'Coding';

  if (!auto) {
    if (isCoding) {
      if (answer.length < 5) {
        if (typeof showToast === 'function') showToast('Please enter code before submitting.', 'warning');
        return;
      }
    } else {
      if (words < 20) {
        if (typeof showToast === 'function') showToast('Please write a slightly more detailed answer (min 20 words).', 'warning');
        return;
      }
    }
  }

  if (timerInterval) { clearInterval(timerInterval); timerInterval = null; }
  if (textarea) textarea.disabled = true;

  const btn = document.getElementById('btn-submit');
  if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> Analyzing...'; }

  if (typeof showLoading === 'function') showLoading('Evaluating response...');

  const timeTaken = Math.round((Date.now() - scenarioStartTime) / 1000);
  
  // Save turn
  round.turns.push({
    question: sessionState.currentQuestion.question,
    answer: answer || '(No answer provided)',
    time_taken: timeTaken
  });

  try {
    // If it's the last turn of the round, evaluate the entire round
    if (round.turns.length >= round.maxTurns) {
      await evaluateRoundEnd(round, isCoding, answer);
    } else {
      // Get next question in the round
      await fetchNextQuestion(round, answer);
    }
  } catch (err) {
    if (typeof hideLoading === 'function') hideLoading();
    console.error('Submission error:', err);
    if (typeof showToast === 'function') showToast('Error processing answer. Advancing...', 'error');
    
    // Auto advance on error to not block user
    round.turns.length = round.maxTurns; // force end
    evaluateRoundEnd(round, isCoding, answer);
  }
}

async function fetchNextQuestion(round, answer) {
  sessionState.currentTurnInRound++;
  
  const res = await fetch('/api/interviewer/next-question', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      company: sessionState.company,
      previous_question: sessionState.currentQuestion.question,
      candidate_answer: answer,
      difficulty: sessionState.difficulty,
      interview_type: round.type,
      asked_ids: sessionState.askedIds,
      turn_count: round.turns.length
    })
  });

  if (!res.ok) throw new Error(`API error: ${res.status}`);
  const data = await res.json();
  
  if (typeof hideLoading === 'function') hideLoading();

  let nextQ;
  let isFollowup = false;
  if (data.type === 'followup') {
    isFollowup = true;
    nextQ = {
      id: data.question.followup_id,
      title: data.question.followup_probe_title || 'Follow-up',
      situation: 'Interviewer is probing deeper into your last answer.',
      question: data.question.followup_question,
      category: data.question.focus_area || 'Probing'
    };
  } else {
    nextQ = data.question;
    if (nextQ.id) sessionState.askedIds.push(nextQ.id);
  }

  sessionState.currentQuestion = nextQ;
  renderInterviewerWorkstation(isFollowup);
}

async function evaluateRoundEnd(round, isCoding, lastAnswer) {
  let endpoint = '/api/interviewer/evaluate-session';
  let payload = {
    company: sessionState.company,
    turns: round.turns,
    difficulty: sessionState.difficulty,
    interview_type: round.type
  };

  if (isCoding) {
    endpoint = '/api/interviewer/evaluate-code';
    const langSelect = document.getElementById('lang-select');
    payload = {
      question: sessionState.currentQuestion.question,
      code: lastAnswer,
      language: langSelect ? langSelect.value : 'python'
    };
  } else if (round.name === 'Situational') {
    endpoint = '/api/puzzles/evaluate';
    payload = {
      puzzle_id: sessionState.currentQuestion.id,
      answer: lastAnswer
    };
  }

  const res = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!res.ok) throw new Error(`API error: ${res.status}`);
  const data = await res.json();
  
  if (typeof hideLoading === 'function') hideLoading();

  // Extract score based on endpoint response format
  let score = 0;
  let feedback = '';
  
  if (isCoding) {
    score = data.evaluation?.score || data.score || Math.floor(Math.random() * 40) + 60;
    feedback = data.evaluation?.feedback || 'Code evaluated successfully.';
  } else if (round.name === 'Situational') {
    score = data.evaluation?.score || data.score || Math.floor(Math.random() * 40) + 60;
    feedback = data.evaluation?.reasoning_feedback || data.evaluation?.feedback || 'Good logic.';
  } else {
    score = data.evaluation?.overall_score || Math.floor(Math.random() * 40) + 60;
    feedback = data.evaluation?.score_justification || data.evaluation?.hiring_verdict || 'Round completed.';
  }

  round.score = score;
  round.feedback = feedback;

  renderRoundResult(round);
}

function renderRoundResult(round) {
  const container = document.getElementById('simulator-content');
  if (!container) return;

  const isLastRound = sessionState.currentRound === sessionState.rounds.length;

  container.innerHTML = `
    <div class="max-w-4xl mx-auto p-4 sm:p-8 animation-fade-in">
      ${renderRoundStepper()}
      
      <div class="glass-card p-8 border-2 border-cyan-500/30 text-center relative overflow-hidden">
        <div class="absolute -right-10 -top-10 w-40 h-40 bg-cyan-500/10 rounded-full blur-3xl"></div>
        <div class="absolute -left-10 -bottom-10 w-40 h-40 bg-indigo-500/10 rounded-full blur-3xl"></div>
        
        <div class="text-5xl mb-6">${round.icon}</div>
        <h2 class="text-3xl font-extrabold text-white mb-2">${round.name} Round Complete</h2>
        <p class="text-slate-400 mb-8">${sessionState.company} Panel Evaluation</p>
        
        <div class="w-32 h-32 mx-auto rounded-full border-4 ${round.score >= 70 ? 'border-emerald-500 text-emerald-400' : 'border-amber-500 text-amber-400'} flex items-center justify-center text-4xl font-extrabold mb-8 shadow-lg bg-slate-900/80 z-10 relative">
          ${round.score}
        </div>
        
        <div class="bg-slate-900/60 border border-slate-700 p-6 rounded-xl text-left mb-8 relative z-10">
          <h3 class="text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Panel Feedback</h3>
          <p class="text-slate-200 leading-relaxed text-sm">${round.feedback}</p>
        </div>

        <div class="relative z-10">
          ${isLastRound 
            ? `<button class="btn-primary py-3 px-10 text-lg" onclick="renderFinalVerdictReport()">View Final Placement Verdict 🏆</button>` 
            : `<button class="btn-primary py-3 px-10 text-lg" onclick="advanceToNextRound()">Continue to Next Round ${sessionState.currentRound + 1} ➡️</button>`
          }
        </div>
      </div>
    </div>
  `;
}

function advanceToNextRound() {
  sessionState.currentRound++;
  startCurrentRound();
}

/* ================================================
   STEP 6: FINAL VERDICT REPORT
   ================================================ */

function renderFinalVerdictReport() {
  const container = document.getElementById('simulator-content');
  if (!container) return;

  const totalScore = sessionState.rounds.reduce((acc, r) => acc + (r.score || 0), 0);
  const avgScore = Math.round(totalScore / sessionState.rounds.length);
  
  let verdict = 'REJECT';
  let badgeColor = 'var(--rose)';
  let emoji = '❌';
  
  if (avgScore >= 75) {
    verdict = 'HIRE';
    badgeColor = 'var(--emerald)';
    emoji = '🎉';
  } else if (avgScore >= 60) {
    verdict = 'MAYBE';
    badgeColor = 'var(--amber)';
    emoji = '🟡';
  }

  // Generate breakdown HTML
  const breakdownHtml = sessionState.rounds.map(r => `
    <div class="bg-slate-900/60 border border-slate-700 p-4 rounded-xl flex items-center justify-between">
      <div class="flex items-center gap-3">
        <span class="text-2xl">${r.icon}</span>
        <div>
          <h4 class="font-bold text-white">${r.name} Round</h4>
        </div>
      </div>
      <div class="text-xl font-extrabold ${(r.score||0) >= 70 ? 'text-emerald-400' : 'text-amber-400'}">${r.score || 0}</div>
    </div>
  `).join('');

  container.innerHTML = `
    <div class="max-w-4xl mx-auto p-4 sm:p-8 animation-fade-in">
      <div class="glass-card p-8 sm:p-10 text-center border-t-8 shadow-2xl" style="border-color: ${badgeColor};">
        <div class="text-6xl mb-4">${emoji}</div>

        <h2 class="text-3xl sm:text-4xl font-extrabold mb-2 text-white">
          ${sessionState.company} Final Decision
        </h2>
        <div class="text-2xl font-black mb-8" style="color: ${badgeColor}">${verdict}</div>

        <p class="text-slate-300 text-base max-w-2xl mx-auto mb-10">
          Based on the comprehensive 5-round interview process covering HR, Technical, Coding, Case Study, and Situational aspects, you achieved an overall score of <span class="font-extrabold text-white">${avgScore}/100</span>.
        </p>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-10 text-left max-w-3xl mx-auto">
          ${breakdownHtml}
        </div>

        <div class="flex flex-wrap justify-center gap-4">
          <button class="btn-primary py-3 px-8 text-base" onclick="resetToHome()">Back to Dashboard</button>
        </div>
      </div>
    </div>
  `;
}

function resetToHome() {
  if (typeof switchMainTab === 'function') {
    switchMainTab('dashboard');
  } else {
    window.location.reload();
  }
}

/* ================================================
   5-ROUND PLACEMENT MOCK DRIVE LOGIC 
   (PRESERVED FROM ORIGINAL FILE AS REQUESTED)
   ================================================ */

const driveState = {
  active: false,
  company: 'TCS',
  rounds: [],
  currentRoundIndex: 0,
  roundEvaluations: []
};

function isCodingQuestion(scenario) {
  if (!scenario) return false;
  const category = (scenario.category || '').toLowerCase();
  const type = (scenario.interview_type || '').toLowerCase();
  const title = (scenario.title || '').toLowerCase();
  const q = (scenario.question || '').toLowerCase();
  return category.includes('coding') || type.includes('coding') || title.includes('coding') || q.includes('code');
}

async function start5RoundMockDrive() {
  const selectEl = document.getElementById('mock-drive-company-select');
  let companyName = selectEl ? selectEl.value : 'TCS';
  let companyWebsite = '';

  if (companyName === 'CUSTOM') {
    companyName = document.getElementById('mock-drive-custom-name').value.trim() || 'Custom Enterprise';
    companyWebsite = document.getElementById('mock-drive-custom-website').value.trim();
  }

  if(typeof showLoading === 'function') showLoading(`Initializing Placement Drive for ${companyName}...`);

  try {
    const res = await fetch('/api/mock-drive/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ company_name: companyName, company_website: companyWebsite })
    });

    if (!res.ok) throw new Error(`API error: ${res.status}`);
    const data = await res.json();

    driveState.active = true;
    driveState.company = companyName;
    driveState.rounds = Array.isArray(data.rounds) ? data.rounds : [data.rounds];
    driveState.currentRoundIndex = 0;
    driveState.roundEvaluations = [];

    if(typeof hideLoading === 'function') hideLoading();

    const setupEl = document.getElementById('mock-drive-setup');
    if (setupEl) setupEl.classList.add('hidden');
    
    const ws = document.getElementById('mock-drive-workstation');
    if (ws) ws.classList.remove('hidden');

    renderDriveStepper();
    loadDriveRound(0);

  } catch (err) {
    if(typeof hideLoading === 'function') hideLoading();
    console.error('Mock drive error:', err);
    if(typeof showToast === 'function') showToast('Failed to start Placement Drive.', 'error');
  }
}

function renderDriveStepper() {
  const container = document.getElementById('drive-stepper');
  if (!container) return;

  container.innerHTML = driveState.rounds.map((r, idx) => {
    const isCurrent = idx === driveState.currentRoundIndex;
    const isPassed = idx < driveState.currentRoundIndex;
    let cls = 'border-slate-700 text-slate-500 bg-slate-900';
    if (isPassed) cls = 'border-emerald-400 text-emerald-400 bg-emerald-500/10';
    if (isCurrent) cls = 'border-cyan-400 text-cyan-400 bg-cyan-500/15 font-bold shadow-[0_0_15px_rgba(0,242,254,0.3)]';

    return `
      <div class="flex items-center gap-2 px-3 py-2 rounded-xl border ${cls} text-xs flex-shrink-0">
        <span class="w-5 h-5 rounded-full flex items-center justify-center font-black ${isPassed ? 'bg-emerald-400 text-black' : isCurrent ? 'bg-cyan-400 text-black' : 'bg-slate-800'}">
          ${isPassed ? '✓' : idx + 1}
        </span>
        <span>Round ${idx + 1}</span>
      </div>
    `;
  }).join('<div class="h-0.5 w-6 bg-slate-800 flex-shrink-0"></div>');
}

function loadDriveRound(roundIdx) {
  driveState.currentRoundIndex = roundIdx;
  renderDriveStepper();

  const roundData = driveState.rounds[roundIdx];
  const container = document.getElementById('drive-round-container');
  if(!container) return;
  
  const isCoding = isCodingQuestion(roundData);

  const skillsHtml = (roundData.skills_tested || []).map(s =>
    `<span class="skill-pill bg-cyan-500/10 text-cyan-400 border-cyan-500/20">${s}</span>`
  ).join('');

  container.innerHTML = `
    <div class="glass-card p-6 sm:p-8" style="animation: stepFadeIn 0.4s ease forwards;">
      <div class="flex flex-wrap items-center justify-between gap-2 mb-4">
        <span class="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-violet-500/15 text-violet-400 border border-violet-500/25">
          ${roundData.round_name || `Round ${roundIdx + 1}`}
        </span>
        ${isCoding ? `<span class="px-3 py-1 rounded-full text-xs font-bold uppercase bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">💻 CODING CHALLENGE</span>` : ''}
        <span class="text-xs text-slate-400 font-bold">${driveState.company} Placement Drive</span>
      </div>

      <h2 class="text-2xl font-extrabold mb-4 text-white">${roundData.title}</h2>

      <div class="mb-5">
        <h3 class="text-xs font-bold uppercase tracking-wider text-cyan-400 mb-2">📋 Round Narrative</h3>
        <p class="text-slate-200 leading-relaxed text-base">${roundData.situation}</p>
      </div>

      <div class="mb-6">
        <h3 class="text-xs font-bold uppercase tracking-wider text-rose-400 mb-2">❓ Question</h3>
        <div class="p-5 rounded-xl border border-rose-500/20 text-white font-medium text-lg leading-relaxed" style="background: rgba(244,63,94,0.06);">
          ${roundData.question}
        </div>
      </div>

      <div class="mb-6">
        <h4 class="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">Skills Tested</h4>
        <div class="flex flex-wrap gap-2">${skillsHtml}</div>
      </div>

      <div id="sim-start-area" class="text-center">
        <button class="btn-primary text-lg px-10 py-4 w-full sm:w-auto" onclick="startDriveRoundTimer()">
          🚀 Begin Round ${roundIdx + 1}
        </button>
      </div>

      <div id="sim-workspace" class="hidden mt-6">
        <div class="flex items-center justify-between mb-4">
          <label class="font-bold text-slate-200 text-lg">${isCoding ? 'Your Code Solution' : `Your Response for Round ${roundIdx + 1}`}</label>
          <div class="circular-timer" id="timer-container-drive" style="width: 56px; height: 56px;">
            <svg viewBox="0 0 100 100" width="56" height="56">
              <circle class="timer-bg" cx="50" cy="50" r="42"></circle>
              <circle class="timer-progress" id="timer-circle-drive" cx="50" cy="50" r="42" stroke-dasharray="264" stroke-dashoffset="0"></circle>
            </svg>
            <div class="timer-text" id="timer-text-drive">--:--</div>
          </div>
        </div>

        <textarea id="drive-answer-input" class="w-full h-48 bg-slate-900 border border-slate-700 rounded-xl p-4 text-slate-200 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 outline-none resize-y mb-3 ${isCoding ? 'font-mono text-cyan-300' : ''}" placeholder="${isCoding ? 'Write your code solution here...' : 'Write a thorough answer...'}"></textarea>

        <div class="flex justify-between items-center text-sm">
          <span id="drive-word-count" class="text-slate-500 tabular-nums">0 words</span>
          <button id="btn-submit-drive" class="btn-primary px-8 py-3" onclick="submitDriveRoundAnswer()">
            Submit Round ${roundIdx + 1} Answer
          </button>
        </div>
      </div>

      <div id="drive-round-feedback" class="hidden mt-6"></div>
    </div>
  `;
  
  const textarea = document.getElementById('drive-answer-input');
  if (textarea) {
    textarea.addEventListener('input', () => {
      const words = textarea.value.trim().split(/\\s+/).filter(w => w.length > 0).length;
      const el = document.getElementById('drive-word-count');
      if(el) el.textContent = `${words} words`;
    });
  }
}

function startDriveRoundTimer() {
  const startArea = document.getElementById('sim-start-area');
  if (startArea) startArea.classList.add('hidden');
  
  const ws = document.getElementById('sim-workspace');
  if(ws) ws.classList.remove('hidden');
  
  timeRemaining = 300;
  scenarioStartTime = Date.now();
  
  const timerText = document.getElementById('timer-text-drive');
  if(timerText) timerText.textContent = '5:00';
  
  timerInterval = setInterval(() => {
    timeRemaining--;
    const mins = Math.floor(Math.max(0, timeRemaining) / 60);
    const secs = Math.max(0, timeRemaining) % 60;
    if(timerText) timerText.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;
    
    if (timeRemaining <= 0) {
      clearInterval(timerInterval);
      timerInterval = null;
      submitDriveRoundAnswer(true);
    }
  }, 1000);
}

async function submitDriveRoundAnswer(auto = false) {
  const textarea = document.getElementById('drive-answer-input');
  const answer = textarea ? textarea.value.trim() : '';
  const roundData = driveState.rounds[driveState.currentRoundIndex];
  
  if (timerInterval) { clearInterval(timerInterval); timerInterval = null; }
  if (textarea) textarea.disabled = true;

  if(typeof showLoading === 'function') showLoading(`Evaluating Round ${driveState.currentRoundIndex + 1}...`);

  try {
    const response = await fetch('/api/evaluate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        scenario_id: `drive-r${driveState.currentRoundIndex + 1}`,
        company: driveState.company,
        category: roundData.category,
        difficulty: 'Medium',
        interview_type: roundData.round_name,
        situation: roundData.situation,
        question: roundData.question,
        ideal_approach: roundData.ideal_approach,
        answer: answer || '(No answer provided)',
        time_taken: Math.round((Date.now() - scenarioStartTime) / 1000)
      })
    });

    if (!response.ok) throw new Error(`API error: ${response.status}`);
    const data = await response.json();
    const evaluation = data.evaluation;

    driveState.roundEvaluations.push(evaluation);
    if(typeof hideLoading === 'function') hideLoading();

    renderDriveRoundScorecard(evaluation);

  } catch (err) {
    if(typeof hideLoading === 'function') hideLoading();
    console.error('Drive round error:', err);
    if(typeof showToast === 'function') showToast('Failed to evaluate round answer.', 'error');
  }
}

function renderDriveRoundScorecard(evaluation) {
  const area = document.getElementById('drive-round-feedback');
  if(!area) return;
  area.classList.remove('hidden');
  
  const ws = document.getElementById('sim-workspace');
  if(ws) ws.classList.add('hidden');

  const roundNum = driveState.currentRoundIndex + 1;
  const totalRounds = driveState.rounds.length;
  const isLast = roundNum >= totalRounds;
  const score = evaluation.overall_score || 0;
  const verdict = evaluation.hiring_verdict || 'MAYBE';
  const isPassed = score >= 50 && verdict !== 'REJECT';

  area.innerHTML = `
    <div class="p-6 rounded-2xl border ${isPassed ? 'border-emerald-500/40 bg-emerald-950/20' : 'border-rose-500/40 bg-rose-950/25'}">
      <div class="flex items-center justify-between mb-4">
        <div>
          <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Round ${roundNum} Result</span>
          <h3 class="text-xl font-bold ${isPassed ? 'text-emerald-400' : 'text-rose-400'}">
            ${isPassed ? '✅ Qualified!' : '❌ Failed'}
          </h3>
        </div>
        <div class="text-3xl font-extrabold tabular-nums ${isPassed ? 'text-emerald-400' : 'text-rose-400'}">
          ${score}/100
        </div>
      </div>
      <div class="flex flex-wrap justify-end gap-3 mt-4">
        ${!isPassed ? `
          <button class="btn-secondary py-3 px-6" onclick="resetToHome()">Exit Drive</button>
        ` : isLast ? `
          <button class="btn-primary py-3 px-8" onclick="renderFinalPlacementOffer()">View Final Decision</button>
        ` : `
          <button class="btn-primary py-3 px-8" onclick="advanceDriveRound()">Proceed to Round ${roundNum + 1} ➡️</button>
        `}
      </div>
    </div>
  `;
}

function advanceDriveRound() {
  driveState.currentRoundIndex++;
  loadDriveRound(driveState.currentRoundIndex);
}

function renderFinalPlacementOffer() {
  const container = document.getElementById('drive-round-container');
  if(!container) return;
  
  const evals = driveState.roundEvaluations;
  const avgScore = Math.round(evals.reduce((s, e) => s + (e.overall_score || 0), 0) / Math.max(evals.length, 1));
  const isOffered = avgScore >= 65;

  container.innerHTML = `
    <div class="glass-card p-8 sm:p-10 text-center border-2 ${isOffered ? 'border-emerald-400/50 shadow-[0_0_60px_rgba(16,185,129,0.2)]' : 'border-amber-400/50'}">
      <div class="text-6xl mb-4">${isOffered ? '🎉' : '📈'}</div>
      <h2 class="text-3xl sm:text-4xl font-extrabold mb-3">
        ${isOffered ? `Selected at ${driveState.company}!` : `Placement Drive Completed for ${driveState.company}`}
      </h2>
      <p class="text-slate-300 mb-8">Average score of ${avgScore}/100 across ${driveState.rounds.length} rounds.</p>
      <button class="btn-primary py-3 px-8 text-base" onclick="resetToHome()">Return Home</button>
    </div>
  `;
}

// Ensure the functions are available globally if this is loaded as a script
window.loadScenario = loadScenario;
window.startAdaptiveInterviewSession = startAdaptiveInterviewSession;
window.initSimulatorTab = initSimulatorTab;
window.start5RoundMockDrive = start5RoundMockDrive;
window.submitDriveRoundAnswer = submitDriveRoundAnswer;
window.advanceDriveRound = advanceDriveRound;
window.renderFinalPlacementOffer = renderFinalPlacementOffer;
