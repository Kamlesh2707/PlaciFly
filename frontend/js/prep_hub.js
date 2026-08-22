/* ================================================
   COMPANY PREP HUB MODULE — Past Questions & Intel
   ================================================ */

const PREP_PRESET_COMPANIES = ["TCS", "Deloitte", "Amazon", "Accenture", "Infosys", "Google", "Microsoft", "Capgemini", "IBM", "Wipro"];
let currentActivePrepCompany = "TCS";

function initPrepHub() {
  renderPrepCompanyPills();
  loadCompanyPrepData("TCS");
}

function renderPrepCompanyPills() {
  const container = document.getElementById('prep-company-pills');
  if (!container) return;

  container.innerHTML = PREP_PRESET_COMPANIES.map(name => `
    <button class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all border ${name === currentActivePrepCompany ? 'bg-cyan-500/15 text-cyan-400 border-cyan-500/30' : 'bg-slate-800/60 text-slate-300 border-slate-700/50 hover:bg-slate-700'}"
            onclick="loadCompanyPrepData('${name}', this)">
      ${name}
    </button>
  `).join('');
}

async function loadCompanyPrepData(companyName, pillEl = null) {
  currentActivePrepCompany = companyName;

  if (pillEl) {
    document.querySelectorAll('#prep-company-pills button').forEach(b => {
      b.className = 'px-3 py-1.5 rounded-lg text-xs font-bold transition-all border bg-slate-800/60 text-slate-300 border-slate-700/50 hover:bg-slate-700';
    });
    pillEl.className = 'px-3 py-1.5 rounded-lg text-xs font-bold transition-all border bg-cyan-500/15 text-cyan-400 border-cyan-500/30';
  }

  showLoading(`Loading interview trends & insights for ${companyName}...`);

  try {
    const res = await fetch(`/api/company-prep/${encodeURIComponent(companyName)}`);
    const data = await res.json();
    hideLoading();
    renderPrepContent(data.prep);
  } catch (err) {
    hideLoading();
    console.error('Failed to load company prep:', err);
    showToast('Failed to load company insights.', 'error');
  }
}

async function triggerCompanyIntelRefresh() {
  showLoading(`Refreshing 2026 hiring trends & tech stack intel for ${currentActivePrepCompany}...`);

  try {
    const res = await fetch('/api/company-intel/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ company_name: currentActivePrepCompany })
    });

    if (!res.ok) throw new Error(`API error: ${res.status}`);
    const data = await res.json();
    hideLoading();

    showToast(`Hiring trends & intel refreshed for ${currentActivePrepCompany}!`, 'success');
    loadCompanyPrepData(currentActivePrepCompany);

  } catch (err) {
    hideLoading();
    console.error('Refresh intel error:', err);
    showToast('Failed to refresh company intel.', 'error');
  }
}

function loadCustomCompanyPrep() {
  const val = document.getElementById('prep-custom-input').value.trim();
  if (!val) {
    showToast('Please enter a company name.', 'warning');
    return;
  }
  loadCompanyPrepData(val);
}

function renderPrepContent(prep) {
  const container = document.getElementById('prep-hub-content');
  if (!container) return;

  const roundsHtml = (prep.placement_rounds || []).map(r => `
    <div class="glass-card p-5 border-l-4 mb-4" style="border-left-color: ${prep.color || '#00f2fe'};">
      <div class="flex flex-wrap justify-between items-center mb-2 gap-2">
        <h4 class="font-bold text-base text-white flex items-center gap-2">
          <span class="w-6 h-6 rounded-full bg-cyan-500/20 text-cyan-400 text-xs flex items-center justify-center font-black">${r.round_num}</span>
          ${r.name}
        </h4>
        <span class="text-xs px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700">⏱ ${r.duration}</span>
      </div>
      <p class="text-xs text-slate-300 leading-relaxed mb-3">${r.description}</p>
      <div class="bg-slate-900/60 p-3 rounded-lg border border-slate-800/80 mb-2">
        <div class="text-xs font-bold text-cyan-400 mb-1">Key Focus Topics:</div>
        <div class="text-xs text-slate-300 font-medium">${r.focus}</div>
      </div>
      <div class="text-xs text-amber-300/90 italic flex items-center gap-1">
        <span>💡 Tip:</span> ${r.tips}
      </div>
    </div>
  `).join('');

  const questionsHtml = (prep.past_questions || []).map(q => `
    <div class="p-4 rounded-xl bg-slate-800/30 border border-slate-700/50 mb-3">
      <div class="flex justify-between items-start mb-2 gap-2">
        <span class="text-xs font-bold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">${q.category}</span>
        <span class="text-xs text-slate-500 font-mono">${q.year}</span>
      </div>
      <p class="text-sm font-medium text-slate-200 leading-relaxed">"${q.question}"</p>
    </div>
  `).join('');

  const techPills = (prep.tech_stack_focus || []).map(t =>
    `<span class="px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-xs font-semibold">${t}</span>`
  ).join('');

  const criteriaPills = (prep.selection_criteria || []).map(c =>
    `<span class="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-semibold">✓ ${c}</span>`
  ).join('');

  container.innerHTML = `
    <div id="pdf-company-guide">
      <div class="glass-card p-6 sm:p-8 mb-8 border-t-4" style="border-top-color: ${prep.color || '#00f2fe'};">
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4">
          <div>
            <div class="flex items-center gap-3 mb-2">
              <div class="w-12 h-12 rounded-xl flex items-center justify-center font-black text-xl text-white shadow-lg" style="background: ${prep.color || '#00f2fe'};">
                ${prep.logo_text || 'COMP'}
              </div>
              <div>
                <h2 class="text-2xl sm:text-3xl font-extrabold text-white">${prep.company}</h2>
                <p class="text-xs text-slate-400">${prep.tagline || 'Placement Prep & Hiring Intelligence'}</p>
              </div>
            </div>
          </div>
          <button class="btn-primary py-2.5 px-5 text-xs flex items-center gap-2" onclick="downloadCompanyPrepPDF('${prep.company}')">
            <span>📄</span> Download Study Guide PDF
          </button>
        </div>

        <p class="text-sm text-slate-300 leading-relaxed mb-6">${prep.overview}</p>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-white/5">
          <div>
            <div class="text-xs font-bold text-slate-400 mb-2 uppercase tracking-wider">Tech Stack Focus</div>
            <div class="flex flex-wrap gap-2">${techPills}</div>
          </div>
          <div>
            <div class="text-xs font-bold text-slate-400 mb-2 uppercase tracking-wider">Key Selection Criteria</div>
            <div class="flex flex-wrap gap-2">${criteriaPills}</div>
          </div>
        </div>
      </div>

      <div class="mb-10">
        <h3 class="text-xl font-extrabold mb-4 flex items-center gap-2">
          <span>🎯</span> Placement Rounds Breakdown
        </h3>
        ${roundsHtml}
      </div>

      <div class="mb-8">
        <h3 class="text-xl font-extrabold mb-4 flex items-center gap-2">
          <span>❓</span> Real Past Interview Questions
        </h3>
        ${questionsHtml}
      </div>
    </div>
  `;
}

function downloadCompanyPrepPDF(companyName) {
  const element = document.getElementById('pdf-company-guide');
  if (!element) return;

  showToast('Generating Study Guide PDF...', 'info');

  const opt = {
    margin: [0.5, 0.5, 0.5, 0.5],
    filename: `Placifly_${companyName.replace(/\s+/g, '_')}_Interview_Guide.pdf`,
    image: { type: 'jpeg', quality: 0.95 },
    html2canvas: { scale: 2, useCORS: true, backgroundColor: '#0f172a' },
    jsPDF: { unit: 'in', format: 'a4', orientation: 'portrait' }
  };

  html2pdf().set(opt).from(element).save().then(() => {
    showToast('Interview Guide PDF downloaded!', 'success');
  });
}
