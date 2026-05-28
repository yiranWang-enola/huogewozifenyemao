import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SemanticMatcher:
    """词向量和余弦相似度匹配"""

    def __init__(self, majors_data):
        """
        Args:
            majors_data: 专业数据列表 [{id, name, keywords, ...}, ...]
        """
        self.majors = majors_data
        self.vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 3))

        # 构建专业文档（keywords + name）
        self.major_docs = [
            f"{m['name']} {' '.join(m.get('keywords', []))}"
            for m in majors_data
        ]

        # 构建TF-IDF矩阵
        self.major_vectors = self.vectorizer.fit_transform(self.major_docs)

    def match_interests_to_majors(self, user_interests, top_k=20):
        """
        匹配用户兴趣到专业

        Args:
            user_interests: 用户兴趣关键词字符串（逗号分隔或空格分隔）
            top_k: 返回Top K匹配的专业

        Returns:
            matched_majors: [{major_id, name, similarity_score}, ...]
        """
        if not user_interests or user_interests.strip() == '':
            return []

        # 构建用户兴趣向量
        user_interests_doc = user_interests
        user_vector = self.vectorizer.transform([user_interests_doc])

        # 计算余弦相似度
        similarities = cosine_similarity(user_vector, self.major_vectors)[0]

        # 获取Top K
        top_indices = np.argsort(-similarities)[:top_k]

        matched = []
        for idx in top_indices:
            if similarities[idx] > 0:  # 只返回相似度 > 0 的
                matched.append({
                    'major_id': self.majors[idx]['id'],
                    'name': self.majors[idx]['name'],
                    'similarity_score': float(similarities[idx]),
                    'keywords': self.majors[idx].get('keywords', [])
                })

        return matched

    def match_school_to_majors(self, school_name, top_k=15):
        """
        根据学校和地区匹配专业（优先级权重）

        Args:
            school_name: 学校名称
            top_k: 返回专业数

        Returns:
            matched_majors: 按热度排序的专业
        """
        # 简化版本：返回高需求专业
        demand_majors = [
            m for m in self.majors
            if m.get('employment_rate', 0) > 0.85 or m.get('salary_level') == '高'
        ]
        return sorted(demand_majors, key=lambda x: x.get('employment_rate', 0), reverse=True)[:top_k]

    def get_major_by_id(self, major_id):
        """根据ID获取专业信息"""
        for major in self.majors:
            if major['id'] == major_id:
                return major
        return None

    def filter_by_criteria(self, criteria):
        """
        按条件过滤专业

        Args:
            criteria: {
                'categories': ['工学', '理学', ...],
                'fields': ['信息技术', ...],
                'min_employment_rate': 0.8,
                'salary_levels': ['高', '中高'],
                'excluded_majors': [...]
            }

        Returns:
            filtered_majors: 符合条件的专业
        """
        filtered = self.majors.copy()

        if 'categories' in criteria and criteria['categories']:
            filtered = [m for m in filtered if m.get('category') in criteria['categories']]

        if 'fields' in criteria and criteria['fields']:
            filtered = [m for m in filtered if m.get('field') in criteria['fields']]

        if 'min_employment_rate' in criteria:
            min_rate = criteria['min_employment_rate']
            filtered = [m for m in filtered if m.get('employment_rate', 0) >= min_rate]

        if 'salary_levels' in criteria and criteria['salary_levels']:
            filtered = [m for m in filtered if m.get('salary_level') in criteria['salary_levels']]

        if 'excluded_majors' in criteria:
            excluded_ids = criteria['excluded_majors']
            filtered = [m for m in filtered if m['id'] not in excluded_ids]

        return filtered
