# ==============================================================================
# COMPANY KNOWLEDGE METADATA — Structured Intelligence for AI Question Generation
# NO hardcoded questions. Only topics, patterns, and focus areas.
# Questions are generated dynamically by Gemini AI using this metadata.
# ==============================================================================

COMPANY_KNOWLEDGE = {
    "TCS": {
        "full_name": "TCS (Tata Consultancy Services)",
        "role": "Software Engineer",
        "topics": {
            "Easy": [
                "Java basics (JDK vs JRE vs JVM)", "OOP four pillars (Encapsulation, Abstraction, Inheritance, Polymorphism)",
                "SQL SELECT, INSERT, UPDATE, DELETE", "Primary Key vs Unique Key", "HTTP vs HTTPS (port 80 vs 443)",
                "Array vs ArrayList in Java", "Basic data types and variables", "For loop and while loop syntax",
                "String manipulation basics", "Simple project walkthrough (2 minutes)"
            ],
            "Medium": [
                "SQL 2nd highest salary query (subquery and DENSE_RANK)", "INNER JOIN vs LEFT JOIN vs RIGHT JOIN",
                "Process vs Thread in OS", "Deadlock conditions (Mutual Exclusion, Hold & Wait, No Preemption, Circular Wait)",
                "REST API design (GET, POST, PUT, DELETE)", "JWT authentication flow (header.payload.signature)",
                "B-Tree indexing for query optimization", "Exception handling (checked vs unchecked in Java)",
                "HashMap internal working", "DBMS Normalization (1NF, 2NF, 3NF)",
                "MVC architecture pattern", "HTTP status codes (200, 201, 401, 404, 500)"
            ],
            "Hard": [
                "Oracle/MySQL query optimization over 20M+ rows", "Database sharding and horizontal partitioning",
                "Microservices DB-per-service pattern", "Table partitioning (range, hash, list)",
                "Write Concern and Read Preference in distributed DB", "CAP Theorem trade-offs",
                "Spring Boot microservices architecture", "API Gateway and service mesh patterns",
                "Distributed caching with Redis cluster", "Zero-downtime database migration"
            ]
        },
        "coding_focus": {
            "Easy": ["Palindrome check", "Reverse a string with loop", "Fibonacci series", "Factorial using recursion", "Check prime number"],
            "Medium": ["Two Sum using HashMap O(N)", "Binary Search on sorted array", "Stack-based balanced parentheses", "Linked List reversal", "SQL complex joins query"],
            "Hard": ["LRU Cache design (HashMap + DoublyLinkedList)", "Trie for autocomplete", "Graph BFS/DFS traversal", "Dynamic Programming (knapsack, LCS)", "Rate limiter design"]
        },
        "behavioral_focus": {
            "Easy": ["Self-introduction", "Tell me about your project", "Why this company", "Strengths and weaknesses"],
            "Medium": ["Team conflict resolution", "Deadline pressure handling", "Disagreement with manager", "Failure and learning"],
            "Hard": ["Client escalation management", "Leadership in crisis", "Ethical dilemma at work", "Cross-team dependency resolution"]
        },
        "interview_style": {
            "Easy": "Friendly and encouraging, testing basic programming and CS fundamentals only",
            "Medium": "Professional corporate interviewer probing Java, SQL, OOP reasoning with structured follow-ups",
            "Hard": "Strict senior enterprise architect demanding precise technical depth on database tuning and microservices"
        },
        "hiring_pattern": "NQT Aptitude Test → Technical Interview I → Technical Interview II → Managerial Round → HR Round. Heavy focus on Java, SQL query writing, OOP concepts, and project discussion.",
        "project_questions": [
            "Architecture and tech stack choices", "Database schema design decisions", "Authentication implementation",
            "API endpoint design", "Deployment strategy", "Challenges faced and how resolved",
            "Scalability considerations", "Security measures implemented"
        ]
    },

    "Amazon": {
        "full_name": "Amazon",
        "role": "Software Development Engineer (SDE)",
        "topics": {
            "Easy": [
                "Python/Java basic syntax", "Array and string manipulation", "Hash Map fundamentals",
                "Time complexity basics (O(N), O(N^2), O(log N))", "Basic OOP concepts",
                "Simple data structure operations (stack, queue)"
            ],
            "Medium": [
                "Sliding Window technique", "Two Pointers approach", "Binary Tree traversals (inorder, preorder, postorder)",
                "Graph BFS/DFS", "HashMap collision handling", "AWS DynamoDB vs S3 architecture",
                "Optimistic locking and eventual consistency", "Amazon Leadership Principles (Customer Obsession, Ownership, Dive Deep)",
                "REST API rate limiting", "System Design basics (URL shortener, parking lot)"
            ],
            "Hard": [
                "Distributed system design at Prime Day scale (100K+ orders/sec)", "SQS/Kafka event streaming architecture",
                "DynamoDB auto-scaling and partition key design", "Distributed locking with Redis/Zookeeper",
                "Idempotency in payment processing", "Consistent hashing for load balancing",
                "Multi-region failover and disaster recovery", "Service mesh and circuit breaker patterns"
            ]
        },
        "coding_focus": {
            "Easy": ["Valid Anagram", "Two Sum", "Reverse Linked List", "Valid Parentheses", "Maximum Subarray"],
            "Medium": ["Longest Substring Without Repeating Characters", "LRU Cache", "Merge Intervals", "Course Schedule (topological sort)", "Word Search in grid"],
            "Hard": ["Median of Two Sorted Arrays", "Serialize/Deserialize Binary Tree", "Word Ladder II", "Minimum Window Substring", "Design Search Autocomplete"]
        },
        "behavioral_focus": {
            "Easy": ["Tell me about yourself", "Why Amazon", "Describe a project you're proud of"],
            "Medium": ["Customer Obsession STAR story", "Ownership — going beyond job scope", "Dive Deep — debugging complex issue", "Disagree and Commit"],
            "Hard": ["Have Backbone — pushing back on leadership", "Invent and Simplify — innovative solution", "Bias for Action — decision under ambiguity", "Earn Trust — rebuilding after failure"]
        },
        "interview_style": {
            "Easy": "Friendly recruiter checking coding basics and communication",
            "Medium": "Fast-paced SDM evaluating DSA problem-solving and Leadership Principles via STAR method",
            "Hard": "Strict Bar Raiser probing hard algorithms, distributed AWS architecture, and deep LP trade-offs"
        },
        "hiring_pattern": "Online Assessment (OA) → Phone Screen → On-site Loop (4-5 rounds: 2 Coding + 1 System Design + 1 Behavioral + 1 Bar Raiser). Every round evaluates at least one Leadership Principle.",
        "project_questions": [
            "Scalability of your project", "How you handle data consistency", "Performance bottlenecks encountered",
            "Trade-offs you made and why", "How you'd redesign with more time", "Monitoring and alerting strategy"
        ]
    },

    "Google": {
        "full_name": "Google",
        "role": "Software Engineer (L3/L4)",
        "topics": {
            "Easy": [
                "Array manipulation", "String processing", "Basic sorting algorithms",
                "Time and space complexity analysis", "Hash tables", "Two pointer technique"
            ],
            "Medium": [
                "Graph algorithms (BFS, DFS, Dijkstra)", "Binary tree operations", "Dynamic Programming (memoization vs tabulation)",
                "Backtracking", "Trie data structure", "Union-Find (Disjoint Set)",
                "Heap/Priority Queue operations", "Sliding window and monotonic stack"
            ],
            "Hard": [
                "Trie autocomplete engine serving 200K QPS with sub-10ms SLA", "Zero-lock concurrency with RCU",
                "MapReduce and distributed data processing", "Consistent hashing",
                "Design Google Search ranking pipeline", "Real-time stream processing at scale",
                "Consensus protocols (Paxos, Raft)", "Global distributed database design (Spanner-like)"
            ]
        },
        "coding_focus": {
            "Easy": ["Remove duplicates from sorted array", "Valid palindrome", "Merge two sorted lists", "Binary search", "Climbing stairs"],
            "Medium": ["Number of Islands (grid BFS/DFS)", "Coin Change (DP)", "Longest Palindromic Substring", "Kth Largest Element", "Word Break"],
            "Hard": ["Alien Dictionary (topological sort)", "Trapping Rain Water", "Regular Expression Matching", "Largest Rectangle in Histogram", "Critical Connections in Network"]
        },
        "behavioral_focus": {
            "Easy": ["Why Google", "Describe a technical challenge"],
            "Medium": ["Googleyness — collaboration and humility", "Ambiguity handling", "Cross-functional teamwork"],
            "Hard": ["Leading without authority", "Navigating organizational complexity", "Impact at scale"]
        },
        "interview_style": {
            "Easy": "Encouraging university recruiter testing clean code and math logic",
            "Medium": "Analytical senior SWE probing data structures, time complexity SLAs, and clean code",
            "Hard": "Rigorous Staff Fellow demanding Hard DP, Tries, Latency SLAs, and zero-lock concurrency"
        },
        "hiring_pattern": "Phone Screen (1 coding) → On-site (4-5 rounds: 3 Coding + 1 System Design + 1 Googleyness/Behavioral). Focus on algorithmic thinking, code quality, and scalable system design.",
        "project_questions": [
            "System architecture decisions", "Algorithm optimization choices", "How you measured performance",
            "Edge cases you handled", "How you'd scale 100x"
        ]
    },

    "Microsoft": {
        "full_name": "Microsoft",
        "role": "Software Engineer",
        "topics": {
            "Easy": [
                "C#/Java OOP basics", "Value Types vs Reference Types", "Stack vs Heap memory",
                "Basic data structures", "ref vs out parameters in C#", "Simple coding problems"
            ],
            "Medium": [
                "Dependency Injection (Transient vs Scoped vs Singleton)", ".NET Core middleware pipeline",
                "Azure App Service deployment", "Azure SQL and Cosmos DB", "SOLID principles in practice",
                "Design patterns (Factory, Observer, Strategy)", "REST API versioning", "Unit testing with xUnit/NUnit"
            ],
            "Hard": [
                "Real-time media streaming (WebRTC, SFU)", "Azure Event Hubs telemetry at scale",
                "Distributed microservices on Azure Kubernetes Service", "Forward Error Correction (FEC) for UDP",
                "Global data replication and conflict resolution", "Zero-trust security architecture",
                "Low-level concurrency (lock-free data structures)"
            ]
        },
        "coding_focus": {
            "Easy": ["Reverse string", "FizzBuzz", "Array rotation", "Check palindrome", "Fibonacci sequence"],
            "Medium": ["Binary Search Tree operations", "Flatten nested list", "LRU Cache", "Graph cycle detection", "Decode Ways (DP)"],
            "Hard": ["Design Excel formula engine", "Concurrent queue implementation", "Skip List", "B-Tree operations", "Stream median"]
        },
        "behavioral_focus": {
            "Easy": ["Growth mindset examples", "Why Microsoft", "Team collaboration"],
            "Medium": ["Handling ambiguous requirements", "Giving and receiving feedback", "Driving results"],
            "Hard": ["Strategic thinking and vision", "Cross-org influence", "Customer empathy at scale"]
        },
        "interview_style": {
            "Easy": "Friendly college recruiter checking OOP basics and growth mindset",
            "Medium": "Collaborative senior engineer discussing C#, .NET, Azure, and OOP design",
            "Hard": "Strict Azure Partner Architect probing distributed microservices, concurrency, and cloud security"
        },
        "hiring_pattern": "Online Assessment → Phone Screen → On-site (4-5 rounds: Coding + Design + Behavioral + As-Appropriate). Growth mindset is valued across all rounds.",
        "project_questions": [
            "How you'd integrate with Azure services", "CI/CD pipeline design", "Testing strategy",
            "Security considerations", "Accessibility in your application"
        ]
    },

    "Deloitte": {
        "full_name": "Deloitte Consulting",
        "role": "Analyst / Consultant",
        "topics": {
            "Easy": [
                "SQL basics (SELECT, WHERE, GROUP BY, HAVING)", "Difference between WHERE and HAVING",
                "Basic Python syntax", "Data types and structures", "Excel formulas and pivot tables",
                "Basic logical reasoning"
            ],
            "Medium": [
                "Complex SQL queries (subqueries, window functions, CTEs)", "Python data analysis with pandas",
                "Business case framework (MECE, profitability)", "Guesstimate questions (market sizing)",
                "Data visualization best practices (Tableau/Power BI)", "ETL pipeline concepts",
                "Statistical analysis basics", "Revenue decomposition frameworks"
            ],
            "Hard": [
                "Enterprise data warehouse design (Star schema, Snowflake schema)", "PySpark distributed processing",
                "Snowflake/Redshift architecture", "GDPR data masking and compliance",
                "Real-time analytics pipeline (Kafka + Spark Streaming)", "Cloud data lake architecture",
                "Machine learning model deployment", "Executive strategy presentation"
            ]
        },
        "coding_focus": {
            "Easy": ["SQL GROUP BY queries", "Python list operations", "String formatting", "Basic math operations"],
            "Medium": ["SQL window functions (ROW_NUMBER, RANK)", "Python pandas transformations", "Data cleaning scripts", "Regex pattern matching"],
            "Hard": ["PySpark data pipeline", "Complex multi-table SQL optimization", "Python ETL automation", "Statistical model implementation"]
        },
        "behavioral_focus": {
            "Easy": ["Why consulting", "Teamwork example", "Communication skills"],
            "Medium": ["Client conflict resolution", "Stakeholder management", "Presenting data-driven insights"],
            "Hard": ["Managing ambiguous client requirements", "Executive-level presentation", "Cross-functional team leadership"]
        },
        "interview_style": {
            "Easy": "Friendly campus analyst recruiter checking logical reasoning and basic analytics",
            "Medium": "Structured management consultant assessing guesstimates, business case logic, and SQL",
            "Hard": "Senior Digital Director probing enterprise data warehousing, cloud architecture, and executive strategy"
        },
        "hiring_pattern": "Online Assessment (aptitude + coding) → Case Study Interview → Technical Interview → Partner/Director Round. Strong focus on structured thinking and communication.",
        "project_questions": [
            "How you derived insights from data", "Tools used for analysis", "Impact measurement",
            "Presentation of findings", "Stakeholder communication approach"
        ]
    },

    "Accenture": {
        "full_name": "Accenture",
        "role": "Associate Software Engineer",
        "topics": {
            "Easy": [
                "Agile vs Waterfall SDLC", "User Stories and Sprints", "Basic HTML/CSS/JavaScript",
                "HTTP methods (GET, POST, PUT, DELETE)", "Version control (Git basics)", "Basic Java/Python syntax"
            ],
            "Medium": [
                "CORS handling in REST APIs", "Spring Boot REST service development", "JWT Bearer token security",
                "Microservices communication patterns", "Docker containerization basics",
                "CI/CD pipeline concepts", "Cloud deployment fundamentals (AWS/Azure)"
            ],
            "Hard": [
                "Multi-cloud migration strategy", "Blue/Green and Canary deployment", "GitHub Actions/Jenkins CI/CD pipeline design",
                "Kubernetes orchestration", "Service mesh (Istio)", "Enterprise security architecture",
                "Cloud cost optimization", "Infrastructure as Code (Terraform)"
            ]
        },
        "coding_focus": {
            "Easy": ["FizzBuzz", "String reverse", "Array sorting", "Basic CRUD operations"],
            "Medium": ["REST API implementation", "Database CRUD with ORM", "File processing script", "JSON parsing and transformation"],
            "Hard": ["Microservice communication design", "Event-driven architecture implementation", "Distributed cache design"]
        },
        "behavioral_focus": {
            "Easy": ["Adaptability", "Learning agility", "Why Accenture"],
            "Medium": ["Client-facing communication", "Cross-cultural teamwork", "Innovation mindset"],
            "Hard": ["Change management leadership", "Digital transformation vision", "Stakeholder alignment"]
        },
        "interview_style": {
            "Easy": "Friendly associate recruiter checking web basics and communication",
            "Medium": "Pragmatic Application Development Lead assessing full-stack web, REST APIs, and Agile",
            "Hard": "Strict Global Technology Principal evaluating cloud microservices, DevOps, and enterprise security"
        },
        "hiring_pattern": "Online Assessment → Technical Interview → HR Interview. Focus on adaptability, full-stack web knowledge, and Agile methodology.",
        "project_questions": [
            "Agile practices used", "Team collaboration tools", "How you handled requirement changes",
            "Testing approach", "Deployment process"
        ]
    },

    "Infosys": {
        "full_name": "Infosys",
        "role": "Systems Engineer",
        "topics": {
            "Easy": [
                "Java String immutability and String Pool", "Basic OOP concepts",
                "SQL DDL vs DML commands", "Python basic syntax", "Array vs LinkedList",
                "Basic networking (TCP/IP, DNS)"
            ],
            "Medium": [
                "Banker's Algorithm for deadlock avoidance", "SQL GROUP BY with HAVING",
                "Java Collections framework (ArrayList vs LinkedList vs HashMap)",
                "Multithreading synchronization", "DBMS Normalization (1NF through BCNF)",
                "Design Patterns (Singleton, Factory)", "REST API error handling"
            ],
            "Hard": [
                "Spring Boot Circuit Breaker (Resilience4j)", "API Gateway routing and load balancing",
                "Distributed tracing with Zipkin/Jaeger", "Kafka message streaming",
                "Microservices saga pattern", "Database replication and consistency"
            ]
        },
        "coding_focus": {
            "Easy": ["String reversal", "Pattern printing", "Array sum", "Prime number check", "Factorial"],
            "Medium": ["Binary search implementation", "Stack operations", "Queue using two stacks", "Sorting algorithms comparison"],
            "Hard": ["Graph shortest path", "Dynamic programming problems", "Tree serialization", "Concurrent data structure design"]
        },
        "behavioral_focus": {
            "Easy": ["Self-introduction", "Educational background", "Why IT industry"],
            "Medium": ["Handling tight deadlines", "Learning new technology quickly", "Team collaboration"],
            "Hard": ["Technical leadership", "Process improvement", "Mentoring juniors"]
        },
        "interview_style": {
            "Easy": "Encouraging technical assessor checking basic syntax and OOP principles",
            "Medium": "Structured technology lead testing Java/Python, OOPs pillars, DBMS queries, OS threads",
            "Hard": "Rigorous Principal Architect probing enterprise Spring Boot, microservice design, and high availability"
        },
        "hiring_pattern": "InfyTQ Assessment → Technical Interview → HR Interview. Strong focus on Java, DBMS, OS, and networking fundamentals.",
        "project_questions": [
            "Project architecture overview", "Database design decisions", "Challenges and solutions",
            "Team size and your contribution", "Technologies learned during project"
        ]
    },

    "Capgemini": {
        "full_name": "Capgemini",
        "role": "Analyst / Associate Consultant",
        "topics": {
            "Easy": [
                "Java basics (variables, loops, conditionals)", "Method Overloading vs Method Overriding",
                "SQL basic queries", "OOP Polymorphism", "Basic data types"
            ],
            "Medium": [
                "Composite Primary Key in SQL", "REST API endpoint design", "Foreign Key constraints",
                "Java exception handling", "JDBC database connectivity", "MVC pattern",
                "Basic Spring Boot concepts"
            ],
            "Hard": [
                "Legacy monolith to Docker/Kubernetes refactoring", "Cloud migration patterns (Strangler Fig)",
                "Multi-stage Docker builds", "Kubernetes Ingress and service discovery",
                "API security (OAuth2, API keys)", "Microservices governance"
            ]
        },
        "coding_focus": {
            "Easy": ["Palindrome check", "Armstrong number", "Array sorting", "String operations"],
            "Medium": ["SQL multi-table joins", "Java CRUD application", "Linked list operations", "Stack implementation"],
            "Hard": ["Distributed system design", "Cache eviction policies", "Load balancer algorithm"]
        },
        "behavioral_focus": {
            "Easy": ["Tell about yourself", "Why Capgemini", "Career goals"],
            "Medium": ["Project contribution", "Handling feedback", "Team dynamics"],
            "Hard": ["Client relationship management", "Technical decision ownership", "Innovation proposal"]
        },
        "interview_style": {
            "Easy": "Friendly junior recruiter checking basic Java and SQL syntax",
            "Medium": "Structured Senior Project Manager evaluating Java, SQL joins, project contributions",
            "Hard": "Strict Enterprise Cloud Practice Director probing cloud migration, API security, and microservice governance"
        },
        "hiring_pattern": "Online Test → Technical Interview → HR Interview. Focus on Java, SQL, OOP, and project discussion.",
        "project_questions": [
            "Project overview and your role", "Technologies used and why", "Database design",
            "Biggest challenge faced", "What you'd do differently"
        ]
    },

    "Meta": {
        "full_name": "Meta (Facebook)",
        "role": "Software Engineer / Production Engineer",
        "topics": {
            "Easy": [
                "React basics (components, props, state)", "Virtual DOM and reconciliation",
                "JavaScript ES6 features (arrow functions, destructuring, promises)",
                "HTML5 semantic elements", "CSS Flexbox and Grid", "Basic HTTP concepts"
            ],
            "Medium": [
                "GraphQL vs REST (over-fetching, under-fetching)", "React custom hooks and state management",
                "React performance optimization (memo, useMemo, useCallback)",
                "Node.js event loop", "WebSocket real-time communication",
                "Database indexing for social graphs", "Caching strategies"
            ],
            "Hard": [
                "News Feed architecture for 1B+ daily active users", "Fan-out on write vs Fan-out on read",
                "GraphQL query optimization and N+1 problem", "Custom React Virtual DOM implementation",
                "Distributed social graph storage", "Real-time notification system at scale",
                "Content delivery network (CDN) design", "Privacy-preserving data processing"
            ]
        },
        "coding_focus": {
            "Easy": ["Array manipulation", "String processing", "Basic tree traversal", "Hash map usage"],
            "Medium": ["Binary tree operations", "Graph traversal", "Dynamic programming", "Interval scheduling"],
            "Hard": ["Design type-ahead search", "Implement simplified React renderer", "Distributed counter", "Rate limiter"]
        },
        "behavioral_focus": {
            "Easy": ["Why Meta", "Collaboration example", "Learning from failure"],
            "Medium": ["Building community", "Moving fast with purpose", "Open feedback culture"],
            "Hard": ["Scaling impact", "Bold decision-making", "Meta values alignment"]
        },
        "interview_style": {
            "Easy": "Friendly university recruiter checking basic frontend HTML/CSS/JS",
            "Medium": "Direct Production Engineering Manager probing React, high-scale APIs, and distributed systems",
            "Hard": "Strict Infrastructure Staff Engineer probing GraphQL efficiency, custom Virtual DOM, and 1B QPS systems"
        },
        "hiring_pattern": "Initial Screen → Phone Interview → On-site (Coding × 2 + System Design + Behavioral). Focus on coding speed, system design breadth, and Meta values.",
        "project_questions": [
            "Frontend architecture decisions", "State management approach", "Performance optimizations",
            "How you'd handle 10x traffic", "User experience considerations"
        ]
    },

    "Netflix": {
        "full_name": "Netflix",
        "role": "Senior Software Engineer",
        "topics": {
            "Easy": [
                "Java memory model (Stack vs Heap)", "Garbage Collection basics",
                "Object-oriented principles", "Basic concurrency concepts",
                "RESTful API basics", "HTTP status codes"
            ],
            "Medium": [
                "Service Discovery (Netflix Eureka / Consul)", "Client-side load balancing (Ribbon)",
                "Spring Cloud configuration management", "Circuit Breaker pattern",
                "Event-driven architecture", "Microservices communication (sync vs async)",
                "Database connection pooling (HikariCP)"
            ],
            "Hard": [
                "Chaos Engineering (Chaos Monkey, Simian Army)", "4K video streaming pipeline across global CDNs",
                "Multi-bitrate HLS/DASH chunking", "Zero-downtime deployment with traffic shifting",
                "Kafka event streaming at Netflix scale", "Multi-region active-active failover",
                "Adaptive bitrate streaming algorithms", "Content recommendation system design"
            ]
        },
        "coding_focus": {
            "Easy": ["Array operations", "String manipulation", "Basic recursion", "Simple data structures"],
            "Medium": ["Binary tree operations", "Graph traversal", "HashMap design", "Sorting algorithm optimization"],
            "Hard": ["Distributed consensus implementation", "Event sourcing system", "Stream processing pipeline", "Consistent hashing ring"]
        },
        "behavioral_focus": {
            "Easy": ["Culture alignment (Freedom & Responsibility)", "Self-motivation", "Why Netflix"],
            "Medium": ["Independent decision-making", "Context over control", "Candid feedback examples"],
            "Hard": ["High-performance culture fit", "Strategic risk-taking", "Organizational impact"]
        },
        "interview_style": {
            "Easy": "Candid talent specialist checking basic programming and culture alignment",
            "Medium": "Senior architect probing chaos engineering, Spring Boot, high availability, and microservice resilience",
            "Hard": "Strict Infrastructure VP probing zero-downtime chaos engineering, Kafka streaming, and multi-region failover"
        },
        "hiring_pattern": "Recruiter Screen → Phone Technical → On-site (5-6 rounds focused on culture, coding, and system design). Netflix values candor, independence, and high performance.",
        "project_questions": [
            "Resilience and fault tolerance approach", "How you handle failures gracefully",
            "Monitoring and observability strategy", "Performance benchmarking"
        ]
    },

    "Adobe": {
        "full_name": "Adobe",
        "role": "Software Development Engineer",
        "topics": {
            "Easy": [
                "C++ pointers vs references", "Dangling pointers and memory leaks",
                "Basic OOP (classes, objects, constructors)", "Stack vs Heap memory allocation",
                "Java vs C++ comparison", "Basic I/O operations"
            ],
            "Medium": [
                "Command Pattern for Undo/Redo (Photoshop/Acrobat)", "Stack data structure for operation history",
                "OOP Design Patterns (Observer, Strategy, Factory)", "Binary Search Tree operations",
                "Recursion and backtracking", "Memory management and smart pointers",
                "File format parsing"
            ],
            "Hard": [
                "QuadTree / R-Tree spatial indexing for vector graphics", "Rendering pipeline optimization",
                "O(N^2) to O(N log N) collision detection optimization", "GPU shader programming concepts",
                "Real-time collaborative editing (CRDT/OT)", "Image processing algorithms",
                "PDF rendering engine architecture"
            ]
        },
        "coding_focus": {
            "Easy": ["Array rotation", "String manipulation in C++", "Pointer arithmetic", "Matrix operations"],
            "Medium": ["BST insert/delete/search", "Stack-based expression evaluation", "Linked list cycle detection", "Backtracking (N-Queens, Sudoku)"],
            "Hard": ["QuadTree implementation", "Graph-based rendering optimization", "Custom memory allocator", "Spatial hashing"]
        },
        "behavioral_focus": {
            "Easy": ["Creative problem-solving", "Why Adobe", "Passion for design tools"],
            "Medium": ["User-centric design thinking", "Innovation examples", "Cross-team collaboration"],
            "Hard": ["Technical vision and roadmap", "Performance culture", "Mentorship and growth"]
        },
        "interview_style": {
            "Easy": "Friendly recruiter checking basic C++/Java syntax and OOP",
            "Medium": "Analytical SDE probing DSA, OOP class design, and practical problem solving",
            "Hard": "Strict Principal Computer Scientist probing complex C++ memory management, rendering algorithms, and hard DSA"
        },
        "hiring_pattern": "Online Test → Technical Phone Screen → On-site (3-4 rounds: DSA + OOP Design + System Design + HR). Strong focus on DSA and design patterns.",
        "project_questions": [
            "Design patterns used", "Performance optimizations", "Memory management approach",
            "User interface decisions", "Algorithm choices and trade-offs"
        ]
    },

    "IBM": {
        "full_name": "IBM",
        "role": "Application Developer",
        "topics": {
            "Easy": [
                "Java 8 features (default methods, lambda expressions, streams)",
                "Interface vs Abstract Class", "Basic SQL operations",
                "OOP fundamentals", "Basic cloud concepts"
            ],
            "Medium": [
                "ACID properties in database transactions", "Spring Data JPA @Transactional",
                "Transaction Isolation Levels", "Java Streams API",
                "RESTful web service design", "Cloud deployment basics (IBM Cloud)",
                "Containerization with Docker"
            ],
            "Hard": [
                "Red Hat OpenShift container orchestration", "Hybrid cloud API Gateway design",
                "Mutual TLS (mTLS) and OAuth2 security", "Mainframe-to-cloud integration",
                "Envoy/Istio service mesh", "Enterprise banking API security",
                "Quantum computing basics"
            ]
        },
        "coding_focus": {
            "Easy": ["Java basic programs", "SQL queries", "Array operations", "String processing"],
            "Medium": ["Java Collections operations", "Spring Boot CRUD API", "Binary tree traversal", "HashMap implementation"],
            "Hard": ["Distributed system design", "Event sourcing", "CQRS pattern implementation", "Security protocol design"]
        },
        "behavioral_focus": {
            "Easy": ["Why IBM", "Interest in enterprise technology", "Team player examples"],
            "Medium": ["Innovation in enterprise context", "Client relationship management", "Technical mentorship"],
            "Hard": ["Enterprise transformation leadership", "Stakeholder alignment", "Vision for cloud+AI integration"]
        },
        "interview_style": {
            "Easy": "Friendly technical recruiter checking DBMS and Java fundamentals",
            "Medium": "Structured Cloud and AI Lead evaluating Java, Spring, Cloud DBMS, and API design",
            "Hard": "Strict IBM Fellow probing enterprise hybrid cloud, Red Hat OpenShift, and high-security banking APIs"
        },
        "hiring_pattern": "Online Assessment → Technical Interview → Manager Interview → HR Round. Focus on Java, Spring, cloud concepts, and enterprise thinking.",
        "project_questions": [
            "Enterprise applicability of your project", "Cloud readiness", "Security considerations",
            "Integration with existing systems", "Data management approach"
        ]
    },

    "Wipro": {
        "full_name": "Wipro",
        "role": "Project Engineer",
        "topics": {
            "Easy": [
                "Python basics (List vs Tuple, dict, set)", "List comprehension",
                "Java basic syntax", "SQL SELECT queries", "Basic OOP",
                "Data types and variables"
            ],
            "Medium": [
                "Database Normalization (1NF, 2NF, 3NF, BCNF)", "Foreign Key constraints",
                "Java Collections (ArrayList, HashMap, TreeMap)", "SQL multi-table joins",
                "Basic design patterns", "REST API development", "Git version control"
            ],
            "Hard": [
                "Cloud migration using Strangler Fig pattern", "Monolith to microservices decomposition",
                "API Gateway design", "Database security and encryption",
                "Enterprise SDLC governance", "Performance testing and optimization"
            ]
        },
        "coding_focus": {
            "Easy": ["Python list operations", "String reversal", "Basic sorting", "Number pattern", "Prime check"],
            "Medium": ["SQL complex queries", "Java file I/O", "HashMap usage", "Linked list operations"],
            "Hard": ["System design components", "Database optimization query", "Distributed lock design"]
        },
        "behavioral_focus": {
            "Easy": ["Self-introduction", "Why Wipro", "Relocation readiness"],
            "Medium": ["Team conflict handling", "Learning from mistakes", "Adaptability"],
            "Hard": ["Technical leadership vision", "Process improvement", "Client management"]
        },
        "interview_style": {
            "Easy": "Friendly graduate trainee evaluator checking basic Python/Java and SQL",
            "Medium": "Structured Project Lead evaluating Java, Python, SQL, OOP, and project contributions",
            "Hard": "Strict Chief Technology Consultant probing cloud migration, database security, and enterprise SDLC"
        },
        "hiring_pattern": "WILP/Elite Assessment → Technical Interview → HR Interview. Focus on Java, Python, SQL, and project discussion.",
        "project_questions": [
            "Project functionality and architecture", "Your specific contribution", "Technologies chosen and why",
            "Testing approach", "Lessons learned"
        ]
    }
}


def get_company_knowledge(company_name):
    """
    Get structured knowledge metadata for a company.
    Returns the company's topics, coding focus, behavioral focus, interview style, and hiring patterns.
    This data is used to build dynamic AI prompts — NOT as complete questions.
    """
    return COMPANY_KNOWLEDGE.get(company_name, COMPANY_KNOWLEDGE.get("TCS"))


def get_all_company_names():
    """Get list of all company names in the knowledge base."""
    return list(COMPANY_KNOWLEDGE.keys())


def get_topic_list(company_name, difficulty="Medium"):
    """
    Get the topic list for a company at a specific difficulty level.
    Used to inject into AI prompts for targeted question generation.
    """
    knowledge = get_company_knowledge(company_name)
    topics = knowledge.get("topics", {})
    return topics.get(difficulty, topics.get("Medium", []))


def get_coding_focus(company_name, difficulty="Medium"):
    """
    Get coding problem focus areas for a company at a specific difficulty.
    """
    knowledge = get_company_knowledge(company_name)
    coding = knowledge.get("coding_focus", {})
    return coding.get(difficulty, coding.get("Medium", []))


def get_behavioral_focus(company_name, difficulty="Medium"):
    """
    Get behavioral/HR focus areas for a company at a specific difficulty.
    """
    knowledge = get_company_knowledge(company_name)
    behavioral = knowledge.get("behavioral_focus", {})
    return behavioral.get(difficulty, behavioral.get("Medium", []))
