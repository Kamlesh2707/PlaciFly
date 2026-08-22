import json
import hashlib
import os
import time
import threading

# Thread-safe lock for file operations
_lock = threading.Lock()

# Path to the question history JSON file
HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'question_history.json')

def _ensure_data_dir():
    """Ensure the data directory exists."""
    data_dir = os.path.dirname(HISTORY_FILE)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)

def _load_history():
    """Load question history from disk."""
    _ensure_data_dir()
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def _save_history(history):
    """Save question history to disk."""
    _ensure_data_dir()
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Warning: Could not save question history: {e}")

def _hash_question(question_text):
    """Generate SHA-256 hash of question text for deduplication."""
    normalized = question_text.strip().lower()
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:16]

def record_question(session_id, question_data):
    """
    Record a generated question in history.
    
    Args:
        session_id: Unique session identifier (can be 'global' for cross-session dedup)
        question_data: Dict with keys like 'company', 'difficulty', 'question', 'topic', 'category'
    """
    with _lock:
        history = _load_history()
        
        key = session_id or 'global'
        if key not in history:
            history[key] = []
        
        question_text = question_data.get('question', '')
        entry = {
            'question_hash': _hash_question(question_text),
            'company': question_data.get('company', ''),
            'difficulty': question_data.get('difficulty', ''),
            'topic': question_data.get('topic', ''),
            'category': question_data.get('category', ''),
            'question_preview': question_text[:100],
            'timestamp': time.time()
        }
        
        history[key].append(entry)
        
        # Keep only last 200 entries per session to prevent file bloat
        if len(history[key]) > 200:
            history[key] = history[key][-200:]
        
        _save_history(history)

def get_asked_hashes(session_id, company=None, difficulty=None):
    """
    Get list of question hashes previously asked.
    
    Args:
        session_id: Session identifier
        company: Optional company filter
        difficulty: Optional difficulty filter
    
    Returns:
        List of question hash strings
    """
    with _lock:
        history = _load_history()
    
    key = session_id or 'global'
    entries = history.get(key, [])
    
    # Also include global entries for cross-session dedup
    if key != 'global':
        entries = entries + history.get('global', [])
    
    # Apply filters
    if company:
        entries = [e for e in entries if e.get('company', '').lower() == company.lower()]
    if difficulty:
        entries = [e for e in entries if e.get('difficulty', '').lower() == difficulty.lower()]
    
    return [e['question_hash'] for e in entries]

def get_asked_previews(session_id, company=None, limit=20):
    """
    Get human-readable previews of previously asked questions.
    Used to inject into AI prompts for deduplication.
    
    Returns:
        List of question preview strings (first 100 chars of each)
    """
    with _lock:
        history = _load_history()
    
    key = session_id or 'global'
    entries = history.get(key, [])
    
    if key != 'global':
        entries = entries + history.get('global', [])
    
    if company:
        entries = [e for e in entries if e.get('company', '').lower() == company.lower()]
    
    # Return most recent previews
    previews = [e.get('question_preview', '') for e in entries[-limit:]]
    return [p for p in previews if p]

def is_duplicate(session_id, question_text):
    """
    Check if a question has already been asked via exact hash or embedding semantic similarity.
    
    Returns:
        True if duplicate/semantically similar, False if new
    """
    if not question_text:
        return True

    # 1. Exact SHA-256 hash check
    q_hash = _hash_question(question_text)
    asked_hashes = get_asked_hashes(session_id)
    if q_hash in asked_hashes:
        return True

    # 2. Embedding / Cosine Semantic Similarity check against recent asked previews
    previews = get_asked_previews(session_id, limit=15)
    if previews:
        from services.interview_memory import is_semantically_similar
        for prev in previews:
            if is_semantically_similar(question_text, prev, threshold=0.75):
                return True

    return False

def clear_history(session_id=None):
    """
    Clear question history for a session or all sessions.
    """
    with _lock:
        if session_id:
            history = _load_history()
            history.pop(session_id, None)
            _save_history(history)
        else:
            _save_history({})
