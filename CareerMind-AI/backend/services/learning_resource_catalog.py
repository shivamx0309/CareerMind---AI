"""
Curated Free Learning Resource Catalog.
Provides verified, real URLs for official documentation, open tutorials,
interactive platforms, and high-quality free learning materials.
"""

from typing import Dict, List, Optional


# Verified Free Learning Resources by Skill and Keyword Topic
RESOURCE_CATALOG: Dict[str, List[Dict[str, str | int | bool]]] = {
    "Python": [
        {
            "title": "Python 3 Official Tutorial — An Informal Introduction",
            "url": "https://docs.python.org/3/tutorial/introduction.html",
            "provider": "Python Software Foundation",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "beginner",
            "estimated_minutes": 45,
            "topic_match": "Variables, Primitive Types, and Control Flow",
        },
        {
            "title": "Defining Functions in Python",
            "url": "https://docs.python.org/3/tutorial/controlflow.html#defining-functions",
            "provider": "Python Software Foundation",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "beginner",
            "estimated_minutes": 40,
            "topic_match": "Functions, Scope, and First-Class Callables",
        },
        {
            "title": "Data Structures — Official Python Documentation",
            "url": "https://docs.python.org/3/tutorial/datastructures.html",
            "provider": "Python Software Foundation",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "intermediate",
            "estimated_minutes": 50,
            "topic_match": "Data Structures (Lists, Dicts, Sets, Tuples)",
        },
        {
            "title": "Classes and Object-Oriented Programming in Python",
            "url": "https://docs.python.org/3/tutorial/classes.html",
            "provider": "Python Software Foundation",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "intermediate",
            "estimated_minutes": 60,
            "topic_match": "Object-Oriented Programming",
        },
        {
            "title": "Errors, Exceptions and File I/O in Python",
            "url": "https://docs.python.org/3/tutorial/errors.html",
            "provider": "Python Software Foundation",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "intermediate",
            "estimated_minutes": 45,
            "topic_match": "Exception Handling",
        },
    ],
    "FastAPI": [
        {
            "title": "FastAPI Tutorial — First Steps & Concurrency",
            "url": "https://fastapi.tiangolo.com/tutorial/first-steps/",
            "provider": "FastAPI Documentation",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "beginner",
            "estimated_minutes": 35,
            "topic_match": "Async Python, Type Annotations, and FastAPI Quickstart",
        },
        {
            "title": "Request Body, Path & Query Parameters with Pydantic",
            "url": "https://fastapi.tiangolo.com/tutorial/body/",
            "provider": "FastAPI Documentation",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "beginner",
            "estimated_minutes": 45,
            "topic_match": "Pydantic",
        },
        {
            "title": "FastAPI Dependency Injection System",
            "url": "https://fastapi.tiangolo.com/tutorial/dependencies/",
            "provider": "FastAPI Documentation",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "intermediate",
            "estimated_minutes": 50,
            "topic_match": "Dependency Injection",
        },
        {
            "title": "SQL Databases with SQLAlchemy and FastAPI",
            "url": "https://fastapi.tiangolo.com/tutorial/sql-databases/",
            "provider": "FastAPI Documentation",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "intermediate",
            "estimated_minutes": 60,
            "topic_match": "SQLAlchemy Database Integration",
        },
        {
            "title": "OAuth2 with Password (and hashing), Bearer with JWT tokens",
            "url": "https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/",
            "provider": "FastAPI Documentation",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "advanced",
            "estimated_minutes": 60,
            "topic_match": "JWT Authentication",
        },
        {
            "title": "Testing FastAPI Applications with Pytest and TestClient",
            "url": "https://fastapi.tiangolo.com/tutorial/testing/",
            "provider": "FastAPI Documentation",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "intermediate",
            "estimated_minutes": 45,
            "topic_match": "Testing with Pytest",
        },
    ],
    "SQL": [
        {
            "title": "SQLBolt — Interactive Lessons in Relational Queries",
            "url": "https://sqlbolt.com/",
            "provider": "SQLBolt",
            "resource_type": "interactive",
            "is_free": True,
            "difficulty": "beginner",
            "estimated_minutes": 45,
            "topic_match": "Data Querying and Filtering",
        },
        {
            "title": "PostgreSQL Tutorial — Joins and Multi-Table Relationships",
            "url": "https://www.postgresql.org/docs/current/tutorial-join.html",
            "provider": "PostgreSQL Global Development Group",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "intermediate",
            "estimated_minutes": 40,
            "topic_match": "Multi-Table Joins",
        },
        {
            "title": "PostgreSQL Aggregate Functions and Grouping",
            "url": "https://www.postgresql.org/docs/current/tutorial-agg.html",
            "provider": "PostgreSQL Global Development Group",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "intermediate",
            "estimated_minutes": 35,
            "topic_match": "Grouping, Aggregations",
        },
        {
            "title": "Modern SQL Window Functions Tutorial",
            "url": "https://mode.com/sql-tutorial/sql-window-functions/",
            "provider": "Mode Analytics",
            "resource_type": "tutorial",
            "is_free": True,
            "difficulty": "advanced",
            "estimated_minutes": 55,
            "topic_match": "Window Functions",
        },
    ],
    "Docker": [
        {
            "title": "Docker Official Orientation and Container Setup",
            "url": "https://docs.docker.com/get-started/",
            "provider": "Docker Docs",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "beginner",
            "estimated_minutes": 40,
            "topic_match": "Containerization Concepts",
        },
        {
            "title": "Dockerfile Best Practices and Multi-Stage Builds",
            "url": "https://docs.docker.com/build/building/best-practices/",
            "provider": "Docker Docs",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "intermediate",
            "estimated_minutes": 45,
            "topic_match": "Writing Multi-Stage",
        },
        {
            "title": "Manage Data in Docker Volumes and Bind Mounts",
            "url": "https://docs.docker.com/storage/volumes/",
            "provider": "Docker Docs",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "intermediate",
            "estimated_minutes": 35,
            "topic_match": "Data Persistence",
        },
        {
            "title": "Getting Started with Docker Compose",
            "url": "https://docs.docker.com/compose/gettingstarted/",
            "provider": "Docker Docs",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "intermediate",
            "estimated_minutes": 50,
            "topic_match": "Docker Compose",
        },
    ],
    "PostgreSQL": [
        {
            "title": "PostgreSQL Official Documentation Tutorial",
            "url": "https://www.postgresql.org/docs/current/tutorial.html",
            "provider": "PostgreSQL Global Development Group",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "beginner",
            "estimated_minutes": 45,
            "topic_match": "Architecture",
        },
        {
            "title": "PostgreSQL JSON Types and JSONB Querying",
            "url": "https://www.postgresql.org/docs/current/datatype-json.html",
            "provider": "PostgreSQL Global Development Group",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "intermediate",
            "estimated_minutes": 40,
            "topic_match": "JSONB",
        },
        {
            "title": "PostgreSQL Index Types and EXPLAIN Performance Tuning",
            "url": "https://www.postgresql.org/docs/current/indexes.html",
            "provider": "PostgreSQL Global Development Group",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "advanced",
            "estimated_minutes": 50,
            "topic_match": "Index Types",
        },
    ],
    "REST API": [
        {
            "title": "MDN Web Docs — HTTP Methods and Status Codes",
            "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods",
            "provider": "Mozilla Developer Network",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "beginner",
            "estimated_minutes": 35,
            "topic_match": "HTTP Protocols",
        },
        {
            "title": "REST API Design Best Practices Handbook",
            "url": "https://www.freecodecamp.org/news/rest-api-design-best-practices/",
            "provider": "freeCodeCamp",
            "resource_type": "tutorial",
            "is_free": True,
            "difficulty": "intermediate",
            "estimated_minutes": 45,
            "topic_match": "RESTful Resource Modeling",
        },
    ],
    "Git": [
        {
            "title": "Pro Git Book — Git Basics and Commits",
            "url": "https://git-scm.com/book/en/v2/Git-Basics-Getting-a-Git-Repository",
            "provider": "Git Official",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "beginner",
            "estimated_minutes": 40,
            "topic_match": "Version Control Fundamentals",
        },
        {
            "title": "Pro Git Book — Git Branching and Merging",
            "url": "https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging",
            "provider": "Git Official",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "intermediate",
            "estimated_minutes": 45,
            "topic_match": "Branching Strategies",
        },
    ],
    "React": [
        {
            "title": "React.dev — Describing the UI with Components",
            "url": "https://react.dev/learn/describing-the-ui",
            "provider": "React Documentation",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "beginner",
            "estimated_minutes": 40,
            "topic_match": "Component Architecture",
        },
        {
            "title": "React.dev — Managing State and Interactivity",
            "url": "https://react.dev/learn/managing-state",
            "provider": "React Documentation",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "intermediate",
            "estimated_minutes": 50,
            "topic_match": "State Management",
        },
        {
            "title": "Synchronizing with Effects in React",
            "url": "https://react.dev/learn/synchronizing-with-effects",
            "provider": "React Documentation",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "intermediate",
            "estimated_minutes": 45,
            "topic_match": "Side Effects",
        },
    ],
    "System Design": [
        {
            "title": "The System Design Primer — Comprehensive Architecture Guide",
            "url": "https://github.com/donnemartin/system-design-primer",
            "provider": "Open Source / GitHub",
            "resource_type": "course",
            "is_free": True,
            "difficulty": "advanced",
            "estimated_minutes": 90,
            "topic_match": "Scalability Fundamentals",
        },
    ],
    "Data Structures": [
        {
            "title": "Python Data Structures and Algorithms Interactive Overview",
            "url": "https://docs.python.org/3/tutorial/datastructures.html",
            "provider": "Python Software Foundation",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "intermediate",
            "estimated_minutes": 55,
            "topic_match": "Linear Structures",
        },
    ],
    "Machine Learning": [
        {
            "title": "Scikit-Learn Official Getting Started Tutorial",
            "url": "https://scikit-learn.org/stable/getting_started.html",
            "provider": "Scikit-learn Community",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "intermediate",
            "estimated_minutes": 50,
            "topic_match": "Supervised vs Unsupervised",
        },
    ],
    "PyTorch": [
        {
            "title": "PyTorch Learn the Basics Tutorial",
            "url": "https://pytorch.org/tutorials/beginner/basics/intro.html",
            "provider": "PyTorch Foundation",
            "resource_type": "tutorial",
            "is_free": True,
            "difficulty": "intermediate",
            "estimated_minutes": 55,
            "topic_match": "Tensors",
        },
    ],
}


# General Official Portals for Fallbacks
OFFICIAL_SKILL_PORTALS: Dict[str, str] = {
    "Python": "https://docs.python.org/3/",
    "FastAPI": "https://fastapi.tiangolo.com/",
    "SQL": "https://www.postgresql.org/docs/",
    "PostgreSQL": "https://www.postgresql.org/docs/",
    "Docker": "https://docs.docker.com/",
    "REST API": "https://developer.mozilla.org/en-US/docs/Web/HTTP",
    "Git": "https://git-scm.com/doc",
    "JavaScript": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
    "TypeScript": "https://www.typescriptlang.org/docs/",
    "React": "https://react.dev/",
    "HTML5": "https://developer.mozilla.org/en-US/docs/Web/HTML",
    "CSS3": "https://developer.mozilla.org/en-US/docs/Web/CSS",
    "Tailwind CSS": "https://tailwindcss.com/docs",
    "Data Structures": "https://docs.python.org/3/tutorial/datastructures.html",
    "Algorithms": "https://docs.python.org/3/library/",
    "System Design": "https://github.com/donnemartin/system-design-primer",
    "Redis": "https://redis.io/docs/",
    "CI/CD": "https://docs.github.com/en/actions",
    "Linux": "https://tldp.org/LDP/intro-linux/html/",
    "Machine Learning": "https://scikit-learn.org/stable/",
    "Deep Learning": "https://pytorch.org/tutorials/",
    "PyTorch": "https://pytorch.org/docs/stable/index.html",
}


def get_resources_for_topic(skill_name: str, topic_name: str) -> List[Dict[str, str | int | bool]]:
    """
    Retrieve matching verified free resources for a specific topic within a skill.
    If no exact topic match is found, provides the skill's official documentation reference.
    """
    skill_resources = RESOURCE_CATALOG.get(skill_name, [])
    matches: List[Dict[str, str | int | bool]] = []

    topic_lower = topic_name.lower()
    for res in skill_resources:
        match_keyword = str(res.get("topic_match", "")).lower()
        if match_keyword and (match_keyword in topic_lower or any(word in topic_lower for word in match_keyword.split() if len(word) > 4)):
            matches.append(res)

    if matches:
        return matches

    # Return primary resource for skill if available
    if skill_resources:
        return [skill_resources[0]]

    # Fallback to official portal URL
    portal_url = OFFICIAL_SKILL_PORTALS.get(skill_name, "https://devdocs.io/")
    return [
        {
            "title": f"{skill_name} Official Reference Guide",
            "url": portal_url,
            "provider": f"{skill_name} Community / Documentation",
            "resource_type": "documentation",
            "is_free": True,
            "difficulty": "intermediate",
            "estimated_minutes": 45,
            "topic_match": topic_name,
        }
    ]

