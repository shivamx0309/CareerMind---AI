"""
Learning Priority Engine.
Evaluates candidate skill gaps against role benchmarks to assign deterministic
learning priorities (HIGH, MEDIUM, LOW) and clear educational rationales.
"""

from typing import Dict, List, Set, Tuple
from database.models.skill_gap_report import SkillGapReport
from services.skill_dependency_service import get_skill_prerequisites


class PrioritizedSkillItem:
    """Structured container for a skill prioritized for roadmap learning."""

    def __init__(
        self,
        skill_name: str,
        category: str,
        priority: str,  # 'high', 'medium', 'low'
        importance: str,  # 'required', 'preferred'
        gap_type: str,  # 'missing_required', 'related_required', 'missing_preferred'
        rationale: str,
        prerequisites: List[str],
    ):
        self.skill_name = skill_name
        self.category = category
        self.priority = priority
        self.importance = importance
        self.gap_type = gap_type
        self.rationale = rationale
        self.prerequisites = prerequisites


def prioritize_skills_for_roadmap(
    report: SkillGapReport,
    category_map: Dict[str, str] | None = None,
) -> List[PrioritizedSkillItem]:
    """
    Classify and prioritize skills to learn from a SkillGapReport.

    Priority Rules:
    1. HIGH:
       - Missing required skills (mandatory baseline competencies).
       - Skills that serve as foundational prerequisites for other required skills.
    2. MEDIUM:
       - Related required skills (candidate has cluster familiarity, e.g. Django,
         but needs targeted framework transition to master FastAPI).
       - Foundational dependencies needed for subsequent learning modules.
    3. LOW:
       - Missing preferred skills (valuable bonus capabilities for secondary upskilling).
       - Related preferred skills.

    Exclusion Rule:
    - Exact and alias matches already in candidate's profile are NOT recommended as missing.

    Parameters:
        report: SkillGapReport instance containing parsed gap analysis data.
        category_map: Optional mapping of skill_name -> category.

    Returns:
        List of PrioritizedSkillItem instances.
    """
    cat_lookup = category_map or {}

    # Extract skill lists from report
    missing_req = set(report.missing_required_skills or [])
    missing_pref = set(report.missing_preferred_skills or [])

    # Extract related skills and their original importances
    related_skills_list = report.related_skills or []
    related_req = {
        item["skill_name"]: item
        for item in related_skills_list
        if item.get("importance") == "required"
    }
    related_pref = {
        item["skill_name"]: item
        for item in related_skills_list
        if item.get("importance") == "preferred"
    }

    # Helper to resolve category
    def find_category(skill: str) -> str:
        if skill in cat_lookup:
            return cat_lookup[skill]
        for item in (report.matched_skills or []) + related_skills_list:
            if item.get("skill_name") == skill:
                return item.get("category", "other")
        return "other"

    # Identify prerequisite dependencies among missing required skills
    # Skills that unblock other required skills have elevated pedagogical value
    prereqs_of_required: Set[str] = set()
    for s in missing_req:
        for p in get_skill_prerequisites(s):
            prereqs_of_required.add(p)

    prioritized_items: List[PrioritizedSkillItem] = []

    # 1. Process Missing Required Skills -> HIGH Priority
    for skill in missing_req:
        prereqs = get_skill_prerequisites(skill)
        cat = find_category(skill)

        if skill in prereqs_of_required:
            rationale = (
                f"Mandatory baseline core skill for {report.role_title}. "
                f"Also serves as a foundational prerequisite for other required competencies."
            )
        else:
            rationale = (
                f"Mandatory baseline core skill required for {report.role_title}. "
                f"Directly addresses a critical competency gap."
            )

        prioritized_items.append(
            PrioritizedSkillItem(
                skill_name=skill,
                category=cat,
                priority="high",
                importance="required",
                gap_type="missing_required",
                rationale=rationale,
                prerequisites=prereqs,
            )
        )

    # 2. Process Related Required Skills -> MEDIUM Priority
    for skill, item in related_req.items():
        prereqs = get_skill_prerequisites(skill)
        cat = item.get("category", find_category(skill))
        evidenced = item.get("matched_skill", "similar technologies")

        rationale = (
            f"Required benchmark skill. You demonstrated relevant transferable knowledge in {evidenced} "
            f"(earning 60% partial credit). Targeted bridge learning will achieve complete production mastery."
        )

        prioritized_items.append(
            PrioritizedSkillItem(
                skill_name=skill,
                category=cat,
                priority="medium",
                importance="required",
                gap_type="related_required",
                rationale=rationale,
                prerequisites=prereqs,
            )
        )

    # 3. Process Missing Preferred Skills -> LOW Priority
    for skill in missing_pref:
        prereqs = get_skill_prerequisites(skill)
        cat = find_category(skill)

        rationale = (
            f"High-value preferred skill for {report.role_title}. "
            f"Provides competitive advantage and architectural depth for advanced project execution."
        )

        prioritized_items.append(
            PrioritizedSkillItem(
                skill_name=skill,
                category=cat,
                priority="low",
                importance="preferred",
                gap_type="missing_preferred",
                rationale=rationale,
                prerequisites=prereqs,
            )
        )

    # 4. Process Related Preferred Skills -> LOW Priority
    for skill, item in related_pref.items():
        prereqs = get_skill_prerequisites(skill)
        cat = item.get("category", find_category(skill))
        evidenced = item.get("matched_skill", "similar technologies")

        rationale = (
            f"Preferred skill with transferable foundations in {evidenced}. "
            f"Recommended for optional secondary upskilling."
        )

        prioritized_items.append(
            PrioritizedSkillItem(
                skill_name=skill,
                category=cat,
                priority="low",
                importance="preferred",
                gap_type="missing_preferred",
                rationale=rationale,
                prerequisites=prereqs,
            )
        )

    return prioritized_items

