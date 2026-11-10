import sys
sys.path.insert(0, ".")
from database.session import engine
from sqlalchemy import text

tables = [
    "career_profiles",
    "resume_records",
    "resume_profiles",
    "skill_gap_reports",
    "learning_roadmaps",
    "roadmap_skills",
    "roadmap_topics",
    "learning_resources",
    "roadmap_milestones",
    "learning_preferences",
]

with engine.connect() as conn:
    print("Database Table Row Counts in careermind.db:")
    for tbl in tables:
        count = conn.execute(text(f"SELECT COUNT(1) FROM {tbl}")).scalar()
        print(f"  - {tbl}: {count}")
