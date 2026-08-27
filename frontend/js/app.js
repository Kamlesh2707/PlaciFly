/* ==============================================================================
   PLACIFLY — MAIN APPLICATION CONTROLLER
   - Airplane Opening Canvas Animation
   - 26+ Companies Directory & Instant Search
   - Custom Company URL Analyzer Engine
   - Candidate Performance Dashboard & Progress Tracking
   - Authentication (Login, Register with Email OTP, Password Reset)
   - Seamless 5-Round Interview Workstation Launch
   ============================================================================== */

const PlaciflyApp = {
  currentUser: null,
  authToken: null,
  companies: [],
  filteredCompanies: [],
  selectedCustomCompany: null,
  history: [],
  otpTargetEmail: '',
  otpTimer: null,
  otpCountdown: 30,
  devModalOTP: null
};

// Global state compatibility
window.state = {
  activeTab: 'home',
  selectedCompany: 'TCS',
  selectedDifficulty: 'Medium'
};

/* ==============================================================================
   1. INITIALIZATION & LIFECYCLE
   ============================================================================== */

document.addEventListener('DOMContentLoaded', async () => {
  initNavbarScroll();
  checkAuthSession();
  initIntroFlightAnimation();
  initHeroFlightCanvas();
  await loadCompanyDirectory();
  loadCandidatePerformance();

  // If user already visited intro this session, skip automatically
  if (sessionStorage.getItem('placifly_intro_seen')) {
    const splash = document.getElementById('intro-splash');
    if (splash) {
      splash.classList.add('fade-out');
      splash.style.display = 'none';
    }
  }
});

function initNavbarScroll() {
  window.addEventListener('scroll', () => {
    const nav = document.querySelector('.placifly-navbar');
    if (nav) {
      if (window.scrollY > 30) nav.classList.add('scrolled');
      else nav.classList.remove('scrolled');
    }
  });
}

/* ==============================================================================
   2. INTRO AIRPLANE FLIGHT ANIMATION
   ============================================================================== */

function initIntroFlightAnimation() {
  const canvas = document.getElementById('flight-intro-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let width = canvas.width = window.innerWidth;
  let height = canvas.height = window.innerHeight;

  window.addEventListener('resize', () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  });

  // Sparkle particles that appear along the flight path
  const particles = [];
  let progress = 0;
  const startTime = performance.now();
  const flightDuration = 2600; // ms, matches CSS animation

  // Flight path control points (matches CSS keyframes approximately)
  function getFlightPosition(t) {
    // Bezier curve from bottom-left to center
    const p0 = { x: -50, y: height * 0.75 };
    const p1 = { x: width * 0.3, y: height * 0.35 };
    const p2 = { x: width * 0.55, y: height * 0.3 };
    const p3 = { x: width * 0.5, y: height * 0.42 };

    const mt = 1 - t;
    return {
      x: mt*mt*mt*p0.x + 3*mt*mt*t*p1.x + 3*mt*t*t*p2.x + t*t*t*p3.x,
      y: mt*mt*mt*p0.y + 3*mt*mt*t*p1.y + 3*mt*t*t*p2.y + t*t*t*p3.y
    };
  }

  function spawnParticle(x, y) {
    for (let i = 0; i < 3; i++) {
      particles.push({
        x: x + (Math.random() - 0.5) * 20,
        y: y + (Math.random() - 0.5) * 20,
        vx: (Math.random() - 0.5) * 1.5,
        vy: (Math.random() - 0.5) * 1.5,
        alpha: 0.6 + Math.random() * 0.4,
        size: 1 + Math.random() * 3,
        hue: 190 + Math.random() * 30 // cyan range
      });
    }
  }

  function animateTrail() {
    ctx.clearRect(0, 0, width, height);
    const elapsed = performance.now() - startTime - 200; // 200ms delay like CSS
    progress = Math.max(0, Math.min(elapsed / flightDuration, 1));

    // Spawn particles along flight path
    if (progress > 0 && progress < 0.85) {
      const pos = getFlightPosition(progress);
      spawnParticle(pos.x, pos.y);

      // Draw glowing trail line
      ctx.beginPath();
      ctx.strokeStyle = 'rgba(0, 210, 255, 0.15)';
      ctx.lineWidth = 2;
      ctx.shadowColor = '#00D2FF';
      ctx.shadowBlur = 15;
      const steps = Math.floor(progress * 50);
      for (let i = 0; i <= steps; i++) {
        const t = i / 50;
        const p = getFlightPosition(t);
        if (i === 0) ctx.moveTo(p.x, p.y);
        else ctx.lineTo(p.x, p.y);
      }
      ctx.stroke();
      ctx.shadowBlur = 0;
    }

    // Update and draw particles
    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.alpha -= 0.008;
      p.size *= 0.995;

      if (p.alpha <= 0) {
        particles.splice(i, 1);
        continue;
      }

      ctx.beginPath();
      ctx.fillStyle = `hsla(${p.hue}, 100%, 70%, ${p.alpha})`;
      ctx.shadowColor = `hsla(${p.hue}, 100%, 70%, ${p.alpha * 0.5})`;
      ctx.shadowBlur = 8;
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.shadowBlur = 0;

    // Center glow burst when airplane arrives
    if (progress > 0.8 && progress < 1) {
      const burstProgress = (progress - 0.8) / 0.2;
      const burstRadius = burstProgress * 150;
      const burstAlpha = (1 - burstProgress) * 0.3;
      const cx = width * 0.5;
      const cy = height * 0.42;
      const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, burstRadius);
      grad.addColorStop(0, `rgba(0, 210, 255, ${burstAlpha})`);
      grad.addColorStop(0.5, `rgba(0, 102, 255, ${burstAlpha * 0.5})`);
      grad.addColorStop(1, 'transparent');
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(cx, cy, burstRadius, 0, Math.PI * 2);
      ctx.fill();
    }

    // Keep animating while particles exist or flight is active
    if (progress < 1 || particles.length > 0) {
      requestAnimationFrame(animateTrail);
    }
  }

  requestAnimationFrame(animateTrail);
}

function dismissIntroSplash(targetView = 'simulator') {
  const splash = document.getElementById('intro-splash');
  if (splash) {
    splash.classList.add('fade-out');
    splash.style.pointerEvents = 'none';
    sessionStorage.setItem('placifly_intro_seen', 'true');
    setTimeout(() => {
      splash.style.display = 'none';
    }, 600);
  }
  if (targetView) {
    switchPlaciflyView(targetView);
  }
}

/* ==============================================================================
   3. HERO BACKGROUND FLIGHT PATH NETWORK
   ============================================================================== */

function initHeroFlightCanvas() {
  const canvas = document.getElementById('hero-flight-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let width = canvas.width = canvas.offsetWidth;
  let height = canvas.height = canvas.offsetHeight;

  const points = [
    { x: width * 0.15, y: height * 0.35, r: 4 },
    { x: width * 0.38, y: height * 0.22, r: 5 },
    { x: width * 0.62, y: height * 0.48, r: 6 },
    { x: width * 0.85, y: height * 0.28, r: 4 },
    { x: width * 0.78, y: height * 0.72, r: 5 },
    { x: width * 0.32, y: height * 0.78, r: 4 }
  ];

  let pulseT = 0;

  function renderRoutes() {
    ctx.clearRect(0, 0, width, height);

    ctx.strokeStyle = 'rgba(0, 210, 255, 0.18)';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([4, 6]);

    for (let i = 0; i < points.length; i++) {
      const pA = points[i];
      const pB = points[(i + 1) % points.length];

      ctx.beginPath();
      ctx.moveTo(pA.x, pA.y);
      ctx.bezierCurveTo(
        (pA.x + pB.x) / 2, pA.y - 40,
        (pA.x + pB.x) / 2, pB.y - 40,
        pB.x, pB.y
      );
      ctx.stroke();
    }

    ctx.setLineDash([]);

    pulseT += 0.03;
    points.forEach((p, idx) => {
      const glow = Math.sin(pulseT + idx) * 3 + 6;
      ctx.shadowColor = '#00D2FF';
      ctx.shadowBlur = glow;

      ctx.fillStyle = '#00D2FF';
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fill();

      ctx.strokeStyle = 'rgba(0, 240, 255, 0.4)';
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r + 4, 0, Math.PI * 2);
      ctx.stroke();
    });

    requestAnimationFrame(renderRoutes);
  }

  requestAnimationFrame(renderRoutes);
}

/* ==============================================================================
   4. 26+ COMPANIES DIRECTORY & SEARCH
   ============================================================================== */

async function loadCompanyDirectory() {
  try {
    const res = await fetch('/api/companies');
    const data = await res.json();
    PlaciflyApp.companies = data.companies || [];
    PlaciflyApp.filteredCompanies = PlaciflyApp.companies;
    renderCompanyCards(PlaciflyApp.filteredCompanies);
  } catch (err) {
    console.error('Failed to load companies:', err);
  }
}

function renderCompanyCards(companies) {
  const grid = document.getElementById('company-cards-grid');
  if (!grid) return;

  if (companies.length === 0) {
    grid.innerHTML = `
      <div class="col-span-full text-center py-12">
        <div class="text-4xl mb-2">🏢</div>
        <h4 class="text-base font-bold text-white mb-1">Company Not Found</h4>
        <p class="text-xs text-slate-400">Use "+ Custom Company" to analyze any company website.</p>
      </div>
    `;
    return;
  }

  grid.innerHTML = companies.map((c, idx) => `
    <div class="placifly-card p-5 flex flex-col justify-between group" style="animation: elementFadeUp 0.3s ease forwards ${idx * 30}ms;">
      <div>
        <div class="flex items-center justify-between gap-3 mb-3">
          <div class="w-10 h-10 rounded-xl bg-slate-900 border border-cyan-500/30 flex items-center justify-center font-black text-sm text-cyan-300" style="border-color: ${c.color}66; color: ${c.color};">
            ${c.name.slice(0, 2).toUpperCase()}
          </div>
          <span class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-900 text-slate-400 border border-slate-800">
            ${c.industry || 'Tech'}
          </span>
        </div>

        <h3 class="font-bold text-base text-white group-hover:text-cyan-300 transition-colors mb-1">
          ${c.name}
        </h3>

        <p class="text-xs text-cyan-400/90 font-medium mb-2">
          ${c.role || 'Software Engineer'}
        </p>

        <p class="text-xs text-slate-400 line-clamp-2 leading-relaxed mb-4">
          ${c.desc || 'Comprehensive 5-round company interview simulation.'}
        </p>
      </div>

      <button class="btn-placifly-primary w-full py-2.5 text-xs justify-center" onclick="prepareForCompany('${c.name}')">
        <span>Prepare for Interview</span>
        <span class="btn-arrow">→</span>
      </button>
    </div>
  `).join('');
}

function handleCompanySearch(query) {
  const q = query.toLowerCase().trim();
  if (!q) {
    PlaciflyApp.filteredCompanies = PlaciflyApp.companies;
  } else {
    PlaciflyApp.filteredCompanies = PlaciflyApp.companies.filter(c => 
      c.name.toLowerCase().includes(q) ||
      (c.full_name && c.full_name.toLowerCase().includes(q)) ||
      (c.industry && c.industry.toLowerCase().includes(q))
    );
  }
  renderCompanyCards(PlaciflyApp.filteredCompanies);
}

function prepareForCompany(companyName) {
  state.selectedCompany = companyName;
  switchPlaciflyView('simulator');
}

/* ==============================================================================
   5. CUSTOM COMPANY URL ANALYZER
   ============================================================================== */

function openCustomCompanyModal() {
  const modal = document.getElementById('custom-company-modal');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    
    const step1 = document.getElementById('custom-step-1');
    const step2 = document.getElementById('custom-step-2');
    const step3 = document.getElementById('custom-step-3');
    if (step1) step1.classList.remove('hidden');
    if (step2) step2.classList.add('hidden');
    if (step3) step3.classList.add('hidden');
    
    const textInput = document.getElementById('custom-company-text-input');
    if (textInput) textInput.value = '';
    
    const resumeTextInput = document.getElementById('custom-resume-text-input');
    if (resumeTextInput) resumeTextInput.value = '';
    
    window.customResumeFile = null;
    const fileNameEl = document.getElementById('custom-resume-file-name');
    if (fileNameEl) {
      fileNameEl.textContent = '';
      fileNameEl.classList.add('hidden');
    }

    const ind1 = document.getElementById('custom-step-indicator-1');
    const ind2 = document.getElementById('custom-step-indicator-2');
    const ind3 = document.getElementById('custom-step-indicator-3');
    if (ind1) { ind1.classList.add('active'); ind1.classList.remove('completed'); }
    if (ind2) { ind2.classList.remove('active', 'completed'); }
    if (ind3) { ind3.classList.remove('active', 'completed'); }
  }
}

function closeCustomCompanyModal() {
  const modal = document.getElementById('custom-company-modal');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
    const step1 = document.getElementById('custom-step-1');
    const step2 = document.getElementById('custom-step-2');
    const step3 = document.getElementById('custom-step-3');
    if (step1) step1.classList.remove('hidden');
    if (step2) step2.classList.add('hidden');
    if (step3) step3.classList.add('hidden');

    const ind1 = document.getElementById('custom-step-indicator-1');
    const ind2 = document.getElementById('custom-step-indicator-2');
    const ind3 = document.getElementById('custom-step-indicator-3');
    if (ind1) { ind1.classList.add('active'); ind1.classList.remove('completed'); }
    if (ind2) { ind2.classList.remove('active', 'completed'); }
    if (ind3) { ind3.classList.remove('active', 'completed'); }
  }
}

async function executeCompanyTextAnalysis() {
  const textInput = document.getElementById('custom-company-text-input');
  const inputText = textInput ? textInput.value.trim() : '';
  if (!inputText) {
    if (typeof showToast === 'function') showToast('Please enter company details', 'error');
    else alert('Please enter company details');
    return;
  }
  
  const loading = document.getElementById('custom-analysis-loading');
  const btn = document.getElementById('custom-analyze-btn');
  
  if (loading) loading.classList.remove('hidden');
  if (btn) btn.classList.add('hidden');
  
  try {
    const res = await fetch('/api/company/analyze-text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: inputText })
    });
    
    if (!res.ok) throw new Error('Analysis failed');
    const data = await res.json();
    
    window.customCompanyProfile = data.analysis;
    
    const card = document.getElementById('custom-company-profile-card');
    if (card) {
      card.innerHTML = `
        <div class="custom-profile-field">
          <div class="custom-profile-value text-2xl font-bold mb-2">${data.analysis.name || 'Company'}</div>
        </div>
        <div class="custom-profile-field mb-2">
          <span class="custom-profile-label text-slate-400 text-xs">Industry:</span>
          <span class="custom-profile-value ml-2 text-cyan-300">${data.analysis.industry || 'N/A'}</span>
        </div>
        <div class="custom-profile-field mb-3">
          <div class="custom-profile-label text-slate-400 text-xs mb-1">Description:</div>
          <div class="custom-profile-value text-sm text-slate-300">${data.analysis.description || ''}</div>
        </div>
        <div class="custom-profile-field mb-3">
          <div class="custom-profile-label text-slate-400 text-xs mb-1">Products & Services:</div>
          <div class="custom-profile-tags flex flex-wrap gap-2">
            ${(data.analysis.products_services || []).map(t => `<span class="custom-profile-tag px-2 py-1 bg-slate-800 rounded text-xs text-slate-300">${t}</span>`).join('')}
          </div>
        </div>
        <div class="custom-profile-field mb-3">
          <div class="custom-profile-label text-slate-400 text-xs mb-1">Technologies:</div>
          <div class="custom-profile-tags flex flex-wrap gap-2">
            ${(data.analysis.technologies || []).map(t => `<span class="custom-profile-tag px-2 py-1 bg-slate-800 rounded text-xs text-slate-300">${t}</span>`).join('')}
          </div>
        </div>
        <div class="custom-profile-field mb-3">
          <div class="custom-profile-label text-slate-400 text-xs mb-1">Culture & Values:</div>
          <div class="custom-profile-value text-sm text-slate-300">${data.analysis.culture_values || ''}</div>
        </div>
        ${data.analysis.required_skills && data.analysis.required_skills.length ? `
        <div class="custom-profile-field mb-3">
          <div class="custom-profile-label text-slate-400 text-xs mb-1">Required Skills:</div>
          <div class="custom-profile-tags flex flex-wrap gap-2">
            ${data.analysis.required_skills.map(t => `<span class="custom-profile-tag px-2 py-1 bg-cyan-900/50 text-cyan-300 border border-cyan-500/30 rounded text-xs">${t}</span>`).join('')}
          </div>
        </div>
        ` : ''}
        <div class="custom-profile-field">
          <div class="custom-profile-label text-slate-400 text-xs mb-1">Interview Prep Areas:</div>
          <ul class="custom-profile-value list-disc list-inside text-sm text-slate-300">
            ${(data.analysis.interview_prep_areas || []).map(p => `<li>${p}</li>`).join('')}
          </ul>
        </div>
      `;
    }
    
    const ind1 = document.getElementById('custom-step-indicator-1');
    const ind2 = document.getElementById('custom-step-indicator-2');
    if (ind1) { ind1.classList.remove('active'); ind1.classList.add('completed'); }
    if (ind2) { ind2.classList.add('active'); }
    
    document.getElementById('custom-step-1')?.classList.add('hidden');
    document.getElementById('custom-step-2')?.classList.remove('hidden');
    
  } catch (err) {
    if (typeof showToast === 'function') showToast('Analysis error. Please try again.', 'error');
    else alert('Analysis error');
  } finally {
    if (loading) loading.classList.add('hidden');
    if (btn) btn.classList.remove('hidden');
  }
}

function goToCustomStep3() {
  const ind2 = document.getElementById('custom-step-indicator-2');
  const ind3 = document.getElementById('custom-step-indicator-3');
  if (ind2) { ind2.classList.remove('active'); ind2.classList.add('completed'); }
  if (ind3) { ind3.classList.add('active'); }
  
  document.getElementById('custom-step-2')?.classList.add('hidden');
  document.getElementById('custom-step-3')?.classList.remove('hidden');
}

function handleCustomResumeFile(event) {
  const file = event.target.files[0];
  if (file) {
    window.customResumeFile = file;
    const nameEl = document.getElementById('custom-resume-file-name');
    if (nameEl) {
      nameEl.textContent = '📎 ' + file.name;
      nameEl.classList.remove('hidden');
    }
  }
}

async function startCustomCompanyInterview() {
  const textInput = document.getElementById('custom-resume-text-input');
  const resumeText = textInput ? textInput.value.trim() : '';
  const resumeFile = window.customResumeFile;
  
  if (!resumeFile && !resumeText) {
    if (typeof showToast === 'function') showToast('Please provide resume text or file', 'error');
    else alert('Please provide resume text or file');
    return;
  }
  
  const loading = document.getElementById('custom-resume-loading');
  const btn = document.getElementById('custom-start-interview-btn');
  
  if (loading) loading.classList.remove('hidden');
  if (btn) btn.classList.add('hidden');
  
  try {
    let res;
    if (resumeFile) {
      const formData = new FormData();
      formData.append('file', resumeFile);
      if (resumeText) formData.append('resume_text', resumeText);
      
      res = await fetch('/api/resume/parse-skills-enhanced', {
        method: 'POST',
        body: formData
      });
    } else {
      res = await fetch('/api/resume/parse-skills-enhanced', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume_text: resumeText })
      });
    }
    
    if (!res.ok) throw new Error('Failed to parse resume');
    
    const data = await res.json();
    window.customCandidateProfile = data.profile;
    window.customResumeSummary = data.summary;
    
    closeCustomCompanyModal();
    if (typeof launchStructuredInterview === 'function') {
      launchStructuredInterview('custom_company');
    }
  } catch (err) {
    console.error(err);
    if (typeof showToast === 'function') showToast('Error parsing resume', 'error');
  } finally {
    if (loading) loading.classList.add('hidden');
    if (btn) btn.classList.remove('hidden');
  }
}

async function executeCompanyUrlAnalysis() {
  const input = document.getElementById('custom-company-url-input');
  const btn = document.getElementById('btn-analyze-company');
  const resultBox = document.getElementById('custom-company-analysis-box');
  const url = input ? input.value.trim() : '';

  if (!url) {
    showToast('Please enter a company website URL or domain.', 'error');
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> ✈️ Analyzing Company with AI...';

  try {
    const res = await fetch('/api/company/analyze-url', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    const data = await res.json();

    if (data.analysis) {
      PlaciflyApp.selectedCustomCompany = data.analysis;

      document.getElementById('analyzed-comp-name').textContent = data.analysis.name;
      document.getElementById('analyzed-comp-industry').textContent = data.analysis.industry;
      document.getElementById('analyzed-comp-culture').textContent = data.analysis.culture;

      const prepBox = document.getElementById('analyzed-comp-prep-areas');
      prepBox.innerHTML = (data.analysis.prep_areas || []).map(p => `
        <span class="px-2 py-0.5 rounded-md bg-slate-900 border border-cyan-500/25 text-cyan-300">
          • ${p}
        </span>
      `).join('');

      resultBox.classList.remove('hidden');
      showToast(`Analyzed ${data.analysis.name}! Ready to launch custom interview.`, 'success');
    }
  } catch (err) {
    showToast('Analysis error. Please try again.', 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<span>Analyze Company & Start →</span>';
  }
}

function launchCustomCompanyInterview() {
  if (!PlaciflyApp.selectedCustomCompany) return;
  state.selectedCompany = PlaciflyApp.selectedCustomCompany.name;
  closeCustomCompanyModal();
  switchPlaciflyView('simulator');
}

/* ==============================================================================
   6. CANDIDATE PERFORMANCE DASHBOARD & CHART
   ============================================================================== */

function loadCandidatePerformance() {
  renderProgressChart();
}

function renderProgressChart() {
  const canvas = document.getElementById('progress-trend-chart');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  
  // Clean modern Chart.js setup matching Placifly Palette
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Interview 1', 'Interview 2', 'Interview 3', 'Interview 4'],
      datasets: [{
        label: 'Overall Performance Score',
        data: [54, 61, 68, 76],
        borderColor: '#00D2FF',
        backgroundColor: 'rgba(0, 210, 255, 0.12)',
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#00F0FF',
        pointBorderColor: '#030B1E',
        pointBorderWidth: 2,
        pointRadius: 5
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#0A1128',
          titleColor: '#00F0FF',
          bodyColor: '#FFFFFF',
          borderColor: 'rgba(0, 210, 255, 0.3)',
          borderWidth: 1
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { color: '#94A3B8', font: { size: 11 } }
        },
        y: {
          min: 40,
          max: 100,
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { color: '#94A3B8', font: { size: 11 } }
        }
      }
    }
  });
}

function startDailyChallenge(mode = 'rapid_fire') {
  if (window.DailyChallengeEngine && typeof window.DailyChallengeEngine.startChallenge === 'function') {
    window.DailyChallengeEngine.startChallenge(mode);
  } else {
    switchPlaciflyView('daily-challenge');
  }
}

/* ==============================================================================
   7. AUTHENTICATION & EMAIL OTP SYSTEM
   ============================================================================== */

function checkAuthSession() {
  const token = localStorage.getItem('placifly_token');
  const user = localStorage.getItem('placifly_user');

  if (token && user) {
    try {
      PlaciflyApp.authToken = token;
      PlaciflyApp.currentUser = JSON.parse(user);
      renderAuthNavbar(true);
    } catch (e) {
      renderAuthNavbar(false);
    }
  } else {
    renderAuthNavbar(false);
  }
}

function renderAuthNavbar(isAuth) {
  const guestBtns = document.getElementById('nav-guest-btns');
  const userBtns = document.getElementById('nav-user-btns');
  const userName = document.getElementById('nav-user-name');
  const avatarInit = document.getElementById('user-avatar-initial');

  if (isAuth && PlaciflyApp.currentUser) {
    if (guestBtns) guestBtns.classList.add('hidden');
    if (userBtns) userBtns.classList.remove('hidden');
    if (userName) userName.textContent = PlaciflyApp.currentUser.name || 'Candidate';
    if (avatarInit) avatarInit.textContent = (PlaciflyApp.currentUser.name || 'C').charAt(0).toUpperCase();
  } else {
    if (guestBtns) guestBtns.classList.remove('hidden');
    if (userBtns) userBtns.classList.add('hidden');
  }
}

function openAuthModal(tab = 'login') {
  const modal = document.getElementById('auth-modal');
  if (modal) modal.classList.remove('hidden');
  setAuthTab(tab);
}

function closeAuthModal() {
  const modal = document.getElementById('auth-modal');
  if (modal) modal.classList.add('hidden');
}

function setAuthTab(tab) {
  const pLogin = document.getElementById('panel-login');
  const pReg = document.getElementById('panel-register');
  const pVerify = document.getElementById('panel-verify');
  const pForgot = document.getElementById('panel-forgot');
  const tabLogin = document.getElementById('auth-tab-login');
  const tabReg = document.getElementById('auth-tab-register');
  const switchers = document.getElementById('auth-tab-switchers');

  [pLogin, pReg, pVerify, pForgot].forEach(p => p && p.classList.add('hidden'));

  if (tab === 'login') {
    if (pLogin) pLogin.classList.remove('hidden');
    if (switchers) switchers.classList.remove('hidden');
    if (tabLogin) tabLogin.className = 'flex-1 py-2 rounded-lg text-sm font-bold text-cyan-300 bg-cyan-500/20 transition-all';
    if (tabReg) tabReg.className = 'flex-1 py-2 rounded-lg text-sm font-bold text-slate-400 transition-all';
  } else if (tab === 'register') {
    if (pReg) pReg.classList.remove('hidden');
    if (switchers) switchers.classList.remove('hidden');
    if (tabReg) tabReg.className = 'flex-1 py-2 rounded-lg text-sm font-bold text-cyan-300 bg-cyan-500/20 transition-all';
    if (tabLogin) tabLogin.className = 'flex-1 py-2 rounded-lg text-sm font-bold text-slate-400 transition-all';
  } else if (tab === 'verify') {
    if (pVerify) pVerify.classList.remove('hidden');
    if (switchers) switchers.classList.add('hidden');
  } else if (tab === 'forgot') {
    if (pForgot) pForgot.classList.remove('hidden');
    if (switchers) switchers.classList.add('hidden');
  }
}

async function handleLoginSubmit() {
  const email = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;
  const errorEl = document.getElementById('login-error');
  const btn = document.getElementById('btn-login-submit');

  errorEl.classList.add('hidden');

  if (!email || !password) {
    errorEl.textContent = 'Please enter your email and password.';
    errorEl.classList.remove('hidden');
    return;
  }

  btn.disabled = true;
  btn.textContent = 'Logging in...';

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();

    if (data.success) {
      PlaciflyApp.authToken = data.token;
      PlaciflyApp.currentUser = data.user;
      localStorage.setItem('placifly_token', data.token);
      localStorage.setItem('placifly_user', JSON.stringify(data.user));
      localStorage.setItem('placifly_registered', 'true');

      renderAuthNavbar(true);
      closeAuthModal();
      showToast(`Welcome back, ${data.user.name}! 🚀`, 'success');
    } else {
      errorEl.textContent = data.message || 'Login failed.';
      errorEl.classList.remove('hidden');
    }
  } catch (err) {
    errorEl.textContent = 'Network error. Please try again.';
    errorEl.classList.remove('hidden');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Log In →';
  }
}

async function handleRegisterSubmit() {
  const name = document.getElementById('reg-name').value.trim();
  const email = document.getElementById('reg-email').value.trim();
  const password = document.getElementById('reg-password').value;
  const confirmPwd = document.getElementById('reg-password-confirm').value;
  const errorEl = document.getElementById('reg-error');
  const btn = document.getElementById('btn-reg-submit');

  errorEl.classList.add('hidden');

  if (!name || !email || !password) {
    errorEl.textContent = 'Please fill out all required fields.';
    errorEl.classList.remove('hidden');
    return;
  }

  if (password !== confirmPwd) {
    errorEl.textContent = 'Passwords do not match.';
    errorEl.classList.remove('hidden');
    return;
  }

  if (password.length < 6) {
    errorEl.textContent = 'Password must be at least 6 characters.';
    errorEl.classList.remove('hidden');
    return;
  }

  btn.disabled = true;
  btn.textContent = 'Sending Verification Code...';

  try {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password })
    });
    const data = await res.json();

    if (data.success) {
      PlaciflyApp.otpTargetEmail = email;
      document.getElementById('verify-email-target').textContent = email;

      if (data.dev_otp) {
        PlaciflyApp.devModalOTP = data.dev_otp;
        const banner = document.getElementById('modal-dev-otp-banner');
        const codeEl = document.getElementById('modal-dev-otp-code');
        if (banner && codeEl) {
          codeEl.textContent = data.dev_otp;
          banner.classList.remove('hidden');
        }
      }

      setAuthTab('verify');
      startModalResendTimer();
      document.querySelector('#modal-otp-inputs .otp-box[data-idx="0"]').focus();
      showToast('Verification code sent to your email!', 'success');
    } else {
      errorEl.textContent = data.message || 'Registration failed.';
      errorEl.classList.remove('hidden');
    }
  } catch (err) {
    errorEl.textContent = 'Network error. Please try again.';
    errorEl.classList.remove('hidden');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Continue & Verify Email →';
  }
}

function handleModalOTPInput(el, idx) {
  const val = el.value.replace(/\D/g, '');
  el.value = val;

  if (val && idx < 5) {
    const next = document.querySelector(`#modal-otp-inputs .otp-box[data-idx="${idx + 1}"]`);
    if (next) next.focus();
  }

  checkModalOTPComplete();
}

function handleModalOTPKeydown(e, idx) {
  if (e.key === 'Backspace' && !e.target.value && idx > 0) {
    const prev = document.querySelector(`#modal-otp-inputs .otp-box[data-idx="${idx - 1}"]`);
    if (prev) prev.focus();
  }
}

function getModalOTPValue() {
  let otp = '';
  document.querySelectorAll('#modal-otp-inputs .otp-box').forEach(el => { otp += el.value; });
  return otp;
}

function checkModalOTPComplete() {
  const otp = getModalOTPValue();
  const btn = document.getElementById('btn-verify-submit');
  if (btn) btn.disabled = otp.length < 6;
}

function autofillModalDevOTP() {
  if (!PlaciflyApp.devModalOTP) return;
  const digits = PlaciflyApp.devModalOTP.split('');
  document.querySelectorAll('#modal-otp-inputs .otp-box').forEach((el, idx) => {
    el.value = digits[idx] || '';
  });
  checkModalOTPComplete();
  showToast('Code auto-filled!', 'success');
}

async function handleVerifyOTPSubmit() {
  const otp = getModalOTPValue();
  const errorEl = document.getElementById('verify-error');
  const btn = document.getElementById('btn-verify-submit');

  if (otp.length !== 6) return;

  btn.disabled = true;
  btn.textContent = 'Verifying...';
  errorEl.classList.add('hidden');

  try {
    const res = await fetch('/api/auth/verify-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: PlaciflyApp.otpTargetEmail, otp })
    });
    const data = await res.json();

    if (data.success) {
      PlaciflyApp.authToken = data.token;
      PlaciflyApp.currentUser = data.user;
      localStorage.setItem('placifly_token', data.token);
      localStorage.setItem('placifly_user', JSON.stringify(data.user));
      localStorage.setItem('placifly_registered', 'true');

      renderAuthNavbar(true);
      closeAuthModal();
      showToast(`Account verified! Welcome to Placifly, ${data.user.name}! ✈️`, 'success');
    } else {
      errorEl.textContent = data.message || 'Invalid verification code.';
      errorEl.classList.remove('hidden');
      document.querySelectorAll('#modal-otp-inputs .otp-box').forEach(el => el.value = '');
      document.querySelector('#modal-otp-inputs .otp-box[data-idx="0"]').focus();
    }
  } catch (err) {
    errorEl.textContent = 'Network error. Please try again.';
    errorEl.classList.remove('hidden');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Verify & Enter Placifly';
    checkModalOTPComplete();
  }
}

function startModalResendTimer() {
  PlaciflyApp.otpCountdown = 30;
  const btn = document.getElementById('btn-resend-otp');
  const timerEl = document.getElementById('resend-countdown');
  if (btn) btn.disabled = true;

  if (PlaciflyApp.otpTimer) clearInterval(PlaciflyApp.otpTimer);
  PlaciflyApp.otpTimer = setInterval(() => {
    PlaciflyApp.otpCountdown--;
    if (timerEl) timerEl.textContent = PlaciflyApp.otpCountdown;
    if (PlaciflyApp.otpCountdown <= 0) {
      clearInterval(PlaciflyApp.otpTimer);
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = 'Resend Code';
      }
    }
  }, 1000);
}

async function handleResendOTP() {
  if (!PlaciflyApp.otpTargetEmail) return;
  try {
    const res = await fetch('/api/auth/send-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: PlaciflyApp.otpTargetEmail })
    });
    const data = await res.json();
    if (data.success || !data.error) {
      if (data.dev_otp) {
        PlaciflyApp.devModalOTP = data.dev_otp;
        const codeEl = document.getElementById('modal-dev-otp-code');
        if (codeEl) codeEl.textContent = data.dev_otp;
      }
      startModalResendTimer();
      showToast('New verification code sent!', 'success');
    }
  } catch (e) {
    showToast('Failed to resend code.', 'error');
  }
}

function handleLogout() {
  PlaciflyApp.authToken = null;
  PlaciflyApp.currentUser = null;
  localStorage.removeItem('placifly_token');
  localStorage.removeItem('placifly_user');
  renderAuthNavbar(false);
  showToast('Logged out successfully.', 'info');
}

/* ==============================================================================
   8. VIEW ROUTING
   ============================================================================== */

function startInterviewFlow() {
  switchPlaciflyView('simulator');
}

function switchPlaciflyView(viewName) {
  state.activeTab = viewName;

  document.querySelectorAll('.placifly-main-view').forEach(v => v.classList.add('hidden'));

  const navHome = document.getElementById('nav-btn-home');

  if (viewName === 'home') {
    const vHome = document.getElementById('view-home');
    if (vHome) vHome.classList.remove('hidden');
    if (navHome) navHome.classList.add('active');
  } else if (viewName === 'simulator') {
    const vSim = document.getElementById('view-simulator');
    if (vSim) vSim.classList.remove('hidden');
    if (navHome) navHome.classList.remove('active');

    // Launch Simulator Engine
    if (typeof startAdaptiveInterviewSession === 'function') {
      startAdaptiveInterviewSession();
    }
  } else if (viewName === 'daily-challenge') {
    const vDaily = document.getElementById('view-daily-challenge');
    if (vDaily) vDaily.classList.remove('hidden');
    if (navHome) navHome.classList.remove('active');
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function scrollToSection(sectionId) {
  const el = document.getElementById(sectionId);
  if (el) {
    switchPlaciflyView('home');
    setTimeout(() => {
      el.scrollIntoView({ behavior: 'smooth' });
    }, 50);
  }
}

/* ==============================================================================
   9. TOAST NOTIFICATIONS
   ============================================================================== */

function showToast(msg, type = 'info', duration = 3500) {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span>${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
    <span>${msg}</span>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// Global functions attached to window
window.switchPlaciflyView = switchPlaciflyView;
window.scrollToSection = scrollToSection;
window.startInterviewFlow = startInterviewFlow;
window.prepareForCompany = prepareForCompany;
window.handleCompanySearch = handleCompanySearch;
window.openCustomCompanyModal = openCustomCompanyModal;
window.closeCustomCompanyModal = closeCustomCompanyModal;
window.executeCompanyUrlAnalysis = executeCompanyUrlAnalysis;
window.launchCustomCompanyInterview = launchCustomCompanyInterview;
window.openAuthModal = openAuthModal;
window.closeAuthModal = closeAuthModal;
window.setAuthTab = setAuthTab;
window.handleLoginSubmit = handleLoginSubmit;
window.handleRegisterSubmit = handleRegisterSubmit;
window.handleVerifyOTPSubmit = handleVerifyOTPSubmit;
window.handleModalOTPInput = handleModalOTPInput;
window.handleModalOTPKeydown = handleModalOTPKeydown;
window.autofillModalDevOTP = autofillModalDevOTP;
window.handleResendOTP = handleResendOTP;
window.handleLogout = handleLogout;
window.dismissIntroSplash = dismissIntroSplash;
window.startDailyChallenge = startDailyChallenge;
window.showToast = showToast;
window.executeCompanyTextAnalysis = executeCompanyTextAnalysis;
window.goToCustomStep3 = goToCustomStep3;
window.handleCustomResumeFile = handleCustomResumeFile;
window.startCustomCompanyInterview = startCustomCompanyInterview;

document.addEventListener('DOMContentLoaded', () => {
  // Update daily streak badges on home view
  if (window.DailyChallengeEngine && typeof window.DailyChallengeEngine.getDailyStats === 'function') {
    const stats = window.DailyChallengeEngine.getDailyStats();
    document.querySelectorAll('.daily-streak-badge-val').forEach(el => {
      el.textContent = stats.dailyStreak || 1;
    });
  }

  const dropZone = document.getElementById('custom-resume-drop-zone');
  if (dropZone) {
      dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('drag-over'); });
      dropZone.addEventListener('dragleave', () => { dropZone.classList.remove('drag-over'); });
      dropZone.addEventListener('drop', (e) => {
          e.preventDefault();
          dropZone.classList.remove('drag-over');
          const file = e.dataTransfer.files[0];
          if (file && (file.name.endsWith('.pdf') || file.name.endsWith('.txt'))) {
              window.customResumeFile = file;
              document.getElementById('custom-resume-file-name').textContent = '📎 ' + file.name;
              document.getElementById('custom-resume-file-name').classList.remove('hidden');
          }
      });
  }
});
