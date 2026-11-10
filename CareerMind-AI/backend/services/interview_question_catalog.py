"""
Curated Interview Question Catalog for CareerMind AI Mock Interview Simulator.
Contains standardized, production-grade technical, behavioral, and project-based questions
with comprehensive evaluation rubrics, expected concepts, and suggested answer points.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class QuestionItem(BaseModel):
    """Normalized question definition within the question catalog."""

    question_id: str
    question_text: str
    interview_type: str  # 'technical', 'behavioral', 'project'
    category: str
    difficulty: str  # 'beginner', 'intermediate', 'advanced'
    relevant_skill: str
    applicable_roles: List[str] = Field(default_factory=list)  # or ['all']
    expected_concepts: List[str] = Field(default_factory=list)
    suggested_answer_points: List[str] = Field(default_factory=list)
    evaluation_rubric: Dict[str, Any] = Field(default_factory=dict)
    weight: float = 1.0


QUESTION_BANK: List[QuestionItem] = [
    # =========================================================================
    # 1. PROGRAMMING FUNDAMENTALS
    # =========================================================================
    QuestionItem(
        question_id="prog_fund_oop_principles",
        question_text="Explain the four core principles of Object-Oriented Programming (OOP) and give a brief real-world example of each.",
        interview_type="technical",
        category="programming_fundamentals",
        difficulty="beginner",
        relevant_skill="OOP",
        applicable_roles=["all"],
        expected_concepts=["encapsulation", "abstraction", "inheritance", "polymorphism", "data hiding", "interface", "method overriding"],
        suggested_answer_points=[
            "Encapsulation bundles data and methods together while restricting direct access to internal state.",
            "Abstraction hides internal implementation details and exposes only clean, necessary interfaces.",
            "Inheritance allows a subclass to acquire properties and behavior from a parent class.",
            "Polymorphism allows objects of different classes to be treated as instances of a common superclass through method overriding or overloading.",
        ],
        evaluation_rubric={
            "required_keywords": ["encapsulation", "abstraction", "inheritance", "polymorphism"],
            "core_points": ["four principles named", "practical examples provided", "data hiding explained"],
            "ideal_structure": ["definitions", "mechanisms", "real_world_examples"],
            "weight": 1.0,
        },
    ),
    QuestionItem(
        question_id="prog_fund_stack_vs_heap",
        question_text="What is the difference between Stack and Heap memory allocation, and how does memory management differ between them?",
        interview_type="technical",
        category="programming_fundamentals",
        difficulty="intermediate",
        relevant_skill="Memory Management",
        applicable_roles=["sde", "backend_developer", "full_stack_developer"],
        expected_concepts=["stack", "heap", "static allocation", "dynamic allocation", "LIFO", "garbage collection", "memory leak", "stack overflow"],
        suggested_answer_points=[
            "Stack memory is used for static memory allocation and stores local variables, function calls, and control flow in LIFO order.",
            "Heap memory is used for dynamic memory allocation where blocks can be allocated and deallocated in arbitrary order.",
            "Stack access is extremely fast and managed automatically by the compiler/OS; Heap requires garbage collection or manual free.",
            "Stack is size-constrained (risk of stack overflow), whereas Heap is larger but prone to memory leaks and fragmentation.",
        ],
        evaluation_rubric={
            "required_keywords": ["stack", "heap", "dynamic", "lifo", "allocation"],
            "core_points": ["lifo stack vs dynamic heap", "speed comparison", "lifecycle/garbage collection"],
            "ideal_structure": ["comparison", "speed_and_lifecycle", "failure_modes"],
            "weight": 1.0,
        },
    ),

    # =========================================================================
    # 2. PYTHON
    # =========================================================================
    QuestionItem(
        question_id="py_gil_multithreading",
        question_text="Explain the Python Global Interpreter Lock (GIL). How does it affect multi-threaded CPU-bound versus I/O-bound programs, and how do you bypass it?",
        interview_type="technical",
        category="python",
        difficulty="intermediate",
        relevant_skill="Python",
        applicable_roles=["sde", "backend_developer", "data_scientist", "machine_learning_engineer", "python_developer", "full_stack_developer"],
        expected_concepts=["Global Interpreter Lock", "mutex", "single thread", "bytecode", "CPU-bound", "I/O-bound", "multiprocessing", "asyncio", "C extensions"],
        suggested_answer_points=[
            "The GIL is a mutex that prevents multiple native OS threads from executing Python bytecodes concurrently to ensure thread-safe memory management in CPython.",
            "For CPU-bound tasks, multi-threading cannot achieve parallelism and may actually slow down due to context switching overhead.",
            "For I/O-bound tasks, the GIL is released during system calls (network, disk I/O), allowing threads to run concurrently.",
            "To bypass the GIL for CPU-intensive workloads, developers use the multiprocessing module, Celery, Cython, or external C/Rust extensions.",
        ],
        evaluation_rubric={
            "required_keywords": ["gil", "mutex", "thread", "cpu", "io", "multiprocessing"],
            "core_points": ["mutex definition", "cpu-bound limitation", "io-bound release", "multiprocessing solution"],
            "ideal_structure": ["gil_definition", "impact_on_threads", "solutions_bypass"],
            "weight": 1.0,
        },
    ),
    QuestionItem(
        question_id="py_generators_vs_lists",
        question_text="What are Python generators and iterators? How do they differ from regular lists in terms of memory efficiency and execution flow?",
        interview_type="technical",
        category="python",
        difficulty="beginner",
        relevant_skill="Python",
        applicable_roles=["sde", "backend_developer", "data_analyst", "data_scientist", "python_developer", "full_stack_developer"],
        expected_concepts=["generator", "yield", "lazy evaluation", "memory efficiency", "iterator protocol", "iter", "next", "StopIteration"],
        suggested_answer_points=[
            "Generators are functions that produce a sequence of values on-the-fly using the yield keyword rather than returning all elements at once.",
            "Generators use lazy evaluation, meaning items are computed only when requested, keeping memory consumption O(1) regardless of sequence size.",
            "Lists store all elements eagerly in contiguous memory, requiring O(N) space.",
            "Generators adhere to the iterator protocol implementing __iter__() and __next__(), raising StopIteration when exhausted.",
        ],
        evaluation_rubric={
            "required_keywords": ["generator", "yield", "lazy", "memory", "iterator"],
            "core_points": ["yield keyword", "lazy vs eager evaluation", "O(1) memory footprint"],
            "ideal_structure": ["generator_definition", "memory_difference", "iterator_protocol"],
            "weight": 1.0,
        },
    ),
    QuestionItem(
        question_id="py_decorators_closures",
        question_text="How do decorators work under the hood in Python? Explain closures and how you would implement a decorator that accepts custom arguments.",
        interview_type="technical",
        category="python",
        difficulty="advanced",
        relevant_skill="Python",
        applicable_roles=["sde", "backend_developer", "python_developer", "full_stack_developer"],
        expected_concepts=["decorator", "closure", "first-class functions", "higher-order function", "wrapper", "functools.wraps", "nested functions", "args and kwargs"],
        suggested_answer_points=[
            "Decorators are higher-order functions that take a callable as input and return a modified callable without altering the original source code.",
            "They rely on closures: inner functions retaining access to variables in their enclosing lexical scope even after the outer function finishes.",
            "A decorator with arguments requires three nested function layers: an outer factory function that accepts arguments, returning the actual decorator, which returns the wrapper.",
            "Using functools.wraps preserves docstrings, function names, and signature metadata of the wrapped function.",
        ],
        evaluation_rubric={
            "required_keywords": ["decorator", "closure", "wrapper", "wraps", "higher-order"],
            "core_points": ["closure mechanism", "three-level nesting for parameterized decorators", "functools.wraps importance"],
            "ideal_structure": ["closure_explanation", "decorator_architecture", "parameterized_decorator_pattern"],
            "weight": 1.0,
        },
    ),

    # =========================================================================
    # 3. JAVASCRIPT & FRONTEND
    # =========================================================================
    QuestionItem(
        question_id="js_event_loop",
        question_text="Explain the JavaScript Event Loop, Call Stack, Microtask Queue, and Macrotask (Callback) Queue. In what order are Promises and setTimeout executed?",
        interview_type="technical",
        category="javascript",
        difficulty="intermediate",
        relevant_skill="JavaScript",
        applicable_roles=["frontend_developer", "full_stack_developer", "sde"],
        expected_concepts=["event loop", "call stack", "microtask queue", "macrotask queue", "Promise", "setTimeout", "single threaded", "non-blocking"],
        suggested_answer_points=[
            "JavaScript has a single-threaded runtime engine with a synchronous Call Stack.",
            "Asynchronous operations delegate to browser Web APIs or Node libuv and schedule callbacks onto queues.",
            "The microtask queue (Promises, queueMicrotask, MutationObserver) has priority and is drained completely after each stack frame before any macrotask is processed.",
            "The macrotask queue (setTimeout, setInterval, I/O) runs one task at a time after the microtask queue is empty.",
            "Therefore, a resolved Promise (.then) always executes before a setTimeout(..., 0) callback.",
        ],
        evaluation_rubric={
            "required_keywords": ["event loop", "call stack", "microtask", "macrotask", "promise", "settimeout"],
            "core_points": ["single-threaded stack", "microtask priority over macrotasks", "promises run before setTimeout"],
            "ideal_structure": ["event_loop_overview", "queues_comparison", "execution_order"],
            "weight": 1.0,
        },
    ),
    QuestionItem(
        question_id="react_virtual_dom_reconciliation",
        question_text="How does React's Virtual DOM and Reconciliation algorithm (Fiber) work? Why are unique keys critical when rendering lists?",
        interview_type="technical",
        category="react",
        difficulty="intermediate",
        relevant_skill="React",
        applicable_roles=["frontend_developer", "full_stack_developer"],
        expected_concepts=["Virtual DOM", "reconciliation", "Fiber", "diffing algorithm", "keys", "DOM manipulation", "component tree"],
        suggested_answer_points=[
            "The Virtual DOM is an in-memory lightweight JavaScript tree representation of the actual UI DOM elements.",
            "When state changes, React creates a new VDOM tree and diffs it with the previous snapshot (Reconciliation/Fiber).",
            "React calculates the minimal set of real DOM mutations needed, batching updates to avoid expensive layout reflows.",
            "Unique stable keys allow React to track element identity across renders, preventing wasteful unmounting, re-rendering, or state corruption during re-ordering.",
        ],
        evaluation_rubric={
            "required_keywords": ["virtual dom", "reconciliation", "diffing", "keys", "fiber"],
            "core_points": ["vdom concept", "diffing & batching", "purpose of stable keys"],
            "ideal_structure": ["vdom_definition", "diffing_process", "key_importance"],
            "weight": 1.0,
        },
    ),
    QuestionItem(
        question_id="react_useeffect_lifecycle",
        question_text="Explain the lifecycle of the useEffect hook in React. How do dependency arrays and cleanup functions prevent memory leaks?",
        interview_type="technical",
        category="react",
        difficulty="beginner",
        relevant_skill="React",
        applicable_roles=["frontend_developer", "full_stack_developer"],
        expected_concepts=["useEffect", "dependency array", "cleanup function", "mount", "unmount", "memory leak", "subscriptions"],
        suggested_answer_points=[
            "useEffect executes side effects (data fetching, DOM subscriptions) after the component renders and commits to the screen.",
            "An empty dependency array ([]) runs only once on mount; omitted dependencies run on every render; specified dependencies run when those values change.",
            "Returning a cleanup function ensures previous subscriptions, event listeners, or timers are disposed before re-running or when unmounting.",
            "Failing to clean up leads to memory leaks, state updates on unmounted components, and zombie event listeners.",
        ],
        evaluation_rubric={
            "required_keywords": ["useeffect", "dependency", "cleanup", "unmount", "memory leak"],
            "core_points": ["render lifecycle", "dependency array behaviors", "cleanup function purpose"],
            "ideal_structure": ["lifecycle_timing", "dependency_behaviors", "cleanup_and_safety"],
            "weight": 1.0,
        },
    ),

    # =========================================================================
    # 4. BACKEND & NODE.JS
    # =========================================================================
    QuestionItem(
        question_id="node_event_driven_architecture",
        question_text="How does Node.js achieve high concurrency despite being single-threaded? What is the role of Libuv?",
        interview_type="technical",
        category="node_js",
        difficulty="intermediate",
        relevant_skill="Node.js",
        applicable_roles=["backend_developer", "full_stack_developer", "sde"],
        expected_concepts=["Node.js", "Libuv", "event-driven", "non-blocking I/O", "thread pool", "asynchronous", "system kernel"],
        suggested_answer_points=[
            "Node.js runs on a single main JavaScript thread using an asynchronous, event-driven I/O model.",
            "I/O operations (network sockets, file system, crypto) are offloaded to the operating system kernel via epoll/kqueue or Libuv's thread pool.",
            "When asynchronous operations finish, Libuv pushes their callbacks onto the Event Loop queue.",
            "This enables Node.js to handle tens of thousands of concurrent connections without thread-per-connection memory overhead.",
        ],
        evaluation_rubric={
            "required_keywords": ["libuv", "event loop", "non-blocking", "thread pool", "single-threaded"],
            "core_points": ["single main thread", "libuv thread pool offloading", "asynchronous non-blocking I/O"],
            "ideal_structure": ["concurrency_model", "libuv_role", "throughput_benefits"],
            "weight": 1.0,
        },
    ),

    # =========================================================================
    # 5. SQL & DBMS
    # =========================================================================
    QuestionItem(
        question_id="db_acid_properties",
        question_text="What are ACID properties in database transactions? Explain each property with a banking transaction scenario.",
        interview_type="technical",
        category="sql_dbms",
        difficulty="beginner",
        relevant_skill="SQL",
        applicable_roles=["backend_developer", "data_analyst", "full_stack_developer", "sde"],
        expected_concepts=["ACID", "atomicity", "consistency", "isolation", "durability", "commit", "rollback", "transaction"],
        suggested_answer_points=[
            "Atomicity: All operations in a transaction succeed or none do (all-or-nothing). In bank transfer, debiting account A and crediting B must both complete.",
            "Consistency: Transactions take the database from one valid state to another, preserving constraints and invariants (total money remains constant).",
            "Isolation: Concurrent transactions execute without interfering with one another as if running serially.",
            "Durability: Once committed, changes are permanently saved in non-volatile storage and survive power failures or crashes.",
        ],
        evaluation_rubric={
            "required_keywords": ["atomicity", "consistency", "isolation", "durability", "transaction", "rollback"],
            "core_points": ["all 4 acid terms defined", "banking transfer example", "commit/rollback concept"],
            "ideal_structure": ["acid_definitions", "banking_scenario", "database_guarantees"],
            "weight": 1.0,
        },
    ),
    QuestionItem(
        question_id="db_indexing_b_tree",
        question_text="How do B-Tree indexes work in relational databases (e.g., PostgreSQL)? Why can having too many indexes degrade write performance?",
        interview_type="technical",
        category="sql_dbms",
        difficulty="intermediate",
        relevant_skill="PostgreSQL",
        applicable_roles=["backend_developer", "data_engineer", "data_analyst", "full_stack_developer", "sde"],
        expected_concepts=["indexing", "B-Tree", "binary search", "disk I/O", "write amplification", "INSERT", "UPDATE", "lookup complexity", "O(log N)"],
        suggested_answer_points=[
            "B-Tree indexes maintain a balanced multi-way tree on disk that enables O(log N) search, range queries, and ordered traversals.",
            "Instead of full table scans (O(N) disk pages), database engines traverse root to leaf nodes with minimal I/O operations.",
            "Indexes speed up SELECT queries but introduce overhead during INSERT, UPDATE, and DELETE operations.",
            "Every write requires updating and re-balancing multiple B-Trees on disk (write amplification), consuming CPU and storage I/O.",
        ],
        evaluation_rubric={
            "required_keywords": ["b-tree", "index", "disk", "write", "insert", "log n"],
            "core_points": ["balanced tree structure", "log N lookup speed", "write degradation tradeoff"],
            "ideal_structure": ["how_index_works", "read_benefits", "write_penalties"],
            "weight": 1.0,
        },
    ),

    # =========================================================================
    # 6. DATA STRUCTURES & ALGORITHMS
    # =========================================================================
    QuestionItem(
        question_id="dsa_array_vs_linked_list",
        question_text="Compare Arrays and Linked Lists across time and space complexity for insertion, deletion, and random access. When would you choose one over the other?",
        interview_type="technical",
        category="data_structures_algorithms",
        difficulty="beginner",
        relevant_skill="Data Structures",
        applicable_roles=["sde", "backend_developer", "full_stack_developer", "data_scientist"],
        expected_concepts=["array", "linked list", "O(1)", "O(n)", "contiguous memory", "cache locality", "pointers", "random access", "insertion"],
        suggested_answer_points=[
            "Arrays store elements in contiguous memory blocks, granting O(1) instantaneous random indexing by offset.",
            "Inserting or deleting in an array requires shifting remaining elements, costing O(N) unless at the end (amortized O(1)).",
            "Linked Lists store nodes connected by pointers; insertion/deletion at a known node is O(1), but random access requires O(N) linear traversal.",
            "Arrays have superior CPU cache locality; linked lists have pointer memory overhead and scattered cache misses.",
            "Use arrays when fast indexing and read operations dominate; use linked lists for frequent insertions/deletions with unknown size.",
        ],
        evaluation_rubric={
            "required_keywords": ["array", "linked list", "contiguous", "cache", "random access", "o(1)"],
            "core_points": ["random access comparison", "insertion/deletion complexity", "cache locality tradeoff"],
            "ideal_structure": ["complexity_comparison", "memory_and_cache", "use_cases"],
            "weight": 1.0,
        },
    ),
    QuestionItem(
        question_id="dsa_hash_collision_resolution",
        question_text="How do Hash Tables achieve O(1) average lookup time? What are the common collision resolution strategies, and what causes worst-case O(N) performance?",
        interview_type="technical",
        category="data_structures_algorithms",
        difficulty="intermediate",
        relevant_skill="Data Structures",
        applicable_roles=["sde", "backend_developer", "full_stack_developer", "data_scientist"],
        expected_concepts=["hash table", "hash function", "collision", "separate chaining", "open addressing", "linear probing", "load factor", "O(1)", "O(n)"],
        suggested_answer_points=[
            "Hash tables compute an array index from a key using a deterministic hash function, enabling direct O(1) bucket access.",
            "Collisions occur when two distinct keys yield the same bucket index.",
            "Separate Chaining resolves collisions by storing entries in a linked list or balanced tree at each bucket.",
            "Open Addressing (Linear/Quadratic Probing, Double Hashing) searches for the next available vacant slot within the array.",
            "If the hash function has poor distribution or load factor exceeds capacity, all keys map to one bucket, degrading lookup to O(N).",
        ],
        evaluation_rubric={
            "required_keywords": ["hash", "collision", "chaining", "open addressing", "load factor", "o(n)"],
            "core_points": ["hash function mapping", "chaining vs open addressing", "worst case degradation reason"],
            "ideal_structure": ["mechanism", "collision_strategies", "worst_case_analysis"],
            "weight": 1.0,
        },
    ),

    # =========================================================================
    # 7. OPERATING SYSTEMS & NETWORKS
    # =========================================================================
    QuestionItem(
        question_id="os_process_vs_thread",
        question_text="What is the difference between a Process and a Thread? How do context switching, memory sharing, and IPC differ between them?",
        interview_type="technical",
        category="operating_systems",
        difficulty="intermediate",
        relevant_skill="Operating Systems",
        applicable_roles=["sde", "backend_developer", "full_stack_developer"],
        expected_concepts=["process", "thread", "address space", "context switch", "IPC", "shared memory", "multithreading", "overhead"],
        suggested_answer_points=[
            "A process is an independent program execution unit with its own private virtual address space, file descriptors, and registers.",
            "A thread is a lightweight execution flow within a process; multiple threads share the same address space, code, and heap, but have private stacks.",
            "Context switching between processes is expensive because it requires changing virtual memory page tables and flushing TLB caches.",
            "Thread context switching is significantly faster because the address space remains identical.",
            "Processes communicate via Inter-Process Communication (pipes, sockets, message queues, shared memory); threads communicate directly via shared memory with lock synchronization.",
        ],
        evaluation_rubric={
            "required_keywords": ["process", "thread", "address space", "context switch", "shared memory", "ipc"],
            "core_points": ["memory isolation vs sharing", "context switch cost differences", "communication mechanisms"],
            "ideal_structure": ["definitions", "memory_sharing", "switching_and_ipc"],
            "weight": 1.0,
        },
    ),
    QuestionItem(
        question_id="net_tcp_vs_udp",
        question_text="Compare TCP and UDP protocols. Explain the TCP three-way handshake and describe applications where UDP is preferable over TCP.",
        interview_type="technical",
        category="computer_networks",
        difficulty="beginner",
        relevant_skill="Computer Networks",
        applicable_roles=["backend_developer", "sde", "full_stack_developer", "devops_engineer"],
        expected_concepts=["TCP", "UDP", "three-way handshake", "SYN", "ACK", "connection-oriented", "packet loss", "retransmission", "latency", "streaming", "gaming"],
        suggested_answer_points=[
            "TCP is a connection-oriented, reliable protocol that guarantees in-order packet delivery using acknowledgments, checksums, and retransmissions.",
            "The TCP 3-way handshake establishes a session: Client sends SYN -> Server responds SYN-ACK -> Client replies ACK.",
            "UDP is a connectionless, lightweight datagram protocol with no delivery guarantee, ordering, or flow control.",
            "UDP offers minimal latency and overhead, making it ideal for live video streaming, VoIP, DNS queries, and multiplayer gaming where dropping a frame is better than buffering delays.",
        ],
        evaluation_rubric={
            "required_keywords": ["tcp", "udp", "syn", "ack", "handshake", "retransmission", "latency"],
            "core_points": ["reliable vs datagram", "three-way handshake steps", "udp real-world use cases"],
            "ideal_structure": ["protocol_differences", "three_way_handshake", "udp_use_cases"],
            "weight": 1.0,
        },
    ),

    # =========================================================================
    # 8. SYSTEM DESIGN
    # =========================================================================
    QuestionItem(
        question_id="sys_design_caching_strategies",
        question_text="Explain common caching strategies (Cache-Aside, Write-Through, Write-Behind). What is cache invalidation and how do you handle cache stampedes?",
        interview_type="technical",
        category="system_design",
        difficulty="advanced",
        relevant_skill="System Design",
        applicable_roles=["backend_developer", "sde", "full_stack_developer"],
        expected_concepts=["caching", "Cache-Aside", "Write-Through", "Write-Behind", "Redis", "cache invalidation", "TTL", "cache stampede", "distributed lock"],
        suggested_answer_points=[
            "Cache-Aside (Lazy Loading): The application queries cache first; on miss, loads from DB and populates cache.",
            "Write-Through: Data is written simultaneously to cache and database, ensuring consistency at the cost of higher write latency.",
            "Write-Behind (Write-Back): Data is written directly to cache and asynchronously flushed to DB, offering ultra-fast writes but risking data loss on cache crash.",
            "Cache Stampede occurs when an expired popular key causes hundreds of concurrent requests to hit the database at once.",
            "Mitigate stampedes using mutual exclusion (mutex/distributed lock), probabilistic early expiration, or background pre-warming.",
        ],
        evaluation_rubric={
            "required_keywords": ["cache-aside", "write-through", "invalidation", "ttl", "stampede", "redis"],
            "core_points": ["cache patterns defined", "write tradeoffs", "stampede mitigation strategy"],
            "ideal_structure": ["patterns_overview", "invalidation_challenges", "stampede_solutions"],
            "weight": 1.0,
        },
    ),
    QuestionItem(
        question_id="sys_design_cap_theorem",
        question_text="Explain the CAP Theorem in distributed systems. Why is it impossible to achieve Consistency, Availability, and Partition Tolerance simultaneously across a network partition?",
        interview_type="technical",
        category="system_design",
        difficulty="intermediate",
        relevant_skill="System Design",
        applicable_roles=["backend_developer", "sde", "full_stack_developer", "data_engineer"],
        expected_concepts=["CAP theorem", "consistency", "availability", "partition tolerance", "network partition", "CP", "AP", "distributed system"],
        suggested_answer_points=[
            "The CAP Theorem states that in any distributed data store, you can only guarantee at most two out of Consistency, Availability, and Partition Tolerance.",
            "In real-world networks, network partitions (delays, dropped packets) are inevitable; therefore, Partition Tolerance (P) is non-negotiable.",
            "During a network partition, the system must choose between:",
            "Consistency (CP): Reject writes on partitioned nodes to prevent stale reads and diverging state.",
            "Availability (AP): Allow partitioned nodes to accept reads and writes, sacrificing immediate consistency (eventual consistency).",
        ],
        evaluation_rubric={
            "required_keywords": ["cap", "consistency", "availability", "partition tolerance", "cp", "ap"],
            "core_points": ["definitions of C, A, P", "inevitability of P", "tradeoff choice between CP and AP"],
            "ideal_structure": ["cap_definitions", "partition_inevitability", "cp_vs_ap_tradeoff"],
            "weight": 1.0,
        },
    ),

    # =========================================================================
    # 9. MACHINE LEARNING & DATA ANALYTICS
    # =========================================================================
    QuestionItem(
        question_id="ml_overfitting_regularization",
        question_text="What is overfitting in machine learning? How do L1 (Lasso) and L2 (Ridge) regularization help prevent overfitting, and how do their penalties differ?",
        interview_type="technical",
        category="machine_learning",
        difficulty="intermediate",
        relevant_skill="Machine Learning",
        applicable_roles=["data_scientist", "machine_learning_engineer", "data_analyst"],
        expected_concepts=["overfitting", "regularization", "L1 Lasso", "L2 Ridge", "loss function", "penalty", "sparsity", "feature selection", "bias-variance tradeoff"],
        suggested_answer_points=[
            "Overfitting occurs when a model memorizes training noise and high-variance patterns, failing to generalize to unseen test data.",
            "Regularization adds a penalty term to the loss function to constrain model weights and avoid extreme coefficients.",
            "L1 Regularization (Lasso) adds the sum of absolute weights (|w|). It drives less important weights strictly to zero, effectively performing feature selection.",
            "L2 Regularization (Ridge) adds the sum of squared weights (w^2). It shrinks weights continuously towards zero without setting them exactly to zero, handling multicollinearity.",
        ],
        evaluation_rubric={
            "required_keywords": ["overfitting", "regularization", "l1", "l2", "lasso", "ridge", "weights"],
            "core_points": ["overfitting definition", "l1 absolute penalty / sparsity", "l2 squared penalty / shrinkage"],
            "ideal_structure": ["overfitting_explanation", "regularization_principle", "l1_vs_l2_comparison"],
            "weight": 1.0,
        },
    ),
    QuestionItem(
        question_id="da_handling_missing_data",
        question_text="What techniques do you use to handle missing data in an exploratory data analysis (EDA)? When is imputation appropriate versus dropping rows or columns?",
        interview_type="technical",
        category="data_analytics",
        difficulty="beginner",
        relevant_skill="Data Analytics",
        applicable_roles=["data_analyst", "data_scientist", "machine_learning_engineer"],
        expected_concepts=["missing data", "imputation", "mean", "median", "mode", "KNN imputation", "MCAR", "MAR", "data loss", "bias"],
        suggested_answer_points=[
            "First identify the missingness mechanism: Missing Completely at Random (MCAR), Missing at Random (MAR), or Not at Random (MNAR).",
            "Dropping rows/columns is appropriate when missing values exceed 60-70% of a feature or when MCAR sample loss has negligible impact on dataset size.",
            "Mean/Median/Mode imputation works for numerical/categorical data with low missingness (<5-10%), though median is preferred for skewed distributions with outliers.",
            "Advanced techniques (KNN, IterativeImputer, forward/backward fill in time series) preserve multivariate correlations without distorting variance.",
        ],
        evaluation_rubric={
            "required_keywords": ["imputation", "mean", "median", "outliers", "missing", "drop"],
            "core_points": ["drop vs impute criteria", "mean/median for outliers", "advanced imputation options"],
            "ideal_structure": ["identification", "dropping_criteria", "imputation_strategies"],
            "weight": 1.0,
        },
    ),

    # =========================================================================
    # 10. PROJECT-BASED & PRACTICAL EXPERIENCE
    # =========================================================================
    QuestionItem(
        question_id="proj_challenging_engineering_bug",
        question_text="Describe the most complex technical bug or production incident you have diagnosed. Walk through your debugging methodology, root cause, and how you prevented recurrence.",
        interview_type="project",
        category="projects_and_practical",
        difficulty="intermediate",
        relevant_skill="Debugging",
        applicable_roles=["all"],
        expected_concepts=["debugging", "root cause analysis", "logs", "metrics", "reproduction", "monitoring", "post-mortem", "unit test"],
        suggested_answer_points=[
            "Context: Clearly describe the symptoms and business impact of the bug (e.g. memory leak, deadlock, data corruption, latency spike).",
            "Investigation: Explain the diagnostic tools used (APM tracing, log aggregation, profiling, reproducing in staging).",
            "Root Cause: State the exact underlying mechanism identified (e.g. unclosed connection pool, off-by-one concurrency race).",
            "Resolution & Prevention: Describe the fix deployed and preventative measures implemented (regression tests, alerts, CI/CD gates, architectural safeguard).",
        ],
        evaluation_rubric={
            "required_keywords": ["bug", "root cause", "debug", "logs", "fix", "test"],
            "core_points": ["problem statement", "investigation methodology", "root cause discovery", "long-term prevention"],
            "ideal_structure": ["symptoms_and_context", "diagnostic_process", "root_cause_and_solution"],
            "weight": 1.0,
        },
    ),
    QuestionItem(
        question_id="proj_architectural_tradeoffs",
        question_text="Tell me about a project where you had to make a difficult architectural trade-off. What options did you consider, what data guided your decision, and what were the outcomes?",
        interview_type="project",
        category="projects_and_practical",
        difficulty="advanced",
        relevant_skill="Architecture",
        applicable_roles=["all"],
        expected_concepts=["trade-off", "architecture", "scalability", "cost", "complexity", "benchmarks", "monitoring", "iteration"],
        suggested_answer_points=[
            "Context: The business requirement or scaling constraint driving the need for architectural decisions.",
            "Options: Compare at least two distinct approaches (e.g. SQL vs NoSQL, Monolith vs Microservices, Polling vs WebSockets).",
            "Evaluation Criteria: Discuss constraints (development velocity, latency, operational maintenance, cloud cost).",
            "Outcome & Retrospective: The measurable result achieved and lessons learned from the selected trade-off.",
        ],
        evaluation_rubric={
            "required_keywords": ["trade-off", "options", "decision", "scalability", "latency", "outcome"],
            "core_points": ["clear options compared", "objective criteria used", "retrospective on outcomes"],
            "ideal_structure": ["context", "options_considered", "decision_criteria", "outcome"],
            "weight": 1.0,
        },
    ),

    # =========================================================================
    # 11. HR & BEHAVIORAL (STAR METHOD)
    # =========================================================================
    QuestionItem(
        question_id="hr_conflict_resolution",
        question_text="Tell me about a time when you strongly disagreed with a team member or technical lead on a technical direction. How did you handle the situation and what was the outcome?",
        interview_type="behavioral",
        category="hr_behavioral",
        difficulty="intermediate",
        relevant_skill="Conflict Resolution",
        applicable_roles=["all"],
        expected_concepts=["disagreement", "listen", "data", "compromise", "alignment", "respect", "STAR method", "outcome"],
        suggested_answer_points=[
            "Situation: Describe the specific technical context and the conflicting proposals or viewpoints.",
            "Task: Your responsibility in finding common ground while ensuring project objectives and code quality were met.",
            "Action: How you actively listened to their rationale, gathered objective data/proof-of-concept benchmarks, and discussed trade-offs collaboratively without ego.",
            "Result: The mutually agreed path chosen, successful project delivery, and strengthened professional relationship.",
        ],
        evaluation_rubric={
            "required_keywords": ["situation", "task", "action", "result", "disagree", "data", "compromise"],
            "core_points": ["star format followed", "objective data over emotion", "positive collaborative resolution"],
            "ideal_structure": ["situation", "task", "action", "result"],
            "weight": 1.0,
        },
    ),
    QuestionItem(
        question_id="hr_handling_tight_deadlines",
        question_text="Describe a situation where project scope expanded unexpectedly under a tight delivery deadline. How did you prioritize tasks and communicate with stakeholders?",
        interview_type="behavioral",
        category="hr_behavioral",
        difficulty="beginner",
        relevant_skill="Time Management",
        applicable_roles=["all"],
        expected_concepts=["deadline", "scope creep", "prioritization", "communication", "MVP", "stakeholders", "trade-offs", "result"],
        suggested_answer_points=[
            "Situation: Outline the project deadline and the unexpected requirements or roadblock encountered.",
            "Task: The critical deliverables that had to be met versus nice-to-have scope additions.",
            "Action: Transparent communication with product managers/stakeholders, re-scoping to an MVP, deprioritizing non-essential features, and setting realistic expectations.",
            "Result: On-time delivery of the core system with zero outages, with deferred items prioritized in the next sprint.",
        ],
        evaluation_rubric={
            "required_keywords": ["deadline", "priority", "communicate", "scope", "result"],
            "core_points": ["proactive stakeholder communication", "scope triage/prioritization", "successful delivery result"],
            "ideal_structure": ["situation", "task", "action", "result"],
            "weight": 1.0,
        },
    ),
    QuestionItem(
        question_id="hr_handling_failure_learning",
        question_text="Can you share an experience where a project or feature you worked on did not succeed or broke in production? What did you learn and how did you adapt?",
        interview_type="behavioral",
        category="hr_behavioral",
        difficulty="intermediate",
        relevant_skill="Accountability",
        applicable_roles=["all"],
        expected_concepts=["failure", "mistake", "accountability", "learning", "action", "retrospective", "growth", "prevention"],
        suggested_answer_points=[
            "Situation: A candid description of the incident, faulty assumption, or missed edge case.",
            "Task: Taking immediate ownership and responsibility rather than shifting blame.",
            "Action: The immediate mitigation deployed to recover system health, followed by a blameless post-mortem.",
            "Result: Concrete process improvements (e.g. automated integration tests, staged rollouts) ensuring the mistake never recurred.",
        ],
        evaluation_rubric={
            "required_keywords": ["ownership", "learned", "incident", "prevention", "growth"],
            "core_points": ["personal accountability", "blameless recovery action", "institutional learning"],
            "ideal_structure": ["situation", "task", "action", "result"],
            "weight": 1.0,
        },
    ),
    QuestionItem(
        question_id="os_deadlocks_prevention",
        question_text="What are the four Coffman conditions necessary for a Deadlock to occur? How can an operating system or software design prevent or recover from deadlocks?",
        interview_type="technical",
        category="operating_systems",
        difficulty="advanced",
        relevant_skill="Operating Systems",
        applicable_roles=["sde", "backend_developer", "full_stack_developer"],
        expected_concepts=["deadlock", "mutual exclusion", "hold and wait", "no preemption", "circular wait", "bankers algorithm", "lock ordering", "resource allocation"],
        suggested_answer_points=[
            "Mutual Exclusion: Resource cannot be shared and is held in a non-shareable mode.",
            "Hold and Wait: A process holds at least one resource and is waiting to acquire additional resources held by other processes.",
            "No Preemption: Resources cannot be forcibly revoked from a process; they can only be released voluntarily.",
            "Circular Wait: A closed loop of processes where each process waits for a resource held by the next.",
            "Prevention breaks one condition (e.g. strict global lock ordering eliminates circular wait, preemption revokes resources).",
        ],
        evaluation_rubric={
            "required_keywords": ["mutual exclusion", "hold and wait", "preemption", "circular wait", "lock"],
            "core_points": ["all four coffman conditions", "lock ordering prevention", "resource preemption"],
            "ideal_structure": ["conditions_list", "prevention_strategies", "software_design_tactics"],
            "weight": 1.0,
        },
    ),
    QuestionItem(
        question_id="net_http_versions",
        question_text="Explain the key architectural differences between HTTP/1.1, HTTP/2, and HTTP/3. How do multiplexing and QUIC (UDP) solve head-of-line blocking?",
        interview_type="technical",
        category="computer_networks",
        difficulty="advanced",
        relevant_skill="Computer Networks",
        applicable_roles=["backend_developer", "sde", "full_stack_developer", "frontend_developer"],
        expected_concepts=["HTTP/1.1", "HTTP/2", "HTTP/3", "multiplexing", "head-of-line blocking", "QUIC", "UDP", "binary framing", "TCP handshake"],
        suggested_answer_points=[
            "HTTP/1.1 uses plaintext request/response pipelining over persistent TCP connections but suffers from HTTP head-of-line blocking.",
            "HTTP/2 introduced binary framing, multiplexing multiple concurrent streams over a single TCP connection, and header compression (HPACK).",
            "However, HTTP/2 still suffered from TCP-level head-of-line blocking when a single packet was lost.",
            "HTTP/3 replaces TCP with QUIC over UDP, providing connection migration, zero-RTT connection establishment, and independent stream recovery.",
        ],
        evaluation_rubric={
            "required_keywords": ["http/2", "http/3", "multiplexing", "quic", "udp", "head-of-line"],
            "core_points": ["multiplexing in http/2", "tcp hol blocking issue", "quic/udp solution in http/3"],
            "ideal_structure": ["http1_vs_http2", "tcp_limitation", "http3_quic_advancement"],
            "weight": 1.0,
        },
    ),
    QuestionItem(
        question_id="react_performance_optimization",
        question_text="How do React.memo, useMemo, and useCallback prevent unnecessary component re-renders? What are the overheads of overusing these hooks?",
        interview_type="technical",
        category="react",
        difficulty="intermediate",
        relevant_skill="React",
        applicable_roles=["frontend_developer", "full_stack_developer"],
        expected_concepts=["React.memo", "useMemo", "useCallback", "re-render", "referential equality", "shallow comparison", "memoization overhead"],
        suggested_answer_points=[
            "React.memo is a higher-order component that skips re-rendering a functional component if its props have not changed by shallow comparison.",
            "useMemo memoizes the computed result of an expensive calculation and only recalculates when dependencies change.",
            "useCallback memoizes a callback function definition to preserve referential equality across renders, preventing child re-renders.",
            "Overuse overhead: Every hook allocates memory for dependency arrays and executes comparison overhead on each render, which can be more expensive than cheap re-renders.",
        ],
        evaluation_rubric={
            "required_keywords": ["usememo", "usecallback", "react.memo", "referential equality", "shallow comparison"],
            "core_points": ["function memoization vs value memoization", "referential equality", "premature optimization costs"],
            "ideal_structure": ["hook_definitions", "referential_equality", "tradeoffs_and_overheads"],
            "weight": 1.0,
        },
    ),
    QuestionItem(
        question_id="sql_window_functions_vs_group_by",
        question_text="What is the difference between SQL GROUP BY and Window Functions (e.g. ROW_NUMBER, RANK, DENSE_RANK)? Write an example conceptual query.",
        interview_type="technical",
        category="sql_dbms",
        difficulty="intermediate",
        relevant_skill="SQL",
        applicable_roles=["data_analyst", "data_scientist", "backend_developer", "data_engineer"],
        expected_concepts=["window functions", "GROUP BY", "OVER clause", "PARTITION BY", "ROW_NUMBER", "RANK", "DENSE_RANK", "aggregation", "row preservation"],
        suggested_answer_points=[
            "GROUP BY collapses multiple individual rows into a single aggregated summary row per group.",
            "Window Functions perform calculations across a set of rows related to the current row without collapsing the rows; each individual row retains its identity.",
            "ROW_NUMBER assigns unique sequential integers (1, 2, 3) without ties.",
            "RANK assigns the same rank to identical values and skips subsequent ranks (1, 2, 2, 4).",
            "DENSE_RANK assigns the same rank to identical values without skipping subsequent ranks (1, 2, 2, 3).",
        ],
        evaluation_rubric={
            "required_keywords": ["window function", "group by", "partition by", "row_number", "rank", "dense_rank"],
            "core_points": ["collapsing vs preserving rows", "over/partition by usage", "rank vs dense_rank difference"],
            "ideal_structure": ["core_difference", "ranking_functions_compared", "conceptual_example"],
            "weight": 1.0,
        },
    ),
    QuestionItem(
        question_id="dl_transformers_attention",
        question_text="How does the Self-Attention mechanism in Transformer models work compared to Recurrent Neural Networks (RNNs)? Why does attention allow effective parallelization?",
        interview_type="technical",
        category="deep_learning",
        difficulty="advanced",
        relevant_skill="Deep Learning",
        applicable_roles=["machine_learning_engineer", "data_scientist"],
        expected_concepts=["Transformer", "Self-Attention", "Query", "Key", "Value", "RNN", "parallelization", "sequential processing", "softmax", "context"],
        suggested_answer_points=[
            "RNNs process tokens sequentially step-by-step, maintaining a hidden state which prevents parallel computation across a sequence.",
            "Self-Attention computes direct pairwise affinity between all tokens in a sequence simultaneously using Query (Q), Key (K), and Value (V) matrix projections.",
            "Attention score is calculated as Softmax(Q * K^T / sqrt(d_k)) * V, capturing long-range dependencies in O(1) path length.",
            "Because matrix multiplications are independent across tokens, GPU tensor cores can parallelize training across the entire batch and sequence length.",
        ],
        evaluation_rubric={
            "required_keywords": ["transformer", "self-attention", "query", "key", "value", "rnn", "parallel"],
            "core_points": ["sequential rnn bottleneck", "qkv projection formula", "matrix parallelization on gpus"],
            "ideal_structure": ["rnn_limitations", "qkv_attention_mechanism", "parallelization_advantage"],
            "weight": 1.0,
        },
    ),
]


def get_all_questions() -> List[QuestionItem]:
    """Return the entire curated question catalog."""
    return QUESTION_BANK


def get_question_by_id(question_id: str) -> Optional[QuestionItem]:
    """Retrieve an individual question by its stable identifier."""
    for q in QUESTION_BANK:
        if q.question_id == question_id:
            return q
    return None


def filter_questions(
    interview_type: Optional[str] = None,
    target_role: Optional[str] = None,
    difficulty: Optional[str] = None,
    category: Optional[str] = None,
) -> List[QuestionItem]:
    """
    Filter question catalog by interview type, role relevance, difficulty, or category.
    Supports mixed interviews that pull across technical, behavioral, and project types.
    """
    results: List[QuestionItem] = []

    for q in QUESTION_BANK:
        # 1. Filter by Interview Type
        if interview_type and interview_type != "mixed":
            if q.interview_type != interview_type:
                continue

        # 2. Filter by Role Relevance
        if target_role:
            role_norm = target_role.lower().strip()
            if "all" not in q.applicable_roles and role_norm not in q.applicable_roles:
                # If target role is python_developer, check backend_developer or sde
                if role_norm == "python_developer" and any(r in ("backend_developer", "sde") for r in q.applicable_roles):
                    pass
                else:
                    continue

        # 3. Filter by Difficulty (allows fallback to adjacent difficulties)
        if difficulty and q.difficulty != difficulty:
            # We will use this in ranking/matching
            pass

        # 4. Filter by Category
        if category and q.category != category:
            continue

        results.append(q)

    return results
