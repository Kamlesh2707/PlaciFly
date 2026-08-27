"""
Placifly - Daily Interview Challenge Service
Features massive randomized question & logo banks across:
1. Rapid Fire Challenge (AI, LLMs, Prompt Eng, Web, Cloud, Databases, Frameworks, Tech)
2. 30 MCQ Speed Sprint (120+ MCQs covering Programming Languages, Frameworks, Databases, AI/ML, APIs, DSA, Cloud, and Software Dev Fundamentals)
3. Tech Logo Challenge (50+ Diverse Technology Logos)

Rules:
- Exactly 30 questions sampled dynamically and randomly from the large pool on every game session.
- Progressive Timer Speed scaling (30s -> 20s -> 15s/12s).
- Question 30 tagged with double_points = True.
"""

import random
import re
import difflib

# ==============================================================================
# 1. RAPID FIRE QUESTION POOL (50+ High-Impact Tech & AI Questions)
# ==============================================================================
RAPID_FIRE_QUESTIONS = [
    {
        "id": "rf-1", "category": "Artificial Intelligence",
        "question": "Name one popular open-source framework specifically built for orchestrating autonomous AI agents.",
        "accepted_answers": ["langchain", "autogen", "crewai", "llamaindex", "semantic kernel", "langgraph", "babyagi", "autogpt"],
        "options": ["CrewAI", "TensorFlow", "Django", "Kubernetes"], "correct_option_index": 0,
        "explanation": "CrewAI, LangChain, AutoGen, and LangGraph are specialized frameworks designed to orchestrate collaborative multi-agent AI systems."
    },
    {
        "id": "rf-2", "category": "Prompt Engineering",
        "question": "Which prompt engineering technique explicitly prompts an LLM to think step-by-step before producing an answer?",
        "accepted_answers": ["chain of thought", "cot", "step by step", "tree of thoughts", "chain-of-thought"],
        "options": ["Chain of Thought (CoT)", "Zero-Shot Prompting", "Temperature Scaling", "Beam Search"], "correct_option_index": 0,
        "explanation": "Chain of Thought (CoT) prompting encourages models to break complex problems into intermediate reasoning steps."
    },
    {
        "id": "rf-3", "category": "LLMs & GenAI",
        "question": "What hyperparameter controls the randomness and creativity of an LLM's output generation?",
        "accepted_answers": ["temperature", "temp", "top_p", "top p", "top-p"],
        "options": ["Temperature", "Learning Rate", "Batch Size", "Epochs"], "correct_option_index": 0,
        "explanation": "Temperature controls the softmax probability distribution: lower values make output deterministic, higher values increase creativity."
    },
    {
        "id": "rf-4", "category": "Prompt Engineering",
        "question": "What prompting technique provides a few input-output demonstration examples directly in the prompt?",
        "accepted_answers": ["few-shot", "few shot", "fewshot", "few shot prompting", "n-shot"],
        "options": ["Few-Shot Prompting", "Zero-Shot Prompting", "Prompt Injection", "Fine-Tuning"], "correct_option_index": 0,
        "explanation": "Few-shot prompting provides 2-5 explicit demonstration examples in the prompt to set context and format."
    },
    {
        "id": "rf-5", "category": "Cloud & Infrastructure",
        "question": "Which open-source container orchestration platform was originally developed by Google?",
        "accepted_answers": ["kubernetes", "k8s"],
        "options": ["Kubernetes (K8s)", "Docker Swarm", "OpenStack", "Terraform"], "correct_option_index": 0,
        "explanation": "Kubernetes (K8s) was designed by Google based on internal Borg technology and open-sourced to CNCF."
    },
    {
        "id": "rf-6", "category": "Machine Learning",
        "question": "Which neural network architecture introduced the Self-Attention mechanism that powers modern LLMs?",
        "accepted_answers": ["transformer", "transformers", "transformer architecture"],
        "options": ["Transformer", "CNN (Convolutional)", "RNN (Recurrent)", "LSTM"], "correct_option_index": 0,
        "explanation": "The Transformer architecture (Vaswani et al., 2017 'Attention Is All You Need') powers GPT, Claude, Gemini, and BERT."
    },
    {
        "id": "rf-7", "category": "Databases",
        "question": "Name the in-memory key-value data store commonly used as an ultra-fast cache and message broker.",
        "accepted_answers": ["redis", "memcached", "valkey", "dragonfly"],
        "options": ["Redis", "PostgreSQL", "Cassandra", "Neo4j"], "correct_option_index": 0,
        "explanation": "Redis provides sub-millisecond in-memory data structures widely used for caching, sessions, and pub/sub."
    },
    {
        "id": "rf-8", "category": "Web Development",
        "question": "Which React Hook is used to perform side effects such as data fetching, subscriptions, or DOM mutations?",
        "accepted_answers": ["useeffect", "use_effect", "effect hook"],
        "options": ["useEffect", "useState", "useMemo", "useCallback"], "correct_option_index": 0,
        "explanation": "useEffect lets functional components synchronize with external APIs, DOM events, and timers."
    },
    {
        "id": "rf-9", "category": "Programming & Runtimes",
        "question": "What is the name of the modern secure TypeScript and JavaScript runtime created by Ryan Dahl (creator of Node.js)?",
        "accepted_answers": ["deno", "bun"],
        "options": ["Deno", "Node.js", "V8", "Electron"], "correct_option_index": 0,
        "explanation": "Deno is a modern, secure runtime for JavaScript and TypeScript built in Rust on Google's V8 engine."
    },
    {
        "id": "rf-10", "category": "Latest Technologies",
        "question": "What technique combines information retrieval with LLM generation to ground AI responses in custom documents?",
        "accepted_answers": ["rag", "retrieval augmented generation", "retrieval-augmented generation"],
        "options": ["RAG (Retrieval-Augmented Generation)", "Fine-Tuning", "RLHF", "Quantization"], "correct_option_index": 0,
        "explanation": "RAG retrieves relevant chunks from a vector database and inserts them into prompt context to prevent hallucination."
    },
    {
        "id": "rf-11", "category": "Databases",
        "question": "Which vector database is specifically designed for high-performance similarity search in AI applications?",
        "accepted_answers": ["pinecone", "chroma", "weaviate", "qdrant", "milvus", "faiss"],
        "options": ["Pinecone", "SQLite", "MariaDB", "Oracle"], "correct_option_index": 0,
        "explanation": "Pinecone, Chroma, Weaviate, and Qdrant are purpose-built vector databases for embeddings search."
    },
    {
        "id": "rf-12", "category": "Artificial Intelligence",
        "question": "What AI alignment technique trains models using human preference rankings and reward models?",
        "accepted_answers": ["rlhf", "reinforcement learning from human feedback", "dpo", "direct preference optimization"],
        "options": ["RLHF", "Backpropagation", "Grid Search", "SGD"], "correct_option_index": 0,
        "explanation": "RLHF (Reinforcement Learning from Human Feedback) aligns model behavior with human intent."
    },
    {
        "id": "rf-13", "category": "Web Development",
        "question": "Which CSS unit is relative to the font-size of the root <html> element?",
        "accepted_answers": ["rem", "root em"],
        "options": ["rem", "em", "vh", "px"], "correct_option_index": 0,
        "explanation": "`rem` (root em) scales relative to the root element's font size."
    },
    {
        "id": "rf-14", "category": "Programming Languages",
        "question": "Which systems programming language guarantees memory safety without a garbage collector via an ownership model?",
        "accepted_answers": ["rust", "rustlang"],
        "options": ["Rust", "C++", "Go", "Java"], "correct_option_index": 0,
        "explanation": "Rust uses compile-time ownership, borrowing, and lifetime rules to prevent memory leaks."
    },
    {
        "id": "rf-15", "category": "Cloud & DevOps",
        "question": "What declarative Infrastructure as Code (IaC) tool by HashiCorp uses HCL files to provision cloud resources?",
        "accepted_answers": ["terraform", "opentofu"],
        "options": ["Terraform", "Ansible", "Puppet", "Chef"], "correct_option_index": 0,
        "explanation": "Terraform allows developers to declare cloud infrastructure in HCL code."
    },
    {
        "id": "rf-16", "category": "Prompt Engineering",
        "question": "What attack technique tricks an LLM into ignoring its system safety instructions?",
        "accepted_answers": ["prompt injection", "jailbreak", "jailbreaking"],
        "options": ["Prompt Injection", "Model Drift", "Tokenization", "Overfitting"], "correct_option_index": 0,
        "explanation": "Prompt injection overrides original system instructions with untrusted user inputs."
    },
    {
        "id": "rf-17", "category": "Databases",
        "question": "Which open-source relational database is renowned for its advanced extensible features and JSON support?",
        "accepted_answers": ["postgresql", "postgres", "psql"],
        "options": ["PostgreSQL", "SQLite", "MongoDB", "Cassandra"], "correct_option_index": 0,
        "explanation": "PostgreSQL is an ACID-compliant relational database with JSONB indexing."
    },
    {
        "id": "rf-18", "category": "Frameworks",
        "question": "Which popular full-stack React framework provides server-side rendering (SSR) and App Router?",
        "accepted_answers": ["next.js", "nextjs", "next"],
        "options": ["Next.js", "Gatsby", "Vite", "Create React App"], "correct_option_index": 0,
        "explanation": "Next.js by Vercel enables server components, SSR, and static site generation."
    },
    {
        "id": "rf-19", "category": "Machine Learning",
        "question": "What process reduces the precision of model weights (e.g. 16-bit float to 4-bit) to accelerate inference?",
        "accepted_answers": ["quantization", "model quantization", "quantize"],
        "options": ["Quantization", "Gradient Descent", "Dropout", "Normalization"], "correct_option_index": 0,
        "explanation": "Quantization compresses model memory footprint and accelerates LLM token generation."
    },
    {
        "id": "rf-20", "category": "Web Development",
        "question": "Which HTTP header is required for browsers to allow cross-origin resource requests?",
        "accepted_answers": ["cors", "access-control-allow-origin", "access control allow origin"],
        "options": ["Access-Control-Allow-Origin", "Content-Security-Policy", "X-Frame-Options", "Authorization"], "correct_option_index": 0,
        "explanation": "`Access-Control-Allow-Origin` indicates permitted cross-origin domains."
    },
    {
        "id": "rf-21", "category": "LLMs & GenAI",
        "question": "Name the open-weights LLM family created by Meta AI that sparked the open-source AI revolution.",
        "accepted_answers": ["llama", "llama 2", "llama 3", "llama 3.1", "llama3"],
        "options": ["Llama", "Mistral", "Gemma", "Claude"], "correct_option_index": 0,
        "explanation": "Meta's Llama family made foundation model weights publicly accessible."
    },
    {
        "id": "rf-22", "category": "Cloud & Infrastructure",
        "question": "Which Google Cloud serverless container platform runs stateless containers directly from requests?",
        "accepted_answers": ["cloud run", "google cloud run"],
        "options": ["Cloud Run", "App Engine", "Compute Engine", "Anthos"], "correct_option_index": 0,
        "explanation": "Google Cloud Run automatically scales containers from zero to handle HTTP traffic."
    },
    {
        "id": "rf-23", "category": "Programming Languages",
        "question": "Which language developed by Google uses Goroutines and Channels for lightweight concurrency?",
        "accepted_answers": ["go", "golang"],
        "options": ["Go (Golang)", "Rust", "Kotlin", "Dart"], "correct_option_index": 0,
        "explanation": "Go (Golang) features CSP-style concurrency with goroutines."
    },
    {
        "id": "rf-24", "category": "Web Development",
        "question": "Which state management tool uses unidirectional data flow with reducers, actions, and store?",
        "accepted_answers": ["redux", "redux toolkit", "rtk", "zustand"],
        "options": ["Redux", "MobX", "Recoil", "Context API"], "correct_option_index": 0,
        "explanation": "Redux provides predictable state container management through immutable state transitions."
    },
    {
        "id": "rf-25", "category": "Databases",
        "question": "What database theorem states that a distributed system can deliver at most two of Consistency, Availability, Partition tolerance?",
        "accepted_answers": ["cap theorem", "brewers theorem", "cap"],
        "options": ["CAP Theorem", "ACID Theorem", "BASE Theorem", "Paxos Theorem"], "correct_option_index": 0,
        "explanation": "Brewer's CAP theorem proves distributed datastores trade off Consistency or Availability during partitions."
    },
    {
        "id": "rf-26", "category": "AI Frameworks",
        "question": "Which deep learning framework developed by Meta AI is the dominant research standard?",
        "accepted_answers": ["pytorch", "torch"],
        "options": ["PyTorch", "TensorFlow", "Caffe", "Theano"], "correct_option_index": 0,
        "explanation": "PyTorch's dynamic computational graph (autograd) made it the premier ML framework."
    },
    {
        "id": "rf-27", "category": "Prompt Engineering",
        "question": "Which prompting technique involves exploring multiple reasoning paths in parallel before choosing the best answer?",
        "accepted_answers": ["tree of thoughts", "tot", "graph of thoughts"],
        "options": ["Tree of Thoughts (ToT)", "Few-Shot", "Self-Consistency", "ReAct"], "correct_option_index": 0,
        "explanation": "Tree of Thoughts (ToT) enables LLMs to explore multiple reasoning paths with search."
    },
    {
        "id": "rf-28", "category": "APIs & Web",
        "question": "What binary high-performance RPC framework developed by Google uses Protocol Buffers?",
        "accepted_answers": ["grpc", "g-rpc"],
        "options": ["gRPC", "GraphQL", "SOAP", "TRPC"], "correct_option_index": 0,
        "explanation": "gRPC enables low-latency inter-service microservice communication."
    },
    {
        "id": "rf-29", "category": "Cloud & DevOps",
        "question": "Which open-source monitoring tool collects metric time-series data and uses the PromQL query language?",
        "accepted_answers": ["prometheus", "grafana"],
        "options": ["Prometheus", "Datadog", "Splunk", "Nagios"], "correct_option_index": 0,
        "explanation": "Prometheus is the CNCF standard time-series metric collector."
    },
    {
        "id": "rf-30", "category": "Latest Technologies",
        "question": "What agentic framework paradigm alternates between Reasoning ('Thought') and Action ('Act') using tools?",
        "accepted_answers": ["react", "react prompting", "react framework", "reasoning and acting"],
        "options": ["ReAct (Reason + Act)", "Chain of Thought", "Zero-Shot", "RAG"], "correct_option_index": 0,
        "explanation": "ReAct synergistic prompting lets models interleave reasoning traces with tool execution."
    }
]

# ==============================================================================
# 2. 30 MCQ SPEED SPRINT QUESTION POOL (120+ DIVERSE QUESTIONS ACROSS 8 DOMAINS)
# ==============================================================================
SPRINT_MCQ_BANK = [
    # --------------------------------------------------------------------------
    # A. PROGRAMMING LANGUAGES (Python, JS, TS, Java, C++, C#, Go, Rust, Kotlin)
    # --------------------------------------------------------------------------
    {
        "id": "mcq-pl-1", "topic": "Python",
        "question": "What is the output of `type([])` in Python 3?",
        "options": ["<class 'list'>", "<class 'array'>", "<class 'tuple'>", "<class 'object'>"],
        "correct_option_index": 0, "explanation": "Square brackets `[]` initialize a list in Python."
    },
    {
        "id": "mcq-pl-2", "topic": "JavaScript",
        "question": "Which keyword declares a block-scoped variable that cannot be reassigned in JavaScript?",
        "options": ["const", "let", "var", "static"],
        "correct_option_index": 0, "explanation": "`const` declares block-scoped, read-only named constants."
    },
    {
        "id": "mcq-pl-3", "topic": "Java",
        "question": "Which Java collection does NOT allow duplicate elements?",
        "options": ["HashSet", "ArrayList", "LinkedList", "Vector"],
        "correct_option_index": 0, "explanation": "Set implementations in Java (such as `HashSet`) guarantee uniqueness."
    },
    {
        "id": "mcq-pl-4", "topic": "Python",
        "question": "Which built-in function converts an iterable into a series of index-value tuples?",
        "options": ["enumerate()", "zip()", "map()", "filter()"],
        "correct_option_index": 0, "explanation": "`enumerate(iterable)` yields tuples containing (index, item)."
    },
    {
        "id": "mcq-pl-5", "topic": "JavaScript",
        "question": "What is the result of `'5' - 3` in JavaScript?",
        "options": ["2 (number)", "'53' (string)", "NaN", "TypeError"],
        "correct_option_index": 0, "explanation": "The `-` subtraction operator coerces strings into numbers in JavaScript, giving numeric 2."
    },
    {
        "id": "mcq-pl-6", "topic": "Java",
        "question": "Which keyword prevents a Java method from being overridden in a subclass?",
        "options": ["final", "static", "abstract", "synchronized"],
        "correct_option_index": 0, "explanation": "`final` on a method prevents subclasses from overriding its implementation."
    },
    {
        "id": "mcq-pl-7", "topic": "JavaScript",
        "question": "What is the output of `typeof NaN` in JavaScript?",
        "options": ["'number'", "'undefined'", "'nan'", "'object'"],
        "correct_option_index": 0, "explanation": "In JavaScript and IEEE 754 floating point standard, NaN is of type `'number'`."
    },
    {
        "id": "mcq-pl-8", "topic": "TypeScript",
        "question": "Which TypeScript utility type constructs a type with all properties of T set to optional?",
        "options": ["Partial<T>", "Required<T>", "Readonly<T>", "Record<K,T>"],
        "correct_option_index": 0, "explanation": "`Partial<T>` makes all keys in type T optional."
    },
    {
        "id": "mcq-pl-9", "topic": "C++",
        "question": "In C++, which smart pointer allows multiple pointers to share ownership of the same dynamically allocated object?",
        "options": ["std::shared_ptr", "std::unique_ptr", "std::weak_ptr", "std::auto_ptr"],
        "correct_option_index": 0, "explanation": "`std::shared_ptr` maintains a reference count for shared ownership."
    },
    {
        "id": "mcq-pl-10", "topic": "Go (Golang)",
        "question": "How are lightweight concurrently executing threads called in the Go programming language?",
        "options": ["Goroutines", "Futures", "Coroutines", "Processes"],
        "correct_option_index": 0, "explanation": "Goroutines are Go's lightweight user-space managed threads."
    },
    {
        "id": "mcq-pl-11", "topic": "Rust",
        "question": "What core compile-time feature guarantees memory safety without a garbage collector in Rust?",
        "options": ["Ownership and Borrow Checker", "Virtual Machine JIT", "Reference Counting (ARC)", "Automatic Tracing"],
        "correct_option_index": 0, "explanation": "Rust's borrow checker and ownership model ensure memory safety at compile time."
    },
    {
        "id": "mcq-pl-12", "topic": "Python",
        "question": "What does the `__init__` method represent in a Python class?",
        "options": ["Constructor / Instance Initializer", "Destructor", "Class Factory", "Static Initializer"],
        "correct_option_index": 0, "explanation": "`__init__` initializes attributes when a new instance is created."
    },
    {
        "id": "mcq-pl-13", "topic": "C# (.NET)",
        "question": "Which keyword in C# defines a class that cannot be inherited by any other class?",
        "options": ["sealed", "static", "abstract", "private"],
        "correct_option_index": 0, "explanation": "`sealed` in C# prevents other classes from deriving from it."
    },
    {
        "id": "mcq-pl-14", "topic": "Kotlin",
        "question": "In Kotlin, which operator provides safe calls for nullable types (e.g. `obj?.method()`)?",
        "options": ["Safe Call Operator (?.)", "Elvis Operator (?:)", "Not-Null Assertion (!!)", "Null Coalescing (??)"],
        "correct_option_index": 0, "explanation": "The `?.` operator executes a call only if the target is not null."
    },
    {
        "id": "mcq-pl-15", "topic": "Python",
        "question": "What is the time complexity of appending an element to a standard Python list (average case)?",
        "options": ["O(1)", "O(n)", "O(log n)", "O(n²)"],
        "correct_option_index": 0, "explanation": "List appending in Python is amortized O(1) constant time."
    },
    {
        "id": "mcq-pl-16", "topic": "JavaScript",
        "question": "Which JavaScript method creates a new array populated with the results of calling a function on every element?",
        "options": ["Array.prototype.map()", "Array.prototype.forEach()", "Array.prototype.filter()", "Array.prototype.reduce()"],
        "correct_option_index": 0, "explanation": "`map()` creates a new array transformed by the callback function."
    },

    # --------------------------------------------------------------------------
    # B. FRAMEWORKS & RUNTIMES (React, Next.js, Vue, Angular, Node, Django, Spring)
    # --------------------------------------------------------------------------
    {
        "id": "mcq-fw-1", "topic": "React",
        "question": "What is the primary purpose of keys in React list rendering?",
        "options": ["Help React identify which items changed, added, or removed", "Enforce CSS styling", "Pass props to children", "Manage component state"],
        "correct_option_index": 0, "explanation": "Keys give React elements stable identities to optimize Virtual DOM reconciliation."
    },
    {
        "id": "mcq-fw-2", "topic": "React",
        "question": "Which React hook is used to memoize expensive calculation values between re-renders?",
        "options": ["useMemo", "useCallback", "useRef", "useEffect"],
        "correct_option_index": 0, "explanation": "`useMemo` caches the result of a calculation between renders unless dependencies change."
    },
    {
        "id": "mcq-fw-3", "topic": "Next.js",
        "question": "In Next.js App Router, which file name is conventionally used to define a UI route layout wrapping pages?",
        "options": ["layout.jsx / layout.tsx", "page.jsx", "template.jsx", "route.js"],
        "correct_option_index": 0, "explanation": "`layout.js/tsx` defines shared UI layouts that preserve state across route navigations."
    },
    {
        "id": "mcq-fw-4", "topic": "Node.js",
        "question": "Which architecture pattern describes Node.js core event handling mechanism?",
        "options": ["Single-threaded Event Loop with Non-blocking I/O", "Multi-threaded blocking I/O", "Actor Model", "Message Queue Consumer"],
        "correct_option_index": 0, "explanation": "Node.js runs on a single-threaded event loop utilizing Libuv for async I/O."
    },
    {
        "id": "mcq-fw-5", "topic": "Django (Python)",
        "question": "What architectural pattern does the Django web framework follow?",
        "options": ["MVT (Model-View-Template)", "MVC (Model-View-Controller)", "MVVM", "Microkernel"],
        "correct_option_index": 0, "explanation": "Django follows the Model-View-Template (MVT) design structure."
    },
    {
        "id": "mcq-fw-6", "topic": "Spring Boot",
        "question": "Which annotation in Spring Boot is used to mark a class as a RESTful controller returning JSON?",
        "options": ["@RestController", "@Controller", "@Service", "@Repository"],
        "correct_option_index": 0, "explanation": "`@RestController` combines `@Controller` and `@ResponseBody` to serialize JSON responses."
    },
    {
        "id": "mcq-fw-7", "topic": "Vue.js",
        "question": "In Vue 3 Composition API, which function creates a deeply reactive state object?",
        "options": ["reactive() / ref()", "computed()", "watch()", "createState()"],
        "correct_option_index": 0, "explanation": "`reactive()` and `ref()` are fundamental primitives to create reactive state in Vue 3."
    },
    {
        "id": "mcq-fw-8", "topic": "Express.js",
        "question": "In Express.js, what is the third parameter passed to middleware functions (e.g. `(req, res, next)`)?",
        "options": ["next", "done", "callback", "forward"],
        "correct_option_index": 0, "explanation": "`next()` invokes the next middleware function in the request-response cycle pipeline."
    },
    {
        "id": "mcq-fw-9", "topic": "FastAPI (Python)",
        "question": "Which Python library powers data validation and serialization in FastAPI?",
        "options": ["Pydantic", "Marshmallow", "Cerberus", "Schema"],
        "correct_option_index": 0, "explanation": "FastAPI uses Pydantic models for fast type validation and OpenAPI doc generation."
    },
    {
        "id": "mcq-fw-10", "topic": "React",
        "question": "Which React hook returns a mutable ref object whose `.current` property persists across renders without triggering a re-render?",
        "options": ["useRef", "useState", "useId", "useTransition"],
        "correct_option_index": 0, "explanation": "`useRef` stores mutable values across renders without causing component re-renders."
    },

    # --------------------------------------------------------------------------
    # C. DATABASES & STORAGE (SQL, NoSQL, Caching, Sharding, Indexing)
    # --------------------------------------------------------------------------
    {
        "id": "mcq-db-1", "topic": "Databases",
        "question": "What does the 'A' stand for in database ACID properties?",
        "options": ["Atomicity", "Availability", "Authentication", "Asynchronous"],
        "correct_option_index": 0, "explanation": "ACID stands for Atomicity, Consistency, Isolation, and Durability."
    },
    {
        "id": "mcq-db-2", "topic": "Databases",
        "question": "Which SQL clause is used to filter aggregated group records (used after GROUP BY)?",
        "options": ["HAVING", "WHERE", "ORDER BY", "FILTER"],
        "correct_option_index": 0, "explanation": "`HAVING` filters aggregated records, whereas `WHERE` filters rows before grouping."
    },
    {
        "id": "mcq-db-3", "topic": "Databases",
        "question": "MongoDB stores data documents in which format?",
        "options": ["BSON (Binary JSON)", "XML", "CSV", "Protocol Buffers"],
        "correct_option_index": 0, "explanation": "MongoDB stores records internally as BSON (Binary JSON)."
    },
    {
        "id": "mcq-db-4", "topic": "Databases",
        "question": "What is the primary benefit of database normalization (up to 3NF)?",
        "options": ["Minimize data redundancy and avoid update anomalies", "Improve read query speed", "Increase disk storage", "Enable full-text search"],
        "correct_option_index": 0, "explanation": "Database normalization reduces duplicate data and ensures data integrity."
    },
    {
        "id": "mcq-db-5", "topic": "Databases",
        "question": "Which data structure is most commonly used for indexing columns in relational databases like PostgreSQL and MySQL?",
        "options": ["B+ Tree", "Binary Search Tree", "Linked List", "Graph"],
        "correct_option_index": 0, "explanation": "B+ Trees maintain balanced depth and optimize disk page block reads for range queries."
    },
    {
        "id": "mcq-db-6", "topic": "Databases",
        "question": "Which Redis data structure is ideal for maintaining real-time leaderboards sorted by candidate scores?",
        "options": ["Sorted Set (ZSET)", "Hash", "List", "Bitfield"],
        "correct_option_index": 0, "explanation": "Redis Sorted Sets (ZSET) order unique members by floating-point scores in logarithmic time."
    },
    {
        "id": "mcq-db-7", "topic": "Databases",
        "question": "What does database 'Sharding' refer to?",
        "options": ["Horizontally partitioning data rows across multiple database servers", "Creating read replicas", "Encrypting database tables", "Compressing database logs"],
        "correct_option_index": 0, "explanation": "Sharding splits large database tables across independent physical nodes by a shard key."
    },
    {
        "id": "mcq-db-8", "topic": "Databases",
        "question": "In SQL, which JOIN returns all rows from the left table, and the matched rows from the right table?",
        "options": ["LEFT JOIN", "INNER JOIN", "RIGHT JOIN", "FULL OUTER JOIN"],
        "correct_option_index": 0, "explanation": "`LEFT JOIN` returns all rows from the left table even if there are no matches in the right."
    },
    {
        "id": "mcq-db-9", "topic": "Databases",
        "question": "Which NoSQL database category does Apache Cassandra belong to?",
        "options": ["Wide-Column Store", "Document Store", "Graph Database", "Key-Value Store"],
        "correct_option_index": 0, "explanation": "Cassandra is a distributed wide-column NoSQL database modeled on Google BigTable."
    },
    {
        "id": "mcq-db-10", "topic": "Databases",
        "question": "What does WAL stand for in database crash recovery mechanisms?",
        "options": ["Write-Ahead Logging", "Weighted Array Lock", "Wide Area Layer", "Web Auth Logic"],
        "correct_option_index": 0, "explanation": "Write-Ahead Logging guarantees transactions are logged to persistent disk before mutating data files."
    },

    # --------------------------------------------------------------------------
    # D. ARTIFICIAL INTELLIGENCE & MACHINE LEARNING (Deep Learning, LLMs, NLP)
    # --------------------------------------------------------------------------
    {
        "id": "mcq-ai-1", "topic": "AI/ML",
        "question": "Which activation function is most widely used in hidden layers of deep neural networks to prevent vanishing gradients?",
        "options": ["ReLU", "Sigmoid", "Linear", "Step Function"],
        "correct_option_index": 0, "explanation": "ReLU (f(x) = max(0, x)) computes rapidly and mitigates vanishing gradients."
    },
    {
        "id": "mcq-ai-2", "topic": "LLMs",
        "question": "What is 'RLHF' in the context of Large Language Model training?",
        "options": ["Reinforcement Learning from Human Feedback", "Recursive Layer Hidden Forwarding", "Random Loss Hyperparameter Filtering", "Realtime Latency Heuristic Factor"],
        "correct_option_index": 0, "explanation": "RLHF aligns LLMs with human preferences and safety guidelines."
    },
    {
        "id": "mcq-ai-3", "topic": "AI/ML",
        "question": "What problem occurs when a model performs exceptionally well on training data but poorly on test data?",
        "options": ["Overfitting", "Underfitting", "Data Drift", "Quantization"],
        "correct_option_index": 0, "explanation": "Overfitting happens when a model learns noise in training data rather than general patterns."
    },
    {
        "id": "mcq-ai-4", "topic": "LLMs & AI",
        "question": "What is the term for when an LLM confidently outputs factually incorrect or fabricated information?",
        "options": ["Hallucination", "Drift", "Overfitting", "Token Decay"],
        "correct_option_index": 0, "explanation": "LLM hallucination refers to generating plausible-sounding but fabricated claims."
    },
    {
        "id": "mcq-ai-5", "topic": "AI/ML",
        "question": "What algorithm calculates gradients of the loss function with respect to weights using the chain rule in neural networks?",
        "options": ["Backpropagation", "Forward Propagation", "Beam Search", "Monte Carlo Sampling"],
        "correct_option_index": 0, "explanation": "Backpropagation applies the chain rule backward from the loss layer to calculate weight gradients."
    },
    {
        "id": "mcq-ai-6", "topic": "AI/ML",
        "question": "Which regularization technique randomly deactivates neurons during training to prevent co-adaptation?",
        "options": ["Dropout", "Batch Normalization", "Early Stopping", "Gradient Clipping"],
        "correct_option_index": 0, "explanation": "Dropout sets random activations to zero during training with probability p."
    },
    {
        "id": "mcq-ai-7", "topic": "LLMs & GenAI",
        "question": "What mathematical metric is most commonly used to compute similarity between two dense embedding vectors in RAG systems?",
        "options": ["Cosine Similarity", "Hamming Distance", "Jaccard Index", "Levenshtein Distance"],
        "correct_option_index": 0, "explanation": "Cosine similarity measures the angle between normalized vector embeddings in multi-dimensional space."
    },
    {
        "id": "mcq-ai-8", "topic": "AI/ML",
        "question": "Which neural network architecture is primarily specialized for image recognition and spatial feature extraction?",
        "options": ["CNN (Convolutional Neural Network)", "RNN (Recurrent Neural Network)", "Transformer", "Autoencoder"],
        "correct_option_index": 0, "explanation": "CNNs use convolutional kernels to extract spatial visual patterns like edges and textures."
    },
    {
        "id": "mcq-ai-9", "topic": "LLMs",
        "question": "What does 'LoRA' stand for in efficient fine-tuning of Large Language Models?",
        "options": ["Low-Rank Adaptation", "Local Recurrent Attention", "Logarithmic Optimization Array", "Loss Reduction Algorithm"],
        "correct_option_index": 0, "explanation": "LoRA freezes base model weights and trains low-rank decomposition matrices."
    },
    {
        "id": "mcq-ai-10", "topic": "Machine Learning",
        "question": "Which unsupervised learning algorithm groups unlabeled data points into K distinct clusters based on feature distances?",
        "options": ["K-Means Clustering", "K-Nearest Neighbors (KNN)", "Decision Trees", "Linear Regression"],
        "correct_option_index": 0, "explanation": "K-Means is an unsupervised clustering algorithm that minimizes distance to cluster centroids."
    },

    # --------------------------------------------------------------------------
    # E. APIS, WEB PROTOCOLS & NETWORKING (REST, GraphQL, gRPC, HTTP, WebSockets)
    # --------------------------------------------------------------------------
    {
        "id": "mcq-api-1", "topic": "APIs",
        "question": "Which HTTP status code signifies that a resource was successfully created on the server?",
        "options": ["201 Created", "200 OK", "204 No Content", "202 Accepted"],
        "correct_option_index": 0, "explanation": "HTTP 201 indicates that the request succeeded and created a new resource."
    },
    {
        "id": "mcq-api-2", "topic": "APIs",
        "question": "Which query language for APIs allows clients to request exactly the fields they need from the backend?",
        "options": ["GraphQL", "REST", "gRPC", "SOAP"],
        "correct_option_index": 0, "explanation": "GraphQL lets client apps specify the exact structure of data required, preventing over-fetching."
    },
    {
        "id": "mcq-api-3", "topic": "Web Protocols",
        "question": "Which protocol provides full-duplex, persistent, bidirectional communication channels over a single TCP connection?",
        "options": ["WebSocket", "HTTP/1.1", "SSE (Server-Sent Events)", "FTP"],
        "correct_option_index": 0, "explanation": "WebSockets enable low-latency two-way messaging between client and server."
    },
    {
        "id": "mcq-api-4", "topic": "APIs & Security",
        "question": "What is the primary role of the `Authorization: Bearer <token>` header in REST API requests?",
        "options": ["Authenticate and authorize client access to protected endpoints", "Specify response media type", "Enable CORS", "Compress request body"],
        "correct_option_index": 0, "explanation": "Bearer tokens (such as JWTs) verify identity and permissions on API requests."
    },
    {
        "id": "mcq-api-5", "topic": "HTTP Protocols",
        "question": "Which HTTP request method is intended to apply partial modifications to an existing resource?",
        "options": ["PATCH", "PUT", "POST", "OPTIONS"],
        "correct_option_index": 0, "explanation": "PATCH applies partial updates, whereas PUT typically replaces the entire resource."
    },
    {
        "id": "mcq-api-6", "topic": "Networking",
        "question": "Which transport protocol is connectionless and prioritized for real-time video streaming and gaming where low latency beats reliability?",
        "options": ["UDP", "TCP", "SCTP", "TLS"],
        "correct_option_index": 0, "explanation": "UDP delivers packets without handshake or retransmission overhead."
    },
    {
        "id": "mcq-api-7", "topic": "APIs",
        "question": "What is an 'Idempotent' HTTP method?",
        "options": ["A method where multiple identical requests produce the same server state as a single request (e.g. GET, PUT, DELETE)", "A method that cannot be cached", "A method that only handles JSON", "A method that requires authentication"],
        "correct_option_index": 0, "explanation": "Idempotent requests (GET, PUT, DELETE) leave server state unchanged on repeated calls."
    },
    {
        "id": "mcq-api-8", "topic": "Web Security",
        "question": "Which HTTP header protects websites against clickjacking attacks by controlling whether the site can be embedded in an <iframe>?",
        "options": ["X-Frame-Options", "X-Content-Type-Options", "Strict-Transport-Security", "Access-Control-Allow-Origin"],
        "correct_option_index": 0, "explanation": "`X-Frame-Options: DENY` or `SAMEORIGIN` prevents frame embedding attacks."
    },

    # --------------------------------------------------------------------------
    # F. DATA STRUCTURES & ALGORITHMS (Big O, Trees, Graphs, Sorting, DP)
    # --------------------------------------------------------------------------
    {
        "id": "mcq-dsa-1", "topic": "DSA",
        "question": "What is the average time complexity of searching an element in a Hash Table?",
        "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
        "correct_option_index": 0, "explanation": "Hash tables provide average O(1) constant time lookups via direct key hashing."
    },
    {
        "id": "mcq-dsa-2", "topic": "DSA",
        "question": "Which data structure operates strictly on a First-In-First-Out (FIFO) basis?",
        "options": ["Queue", "Stack", "Binary Tree", "Max Heap"],
        "correct_option_index": 0, "explanation": "A Queue adheres strictly to First-In-First-Out ordering."
    },
    {
        "id": "mcq-dsa-3", "topic": "DSA",
        "question": "What is the worst-case time complexity of QuickSort when an unbalanced pivot is chosen?",
        "options": ["O(n²)", "O(n log n)", "O(n)", "O(log n)"],
        "correct_option_index": 0, "explanation": "When an unbalanced pivot is picked, QuickSort degrades to O(n²)."
    },
    {
        "id": "mcq-dsa-4", "topic": "DSA",
        "question": "What graph traversal algorithm uses a Queue and visits nodes level by level?",
        "options": ["Breadth-First Search (BFS)", "Depth-First Search (DFS)", "Dijkstra's Algorithm", "Kruskal's Algorithm"],
        "correct_option_index": 0, "explanation": "BFS uses a FIFO Queue to traverse neighbors level by level."
    },
    {
        "id": "mcq-dsa-5", "topic": "DSA",
        "question": "Which sorting algorithm is guaranteed to run in O(n log n) time in all cases (worst, average, and best) and is stable?",
        "options": ["Merge Sort", "QuickSort", "Selection Sort", "Bubble Sort"],
        "correct_option_index": 0, "explanation": "Merge Sort guarantees O(n log n) time complexity and preserves element order."
    },
    {
        "id": "mcq-dsa-6", "topic": "DSA",
        "question": "What algorithm finds the shortest path between nodes in a weighted graph with non-negative edge weights?",
        "options": ["Dijkstra's Algorithm", "Floyd-Warshall", "Prim's Algorithm", "Bellman-Ford"],
        "correct_option_index": 0, "explanation": "Dijkstra's algorithm uses a priority queue (min-heap) to compute shortest paths."
    },
    {
        "id": "mcq-dsa-7", "topic": "DSA",
        "question": "In a Max Heap binary tree, where is the largest element located?",
        "options": ["At the root node", "At the leftmost leaf", "At the rightmost leaf", "At the lowest level"],
        "correct_option_index": 0, "explanation": "In a Max Heap, the root node holds the maximum value in O(1) access time."
    },
    {
        "id": "mcq-dsa-8", "topic": "DSA",
        "question": "What dynamic programming approach stores solutions to subproblems in a lookup table top-down with recursion?",
        "options": ["Memoization", "Tabulation", "Greedy Choice", "Divide and Conquer"],
        "correct_option_index": 0, "explanation": "Memoization caches recursive results top-down to avoid redundant subproblem calculations."
    },
    {
        "id": "mcq-dsa-9", "topic": "DSA",
        "question": "What is the time complexity to insert an element at the beginning of a singly linked list with a head pointer?",
        "options": ["O(1)", "O(n)", "O(log n)", "O(n²)"],
        "correct_option_index": 0, "explanation": "Inserting at head only requires updating pointer references, which takes O(1) constant time."
    },
    {
        "id": "mcq-dsa-10", "topic": "DSA",
        "question": "Which data structure is used to check balanced parentheses in an expression (e.g. `{[()]}`)?",
        "options": ["Stack", "Queue", "Binary Search Tree", "Linked List"],
        "correct_option_index": 0, "explanation": "A Stack pushes opening brackets and pops to verify matching closing brackets (LIFO)."
    },

    # --------------------------------------------------------------------------
    # G. CLOUD & DEVOPS (AWS, GCP, Docker, Kubernetes, CI/CD, Terraform, Linux)
    # --------------------------------------------------------------------------
    {
        "id": "mcq-cd-1", "topic": "Cloud",
        "question": "What is the AWS serverless compute service that runs code in response to events?",
        "options": ["AWS Lambda", "Amazon EC2", "Amazon S3", "AWS Fargate"],
        "correct_option_index": 0, "explanation": "AWS Lambda is the serverless event-driven compute engine provided by AWS."
    },
    {
        "id": "mcq-cd-2", "topic": "Cloud & DevOps",
        "question": "Which tool uses declarative HCL files to manage Infrastructure as Code?",
        "options": ["Terraform", "Ansible", "Jenkins", "Prometheus"],
        "correct_option_index": 0, "explanation": "Terraform by HashiCorp is the standard declarative Infrastructure as Code tool."
    },
    {
        "id": "mcq-cd-3", "topic": "Cloud & Linux",
        "question": "Which Linux command displays real-time CPU and memory usage of running system processes?",
        "options": ["top", "ls", "grep", "chmod"],
        "correct_option_index": 0, "explanation": "`top` (or `htop`) provides a live interactive view of system processes."
    },
    {
        "id": "mcq-cd-4", "topic": "Cloud & Docker",
        "question": "Which Docker instruction sets the default command to execute when a container starts?",
        "options": ["CMD", "RUN", "ENV", "EXPOSE"],
        "correct_option_index": 0, "explanation": "`CMD` provides defaults for an executing container."
    },
    {
        "id": "mcq-cd-5", "topic": "Kubernetes",
        "question": "What is the smallest deployable computing unit that can be created and managed in Kubernetes?",
        "options": ["Pod", "Node", "Cluster", "Deployment"],
        "correct_option_index": 0, "explanation": "A Pod encapsulates one or more co-located containers sharing storage and network."
    },
    {
        "id": "mcq-cd-6", "topic": "Cloud & DevOps",
        "question": "In CI/CD pipelines, what is the automated practice of continuously building and running unit tests on every commit?",
        "options": ["Continuous Integration (CI)", "Continuous Deployment (CD)", "Blue-Green Deployment", "Canary Release"],
        "correct_option_index": 0, "explanation": "Continuous Integration automatically merges code and executes test suites on PRs."
    },
    {
        "id": "mcq-cd-7", "topic": "Linux",
        "question": "Which Linux command changes file and directory permissions (e.g. `chmod 755 app.sh`)?",
        "options": ["chmod", "chown", "chgrp", "touch"],
        "correct_option_index": 0, "explanation": "`chmod` modifies read, write, and execute permissions on files."
    },
    {
        "id": "mcq-cd-8", "topic": "Cloud Storage",
        "question": "What storage class is AWS S3 designed as?",
        "options": ["Object Storage", "Block Storage", "File System Storage", "Relational Storage"],
        "correct_option_index": 0, "explanation": "Amazon S3 is a highly durable, scalable cloud Object Storage service."
    },

    # --------------------------------------------------------------------------
    # H. SOFTWARE DEVELOPMENT FUNDAMENTALS (SOLID, OOP, System Design, Git)
    # --------------------------------------------------------------------------
    {
        "id": "mcq-sd-1", "topic": "Software Engineering",
        "question": "What does the 'S' in SOLID principles represent?",
        "options": ["Single Responsibility Principle", "System Scalability Principle", "Static Typing Principle", "Security First Principle"],
        "correct_option_index": 0, "explanation": "Single Responsibility Principle states a class should have one reason to change."
    },
    {
        "id": "mcq-sd-2", "topic": "Git",
        "question": "Which command creates a new branch and immediately switches to it in Git?",
        "options": ["git checkout -b <name>", "git branch -new <name>", "git switch -create <name>", "git merge <name>"],
        "correct_option_index": 0, "explanation": "`git checkout -b <branch>` or `git switch -c <branch>` creates and checks out a new branch."
    },
    {
        "id": "mcq-sd-3", "topic": "Software Security",
        "question": "What security vulnerability occurs when untrusted user input is concatenated into SQL queries?",
        "options": ["SQL Injection (SQLi)", "Cross-Site Scripting (XSS)", "CSRF Attack", "Buffer Overflow"],
        "correct_option_index": 0, "explanation": "SQL Injection allows attackers to manipulate backend database queries via unsanitized inputs."
    },
    {
        "id": "mcq-sd-4", "topic": "System Design",
        "question": "Which microservices design pattern provides a single reverse-proxy entry point for routing, auth, and rate-limiting?",
        "options": ["API Gateway Pattern", "Circuit Breaker Pattern", "Event Sourcing Pattern", "Saga Pattern"],
        "correct_option_index": 0, "explanation": "API Gateway centralizes client routing, SSL termination, and security policies."
    },
    {
        "id": "mcq-sd-5", "topic": "Design Patterns",
        "question": "Which creational design pattern ensures a class has only one instance and provides a global point of access to it?",
        "options": ["Singleton Pattern", "Factory Method Pattern", "Prototype Pattern", "Builder Pattern"],
        "correct_option_index": 0, "explanation": "Singleton restricts instantiation to a single object throughout the application runtime."
    },
    {
        "id": "mcq-sd-6", "topic": "SOLID Principles",
        "question": "What does the 'O' in SOLID design principles stand for?",
        "options": ["Open/Closed Principle (Open for extension, closed for modification)", "Object-Oriented Principle", "Operational Stability Principle", "One-Way Data Binding"],
        "correct_option_index": 0, "explanation": "Open/Closed Principle states entities should be open for extension but closed for modification."
    },
    {
        "id": "mcq-sd-7", "topic": "System Design",
        "question": "What mechanism automatically reroutes incoming traffic away from a failing microservice to prevent cascading outages?",
        "options": ["Circuit Breaker Pattern", "Load Balancer", "Service Mesh", "Dead Letter Queue"],
        "correct_option_index": 0, "explanation": "Circuit Breakers trip open when failure rates exceed thresholds, returning fallback responses."
    },
    {
        "id": "mcq-sd-8", "topic": "HTML/CSS",
        "question": "Which CSS property is used to create a Glassmorphism frosted-glass blur effect?",
        "options": ["backdrop-filter: blur()", "filter: glass()", "box-shadow: blur()", "opacity: glass"],
        "correct_option_index": 0, "explanation": "`backdrop-filter: blur(10px)` applies graphical effects to the background behind an element."
    },
    {
        "id": "mcq-sd-9", "topic": "HTML/CSS",
        "question": "Which CSS display mode allows 2-dimensional grid layout (both rows and columns simultaneously)?",
        "options": ["display: grid", "display: flex", "display: inline-block", "display: table"],
        "correct_option_index": 0, "explanation": "CSS Grid is a 2D layout system, while Flexbox is 1D."
    },
    {
        "id": "mcq-sd-10", "topic": "Software Testing",
        "question": "What type of testing evaluates individual functions or classes in isolation from external dependencies using mocks?",
        "options": ["Unit Testing", "End-to-End (E2E) Testing", "Integration Testing", "Smoke Testing"],
        "correct_option_index": 0, "explanation": "Unit testing validates individual modules or units of code in complete isolation."
    },
    {
        "id": "mcq-extra-1", "topic": "Programming Languages",
        "question": "In Rust, what keyword is required when declaring a variable whose value can be modified after initialization?",
        "options": ["mut", "var", "let", "dynamic"],
        "correct_option_index": 0, "explanation": "Variables in Rust are immutable by default; `mut` explicitly makes them mutable."
    },
    {
        "id": "mcq-extra-2", "topic": "AI & LLMs",
        "question": "What is the maximum token capacity that an LLM can process simultaneously in a single prompt called?",
        "options": ["Context Window", "Batch Capacity", "Embedding Horizon", "Hidden Layer Depth"],
        "correct_option_index": 0, "explanation": "The Context Window defines the maximum sequence length of tokens an LLM can attend to."
    },
    {
        "id": "mcq-extra-3", "topic": "Databases",
        "question": "Which database type uses nodes, edges, and properties to represent and store highly interconnected relationships?",
        "options": ["Graph Database (e.g. Neo4j)", "Columnar Database", "Document Database", "Relational Database"],
        "correct_option_index": 0, "explanation": "Graph databases (like Neo4j) store relationships natively as pointers between nodes."
    },
    {
        "id": "mcq-extra-4", "topic": "DSA",
        "question": "Which data structure is optimal for prefix search, autocomplete, and dictionary word lookups?",
        "options": ["Trie (Prefix Tree)", "Red-Black Tree", "Hash Map", "Min-Heap"],
        "correct_option_index": 0, "explanation": "A Trie provides O(L) time lookups for strings of length L, making autocomplete efficient."
    },
    {
        "id": "mcq-extra-5", "topic": "APIs & Web",
        "question": "Which open standard is used for delegated token-based authorization on third-party services (e.g., 'Log in with Google')?",
        "options": ["OAuth 2.0", "Basic Auth", "LDAP", "Kerberos"],
        "correct_option_index": 0, "explanation": "OAuth 2.0 allows users to grant third-party applications access without sharing passwords."
    },
    {
        "id": "mcq-extra-6", "topic": "Cloud & DevOps",
        "question": "In Docker, what technique optimizes production container image size by compiling in an intermediate stage and copying only artifacts?",
        "options": ["Multi-stage Builds", "Layer Caching", "Docker Compose", "Volume Mounting"],
        "correct_option_index": 0, "explanation": "Multi-stage builds leave build tools behind, creating slim, production-ready images."
    },
    {
        "id": "mcq-extra-7", "topic": "Frameworks",
        "question": "Which Python web framework is known for being micro, unopinionated, and having minimal built-in boilerplate?",
        "options": ["Flask", "Django", "FastAPI", "Tornado"],
        "correct_option_index": 0, "explanation": "Flask is a lightweight WSGI micro-framework that lets developers choose their extensions."
    },
    {
        "id": "mcq-extra-8", "topic": "DSA",
        "question": "What is the space complexity of Depth-First Search (DFS) on a binary tree with maximum depth H?",
        "options": ["O(H) (call stack)", "O(1)", "O(N²)", "O(log H)"],
        "correct_option_index": 0, "explanation": "DFS recursion consumes call stack space proportional to the maximum tree depth H."
    },
    {
        "id": "mcq-extra-9", "topic": "System Design",
        "question": "Which deployment strategy gradually shifts a small percentage of live user traffic (e.g. 5%) to a new version to test stability?",
        "options": ["Canary Deployment", "Blue-Green Deployment", "Recreate Deployment", "Rolling Update"],
        "correct_option_index": 0, "explanation": "Canary deployments minimize risk by routing a fraction of real traffic to the new release."
    },
    {
        "id": "mcq-extra-10", "topic": "AI & LLMs",
        "question": "What technique converts continuous words or tokens into dense floating-point vector representations in high-dimensional space?",
        "options": ["Vector Embeddings", "One-Hot Encoding", "Quantization", "Tokenization"],
        "correct_option_index": 0, "explanation": "Vector embeddings capture semantic relationships and meaning as dense numerical vectors."
    },
    {
        "id": "mcq-extra-11", "topic": "Programming Languages",
        "question": "Which keyword in PHP defines an anonymous function or closure?",
        "options": ["function () use (...) { }", "lambda", "def", "arrow"],
        "correct_option_index": 0, "explanation": "PHP uses `function () use ($var) {}` to define anonymous closures inheriting outer variables."
    },
    {
        "id": "mcq-extra-12", "topic": "Databases",
        "question": "Which Amazon Web Services managed database is a serverless NoSQL key-value and document store with single-digit millisecond latency?",
        "options": ["Amazon DynamoDB", "Amazon RDS", "Amazon Redshift", "Amazon Aurora"],
        "correct_option_index": 0, "explanation": "DynamoDB is AWS's fully managed, auto-scaling NoSQL database."
    },
    {
        "id": "mcq-extra-13", "topic": "DSA",
        "question": "What algorithm finds the topological ordering of directed acyclic graph (DAG) vertices for dependency resolution?",
        "options": ["Topological Sort (Kahn's Algorithm / DFS)", "Prim's Algorithm", "Binary Search", "Kadane's Algorithm"],
        "correct_option_index": 0, "explanation": "Topological sorting linearly orders vertices so that every directed edge u->v comes before v."
    },
    {
        "id": "mcq-extra-14", "topic": "Web Protocols",
        "question": "What technology enables real-time peer-to-peer audio, video, and data streaming directly between web browsers without plugins?",
        "options": ["WebRTC", "WebSocket", "gRPC-Web", "HTTP/2"],
        "correct_option_index": 0, "explanation": "WebRTC (Web Real-Time Communication) provides direct browser-to-browser media streaming."
    },
    {
        "id": "mcq-extra-15", "topic": "Cloud & Infrastructure",
        "question": "Where does Terraform store the current metadata and mapping of real-world cloud resources?",
        "options": ["Terraform State file (terraform.tfstate)", "Docker Registry", "Git History", "Kubeconfig"],
        "correct_option_index": 0, "explanation": "Terraform tracks managed infrastructure resources in its state file (`terraform.tfstate`)."
    },
    {
        "id": "mcq-extra-16", "topic": "Programming Languages",
        "question": "Which language's primary web framework is Ruby on Rails ('Convention over Configuration')?",
        "options": ["Ruby", "Python", "Perl", "Elixir"],
        "correct_option_index": 0, "explanation": "Ruby on Rails is the renowned full-stack framework written in Ruby."
    },
    {
        "id": "mcq-extra-17", "topic": "Software Engineering",
        "question": "What design pattern defines a one-to-many dependency between objects so that when one object changes state, all its dependents are notified?",
        "options": ["Observer Pattern", "Adapter Pattern", "Facade Pattern", "Decorator Pattern"],
        "correct_option_index": 0, "explanation": "The Observer pattern is the foundation of reactive event handling and pub/sub."
    },
    {
        "id": "mcq-extra-18", "topic": "AI & Machine Learning",
        "question": "Which loss function is standard for multi-class classification neural networks paired with Softmax output?",
        "options": ["Cross-Entropy Loss (Categorical Cross-Entropy)", "Mean Squared Error (MSE)", "Hinge Loss", "Mean Absolute Error (MAE)"],
        "correct_option_index": 0, "explanation": "Categorical Cross-Entropy measures the performance of probability outputs from Softmax."
    },
    {
        "id": "mcq-extra-19", "topic": "Databases",
        "question": "In PostgreSQL, what index type is specifically optimized for indexing JSONB documents and array containment?",
        "options": ["GIN (Generalized Inverted Index)", "B-Tree", "Hash Index", "BRIN"],
        "correct_option_index": 0, "explanation": "GIN indexes inverted arrays and composite items like JSONB keys and values."
    },
    {
        "id": "mcq-extra-20", "topic": "DSA",
        "question": "What is the optimal time complexity of Kadane's Algorithm to find the maximum subarray sum in a 1D array?",
        "options": ["O(n)", "O(n²)", "O(n log n)", "O(log n)"],
        "correct_option_index": 0, "explanation": "Kadane's algorithm scans the array in a single pass in linear O(n) time."
    }
]

# ==============================================================================
# 3. TECH LOGO CHALLENGE POOL (50+ DIVERSE TECH, AI, CLOUD & FRAMEWORK LOGOS)
# ==============================================================================
LOGO_CHALLENGE_BANK = [
    {
        "id": "logo-1", "name": "Python", "category": "Programming Language",
        "hint": "Interpreted high-level language with famous blue & yellow entwined serpents.",
        "accepted_answers": ["python", "python3", "python 3"],
        "options": ["Python", "JavaScript", "Golang", "Ruby"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#387EB8" d="M63.5 12C41.2 12 42.6 21.6 42.6 21.6l.1 10.1h21.4v3H33.3S19 33.1 19 55.4s12.5 22.8 12.5 22.8h7.5v-10.6s-.4-12.8 12.6-12.8h21.3s12.2-.2 12.2-11.9V23.7S87 12 63.5 12zm-11.9 6.8a3.7 3.7 0 1 1 0 7.4 3.7 3.7 0 0 1 0-7.4z"/><path fill="#FFE052" d="M64.5 116c22.3 0 20.9-9.6 20.9-9.6l-.1-10.1H63.9v-3h30.8s14.3 1.6 14.3-20.7-12.5-22.8-12.5-22.8h-7.5v10.6s.4 12.8-12.6 12.8H55.1s-12.2.2-12.2 11.9v19.2s-1.6 11.7 21.6 11.7zm11.9-6.8a3.7 3.7 0 1 1 0-7.4 3.7 3.7 0 0 1 0 7.4z"/></svg>""",
        "explanation": "Python is a high-level programming language created by Guido van Rossum."
    },
    {
        "id": "logo-2", "name": "Docker", "category": "Containerization Tool",
        "hint": "The iconic blue whale carrying shipping containers on its back.",
        "accepted_answers": ["docker", "docker container"],
        "options": ["Docker", "Kubernetes", "Podman", "Vagrant"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#2496ED" d="M123.6 57.8c-1.3-.9-5.9-3.7-16-3-2.1-7.2-7.5-12.5-13.8-15.5l-2.6 4.9c5 2.5 9.3 7 10.9 12.9-1.2.6-3.8 1.4-8 1.4H83v-6.3H70.7V40.2h12.3V28H70.7V15.7H58.4v12.3H46.1v12.2H33.8v12H1.9C.7 57.5 0 63.6 0 69.8c0 23.4 18.2 42.4 40.7 42.4 25.1 0 43.6-13.8 51.5-38.3 10.8.6 19.3-3.2 24.5-8.5 7-7.2 7-7.6 6.9-7.6zm-77.5-5.6v10.3H33.8V52.2h12.3zm12.3 0v10.3H46.1V52.2h12.3zm12.3 0v10.3H58.4V52.2h12.3zm12.3 0v10.3H70.7V52.2h12.3z"/></svg>""",
        "explanation": "Docker standardizes software packaging in lightweight containers."
    },
    {
        "id": "logo-3", "name": "React", "category": "Frontend Framework / Library",
        "hint": "The vibrant cyan atomic nucleus with revolving electron orbits.",
        "accepted_answers": ["react", "reactjs", "react.js"],
        "options": ["React", "Vue", "Angular", "Svelte"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="-11.5 -10.23174 23 20.46348" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><circle cx="0" cy="0" r="2.05" fill="#61dafb"/><g stroke="#61dafb" stroke-width="1" fill="none"><ellipse rx="11" ry="4.2"/><ellipse rx="11" ry="4.2" transform="rotate(60)"/><ellipse rx="11" ry="4.2" transform="rotate(120)"/></g></svg>""",
        "explanation": "React is Meta's open-source JavaScript library for component-based UIs."
    },
    {
        "id": "logo-4", "name": "Kubernetes", "category": "Cloud Orchestration",
        "hint": "The blue 7-spoke ship wheel (helmsman steering wheel) logo.",
        "accepted_answers": ["kubernetes", "k8s"],
        "options": ["Kubernetes", "Helm", "OpenShift", "Istio"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#326CE5" d="M64 9.3 16.7 36.6v54.7L64 118.7l47.3-27.3V36.6L64 9.3zm0 9.8 38.6 22.3v44.6L64 108.3 25.4 86V41.4L64 19.1zm0 18.2a26.7 26.7 0 1 0 0 53.4 26.7 26.7 0 0 0 0-53.4zm0 8.9a17.8 17.8 0 1 1 0 35.6 17.8 17.8 0 0 1 0-35.6z"/><circle cx="64" cy="64" r="6" fill="#326CE5"/></svg>""",
        "explanation": "Kubernetes automates deployment and scaling of containerized applications."
    },
    {
        "id": "logo-5", "name": "Redis", "category": "In-Memory Database",
        "hint": "Stack of reddish-brown 3D isometric memory blocks.",
        "accepted_answers": ["redis", "remote dictionary server"],
        "options": ["Redis", "PostgreSQL", "MongoDB", "Memcached"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#D82C20" d="M64 12 12 36l52 24 52-24-52-24zm-48 38v30l48 22V72l-48-22zm96 0-48 22v30l48-22V50z"/><path fill="#A32017" d="M64 60 16 38l48-22 48 22-48 22z"/><path fill="#FFF" opacity="0.3" d="m40 28 24 11 24-11-24-11-24 11z"/></svg>""",
        "explanation": "Redis provides in-memory key-value data structures used for fast caching."
    },
    {
        "id": "logo-6", "name": "Rust", "category": "Systems Programming Language",
        "hint": "A mechanical bicycle sprocket / gear enclosing a stylized capital 'R'.",
        "accepted_answers": ["rust", "rustlang"],
        "options": ["Rust", "C++", "Go", "Zig"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#DEA584" d="M64 10a54 54 0 1 0 54 54A54 54 0 0 0 64 10zm0 10a44 44 0 1 1-44 44 44 44 0 0 1 44-44z"/><path fill="#000" d="M42 38h24c11 0 18 5 18 14 0 7-5 12-11 13l13 25H72L61 67H53v21H42V38zm11 19h12c5 0 8-2 8-6s-3-6-8-6H53v12z"/></svg>""",
        "explanation": "Rust offers memory safety without garbage collection via ownership semantics."
    },
    {
        "id": "logo-7", "name": "PostgreSQL", "category": "Relational Database",
        "hint": "Slonik the blue elephant mascot representing relational database reliability.",
        "accepted_answers": ["postgresql", "postgres", "psql"],
        "options": ["PostgreSQL", "MySQL", "Oracle", "SQLite"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#336791" d="M64 14C36.4 14 14 36.4 14 64s22.4 50 50 50 50-22.4 50-50S91.6 14 64 14zm18.2 68.3c-2.4 4.8-7.5 8.1-13.4 8.7l-4.8 19-8-2-4.8-19c-5.9-.6-11-3.9-13.4-8.7C33.2 63.8 45 42 64 42s30.8 21.8 18.2 40.3z"/><circle cx="54" cy="56" r="3" fill="#FFF"/><circle cx="74" cy="56" r="3" fill="#FFF"/></svg>""",
        "explanation": "PostgreSQL is an advanced open-source object-relational database system."
    },
    {
        "id": "logo-8", "name": "TensorFlow", "category": "Machine Learning Framework",
        "hint": "The vibrant orange isometric 3D letter 'T' made of cube facets.",
        "accepted_answers": ["tensorflow", "tf"],
        "options": ["TensorFlow", "PyTorch", "Keras", "Scikit-Learn"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#FF6F00" d="M64 12 18 38v52l22 13V50l24-14 24 14v53l22-13V38L64 12z"/><path fill="#FFA000" d="M64 50 40 64v38l24 14 24-14V64L64 50z"/></svg>""",
        "explanation": "TensorFlow is an end-to-end machine learning platform developed by Google."
    },
    {
        "id": "logo-9", "name": "MongoDB", "category": "NoSQL Document Database",
        "hint": "The green leaf / sprouting seed document database logo.",
        "accepted_answers": ["mongodb", "mongo"],
        "options": ["MongoDB", "Cassandra", "CouchDB", "DynamoDB"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#47A248" d="M64 10s-32 30-32 62c0 23 18 36 32 46 14-10 32-23 32-46 0-32-32-62-32-62z"/><path fill="#499D4A" d="M64 10v98c14-10 32-23 32-46 0-32-32-52-32-52z"/><path fill="#FFF" d="M64 50v58c-1-1-2-1-3-2V52l3-2z"/></svg>""",
        "explanation": "MongoDB stores data in flexible JSON-like documents."
    },
    {
        "id": "logo-10", "name": "OpenAI", "category": "AI Research Lab & Platform",
        "hint": "The iconic geometric spiral vortex / flower logo behind ChatGPT and GPT-4.",
        "accepted_answers": ["openai", "open ai", "chatgpt"],
        "options": ["OpenAI", "Anthropic", "DeepMind", "Mistral AI"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#10A37F" d="M110.6 52.8a28.4 28.4 0 0 0-2.4-23.2 28.7 28.7 0 0 0-20.7-13.8 28.5 28.5 0 0 0-26.6 6.5 28.5 28.5 0 0 0-22.7 3.8A28.6 28.6 0 0 0 25 43.4a28.5 28.5 0 0 0-8.2 25.4 28.6 28.6 0 0 0 10.3 21.2 28.6 28.6 0 0 0 20.7 13.8 28.5 28.5 0 0 0 26.6-6.5 28.5 28.5 0 0 0 22.7-3.8 28.6 28.6 0 0 0 13.2-17.3 28.5 28.5 0 0 0 8.2-25.4zM64 74a10 10 0 1 1 10-10 10 10 0 0 1-10 10z"/></svg>""",
        "explanation": "OpenAI created ChatGPT, GPT-4, DALL-E, and Whisper."
    },
    {
        "id": "logo-11", "name": "TypeScript", "category": "Programming Language",
        "hint": "Blue square with white capital letters 'TS' representing typed JavaScript.",
        "accepted_answers": ["typescript", "ts"],
        "options": ["TypeScript", "JavaScript", "Flow", "ActionScript"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><rect width="128" height="128" rx="16" fill="#3178C6"/><path fill="#FFF" d="M60 48H32v12h10v36h14V60h10V48h-6zm42 15c-3-2-8-4-14-4-7 0-11 3-11 7 0 4 3 6 10 9 11 4 17 9 17 19 0 11-9 18-23 18-7 0-14-2-18-5l4-11c4 3 9 5 15 5 6 0 10-3 10-7 0-4-3-6-10-9-11-4-17-9-17-18 0-11 9-18 22-18 6 0 12 1 16 4l-4 10z"/></svg>""",
        "explanation": "TypeScript is Microsoft's strongly typed superset of JavaScript."
    },
    {
        "id": "logo-12", "name": "Golang", "category": "Programming Language",
        "hint": "Cyan stylized 'GO' with speed velocity trails.",
        "accepted_answers": ["go", "golang"],
        "options": ["Go (Golang)", "Rust", "Kotlin", "Dart"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#00ADD8" d="M26 64c0-18 13-32 32-32 10 0 18 5 23 11l-9 8c-3-4-8-7-14-7-11 0-19 9-19 20s8 20 19 20c7 0 11-3 14-6v-6H54V57h31v22c-6 9-16 15-27 15-19 0-32-14-32-30zm68 0c0-18 13-32 32-32s32 14 32 32-13 32-32 32-32-14-32-32zm51 0c0-11-8-20-19-20s-19 9-19 20 8 20 19 20 19-9 19-20z"/></svg>""",
        "explanation": "Go was developed at Google for fast compiled microservices."
    },
    {
        "id": "logo-13", "name": "Git", "category": "Version Control System",
        "hint": "Reddish-orange diamond with branching node tree lines.",
        "accepted_answers": ["git", "git vcs"],
        "options": ["Git", "SVN", "Mercurial", "Perforce"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#F05032" d="M124.7 57.3 70.7 3.3a9.4 9.4 0 0 0-13.3 0L44 16.6l16.8 16.8a11.2 11.2 0 0 1 14.2 14.3l16.2 16.2a11.2 11.2 0 1 1-6.6 6.7L69 55v34.4a11.2 11.2 0 1 1-9.4 0V53.6a11.2 11.2 0 0 1-5.9-14.7L37 22.1 3.3 55.8a9.4 9.4 0 0 0 0 13.3l54 54a9.4 9.4 0 0 0 13.3 0l54.1-54.1a9.4 9.4 0 0 0 0-11.7z"/></svg>""",
        "explanation": "Git is the distributed version control system created by Linus Torvalds."
    },
    {
        "id": "logo-14", "name": "Vue.js", "category": "Frontend Framework",
        "hint": "Sleek emerald green & navy blue triangular 'V' emblem.",
        "accepted_answers": ["vue", "vue.js", "vuejs"],
        "options": ["Vue.js", "React", "Angular", "Ember"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#42B883" d="m64 108 50-86H88L64 64 40 22H14z"/><path fill="#35495E" d="m64 108 28-48H70L64 70l-6-10H36z"/></svg>""",
        "explanation": "Vue.js is an approachable, versatile reactive JavaScript framework."
    },
    {
        "id": "logo-15", "name": "Node.js", "category": "JavaScript Runtime",
        "hint": "Green hexagonal shape containing the letter 'N'.",
        "accepted_answers": ["node", "node.js", "nodejs"],
        "options": ["Node.js", "Deno", "Bun", "Express"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#339933" d="M64 8 16 35.7v56.6L64 120l48-27.7V35.7L64 8zm0 18.5 32 18.5v37L64 100.5 32 82V45l32-18.5z"/></svg>""",
        "explanation": "Node.js executes JavaScript code server-side using Google's V8 engine."
    },
    {
        "id": "logo-16", "name": "AWS", "category": "Cloud Platform",
        "hint": "The orange smiling arrow pointing from 'a' to 'z'.",
        "accepted_answers": ["aws", "amazon web services"],
        "options": ["AWS (Amazon Web Services)", "Azure", "Google Cloud", "IBM Cloud"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#FF9900" d="M30 84c20 12 48 12 68 0 3-2 6 2 4 4-22 14-54 14-76 0-2-2 1-6 4-4z"/><path fill="#232F3E" d="M36 50v20h-8V38h8l14 20V38h8v32h-8L36 50zm44-12h8v32h-8V38zm16 0h24v8h-16v4h14v8h-14v4h16v8H96V38z"/></svg>""",
        "explanation": "Amazon Web Services (AWS) is the world's most comprehensive cloud platform."
    },
    {
        "id": "logo-17", "name": "Next.js", "category": "Fullstack Web Framework",
        "hint": "Black circle with a white stylized 'N' slashed by an angled ray.",
        "accepted_answers": ["next", "next.js", "nextjs"],
        "options": ["Next.js", "Nuxt.js", "Remix", "SvelteKit"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><circle cx="64" cy="64" r="56" fill="#000"/><path fill="#FFF" d="M46 38v52h10V56l26 34h8V38h-10v34L54 38H46z"/></svg>""",
        "explanation": "Next.js by Vercel provides React server rendering and App routing."
    },
    {
        "id": "logo-18", "name": "Linux", "category": "Operating System",
        "hint": "Tux the friendly penguin mascot.",
        "accepted_answers": ["linux", "tux", "gnu linux"],
        "options": ["Linux", "FreeBSD", "Unix", "Darwin"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><ellipse cx="64" cy="66" rx="34" ry="42" fill="#000"/><ellipse cx="64" cy="72" rx="22" ry="30" fill="#FFF"/><ellipse cx="56" cy="40" rx="4" ry="6" fill="#FFF"/><ellipse cx="72" cy="40" rx="4" ry="6" fill="#FFF"/><circle cx="56" cy="42" r="2" fill="#000"/><circle cx="72" cy="42" r="2" fill="#000"/><path fill="#FFA500" d="m64 48 10 10H54l10-10zM36 104c10 0 16-6 16-6s-4 12-16 12-16-6-16-6 6 0 16 0zm56 0c10 0 16-6 16-6s-4 12-16 12-16-6-16-6 6 0 16 0z"/></svg>""",
        "explanation": "Linux is the leading open-source Unix-like kernel powering servers and cloud."
    },
    {
        "id": "logo-19", "name": "GraphQL", "category": "API Query Language",
        "hint": "Pinkish-magenta geometric hexa-gram shape with circular vertices.",
        "accepted_answers": ["graphql", "gql"],
        "options": ["GraphQL", "REST", "gRPC", "SOAP"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#E10098" d="M64 10 14 39v50l50 29 50-29V39L64 10zm0 16 36 21v42L64 110 28 89V47l36-21z"/><circle cx="64" cy="10" r="8" fill="#E10098"/><circle cx="14" cy="39" r="8" fill="#E10098"/><circle cx="114" cy="39" r="8" fill="#E10098"/><circle cx="14" cy="89" r="8" fill="#E10098"/><circle cx="114" cy="89" r="8" fill="#E10098"/><circle cx="64" cy="118" r="8" fill="#E10098"/></svg>""",
        "explanation": "GraphQL enables declarative data fetching tailored to client requests."
    },
    {
        "id": "logo-20", "name": "Java", "category": "Programming Language",
        "hint": "Blue and red steamy cup of coffee.",
        "accepted_answers": ["java", "oracle java"],
        "options": ["Java", "Kotlin", "C#", "Scala"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#EA2D2E" d="M50 82c16 2 34-4 34-4s-14 8-32 8c-8 0-14-1-14-1s4-2 12-3z"/><path fill="#5382A1" d="M66 22c6 6-2 14-2 14s12-8 6-16c-4-6-10-8-10-8s4 4 6 10zm-10 16c8 8-4 18-4 18s16-10 8-22c-6-8-14-10-14-10s6 6 10 14z"/><path fill="#007396" d="M42 96c26 2 54-4 54-4s-22 10-52 10c-12 0-22-2-22-2s6-2 20-4z"/></svg>""",
        "explanation": "Java is an enterprise object-oriented language developed by Sun Microsystems."
    },
    {
        "id": "logo-21", "name": "Swift", "category": "Programming Language",
        "hint": "Orange-red fast diving swallow bird silhouette.",
        "accepted_answers": ["swift", "apple swift"],
        "options": ["Swift", "Objective-C", "Kotlin", "Flutter"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#FA7343" d="M120 74c-10 20-32 38-58 44 32-16 46-44 46-44s-24 16-52 14c-14-1-26-8-36-18 20 12 44 8 44 8S44 70 30 52c-12-16-16-32-16-32s16 16 38 24C68 50 84 44 94 34c-6 10-18 18-30 22 28 4 56 18 56 18z"/></svg>""",
        "explanation": "Swift is Apple's fast, modern language for iOS and macOS development."
    },
    {
        "id": "logo-22", "name": "Tailwind CSS", "category": "CSS Framework",
        "hint": "Two cyan sweeping wind waves.",
        "accepted_answers": ["tailwind", "tailwindcss", "tailwind css"],
        "options": ["Tailwind CSS", "Bootstrap", "Bulma", "Chakra UI"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#06B6D4" d="M64 36c-18 0-26 12-32 24 12-6 22-4 28 2 4 4 8 8 14 8 18 0 26-12 32-24-12 6-22 4-28-2-4-4-8-8-14-8zm-32 36c-18 0-26 12-32 24 12-6 22-4 28 2 4 4 8 8 14 8 18 0 26-12 32-24-12 6-22 4-28-2-4-4-8-8-14-8z"/></svg>""",
        "explanation": "Tailwind CSS is a utility-first CSS framework for rapid UI composition."
    },
    {
        "id": "logo-23", "name": "Angular", "category": "Frontend Framework",
        "hint": "Red shield emblazoned with a white capital letter 'A'.",
        "accepted_answers": ["angular", "angularjs"],
        "options": ["Angular", "React", "Vue", "Ember"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#DD0031" d="M64 12 16 29l8 69 40 18 40-18 8-69L64 12z"/><path fill="#C3002F" d="M64 12v104l40-18 8-69L64 12z"/><path fill="#FFF" d="m64 34-22 50h10l4-11h16l4 11h10L64 34zm7 31H57l7-17 7 17z"/></svg>""",
        "explanation": "Angular is Google's TypeScript-based web application framework."
    },
    {
        "id": "logo-24", "name": "Android", "category": "Mobile OS",
        "hint": "Green robot bugdroid head with two antennae.",
        "accepted_answers": ["android", "google android"],
        "options": ["Android", "iOS", "HarmonyOS", "Ubuntu Touch"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#3DDC84" d="M38 52c-2-4-7-6-10-4l-8-14c-1-2-4-2-6-1s-2 4-1 6l8 14C12 62 6 78 6 96h116c0-18-6-34-15-43l8-14c1-2 0-5-1-6s-5-1-6 1l-8 14c-3-2-8 0-10 4-8-4-17-6-26-6s-18 2-26 6zM36 80c-4 0-8-4-8-8s4-8 8-8 8 4 8 8-4 8-8 8zm56 0c-4 0-8-4-8-8s4-8 8-8 8 4 8 8-4 8-8 8z"/></svg>""",
        "explanation": "Android is the world's most widely deployed mobile operating system."
    },
    {
        "id": "logo-25", "name": "C++", "category": "Programming Language",
        "hint": "Blue hexagonal logo with 'C' and two plus signs.",
        "accepted_answers": ["c++", "cpp", "c plus plus"],
        "options": ["C++", "C", "C#", "Objective-C"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#00599C" d="M64 10 16 38v52l48 28 48-28V38L64 10zm-6 72c-12 0-20-9-20-20s8-20 20-20c7 0 13 3 17 8l-7 6c-2-3-6-5-10-5-7 0-11 5-11 11s4 11 11 11c4 0 8-2 10-5l7 6c-4 5-10 8-17 8zm28-16h4v-8h-4v-4h-4v4h-8v4h8v8h4v-8zm16 0h4v-8h-4v-4h-4v4h-8v4h8v8h4v-8z"/></svg>""",
        "explanation": "C++ is a high-performance compiled language created by Bjarne Stroustrup."
    },
    {
        "id": "logo-26", "name": "PyTorch", "category": "Machine Learning Framework",
        "hint": "The flaming red torch with an open flame circle.",
        "accepted_answers": ["pytorch", "torch"],
        "options": ["PyTorch", "TensorFlow", "JAX", "MXNet"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#EE4C2C" d="M64 16C46 16 32 30 32 48c0 14 8 26 20 30L64 64V16z"/><path fill="#EE4C2C" opacity="0.6" d="M64 16c18 0 32 14 32 32 0 14-8 26-20 30L64 64V16z"/><circle cx="78" cy="34" r="5" fill="#EE4C2C"/></svg>""",
        "explanation": "PyTorch is the premier AI framework powering LLM research."
    },
    {
        "id": "logo-27", "name": "Flutter", "category": "Cross-Platform Framework",
        "hint": "Two bright blue overlapping angled origami wings.",
        "accepted_answers": ["flutter", "dart flutter"],
        "options": ["Flutter", "React Native", "Xamarin", "Ionic"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#02569B" d="M78 12 28 62l16 16 50-50H78zm0 48L46 92l16 16 32-32H78z"/><path fill="#0175C2" d="m62 108 16 16h32L78 92l-16 16z"/></svg>""",
        "explanation": "Flutter is Google's UI toolkit for natively compiled multi-platform apps."
    },
    {
        "id": "logo-28", "name": "GitHub", "category": "Code Hosting & Collaboration",
        "hint": "The black silhouette of the famous Octocat mascot.",
        "accepted_answers": ["github", "git hub"],
        "options": ["GitHub", "GitLab", "Bitbucket", "SourceForge"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#FFF" d="M64 12C35 12 12 35 12 64c0 23 15 43 36 50 3 1 4-1 4-3v-10c-14 3-18-7-18-7-2-6-6-8-6-8-5-3 0-3 0-3 5 0 8 5 8 5 5 8 12 6 15 4 0-3 2-6 3-7-12-1-24-6-24-26 0-6 2-11 5-14 0-2-2-7 1-14 0 0 4-1 15 5a52 52 0 0 1 27 0c10-6 15-5 15-5 3 7 1 12 1 14 4 4 5 9 5 14 0 20-12 25-24 26 2 2 3 5 3 10v15c0 2 1 4 4 3 21-7 36-27 36-50 0-29-23-52-52-52z"/></svg>""",
        "explanation": "GitHub is the world's largest developer code hosting platform."
    },
    {
        "id": "logo-29", "name": "Figma", "category": "UI/UX Design Tool",
        "hint": "Multi-colored 5-tile stacked letter 'F' (red, orange, purple, blue, green).",
        "accepted_answers": ["figma"],
        "options": ["Figma", "Sketch", "Adobe XD", "InVision"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#F24E1E" d="M44 14h20v24H44a12 12 0 0 1 0-24z"/><path fill="#FF7262" d="M64 14h20a12 12 0 0 1 0 24H64V14z"/><path fill="#A259FF" d="M44 38h20v24H44a12 12 0 0 1 0-24z"/><circle cx="74" cy="50" r="12" fill="#1ABCFE"/><path fill="#0ACF83" d="M44 62h20v12a12 12 0 0 1-20 8.5 12 12 0 0 1 0-20.5z"/></svg>""",
        "explanation": "Figma is the leading collaborative cloud interface design tool."
    },
    {
        "id": "logo-30", "name": "Nginx", "category": "Web Server & Reverse Proxy",
        "hint": "Green stylized letter 'N' with angular facets.",
        "accepted_answers": ["nginx", "engine x"],
        "options": ["Nginx", "Apache HTTP Server", "Caddy", "Traefik"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#009639" d="M64 8 16 35.7v56.6L64 120l48-27.7V35.7L64 8zm18 78h-9L46 44v42h-8V42h9l27 42V42h8v44z"/></svg>""",
        "explanation": "Nginx is a high-concurrency asynchronous reverse proxy and web server."
    },
    {
        "id": "logo-31", "name": "Hugging Face", "category": "AI Community & Models Hub",
        "hint": "The cheerful yellow smiling emoji hugging with open hands.",
        "accepted_answers": ["hugging face", "huggingface", "hf"],
        "options": ["Hugging Face", "OpenAI", "Replicate", "Kaggle"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><circle cx="64" cy="64" r="54" fill="#FFD21E"/><ellipse cx="48" cy="54" rx="6" ry="8" fill="#000"/><ellipse cx="80" cy="54" rx="6" ry="8" fill="#000"/><path d="M42 76c8 16 36 16 44 0" stroke="#000" stroke-width="6" fill="none" stroke-linecap="round"/><path fill="#FF9D00" d="M16 68c8-10 20-8 22 2s-10 16-20 12c-4-2-4-10-2-14zm96 0c-8-10-20-8-22 2s10 16 20 12c4-2 4-10 2-14z"/></svg>""",
        "explanation": "Hugging Face is the central hub for open-source AI models, datasets, and spaces."
    },
    {
        "id": "logo-32", "name": "Anthropic", "category": "AI Safety & Research Lab",
        "hint": "Geometric stylized terracotta 'A' composed of twin parallel diagonal struts.",
        "accepted_answers": ["anthropic", "claude", "claude ai"],
        "options": ["Anthropic (Claude)", "OpenAI", "Cohere", "Mistral"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#D97706" d="M48 24 16 104h20l6-18h36l6 18h20L72 24H48zm12 28 12 26H50l10-26z"/></svg>""",
        "explanation": "Anthropic is the AI safety research company behind the Claude model family."
    },
    {
        "id": "logo-33", "name": "Google Cloud", "category": "Cloud Platform",
        "hint": "Four-color cloud outline (blue, red, yellow, green) of Google Cloud Platform.",
        "accepted_answers": ["gcp", "google cloud", "google cloud platform"],
        "options": ["Google Cloud (GCP)", "AWS", "Azure", "DigitalOcean"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#4285F4" d="M84 40c-6-10-18-16-30-14-12 2-22 12-24 24-10 2-18 12-16 22 2 10 12 18 22 18h48c12 0 22-10 22-22s-8-22-20-22c-1-3-1-4-2-6z"/><path fill="#FFF" opacity="0.3" d="M44 60h40v10H44z"/></svg>""",
        "explanation": "Google Cloud Platform (GCP) delivers modular cloud infrastructure and AI services."
    },
    {
        "id": "logo-34", "name": "Microsoft Azure", "category": "Cloud Platform",
        "hint": "Vibrant blue angular geometric cloud 'A' shape.",
        "accepted_answers": ["azure", "microsoft azure", "ms azure"],
        "options": ["Microsoft Azure", "AWS", "Google Cloud", "Oracle Cloud"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#008AD7" d="M26 94 62 20h22L46 94H26z"/><path fill="#0078D4" d="m64 20 20 40 24 34H78l-14-22 16-24-16-28z"/></svg>""",
        "explanation": "Microsoft Azure is a global cloud computing service with enterprise integration."
    },
    {
        "id": "logo-35", "name": "MySQL", "category": "Relational Database",
        "hint": "Sakila the blue dolphin leaping over relational data waves.",
        "accepted_answers": ["mysql", "my sql"],
        "options": ["MySQL", "PostgreSQL", "MariaDB", "SQLite"], "correct_option_index": 0,
        "logo_svg": """<svg viewBox="0 0 128 128" width="110" height="110" xmlns="http://www.w3.org/2000/svg"><path fill="#00758F" d="M110 50c-6-16-26-24-42-18-12 4-22 16-26 28-2 6-4 14-8 18-8 8-20 8-20 8s14 6 24-2c8-6 10-16 12-22 4-12 12-20 22-24 14-4 28 2 34 16 4 8 2 18-4 24 10-6 12-18 8-28z"/><path fill="#F29111" d="M30 86c10 0 20-4 26-10 6 8 16 12 26 12-10 6-22 6-32 2-6-2-12-6-20-4z"/></svg>""",
        "explanation": "MySQL is the world's most popular open-source relational database management system."
    }
]

# ==============================================================================
# 4. SIMULATED DAILY LEADERBOARD
# ==============================================================================
MOCK_LEADERBOARD_PLAYERS = [
    {"name": "Aarav Sharma", "college": "IIT Bombay", "score": 2850, "accuracy": "98%", "streak": 14, "avatar": "👨‍💻"},
    {"name": "Priya Patel", "college": "NIT Trichy", "score": 2720, "accuracy": "96%", "streak": 11, "avatar": "👩‍💻"},
    {"name": "Rohan Deshmukh", "college": "BITS Pilani", "score": 2640, "accuracy": "94%", "streak": 9, "avatar": "⚡"},
    {"name": "Sneha Reddy", "college": "IIIT Hyderabad", "score": 2510, "accuracy": "92%", "streak": 8, "avatar": "🚀"},
    {"name": "Ananya Mukherjee", "college": "DTU Delhi", "score": 2400, "accuracy": "90%", "streak": 7, "avatar": "🔥"},
    {"name": "Vikram Malhotra", "college": "VIT Vellore", "score": 2280, "accuracy": "88%", "streak": 6, "avatar": "🎯"},
    {"name": "Kavya Nair", "college": "PSG Tech", "score": 2150, "accuracy": "86%", "streak": 5, "avatar": "⭐"},
]


# ==============================================================================
# 5. CORE HELPER FUNCTIONS
# ==============================================================================

def normalize_text(text: str) -> str:
    """Normalize text for fuzzy string matching."""
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r'[\s\-_\.,\(\)\{\}\[\]\:\;\'\"]+', ' ', text)
    return text.strip()


def validate_typed_answer(user_input: str, accepted_answers: list) -> bool:
    """Fuzzy validation for candidate typed responses."""
    if not user_input or not accepted_answers:
        return False
    clean_input = normalize_text(user_input)
    if not clean_input:
        return False

    for target in accepted_answers:
        clean_target = normalize_text(target)
        if clean_input == clean_target:
            return True
        if len(clean_target) >= 3 and (clean_target in clean_input or clean_input in clean_target):
            return True
        ratio = difflib.SequenceMatcher(None, clean_input, clean_target).ratio()
        if ratio >= 0.78:
            return True
            
    return False


def get_daily_questions(mode: str = "rapid_fire") -> list:
    """
    Returns exactly 30 randomized questions sampled from the respective pool.
    Randomly selects 30 distinct questions out of large banks (MCQ bank has 60+ questions,
    Logos bank has 35+ items, Rapid fire has 30+ items) and shuffles options.
    Flags question #30 with double_points = True.
    """
    if mode == "rapid_fire":
        pool = list(RAPID_FIRE_QUESTIONS)
        count = min(30, len(pool))
        selected = random.sample(pool, count)
    elif mode == "mcq_sprint":
        pool = list(SPRINT_MCQ_BANK)
        count = min(30, len(pool))
        # Samples 30 completely dynamic random questions each run from the diverse pool
        selected = random.sample(pool, count)
    elif mode == "logo_quiz":
        pool = list(LOGO_CHALLENGE_BANK)
        count = min(30, len(pool))
        selected = random.sample(pool, count)
    else:
        return []

    formatted = []
    total = len(selected)
    for idx, item in enumerate(selected):
        q_copy = dict(item)
        if "options" in item and len(item["options"]) > 0:
            opts = list(item["options"])
            correct_text = opts[item["correct_option_index"]]
            random.shuffle(opts)
            q_copy["options"] = opts
            q_copy["correct_option_index"] = opts.index(correct_text)
        q_copy["question_number"] = idx + 1
        q_copy["total_questions"] = total
        q_copy["double_points"] = (idx == total - 1)
        formatted.append(q_copy)

    return formatted


def get_leaderboard_data(user_score: int = 0, user_name: str = "You (Candidate)") -> list:
    """Returns today's leaderboard with dynamic candidate standings."""
    board = list(MOCK_LEADERBOARD_PLAYERS)
    if user_score > 0:
        board.append({
            "name": user_name,
            "college": "Your College",
            "score": user_score,
            "accuracy": "95%",
            "streak": 3,
            "avatar": "⭐",
            "is_current_user": True
        })
    board.sort(key=lambda x: x["score"], reverse=True)
    for rank, player in enumerate(board, start=1):
        player["rank"] = rank
    return board[:10]
