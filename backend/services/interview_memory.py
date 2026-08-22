import re
import math
import google.generativeai as genai
from config import Config

# Key technical concepts dictionary for instant extraction
TECH_KEYWORDS = {
    "redis", "kafka", "jwt", "oauth", "docker", "kubernetes", "aws", "s3", "dynamodb",
    "postgresql", "mysql", "mongodb", "b-tree", "sharding", "index", "indexing",
    "microservices", "monolith", "spring boot", "react", "graphql", "rest", "grpc",
    "circuit breaker", "rate limiter", "load balancer", "cache", "caching", "lru",
    "concurrency", "deadlock", "multithreading", "async", "event loop", "guesstimate",
    "star framework", "mece", "sliding window", "two pointers", "binary search",
    "trie", "dp", "dynamic programming", "dfs", "bfs", "flask", "django", "node.js"
}

# ==============================================================================
# 1. CONCEPT EXTRACTOR & MEMORY GRAPH
# Extract candidate claims and maintain rolling conversation state
# ==============================================================================

def extract_concepts_from_answer(candidate_answer):
    """Extract technical keywords, tools, and frameworks mentioned by the candidate."""
    if not candidate_answer:
        return []
    
    clean_text = candidate_answer.lower()
    words = set(re.findall(r'\b[a-z0-9\.\_\-]+\b', clean_text))
    found = [w for w in words if w in TECH_KEYWORDS]

    # Also check multi-word phrases
    phrases = ["binary search", "sliding window", "circuit breaker", "rate limiter", "load balancer", "spring boot", "event loop"]
    for p in phrases:
        if p in clean_text and p not in found:
            found.append(p)
            
    return found

class InterviewSessionMemory:
    """
    Manages structured memory for an ongoing interview session.
    Keeps context lean and focused: Conversation Summary + Last 3 Turns + Concept Graph + Weak Topics.
    """
    def __init__(self, session_id, company="TCS", difficulty="Medium"):
        self.session_id = session_id
        self.company = company
        self.difficulty = difficulty
        self.concepts_used = set()
        self.weak_topics = []
        self.strong_topics = []
        self.turns = []  # [{question, answer, score, topic}]
        self.conversation_summary = f"Interview initialized for {company} at {difficulty} level."

    def add_turn(self, question, answer, score=70, topic="General Technical", evaluation_result=None):
        # Extract concepts from answer
        new_concepts = extract_concepts_from_answer(answer)
        for c in new_concepts:
            self.concepts_used.add(c)

        # Update strengths & weaknesses
        if score < 60 and topic and topic not in self.weak_topics:
            self.weak_topics.append(topic)
        elif score >= 80 and topic and topic not in self.strong_topics:
            self.strong_topics.append(topic)

        # Store turn
        turn_entry = {
            "turn_num": len(self.turns) + 1,
            "question": question,
            "answer": answer[:300],  # Lean snippet
            "score": score,
            "topic": topic
        }
        self.turns.append(turn_entry)

        # Keep rolling summary updated
        self._update_summary()

    def _update_summary(self):
        turn_count = len(self.turns)
        if turn_count == 0:
            return

        last_scores = [t['score'] for t in self.turns]
        avg_score = sum(last_scores) / len(last_scores)
        
        weak_str = ", ".join(self.weak_topics[-3:]) if self.weak_topics else "None identified yet"
        strong_str = ", ".join(self.strong_topics[-3:]) if self.strong_topics else "General knowledge"
        concepts_str = ", ".join(list(self.concepts_used)[:6]) if self.concepts_used else "Standard interview answers"

        self.conversation_summary = (
            f"Completed {turn_count} turn(s) with average score {avg_score:.1f}/100. "
            f"Candidate claims experience with: {concepts_str}. "
            f"Strengths: {strong_str}. Weak areas needing follow-up: {weak_str}."
        )

    def get_prompt_context(self):
        """Build lean, structured context for Gemini AI prompts."""
        last_3 = self.turns[-3:]
        history_snippet = []
        for t in last_3:
            history_snippet.append(f"Turn {t['turn_num']} ({t['topic']}, Score: {t['score']}/100):\n  Q: {t['question']}\n  A: {t['answer']}")

        return {
            "conversation_summary": self.conversation_summary,
            "concepts_used": list(self.concepts_used),
            "weak_topics": self.weak_topics,
            "strong_topics": self.strong_topics,
            "current_difficulty": self.difficulty,
            "last_3_turns": "\n\n".join(history_snippet) if history_snippet else "First turn of session."
        }

# Global session memory store
_session_memories = {}

def get_or_create_memory(session_id, company="TCS", difficulty="Medium"):
    if not session_id or session_id == "global":
        session_id = f"session-default-{company.lower()}"
        
    if session_id not in _session_memories:
        _session_memories[session_id] = InterviewSessionMemory(session_id, company, difficulty)
    return _session_memories[session_id]

# ==============================================================================
# 2. EMBEDDING-BASED SEMANTIC DEDUPLICATION
# Uses Gemini Embeddings / Cosine Similarity to detect semantic question overlap
# ==============================================================================

def _cosine_similarity(vec1, vec2):
    """Compute cosine similarity between two float vectors."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

def _word_ngram_vector(text, n=2):
    """Fallback n-gram vector generator for offline cosine similarity."""
    words = re.findall(r'\b[a-z0-9]+\b', text.lower())
    grams = {}
    for i in range(len(words) - n + 1):
        g = " ".join(words[i:i+n])
        grams[g] = grams.get(g, 0) + 1
    return grams

def _ngram_cosine_similarity(text1, text2):
    v1 = _word_ngram_vector(text1, n=2)
    v2 = _word_ngram_vector(text2, n=2)
    all_keys = set(v1.keys()).union(set(v2.keys()))
    if not all_keys:
        return 0.0
    vec1 = [v1.get(k, 0) for k in all_keys]
    vec2 = [v2.get(k, 0) for k in all_keys]
    return _cosine_similarity(vec1, vec2)

def get_text_embedding(text):
    """Generate vector embedding using Gemini API if configured, or return None."""
    if Config.GEMINI_API_KEY:
        try:
            res = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            return res.get('embedding', [])
        except Exception as e:
            pass
    return None

def is_semantically_similar(text1, text2, threshold=0.82):
    """
    Check if two question texts are semantically similar (>0.82 cosine similarity).
    Uses Gemini text-embedding-004 if available, or n-gram vector cosine similarity.
    """
    if not text1 or not text2:
        return False
    
    t1_norm = text1.strip().lower()
    t2_norm = text2.strip().lower()

    if t1_norm == t2_norm:
        return True

    emb1 = get_text_embedding(t1_norm)
    emb2 = get_text_embedding(t2_norm)

    if emb1 and emb2:
        sim = _cosine_similarity(emb1, emb2)
        return sim >= threshold
    
    # Fallback to n-gram vector similarity
    sim = _ngram_cosine_similarity(t1_norm, t2_norm)
    return sim >= 0.65

def compute_relevance_score(question_text, answer_text):
    """
    Compute embedding-based relevance between question and answer.
    Returns float 0.0-1.0. Below 0.30 = off-topic.
    """
    q_emb = get_text_embedding(question_text)
    a_emb = get_text_embedding(answer_text)
    if q_emb and a_emb:
        return round(_cosine_similarity(q_emb, a_emb), 4)
    # Fallback to n-gram similarity
    return round(_ngram_cosine_similarity(question_text, answer_text), 4)
