/* ================================================
   REPORT MODULE — Final Assessment Dashboard
   ================================================ */

async function generateReport(evaluations) {
  const container = document.getElementById('report-content');
  showLoading('📊 Generating your assessment report...');

  // Prepare results payload for API
  const resultsPayload = state.results.map(r => ({
    scenario_id: r.scenario_id,
    scores: r.scores,
    time_taken: r.time_taken
  }));

  const storedStats = getStoredStats();

  let report;
  try {
    const response = await fetch('/api/assessment/complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        results: resultsPayload,
        current_badges: storedStats.badges.map(b => b.id || b)
      })
    });

    if (!response.ok) throw new Error(`API error: ${response.status}`);
    const data = await response.json();
    report = data.report;
  } catch (err) {
    console.error('Report error:', err);
    // Fallback local calculation
    const avgScore = evaluations.length > 0
      ? Math.round(evaluations.reduce((sum, e) => sum + (e.overall_score || 0), 0) / evaluations.length)
      : 0;
    report = {
      overall_score: avgScore,
      strengths: ['Communication', 'Problem Solving'],
      weaknesses: ['Time Management'],
      company_readiness_percent: Math.min(100, Math.round(avgScore * 1.1)),
      placement_readiness: avgScore > 85 ? 'High' : avgScore > 60 ? 'Medium' : 'Low',
      skill_improvement_plan: 'Focus on practicing more scenarios regularly.',
      xp_earned: avgScore * evaluations.length,
      new_badges: []
    };
  }

  hideLoading();

  // Calculate average rubric scores across all evaluations
  const avgRubric = {};
  const rubricKeys = Object.keys(RUBRIC_LABELS);
  rubricKeys.forEach(key => {
    const scores = evaluations.map(e => (e.rubric_scores || {})[key] || 0);
    avgRubric[key] = scores.length > 0 ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0;
  });

  // Scenario scores for bar chart
  const scenarioScores = evaluations.map((e, i) => ({
    label: `Scenario ${i + 1}`,
    score: e.overall_score || 0
  }));

  const readinessColor = report.company_readiness_percent >= 80 ? 'text-emerald-400' :
    report.company_readiness_percent >= 60 ? 'text-cyan-400' : 'text-amber-400';

  const placementBadge = report.placement_readiness === 'High'
    ? '<span class="text-emerald-400 font-bold">🟢 High</span>'
    : report.placement_readiness === 'Medium'
    ? '<span class="text-amber-400 font-bold">🟡 Medium</span>'
    : '<span class="text-rose-400 font-bold">🔴 Low</span>';

  // Strengths & Weaknesses
  const strengthsHtml = (report.strengths || []).map(s =>
    `<li class="flex items-center gap-2"><span class="text-emerald-400">✦</span> ${s.replace(/_/g, ' ')}</li>`
  ).join('');

  const weaknessesHtml = (report.weaknesses || []).map(w =>
    `<li class="flex items-center gap-2"><span class="text-rose-400">✦</span> ${w.replace(/_/g, ' ')}</li>`
  ).join('');

  // Week plan
  const weekPlan = [
    { week: 'Week 1', icon: '📚', title: 'Foundation Building', desc: 'Review core concepts and practice structured responses using STAR methodology.' },
    { week: 'Week 2', icon: '🧠', title: 'Critical Thinking', desc: 'Focus on case study analysis, decision-making frameworks, and logical reasoning.' },
    { week: 'Week 3', icon: '🗣️', title: 'Communication Mastery', desc: 'Practice articulating solutions clearly, concisely, and with professional confidence.' },
    { week: 'Week 4', icon: '🎯', title: 'Mock Interviews', desc: 'Simulate full interview sessions with mixed scenario types at higher difficulty levels.' }
  ];

  const weekPlanHtml = weekPlan.map(w => `
    <div class="flex items-start gap-4 p-4 rounded-xl bg-slate-800/30 border border-white/5">
      <div class="text-2xl flex-shrink-0">${w.icon}</div>
      <div>
        <div class="font-bold text-sm text-cyan-400 mb-0.5">${w.week}: ${w.title}</div>
        <div class="text-xs text-slate-400">${w.desc}</div>
      </div>
    </div>
  `).join('');

  // Extract diagnostic metrics from evaluation
  const firstEval = evaluations[0] || {};
  const justification = firstEval.score_justification || report.skill_improvement_plan || '';
  const confidenceScore = firstEval.confidence_score || 90;
  const estimatedWpm = firstEval.estimated_wpm || 65;
  const expectedPoints = firstEval.expected_key_points || ['Structured approach', 'Core technical principles'];
  const missingConcepts = firstEval.missing_concepts || ['Specific quantitative metrics'];
  const commonMistakes = firstEval.common_mistakes || ['Vague generalization without trade-offs'];
  const idealFlow = firstEval.ideal_interview_flow || 'State principles -> detail architecture -> address trade-offs.';
  const modelAnswer = firstEval.better_model_answer || firstEval.ideal_company_answer || '';

  const expectedPointsHtml = expectedPoints.map(p =>
    `<li class="flex items-center gap-2 text-slate-300 text-xs"><span class="text-cyan-400">✓</span> ${p}</li>`
  ).join('');

  const missingConceptsHtml = missingConcepts.map(m =>
    `<li class="flex items-center gap-2 text-slate-300 text-xs"><span class="text-rose-400">✗</span> ${m}</li>`
  ).join('');

  const commonMistakesHtml = commonMistakes.map(cm =>
    `<li class="flex items-center gap-2 text-slate-300 text-xs"><span class="text-amber-400">⚠️</span> ${cm}</li>`
  ).join('');

  container.innerHTML = `
    <div id="pdf-report-area">
      <!-- Report Header -->
      <div class="text-center mb-10 pt-4">
        <h1 class="text-3xl sm:text-4xl font-extrabold mb-2">
          <span class="text-gradient">Assessment</span> Report
        </h1>
        <p class="text-slate-400">
          ${state.selectedCompany || 'Target Company'} • ${state.selectedDifficulty || 'Standard'} Level • ${state.selectedInterviewType || 'Placement'}
        </p>
      </div>

      <!-- Top Stats Grid -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div class="glass-card p-5 text-center">
          <div class="text-slate-400 text-xs font-bold uppercase tracking-wider mb-2">Overall Score</div>
          <div class="text-4xl font-extrabold ${report.overall_score >= 70 ? 'text-emerald-400' : 'text-amber-400'} tabular-nums">${Math.round(report.overall_score)}</div>
          <div class="text-xs text-slate-500 mt-1">/ 100</div>
        </div>
        <div class="glass-card p-5 text-center">
          <div class="text-slate-400 text-xs font-bold uppercase tracking-wider mb-2">Company Ready</div>
          <div class="text-4xl font-extrabold ${readinessColor} tabular-nums">${report.company_readiness_percent}%</div>
          <div class="text-xs text-slate-500 mt-1">Readiness</div>
        </div>
        <div class="glass-card p-5 text-center">
          <div class="text-slate-400 text-xs font-bold uppercase tracking-wider mb-2">AI Confidence</div>
          <div class="text-4xl font-extrabold text-cyan-400 tabular-nums">${confidenceScore}%</div>
          <div class="text-xs text-slate-500 mt-1">Eval Certainty</div>
        </div>
        <div class="glass-card p-5 text-center">
          <div class="text-slate-400 text-xs font-bold uppercase tracking-wider mb-2">Pace (WPM)</div>
          <div class="text-4xl font-extrabold text-violet-400 tabular-nums">${estimatedWpm}</div>
          <div class="text-xs text-slate-500 mt-1">Words / Min</div>
        </div>
      </div>

      <!-- Evaluation Justification Banner -->
      ${justification ? `
      <div class="glass-card p-5 mb-8 border-cyan-500/30 bg-cyan-950/20">
        <h3 class="text-xs font-bold uppercase tracking-wider text-cyan-400 mb-2 flex items-center gap-2">
          <span>💡</span> Evaluator Score Justification
        </h3>
        <p class="text-sm text-slate-200 leading-relaxed">${justification}</p>
      </div>` : ''}

      <!-- Key Points & Missing Concepts Grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div class="glass-card p-5 border-emerald-500/20 bg-emerald-950/10">
          <h3 class="font-bold text-emerald-400 mb-3 flex items-center gap-2 text-xs uppercase tracking-wider">
            <span>🎯</span> Expected Key Points
          </h3>
          <ul class="space-y-2">${expectedPointsHtml}</ul>
        </div>
        <div class="glass-card p-5 border-rose-500/20 bg-rose-950/10">
          <h3 class="font-bold text-rose-400 mb-3 flex items-center gap-2 text-xs uppercase tracking-wider">
            <span>🔍</span> Missing Concepts
          </h3>
          <ul class="space-y-2">${missingConceptsHtml}</ul>
        </div>
        <div class="glass-card p-5 border-amber-500/20 bg-amber-950/10">
          <h3 class="font-bold text-amber-400 mb-3 flex items-center gap-2 text-xs uppercase tracking-wider">
            <span>⚠️</span> Common Pitfalls
          </h3>
          <ul class="space-y-2">${commonMistakesHtml}</ul>
        </div>
      </div>

      <!-- Charts Row -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <!-- Radar Chart -->
        <div class="glass-card p-6">
          <h3 class="text-center font-bold text-sm uppercase tracking-wider text-slate-400 mb-4">Skills Radar</h3>
          <div class="chart-container">
            <canvas id="radarChart"></canvas>
          </div>
        </div>

        <!-- Bar Chart -->
        <div class="glass-card p-6">
          <h3 class="text-center font-bold text-sm uppercase tracking-wider text-slate-400 mb-4">Score Trend</h3>
          <div class="chart-container">
            <canvas id="barChart"></canvas>
          </div>
        </div>
      </div>

      <!-- Ideal Flow & Model Answer Banner -->
      ${modelAnswer ? `
      <div class="glass-card p-6 mb-8 border-violet-500/30 bg-violet-950/20">
        <div class="mb-4">
          <span class="text-xs font-bold uppercase tracking-wider text-violet-400">🎓 Ideal Interview Response Structure</span>
          <p class="text-xs text-slate-400 mt-1">${idealFlow}</p>
        </div>
        <div class="p-4 rounded-xl bg-slate-900/90 border border-slate-800 text-xs text-slate-200 leading-relaxed font-mono">
          ${modelAnswer}
        </div>
      </div>` : ''}

      <!-- Strengths & Weaknesses -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <div class="glass-card p-6">
          <h3 class="font-bold text-emerald-400 mb-4 flex items-center gap-2 text-sm uppercase tracking-wider">
            <span>💪</span> Key Strengths
          </h3>
          <ul class="space-y-2 text-sm text-slate-300 capitalize">${strengthsHtml}</ul>
        </div>
        <div class="glass-card p-6">
          <h3 class="font-bold text-rose-400 mb-4 flex items-center gap-2 text-sm uppercase tracking-wider">
            <span>📈</span> Growth Areas
          </h3>
          <ul class="space-y-2 text-sm text-slate-300 capitalize">${weaknessesHtml}</ul>
        </div>
      </div>

      <!-- Improvement Plan -->
      <div class="glass-card p-6 mb-8">
        <h3 class="font-bold text-sm uppercase tracking-wider text-slate-400 mb-4">📋 4-Week Improvement Plan</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          ${weekPlanHtml}
        </div>
      </div>
    </div>

    <!-- Action Buttons (outside PDF area) -->
    <div class="flex flex-wrap justify-center gap-3 mt-8">
      <button class="btn-primary flex items-center gap-2 px-6 py-3" onclick="downloadReport()">
        <span>📄</span> Download PDF Report
      </button>
      <button class="btn-secondary flex items-center gap-2 px-6 py-3" onclick="shareAchievement()">
        <span>🔗</span> Share Achievement
      </button>
      <button class="btn-secondary flex items-center gap-2 px-6 py-3" style="border-color: var(--violet); color: var(--purple);" onclick="location.reload()">
        <span>🔄</span> New Assessment
      </button>
    </div>
  `;

  // Render Charts
  setTimeout(() => {
    renderRadarChart(avgRubric);
    renderBarChart(scenarioScores);
  }, 200);

  // Handle new badges
  if (report.new_badges && report.new_badges.length > 0) {
    const stats = getStoredStats();
    report.new_badges.forEach((badge, i) => {
      stats.badges.push(badge);
      setTimeout(() => showBadgeUnlocked(badge), 800 + i * 2000);
    });
    saveStats(stats);
  }

  // Update stored XP
  if (report.xp_earned) {
    const stats = getStoredStats();
    const oldLevel = stats.level;
    stats.totalXP += report.xp_earned;
    stats.level = Math.floor(stats.totalXP / 500) + 1;
    if (stats.level > oldLevel) showLevelUp(stats.level);
    saveStats(stats);
    updateXPBar(stats.totalXP, stats.level);
  }
}

function renderRadarChart(avgRubric) {
  const ctx = document.getElementById('radarChart');
  if (!ctx) return;

  const labels = Object.keys(RUBRIC_LABELS).map(k => RUBRIC_LABELS[k]);
  const values = Object.keys(RUBRIC_LABELS).map(k => avgRubric[k] || 0);

  new Chart(ctx, {
    type: 'radar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Your Performance',
        data: values,
        backgroundColor: 'rgba(0, 242, 254, 0.12)',
        borderColor: 'rgba(0, 242, 254, 0.8)',
        pointBackgroundColor: 'rgba(0, 242, 254, 1)',
        pointBorderColor: 'rgba(0, 242, 254, 0.3)',
        pointRadius: 4,
        borderWidth: 2,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      scales: {
        r: {
          angleLines: { color: 'rgba(255, 255, 255, 0.06)' },
          grid: { color: 'rgba(255, 255, 255, 0.06)' },
          pointLabels: {
            color: '#94a3b8',
            font: { size: 10, family: 'Inter' }
          },
          ticks: { display: false },
          suggestedMin: 0,
          suggestedMax: 100
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

function renderBarChart(scenarioScores) {
  const ctx = document.getElementById('barChart');
  if (!ctx) return;

  const colors = scenarioScores.map(s =>
    s.score >= 81 ? 'rgba(16, 185, 129, 0.7)' :
    s.score >= 61 ? 'rgba(79, 172, 254, 0.7)' :
    s.score >= 41 ? 'rgba(245, 158, 11, 0.7)' :
    'rgba(244, 63, 94, 0.7)'
  );

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: scenarioScores.map(s => s.label),
      datasets: [{
        label: 'Score',
        data: scenarioScores.map(s => s.score),
        backgroundColor: colors,
        borderColor: colors.map(c => c.replace('0.7', '1')),
        borderWidth: 1,
        borderRadius: 6,
        borderSkipped: false
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      scales: {
        x: {
          grid: { color: 'rgba(255, 255, 255, 0.04)' },
          ticks: { color: '#94a3b8', font: { family: 'Inter', size: 11 } }
        },
        y: {
          grid: { color: 'rgba(255, 255, 255, 0.04)' },
          ticks: { color: '#64748b', font: { family: 'Inter', size: 11 } },
          min: 0,
          max: 100
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

function downloadReport() {
  const element = document.getElementById('pdf-report-area');
  if (!element) return;

  showToast('Generating PDF...', 'info');

  const opt = {
    margin: [0.5, 0.5, 0.5, 0.5],
    filename: `Placifly_Report_${state.selectedCompany}_${new Date().toISOString().slice(0,10)}.pdf`,
    image: { type: 'jpeg', quality: 0.95 },
    html2canvas: { scale: 2, useCORS: true, backgroundColor: '#0f172a' },
    jsPDF: { unit: 'in', format: 'a4', orientation: 'portrait' }
  };

  html2pdf().set(opt).from(element).save().then(() => {
    showToast('PDF downloaded successfully!', 'success');
  });
}

function shareAchievement() {
  const score = Math.round(state.evaluations.reduce((s, e) => s + (e.overall_score || 0), 0) / (state.evaluations.length || 1));
  const text = `🎯 I just scored ${score}/100 on Placifly's ${state.selectedCompany} Case Study Simulator! Practicing for placement interviews with AI-powered evaluation. #Placifly #PlacementPrep #CaseStudy`;

  navigator.clipboard.writeText(text).then(() => {
    showToast('Result copied to clipboard! Share it on social media.', 'success');
  }).catch(() => {
    showToast('Could not copy to clipboard.', 'error');
  });
}
