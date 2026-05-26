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

#添加的方法

def get_topsis_weights(self, gaokao_score: int = None) -> dict:
    """
    将 AHP 计算的 RIASEC 权重转换为 TOPSIS 算法所需的 5 个指标权重
    
    Args:
        gaokao_score: 高考分数，用于动态调整 gaokao_fit 权重
    
    Returns:
        {
            'personality_fit': 0.25,
            'interest_match': 0.25, 
            'gaokao_fit': 0.20,
            'employment_rate': 0.15,
            'salary_level': 0.15
        }
    """
    # 1. 获取 RIASEC 权重（AHP 计算的结果）
    riasec = self.calculate_weights()
    
    # 2. 映射规则：RIASEC 六维 → TOPSIS 五维
    # personality_fit（性格匹配）：R(动手) + I(思考) + E(领导) + S(沟通) + C(条理) + A(创意)
    personality_fit = (
        riasec.get('R', 0) * 0.30 +   # 现实型 → 动手能力
        riasec.get('I', 0) * 0.20 +   # 研究型 → 思考能力
        riasec.get('E', 0) * 0.20 +   # 企业型 → 领导力
        riasec.get('S', 0) * 0.15 +   # 社会型 → 沟通能力
        riasec.get('C', 0) * 0.10 +   # 常规型 → 条理性
        riasec.get('A', 0) * 0.05     # 艺术型 → 创造力
    )
    
    # interest_match（兴趣匹配）：I(研究) + A(艺术) + S(社会) + R(现实)
    interest_match = (
        riasec.get('I', 0) * 0.40 +   # 研究型 → 学术兴趣
        riasec.get('A', 0) * 0.30 +   # 艺术型 → 创意兴趣
        riasec.get('S', 0) * 0.20 +   # 社会型 → 人际兴趣
        riasec.get('R', 0) * 0.10     # 现实型 → 动手兴趣
    )
    
    # 3. 基础权重
    weights = {
        'personality_fit': personality_fit,
        'interest_match': interest_match,
        'gaokao_fit': 0.20,
        'employment_rate': 0.15,
        'salary_level': 0.15
    }
    
    # 4. 根据高考分数调整 gaokao_fit
    if gaokao_score:
        if gaokao_score < 350:
            weights['gaokao_fit'] = 0.35   # 低分考生更关心能不能考上
        elif gaokao_score > 600:
            weights['gaokao_fit'] = 0.12   # 高分考生不太担心分数
    
    # 5. 根据霍兰德首码调整（从 RIASEC 中取最高分维度）
    top_dimension = max(riasec, key=riasec.get)
    if top_dimension == 'I':  # 研究型
        weights['personality_fit'] *= 1.15
        weights['interest_match'] *= 1.15
        weights['salary_level'] *= 0.90
    elif top_dimension == 'E':  # 企业型
        weights['salary_level'] *= 1.20
        weights['employment_rate'] *= 1.10
        weights['personality_fit'] *= 0.90
    
    # 6. 归一化，使总和为 1
    total = sum(weights.values())
    for k in weights:
        weights[k] = round(weights[k] / total, 4)
    
    return weights


def apply_feedback(self, feedback_key: str, gaokao_score: int = None) -> dict:
    """
    用户点击调整按钮后，重新计算权重
    
    Args:
        feedback_key: 调整选项，可选值：'more_money', 'more_stable', 'more_interest', 'score_worry'
        gaokao_score: 高考分数
    
    Returns:
        调整后的 TOPSIS 权重
    """
    weights = self.get_topsis_weights(gaokao_score)
    
    # 预定义的调整量
    adjustments = {
        'more_money': {      # 我更看重高薪
            'salary_level': +0.08,
            'interest_match': -0.04
        },
        'more_stable': {     # 我更看重就业稳定
            'employment_rate': +0.10,
            'salary_level': -0.05
        },
        'more_interest': {   # 我更看重兴趣匹配
            'interest_match': +0.08,
            'salary_level': -0.04
        },
        'score_worry': {     # 我的分数可能不够
            'gaokao_fit': +0.10,
            'personality_fit': -0.05
        }
    }
    
    if feedback_key in adjustments:
        for key, delta in adjustments[feedback_key].items():
            if key in weights:
                weights[key] = max(0.05, weights[key] + delta)
    
    # 重新归一化
    total = sum(weights.values())
    for k in weights:
        weights[k] = round(weights[k] / total, 4)
    
    return weights


def get_adjustment_options(self) -> list:
    """获取可用的调整选项（供前端展示按钮）"""
    return [
        {'key': 'more_money', 'label': '💰 我更看重高薪'},
        {'key': 'more_stable', 'label': '🏛️ 我更看重就业稳定'},
        {'key': 'more_interest', 'label': '❤️ 我更看重兴趣匹配'},
        {'key': 'score_worry', 'label': '📝 我的分数可能不够'},
    ]