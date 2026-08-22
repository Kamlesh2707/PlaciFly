/* ================================================
   FEEDBACK MODULE — AI Evaluation Result Renderer
   ================================================ */

const RUBRIC_LABELS = {
  communication: 'Communication',
  technical_understanding: 'Technical Understanding',
  logical_thinking: 'Logical Thinking',
  decision_making: 'Decision Making',
  professionalism: 'Professionalism',
  confidence: 'Confidence',
  leadership: 'Leadership',
  problem_solving: 'Problem Solving',
  creativity: 'Creativity',
  time_management: 'Time Management'
};

function getScoreColor(score) {
  if (score >= 81) return 'var(--emerald)';
  if (score >= 61) return 'var(--blue)';
  if (score >= 41) return 'var(--amber)';
  return 'var(--rose)';
}

function getScoreLabel(score) {
  if (score >= 81) return 'Excellent';
  if (score >= 61) return 'Good';
  if (score >= 41) return 'Average';
  return 'Needs Improvement';
}

function getBarColorClass(score) {
  if (score >= 81) return 'from-emerald-400 to-emerald-500';
  if (score >= 61) return 'from-blue-400 to-blue-500';
  if (score >= 41) return 'from-amber-400 to-amber-500';
  return 'from-rose-400 to-rose-500';
}

function renderFeedback(evaluation, scenarioIndex, totalScenarios) {
  const area = document.getElementById('feedback-area');
  area.classList.remove('hidden');
  area.scrollIntoView({ behavior: 'smooth', block: 'start' });

  const score = evaluation.overall_score;
  const scoreColor = getScoreColor(score);
  const scoreLabel = getScoreLabel(score);
  const rubric = evaluation.rubric_scores || {};

  // Build rubric bars HTML
  const rubricHtml = Object.entries(RUBRIC_LABELS).map(([key, label]) => {
    const val = Math.min(100, Math.max(0, rubric[key] || 0));
    const colorClass = getBarColorClass(val);
    return `
      <div class="mb-4">
        <div class="flex justify-between text-sm mb-1.5">
          <span class="text-slate-300 font-medium">${label}</span>
          <span class="font-bold tabular-nums" style="color: ${getScoreColor(val)}">${val}</span>
        </div>
        <div class="skill-bar">
          <div class="skill-bar-fill bg-gradient-to-r ${colorClass}" style="width: 0%;" data-target-width="${val}%"></div>
        </div>
      </div>
    `;
  }).join('');

  // Build feedback sections
  const goodPointsHtml = (evaluation.good_points || []).map(p =>
    `<li class="flex items-start gap-2"><span class="text-emerald-400 mt-0.5 flex-shrink-0">✓</span><span>${p}</span></li>`
  ).join('');

  const improveHtml = (evaluation.areas_to_improve || []).map(p =>
    `<li class="flex items-start gap-2"><span class="text-amber-400 mt-0.5 flex-shrink-0">→</span><span>${p}</span></li>`
  ).join('');

  const isLast = scenarioIndex >= totalScenarios - 1;
  const nextBtnHtml = isLast
    ? `<button class="btn-primary text-base px-8 py-3" onclick="completeAssessment()">📊 View Final Report</button>`
    : `<button class="btn-primary text-base px-8 py-3" onclick="nextScenario()">Next Scenario ➡️</button>`;

  area.innerHTML = `
    <div class="glass-card p-6 sm:p-8" style="animation: stepFadeIn 0.5s ease forwards;">

      <!-- Header -->
      <h2 class="text-2xl font-extrabold mb-8 text-center">
        <span class="text-gradient">AI Evaluation</span> Results
      </h2>

      <!-- Score + Rubric Row -->
      <div class="flex flex-col lg:flex-row gap-8 items-center lg:items-start mb-8">

        <!-- Score Gauge -->
        <div class="flex flex-col items-center flex-shrink-0">
          <div class="score-gauge mb-3" id="fb-score-gauge" style="background: conic-gradient(${scoreColor} 0%, rgba(255,255,255,0.06) 0%);">
            <span class="score-value" id="fb-score-val">0</span>
          </div>
          <div class="text-lg font-bold" style="color: ${scoreColor}">${scoreLabel}</div>
          <div class="text-xs text-slate-500 mt-1">Overall Score</div>
        </div>

        <!-- Rubric Bars -->
        <div class="flex-1 w-full">
          <h3 class="font-bold text-sm uppercase tracking-wider text-slate-400 mb-4 pb-2 border-b border-white/5">Skill Breakdown</h3>
          ${rubricHtml}
        </div>
      </div>

      <!-- Feedback Cards Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <!-- Good Points -->
        <div class="rounded-xl p-5 border border-emerald-500/20" style="background: rgba(16,185,129,0.05);">
          <h3 class="font-bold text-emerald-400 mb-3 flex items-center gap-2 text-sm uppercase tracking-wider">
            <span>✅</span> What You Did Well
          </h3>
          <ul class="space-y-2 text-sm text-slate-300">${goodPointsHtml}</ul>
        </div>

        <!-- Areas to Improve -->
        <div class="rounded-xl p-5 border border-amber-500/20" style="background: rgba(245,158,11,0.05);">
          <h3 class="font-bold text-amber-400 mb-3 flex items-center gap-2 text-sm uppercase tracking-wider">
            <span>🔧</span> Areas to Improve
          </h3>
          <ul class="space-y-2 text-sm text-slate-300">${improveHtml}</ul>
        </div>
      </div>

      <!-- Accordion Sections -->
      <div class="space-y-3 mb-8">
        ${buildAccordion('💡', 'Better Answer Example', `<p class="text-slate-300 leading-relaxed">${evaluation.better_answer_example || 'N/A'}</p>`)}
        ${buildAccordion('🏢', 'Industry Best Practice', `<p class="text-slate-300 leading-relaxed">${evaluation.industry_best_practice || 'N/A'}</p>`)}
        ${buildAccordion('👔', 'HR Expectation', `<p class="text-slate-300 leading-relaxed">${evaluation.hr_expectation || 'N/A'}</p>`)}
        ${buildAccordion('🎯', 'Company Expectation', `<p class="text-slate-300 leading-relaxed">${evaluation.company_expectation || 'N/A'}</p>`)}
      </div>

      <!-- Navigation -->
      <div class="flex justify-between items-center pt-4 border-t border-white/5">
        <div class="text-sm text-slate-400">Scenario ${scenarioIndex + 1} of ${totalScenarios}</div>
        ${nextBtnHtml}
      </div>
    </div>
  `;

  // Animate score gauge & bars
  setTimeout(() => animateFeedback(score, scoreColor), 150);
}

function buildAccordion(icon, title, contentHtml) {
  const id = 'acc-' + title.replace(/\s+/g, '-').toLowerCase();
  return `
    <div class="rounded-xl overflow-hidden border border-white/5" style="background: rgba(255,255,255,0.02);">
      <div class="accordion-header flex items-center justify-between px-5 py-4" onclick="toggleAccordion('${id}')">
        <span class="font-semibold flex items-center gap-2"><span>${icon}</span> ${title}</span>
        <span class="accordion-arrow text-slate-400" id="${id}-arrow">▼</span>
      </div>
      <div class="accordion-content px-5 pb-0" id="${id}">
        <div class="pb-5">${contentHtml}</div>
      </div>
    </div>
  `;
}

function toggleAccordion(id) {
  const el = document.getElementById(id);
  const arrow = document.getElementById(id + '-arrow');
  if (!el) return;
  el.classList.toggle('open');
  if (arrow) arrow.classList.toggle('open');
}

function animateFeedback(targetScore, color) {
  // Animate score counter
  const scoreEl = document.getElementById('fb-score-val');
  const gaugeEl = document.getElementById('fb-score-gauge');
  if (scoreEl && gaugeEl) {
    let current = 0;
    const step = Math.ceil(targetScore / 40);
    const interval = setInterval(() => {
      current = Math.min(current + step, targetScore);
      scoreEl.textContent = current;
      gaugeEl.style.background = `conic-gradient(${color} ${current * 3.6}deg, rgba(255,255,255,0.06) 0deg)`;
      if (current >= targetScore) clearInterval(interval);
    }, 25);
  }

  // Animate skill bars
  document.querySelectorAll('[data-target-width]').forEach((bar, i) => {
    setTimeout(() => {
      bar.style.width = bar.getAttribute('data-target-width');
    }, 100 + i * 60);
  });
}
