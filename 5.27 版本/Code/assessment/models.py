from django.db import models
import json
import uuid


class UserProfile(models.Model):
    session_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4) #用户唯一标识
    gaokao_score = models.IntegerField(null=True, blank=True) #高考分数
    province = models.CharField(max_length=50, blank=True) #省份
     # 在你的用户模型里追加这三行
    chinese_score = models.IntegerField(null=True, blank=True)
    math_score = models.IntegerField(null=True, blank=True)
    physics_score = models.IntegerField(null=True, blank=True)
    history_score = models.IntegerField(null=True, blank=True)
    city = models.CharField(max_length=50, blank=True)  #城市
    school = models.CharField(max_length=100, blank=True)  #学校
    selected_subjects = models.CharField(max_length=200, blank=True, help_text="如: 物理+化学+地理")  #选考科目
    interests = models.TextField(blank=True, help_text="兴趣关键词，逗号分隔")  #兴趣关键词
    created_at = models.DateTimeField(auto_now_add=True) #创建时间
    updated_at = models.DateTimeField(auto_now=True) #更新时间

    def __str__(self):
        return f"UserProfile({self.session_id})" #返回用户唯一标识


class AssessmentResult(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='assessment') #一对一关联，一个用户对应一个评估结果
    holland_code = models.CharField(max_length=10, blank=True, help_text="如: IEC") #霍兰德代码
    holland_scores = models.JSONField(default=dict, help_text="{R: 5, I: 8, ...}") #霍兰德代码对应的分数
    mbti_type = models.CharField(max_length=10, blank=True, help_text="如: INTJ") #MBTI类型
    created_at = models.DateTimeField(auto_now_add=True) #创建时间
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Assessment({self.user.session_id}): {self.holland_code}-{self.mbti_type}" #返回用户唯一标识和霍兰德代码、MBTI类型


class RecommendationResult(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='recommendations') #多对一关联，一个用户对应多个推荐结果
    assessment = models.ForeignKey(AssessmentResult, on_delete=models.CASCADE) #多对一关联，一个评估结果对应多个推荐结果
    recommendations = models.JSONField(default=list, help_text="[{major_id, name, score, rank}, ...]") #推荐列表
    weights = models.JSONField(default=dict, help_text="TOPSIS权重配置") #TOPSIS权重配置
    version = models.IntegerField(default=0, help_text="版本号：0=初始，1,2...=对话调整后") #版本号：0=初始，1,2...=对话调整后
    created_at = models.DateTimeField(auto_now_add=True) #创建时间

    class Meta:
        unique_together = ('user', 'version') #一个用户对应一个版本

    def __str__(self):
        return f"Recommendation({self.user.session_id})-v{self.version}" #返回用户唯一标识和版本号


class DialogueLog(models.Model):
    recommendation = models.ForeignKey(RecommendationResult, on_delete=models.CASCADE, related_name='dialogues') #多对一关联，一个推荐结果对应多个对话记录
    user_input = models.TextField() #用户输入
    system_intent = models.CharField(max_length=100, blank=True, help_text="解析的意图") #解析的意图
    extracted_entities = models.JSONField(default=dict, help_text="提取的实体") #提取的实体
    weights_adjusted = models.JSONField(default=dict, help_text="调整后的权重") #调整后的权重
    new_recommendations = models.JSONField(default=list, help_text="新的推荐列表") #新的推荐列表
    system_response = models.TextField(blank=True, help_text="系统回复") #系统回复
    timestamp = models.DateTimeField(auto_now_add=True) #记录时间

    def __str__(self):
        return f"Dialogue({self.recommendation.user.session_id})-{self.timestamp}" #返回用户唯一标识和记录时间
