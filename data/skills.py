from typing import Dict, List

from constants import SKILL_LEVELS, SKILLS
from enums import SkillEnum


class Skill:
    skill_type: SkillEnum
    level: int

    def __init__(self, skill_type: SkillEnum, level: int):
        self.skill_type = skill_type
        self.level = level

    @staticmethod
    def from_dict(source: Dict):
        skills = source.get(SKILLS, [])
        levels = source.get(SKILL_LEVELS, [])
        if len(skills) != len(levels):
            raise ValueError("Skills and skill levels have to have the same length")
        retval: List[Skill] = []
        for i in range(len(skills)):
            retval.append(Skill(skill_type=SkillEnum(skills[i]), level=levels[i]))
        return retval
