/* ================================================
   GAMIFICATION MODULE — XP, Badges, Level, Streak
   ================================================ */

const STORAGE_KEY = 'placifly_stats';

function getStoredStats() {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    if (data) return JSON.parse(data);
  } catch (e) {}
  return { totalXP: 0, level: 1, badges: [], streak: 0, lastPlayed: null };
}

function saveStats(stats) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(stats));
  } catch (e) {}
}

function updateStreak() {
  const stats = getStoredStats();
  const today = new Date().toDateString();
  if (stats.lastPlayed !== today) {
    const yesterday = new Date(Date.now() - 86400000).toDateString();
    stats.streak = (stats.lastPlayed === yesterday) ? stats.streak + 1 : 1;
    stats.lastPlayed = today;
    saveStats(stats);
  }
  const el = document.getElementById('streak-count');
  if (el) el.textContent = stats.streak;
}

function updateXPBar(currentXP, level) {
  const xpBar = document.getElementById('xp-bar-fill');
  const xpText = document.getElementById('xp-text');
  const levelBadge = document.getElementById('level-badge');
  if (!xpBar) return;

  const xpPerLevel = 500;
  const xpInLevel = currentXP % xpPerLevel;
  const pct = Math.min((xpInLevel / xpPerLevel) * 100, 100);

  xpBar.style.width = pct + '%';
  if (xpText) xpText.textContent = `${xpInLevel} / ${xpPerLevel} XP`;
  if (levelBadge) levelBadge.textContent = `Lvl ${level}`;
}

function addXP(amount) {
  const stats = getStoredStats();
  stats.totalXP += amount;
  stats.level = Math.floor(stats.totalXP / 500) + 1;
  saveStats(stats);
  updateXPBar(stats.totalXP, stats.level);
  showToast(`+${amount} XP earned!`, 'success');
}

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = 'toast';
  if (type === 'success') toast.style.borderLeftColor = 'var(--emerald)';
  else if (type === 'warning') toast.style.borderLeftColor = 'var(--amber)';
  else if (type === 'error') toast.style.borderLeftColor = 'var(--rose)';
  else toast.style.borderLeftColor = 'var(--blue)';

  toast.innerHTML = `<div class="flex items-center gap-2">
    <span>${type === 'success' ? '✨' : type === 'warning' ? '⚠️' : type === 'error' ? '❌' : 'ℹ️'}</span>
    <span>${message}</span>
  </div>`;

  container.appendChild(toast);
  setTimeout(() => {
    toast.classList.add('toast-out');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

function showBadgeUnlocked(badge) {
  createConfetti();
  const modal = document.createElement('div');
  modal.className = 'badge-modal';
  modal.onclick = (e) => { if (e.target === modal) modal.remove(); };
  modal.innerHTML = `
    <div class="badge-modal-content glass-card p-10 text-center max-w-sm mx-4" style="border-color: rgba(245,158,11,0.3); box-shadow: 0 0 60px rgba(245,158,11,0.15);">
      <div class="text-xs font-bold text-amber-400 uppercase tracking-[0.2em] mb-3">🏆 Badge Unlocked</div>
      <div class="text-7xl mb-4" style="animation: bounce 1s ease infinite;">${badge.icon_emoji || badge.icon || '🎖️'}</div>
      <h3 class="text-2xl font-extrabold mb-2">${badge.name}</h3>
      <p class="text-slate-400 mb-6 text-sm">${badge.description || badge.desc || ''}</p>
      <button class="btn-primary w-full text-base" onclick="this.closest('.badge-modal').remove()">Awesome!</button>
    </div>
  `;
  document.body.appendChild(modal);
  setTimeout(() => { if (document.body.contains(modal)) modal.remove(); }, 5000);
}

function showLevelUp(newLevel) {
  createConfetti();
  showToast(`🎉 Level Up! You are now Level ${newLevel}!`, 'success');
}

function createConfetti() {
  const colors = ['#00f2fe', '#4facfe', '#7f00ff', '#a855f7', '#10b981', '#f59e0b', '#f43f5e', '#ec4899', '#fbbf24'];
  for (let i = 0; i < 60; i++) {
    const piece = document.createElement('div');
    piece.className = 'confetti-piece';
    const size = Math.random() * 8 + 4;
    piece.style.cssText = `
      left: ${Math.random() * 100}vw;
      top: -10px;
      width: ${size}px;
      height: ${size * (Math.random() > 0.5 ? 1 : 0.6)}px;
      background: ${colors[Math.floor(Math.random() * colors.length)]};
      border-radius: ${Math.random() > 0.5 ? '50%' : '2px'};
      animation-duration: ${Math.random() * 2 + 2}s;
      animation-delay: ${Math.random() * 0.5}s;
    `;
    document.body.appendChild(piece);
    setTimeout(() => piece.remove(), 5000);
  }
}

function showLoading(text = 'Analyzing your response...') {
  const overlay = document.getElementById('loading-overlay');
  const loadingText = document.getElementById('loading-text');
  if (overlay) overlay.classList.add('active');
  if (loadingText) loadingText.textContent = text;
}

function hideLoading() {
  const overlay = document.getElementById('loading-overlay');
  if (overlay) overlay.classList.remove('active');
}
