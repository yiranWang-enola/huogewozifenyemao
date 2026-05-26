from django.db import models
import json
import uuid


class UserProfile(models.Model):
    session_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    gaokao_score = models.IntegerField(null=True, blank=True)
    province = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    school = models.CharField(max_length=100, blank=True)
    selected_subjects = models.CharField(max_length=200, blank=True, help_text="如: 物理+化学+地理")
    interests = models.TextField(blank=True, help_text="兴趣关键词，逗号分隔")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"UserProfile({self.session_id})"


class AssessmentResult(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='assessment')
    holland_code = models.CharField(max_length=10, blank=True, help_text="如: IEC")
    holland_scores = models.JSONField(default=dict, help_text="{R: 5, I: 8, ...}")
    mbti_type = models.CharField(max_length=10, blank=True, help_text="如: INTJ")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Assessment({self.user.session_id}): {self.holland_code}-{self.mbti_type}"


class RecommendationResult(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='recommendations')
    assessment = models.ForeignKey(AssessmentResult, on_delete=models.CASCADE)
    recommendations = models.JSONField(default=list, help_text="[{major_id, name, score, rank}, ...]")
    weights = models.JSONField(default=dict, help_text="TOPSIS权重配置")
    version = models.IntegerField(default=0, help_text="版本号：0=初始，1,2...=对话调整后")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'version')

    def __str__(self):
        return f"Recommendation({self.user.session_id})-v{self.version}"


class DialogueLog(models.Model):
    recommendation = models.ForeignKey(RecommendationResult, on_delete=models.CASCADE, related_name='dialogues')
    user_input = models.TextField()
    system_intent = models.CharField(max_length=100, blank=True, help_text="解析的意图")
    extracted_entities = models.JSONField(default=dict, help_text="提取的实体")
    weights_adjusted = models.JSONField(default=dict, help_text="调整后的权重")
    new_recommendations = models.JSONField(default=list, help_text="新的推荐列表")
    system_response = models.TextField(blank=True, help_text="系统回复")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dialogue({self.recommendation.user.session_id})-{self.timestamp}"
