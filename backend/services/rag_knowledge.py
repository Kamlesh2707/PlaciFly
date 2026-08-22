import math

# Cache for embeddings to avoid redundant API calls
_embedding_cache = {}

KNOWLEDGE_CHUNKS = {
    "rate_limiting": {
        "title": "Rate Limiting",
        "concepts": ["Token Bucket", "Leaky Bucket", "Fixed Window Counter", "Sliding Window Log", "Sliding Window Counter"],
        "facts": [
            "Rate limiting controls the rate of traffic sent or received by a network interface controller.",
            "It is used to prevent DoS attacks and limit web scraping.",
            "Helps in controlling resource utilization and managing quotas."
        ],
        "expected_keywords": ["throttling", "tokens", "requests", "API", "quotas", "DDoS", "window"],
        "common_mistakes": [
            "Confusing rate limiting with load balancing.",
            "Assuming fixed window is strictly better than sliding window."
        ]
    },
    "jwt_authentication": {
        "title": "JWT Authentication",
        "concepts": ["Header", "Payload", "Signature", "Symmetric Encryption", "Asymmetric Encryption", "Claims"],
        "facts": [
            "JWT is a standard for creating data with optional signature and/or optional encryption whose payload holds JSON.",
            "It is stateless, meaning the server does not need to keep track of the tokens.",
            "Contains three parts: header, payload, and signature separated by dots."
        ],
        "expected_keywords": ["JSON", "token", "stateless", "bearer", "authorization", "secret", "verify"],
        "common_mistakes": [
            "Storing sensitive data like passwords in the JWT payload.",
            "Not verifying the signature on the backend."
        ]
    },
    "database_indexing": {
        "title": "Database Indexing",
        "concepts": ["B-Trees", "Hash Indexes", "Primary Key", "Clustered Index", "Non-clustered Index"],
        "facts": [
            "Indexing improves the speed of data retrieval operations on a database table.",
            "It comes at the cost of additional writes and storage space to maintain the index.",
            "B-trees are commonly used for range queries."
        ],
        "expected_keywords": ["lookup", "B-tree", "performance", "read", "write penalty", "pointer", "optimization"],
        "common_mistakes": [
            "Indexing every column to make reads faster, ignoring write degradation.",
            "Assuming indexes are always used by the query optimizer."
        ]
    },
    "database_sharding": {
        "title": "Database Sharding",
        "concepts": ["Horizontal Partitioning", "Shard Key", "Consistent Hashing", "Data Distribution", "Rebalancing"],
        "facts": [
            "Sharding is horizontal partitioning of data across multiple databases.",
            "A shard key determines which partition a given row of data belongs to.",
            "Helps in scaling databases horizontally."
        ],
        "expected_keywords": ["horizontal scaling", "partitioning", "shard key", "distribution", "nodes", "scale out"],
        "common_mistakes": [
            "Choosing a shard key with low cardinality.",
            "Ignoring the complexity of cross-shard joins and transactions."
        ]
    },
    "microservices_vs_monolith": {
        "title": "Microservices vs Monolithic Architecture",
        "concepts": ["Independent Deployability", "Coupling", "Service Discovery", "API Gateway", "Monolith"],
        "facts": [
            "Microservices are independently deployable and scalable services.",
            "Monoliths are single, unified units of deployment.",
            "Microservices introduce network latency and operational complexity."
        ],
        "expected_keywords": ["decoupled", "independent", "scalability", "complexity", "domain", "RPC", "latency"],
        "common_mistakes": [
            "Believing microservices are always better than monoliths.",
            "Ignoring the complexity of distributed transactions."
        ]
    },
    "rest_api_design": {
        "title": "REST API Design",
        "concepts": ["Statelessness", "Resources", "URIs", "HATEOAS", "Idempotency"],
        "facts": [
            "REST stands for Representational State Transfer.",
            "Resources are identified by URIs and manipulated using HTTP methods.",
            "A RESTful API should be stateless."
        ],
        "expected_keywords": ["resource", "URI", "stateless", "JSON", "CRUD", "methods", "endpoints"],
        "common_mistakes": [
            "Using verbs instead of nouns in URIs (e.g., /getUsers instead of /users).",
            "Not using HTTP status codes correctly."
        ]
    },
    "oauth2": {
        "title": "OAuth 2.0",
        "concepts": ["Authorization Code Flow", "Access Token", "Refresh Token", "Client ID", "Scopes"],
        "facts": [
            "OAuth2 is an authorization framework, not an authentication protocol.",
            "It allows third-party applications to grant limited access to an HTTP service.",
            "Uses access tokens to authorize requests."
        ],
        "expected_keywords": ["authorization", "delegation", "token", "grant type", "client", "scope", "redirect"],
        "common_mistakes": [
            "Confusing OAuth2 (authorization) with OpenID Connect (authentication).",
            "Leaking the client secret in frontend applications."
        ]
    },
    "caching_strategies": {
        "title": "Caching Strategies",
        "concepts": ["Cache Aside", "Read Through", "Write Through", "Write Behind", "Eviction Policies (LRU, LFU)"],
        "facts": [
            "Caching reduces latency and load on the primary data store.",
            "Cache invalidation is a difficult problem in computer science.",
            "Eviction policies determine which items to remove when the cache is full."
        ],
        "expected_keywords": ["Redis", "Memcached", "latency", "hit rate", "stale data", "TTL", "invalidation"],
        "common_mistakes": [
            "Caching everything without considering the hit/miss ratio.",
            "Ignoring cache stampede or thundering herd problems."
        ]
    },
    "load_balancing": {
        "title": "Load Balancing",
        "concepts": ["Round Robin", "Least Connections", "Session Persistence (Sticky Sessions)", "Layer 4 vs Layer 7", "Health Checks"],
        "facts": [
            "Load balancing distributes incoming network traffic across multiple servers.",
            "It increases availability and reliability.",
            "Health checks ensure traffic is only routed to healthy instances."
        ],
        "expected_keywords": ["distribution", "availability", "proxy", "servers", "traffic", "algorithm", "scaling"],
        "common_mistakes": [
            "Using sticky sessions inappropriately leading to uneven load.",
            "Not implementing health checks for backend servers."
        ]
    },
    "message_queues": {
        "title": "Message Queues",
        "concepts": ["Producer-Consumer", "Pub/Sub", "Asynchronous Processing", "Message Broker", "At-least-once Delivery"],
        "facts": [
            "Message queues facilitate asynchronous communication between services.",
            "They help in decoupling components and smoothing out traffic spikes.",
            "Kafka, RabbitMQ, and SQS are common examples."
        ],
        "expected_keywords": ["asynchronous", "decoupling", "broker", "Kafka", "RabbitMQ", "topics", "events"],
        "common_mistakes": [
            "Assuming message delivery is always exactly-once.",
            "Using queues for synchronous request-response flows."
        ]
    },
    "oop_principles": {
        "title": "Object-Oriented Programming Principles",
        "concepts": ["Encapsulation", "Abstraction", "Inheritance", "Polymorphism", "Classes and Objects"],
        "facts": [
            "Encapsulation hides the internal state of an object.",
            "Inheritance allows a class to inherit properties from another.",
            "Polymorphism allows objects of different types to be treated uniformly."
        ],
        "expected_keywords": ["class", "object", "hide", "extend", "override", "interface", "behavior"],
        "common_mistakes": [
            "Favoring deep inheritance hierarchies over composition.",
            "Exposing internal state by making all fields public."
        ]
    },
    "solid_principles": {
        "title": "SOLID Principles",
        "concepts": ["Single Responsibility", "Open-Closed", "Liskov Substitution", "Interface Segregation", "Dependency Inversion"],
        "facts": [
            "SOLID is an acronym for five design principles intended to make software designs more understandable and maintainable.",
            "Single Responsibility states a class should have one reason to change.",
            "Dependency Inversion favors depending on abstractions, not concretions."
        ],
        "expected_keywords": ["maintainability", "decoupling", "interfaces", "abstraction", "responsibility", "extend"],
        "common_mistakes": [
            "Applying SOLID principles dogmatically everywhere, overcomplicating simple code.",
            "Violating Liskov Substitution by throwing unexpected exceptions in subclasses."
        ]
    },
    "design_patterns": {
        "title": "Design Patterns",
        "concepts": ["Creational (Singleton, Factory)", "Structural (Adapter, Decorator)", "Behavioral (Observer, Strategy)", "Anti-patterns"],
        "facts": [
            "Design patterns are typical solutions to common problems in software design.",
            "Singleton ensures a class has only one instance.",
            "Observer defines a one-to-many dependency between objects."
        ],
        "expected_keywords": ["solution", "reusable", "Singleton", "Factory", "Observer", "architecture", "pattern"],
        "common_mistakes": [
            "Overusing the Singleton pattern leading to global state issues.",
            "Using a design pattern when a simple function would suffice."
        ]
    },
    "sql_joins": {
        "title": "SQL Joins",
        "concepts": ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN", "CROSS JOIN"],
        "facts": [
            "INNER JOIN returns records that have matching values in both tables.",
            "LEFT JOIN returns all records from the left table, and matched records from the right.",
            "CROSS JOIN produces a Cartesian product of the two tables."
        ],
        "expected_keywords": ["tables", "relational", "keys", "foreign key", "intersection", "union", "filter"],
        "common_mistakes": [
            "Confusing LEFT JOIN with INNER JOIN.",
            "Accidentally creating a CROSS JOIN by omitting the ON clause."
        ]
    },
    "sql_normalization": {
        "title": "SQL Normalization",
        "concepts": ["1NF", "2NF", "3NF", "BCNF", "Denormalization"],
        "facts": [
            "Normalization reduces data redundancy and improves data integrity.",
            "1NF requires atomic columns.",
            "3NF requires no transitive dependencies."
        ],
        "expected_keywords": ["redundancy", "anomalies", "atomic", "dependencies", "normal forms", "integrity", "tables"],
        "common_mistakes": [
            "Normalizing to the extreme, leading to poor read performance due to many joins.",
            "Confusing normalization with indexing."
        ]
    },
    "nosql_vs_sql": {
        "title": "NoSQL vs SQL",
        "concepts": ["Relational vs Non-relational", "Schema Flexibility", "ACID vs BASE", "Scaling (Vertical vs Horizontal)", "Document Stores"],
        "facts": [
            "SQL databases use structured query language and have predefined schemas.",
            "NoSQL databases are often document, key-value, graph, or wide-column stores.",
            "SQL typically scales vertically, NoSQL scales horizontally."
        ],
        "expected_keywords": ["schema", "ACID", "relational", "document", "scale", "consistency", "flexibility"],
        "common_mistakes": [
            "Believing NoSQL doesn't support transactions at all.",
            "Thinking NoSQL is always faster than SQL."
        ]
    },
    "tcp_vs_udp": {
        "title": "TCP vs UDP",
        "concepts": ["Connection-oriented", "Connectionless", "Reliability", "Ordering", "Overhead"],
        "facts": [
            "TCP provides reliable, ordered, and error-checked delivery of a stream of octets.",
            "UDP is connectionless and does not guarantee delivery or ordering.",
            "TCP is used for web browsing and email; UDP is used for streaming and gaming."
        ],
        "expected_keywords": ["handshake", "reliable", "packets", "datagrams", "latency", "retransmission", "protocol"],
        "common_mistakes": [
            "Assuming UDP is inherently more secure than TCP.",
            "Using TCP for real-time video streaming where slight packet loss is acceptable."
        ]
    },
    "http_methods": {
        "title": "HTTP Methods",
        "concepts": ["GET", "POST", "PUT", "PATCH", "DELETE", "Idempotency", "Safe Methods"],
        "facts": [
            "GET is used to request data and should be safe (no side effects).",
            "PUT replaces the target resource, while PATCH applies partial modifications.",
            "PUT, DELETE, and GET are idempotent methods."
        ],
        "expected_keywords": ["verb", "idempotent", "safe", "CRUD", "request", "payload", "REST"],
        "common_mistakes": [
            "Using GET requests to modify data on the server.",
            "Confusing PUT and PATCH semantics."
        ]
    },
    "dns_resolution": {
        "title": "DNS Resolution",
        "concepts": ["Root Server", "TLD Server", "Authoritative Name Server", "A Record", "CNAME"],
        "facts": [
            "DNS translates human-readable domain names into IP addresses.",
            "Resolution involves querying a recursive resolver which contacts other servers.",
            "DNS records are cached at various levels to speed up resolution."
        ],
        "expected_keywords": ["domain", "IP", "resolver", "cache", "records", "query", "nameserver"],
        "common_mistakes": [
            "Assuming DNS changes propagate instantly worldwide.",
            "Confusing A records with CNAME records."
        ]
    },
    "ssl_tls": {
        "title": "SSL/TLS",
        "concepts": ["Handshake", "Symmetric Encryption", "Asymmetric Encryption", "Certificates", "Certificate Authorities"],
        "facts": [
            "TLS encrypts data in transit to provide privacy and data integrity.",
            "The handshake uses asymmetric encryption to securely exchange a symmetric key.",
            "Certificates verify the identity of the server."
        ],
        "expected_keywords": ["encryption", "security", "HTTPS", "keys", "handshake", "cipher", "public key"],
        "common_mistakes": [
            "Believing SSL is the current standard (TLS replaced it).",
            "Assuming self-signed certificates provide the same trust as CA-signed ones."
        ]
    },
    "binary_search": {
        "title": "Binary Search",
        "concepts": ["Divide and Conquer", "Sorted Array", "Time Complexity O(log n)", "Midpoint Calculation"],
        "facts": [
            "Binary search requires the target array to be sorted.",
            "It works by repeatedly dividing the search interval in half.",
            "The time complexity is O(log n)."
        ],
        "expected_keywords": ["sorted", "divide", "logarithmic", "mid", "search", "array", "pointer"],
        "common_mistakes": [
            "Attempting to use binary search on an unsorted array.",
            "Causing integer overflow when calculating the midpoint."
        ]
    },
    "sorting_algorithms": {
        "title": "Sorting Algorithms",
        "concepts": ["Quick Sort", "Merge Sort", "Bubble Sort", "Time Complexity", "Space Complexity"],
        "facts": [
            "Merge sort is a stable, divide-and-conquer algorithm with O(n log n) time complexity.",
            "Quick sort has an average time complexity of O(n log n) but O(n^2) worst-case.",
            "Bubble sort is inefficient for large datasets."
        ],
        "expected_keywords": ["sort", "divide and conquer", "pivot", "stable", "O(n log n)", "inplace", "comparisons"],
        "common_mistakes": [
            "Believing bubble sort is practical for production use.",
            "Forgetting that standard quick sort is not stable."
        ]
    },
    "hash_tables": {
        "title": "Hash Tables",
        "concepts": ["Hash Function", "Collisions", "Chaining", "Open Addressing", "Load Factor"],
        "facts": [
            "Hash tables provide average O(1) time complexity for search, insert, and delete.",
            "A hash function maps keys to indices in an array.",
            "Collisions happen when two keys hash to the same index and must be handled."
        ],
        "expected_keywords": ["hash", "O(1)", "collision", "chaining", "key-value", "dictionary", "map"],
        "common_mistakes": [
            "Assuming hash tables always have O(1) worst-case performance.",
            "Using a poor hash function leading to many collisions."
        ]
    },
    "linked_lists": {
        "title": "Linked Lists",
        "concepts": ["Nodes", "Pointers", "Singly Linked", "Doubly Linked", "Head and Tail"],
        "facts": [
            "A linked list consists of nodes where each node points to the next.",
            "Insertion and deletion at the beginning are O(1).",
            "Random access is O(n) because you must traverse from the head."
        ],
        "expected_keywords": ["node", "pointer", "next", "O(1) insert", "traversal", "head", "null"],
        "common_mistakes": [
            "Losing the head pointer when manipulating the list.",
            "Assuming linked lists have better cache locality than arrays."
        ]
    },
    "trees_and_graphs": {
        "title": "Trees and Graphs",
        "concepts": ["Binary Tree", "Binary Search Tree", "Directed/Undirected", "BFS", "DFS"],
        "facts": [
            "A tree is an acyclic connected graph.",
            "In a BST, the left child is smaller and the right child is larger than the parent.",
            "BFS uses a queue, while DFS uses a stack or recursion."
        ],
        "expected_keywords": ["root", "edge", "vertex", "traversal", "acyclic", "search", "depth"],
        "common_mistakes": [
            "Confusing a binary tree with a binary search tree.",
            "Not handling cycles when performing DFS/BFS on a graph."
        ]
    },
    "dynamic_programming": {
        "title": "Dynamic Programming",
        "concepts": ["Memoization", "Tabulation", "Overlapping Subproblems", "Optimal Substructure"],
        "facts": [
            "DP solves complex problems by breaking them down into simpler subproblems.",
            "Memoization is top-down caching of results.",
            "Tabulation is a bottom-up approach to solving subproblems."
        ],
        "expected_keywords": ["cache", "state", "subproblem", "optimization", "fibonacci", "bottom-up", "top-down"],
        "common_mistakes": [
            "Trying to apply DP to problems without overlapping subproblems.",
            "Forgetting to initialize base cases."
        ]
    },
    "recursion": {
        "title": "Recursion",
        "concepts": ["Base Case", "Recursive Case", "Call Stack", "Stack Overflow", "Tail Recursion"],
        "facts": [
            "Recursion involves a function calling itself.",
            "A base case is required to prevent infinite loops.",
            "Deep recursion can lead to a stack overflow error."
        ],
        "expected_keywords": ["self-reference", "base case", "stack", "unwinding", "infinite", "memory", "function"],
        "common_mistakes": [
            "Missing the base case.",
            "Not returning the result of the recursive call."
        ]
    },
    "big_o_notation": {
        "title": "Big O Notation",
        "concepts": ["Time Complexity", "Space Complexity", "Worst Case", "O(1)", "O(n)", "O(n^2)"],
        "facts": [
            "Big O notation describes the limiting behavior of a function when the argument tends towards a particular value or infinity.",
            "It abstracts away constant factors.",
            "It is used to compare the efficiency of algorithms."
        ],
        "expected_keywords": ["complexity", "asymptotic", "growth", "performance", "bounds", "constant", "linear"],
        "common_mistakes": [
            "Including constants in Big O notation (e.g., O(2n) instead of O(n)).",
            "Confusing worst-case time complexity with average-case."
        ]
    },
    "multithreading": {
        "title": "Multithreading",
        "concepts": ["Threads", "Concurrency", "Locks/Mutexes", "Deadlock", "Race Conditions"],
        "facts": [
            "Multithreading allows concurrent execution of parts of a program.",
            "Race conditions occur when threads access shared data concurrently without synchronization.",
            "A deadlock happens when two or more threads wait indefinitely for each other to release resources."
        ],
        "expected_keywords": ["parallel", "concurrent", "synchronization", "shared memory", "thread", "blocking", "mutex"],
        "common_mistakes": [
            "Assuming multithreading always improves performance.",
            "Using locks everywhere, leading to deadlocks or poor performance."
        ]
    },
    "docker_containers": {
        "title": "Docker Containers",
        "concepts": ["Images", "Containers", "Dockerfile", "Isolation", "Volumes"],
        "facts": [
            "Containers package code and dependencies together.",
            "They share the host OS kernel, making them lightweight compared to VMs.",
            "Docker uses namespaces and cgroups for isolation."
        ],
        "expected_keywords": ["containerization", "image", "lightweight", "portable", "daemon", "registry", "environment"],
        "common_mistakes": [
            "Treating containers as full virtual machines.",
            "Storing persistent data directly inside the container filesystem instead of volumes."
        ]
    }
}

def _get_embedding(text):
    """Get Gemini text embedding with caching."""
    if text in _embedding_cache:
        return _embedding_cache[text]
    try:
        import google.generativeai as genai
        result = genai.embed_content(
            model='models/text-embedding-004',
            content=text,
            task_type='retrieval_document'
        )
        vec = result['embedding']
        _embedding_cache[text] = vec
        return vec
    except Exception as e:
        print(f'Embedding error: {e}')
        return None

def _cosine_sim(v1, v2):
    """Cosine similarity between two vectors."""
    if not v1 or not v2:
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a * a for a in v1))
    mag2 = math.sqrt(sum(b * b for b in v2))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)

def retrieve_relevant_chunks(question_text, top_k=3):
    """
    Given a question, retrieve the top_k most relevant knowledge chunks
    using embedding cosine similarity.
    
    Returns list of dicts: [{topic_key, title, concepts, facts, expected_keywords, similarity_score}]
    """
    q_emb = _get_embedding(question_text)
    if not q_emb:
        # Fallback: keyword matching
        return _keyword_fallback_retrieve(question_text, top_k)
    
    scored = []
    for key, chunk in KNOWLEDGE_CHUNKS.items():
        # Build a summary text for embedding
        chunk_text = f"{chunk['title']}. {'. '.join(chunk['concepts'][:5])}. {'. '.join(chunk['facts'][:3])}"
        c_emb = _get_embedding(chunk_text)
        sim = _cosine_sim(q_emb, c_emb)
        scored.append({
            'topic_key': key,
            'title': chunk['title'],
            'concepts': chunk['concepts'],
            'facts': chunk['facts'],
            'expected_keywords': chunk['expected_keywords'],
            'common_mistakes': chunk.get('common_mistakes', []),
            'similarity_score': round(sim, 4)
        })
    
    scored.sort(key=lambda x: x['similarity_score'], reverse=True)
    return scored[:top_k]

def _keyword_fallback_retrieve(question_text, top_k=3):
    """Fallback retrieval using keyword overlap when embeddings fail."""
    q_lower = question_text.lower()
    scored = []
    for key, chunk in KNOWLEDGE_CHUNKS.items():
        score = 0
        all_keywords = chunk['expected_keywords'] + chunk['concepts']
        for kw in all_keywords:
            if kw.lower() in q_lower:
                score += 1
        scored.append({
            'topic_key': key,
            'title': chunk['title'],
            'concepts': chunk['concepts'],
            'facts': chunk['facts'],
            'expected_keywords': chunk['expected_keywords'],
            'common_mistakes': chunk.get('common_mistakes', []),
            'similarity_score': score / max(len(all_keywords), 1)
        })
    scored.sort(key=lambda x: x['similarity_score'], reverse=True)
    return scored[:top_k]

def get_expected_concepts(question_text):
    """
    Returns the combined list of expected concepts/keywords from
    the top 2 most relevant knowledge chunks for the question.
    """
    chunks = retrieve_relevant_chunks(question_text, top_k=2)
    concepts = []
    for c in chunks:
        concepts.extend(c['concepts'])
        concepts.extend(c['expected_keywords'])
    return list(set(concepts))

def compute_answer_relevance(question_text, answer_text):
    """
    Compute embedding cosine similarity between question and answer.
    Returns float 0.0-1.0. Below 0.30 = off-topic.
    """
    q_emb = _get_embedding(question_text)
    a_emb = _get_embedding(answer_text)
    if not q_emb or not a_emb:
        return _keyword_relevance_fallback(question_text, answer_text)
    return round(_cosine_sim(q_emb, a_emb), 4)

def _keyword_relevance_fallback(question_text, answer_text):
    """Fallback relevance using keyword overlap."""
    q_words = set(question_text.lower().split())
    a_words = set(answer_text.lower().split())
    overlap = q_words.intersection(a_words)
    if len(q_words) == 0:
        return 0.0
    return round(len(overlap) / len(q_words), 4)

def grade_factual_accuracy(answer_text, retrieved_chunks):
    """
    Check what percentage of expected concepts from retrieved chunks
    appear in the answer.
    
    Returns dict: {accuracy_pct, matched_concepts, missing_concepts, total_expected}
    """
    answer_lower = answer_text.lower()
    all_expected = []
    for chunk in retrieved_chunks:
        all_expected.extend(chunk.get('expected_keywords', []))
        all_expected.extend(chunk.get('concepts', []))
    
    unique_expected = list(set(kw.lower() for kw in all_expected))
    matched = [kw for kw in unique_expected if kw in answer_lower]
    missing = [kw for kw in unique_expected if kw not in answer_lower]
    
    accuracy = round(len(matched) / max(len(unique_expected), 1) * 100, 1)
    
    return {
        'accuracy_pct': accuracy,
        'matched_concepts': matched[:10],
        'missing_concepts': missing[:10],
        'total_expected': len(unique_expected)
    }

def check_common_mistakes(answer_text, retrieved_chunks):
    """
    Check if the answer contains any common misconceptions.
    Returns list of detected mistake strings.
    """
    answer_lower = answer_text.lower()
    detected = []
    for chunk in retrieved_chunks:
        for mistake in chunk.get('common_mistakes', []):
            # Check if the mistake concept appears in the answer
            mistake_keywords = [w for w in mistake.lower().split() if len(w) > 4]
            match_count = sum(1 for kw in mistake_keywords if kw in answer_lower)
            if match_count >= len(mistake_keywords) * 0.6:
                detected.append(mistake)
    return detected[:5]
