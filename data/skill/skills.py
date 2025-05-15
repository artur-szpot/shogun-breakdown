from typing import Dict, Optional

from constants import SKILL_LEVELS, SKILLS
from data.skill.skill_enums import SkillEnum


class Skills:
    skills: Dict[SkillEnum, int]

    def __init__(self, skills: Dict[SkillEnum, int] = None):
        self.skills = skills or {}

    @staticmethod
    def from_dict(source: Dict):
        skills = source.get(SKILLS, [])
        levels = source.get(SKILL_LEVELS, [])
        if len(skills) != len(levels):
            raise ValueError("Skills and skill levels have to have the same length")
        retval: Dict[SkillEnum, int] = {}
        for i in range(len(skills)):
            retval[SkillEnum(skills[i])] = levels[i]
        return Skills(retval)

    def to_dict_skills(self):
        return [s.value for s in self.skills.keys()]

    def to_dict_levels(self):
        return [s for s in self.skills.values()]

    def has_skill(self, skill: SkillEnum) -> bool:
        return self.skills.get(skill) is not None

    def skill_level(self, skill: SkillEnum) -> Optional[int]:
        return self.skills.get(skill)
