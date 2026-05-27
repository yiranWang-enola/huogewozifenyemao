from .models import UserProfile, AssessmentResult, RecommendationResult, DialogueLog

# ========== 用户相关 ==========

def create_user(session_id, **kwargs):
    """创建新用户"""
    user, created = UserProfile.objects.get_or_create(
        session_id=session_id,
        defaults=kwargs
    )
    return user

def get_user(session_id):
    """根据 session_id 获取用户"""
    try:
        return UserProfile.objects.get(session_id=session_id)
    except UserProfile.DoesNotExist:
        return None

def update_user(session_id, **kwargs):
    """更新用户信息"""
    user = get_user(session_id)
    if user:
        for key, value in kwargs.items():
            setattr(user, key, value)
        user.save()
    return user

# ========== 测评结果相关 ==========

def save_assessment(session_id, holland_code, holland_scores, mbti_type):
    """保存测评结果"""
    user = get_user(session_id)
    if not user:
        return None
    result, created = AssessmentResult.objects.update_or_create(
        user=user,
        defaults={
            'holland_code': holland_code,
            'holland_scores': holland_scores,
            'mbti_type': mbti_type,
        }
    )
    return result

def get_assessment(session_id):
    """获取用户的测评结果"""
    user = get_user(session_id)
    if user:
        try:
            return AssessmentResult.objects.get(user=user)
        except AssessmentResult.DoesNotExist:
            return None
    return None

# ========== 推荐结果相关 ==========

def save_recommendation(session_id, assessment_id, recommendations, weights, version=0):
    """保存推荐结果"""
    user = get_user(session_id)
    if not user:
        return None
    assessment = AssessmentResult.objects.get(id=assessment_id)
    rec, created = RecommendationResult.objects.update_or_create(
        user=user,
        version=version,
        defaults={
            'assessment': assessment,
            'recommendations': recommendations,
            'weights': weights,
        }
    )
    return rec

def get_latest_recommendation(session_id):
    """获取用户最新的推荐结果"""
    user = get_user(session_id)
    if user:
        return RecommendationResult.objects.filter(user=user).order_by('-version').first()
    return None

# ========== 对话日志相关 ==========

def save_dialogue(recommendation_id, user_input, system_intent, extracted_entities,
                  weights_adjusted, new_recommendations, system_response):
    """保存对话记录"""
    recommendation = RecommendationResult.objects.get(id=recommendation_id)
    dialogue = DialogueLog.objects.create(
        recommendation=recommendation,
        user_input=user_input,
        system_intent=system_intent,
        extracted_entities=extracted_entities,
        weights_adjusted=weights_adjusted,
        new_recommendations=new_recommendations,
        system_response=system_response,
    )
    return dialogue

def get_user_dialogues(session_id):
    """获取用户的所有对话记录"""
    user = get_user(session_id)
    if user:
        return DialogueLog.objects.filter(recommendation__user=user).order_by('timestamp')
    return []