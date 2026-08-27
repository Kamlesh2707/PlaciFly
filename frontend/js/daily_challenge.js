/* ==============================================================================
   PLACIFLY — DAILY INTERVIEW CHALLENGE ENGINE (30 QUESTIONS PER MODE)
   Modes: 
   1. Rapid Fire Challenge (30 questions, 30s each, 15s hint reveal)
   2. 30 MCQ Speed Sprint (30 questions, 30s each, auto-advance)
   3. Tech Logo Challenge (30 questions with Dynamic Speed Scaling:
      - Q1–14:  ⚡ NORMAL SPEED (30s, 15s hint)
      - Q15–20: 🔥 1.5X SPEED   (20s, 10s hint)
      - Q21–30: 🚀 2.5X SPEED   (12s, 6s hint)
   
   Features:
   - Dynamic Speed Indicator & "Difficulty Increased!" Visual Alert
   - Question 30: ⚡ DOUBLE POINTS – 2X SCORE
   - Final Results: Score out of 30, Accuracy, XP, Streaks, Badges
   - Web Audio SFX, Combos, Streaks, Confetti, Leaderboard, Share Result
   ============================================================================== */

const DailyChallengeEngine = (function () {
  // Web Audio Synthesizer (100% zero-latency offline sound system)
  const SoundFX = {
    audioCtx: null,
    isMuted: localStorage.getItem('placifly_sfx_muted') === 'true',

    init() {
      if (!this.audioCtx) {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) {
          this.audioCtx = new AudioContext();
        }
      }
      if (this.audioCtx && this.audioCtx.state === 'suspended') {
        this.audioCtx.resume();
      }
    },

    toggleMute() {
      this.isMuted = !this.isMuted;
      localStorage.setItem('placifly_sfx_muted', this.isMuted);
      this.updateMuteButtonUI();
      return this.isMuted;
    },

    updateMuteButtonUI() {
      const btn = document.getElementById('daily-sound-toggle-btn');
      if (btn) {
        btn.innerHTML = this.isMuted ? '🔇 Sound OFF' : '🔊 Sound ON';
        btn.classList.toggle('opacity-60', this.isMuted);
      }
    },

    playTone(freq, type = 'sine', duration = 0.15, gainVal = 0.12) {
      if (this.isMuted) return;
      try {
        this.init();
        if (!this.audioCtx) return;
        const osc = this.audioCtx.createOscillator();
        const gain = this.audioCtx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(freq, this.audioCtx.currentTime);
        gain.gain.setValueAtTime(gainVal, this.audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.0001, this.audioCtx.currentTime + duration);
        osc.connect(gain);
        gain.connect(this.audioCtx.destination);
        osc.start();
        osc.stop(this.audioCtx.currentTime + duration);
      } catch (e) {}
    },

    correct() {
      if (this.isMuted) return;
      this.init();
      setTimeout(() => this.playTone(523.25, 'triangle', 0.12, 0.15), 0);   // C5
      setTimeout(() => this.playTone(659.25, 'triangle', 0.12, 0.15), 75);  // E5
      setTimeout(() => this.playTone(783.99, 'triangle', 0.25, 0.20), 150); // G5
    },

    wrong() {
      if (this.isMuted) return;
      this.init();
      setTimeout(() => this.playTone(220, 'sawtooth', 0.15, 0.15), 0);
      setTimeout(() => this.playTone(180, 'sawtooth', 0.25, 0.18), 120);
    },

    doublePoints() {
      if (this.isMuted) return;
      this.init();
      setTimeout(() => this.playTone(440, 'triangle', 0.1, 0.2), 0);
      setTimeout(() => this.playTone(554.37, 'triangle', 0.1, 0.2), 80);
      setTimeout(() => this.playTone(659.25, 'triangle', 0.1, 0.2), 160);
      setTimeout(() => this.playTone(880, 'triangle', 0.35, 0.25), 240);
    },

    combo() {
      if (this.isMuted) return;
      this.init();
      setTimeout(() => this.playTone(880, 'sine', 0.08, 0.1), 0);
      setTimeout(() => this.playTone(1174.66, 'sine', 0.15, 0.15), 60);
    },

    tick() {
      if (this.isMuted) return;
      this.playTone(800, 'sine', 0.04, 0.04);
    },

    victory() {
      if (this.isMuted) return;
      this.init();
      const notes = [523.25, 659.25, 783.99, 1046.50];
      notes.forEach((freq, idx) => {
        setTimeout(() => this.playTone(freq, 'triangle', 0.25, 0.25), idx * 120);
      });
    }
  };

  // State
  let state = {
    mode: 'rapid_fire', // 'rapid_fire' | 'mcq_sprint' | 'logo_quiz'
    questions: [],
    currentIndex: 0,
    score: 0,
    correctCount: 0,
    wrongCount: 0,
    consecutiveStreak: 0,
    maxStreak: 0,
    comboMultiplier: 1.0,
    startTime: null,
    questionStartTime: null,
    totalTimeSpent: 0,
    questionTimes: [],
    isAnswered: false,
    
    // Per-question timer with dynamic speed scaling
    questionTotalTime: 30,
    questionTimeLeft: 30,
    questionTimerInterval: null,
    hintThreshold: 15,
    hintRevealed: false,
    feedbackShowing: false,

    // Speed tracking
    previousSpeedLevel: '1.0x'
  };

  // Streaks & Stats storage
  function getDailyStats() {
    try {
      const stats = JSON.parse(localStorage.getItem('placifly_daily_challenge_stats') || '{}');
      return {
        dailyStreak: stats.dailyStreak || 0,
        lastPlayedDate: stats.lastPlayedDate || null,
        bestScores: stats.bestScores || { rapid_fire: 0, mcq_sprint: 0, logo_quiz: 0 },
        totalXP: stats.totalXP || 0,
        totalCompleted: stats.totalCompleted || 0
      };
    } catch (e) {
      return { dailyStreak: 0, lastPlayedDate: null, bestScores: { rapid_fire: 0, mcq_sprint: 0, logo_quiz: 0 }, totalXP: 0, totalCompleted: 0 };
    }
  }

  function saveDailyStats(stats) {
    try {
      localStorage.setItem('placifly_daily_challenge_stats', JSON.stringify(stats));
    } catch (e) {}
  }

  function updateDailyStreak() {
    const stats = getDailyStats();
    const today = new Date().toISOString().split('T')[0];
    
    if (stats.lastPlayedDate !== today) {
      const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];
      if (stats.lastPlayedDate === yesterday) {
        stats.dailyStreak += 1;
      } else if (!stats.lastPlayedDate) {
        stats.dailyStreak = 1;
      } else {
        stats.dailyStreak = 1;
      }
      stats.lastPlayedDate = today;
      stats.totalCompleted += 1;
      saveDailyStats(stats);
    }
    
    const streakBadges = document.querySelectorAll('.daily-streak-badge-val');
    streakBadges.forEach(el => { el.textContent = stats.dailyStreak; });
    return stats.dailyStreak;
  }

  // Speed level configuration for MCQ Sprint, Logo Challenge (and defaults)
  function getQuestionSpeedConfig(mode, index) {
    const qNum = index + 1;
    if (mode === 'mcq_sprint') {
      if (qNum <= 14) {
        return {
          level: '1.0x',
          speedBadge: '⚡ NORMAL SPEED',
          badgeClass: 'border-cyan-500/40 text-cyan-300 bg-cyan-500/10',
          cardBorder: 'border-rose-500/30',
          totalTime: 30,
          hintThreshold: 0,
          speedDesc: 'Normal Speed (30s per question)'
        };
      } else if (qNum <= 20) {
        return {
          level: '1.5x',
          speedBadge: '🔥 1.5X SPEED',
          badgeClass: 'border-amber-500/50 text-amber-300 bg-amber-500/20 animate-pulse shadow-[0_0_15px_rgba(245,158,11,0.3)]',
          cardBorder: 'border-amber-500/50 shadow-[0_0_30px_rgba(245,158,11,0.2)]',
          totalTime: 20,
          hintThreshold: 0,
          speedDesc: '1.5X Faster Speed (20s per question)'
        };
      } else {
        return {
          level: '2.0x',
          speedBadge: '🚀 2.0X SPEED',
          badgeClass: 'border-rose-500/60 text-rose-300 bg-rose-500/25 animate-pulse shadow-[0_0_20px_rgba(244,63,94,0.4)]',
          cardBorder: 'border-rose-500/60 shadow-[0_0_40px_rgba(244,63,94,0.3)]',
          totalTime: 15,
          hintThreshold: 0,
          speedDesc: '2.0X Sprint Speed (15s per question)'
        };
      }
    } else if (mode === 'logo_quiz') {
      if (qNum <= 14) {
        return {
          level: '1.0x',
          speedBadge: '⚡ NORMAL SPEED',
          badgeClass: 'border-cyan-500/40 text-cyan-300 bg-cyan-500/10',
          cardBorder: 'border-purple-500/30',
          totalTime: 30,
          hintThreshold: 15,
          speedDesc: 'Standard Pace (30s per question)'
        };
      } else if (qNum <= 20) {
        return {
          level: '1.5x',
          speedBadge: '🔥 1.5X SPEED',
          badgeClass: 'border-amber-500/50 text-amber-300 bg-amber-500/20 animate-pulse shadow-[0_0_15px_rgba(245,158,11,0.3)]',
          cardBorder: 'border-amber-500/50 shadow-[0_0_30px_rgba(245,158,11,0.2)]',
          totalTime: 20,
          hintThreshold: 10,
          speedDesc: '1.5X Faster Pace (20s per question)'
        };
      } else {
        return {
          level: '2.5x',
          speedBadge: '🚀 2.5X SPEED',
          badgeClass: 'border-rose-500/60 text-rose-300 bg-rose-500/25 animate-pulse shadow-[0_0_20px_rgba(244,63,94,0.4)]',
          cardBorder: 'border-rose-500/60 shadow-[0_0_40px_rgba(244,63,94,0.3)]',
          totalTime: 12,
          hintThreshold: 6,
          speedDesc: '2.5X Hyperdrive Pace (12s per question)'
        };
      }
    }
    return {
      level: '1.0x',
      speedBadge: '⚡ NORMAL SPEED',
      badgeClass: 'border-cyan-500/40 text-cyan-300 bg-cyan-500/10',
      cardBorder: 'border-cyan-500/30',
      totalTime: 30,
      hintThreshold: 15,
      speedDesc: 'Standard Pace (30s per question)'
    };
  }

  function showSpeedLevelAlert(title, message, speedBadge) {
    SoundFX.combo();
    const existing = document.getElementById('speed-increase-overlay');
    if (existing) existing.remove();

    const overlay = document.createElement('div');
    overlay.id = 'speed-increase-overlay';
    overlay.className = 'fixed inset-0 z-[100] flex items-center justify-center bg-black/75 backdrop-blur-sm animate-fadeIn';
    overlay.innerHTML = `
      <div class="p-8 rounded-3xl bg-[#0A1128] border-2 border-amber-400 text-center max-w-md mx-4 shadow-[0_0_60px_rgba(245,158,11,0.5)] transform scale-105 transition-all">
        <div class="text-5xl mb-3 animate-bounce">⚡</div>
        <span class="text-xs font-black uppercase tracking-widest text-amber-400 bg-amber-500/20 px-3.5 py-1 rounded-full border border-amber-500/40">Difficulty Increased!</span>
        <h3 class="text-2xl font-black text-white mt-3">${title}</h3>
        <div class="inline-block my-3 px-4 py-1 rounded-xl bg-amber-500/15 border border-amber-500/30 text-amber-300 text-sm font-black">
          ${speedBadge}
        </div>
        <p class="text-xs text-slate-300 mb-6 leading-relaxed">${message}</p>
        <button class="btn-placifly-primary py-2.5 px-8 text-xs font-bold" onclick="document.getElementById('speed-increase-overlay').remove()">Continue Challenge ⚡</button>
      </div>
    `;
    document.body.appendChild(overlay);
    setTimeout(() => {
      if (document.body.contains(overlay)) overlay.remove();
    }, 2200);
  }

  // Launch Challenge Mode
  async function startChallenge(mode = 'rapid_fire') {
    state.mode = mode;
    state.currentIndex = 0;
    state.score = 0;
    state.correctCount = 0;
    state.wrongCount = 0;
    state.consecutiveStreak = 0;
    state.maxStreak = 0;
    state.comboMultiplier = 1.0;
    state.questionTimes = [];
    state.isAnswered = false;
    state.hintRevealed = false;
    state.feedbackShowing = false;
    state.previousSpeedLevel = '1.0x';

    clearInterval(state.questionTimerInterval);

    if (typeof switchPlaciflyView === 'function') {
      switchPlaciflyView('daily-challenge');
    }

    renderLoadingScreen(mode);

    try {
      const resp = await fetch(`/api/daily-challenge/questions?mode=${mode}`);
      const data = await resp.json();
      state.questions = data.questions || [];
    } catch (e) {
      console.warn('Backend fetch failed, using internal randomized questions pool:', e);
      state.questions = getFallbackQuestions(mode);
    }

    if (!state.questions || state.questions.length === 0) {
      state.questions = getFallbackQuestions(mode);
    }

    state.startTime = Date.now();
    renderChallengeWorkspace();
    loadCurrentQuestion();
  }

  function getModeTitle(mode) {
    if (mode === 'rapid_fire') return '⚡ Rapid Fire Challenge (30 Questions)';
    if (mode === 'mcq_sprint') return '⏱️ 30 MCQ Speed Sprint (30s Per Question)';
    if (mode === 'logo_quiz') return '🧩 Tech Logo Challenge (Dynamic Speed Scaling)';
    return 'Daily Interview Challenge';
  }

  function renderLoadingScreen(mode) {
    const container = document.getElementById('daily-challenge-container');
    if (!container) return;

    container.innerHTML = `
      <div class="placifly-card p-12 text-center max-w-2xl mx-auto my-8 border-cyan-500/30">
        <div class="inline-block p-4 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 mb-4 animate-bounce">
          <span class="text-4xl">${mode === 'logo_quiz' ? '🧩' : mode === 'mcq_sprint' ? '⏱️' : '⚡'}</span>
        </div>
        <h2 class="text-2xl font-bold text-white mb-2">${getModeTitle(mode)}</h2>
        <p class="text-slate-400 text-sm mb-6">Sampling 30 randomized technology questions & initializing speed timers...</p>
        <div class="w-48 h-1.5 bg-slate-800 rounded-full mx-auto overflow-hidden">
          <div class="h-full bg-gradient-to-r from-blue-500 via-cyan-400 to-indigo-500 rounded-full animate-pulse"></div>
        </div>
      </div>
    `;
  }

  function renderChallengeWorkspace() {
    const container = document.getElementById('daily-challenge-container');
    if (!container) return;

    container.innerHTML = `
      <!-- TOP HUD -->
      <div class="flex flex-wrap items-center justify-between gap-4 mb-6 pb-4 border-b border-cyan-500/20">
        <div class="flex items-center gap-3">
          <button onclick="DailyChallengeEngine.confirmExit()" class="text-slate-400 hover:text-white text-xs px-3 py-1.5 rounded-lg border border-slate-800 hover:bg-slate-900 transition-colors">
            ← Exit Challenge
          </button>
          <div>
            <h2 class="text-base sm:text-lg font-bold text-white flex items-center gap-2">
              <span>${getModeTitle(state.mode)}</span>
            </h2>
            <div class="flex items-center gap-2 mt-0.5">
              <span class="text-xs text-cyan-400 font-mono font-bold" id="daily-q-progress-text">Question 1/30</span>
              <span id="daily-hud-speed-badge" class="text-[10px] font-black px-2 py-0.5 rounded-full border border-cyan-500/30 text-cyan-300 bg-cyan-500/10">⚡ NORMAL SPEED</span>
            </div>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <!-- Combo Badge -->
          <div id="daily-combo-badge" class="hidden px-3 py-1 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-bold flex items-center gap-1.5 animate-pulse">
            <span>🔥</span> <span id="daily-combo-text">1.0x Combo</span>
          </div>

          <!-- Live Score -->
          <div class="px-4 py-1.5 rounded-xl bg-slate-900 border border-cyan-500/30 text-cyan-400 text-xs font-mono font-bold flex items-center gap-2 shadow-[0_0_15px_rgba(0,210,255,0.15)]">
            <span class="text-slate-400">SCORE:</span>
            <span id="daily-live-score" class="text-white text-sm">0</span>
          </div>

          <!-- Sound Mute Toggle -->
          <button id="daily-sound-toggle-btn" onclick="DailyChallengeEngine.toggleSound()" class="text-xs px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white transition-colors">
            ${SoundFX.isMuted ? '🔇 Sound OFF' : '🔊 Sound ON'}
          </button>
        </div>
      </div>

      <!-- Question Dynamic Mounting Container -->
      <div id="daily-card-mount"></div>
      <div id="daily-instant-feedback" class="mt-6 hidden"></div>
    `;
  }

  function loadCurrentQuestion() {
    if (state.currentIndex >= state.questions.length) {
      finishChallenge();
      return;
    }

    state.isAnswered = false;
    state.hintRevealed = false;
    state.feedbackShowing = false;

    const qNum = state.currentIndex + 1;
    const speedConfig = getQuestionSpeedConfig(state.mode, state.currentIndex);

    state.questionTotalTime = speedConfig.totalTime;
    state.questionTimeLeft = speedConfig.totalTime;
    state.hintThreshold = speedConfig.hintThreshold;
    state.questionStartTime = Date.now();

    // Check for Speed Tier Transition Alert (MCQ Sprint & Logo Challenge)
    if (state.mode === 'mcq_sprint') {
      if (qNum === 15 && state.previousSpeedLevel !== '1.5x') {
        state.previousSpeedLevel = '1.5x';
        showSpeedLevelAlert('🔥 Difficulty Increased!', 'Sprint timer accelerated to 1.5X Speed (20s per question)!', '🔥 1.5X SPEED');
      } else if (qNum === 21 && state.previousSpeedLevel !== '2.0x') {
        state.previousSpeedLevel = '2.0x';
        showSpeedLevelAlert('🚀 Difficulty Increased!', 'Sprint timer accelerated to 2.0X Speed (15s per question)! Maximum pace!', '🚀 2.0X SPEED');
      }
    } else if (state.mode === 'logo_quiz') {
      if (qNum === 15 && state.previousSpeedLevel !== '1.5x') {
        state.previousSpeedLevel = '1.5x';
        showSpeedLevelAlert('🔥 Difficulty Increased!', 'Speed boosted to 1.5X Faster (20s per question)! Stay sharp!', '🔥 1.5X SPEED');
      } else if (qNum === 21 && state.previousSpeedLevel !== '2.5x') {
        state.previousSpeedLevel = '2.5x';
        showSpeedLevelAlert('🚀 Difficulty Increased!', 'Hyperdrive 2.5X Speed Active (12s per question)! Pure instant recall!', '🚀 2.5X SPEED');
      }
    }

    // Update HUD Speed Badge
    const hudSpeed = document.getElementById('daily-hud-speed-badge');
    if (hudSpeed) {
      hudSpeed.textContent = speedConfig.speedBadge;
      hudSpeed.className = `text-[10px] font-black px-2 py-0.5 rounded-full border ${speedConfig.badgeClass}`;
    }

    const q = state.questions[state.currentIndex];
    const isDouble = q.double_points || (state.currentIndex === state.questions.length - 1);

    if (isDouble) {
      SoundFX.doublePoints();
    }

    renderQuestionCard(q, isDouble, speedConfig);
    startPerQuestionTimer(isDouble, speedConfig);
  }

  function startPerQuestionTimer(isDouble, speedConfig) {
    clearInterval(state.questionTimerInterval);
    updateTimerUI(state.questionTimeLeft, state.questionTotalTime);

    state.questionTimerInterval = setInterval(() => {
      state.questionTimeLeft--;

      if (state.questionTimeLeft <= 4 && state.questionTimeLeft > 0) {
        SoundFX.tick();
      }

      updateTimerUI(state.questionTimeLeft, state.questionTotalTime);

      // Reveal 4 MCQ options as hints when time reaches hintThreshold (for Rapid Fire & Logo modes)
      if (state.mode !== 'mcq_sprint' && state.questionTimeLeft <= state.hintThreshold && !state.hintRevealed && !state.isAnswered) {
        revealHints();
      }

      // Time Expired for this question
      if (state.questionTimeLeft <= 0) {
        clearInterval(state.questionTimerInterval);
        handleTimeExpired();
      }
    }, 1000);
  }

  function revealHints() {
    state.hintRevealed = true;
    const hintContainer = document.getElementById('daily-mcq-hint-container');
    const hintBanner = document.getElementById('hint-reveal-banner');
    
    if (hintBanner) {
      hintBanner.classList.remove('hidden');
      hintBanner.classList.add('animate-pulse');
    }
    
    if (hintContainer) {
      hintContainer.classList.remove('hidden');
      hintContainer.classList.add('animate-fadeInUp');
    }

    SoundFX.playTone(600, 'sine', 0.1, 0.08);
  }

  function handleTimeExpired() {
    if (state.isAnswered) return;
    state.isAnswered = true;
    state.wrongCount++;
    state.consecutiveStreak = 0;
    state.comboMultiplier = 1.0;
    SoundFX.wrong();

    const q = state.questions[state.currentIndex];
    const correctAns = q.options ? q.options[q.correct_option_index] : (q.name || '');

    if (state.mode === 'mcq_sprint') {
      showSprintTimeoutAnimation(correctAns);
    } else {
      showInstantFeedback(false, correctAns, q.explanation || 'Time ran out before an answer was submitted.', 0);
    }
  }

  function showSprintTimeoutAnimation(correctAns) {
    const mount = document.getElementById('daily-card-mount');
    if (mount) {
      const banner = document.createElement('div');
      banner.className = 'p-3 mt-4 rounded-xl bg-rose-950/80 border border-rose-500/60 text-rose-300 text-xs font-bold text-center animate-fadeInUp';
      banner.innerHTML = `⏱️ Time Expired! Correct Answer: <strong class="text-white">${correctAns}</strong>`;
      mount.appendChild(banner);
    }
    setTimeout(() => {
      state.currentIndex++;
      loadCurrentQuestion();
    }, 900);
  }

  function renderQuestionCard(q, isDouble, speedConfig) {
    const mount = document.getElementById('daily-card-mount');
    if (!mount) return;

    const qNum = state.currentIndex + 1;
    const totalQ = state.questions.length;
    const progressPct = ((qNum - 1) / totalQ) * 100;

    const progText = document.getElementById('daily-q-progress-text');
    if (progText) progText.textContent = `Question ${qNum}/${totalQ}`;

    mount.innerHTML = `
      <div class="placifly-card p-6 sm:p-8 relative overflow-hidden ${isDouble ? 'border-amber-500/50 shadow-[0_0_35px_rgba(245,158,11,0.25)] double-points-card' : speedConfig.cardBorder}">
        
        <!-- Question 30 Special Double Points Glow Banner -->
        ${isDouble ? `
          <div class="absolute -top-1 -right-1 z-20">
            <div class="bg-gradient-to-r from-amber-500 via-rose-500 to-yellow-400 text-slate-950 font-black text-xs px-4 py-1.5 rounded-bl-xl shadow-lg flex items-center gap-1.5 animate-pulse tracking-wider">
              <span>⚡</span> <span>DOUBLE POINTS – 2X SCORE</span>
            </div>
          </div>
        ` : ''}

        <!-- Top Progress, Speed Indicator & Circular Timer -->
        <div class="flex items-center justify-between gap-4 mb-6">
          <div class="flex-1">
            <div class="flex items-center justify-between text-xs text-slate-400 mb-1.5">
              <div class="flex items-center gap-2">
                <span class="text-cyan-400 font-bold uppercase tracking-wider">${q.topic || q.category || 'Technology Challenge'}</span>
                <span class="text-[10px] font-black px-2.5 py-0.5 rounded-full border ${speedConfig.badgeClass}">
                  ${speedConfig.speedBadge}
                </span>
              </div>
              <span class="font-mono text-cyan-300 font-bold">${qNum} of ${totalQ} (${Math.round(progressPct)}%)</span>
            </div>
            <div class="w-full h-2 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
              <div class="h-full bg-gradient-to-r from-blue-500 via-cyan-400 to-indigo-500 rounded-full transition-all duration-300" style="width: ${progressPct}%"></div>
            </div>
          </div>

          <!-- Circular SVG Countdown Timer -->
          <div class="relative flex items-center justify-center w-14 h-14 flex-shrink-0">
            <svg class="w-14 h-14 transform -rotate-90">
              <circle cx="28" cy="28" r="23" stroke="#1e293b" stroke-width="4" fill="transparent"/>
              <circle id="daily-timer-circle" cx="28" cy="28" r="23" stroke="#00D2FF" stroke-width="4" fill="transparent"
                stroke-dasharray="144.5" stroke-dashoffset="0" stroke-linecap="round" class="transition-all duration-1000 ease-linear"/>
            </svg>
            <span id="daily-timer-text" class="absolute font-mono font-extrabold text-sm text-white">${speedConfig.totalTime}</span>
          </div>
        </div>

        <!-- Question / Logo Main Body -->
        <div class="mb-6">
          ${state.mode === 'logo_quiz' ? `
            <div class="flex flex-col sm:flex-row items-center gap-6 p-6 rounded-2xl bg-[#030B1E] border border-cyan-500/20 mb-4">
              <div class="w-28 h-28 p-3 rounded-2xl bg-slate-900/90 border border-cyan-500/30 flex items-center justify-center shadow-inner flex-shrink-0">
                ${q.logo_svg || '<span class="text-4xl">🧩</span>'}
              </div>
              <div class="text-center sm:text-left">
                <span class="text-xs font-bold text-amber-400 uppercase tracking-wider bg-amber-500/10 px-3 py-1 rounded-full border border-amber-500/20">
                  IDENTIFY THE TECHNOLOGY (${speedConfig.speedBadge})
                </span>
                <h3 class="text-xl sm:text-2xl font-bold text-white mt-2">Which tech logo is displayed?</h3>
                <p class="text-xs text-slate-400 mt-1">${q.hint || 'Type name directly or wait for MCQ hint options.'}</p>
                <div class="text-[11px] text-cyan-400 font-mono mt-1">⏱️ ${speedConfig.totalTime}s clock (Hints after ${speedConfig.totalTime - speedConfig.hintThreshold}s)</div>
              </div>
            </div>
          ` : `
            <h3 class="text-lg sm:text-xl font-extrabold text-white leading-snug mb-2">
              ${q.question}
            </h3>
            ${state.mode !== 'mcq_sprint' ? `
              <p class="text-xs text-slate-400">
                ⏱️ First 15s: Type your answer below. After 15s, 4 MCQ hint options will unlock automatically.
              </p>
            ` : ''}
          `}
        </div>

        <!-- MODE SPECIFIC INPUTS -->
        ${state.mode === 'mcq_sprint' ? `
          <!-- 30 MCQ SPRINT: 4 Fast Option Buttons -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4">
            ${(q.options || []).map((opt, idx) => `
              <button class="daily-mcq-opt-btn p-4 rounded-xl bg-slate-900/90 hover:bg-cyan-950/40 border border-slate-800 hover:border-cyan-400 text-left text-xs sm:text-sm text-slate-200 hover:text-white transition-all flex items-center justify-between group active:scale-98"
                onclick="DailyChallengeEngine.selectMCQOption(${idx})">
                <span class="flex items-center gap-3">
                  <span class="w-7 h-7 rounded-lg bg-slate-800 group-hover:bg-cyan-500/20 text-slate-300 group-hover:text-cyan-300 font-bold text-xs flex items-center justify-center border border-slate-700">
                    ${String.fromCharCode(65 + idx)}
                  </span>
                  <span class="font-semibold">${opt}</span>
                </span>
                <span class="text-slate-600 group-hover:text-cyan-400">⚡</span>
              </button>
            `).join('')}
          </div>
        ` : `
          <!-- RAPID FIRE & LOGO: Text Input + MCQ Hint Reveal -->
          <div class="mb-6">
            <label class="block text-xs font-semibold text-slate-300 mb-2 flex items-center justify-between">
              <span>⌨️ Type Your Answer Directly:</span>
              <span class="text-[11px] text-cyan-400 font-normal">Fuzzy spell-check enabled</span>
            </label>
            <div class="flex gap-3">
              <input type="text" id="daily-typed-input" placeholder="e.g. ${state.mode === 'logo_quiz' ? 'Python, Docker, React...' : 'Type your answer here...'}"
                class="w-full px-4 py-3.5 rounded-xl bg-slate-900/90 border border-cyan-500/30 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 text-sm font-medium transition-all"
                onkeydown="if(event.key==='Enter') DailyChallengeEngine.submitTypedAnswer()">
              <button class="btn-placifly-primary py-3.5 px-6 text-xs whitespace-nowrap font-bold" onclick="DailyChallengeEngine.submitTypedAnswer()">
                <span>Submit Answer →</span>
              </button>
            </div>
          </div>

          <div id="hint-reveal-banner" class="hidden mb-3">
            <div class="flex items-center gap-2 text-xs text-amber-400 bg-amber-500/10 px-3 py-1.5 rounded-xl border border-amber-500/20">
              <span>💡</span>
              <span class="font-semibold">Hint Options Unlocked! Click an option below or submit your typed answer.</span>
            </div>
          </div>

          <div id="daily-mcq-hint-container" class="hidden grid grid-cols-1 sm:grid-cols-2 gap-3 mt-4">
            ${(q.options || []).map((opt, idx) => `
              <button class="daily-mcq-opt-btn p-4 rounded-xl bg-slate-900/80 hover:bg-slate-800/90 border border-slate-800 hover:border-cyan-500/50 text-left text-xs sm:text-sm text-slate-200 hover:text-white transition-all flex items-center justify-between group"
                onclick="DailyChallengeEngine.selectMCQOption(${idx})">
                <span class="flex items-center gap-3">
                  <span class="w-6 h-6 rounded-lg bg-slate-800 group-hover:bg-cyan-500/20 text-slate-400 group-hover:text-cyan-400 font-bold text-xs flex items-center justify-center border border-slate-700 transition-colors">
                    ${String.fromCharCode(65 + idx)}
                  </span>
                  <span class="font-medium">${opt}</span>
                </span>
                <span class="text-slate-600 group-hover:text-cyan-400 transition-colors">→</span>
              </button>
            `).join('')}
          </div>
        `}

      </div>
    `;

    setTimeout(() => {
      const input = document.getElementById('daily-typed-input');
      if (input) input.focus();
    }, 100);
  }

  function updateTimerUI(timeLeft, totalTime = 30) {
    const timerText = document.getElementById('daily-timer-text');
    const timerCircle = document.getElementById('daily-timer-circle');
    if (!timerText || !timerCircle) return;

    timerText.textContent = Math.max(0, timeLeft);

    const circumference = 2 * Math.PI * 23; // 144.51
    const offset = circumference - (timeLeft / Math.max(1, totalTime)) * circumference;
    timerCircle.style.strokeDashoffset = offset;

    if (timeLeft <= 4) {
      timerCircle.setAttribute('stroke', '#EF4444');
      timerText.classList.add('text-rose-400', 'animate-pulse');
    } else if (timeLeft <= Math.floor(totalTime / 2)) {
      timerCircle.setAttribute('stroke', '#F59E0B');
      timerText.classList.remove('text-rose-400');
      timerText.classList.add('text-amber-400');
    } else {
      timerCircle.setAttribute('stroke', '#00D2FF');
      timerText.classList.remove('text-rose-400', 'text-amber-400');
    }
  }

  /* ============================================================================
     ANSWER SUBMISSION & SCORING
     ============================================================================ */

  function submitTypedAnswer() {
    if (state.isAnswered || state.feedbackShowing) return;
    const input = document.getElementById('daily-typed-input');
    if (!input || !input.value.trim()) {
      if (input) {
        input.focus();
        input.classList.add('border-rose-500');
        setTimeout(() => input.classList.remove('border-rose-500'), 500);
      }
      return;
    }

    const typedText = input.value.trim();
    const q = state.questions[state.currentIndex];
    const isDouble = q.double_points || (state.currentIndex === state.questions.length - 1);

    clearInterval(state.questionTimerInterval);
    state.isAnswered = true;

    const isCorrect = checkFuzzyMatch(typedText, q.accepted_answers || [q.options[q.correct_option_index]]);
    processAnswerResult(isCorrect, q, isDouble, typedText);
  }

  function selectMCQOption(optionIndex) {
    if (state.isAnswered || state.feedbackShowing) return;

    clearInterval(state.questionTimerInterval);
    state.isAnswered = true;

    const q = state.questions[state.currentIndex];
    const isDouble = q.double_points || (state.currentIndex === state.questions.length - 1);
    const isCorrect = (optionIndex === q.correct_option_index);

    const optButtons = document.querySelectorAll('.daily-mcq-opt-btn');
    optButtons.forEach((btn, idx) => {
      btn.disabled = true;
      if (idx === q.correct_option_index) {
        btn.classList.add('bg-emerald-500/20', 'border-emerald-400', 'text-emerald-300');
      } else if (idx === optionIndex && !isCorrect) {
        btn.classList.add('bg-rose-500/20', 'border-rose-400', 'text-rose-300');
      }
    });

    processAnswerResult(isCorrect, q, isDouble, q.options[optionIndex]);
  }

  function processAnswerResult(isCorrect, q, isDouble, userAnsText) {
    const elapsed = (Date.now() - state.questionStartTime) / 1000;
    state.questionTimes.push(elapsed);

    let pointsAwarded = 0;
    const basePoints = 100;

    if (isCorrect) {
      state.correctCount++;
      state.consecutiveStreak++;
      if (state.consecutiveStreak > state.maxStreak) {
        state.maxStreak = state.consecutiveStreak;
      }

      if (state.consecutiveStreak >= 5) state.comboMultiplier = 3.0;
      else if (state.consecutiveStreak >= 4) state.comboMultiplier = 2.0;
      else if (state.consecutiveStreak >= 3) state.comboMultiplier = 1.5;
      else if (state.consecutiveStreak >= 2) state.comboMultiplier = 1.2;
      else state.comboMultiplier = 1.0;

      const speedBonus = Math.max(0, Math.floor((state.questionTotalTime - elapsed) * 2));
      const doubleMult = isDouble ? 2 : 1;
      pointsAwarded = Math.round((basePoints + speedBonus) * state.comboMultiplier * doubleMult);
      state.score += pointsAwarded;

      SoundFX.correct();
      if (state.consecutiveStreak >= 3) {
        SoundFX.combo();
      }
    } else {
      state.wrongCount++;
      state.consecutiveStreak = 0;
      state.comboMultiplier = 1.0;
      SoundFX.wrong();
    }

    updateHUDStats();

    const correctAns = q.options ? q.options[q.correct_option_index] : (q.name || '');

    if (state.mode === 'mcq_sprint') {
      setTimeout(() => {
        state.currentIndex++;
        if (state.currentIndex < state.questions.length) {
          loadCurrentQuestion();
        } else {
          finishChallenge();
        }
      }, 750);
    } else {
      showInstantFeedback(isCorrect, correctAns, q.explanation, pointsAwarded);
    }
  }

  function showInstantFeedback(isCorrect, correctAns, explanation, pointsAwarded) {
    state.feedbackShowing = true;
    const feedbackBox = document.getElementById('daily-instant-feedback');
    if (!feedbackBox) return;

    feedbackBox.classList.remove('hidden');
    feedbackBox.innerHTML = `
      <div class="p-6 rounded-2xl ${isCorrect ? 'bg-emerald-950/40 border-emerald-500/40' : 'bg-rose-950/40 border-rose-500/40'} border backdrop-blur-md animate-fadeInUp">
        <div class="flex items-start justify-between gap-4 mb-3">
          <div class="flex items-center gap-3">
            <span class="text-3xl">${isCorrect ? '✨' : '❌'}</span>
            <div>
              <h4 class="text-lg font-bold ${isCorrect ? 'text-emerald-300' : 'text-rose-300'}">
                ${isCorrect ? 'Correct! Excellent Reflexes!' : 'Not Quite Right'}
              </h4>
              <span class="text-xs text-slate-400">
                ${isCorrect ? `+${pointsAwarded} Points (${state.comboMultiplier}x Combo)` : `Correct answer: <strong class="text-cyan-300">${correctAns}</strong>`}
              </span>
            </div>
          </div>
          ${state.consecutiveStreak >= 2 ? `
            <div class="px-3 py-1 rounded-full bg-amber-500/20 border border-amber-500/40 text-amber-300 text-xs font-bold animate-pulse">
              🔥 ${state.consecutiveStreak} in a Row! (${state.comboMultiplier}x)
            </div>
          ` : ''}
        </div>

        <p class="text-xs text-slate-300 leading-relaxed mb-4 pl-1 border-l-2 ${isCorrect ? 'border-emerald-500' : 'border-rose-500'}">
          ${explanation || 'Great job answering! Keep your momentum going for the next question.'}
        </p>

        <div class="flex justify-end">
          <button class="btn-placifly-primary py-2 px-6 text-xs font-bold" onclick="DailyChallengeEngine.nextQuestion()">
            <span>${state.currentIndex === state.questions.length - 1 ? 'View Final Results →' : 'Next Question →'}</span>
          </button>
        </div>
      </div>
    `;

    feedbackBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  function nextQuestion() {
    state.currentIndex++;
    loadCurrentQuestion();
  }

  function checkFuzzyMatch(userInput, acceptedList) {
    if (!userInput || !acceptedList) return false;
    const clean = userInput.toLowerCase().replace(/[^a-z0-9]/g, '');
    for (const target of acceptedList) {
      const cleanTarget = target.toLowerCase().replace(/[^a-z0-9]/g, '');
      if (clean === cleanTarget) return true;
      if (cleanTarget.length >= 3 && (clean.includes(cleanTarget) || cleanTarget.includes(clean))) return true;
    }
    return false;
  }

  function updateHUDStats() {
    const scoreEl = document.getElementById('daily-live-score');
    if (scoreEl) scoreEl.textContent = state.score;

    const comboBadge = document.getElementById('daily-combo-badge');
    const comboText = document.getElementById('daily-combo-text');
    if (comboBadge && comboText) {
      if (state.consecutiveStreak >= 2) {
        comboBadge.classList.remove('hidden');
        comboText.textContent = `${state.consecutiveStreak} Streak (${state.comboMultiplier}x)`;
      } else {
        comboBadge.classList.add('hidden');
      }
    }
  }

  /* ============================================================================
     FINAL RESULT SCREEN (SCORE OUT OF 30)
     ============================================================================ */

  async function finishChallenge() {
    clearInterval(state.questionTimerInterval);
    SoundFX.victory();

    const totalQuestions = state.questions.length || 30;
    const accuracy = totalQuestions > 0 ? Math.round((state.correctCount / Math.max(1, totalQuestions)) * 100) : 0;
    
    state.totalTimeSpent = Math.round((Date.now() - state.startTime) / 1000);
    const avgTime = state.questionTimes.length > 0
      ? (state.questionTimes.reduce((a, b) => a + b, 0) / state.questionTimes.length).toFixed(1)
      : '0.0';

    const currentStreak = updateDailyStreak();
    const stats = getDailyStats();
    let isNewPB = false;

    if (!stats.bestScores[state.mode] || state.score > stats.bestScores[state.mode]) {
      stats.bestScores[state.mode] = state.score;
      isNewPB = true;
    }
    stats.totalXP += Math.floor(state.score / 10) + (currentStreak * 15);
    saveDailyStats(stats);

    if (typeof addXP === 'function') {
      const earnedXP = Math.floor(state.score / 10) + (currentStreak * 15);
      addXP(earnedXP);
    }

    triggerCelebration();

    let backendBadges = [];
    try {
      const submitResp = await fetch('/api/daily-challenge/submit-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mode: state.mode,
          score: state.score,
          accuracy: accuracy,
          streak: currentStreak
        })
      });
      const submitData = await submitResp.json();
      backendBadges = submitData.badges_earned || [];
    } catch (e) {}

    renderFinalResultsScreen({
      score: state.score,
      correctCount: state.correctCount,
      wrongCount: state.wrongCount,
      totalQuestions: totalQuestions,
      accuracy: accuracy,
      totalTimeSpent: state.totalTimeSpent,
      avgTime: avgTime,
      currentStreak: currentStreak,
      bestStreak: Math.max(currentStreak, stats.dailyStreak || currentStreak),
      isNewPB: isNewPB,
      personalBest: stats.bestScores[state.mode],
      xpEarned: Math.floor(state.score / 10) + (currentStreak * 15),
      badgesEarned: backendBadges
    });
  }

  function triggerCelebration() {
    if (typeof confetti === 'function') {
      confetti({
        particleCount: 100,
        spread: 80,
        origin: { y: 0.6 }
      });
    } else if (typeof createConfetti === 'function') {
      createConfetti();
    }
  }

  function getMotivationalFeedback(accuracy) {
    if (accuracy >= 90) return "🌟 Outstanding Performance! Your technical reflexes and speed are at elite top-tier placement standards.";
    if (accuracy >= 70) return "💪 Solid Accuracy! Great technical recall under pressure. Keep practicing to hit 30/30!";
    if (accuracy >= 50) return "🎯 Good Warmup! Consistency is the key to cracking technical rounds. Try another 30-question sprint!";
    return "💡 Practice makes perfect! Daily repetition sharpens your instant recall. Try another round to beat your personal best!";
  }

  function renderFinalResultsScreen(res) {
    const container = document.getElementById('daily-challenge-container');
    if (!container) return;

    container.innerHTML = `
      <div class="placifly-card p-6 sm:p-10 max-w-3xl mx-auto my-6 border-cyan-500/30 relative overflow-hidden animate-fadeIn">
        
        <!-- Top Celebration Header -->
        <div class="text-center mb-8">
          <div class="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-cyan-500/10 border border-cyan-500/30 text-4xl mb-4 shadow-[0_0_30px_rgba(0,210,255,0.2)]">
            ${res.accuracy >= 80 ? '🏆' : '🎯'}
          </div>
          <span class="text-xs font-bold text-cyan-400 uppercase tracking-widest bg-cyan-500/10 px-3 py-1 rounded-full border border-cyan-500/20">
            ${getModeTitle(state.mode)} Completed
          </span>
          <h2 class="text-3xl sm:text-4xl font-extrabold text-white mt-3">
            Score: <span class="text-cyan-400 font-mono">${res.correctCount} / 30</span> Correct
          </h2>
          <p class="text-sm text-slate-300 max-w-md mx-auto mt-2 leading-relaxed">
            ${getMotivationalFeedback(res.accuracy)}
          </p>

          ${res.isNewPB ? `
            <div class="inline-flex items-center gap-2 mt-4 px-4 py-1.5 rounded-full bg-amber-500/20 border border-amber-500/40 text-amber-300 text-xs font-bold animate-pulse">
              <span>🏆</span> <span>NEW PERSONAL BEST SCORE!</span>
            </div>
          ` : ''}
        </div>

        <!-- 4-Grid Key Performance Metrics -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
          
          <div class="p-4 rounded-2xl bg-[#030B1E] border border-cyan-500/20 text-center">
            <span class="text-[11px] text-slate-400 block mb-1 font-semibold uppercase">TOTAL SCORE</span>
            <span class="text-2xl sm:text-3xl font-black text-white font-mono">${res.score}</span>
            <span class="text-[10px] text-cyan-400 block mt-1">PB: ${res.personalBest}</span>
          </div>

          <div class="p-4 rounded-2xl bg-[#030B1E] border border-emerald-500/20 text-center">
            <span class="text-[11px] text-slate-400 block mb-1 font-semibold uppercase">ACCURACY</span>
            <span class="text-2xl sm:text-3xl font-black text-emerald-400 font-mono">${res.accuracy}%</span>
            <span class="text-[10px] text-slate-400 block mt-1">${res.correctCount}/30 Correct</span>
          </div>

          <div class="p-4 rounded-2xl bg-[#030B1E] border border-amber-500/20 text-center">
            <span class="text-[11px] text-slate-400 block mb-1 font-semibold uppercase">DAILY STREAK</span>
            <span class="text-2xl sm:text-3xl font-black text-amber-400 font-mono">${res.currentStreak} 🔥</span>
            <span class="text-[10px] text-slate-400 block mt-1">Best: ${res.bestStreak} Days</span>
          </div>

          <div class="p-4 rounded-2xl bg-[#030B1E] border border-purple-500/20 text-center">
            <span class="text-[11px] text-slate-400 block mb-1 font-semibold uppercase">XP EARNED</span>
            <span class="text-2xl sm:text-3xl font-black text-purple-400 font-mono">+${res.xpEarned}</span>
            <span class="text-[10px] text-purple-300 block mt-1">Level Progress</span>
          </div>

        </div>

        <!-- Detailed Analytics & Badges -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
          <div class="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
            <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-2">
              <span>⏱️</span> Time & Breakdown
            </h4>
            <div class="space-y-2 text-xs">
              <div class="flex justify-between text-slate-300">
                <span class="text-slate-400">Total Duration:</span>
                <span class="font-mono font-bold text-white">${res.totalTimeSpent}s</span>
              </div>
              <div class="flex justify-between text-slate-300">
                <span class="text-slate-400">Avg Response Time:</span>
                <span class="font-mono font-bold text-cyan-400">${res.avgTime}s / question</span>
              </div>
              <div class="flex justify-between text-slate-300">
                <span class="text-slate-400">Correct / Wrong:</span>
                <span class="font-mono font-bold text-white"><span class="text-emerald-400">${res.correctCount}</span> / <span class="text-rose-400">${res.wrongCount}</span></span>
              </div>
              <div class="flex justify-between text-slate-300">
                <span class="text-slate-400">Max Combo Streak:</span>
                <span class="font-mono font-bold text-amber-400">${state.maxStreak} in a row</span>
              </div>
            </div>
          </div>

          <div class="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
            <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-2">
              <span>🎖️</span> Badges & Achievements
            </h4>
            ${res.badgesEarned.length > 0 ? `
              <div class="space-y-2">
                ${res.badgesEarned.map(b => `
                  <div class="flex items-center gap-2.5 p-2 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs">
                    <span class="text-lg">${b.icon || '🏅'}</span>
                    <div>
                      <span class="font-bold text-amber-300 block">${b.name}</span>
                      <span class="text-[10px] text-slate-400">${b.desc}</span>
                    </div>
                  </div>
                `).join('')}
              </div>
            ` : `
              <div class="text-center py-3 text-xs text-slate-500">
                <span>🎯 Keep scoring above 80% with quick response times to unlock badges!</span>
              </div>
            `}
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex flex-col sm:flex-row items-center justify-center gap-3 pt-4 border-t border-cyan-500/20">
          <button class="btn-placifly-primary w-full sm:w-auto py-3 px-6 text-xs font-bold" onclick="DailyChallengeEngine.startChallenge('${state.mode}')">
            <span>🔄 Play Again (30 Qs)</span>
          </button>
          
          <button class="w-full sm:w-auto py-3 px-6 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold border border-slate-700 transition-colors"
            onclick="DailyChallengeEngine.openModeSelector()">
            <span>⚡ Try Another Challenge</span>
          </button>

          <button class="w-full sm:w-auto py-3 px-5 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 text-xs font-bold border border-cyan-500/30 transition-colors"
            onclick="DailyChallengeEngine.shareResult(${res.correctCount}, ${res.accuracy})">
            <span>🔗 Share Result</span>
          </button>

          <button class="w-full sm:w-auto py-3 px-5 rounded-xl text-slate-400 hover:text-white text-xs transition-colors"
            onclick="switchPlaciflyView('home')">
            <span>Back to Dashboard</span>
          </button>
        </div>

      </div>
    `;
  }

  function openModeSelector() {
    const container = document.getElementById('daily-challenge-container');
    if (!container) return;

    const stats = getDailyStats();

    container.innerHTML = `
      <div class="max-w-4xl mx-auto my-6">
        
        <div class="flex items-center justify-between mb-8">
          <div>
            <span class="text-xs font-bold text-amber-400 uppercase tracking-wider bg-amber-500/10 px-3 py-1 rounded-full border border-amber-500/20">
              DAILY GAMIFIED HABIT
            </span>
            <h2 class="text-2xl sm:text-3xl font-extrabold text-white mt-2">Choose Challenge Mode</h2>
            <p class="text-xs text-slate-400 mt-1">30 questions per mode. Question 30 awards Double Points!</p>
          </div>
          <button onclick="switchPlaciflyView('home')" class="text-xs text-slate-400 hover:text-white px-3 py-1.5 rounded-lg border border-slate-800 hover:bg-slate-900 transition-colors">
            ← Dashboard
          </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          <!-- Mode 1: Rapid Fire -->
          <div class="placifly-card p-6 border-cyan-500/30 hover:border-cyan-400 transition-all flex flex-col justify-between group">
            <div>
              <div class="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 text-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                ⚡
              </div>
              <h3 class="text-lg font-bold text-white mb-2">Rapid Fire Challenge</h3>
              <p class="text-xs text-slate-400 leading-relaxed mb-4">
                30 technology questions across AI, LLMs, Cloud, Web & Databases. 30s per question with 15s hint reveal.
              </p>
              <div class="space-y-1 text-[11px] text-slate-400 mb-6">
                <div>🎯 30 Questions</div>
                <div>⏱️ 30s for EACH question</div>
                <div>💡 15s MCQ Hint Reveal</div>
                <div>⚡ Q30: Double Points (2X)</div>
                <div class="text-cyan-400 font-mono">🏆 Best: ${stats.bestScores.rapid_fire || 0} pts</div>
              </div>
            </div>
            <button class="btn-placifly-primary w-full py-2.5 text-xs font-bold" onclick="DailyChallengeEngine.startChallenge('rapid_fire')">
              <span>Start Rapid Fire (30 Qs) →</span>
            </button>
          </div>

          <!-- Mode 2: 30 MCQ Speed Sprint -->
          <div class="placifly-card p-6 border-rose-500/30 hover:border-rose-400 transition-all flex flex-col justify-between group">
            <div>
              <div class="w-12 h-12 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                ⏱️
              </div>
              <h3 class="text-lg font-bold text-white mb-2">30 MCQ Speed Sprint</h3>
              <p class="text-xs text-slate-400 leading-relaxed mb-4">
                30 MCQ questions across Python, JS, Java, DSA, AI & Cloud with progressive timer scaling (1.0X ➔ 1.5X ➔ 2.0X).
              </p>
              <div class="space-y-1 text-[11px] text-slate-400 mb-6">
                <div>🎯 30 Fast MCQs</div>
                <div>⚡ Q1–14: Normal Speed (30s)</div>
                <div>🔥 Q15–20: 1.5X Speed (20s)</div>
                <div>🚀 Q21–30: 2.0X Speed (15s)</div>
                <div>⚡ Q30: Double Points (2X)</div>
                <div class="text-rose-400 font-mono">🏆 Best: ${stats.bestScores.mcq_sprint || 0} pts</div>
              </div>
            </div>
            <button class="btn-placifly-primary w-full py-2.5 text-xs font-bold" onclick="DailyChallengeEngine.startChallenge('mcq_sprint')">
              <span>Start Speed Sprint (Dynamic Speed) →</span>
            </button>
          </div>

          <!-- Mode 3: Logo Challenge with Dynamic Speed Scaling -->
          <div class="placifly-card p-6 border-purple-500/30 hover:border-purple-400 transition-all flex flex-col justify-between group">
            <div>
              <div class="w-12 h-12 rounded-2xl bg-purple-500/10 border border-purple-500/30 text-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                🧩
              </div>
              <h3 class="text-lg font-bold text-white mb-2">Tech Logo Challenge</h3>
              <p class="text-xs text-slate-400 leading-relaxed mb-4">
                30 randomized logos of languages, frameworks, AI & cloud tools with dynamic speed tiers (1.0X ➔ 1.5X ➔ 2.5X).
              </p>
              <div class="space-y-1 text-[11px] text-slate-400 mb-6">
                <div>🎨 30 Tech & AI Logos</div>
                <div>⚡ Q1–14: Normal Speed (30s)</div>
                <div>🔥 Q15–20: 1.5X Speed (20s)</div>
                <div>🚀 Q21–30: 2.5X Speed (12s)</div>
                <div>⚡ Q30: Double Points (2X)</div>
                <div class="text-purple-400 font-mono">🏆 Best: ${stats.bestScores.logo_quiz || 0} pts</div>
              </div>
            </div>
            <button class="btn-placifly-primary w-full py-2.5 text-xs font-bold" onclick="DailyChallengeEngine.startChallenge('logo_quiz')">
              <span>Start Logo Quiz (Dynamic Speed) →</span>
            </button>
          </div>

        </div>
      </div>
    `;
  }

  function shareResult(correctCount, accuracy) {
    const text = `🎯 I scored ${correctCount}/30 (${accuracy}%) in today's Placifly Daily Interview Challenge! 🚀 Practice your developer reflexes on Placifly!`;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(() => {
        if (typeof showToast === 'function') {
          showToast('Scorecard copied to clipboard! 📋', 'success');
        } else {
          alert('Scorecard copied to clipboard!');
        }
      });
    } else {
      alert(text);
    }
  }

  function confirmExit() {
    if (confirm('Are you sure you want to exit? Your current challenge progress will be reset.')) {
      clearInterval(state.questionTimerInterval);
      openModeSelector();
    }
  }

  function getFallbackQuestions(mode) {
    const questions = [];
    for (let i = 1; i <= 30; i++) {
      questions.push({
        id: `fb-${mode}-${i}`,
        topic: 'Technology',
        category: 'Software Engineering',
        question: `Question ${i}: Which concept is fundamental to modern high-performance cloud and AI applications?`,
        options: ['Microservices & Async I/O', 'Monolithic Single-Threaded Design', 'Direct Raw Pointer Manipulation', 'Unindexed Full Table Scans'],
        correct_option_index: 0,
        accepted_answers: ['microservices', 'async io', 'concurrency'],
        double_points: (i === 30),
        explanation: 'Asynchronous I/O and scalable microservices enable resilient distributed cloud architectures.'
      });
    }
    return questions;
  }

  // Public Interface
  return {
    startChallenge,
    submitTypedAnswer,
    selectMCQOption,
    nextQuestion,
    toggleSound: () => SoundFX.toggleMute(),
    openModeSelector,
    shareResult,
    confirmExit,
    updateDailyStreak,
    getDailyStats
  };
})();

window.DailyChallengeEngine = DailyChallengeEngine;
