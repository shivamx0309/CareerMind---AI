"""
Skill Dependency Graph and Curriculum Syllabus Service.
Defines prerequisite relationships, topic breakdowns, practical tasks,
and cycle-safe topological sequencing for technical competencies.
"""

import logging
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


# =============================================================================
# 1. Skill Dependency Graph (Prerequisite Relationships)
# =============================================================================

SKILL_DEPENDENCY_GRAPH: Dict[str, List[str]] = {
    # Backend & Web Frameworks
    "FastAPI": ["Python", "REST API"],
    "Django": ["Python", "SQL"],
    "Flask": ["Python"],
    "REST API": ["Python"],
    "Microservices": ["REST API", "Docker", "System Design"],

    # Frontend Technologies
    "TypeScript": ["JavaScript"],
    "React": ["JavaScript", "HTML5", "CSS3"],
    "Next.js": ["React", "TypeScript"],
    "Redux": ["React"],
    "Tailwind CSS": ["CSS3", "HTML5"],
    "Vite": ["JavaScript"],
    "GraphQL": ["REST API", "JavaScript"],

    # Databases & Caching
    "PostgreSQL": ["SQL"],
    "MySQL": ["SQL"],
    "Redis": ["SQL"],
    "BigQuery": ["SQL"],

    # Cloud, DevOps & Infrastructure
    "Docker": ["Linux"],
    "CI/CD": ["Git", "Docker"],
    "Kubernetes": ["Docker"],
    "Cloud Infrastructure": ["Linux", "Docker"],
    "AWS": ["Linux", "Cloud Infrastructure"],

    # Computer Science Fundamentals
    "Algorithms": ["Data Structures", "Python"],
    "Data Structures": ["Python"],
    "System Design": ["Data Structures", "REST API", "SQL"],

    # Data Analytics & BI
    "Data Analytics": ["SQL", "Excel"],
    "Data Cleaning": ["Python", "Data Analytics"],
    "Data Visualization": ["Excel", "Data Analytics"],
    "Power BI": ["Excel", "SQL"],
    "Tableau": ["SQL", "Data Visualization"],
    "Pandas": ["Python"],
    "NumPy": ["Python"],

    # AI / Machine Learning
    "Statistics": ["Python"],
    "Scikit-learn": ["Python", "NumPy", "Pandas", "Statistics"],
    "Machine Learning": ["Python", "Statistics", "Data Analytics"],
    "Deep Learning": ["Machine Learning", "Python"],
    "PyTorch": ["Deep Learning", "Python"],
    "TensorFlow": ["Deep Learning", "Python"],
    "MLflow": ["Machine Learning", "Python"],
    "MLOps": ["Machine Learning", "Docker", "CI/CD"],
}


# =============================================================================
# 2. Granular Topic Syllabus per Skill (Topics with Realistic Study Hours)
# =============================================================================

SKILL_TOPIC_SYLLABUS: Dict[str, List[Dict[str, float | str]]] = {
    "Python": [
        {"topic_name": "Variables, Primitive Types, and Control Flow", "estimated_hours": 2.0},
        {"topic_name": "Functions, Scope, and First-Class Callables", "estimated_hours": 2.5},
        {"topic_name": "Data Structures (Lists, Dicts, Sets, Tuples) and Comprehensions", "estimated_hours": 3.0},
        {"topic_name": "Object-Oriented Programming (Classes, Inheritance, Dunder Methods)", "estimated_hours": 3.5},
        {"topic_name": "Modules, Packaging, Virtual Environments, and pip", "estimated_hours": 2.0},
        {"topic_name": "Exception Handling, Context Managers, and File I/O", "estimated_hours": 3.0},
    ],
    "FastAPI": [
        {"topic_name": "Async Python, Type Annotations, and FastAPI Quickstart", "estimated_hours": 2.5},
        {"topic_name": "Path, Query, and Request Body Validation with Pydantic v2", "estimated_hours": 3.0},
        {"topic_name": "Dependency Injection System and Modular Routers", "estimated_hours": 3.5},
        {"topic_name": "SQLAlchemy Database Integration and Session Lifecycle", "estimated_hours": 4.5},
        {"topic_name": "JWT Authentication, Password Hashing, and Security Headers", "estimated_hours": 4.0},
        {"topic_name": "Unit and Integration Testing with Pytest and TestClient", "estimated_hours": 3.5},
    ],
    "SQL": [
        {"topic_name": "Relational Modeling, Data Types, and DDL Constraints", "estimated_hours": 2.5},
        {"topic_name": "Data Querying and Filtering (SELECT, WHERE, ORDER BY, LIMIT)", "estimated_hours": 2.5},
        {"topic_name": "Multi-Table Joins (INNER, LEFT, RIGHT, FULL, SELF)", "estimated_hours": 3.5},
        {"topic_name": "Grouping, Aggregations, and Conditional HAVING Clauses", "estimated_hours": 3.0},
        {"topic_name": "Subqueries and Common Table Expressions (CTEs)", "estimated_hours": 3.5},
        {"topic_name": "Window Functions (ROW_NUMBER, RANK, DENSE_RANK, OVER)", "estimated_hours": 4.0},
    ],
    "PostgreSQL": [
        {"topic_name": "PostgreSQL Architecture, Installation, and psql CLI", "estimated_hours": 2.0},
        {"topic_name": "Advanced Data Types (JSONB, Arrays, UUID, Timestamps)", "estimated_hours": 3.0},
        {"topic_name": "Index Types (B-Tree, GIN, GiST) and EXPLAIN ANALYZE", "estimated_hours": 4.0},
        {"topic_name": "Transactions, ACID Isolation Levels, and Row-Level Locking", "estimated_hours": 3.5},
        {"topic_name": "Database Migrations with Alembic and Schema Versioning", "estimated_hours": 3.5},
    ],
    "REST API": [
        {"topic_name": "HTTP Protocols, Request/Response Anatomy, and Status Codes", "estimated_hours": 2.0},
        {"topic_name": "RESTful Resource Modeling, URI Design, and Content Negotiation", "estimated_hours": 2.5},
        {"topic_name": "Error Handling, RFC 7807 Problem Details, and Validation", "estimated_hours": 2.5},
        {"topic_name": "Pagination, Filtering, Sorting, and Partial Responses", "estimated_hours": 3.0},
        {"topic_name": "API Security: CORS, Rate Limiting, and Bearer Tokens", "estimated_hours": 3.0},
    ],
    "Docker": [
        {"topic_name": "Containerization Concepts vs Virtual Machines", "estimated_hours": 2.0},
        {"topic_name": "Docker CLI Essentials (run, ps, exec, logs, stop, rm)", "estimated_hours": 2.5},
        {"topic_name": "Writing Multi-Stage, Production-Ready Dockerfiles", "estimated_hours": 3.5},
        {"topic_name": "Data Persistence with Named Volumes and Bind Mounts", "estimated_hours": 2.5},
        {"topic_name": "Container Networking and DNS Resolution", "estimated_hours": 2.5},
        {"topic_name": "Multi-Service Orchestration with Docker Compose", "estimated_hours": 3.5},
    ],
    "Git": [
        {"topic_name": "Version Control Fundamentals, Repositories, and Commits", "estimated_hours": 2.0},
        {"topic_name": "Branching Strategies, Merging, and Conflict Resolution", "estimated_hours": 2.5},
        {"topic_name": "Remote Repositories, Push, Pull, and Upstream Tracking", "estimated_hours": 2.0},
        {"topic_name": "Interactive Rebase, Cherry-Pick, Stashing, and History Rewriting", "estimated_hours": 3.0},
    ],
    "JavaScript": [
        {"topic_name": "Modern ES6+ Syntax (Let/Const, Destructuring, Spread, Arrow Functions)", "estimated_hours": 2.5},
        {"topic_name": "Asynchronous Programming (Promises, Async/Await, Event Loop)", "estimated_hours": 3.5},
        {"topic_name": "DOM Manipulation, Event Delegation, and Browser APIs", "estimated_hours": 3.0},
        {"topic_name": "Closures, Prototypes, and Scope Chains", "estimated_hours": 3.0},
    ],
    "TypeScript": [
        {"topic_name": "TypeScript Compiler (tsc), tsconfig.json, and Basic Types", "estimated_hours": 2.5},
        {"topic_name": "Interfaces, Type Aliases, and Union/Intersection Types", "estimated_hours": 3.0},
        {"topic_name": "Generics, Type Constraints, and Utility Types", "estimated_hours": 3.5},
        {"topic_name": "Strict Null Checks, Type Narrowing, and Discriminated Unions", "estimated_hours": 3.0},
    ],
    "React": [
        {"topic_name": "Component Architecture, JSX, and Virtual DOM", "estimated_hours": 3.0},
        {"topic_name": "State Management with useState and useReducer", "estimated_hours": 3.5},
        {"topic_name": "Side Effects, Cleanup, and Dependencies with useEffect", "estimated_hours": 3.5},
        {"topic_name": "Custom Hooks and Performance (useMemo, useCallback, React.memo)", "estimated_hours": 4.0},
        {"topic_name": "Client-Side Routing with React Router", "estimated_hours": 3.0},
    ],
    "HTML5": [
        {"topic_name": "Semantic Elements (header, nav, main, article, section, footer)", "estimated_hours": 2.0},
        {"topic_name": "Accessible Forms, Input Types, and Client-Side Validation", "estimated_hours": 2.5},
        {"topic_name": "Web Accessibility (a11y), ARIA Roles, and Screen Reader Standards", "estimated_hours": 2.5},
    ],
    "CSS3": [
        {"topic_name": "Box Model, Positioning, Specificity, and CSS Cascade", "estimated_hours": 2.5},
        {"topic_name": "Modern Layouts with Flexbox (Flex Direction, Justify, Align)", "estimated_hours": 3.0},
        {"topic_name": "Responsive Multi-Column Layouts with CSS Grid", "estimated_hours": 3.5},
        {"topic_name": "Transitions, Keyframe Animations, and Media Queries", "estimated_hours": 2.5},
    ],
    "Tailwind CSS": [
        {"topic_name": "Utility-First Paradigm and Tailwind v4 Setup", "estimated_hours": 2.0},
        {"topic_name": "Responsive Design Variants (sm, md, lg, xl)", "estimated_hours": 2.5},
        {"topic_name": "Dark Mode Implementation and Custom Theme Tokens", "estimated_hours": 2.5},
        {"topic_name": "Arbitrary Values, Reusable Components, and Layout Patterns", "estimated_hours": 2.5},
    ],
    "Data Structures": [
        {"topic_name": "Asymptotic Analysis (Big-O, Space vs Time Complexity)", "estimated_hours": 2.5},
        {"topic_name": "Linear Structures: Arrays, Dynamic Arrays, and Linked Lists", "estimated_hours": 3.5},
        {"topic_name": "Stacks and Queues: Implementations and Applications", "estimated_hours": 3.0},
        {"topic_name": "Hash Tables, Hash Functions, and Collision Resolution", "estimated_hours": 3.5},
        {"topic_name": "Trees: Binary Trees, BSTs, Traversals, and Heaps", "estimated_hours": 4.5},
        {"topic_name": "Graphs: Adjacency Lists, Adjacency Matrices, and Representations", "estimated_hours": 4.0},
    ],
    "Algorithms": [
        {"topic_name": "Two-Pointer and Sliding Window Techniques", "estimated_hours": 3.5},
        {"topic_name": "Searching (Binary Search Variations) and Sorting Algorithms", "estimated_hours": 3.5},
        {"topic_name": "Graph Traversal Algorithms (BFS and DFS with Applications)", "estimated_hours": 4.5},
        {"topic_name": "Greedy Algorithms and Backtracking", "estimated_hours": 4.0},
        {"topic_name": "Dynamic Programming: Memoization vs Tabulation Patterns", "estimated_hours": 5.0},
    ],
    "System Design": [
        {"topic_name": "Scalability Fundamentals: Vertical vs Horizontal Scaling and Load Balancing", "estimated_hours": 3.0},
        {"topic_name": "Caching Strategies (Cache-Aside, Write-Through) with Redis", "estimated_hours": 3.5},
        {"topic_name": "Database Sharding, Replication, and CAP Theorem Trade-offs", "estimated_hours": 4.0},
        {"topic_name": "Message Queues and Event-Driven Asynchronous Processing", "estimated_hours": 4.0},
        {"topic_name": "Designing High-Availability Real-World Systems (e.g. URL Shortener, Chat)", "estimated_hours": 4.5},
    ],
    "Redis": [
        {"topic_name": "In-Memory Data Store Architecture and Installation", "estimated_hours": 2.0},
        {"topic_name": "Core Data Types: Strings, Hashes, Lists, Sets, and Sorted Sets", "estimated_hours": 3.0},
        {"topic_name": "Key Expiration, Eviction Policies, and TTL Cache Patterns", "estimated_hours": 2.5},
        {"topic_name": "Pub/Sub Messaging and Distributed Rate Limiting", "estimated_hours": 3.0},
    ],
    "CI/CD": [
        {"topic_name": "Continuous Integration vs Continuous Delivery Concepts", "estimated_hours": 2.0},
        {"topic_name": "GitHub Actions: Workflows, Jobs, Steps, and Runners", "estimated_hours": 3.0},
        {"topic_name": "Automated Linting, Unit Testing, and Security Scanning in Pipelines", "estimated_hours": 3.0},
        {"topic_name": "Automated Container Build, Tagging, and Registry Publishing", "estimated_hours": 3.5},
    ],
    "Linux": [
        {"topic_name": "Linux File System Hierarchy, Permissions, and User Management", "estimated_hours": 2.5},
        {"topic_name": "Essential Shell Navigation, Text Processing (grep, awk, sed)", "estimated_hours": 3.0},
        {"topic_name": "Process Monitoring (ps, top, kill), Systemd, and Daemons", "estimated_hours": 2.5},
        {"topic_name": "Bash Scripting, Environment Variables, and Automation", "estimated_hours": 3.0},
    ],
    "Machine Learning": [
        {"topic_name": "Supervised vs Unsupervised Learning Frameworks", "estimated_hours": 2.5},
        {"topic_name": "Feature Engineering, Scaling, and Train/Test Splitting", "estimated_hours": 3.0},
        {"topic_name": "Regression Models (Linear, Ridge, Lasso) and Metrics (MSE, R2)", "estimated_hours": 3.5},
        {"topic_name": "Classification Models (Logistic Regression, Decision Trees, Random Forests)", "estimated_hours": 4.0},
        {"topic_name": "Cross-Validation, Hyperparameter Tuning, and Overfitting Prevention", "estimated_hours": 3.5},
    ],
    "Deep Learning": [
        {"topic_name": "Artificial Neural Networks (Perceptrons, Activation Functions, Forward Pass)", "estimated_hours": 3.5},
        {"topic_name": "Loss Functions, Backpropagation, and Gradient Descent Optimizers", "estimated_hours": 4.0},
        {"topic_name": "Convolutional Neural Networks (CNNs) for Computer Vision", "estimated_hours": 4.5},
        {"topic_name": "Recurrent Architectures, Attention Mechanisms, and Transformer Fundamentals", "estimated_hours": 5.0},
    ],
    "PyTorch": [
        {"topic_name": "Tensors, GPU Acceleration with CUDA, and Tensor Operations", "estimated_hours": 3.0},
        {"topic_name": "Autograd: Automatic Differentiation and Computational Graphs", "estimated_hours": 3.0},
        {"topic_name": "Building Neural Networks with torch.nn and Custom Modules", "estimated_hours": 4.0},
        {"topic_name": "Data Loading with Dataset and DataLoader", "estimated_hours": 3.0},
        {"topic_name": "Training Loop Architecture, Validation, and Model Checkpointing", "estimated_hours": 4.0},
    ],
}


# =============================================================================
# 3. Practical Hands-On Exercise per Skill
# =============================================================================

SKILL_PRACTICAL_PROJECTS: Dict[str, Dict[str, str | List[str]]] = {
    "FastAPI": {
        "title": "Production REST API with Auth & Database",
        "description": "Build a secure RESTful Task Management API using FastAPI, SQLAlchemy, and Pydantic v2.",
        "deliverables": [
            "CRUD endpoints with query pagination and status filtering",
            "JWT bearer token authentication and password hashing",
            "Database integration with SQLite or PostgreSQL via SQLAlchemy",
            "Comprehensive pytest integration tests using TestClient",
        ],
    },
    "SQL": {
        "title": "Business Intelligence Database Analytics",
        "description": "Design an e-commerce schema and write analytical queries answering core business questions.",
        "deliverables": [
            "Normalized 3NF relational schema with foreign key constraints",
            "Multi-table joins extracting customer lifetime value and order metrics",
            "Window functions ranking top-performing product categories",
            "Common Table Expressions (CTEs) analyzing monthly churn rates",
        ],
    },
    "Docker": {
        "title": "Containerized Multi-Service Web Application",
        "description": "Containerize a full-stack Python and database application with Docker and Docker Compose.",
        "deliverables": [
            "Multi-stage Dockerfile minimizing image layer size",
            "Named volumes for persistent database storage",
            "Docker network isolating backend API and database services",
            "Docker Compose configuration supporting one-command deployment",
        ],
    },
    "PostgreSQL": {
        "title": "High-Performance PostgreSQL Schema & Optimization",
        "description": "Implement indexed schema with JSONB support and query optimization.",
        "deliverables": [
            "Table definitions utilizing JSONB and UUID primary keys",
            "EXPLAIN ANALYZE comparison before and after indexing",
            "ACID transaction block ensuring atomic multi-step balance transfer",
            "Alembic migration script for repeatable schema upgrades",
        ],
    },
    "Python": {
        "title": "Robust Automated CLI Data Pipeline",
        "description": "Build an idiomatic Python command-line tool that parses, processes, and exports structured data.",
        "deliverables": [
            "Modular architecture with classes, custom exceptions, and type hints",
            "Context managers ensuring safe file handles and external connections",
            "Unit test suite achieving >85% code coverage with pytest",
        ],
    },
    "React": {
        "title": "Interactive Analytics Dashboard Component",
        "description": "Develop a responsive React dashboard with client-side state and async API integration.",
        "deliverables": [
            "Custom hooks encapsulating async data fetching and error states",
            "Optimized rendering with useMemo and useCallback",
            "Clean component hierarchy styled with Tailwind CSS",
        ],
    },
    "System Design": {
        "title": "Distributed Scalable Service Architecture Design",
        "description": "Author an architectural blueprint for a scalable service handling 10,000 requests/sec.",
        "deliverables": [
            "High-level architecture diagram detailing load balancing and caching",
            "Database schema and data partitioning strategy",
            "Cache invalidation protocol using Redis",
            "Failure mode analysis and resilience redundancy planning",
        ],
    },
}


# =============================================================================
# 4. Topological Sorting & Dependency Sequencing
# =============================================================================

def get_skill_prerequisites(skill_name: str) -> List[str]:
    """Retrieve direct prerequisites for a skill."""
    return SKILL_DEPENDENCY_GRAPH.get(skill_name, [])


def get_skill_topics(skill_name: str) -> List[Dict[str, float | str]]:
    """
    Retrieve structured sequential topics for a skill.
    Provides a standardized 4-topic fallback if the skill is not explicitly in the catalog.
    """
    if skill_name in SKILL_TOPIC_SYLLABUS:
        return SKILL_TOPIC_SYLLABUS[skill_name]

    # Standardized fallback syllabus
    return [
        {"topic_name": f"{skill_name} Core Fundamentals and Architecture", "estimated_hours": 2.5},
        {"topic_name": f"{skill_name} Practical Syntax, Methods, and Tooling", "estimated_hours": 3.0},
        {"topic_name": f"{skill_name} Advanced Patterns and Integration", "estimated_hours": 3.5},
        {"topic_name": f"{skill_name} Testing, Debugging, and Best Practices", "estimated_hours": 3.0},
    ]


def get_skill_practical_project(skill_name: str) -> Dict[str, str | List[str]]:
    """Retrieve or generate an actionable hands-on task for a skill."""
    if skill_name in SKILL_PRACTICAL_PROJECTS:
        return SKILL_PRACTICAL_PROJECTS[skill_name]

    return {
        "title": f"Hands-On {skill_name} Practical Implementation",
        "description": f"Build a practical proof-of-concept demonstrating core {skill_name} capabilities and best practices.",
        "deliverables": [
            f"Configured and working {skill_name} implementation",
            "Clean code following official community conventions",
            "Documentation explaining architecture and key trade-offs",
        ],
    }


def topological_sort_skills(
    skills_to_learn: List[str],
    candidate_known_skills: Optional[Set[str]] = None,
) -> List[str]:
    """
    Sort skills into a sound learning sequence where all prerequisites appear
    before dependent skills.

    Features:
    - Prerequisite knowledge: Skills in `candidate_known_skills` do not block dependents.
    - Cycle safety: Uses three-color DFS (WHITE=0, GRAY=1, BLACK=2) to detect and break
      circular dependencies without crashing or looping infinitely.
    - Deterministic order: Stable tie-breaking for equal-depth skills.

    Parameters:
        skills_to_learn: List of target skill names to sequence.
        candidate_known_skills: Set of skills the candidate has already mastered.

    Returns:
        Ordered list of skill names from fundamental to advanced.
    """
    known = {s.strip().lower() for s in (candidate_known_skills or set())}
    target_set = {s for s in skills_to_learn}

    # Build adjacency graph within target skills
    # An edge U -> V means U must be learned before V (U is prerequisite of V)
    adj: Dict[str, List[str]] = {s: [] for s in target_set}
    in_degree: Dict[str, int] = {s: 0 for s in target_set}

    for skill in target_set:
        prereqs = SKILL_DEPENDENCY_GRAPH.get(skill, [])
        for prereq in prereqs:
            # If candidate already knows this prereq, it does not constrain sequence
            if prereq.lower() in known:
                continue

            # If prereq is also one of the skills to learn, prereq -> skill
            if prereq in target_set:
                adj[prereq].append(skill)
                in_degree[skill] += 1

    # Cycle-safe Kahn's algorithm with priority queue simulation
    queue = [s for s in target_set if in_degree[s] == 0]
    queue.sort()  # deterministic tie-break

    ordered: List[str] = []
    visited_count = 0

    while queue:
        current = queue.pop(0)
        ordered.append(current)
        visited_count += 1

        for neighbor in sorted(adj[current]):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
                queue.sort()

    # If there was a circular dependency, append remaining unvisited skills gracefully
    if visited_count < len(target_set):
        logger.warning(
            "Circular or unresolved dependency detected in learning roadmap skills: %s. "
            "Appending remaining skills gracefully.",
            [s for s in target_set if s not in ordered],
        )
        remaining = sorted([s for s in target_set if s not in ordered])
        ordered.extend(remaining)

    return ordered

