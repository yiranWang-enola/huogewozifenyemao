# assessment/algorithms/game_engine.py
# 作者：俞天骜
# 版本：v1.1 优化版（AHP成对比较法）
# 功能：高考专业报名指导博弈引擎
# 接口兼容：与团队所有模块100%兼容

import json
import os
from typing import Dict, List, Optional

# 依赖安装：pip install numpy
import numpy as np

# ============================
# 全局配置（不要修改）
# ============================
# AHP一致性检验参考值（萨蒂标准RI表）
RI_TABLE = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45}
# 霍兰德维度固定顺序（与TOPSIS算法严格对应）
DIMENSIONS = ["R", "I", "A", "S", "E", "C"]
# 题库文件名（你的文件名）
QUESTION_FILE = "game_question.json"

# ============================
# 加载题库
# ============================
def load_questions() -> List[Dict]:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, QUESTION_FILE)
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            questions = json.load(f)
            print(f"✅ 博弈引擎初始化成功，加载 {len(questions)} 个问题")
            return questions
    except FileNotFoundError:
        print(f"❌ 错误：未找到题库文件 {json_path}")
        return []
    except json.JSONDecodeError:
        print(f"❌ 错误：{QUESTION_FILE} 格式不正确，请检查逗号和引号")
        return []

GAME_QUESTIONS = load_questions()

# ============================
# 博弈引擎核心类
# ============================
class GameEngine:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.current_index = 0
        self.answers: List[Dict] = []
        
    def get_next_question(self) -> Optional[Dict]:
        """获取下一个问题，返回None表示答题结束"""
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
        """提交用户答案，返回是否成功"""
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
    
    def calculate_weights(self) -> Dict[str, float]:
        """
        AHP层次分析法计算最终权重
        返回格式：{"R": 0.15, "I": 0.20, ...} 与TOPSIS完全兼容
        """
        n = len(DIMENSIONS)
        # 初始化成对比较矩阵（对角线为1）
        matrix = np.ones((n, n))
        
        # 填充矩阵
        for ans in self.answers:
            contrib = ans["weight_contribution"]
            dims = list(contrib.keys())
            i = DIMENSIONS.index(dims[0])
            j = DIMENSIONS.index(dims[1])
            matrix[i][j] = contrib[dims[0]]
            matrix[j][i] = contrib[dims[1]]
        
        # 计算最大特征值和特征向量
        eig_vals, eig_vecs = np.linalg.eig(matrix)
        max_idx = np.argmax(np.real(eig_vals))
        lambda_max = np.real(eig_vals[max_idx])
        weights = np.real(eig_vecs[:, max_idx])
        
        # 归一化
        weights = weights / np.sum(weights)
        
        # 一致性检验
        ci = (lambda_max - n) / (n - 1) if n > 1 else 0.0
        ri = RI_TABLE.get(n, 1.49)
        cr = ci / ri if ri != 0 else 0.0
        
        # 一致性不通过时，使用加权平均法降级（比平均权重更准确）
        if cr >= 0.1:
            print(f"⚠️ 一致性检验CR={cr:.3f}，使用加权平均法计算")
            return self._fallback_weights()
        
        # 保留4位小数，返回字典
        return {DIMENSIONS[i]: round(weights[i], 4) for i in range(n)}
    
    def _fallback_weights(self) -> Dict[str, float]:
        """降级方案：加权平均法（无依赖，结果稳定）"""
        scores = {d: 0 for d in DIMENSIONS}
        for ans in self.answers:
            contrib = ans["weight_contribution"]
            for d, v in contrib.items():
                scores[d] += v
        
        total = sum(scores.values()) or len(DIMENSIONS)
        return {d: round(s / total, 4) for d, s in scores.items()}
    
    def get_dialogue_log(self) -> List[Dict]:
        """获取对话日志，用于数据库存储（与钟鑫平模块对接）"""
        return self.answers

