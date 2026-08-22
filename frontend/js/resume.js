/* ================================================
   RESUME ANALYZER MODULE — AI ATS & Interview Prep
   ================================================ */

async function handleResumeAnalyze(e) {
  if (e) e.preventDefault();

  const resumeText = document.getElementById('resume-text-input').value.trim();
  const targetCompany = document.getElementById('resume-company-select').value;
  const targetRole = document.getElementById('resume-role-select').value;

  if (!resumeText) {
    showToast('Please paste your resume text or project details for analysis.', 'warning');
    return;
  }

  showLoading(`Analyzing your resume against ${targetCompany} (${targetRole}) ATS expectations...`);

  try {
    const res = await fetch('/api/resume/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        resume_text: resumeText,
        target_company: targetCompany,
        target_role: targetRole
      })
    });

    if (!res.ok) throw new Error(`API error: ${res.status}`);
    const data = await res.json();
    hideLoading();

    renderResumeAnalysisReport(data.analysis, targetCompany, targetRole);

  } catch (err) {
    hideLoading();
    console.error('Resume analysis error:', err);
    showToast('Failed to analyze resume. Ensure backend server is running.', 'error');
  }
}

function renderResumeAnalysisReport(analysis, targetCompany, targetRole) {
  const container = document.getElementById('resume-analysis-results');
  if (!container) return;

  container.classList.remove('hidden');
  container.scrollIntoView({ behavior: 'smooth', block: 'start' });

  const score = analysis.match_score || 0;
  const scoreColor = score >= 80 ? 'var(--emerald)' : score >= 60 ? 'var(--cyan)' : 'var(--amber)';

  // Missing Keywords Pills
  const missingPills = (analysis.missing_keywords || []).map(kw =>
    `<span class="px-3 py-1 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20 text-xs font-bold">+ ${kw}</span>`
  ).join('');

  // Strengths List
  const strengthsHtml = (analysis.key_strengths || []).map(s =>
    `<li class="flex items-start gap-2 text-sm text-slate-300"><span class="text-emerald-400 font-bold mt-0.5">✓</span><span>${s}</span></li>`
  ).join('');

  // Formatting Tips List
  const tipsHtml = (analysis.formatting_tips || []).map(t =>
    `<li class="flex items-start gap-2 text-sm text-slate-300"><span class="text-cyan-400 font-bold mt-0.5">💡</span><span>${t}</span></li>`
  ).join('');

  // Bullet Point Improvements
  const bulletsHtml = (analysis.bullet_point_improvements || []).map(b => `
    <div class="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2 mb-3">
      <div class="text-xs font-bold text-rose-400 flex items-center gap-1.5">
        <span>❌ Current Bullet:</span> <span class="font-normal text-slate-300 text-xs">"${b.current}"</span>
      </div>
      <div class="text-xs font-bold text-emerald-400 flex items-start gap-1.5">
        <span class="flex-shrink-0">✨ AI Recommended Bullet:</span> <span class="font-medium text-emerald-200 text-xs">"${b.recommended}"</span>
      </div>
    </div>
  `).join('');

  // Expected Interview Questions Based on Resume
  const questionsHtml = (analysis.expected_interview_questions || []).map((q, idx) => `
    <div class="p-4 rounded-xl bg-indigo-950/20 border border-indigo-500/20 mb-3 flex items-start gap-3">
      <span class="w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5">${idx + 1}</span>
      <p class="text-sm font-medium text-slate-200 leading-relaxed">"${q}"</p>
    </div>
  `).join('');

  container.innerHTML = `
    <div id="pdf-resume-report" class="glass-card p-6 sm:p-8" style="animation: stepFadeIn 0.4s ease forwards;">

      <!-- Header -->
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8 pb-6 border-b border-white/5">
        <div>
          <span class="px-3 py-1 rounded-full text-xs font-bold bg-cyan-500/15 text-cyan-400 border border-cyan-500/25 mb-2 inline-block">AI ATS RESUME AUDIT</span>
          <h2 class="text-2xl sm:text-3xl font-extrabold text-white">Target Match Report: <span class="text-gradient">${targetCompany}</span></h2>
          <p class="text-xs text-slate-400">Target Role: ${targetRole} • Status: <span class="font-bold text-cyan-300">${analysis.ats_verdict || 'Match Analyzed'}</span></p>
        </div>
        <button class="btn-primary py-2.5 px-5 text-xs flex items-center gap-2" onclick="downloadResumeReportPDF('${targetCompany}')">
          <span>📄</span> Download Resume Audit PDF
        </button>
      </div>

      <!-- Top Score & Key Findings Grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <!-- Score Gauge Card -->
        <div class="glass-card p-6 flex flex-col items-center justify-center text-center bg-slate-900/40">
          <div class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">ATS Match Score</div>
          <div class="score-gauge mb-3" style="background: conic-gradient(${scoreColor} ${score * 3.6}deg, rgba(255,255,255,0.06) 0deg);">
            <span class="score-value" style="color: ${scoreColor}">${score}</span>
          </div>
          <div class="text-sm font-bold text-white">${analysis.ats_verdict}</div>
          <div class="text-xs text-slate-500 mt-1">Based on ${targetCompany} ATS Filters</div>
        </div>

        <!-- Strengths Card -->
        <div class="glass-card p-6 md:col-span-2 bg-slate-900/40">
          <h3 class="font-bold text-sm uppercase tracking-wider text-emerald-400 mb-3 flex items-center gap-2">
            <span>💪</span> Resume Key Strengths
          </h3>
          <ul class="space-y-2 mb-4">${strengthsHtml}</ul>
        </div>
      </div>

      <!-- Missing Keywords Section -->
      <div class="glass-card p-6 mb-8 border-rose-500/20 bg-rose-950/10">
        <h3 class="font-bold text-sm uppercase tracking-wider text-rose-400 mb-2 flex items-center gap-2">
          <span>🎯</span> Missing ATS Technical Keywords for ${targetCompany}
        </h3>
        <p class="text-xs text-slate-400 mb-4">Adding these keywords into your skills and project descriptions increases your ATS resume shortlisting rate:</p>
        <div class="flex flex-wrap gap-2">${missingPills}</div>
      </div>

      <!-- Expected Interview Questions Based on Resume -->
      <div class="glass-card p-6 mb-8 border-indigo-500/20 bg-indigo-950/10">
        <h3 class="font-bold text-sm uppercase tracking-wider text-indigo-400 mb-2 flex items-center gap-2">
          <span>❓</span> Questions Interviewers Will Ask Based on Your Resume
        </h3>
        <p class="text-xs text-slate-400 mb-4">Based on your listed projects & tech stack, the ${targetCompany} panel will likely ask:</p>
        <div>${questionsHtml}</div>
      </div>

      <!-- High-Impact Bullet Point Rewrites -->
      <div class="glass-card p-6 mb-8">
        <h3 class="font-bold text-sm uppercase tracking-wider text-amber-400 mb-2 flex items-center gap-2">
          <span>✏️</span> High-Impact Bullet Point Recommendations
        </h3>
        <p class="text-xs text-slate-400 mb-4">Replace weak bullet points with action-oriented, quantifiable descriptions:</p>
        <div>${bulletsHtml}</div>
      </div>

      <!-- Formatting & Action Plan -->
      <div class="glass-card p-6">
        <h3 class="font-bold text-sm uppercase tracking-wider text-cyan-400 mb-3 flex items-center gap-2">
          <span>📋</span> Executive Formatting & Action Plan
        </h3>
        <ul class="space-y-2.5">${tipsHtml}</ul>
      </div>

    </div>
  `;
}

function downloadResumeReportPDF(companyName) {
  const element = document.getElementById('pdf-resume-report');
  if (!element) return;

  showToast('Generating Resume Audit PDF...', 'info');

  const opt = {
    margin: [0.5, 0.5, 0.5, 0.5],
    filename: `Placifly_Resume_Audit_${companyName}_${new Date().toISOString().slice(0,10)}.pdf`,
    image: { type: 'jpeg', quality: 0.95 },
    html2canvas: { scale: 2, useCORS: true, backgroundColor: '#0f172a' },
    jsPDF: { unit: 'in', format: 'a4', orientation: 'portrait' }
  };

  html2pdf().set(opt).from(element).save().then(() => {
    showToast('Resume Audit PDF downloaded!', 'success');
  });
}
