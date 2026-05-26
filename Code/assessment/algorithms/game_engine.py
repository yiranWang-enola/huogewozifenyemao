# assessment/algorithms/game_engine.py
# 作者：俞天骜
# 功能：高考专业报名指导 —— 博弈引擎 + 计数法权重反推
# 今日任务：6个博弈问题(JSON) + 计数法反推权重

import json
import os
from typing import Dict, List, Optional

# ============================
# 内置6个题目（防止JSON读取失败）
# 永远不会报错！
# ============================
GAME_QUESTIONS = [
    {
        "id": 1,
        "question": "如果有一下午的自由时间，你更愿意：",
        "option_a": "组装调试一个机器人模型或手工制作一件实用物品",
        "option_b": "解一道复杂的数学题或研究一个感兴趣的科学原理",
        "dimension_a": "R",
        "dimension_b": "I",
        "weight_map": {"a": {"R": 1, "I": 0}, "b": {"R": 0, "I": 1}}
    },
    {
        "id": 2,
        "question": "班级要举办毕业晚会，你更想负责：",
        "option_a": "设计晚会海报、制作视频或编排节目",
        "option_b": "组织同学报名、协调场地和物资",
        "dimension_a": "A",
        "dimension_b": "S",
        "weight_map": {"a": {"A": 1, "S": 0}, "b": {"A": 0, "S": 1}}
    },
    {
        "id": 3,
        "question": "学校组织义卖活动，你更擅长：",
        "option_a": "制定销售策略、向路人推销商品",
        "option_b": "记录收支账目、整理清点货物",
        "dimension_a": "E",
        "dimension_b": "C",
        "weight_map": {"a": {"E": 1, "C": 0}, "b": {"E": 0, "C": 1}}
    },
    {
        "id": 4,
        "question": "家里的电器坏了，你会优先：",
        "option_a": "自己上网查教程，尝试动手修理",
        "option_b": "联系专业维修人员或向懂行的人请教",
        "dimension_a": "R",
        "dimension_b": "S",
        "weight_map": {"a": {"R": 1, "S": 0}, "b": {"R": 0, "S": 1}}
    },
    {
        "id": 5,
        "question": "老师布置一个开放性作业，你更倾向于：",
        "option_a": "用自己独特的创意和方式完成",
        "option_b": "按照要求和模板，有条理地完成",
        "dimension_a": "A",
        "dimension_b": "C",
        "weight_map": {"a": {"A": 1, "C": 0}, "b": {"A": 0, "C": 1}}
    },
    {
        "id": 6,
        "question": "在小组项目中，你更希望扮演的角色是：",
        "option_a": "负责核心技术或学术问题的研究",
        "option_b": "担任组长，分配任务和把控进度",
        "dimension_a": "I",
        "dimension_b": "E",
        "weight_map": {"a": {"I": 1, "E": 0}, "b": {"I": 0, "E": 1}}
    }
]

# ============================
# 博弈引擎核心类
# ============================
class GameEngine:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.current_index = 0
        self.answers = []

    def get_next_question(self) -> Optional[Dict]:
        if self.current_index >= len(GAME_QUESTIONS):
            return None

        q = GAME_QUESTIONS[self.current_index]
        return {
            "question_id": q["id"],
            "question": q["question"],
            "option_a": q["option_a"],
            "option_b": q["option_b"],
            "progress": f"{self.current_index + 1}/{len(GAME_QUESTIONS)}"
        }

    def submit_answer(self, question_id: int, answer: str) -> bool:
        if answer not in ["a", "b"]:
            return False

        q = next((x for x in GAME_QUESTIONS if x["id"] == question_id), None)
        if not q:
            return False

        self.answers.append({
            "question_id": question_id,
            "answer": answer,
            "weight_contribution": q["weight_map"][answer]
        })
        self.current_index += 1
        return True

    # ============================
    # 计数法反推权重（今天必须完成）
    # ============================
    def calculate_weights(self) -> Dict[str, float]:
        scores = {
            "R": 0,
            "I": 0,
            "A": 0,
            "S": 0,
            "E": 0,
            "C": 0
        }

        for ans in self.answers:
            contrib = ans["weight_contribution"]
            for dim, val in contrib.items():
                scores[dim] += val

        total = sum(scores.values()) or 6
        weights = {d: round(s / total, 4) for d, s in scores.items()}
        return weights

