/* ================================================
   DASHBOARD MODULE — Pure Analytics & Performance Overview
   ================================================
   This module renders a comprehensive analytics dashboard
   with NO company selection (that lives in simulator.js).
   ================================================ */

const DASHBOARD_STORAGE_KEY = 'placifly_session_history';

/* ========== Interview Tips ========== */
const INTERVIEW_TIPS = [
  "💡 Use the STAR method (Situation, Task, Action, Result) for behavioral questions.",
  "🎯 Always clarify requirements before jumping into a complex solution.",
  "⚡ Practice thinking out loud — interviewers evaluate your thought process.",
  "🧠 Break down large engineering problems into modular sub-components.",
  "📝 Review system design patterns — rate limiters, caching, and sharding.",
  "🔥 For coding rounds, state time & space complexity before writing code.",
  "🗣️ Maintain eye contact and confident body language during HR rounds.",
  "📊 Prepare 2-3 strong projects you can discuss in depth with metrics.",
  "🤝 Ask insightful questions at the end — it shows genuine interest.",
  "🧩 For case studies, always start by structuring your approach on paper."
];

/* ========== Rank/Level Definitions ========== */
const RANK_LEVELS = [
  { min: 0,  label: 'Beginner',    icon: '🌱', color: 'text-slate-400'   },
  { min: 3,  label: 'Learner',     icon: '📖', color: 'text-blue-400'    },
  { min: 7,  label: 'Practitioner', icon: '⚡', color: 'text-cyan-400'   },
  { min: 15, label: 'Skilled',     icon: '🔥', color: 'text-amber-400'   },
  { min: 25, label: 'Expert',      icon: '💎', color: 'text-violet-400'  },
  { min: 50, label: 'Master',      icon: '🏆', color: 'text-emerald-400' }
];

/* ========== Session History Persistence ========== */

/**
 * Save a completed interview session to localStorage history.
 * Keeps the most recent 50 sessions.
 * @param {Object} sessionData - The session result data
 */
function saveSessionToHistory(sessionData) {
  try {
    const history = getSessionHistory();
    const newEntry = {
      id: sessionData.id || `session-${Date.now()}`,
      timestamp: Date.now(),
      company: sessionData.company || 'TCS',
      difficulty: sessionData.difficulty || 'Medium',
      score: Math.round(sessionData.score || sessionData.overall_score || 0),
      verdict: sessionData.verdict || sessionData.hiring_verdict || 'MAYBE',
      strengths: sessionData.strengths || sessionData.good_points || [],
      weaknesses: sessionData.weaknesses || sessionData.areas_to_improve || [],
      date: sessionData.date || new Date().toISOString().split('T')[0],
      rounds: sessionData.rounds || {}
    };
    history.unshift(newEntry);
    if (history.length > 50) history.pop();
    localStorage.setItem(DASHBOARD_STORAGE_KEY, JSON.stringify(history));
  } catch (err) {
    console.error('Failed to save session to history:', err);
  }
}

/**
 * Retrieve all stored session history from localStorage.
 * @returns {Array} Array of session objects, newest first
 */
function getSessionHistory() {
  try {
    const raw = localStorage.getItem(DASHBOARD_STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    return [];
  }
}

/* ========== Analytics Helper Functions ========== */

/**
 * Calculate the readiness score based on the most recent sessions.
 * Uses the last 5 sessions' average, weighted toward recent performance.
 */
function calcReadinessScore(history) {
  if (history.length === 0) return 0;
  const recent = history.slice(0, 5);
  const weightedSum = recent.reduce((sum, h, i) => {
    const weight = recent.length - i; // most recent = highest weight
    return sum + (h.score || 0) * weight;
  }, 0);
  const totalWeight = recent.reduce((sum, _, i) => sum + (recent.length - i), 0);
  return Math.min(100, Math.round(weightedSum / totalWeight));
}

/**
 * Calculate average score across all sessions.
 */
function calcAverageScore(history) {
  if (history.length === 0) return 0;
  const total = history.reduce((sum, h) => sum + (h.score || 0), 0);
  return Math.round(total / history.length);
}

/**
 * Calculate qualifying rate (% of sessions scoring > 70).
 */
function calcQualifyingRate(history) {
  if (history.length === 0) return 0;
  const qualified = history.filter(h => (h.score || 0) > 70).length;
  return Math.round((qualified / history.length) * 100);
}

/**
 * Get the current rank/level based on total session count.
 */
function getRank(totalSessions) {
  let rank = RANK_LEVELS[0];
  for (const r of RANK_LEVELS) {
    if (totalSessions >= r.min) rank = r;
  }
  return rank;
}

/**
 * Aggregate skill dimensions from session round scores.
 * Returns scores for: Communication, Technical, Problem Solving, Leadership, Code Quality
 */
function aggregateSkillDimensions(history) {
  const defaults = { communication: 50, technical: 55, problemSolving: 50, leadership: 45, codeQuality: 50 };
  if (history.length === 0) return defaults;

  const recent = history.slice(0, 10);
  let commTotal = 0, techTotal = 0, psTotal = 0, leadTotal = 0, cqTotal = 0;
  let count = 0;

  recent.forEach(h => {
    const r = h.rounds || {};
    count++;
    commTotal += r.hr || r.communication || (h.score || 50);
    techTotal += r.technical || (h.score || 55);
    psTotal += r.case_study || r.problemSolving || (h.score || 50);
    leadTotal += r.situational || r.leadership || (h.score ? Math.max(40, h.score - 10) : 45);
    cqTotal += r.coding || r.codeQuality || (h.score || 50);
  });

  return {
    communication: Math.min(100, Math.round(commTotal / count)),
    technical: Math.min(100, Math.round(techTotal / count)),
    problemSolving: Math.min(100, Math.round(psTotal / count)),
    leadership: Math.min(100, Math.round(leadTotal / count)),
    codeQuality: Math.min(100, Math.round(cqTotal / count))
  };
}

/**
 * Extract top mastered and weak topics from session history.
 */
function getInsights(history) {
  const strengthMap = {};
  const weakMap = {};

  history.forEach(h => {
    (h.strengths || []).forEach(s => { strengthMap[s] = (strengthMap[s] || 0) + 1; });
    (h.weaknesses || []).forEach(w => { weakMap[w] = (weakMap[w] || 0) + 1; });
  });

  const mastered = Object.entries(strengthMap)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([topic]) => topic);

  const improve = Object.entries(weakMap)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([topic]) => topic);

  return { mastered, improve };
}

/* ========== Chart Instances (for cleanup) ========== */
let _trendChart = null;
let _radarChart = null;

/* ========== Main Dashboard Renderer ========== */

/**
 * Render the full analytics dashboard into #view-dashboard.
 * Called from app.js init() and on tab switch.
 */
function renderDashboard() {
  const container = document.getElementById('view-dashboard');
  if (!container) return;

  const history = getSessionHistory();
  const userEmail = localStorage.getItem('placifly_user_email') || 'Candidate';
  const displayName = userEmail.includes('@') ? userEmail.split('@')[0] : userEmail;
  const tip = INTERVIEW_TIPS[Math.floor(Math.random() * INTERVIEW_TIPS.length)];

  // Compute all analytics
  const totalSessions = history.length;
  const readiness = calcReadinessScore(history);
  const avgScore = calcAverageScore(history);
  const qualifyingRate = calcQualifyingRate(history);
  const rank = getRank(totalSessions);
  const skills = aggregateSkillDimensions(history);
  const insights = getInsights(history);

  // Color helpers
  const readinessColor = readiness >= 70 ? 'text-emerald-400' : readiness >= 40 ? 'text-amber-400' : 'text-rose-400';
  const avgColor = avgScore >= 70 ? 'text-emerald-400' : avgScore >= 40 ? 'text-cyan-400' : 'text-rose-400';
  const qualColor = qualifyingRate >= 60 ? 'text-emerald-400' : qualifyingRate >= 30 ? 'text-amber-400' : 'text-rose-400';

  container.innerHTML = `

    <!-- ============================================ -->
    <!-- SECTION 1: Welcome Banner                    -->
    <!-- ============================================ -->
    <div class="glass-card px-5 py-4 mb-6 border-cyan-500/20 bg-gradient-to-r from-cyan-900/20 via-indigo-900/15 to-violet-900/20 stagger-item">
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div>
          <h1 class="text-xl font-extrabold text-white mb-1">
            👋 Welcome back, <span class="text-gradient">${displayName}</span>
          </h1>
          <p class="text-xs text-slate-400">Your performance analytics & interview readiness overview</p>
        </div>
        <div class="flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-800/60 border border-white/5 max-w-md">
          <span class="text-base flex-shrink-0">💡</span>
          <span class="text-[11px] text-slate-300 leading-relaxed">${tip}</span>
        </div>
      </div>
    </div>

    <!-- ============================================ -->
    <!-- SECTION 2: Performance Summary Cards         -->
    <!-- ============================================ -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
      <!-- Readiness Score -->
      <div class="glass-card p-5 text-center stagger-item" style="animation-delay: 40ms">
        <div class="text-lg mb-1">🎯</div>
        <div class="text-slate-400 text-[10px] font-bold uppercase tracking-wider mb-1">Readiness Score</div>
        <div class="text-3xl font-extrabold tabular-nums ${readinessColor}">${readiness}<span class="text-sm font-normal text-slate-500">%</span></div>
        <div class="text-[10px] text-slate-500 mt-1">${readiness >= 70 ? 'Interview Ready' : readiness >= 40 ? 'Getting There' : 'Keep Practicing'}</div>
      </div>

      <!-- Average Score -->
      <div class="glass-card p-5 text-center stagger-item" style="animation-delay: 80ms">
        <div class="text-lg mb-1">📊</div>
        <div class="text-slate-400 text-[10px] font-bold uppercase tracking-wider mb-1">Average Score</div>
        <div class="text-3xl font-extrabold tabular-nums ${avgColor}">${avgScore}<span class="text-sm font-normal text-slate-500">/100</span></div>
        <div class="text-[10px] text-slate-500 mt-1">${totalSessions} session${totalSessions !== 1 ? 's' : ''} total</div>
      </div>

      <!-- Qualifying Rate -->
      <div class="glass-card p-5 text-center stagger-item" style="animation-delay: 120ms">
        <div class="text-lg mb-1">✅</div>
        <div class="text-slate-400 text-[10px] font-bold uppercase tracking-wider mb-1">Qualifying Rate</div>
        <div class="text-3xl font-extrabold tabular-nums ${qualColor}">${qualifyingRate}<span class="text-sm font-normal text-slate-500">%</span></div>
        <div class="text-[10px] text-slate-500 mt-1">Score > 70 threshold</div>
      </div>

      <!-- Level / Rank -->
      <div class="glass-card p-5 text-center stagger-item" style="animation-delay: 160ms">
        <div class="text-lg mb-1">🏆</div>
        <div class="text-slate-400 text-[10px] font-bold uppercase tracking-wider mb-1">Your Rank</div>
        <div class="text-2xl font-extrabold ${rank.color}">${rank.icon} ${rank.label}</div>
        <div class="text-[10px] text-slate-500 mt-1">${totalSessions} interview${totalSessions !== 1 ? 's' : ''} completed</div>
      </div>
    </div>

    <!-- ============================================ -->
    <!-- SECTION 3 & 4: Charts (Trend + Radar)        -->
    <!-- ============================================ -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-6">
      <!-- Score Trend Chart -->
      <div class="glass-card p-5 stagger-item" style="animation-delay: 200ms">
        <h3 class="text-sm font-bold text-white mb-3 flex items-center gap-2">
          📈 Score Trend
          <span class="text-[10px] text-slate-500 font-normal">Last 10 sessions</span>
        </h3>
        <div style="height: 220px;"><canvas id="dashboardTrendChart"></canvas></div>
      </div>

      <!-- Skill Radar Chart -->
      <div class="glass-card p-5 stagger-item" style="animation-delay: 240ms">
        <h3 class="text-sm font-bold text-white mb-3 flex items-center gap-2">
          🎯 Skill Radar
          <span class="text-[10px] text-slate-500 font-normal">5 key dimensions</span>
        </h3>
        <div style="height: 220px;"><canvas id="dashboardRadarChart"></canvas></div>
      </div>
    </div>

    <!-- ============================================ -->
    <!-- SECTION 5: Quick Insights                    -->
    <!-- ============================================ -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
      <!-- Mastered Concepts -->
      <div class="glass-card p-5 border-emerald-500/10 stagger-item" style="animation-delay: 280ms">
        <h4 class="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
          ✅ Mastered Concepts
        </h4>
        ${insights.mastered.length > 0 ? `
          <div class="flex flex-col gap-2">
            ${insights.mastered.map(s => `
              <div class="flex items-center gap-2 px-3 py-2 rounded-lg bg-emerald-500/5 border border-emerald-500/15">
                <span class="text-emerald-400 text-xs">✓</span>
                <span class="text-xs text-emerald-200 font-medium">${s.length > 40 ? s.slice(0, 40) + '…' : s}</span>
              </div>
            `).join('')}
          </div>
        ` : `
          <p class="text-xs text-slate-500 italic">Complete some interviews to see your strengths here.</p>
        `}
      </div>

      <!-- Areas to Improve -->
      <div class="glass-card p-5 border-amber-500/10 stagger-item" style="animation-delay: 320ms">
        <h4 class="text-xs font-bold text-amber-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
          ⚠️ Areas to Improve
        </h4>
        ${insights.improve.length > 0 ? `
          <div class="flex flex-col gap-2">
            ${insights.improve.map(w => `
              <div class="flex items-center gap-2 px-3 py-2 rounded-lg bg-amber-500/5 border border-amber-500/15">
                <span class="text-amber-400 text-xs">⚡</span>
                <span class="text-xs text-amber-200 font-medium">${w.length > 40 ? w.slice(0, 40) + '…' : w}</span>
              </div>
            `).join('')}
          </div>
        ` : `
          <p class="text-xs text-slate-500 italic">Practice more to discover areas for improvement.</p>
        `}
      </div>
    </div>

    <!-- ============================================ -->
    <!-- SECTION 6: Recent Session History Table      -->
    <!-- ============================================ -->
    ${totalSessions > 0 ? `
    <div class="glass-card p-5 mb-6 stagger-item" style="animation-delay: 360ms">
      <h3 class="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
        📋 Recent Sessions
        <span class="text-[10px] text-slate-500 font-normal normal-case tracking-normal">Last 5 interviews</span>
      </h3>
      <div class="overflow-x-auto">
        <table class="w-full text-xs">
          <thead>
            <tr class="text-left text-slate-500 border-b border-white/5">
              <th class="pb-3 font-semibold">Company</th>
              <th class="pb-3 font-semibold">Difficulty</th>
              <th class="pb-3 font-semibold text-center">Score</th>
              <th class="pb-3 font-semibold text-center">Verdict</th>
              <th class="pb-3 font-semibold text-right">Date</th>
            </tr>
          </thead>
          <tbody>
            ${history.slice(0, 5).map(h => {
              const vColor = h.verdict === 'HIRE' ? 'text-emerald-400 bg-emerald-500/10' :
                             h.verdict === 'REJECT' ? 'text-rose-400 bg-rose-500/10' :
                             'text-amber-400 bg-amber-500/10';
              const diffColor = h.difficulty === 'Easy' ? 'text-emerald-400' :
                                h.difficulty === 'Hard' ? 'text-rose-400' : 'text-amber-400';
              const dateStr = h.date || 'N/A';
              return `
                <tr class="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
                  <td class="py-3 text-white font-semibold">${h.company || 'Unknown'}</td>
                  <td class="py-3 ${diffColor} font-medium">${h.difficulty || 'Medium'}</td>
                  <td class="py-3 text-center">
                    <span class="font-bold tabular-nums ${(h.score || 0) >= 70 ? 'text-emerald-400' : (h.score || 0) >= 40 ? 'text-amber-400' : 'text-rose-400'}">${h.score || 0}</span>
                    <span class="text-slate-500">/100</span>
                  </td>
                  <td class="py-3 text-center">
                    <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${vColor}">${h.verdict || 'MAYBE'}</span>
                  </td>
                  <td class="py-3 text-right text-slate-400">${dateStr}</td>
                </tr>`;
            }).join('')}
          </tbody>
        </table>
      </div>
    </div>
    ` : `
    <div class="glass-card p-8 mb-6 text-center stagger-item" style="animation-delay: 360ms">
      <div class="text-4xl mb-3">📭</div>
      <h3 class="text-sm font-bold text-white mb-1">No Sessions Yet</h3>
      <p class="text-xs text-slate-400">Start your first interview to see detailed analytics here.</p>
    </div>
    `}

    <!-- ============================================ -->
    <!-- SECTION 7: Quick Actions                     -->
    <!-- ============================================ -->
    <div class="mb-4">
      <h3 class="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
        ⚡ Quick Actions
      </h3>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <!-- Start Interview -->
        <div class="glass-card interactive p-5 text-center group stagger-item" style="animation-delay: 400ms"
             onclick="switchMainTab('simulator')">
          <div class="text-3xl mb-2 group-hover:scale-110 transition-transform">🎯</div>
          <h4 class="text-sm font-bold text-white mb-1">Start Interview</h4>
          <p class="text-[11px] text-slate-400 leading-relaxed">Select a company and begin your AI-powered mock interview</p>
        </div>

        <!-- Placement Drive -->
        <div class="glass-card interactive p-5 text-center group stagger-item" style="animation-delay: 440ms"
             onclick="switchMainTab('mock-drive')">
          <div class="text-3xl mb-2 group-hover:scale-110 transition-transform">🏢</div>
          <h4 class="text-sm font-bold text-white mb-1">Placement Drive</h4>
          <p class="text-[11px] text-slate-400 leading-relaxed">Simulate a full multi-round placement drive experience</p>
        </div>

        <!-- Resume Check -->
        <div class="glass-card interactive p-5 text-center group stagger-item" style="animation-delay: 480ms"
             onclick="switchMainTab('resume')">
          <div class="text-3xl mb-2 group-hover:scale-110 transition-transform">📄</div>
          <h4 class="text-sm font-bold text-white mb-1">Resume Check</h4>
          <p class="text-[11px] text-slate-400 leading-relaxed">Get AI-powered feedback and ATS score for your resume</p>
        </div>
      </div>
    </div>
  `;

  // Render charts after DOM is ready
  setTimeout(() => {
    renderDashboardTrend(history);
    renderDashboardRadar(history);
  }, 100);
}

/* ========== Chart Renderers ========== */

/**
 * Render a line chart showing score trend over the last 10 sessions.
 * Uses gradient area fill from cyan to transparent.
 */
function renderDashboardTrend(history) {
  const canvas = document.getElementById('dashboardTrendChart');
  if (!canvas || typeof Chart === 'undefined') return;

  // Destroy previous instance to prevent memory leaks
  if (_trendChart) { _trendChart.destroy(); _trendChart = null; }

  const recent = history.slice(0, 10).reverse();
  const labels = recent.map((h, i) => h.company || `Session ${i + 1}`);
  const scores = recent.map(h => h.score || 0);

  // Use sample data when no history exists
  const hasData = scores.length > 0;
  const chartLabels = hasData ? labels : ['S1', 'S2', 'S3', 'S4', 'S5'];
  const chartScores = hasData ? scores : [62, 68, 74, 71, 82];

  // Create gradient fill
  const ctx = canvas.getContext('2d');
  const gradient = ctx.createLinearGradient(0, 0, 0, 220);
  gradient.addColorStop(0, 'rgba(0, 242, 254, 0.20)');
  gradient.addColorStop(0.5, 'rgba(0, 242, 254, 0.08)');
  gradient.addColorStop(1, 'rgba(0, 242, 254, 0.0)');

  _trendChart = new Chart(canvas, {
    type: 'line',
    data: {
      labels: chartLabels,
      datasets: [{
        label: 'Score',
        data: chartScores,
        borderColor: '#00f2fe',
        backgroundColor: gradient,
        borderWidth: 2.5,
        pointBackgroundColor: '#00f2fe',
        pointBorderColor: '#0f172a',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
        tension: 0.4,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { intersect: false, mode: 'index' },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(15, 23, 42, 0.95)',
          borderColor: 'rgba(0, 242, 254, 0.3)',
          borderWidth: 1,
          titleFont: { size: 11, weight: 'bold' },
          bodyFont: { size: 11 },
          padding: 10,
          cornerRadius: 8,
          callbacks: {
            label: (ctx) => `Score: ${ctx.parsed.y}/100`
          }
        }
      },
      scales: {
        y: {
          min: 0,
          max: 100,
          ticks: { color: '#94a3b8', font: { size: 10 }, stepSize: 25 },
          grid: { color: 'rgba(255, 255, 255, 0.04)', drawBorder: false }
        },
        x: {
          ticks: { color: '#94a3b8', font: { size: 9 }, maxRotation: 0 },
          grid: { display: false }
        }
      }
    }
  });
}

/**
 * Render a radar chart showing 5 skill dimensions.
 * Dimensions: Communication, Technical, Problem Solving, Leadership, Code Quality
 */
function renderDashboardRadar(history) {
  const canvas = document.getElementById('dashboardRadarChart');
  if (!canvas || typeof Chart === 'undefined') return;

  // Destroy previous instance to prevent memory leaks
  if (_radarChart) { _radarChart.destroy(); _radarChart = null; }

  const skills = aggregateSkillDimensions(history);
  const dimensions = ['Communication', 'Technical', 'Problem Solving', 'Leadership', 'Code Quality'];
  const values = [
    skills.communication,
    skills.technical,
    skills.problemSolving,
    skills.leadership,
    skills.codeQuality
  ];

  _radarChart = new Chart(canvas, {
    type: 'radar',
    data: {
      labels: dimensions,
      datasets: [{
        label: 'Your Skills',
        data: values,
        borderColor: '#818cf8',
        backgroundColor: 'rgba(129, 140, 248, 0.12)',
        borderWidth: 2.5,
        pointBackgroundColor: '#a855f7',
        pointBorderColor: '#0f172a',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(15, 23, 42, 0.95)',
          borderColor: 'rgba(129, 140, 248, 0.3)',
          borderWidth: 1,
          titleFont: { size: 11, weight: 'bold' },
          bodyFont: { size: 11 },
          padding: 10,
          cornerRadius: 8,
          callbacks: {
            label: (ctx) => `${ctx.label}: ${ctx.parsed.r}/100`
          }
        }
      },
      scales: {
        r: {
          min: 0,
          max: 100,
          ticks: { display: false, stepSize: 25 },
          pointLabels: {
            color: '#cbd5e1',
            font: { size: 10, weight: '600' }
          },
          grid: { color: 'rgba(255, 255, 255, 0.06)' },
          angleLines: { color: 'rgba(255, 255, 255, 0.06)' }
        }
      }
    }
  });
}
