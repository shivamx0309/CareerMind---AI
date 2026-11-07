"""
Technical skills parser and categorizer for resume intelligence.

Maps discovered technical keywords and competencies into 10 structured domains:
1. Programming Languages
2. Frontend Technologies
3. Backend Technologies
4. Databases
5. Data Analytics
6. Machine Learning
7. Deep Learning
8. Cloud and DevOps
9. Tools and Platforms
10. Other Technical Skills

Features:
- Canonical skill names with alias resolution (e.g. React.js -> React, REST APIs -> REST API).
- Deduplication and overlap suppression (e.g. Data Structures & Algorithms subsumes DSA and Algorithms).
- Priority given to explicitly declared skills sections and project tech stacks.
- Protection against false positive matches from general English prose (e.g. regression testing).
"""

import re
from schemas.candidate_schema import TechnicalSkills


# Canonical alias dictionary: maps lowercase aliases to canonical display names
CANONICAL_ALIASES: dict[str, str] = {
    # Programming Languages
    "python": "Python",
    "python3": "Python",
    "java": "Java",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "sql": "SQL",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    "golang": "Go",
    "rust": "Rust",
    "ruby": "Ruby",
    "php": "PHP",
    "swift": "Swift",
    "kotlin": "Kotlin",
    "dart": "Dart",
    "scala": "Scala",
    "shell": "Shell",
    "bash": "Bash",
    "powershell": "PowerShell",
    "matlab": "MATLAB",

    # Frontend
    "react": "React",
    "react.js": "React",
    "reactjs": "React",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "vue": "Vue.js",
    "vue.js": "Vue.js",
    "vuejs": "Vue.js",
    "angular": "Angular",
    "angular.js": "Angular",
    "html": "HTML5",
    "html5": "HTML5",
    "css": "CSS3",
    "css3": "CSS3",
    "tailwind": "Tailwind CSS",
    "tailwind css": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "bootstrap": "Bootstrap",
    "redux": "Redux",
    "svelte": "Svelte",
    "jquery": "jQuery",
    "sass": "Sass",
    "scss": "Sass",
    "vite": "Vite",
    "webpack": "Webpack",

    # Backend
    "node": "Node.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "express": "Express",
    "express.js": "Express",
    "expressjs": "Express",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "spring boot": "Spring Boot",
    "spring": "Spring Boot",
    "asp.net": "ASP.NET",
    ".net core": ".NET Core",
    "ruby on rails": "Ruby on Rails",
    "nest.js": "NestJS",
    "nestjs": "NestJS",
    "graphql": "GraphQL",
    "rest api": "REST API",
    "rest apis": "REST API",
    "restful api": "REST API",
    "restful apis": "REST API",
    "socket.io": "Socket.IO",
    "socketio": "Socket.IO",
    "jwt": "JWT",
    "grpc": "gRPC",

    # Databases
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "supabase": "Supabase",
    "redis": "Redis",
    "sqlite": "SQLite",
    "oracle": "Oracle",
    "cassandra": "Cassandra",
    "elasticsearch": "Elasticsearch",
    "dynamodb": "DynamoDB",
    "mariadb": "MariaDB",
    "firebase": "Firebase",
    "firestore": "Firestore",

    # Data Analytics
    "pandas": "Pandas",
    "numpy": "NumPy",
    "power bi": "Power BI",
    "powerbi": "Power BI",
    "excel": "Excel",
    "microsoft excel": "Excel",
    "tableau": "Tableau",
    "matplotlib": "Matplotlib",
    "seaborn": "Seaborn",
    "eda": "EDA",
    "exploratory data analysis": "EDA",
    "data cleaning": "Data Cleaning",
    "data visualization": "Data Visualization",
    "business intelligence": "Business Intelligence",
    "bi": "Business Intelligence",
    "data analytics": "Data Analytics",
    "data analysis": "Data Analytics",
    "operational data analysis": "Data Analytics",
    "bigquery": "BigQuery",
    "snowflake": "Snowflake",
    "spark": "Apache Spark",
    "apache spark": "Apache Spark",
    "databricks": "Databricks",
    "etl": "ETL",

    # Machine Learning
    "scikit-learn": "Scikit-learn",
    "sklearn": "Scikit-learn",
    "logistic regression": "Logistic Regression",
    "linear regression": "Linear Regression",
    "classification": "Classification",
    "clustering": "Clustering",
    "random forest": "Random Forest",
    "xgboost": "XGBoost",
    "lightgbm": "LightGBM",
    "decision tree": "Decision Tree",
    "decision trees": "Decision Tree",
    "svm": "SVM",
    "feature engineering": "Feature Engineering",
    "k-means": "K-Means",
    "time series": "Time Series",

    # Deep Learning
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "keras": "Keras",
    "cnn": "CNN",
    "rnn": "RNN",
    "lstm": "LSTM",
    "transformers": "Transformers",
    "hugging face": "Hugging Face",
    "bert": "BERT",
    "opencv": "OpenCV",
    "llms": "LLMs",
    "llm": "LLMs",
    "nlp": "NLP",
    "langchain": "LangChain",
    "neural networks": "Neural Networks",
    "generative ai": "Generative AI",
    "genai": "Generative AI",

    # Cloud & DevOps
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Azure",
    "google cloud": "Google Cloud",
    "gcp": "Google Cloud",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "ci/cd": "CI/CD",
    "github actions": "GitHub Actions",
    "terraform": "Terraform",
    "jenkins": "Jenkins",
    "ansible": "Ansible",
    "linux": "Linux",
    "nginx": "Nginx",

    # Tools
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "vs code": "VS Code",
    "visual studio code": "VS Code",
    "jupyter": "Jupyter Notebook",
    "jupyter notebook": "Jupyter Notebook",
    "postman": "Postman",
    "jira": "Jira",
    "bitbucket": "Bitbucket",
    "figma": "Figma",

    # Other
    "data structures & algorithms": "Data Structures & Algorithms",
    "data structures and algorithms": "Data Structures & Algorithms",
    "data structures": "Data Structures & Algorithms",
    "algorithms": "Data Structures & Algorithms",
    "dsa": "Data Structures & Algorithms",
    "oop": "OOP",
    "object-oriented programming": "OOP",
    "dbms": "DBMS",
    "database management systems": "DBMS",
    "operating systems": "Operating Systems",
    "os": "Operating Systems",
    "sdlc": "SDLC",
    "agile": "Agile",
    "scrum": "Agile",
    "debugging": "Debugging",
    "web testing": "Web Testing",
    "unit testing": "Unit Testing",
    "problem solving": "Problem Solving",
}

# Domain mapping for canonical skill names
CANONICAL_TO_CATEGORY: dict[str, str] = {
    # Programming Languages
    "Python": "programming_languages",
    "Java": "programming_languages",
    "JavaScript": "programming_languages",
    "TypeScript": "programming_languages",
    "SQL": "programming_languages",
    "C++": "programming_languages",
    "C#": "programming_languages",
    "C": "programming_languages",
    "Go": "programming_languages",
    "Rust": "programming_languages",
    "Ruby": "programming_languages",
    "PHP": "programming_languages",
    "Swift": "programming_languages",
    "Kotlin": "programming_languages",
    "Dart": "programming_languages",
    "Scala": "programming_languages",
    "Shell": "programming_languages",
    "Bash": "programming_languages",
    "PowerShell": "programming_languages",
    "MATLAB": "programming_languages",

    # Frontend
    "React": "frontend",
    "Next.js": "frontend",
    "Vue.js": "frontend",
    "Angular": "frontend",
    "HTML5": "frontend",
    "CSS3": "frontend",
    "Tailwind CSS": "frontend",
    "Bootstrap": "frontend",
    "Redux": "frontend",
    "Svelte": "frontend",
    "jQuery": "frontend",
    "Sass": "frontend",
    "Vite": "frontend",
    "Webpack": "frontend",

    # Backend
    "Node.js": "backend",
    "Express": "backend",
    "FastAPI": "backend",
    "Django": "backend",
    "Flask": "backend",
    "Spring Boot": "backend",
    "ASP.NET": "backend",
    ".NET Core": "backend",
    "Ruby on Rails": "backend",
    "NestJS": "backend",
    "GraphQL": "backend",
    "REST API": "backend",
    "Socket.IO": "backend",
    "JWT": "backend",
    "gRPC": "backend",

    # Databases
    "MySQL": "databases",
    "MongoDB": "databases",
    "PostgreSQL": "databases",
    "Supabase": "databases",
    "Redis": "databases",
    "SQLite": "databases",
    "Oracle": "databases",
    "Cassandra": "databases",
    "Elasticsearch": "databases",
    "DynamoDB": "databases",
    "MariaDB": "databases",
    "Firebase": "databases",
    "Firestore": "databases",

    # Data Analytics
    "Pandas": "data_analytics",
    "NumPy": "data_analytics",
    "Power BI": "data_analytics",
    "Excel": "data_analytics",
    "Tableau": "data_analytics",
    "Matplotlib": "data_analytics",
    "Seaborn": "data_analytics",
    "EDA": "data_analytics",
    "Data Cleaning": "data_analytics",
    "Data Visualization": "data_analytics",
    "Business Intelligence": "data_analytics",
    "Data Analytics": "data_analytics",
    "BigQuery": "data_analytics",
    "Snowflake": "data_analytics",
    "Apache Spark": "data_analytics",
    "Databricks": "data_analytics",
    "ETL": "data_analytics",

    # Machine Learning
    "Scikit-learn": "machine_learning",
    "Regression": "machine_learning",
    "Logistic Regression": "machine_learning",
    "Linear Regression": "machine_learning",
    "Classification": "machine_learning",
    "Clustering": "machine_learning",
    "Random Forest": "machine_learning",
    "XGBoost": "machine_learning",
    "LightGBM": "machine_learning",
    "Decision Tree": "machine_learning",
    "SVM": "machine_learning",
    "Feature Engineering": "machine_learning",
    "K-Means": "machine_learning",
    "Time Series": "machine_learning",

    # Deep Learning
    "TensorFlow": "deep_learning",
    "PyTorch": "deep_learning",
    "Keras": "deep_learning",
    "CNN": "deep_learning",
    "RNN": "deep_learning",
    "LSTM": "deep_learning",
    "Transformers": "deep_learning",
    "Hugging Face": "deep_learning",
    "BERT": "deep_learning",
    "OpenCV": "deep_learning",
    "LLMs": "deep_learning",
    "NLP": "deep_learning",
    "LangChain": "deep_learning",
    "Neural Networks": "deep_learning",
    "Generative AI": "deep_learning",

    # Cloud & DevOps
    "AWS": "cloud_devops",
    "Azure": "cloud_devops",
    "Google Cloud": "cloud_devops",
    "Docker": "cloud_devops",
    "Kubernetes": "cloud_devops",
    "CI/CD": "cloud_devops",
    "GitHub Actions": "cloud_devops",
    "Terraform": "cloud_devops",
    "Jenkins": "cloud_devops",
    "Ansible": "cloud_devops",
    "Linux": "cloud_devops",
    "Nginx": "cloud_devops",

    # Tools
    "Git": "tools",
    "GitHub": "tools",
    "GitLab": "tools",
    "VS Code": "tools",
    "Jupyter Notebook": "tools",
    "Postman": "tools",
    "Jira": "tools",
    "Bitbucket": "tools",
    "Figma": "tools",

    # Other
    "Data Structures & Algorithms": "other",
    "OOP": "other",
    "DBMS": "other",
    "Operating Systems": "other",
    "SDLC": "other",
    "Agile": "other",
    "Debugging": "other",
    "Web Testing": "other",
    "Unit Testing": "other",
    "Problem Solving": "other",
}

# Regex patterns for backward compatibility and fallback scanning
SKILL_TAXONOMY: dict[str, list[tuple[str, str]]] = {
    "programming_languages": [
        ("Python", r"\bpython(?:3)?\b"),
        ("SQL", r"\bsql\b"),
        ("Java", r"\bjava\b(?!script)"),
        ("JavaScript", r"\bjavascript\b|\bjs\b"),
        ("TypeScript", r"\btypescript\b|\bts\b"),
        ("C++", r"\bc\+\+\b"),
        ("C#", r"\bc\#\b|\bc\s*sharp\b"),
        ("C", r"(?:[\s,/]|^)C(?=[\s,/]|$)"),
        ("Go", r"\bgolang\b|(?:\bGo\s+language\b)"),
        ("Rust", r"\brust\b"),
        ("Ruby", r"\bruby\b"),
        ("PHP", r"\bphp\b"),
        ("Swift", r"\bswift\b"),
        ("Kotlin", r"\bkotlin\b"),
        ("R", r"(?:[\s,/]|^)R(?=[\s,/]|$)"),
        ("Scala", r"\bscala\b"),
        ("Dart", r"\bdart\b"),
        ("Bash", r"\bbash\b"),
        ("Shell", r"\bshell\b"),
        ("PowerShell", r"\bpowershell\b"),
        ("MATLAB", r"\bmatlab\b"),
    ],
    "frontend": [
        ("React", r"\breact(?:\.?js)?\b"),
        ("Next.js", r"\bnext(?:\.?js)?\b"),
        ("Vue.js", r"\bvue(?:\.?js)?\b"),
        ("Angular", r"\bangular(?:\.?js)?\b"),
        ("HTML5", r"\bhtml5?\b"),
        ("CSS3", r"\bcss3?\b"),
        ("Tailwind CSS", r"\btailwind(?:\s*css)?\b"),
        ("Bootstrap", r"\bbootstrap(?:\s*5)?\b"),
        ("Redux", r"\bredux\b"),
        ("Svelte", r"\bsvelte\b"),
        ("jQuery", r"\bjquery\b"),
        ("Sass", r"\bsass\b|\bscss\b"),
        ("Vite", r"\bvite\b"),
        ("Webpack", r"\bwebpack\b"),
    ],
    "backend": [
        ("Node.js", r"\bnode(?:\.?js)?\b"),
        ("Express", r"\bexpress(?:\.?js)?\b"),
        ("FastAPI", r"\bfastapi\b"),
        ("Django", r"\bdjango\b"),
        ("Flask", r"\bflask\b"),
        ("Spring Boot", r"\bspring\s*boot\b"),
        ("ASP.NET", r"\basp\.net\b|\b\.net\s*core\b"),
        ("Ruby on Rails", r"\bruby\s*on\s*rails\b"),
        ("NestJS", r"\bnest(?:\.?js)?\b"),
        ("GraphQL", r"\bgraphql\b"),
        ("REST API", r"\brest(?:ful)?\s*(?:api|apis)?\b"),
        ("Socket.IO", r"\bsocket\.?io\b"),
        ("JWT", r"\bjwt\b"),
        ("gRPC", r"\bgrpc\b"),
    ],
    "databases": [
        ("MySQL", r"\bmysql\b"),
        ("MongoDB", r"\bmongo(?:db)?\b"),
        ("PostgreSQL", r"\bpostgre(?:sql)?\b|\bpostgres\b"),
        ("Supabase", r"\bsupabase\b"),
        ("Redis", r"\bredis\b"),
        ("SQLite", r"\bsqlite(?:3)?\b"),
        ("Oracle", r"\boracle(?:\s*db)?\b"),
        ("Cassandra", r"\bcassandra\b"),
        ("Elasticsearch", r"\belasticsearch\b"),
        ("DynamoDB", r"\bdynamodb\b"),
        ("MariaDB", r"\bmariadb\b"),
        ("Firebase", r"\bfirebase\b|\bfirestore\b"),
    ],
    "data_analytics": [
        ("Data Analytics", r"\bdata\s+analytics\b|\bdata\s+analysis\b|\boperational\s+data\s+analysis\b"),
        ("Pandas", r"\bpandas\b"),
        ("NumPy", r"\bnumpy\b"),
        ("Power BI", r"\bpower\s*bi\b"),
        ("Excel", r"\bexcel\b|\bmicrosoft\s+excel\b"),
        ("Tableau", r"\btableau\b"),
        ("Matplotlib", r"\bmatplotlib\b"),
        ("Seaborn", r"\bseaborn\b"),
        ("EDA", r"\beda\b|\bexploratory\s+data\s+analysis\b"),
        ("Data Cleaning", r"\bdata\s+cleaning\b"),
        ("Data Visualization", r"\bdata\s+visualization\b"),
        ("Business Intelligence", r"\bbusiness\s+intelligence\b|\bbi\b"),
        ("BigQuery", r"\bbigquery\b"),
        ("Snowflake", r"\bsnowflake\b"),
        ("Apache Spark", r"\bspark\b|\bpyspark\b"),
        ("Databricks", r"\bdatabricks\b"),
        ("ETL", r"\betl\b"),
    ],
    "machine_learning": [
        ("Scikit-learn", r"\bscikit-?learn\b|\bsklearn\b"),
        ("Regression", r"\bregression\s+(?:model|modeling|analysis)\b|\blinear\s+regression\b|\blogistic\s+regression\b"),
        ("Classification", r"\bclassification\b"),
        ("Clustering", r"\bclustering\b"),
        ("Random Forest", r"\brandom\s*forests?\b"),
        ("XGBoost", r"\bxgboost\b"),
        ("LightGBM", r"\blightgbm\b"),
        ("Decision Tree", r"\bdecision\s*trees?\b"),
        ("SVM", r"\bsvm\b"),
        ("Feature Engineering", r"\bfeature\s+engineering\b"),
        ("K-Means", r"\bk-?means\b"),
        ("Time Series", r"\btime\s+series\b"),
    ],
    "deep_learning": [
        ("TensorFlow", r"\btensorflow\b"),
        ("PyTorch", r"\bpytorch\b"),
        ("Keras", r"\bkeras\b"),
        ("CNN", r"\bcnn\b"),
        ("RNN", r"\brnn\b"),
        ("LSTM", r"\blstm\b"),
        ("Transformers", r"\btransformers\b"),
        ("Hugging Face", r"\bhugging\s*face\b"),
        ("BERT", r"\bbert\b"),
        ("OpenCV", r"\bopencv\b"),
        ("LLMs", r"\bllms?\b|\blarge\s+language\s+models?\b"),
        ("NLP", r"\bnlp\b"),
        ("LangChain", r"\blangchain\b"),
        ("Neural Networks", r"\bneural\s+networks?\b"),
        ("Generative AI", r"\bgenerative\s+ai\b|\bgenai\b"),
    ],
    "cloud_devops": [
        ("AWS", r"\baws\b|\bamazon\s+web\s+services\b"),
        ("Azure", r"\bazure\b"),
        ("Google Cloud", r"\bgoogle\s+cloud\b|\bgcp\b"),
        ("Docker", r"\bdocker\b"),
        ("Kubernetes", r"\bkubernetes\b|\bk8s\b"),
        ("CI/CD", r"\bci[\s/]*cd\b"),
        ("GitHub Actions", r"\bgithub\s+actions\b"),
        ("Terraform", r"\bterraform\b"),
        ("Jenkins", r"\bjenkins\b"),
        ("Ansible", r"\bansible\b"),
        ("Linux", r"\blinux\b"),
        ("Nginx", r"\bnginx\b"),
    ],
    "tools": [
        ("Git", r"\bgit\b(?!hub|lab)"),
        ("GitHub", r"\bgithub\b"),
        ("GitLab", r"\bgitlab\b"),
        ("VS Code", r"\bvs\s*code\b|\bvisual\s+studio\s+code\b"),
        ("Jupyter Notebook", r"\bjupyter(?:\s+notebook)?\b"),
        ("Postman", r"\bpostman\b"),
        ("Jira", r"\bjira\b"),
        ("Bitbucket", r"\bbitbucket\b"),
        ("Figma", r"\bfigma\b"),
    ],
    "other": [
        ("Data Structures & Algorithms", r"\bdata\s+structures\s*(?:&|and)\s*algorithms\b|\bdsa\b|\bdata\s+structures\b|\balgorithms\b"),
        ("OOP", r"\boop\b|\bobject-oriented\s+programming\b"),
        ("DBMS", r"\bdbms\b"),
        ("Operating Systems", r"\boperating\s+systems\b"),
        ("SDLC", r"\bsdlc\b"),
        ("Agile", r"\bagile\b|\bscrum\b"),
        ("Debugging", r"\bdebugging\b"),
        ("Web Testing", r"\bweb\s+testing\b"),
        ("Unit Testing", r"\bunit\s+testing\b"),
        ("Problem Solving", r"\bproblem\s+solving\b"),
    ],
}


def resolve_skill_alias(raw_token: str) -> tuple[str, str] | None:
    """
    Map a raw skill string to its canonical name and destination category.
    """
    clean_lower = re.sub(r"[•\-*]", "", raw_token).strip().lower()
    if not clean_lower:
        return None

    # Check direct canonical aliases
    if clean_lower in CANONICAL_ALIASES:
        canonical_name = CANONICAL_ALIASES[clean_lower]
        category = CANONICAL_TO_CATEGORY.get(canonical_name, "other")
        return canonical_name, category

    # Check taxonomy regex patterns
    for cat, skills in SKILL_TAXONOMY.items():
        for canonical_name, pattern in skills:
            if re.fullmatch(pattern, clean_lower, re.IGNORECASE) or re.search(pattern, clean_lower, re.IGNORECASE):
                return canonical_name, cat

    # Preserve clean title-cased token if it appears to be a valid skill
    if 2 <= len(clean_lower) <= 30 and not any(ch in clean_lower for ch in ("•", "*", ":")):
        return raw_token.strip(), "other"

    return None


def parse_technical_skills(
    skills_lines: list[str],
    full_text: str = "",
) -> TechnicalSkills:
    """
    Extract and categorize technical skills from resume text.

    Prioritizes explicit declarations in the Skills section and tech stack headers.
    Resolves aliases, canonicalizes names, and eliminates overlapping duplicates.
    """
    categorized: dict[str, list[str]] = {cat: [] for cat in SKILL_TAXONOMY}

    # 1. Parse explicitly listed items in the skills section
    for line in skills_lines:
        line_clean = line.strip()
        if not line_clean:
            continue

        # Check for "Category: Skill1, Skill2, Skill3" format
        if ":" in line_clean:
            category_label, skills_part = line_clean.split(":", 1)
            cat_lower = category_label.lower()

            raw_tokens = [s.strip() for s in re.split(r"[,|•–—/]", skills_part) if s.strip()]

            # Determine hinted category from the label
            hinted_cat = None
            if "language" in cat_lower or "programming" in cat_lower:
                hinted_cat = "programming_languages"
            elif "frontend" in cat_lower or "web" in cat_lower:
                hinted_cat = "frontend"
            elif "backend" in cat_lower:
                hinted_cat = "backend"
            elif "database" in cat_lower:
                hinted_cat = "databases"
            elif "analytic" in cat_lower or "bi" in cat_lower:
                hinted_cat = "data_analytics"
            elif "machine learning" in cat_lower or "ml" in cat_lower:
                hinted_cat = "machine_learning"
            elif "deep learning" in cat_lower or "ai" in cat_lower:
                hinted_cat = "deep_learning"
            elif "cloud" in cat_lower or "devops" in cat_lower:
                hinted_cat = "cloud_devops"
            elif "tool" in cat_lower:
                hinted_cat = "tools"
            elif "core" in cat_lower or "software engineering" in cat_lower:
                hinted_cat = "other"

            for token in raw_tokens:
                res = resolve_skill_alias(token)
                if res:
                    canon_name, auto_cat = res
                    dest_cat = hinted_cat or auto_cat
                    # Special rule: Supabase is Databases in candidates' resumes
                    if canon_name == "Supabase":
                        dest_cat = "databases"
                    if canon_name not in categorized[dest_cat]:
                        categorized[dest_cat].append(canon_name)
                else:
                    clean_token = token.strip()
                    if clean_token and len(clean_token) <= 30:
                        target = hinted_cat or "other"
                        if clean_token not in categorized[target]:
                            categorized[target].append(clean_token)
        else:
            # Unlabeled lines in skills section (comma-separated or bullet list)
            tokens = [s.strip() for s in re.split(r"[,|•–—/]", line_clean) if s.strip()]
            for token in tokens:
                res = resolve_skill_alias(token)
                if res:
                    canon_name, cat = res
                    if canon_name not in categorized[cat]:
                        categorized[cat].append(canon_name)

    # 2. Extract skills from explicit "Tech Stack:" lines across the document
    for match in re.finditer(r"(?:tech\s*stack|technologies|tools)[\s:]+([^\n]+)", full_text, re.IGNORECASE):
        tech_line = match.group(1)
        tokens = [s.strip() for s in re.split(r"[,|•–—/]", tech_line) if s.strip()]
        for token in tokens:
            res = resolve_skill_alias(token)
            if res:
                canon_name, cat = res
                if canon_name not in categorized[cat]:
                    categorized[cat].append(canon_name)

    # 3. Check for specific unambiguous skills in experience (e.g. operational data analysis)
    if not categorized["data_analytics"] and re.search(r"\b(?:operational\s+)?data\s+analysis\b", full_text, re.I):
        categorized["data_analytics"].append("Data Analytics")

    # 4. Overlap suppression:
    # If "Data Structures & Algorithms" is present, ensure "Data Structures", "Algorithms", "DSA" are suppressed
    if "Data Structures & Algorithms" in categorized["other"]:
        categorized["other"] = [
            s for s in categorized["other"]
            if s not in ("Data Structures", "Algorithms", "DSA")
        ]

    # Suppress generic Regression if classification was not in ML section
    # (keeps regression only if explicitly in ML or accompanied by regression models)
    if "Regression" in categorized["machine_learning"] and not any(
        re.search(r"\bmachine\s+learning\b|\bml\b|\bregression\s+model\b|\blogistic\s+regression\b", l, re.I)
        for l in skills_lines
    ):
        categorized["machine_learning"].remove("Regression")

    return TechnicalSkills(
        programming_languages=categorized["programming_languages"],
        frontend=categorized["frontend"],
        backend=categorized["backend"],
        databases=categorized["databases"],
        data_analytics=categorized["data_analytics"],
        machine_learning=categorized["machine_learning"],
        deep_learning=categorized["deep_learning"],
        cloud_devops=categorized["cloud_devops"],
        tools=categorized["tools"],
        other=categorized["other"],
    )
