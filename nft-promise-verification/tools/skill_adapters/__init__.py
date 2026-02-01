"""
Skill 适配器模块

将外部 Skill (如 bird, github, excel) 适配为 SpoonOS BaseTool 接口
"""
from .twitter_skill import TwitterSkillAdapter
from .github_skill import GitHubSkillAdapter
from .excel_skill import ExcelSkillAdapter

__all__ = [
    "TwitterSkillAdapter",
    "GitHubSkillAdapter",
    "ExcelSkillAdapter"
]
