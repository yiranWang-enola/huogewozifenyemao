import numpy as np
from scipy.spatial.distance import euclidean


class TOPSIS:
    """TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)"""

    def __init__(self, weights=None):
        self.weights = weights or {
            'personality_fit': 0.25,
            'interest_match': 0.25,
            'gaokao_fit': 0.20,
            'employment_rate': 0.15,
            'salary_level': 0.15
        }

    def rank_majors(self, majors, criteria_matrix):
        """
        Args:
            majors: 专业列表 [{id, name, ...}, ...]
            criteria_matrix: (M x N) numpy数组，M个专业，N个指标
                            指标顺序必须与weights键顺序一致

        Returns:
            ranked_majors: 排序后的专业列表，包含TOPSIS得分和排名
        """
        if len(majors) == 0:
            return []

        # 接受 list 或 numpy 数组，确保为 numpy ndarray
        criteria_matrix = np.array(criteria_matrix, dtype=float)
        if criteria_matrix.ndim == 1:
            # 单行情况，转换为二维
            criteria_matrix = criteria_matrix.reshape(1, -1)
        M, N = criteria_matrix.shape

        # 1. 标准化矩阵
        normalized = self._normalize_matrix(criteria_matrix)

        # 2. 加权标准化矩阵
        weight_list = list(self.weights.values())
        weighted = normalized * np.array(weight_list)

        # 3. 确定理想解和负理想解
        ideal_best = np.max(weighted, axis=0)  # 每个指标的最大值
        ideal_worst = np.min(weighted, axis=0)  # 每个指标的最小值

        # 4. 计算欧式距离
        distances_to_best = np.array([euclidean(weighted[i], ideal_best) for i in range(M)])
        distances_to_worst = np.array([euclidean(weighted[i], ideal_worst) for i in range(M)])

        # 5. 计算相对接近度
        topsis_scores = distances_to_worst / (distances_to_best + distances_to_worst + 1e-10)

        # 6. 排序
        ranked_indices = np.argsort(-topsis_scores)  # 降序排列

        # 7. 构建结果
        result = []
        for rank, idx in enumerate(ranked_indices, 1):
            major = majors[idx].copy() if isinstance(majors[idx], dict) else majors[idx].__dict__
            major['topsis_score'] = float(topsis_scores[idx])
            major['rank'] = rank
            result.append(major)

        return result

    def _normalize_matrix(self, matrix):
        """向量归一化：每列除以该列的平方和的开方"""
        col_sums = np.sqrt(np.sum(matrix ** 2, axis=0))
        col_sums[col_sums == 0] = 1  # 避免除以零
        return matrix / col_sums

    def update_weights(self, weight_adjustments):
        """动态调整权重"""
        for key, adjustment in weight_adjustments.items():
            if key in self.weights:
                self.weights[key] = max(0, self.weights[key] + adjustment)

        # 重新归一化权重使其和为1
        total = sum(self.weights.values())
        for key in self.weights:
            self.weights[key] /= total

        return self.weights


def get_initial_weights(holland_code, mbti, gaokao_score, province,
                        selected_subjects, chinese_score, math_score,
                        physics_score, history_score):
        # 修复：将列表转为字符串
    if isinstance(holland_code, list):
        holland_code = ''.join(holland_code)
    if isinstance(mbti, list):
        mbti = ''.join(mbti)
    """
    根据用户特征动态调整初始权重
    新增：选科组合、语文/数学/物理/历史 单科分数 影响权重
    """
    weights = {
        'personality_fit': 0.25,
        'interest_match': 0.25,
        'gaokao_fit': 0.20,
        'employment_rate': 0.15,
        'salary_level': 0.15
    }

    # ========== 1. 霍兰德类型 原有逻辑 ==========
    # 研究型学生更看重性格和兴趣匹配
    if 'I' in holland_code:
        weights['personality_fit'] = 0.30
        weights['interest_match'] = 0.30
        weights['gaokao_fit'] = 0.15
        weights['employment_rate'] = 0.125
        weights['salary_level'] = 0.125

    # 企业型学生更看重薪资
    if 'E' in holland_code:
        weights['salary_level'] = 0.25
        weights['employment_rate'] = 0.20
        weights['personality_fit'] = 0.20
        weights['gaokao_fit'] = 0.15
        weights['interest_match'] = 0.20

    # ========== 2. 高考总分 原有逻辑 ==========
    # 低分考生更关注分数适配度
    if gaokao_score and gaokao_score < 350:
        weights['gaokao_fit'] = 0.35
        weights['personality_fit'] = 0.20
        weights['interest_match'] = 0.20
        weights['employment_rate'] = 0.125
        weights['salary_level'] = 0.125

    # 高分考生更关注兴趣和性格
    elif gaokao_score and gaokao_score > 600:
        weights['personality_fit'] = 0.30
        weights['interest_match'] = 0.30
        weights['gaokao_fit'] = 0.15
        weights['employment_rate'] = 0.125
        weights['salary_level'] = 0.125

    # ========== 3. 新增：选科组合 区分逻辑 ==========
    physics_group = ["物化生", "物化政", "物化地"]
    history_group = ["历政地", "历政生"]

    # 物理类选科：强化分数适配权重（理工科对分数要求高）
    if selected_subjects in physics_group:
        weights['gaokao_fit'] += 0.08
        weights['employment_rate'] += 0.05
    # 历史类选科：强化性格、兴趣匹配（文综类更看重个人特质）
    elif selected_subjects in history_group:
        weights['personality_fit'] += 0.08
        weights['interest_match'] += 0.05

    # ========== 4. 新增：单科分数 微调权重 ==========
    # 语文、数学通用判断
    total_single = 0
    if chinese_score:
        total_single += chinese_score
    if math_score:
        total_single += math_score

    # 单科整体偏低，进一步提高分数适配权重
    if total_single > 0 and total_single < 180:
        weights['gaokao_fit'] += 0.07
    # 单科整体优秀，偏向兴趣/性格
    elif total_single > 0 and total_single > 240:
        weights['personality_fit'] += 0.06
        weights['interest_match'] += 0.04

    # 物理单科低分：降低理工科专业倾向（分数权重拉高）
    if physics_score and physics_score < 60:
        weights['gaokao_fit'] += 0.06
    # 历史单科低分：降低文史类专业倾向
    if history_score and history_score < 60:
        weights['gaokao_fit'] += 0.06

    # ========== 权重归一化：保证总和始终为1 ==========
    total_w = sum(weights.values())
    for k in weights:
        weights[k] = round(weights[k] / total_w, 4)

    return weights