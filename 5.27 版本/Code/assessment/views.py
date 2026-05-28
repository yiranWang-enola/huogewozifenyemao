from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
import json
import os
import logging
import re

# 简单配置日志，输出到控制台
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== 静态数据（保留原有） ====================

HOLLAND_QUESTIONS = [
    {'id': 1, 'type': 'R', 'text': '我喜欢动手修理或制作东西'},
    {'id': 2, 'type': 'I', 'text': '我喜欢解决数学或逻辑难题'},
    {'id': 3, 'type': 'A', 'text': '我对音乐、色彩和美丽事物敏感'},
    {'id': 4, 'type': 'S', 'text': '我喜欢帮助朋友解决他们的困难'},
    {'id': 5, 'type': 'E', 'text': '我喜欢在团队中担任领导角色'},
    {'id': 6, 'type': 'C', 'text': '我做事注重细节和准确性'},
    {'id': 7, 'type': 'R', 'text': '我喜欢户外活动和体育运动'},
    {'id': 8, 'type': 'I', 'text': '我对科学实验和探索真相感兴趣'},
    {'id': 9, 'type': 'A', 'text': '我经常有新的创意和想法'},
    {'id': 10, 'type': 'S', 'text': '我享受教别人学习新东西'},
    {'id': 11, 'type': 'E', 'text': '我享受说服别人接受我的观点'},
    {'id': 12, 'type': 'C', 'text': '我喜欢按规则和流程做事'},
    {'id': 13, 'type': 'R', 'text': '我不在乎工作把手弄脏'},
    {'id': 14, 'type': 'I', 'text': '我喜欢花时间想通事情的道理'},
    {'id': 15, 'type': 'A', 'text': '我喜欢尝试创新的颜色和款式'},
    {'id': 16, 'type': 'S', 'text': '亲密的人际关系对我很重要'},
    {'id': 17, 'type': 'E', 'text': '升迁和进步对我极重要'},
    {'id': 18, 'type': 'C', 'text': '当我把每日工作计划好时更有安全感'},
    {'id': 19, 'type': 'R', 'text': '我喜欢独立完成一项具体任务'},
    {'id': 20, 'type': 'I', 'text': '我会不断思索一个问题直到找到答案'},
    {'id': 21, 'type': 'A', 'text': '我喜欢重新布置我的环境使之与众不同'},
    {'id': 22, 'type': 'S', 'text': '我对别人的困难乐于伸出援手'},
    {'id': 23, 'type': 'E', 'text': '能影响别人使我感到兴奋'},
    {'id': 24, 'type': 'C', 'text': '我花钱时小心翼翼'},
    {'id': 25, 'type': 'R', 'text': '我喜欢把东西拆开看看能否修理'},
    {'id': 26, 'type': 'I', 'text': '我喜欢研读所有事实再有逻辑地做决定'},
    {'id': 27, 'type': 'A', 'text': '没有美丽事物的生活对我不可思议'},
    {'id': 28, 'type': 'S', 'text': '我常关心孤独不友善的人'},
    {'id': 29, 'type': 'E', 'text': '做事失败了我再接再厉'},
    {'id': 30, 'type': 'C', 'text': '小心谨慎完成一件事让我有成就感'},
]

HOLLAND_PROFILES = {
    'R': {'name': '现实型', 'traits': '动手能力强，喜欢具体实际的任务',
          'majors': ['机械工程', '土木工程', '电气工程', '航空航天', '车辆工程'],
          'careers': ['工程师', '技术员', '飞行员', '运动员']},
    'I': {'name': '研究型', 'traits': '喜欢思考分析，对科学充满好奇',
          'majors': ['计算机科学', '软件工程', '数学', '物理学', '临床医学'],
          'careers': ['科学家', '程序员', '医生', '研究员']},
    'A': {'name': '艺术型', 'traits': '富有想象力和创造力，喜欢表达',
          'majors': ['设计学', '建筑学', '汉语言文学', '新闻传播', '音乐表演'],
          'careers': ['设计师', '作家', '导演', '建筑师']},
    'S': {'name': '社会型', 'traits': '喜欢帮助他人，善于沟通合作',
          'majors': ['教育学', '心理学', '护理学', '社会学', '人力资源管理'],
          'careers': ['教师', '心理咨询师', '护士', '社工']},
    'E': {'name': '企业型', 'traits': '自信果断，喜欢领导和说服他人',
          'majors': ['工商管理', '市场营销', '金融学', '法学', '经济学'],
          'careers': ['企业家', '律师', '投资顾问', '销售经理']},
    'C': {'name': '常规型', 'traits': '喜欢有条理的工作，注重细节规范',
          'majors': ['会计学', '财务管理', '统计学', '审计学', '行政管理'],
          'careers': ['会计师', '审计师', '银行职员', '行政主管']},
}

MBTI_QUESTIONS = [
    # E/I 维度 (8题)
    {"id": 1, "text": "在社交聚会中，你通常：", "option_a": "主动与许多人交谈，包括陌生人", "option_b": "只与几个熟悉的朋友深入交谈", "dimension": "EI", "a_value": "E"},
    {"id": 2, "text": "当你独处时，你通常感觉：", "option_a": "感到无聊，希望有人陪伴", "option_b": "感到放松，享受独处时光", "dimension": "EI", "a_value": "I"},
    {"id": 3, "text": "面对新环境时，你倾向于：", "option_a": "主动探索，很快融入其中", "option_b": "先观察了解，慢慢适应", "dimension": "EI", "a_value": "E"},
    {"id": 4, "text": "周末时，你更喜欢：", "option_a": "参加聚会或外出活动", "option_b": "在家休息或做自己喜欢的事", "dimension": "EI", "a_value": "E"},
    {"id": 5, "text": "在团队中，你通常：", "option_a": "积极发言，带动讨论", "option_b": "倾听思考，适时表达观点", "dimension": "EI", "a_value": "E"},
    {"id": 6, "text": "遇到问题时，你倾向于：", "option_a": "找人讨论，寻求建议", "option_b": "独自思考，自己解决", "dimension": "EI", "a_value": "E"},
    {"id": 7, "text": "你更喜欢哪种工作方式：", "option_a": "与团队合作，共同完成", "option_b": "独立工作，专注任务", "dimension": "EI", "a_value": "E"},
    {"id": 8, "text": "在陌生场合，你通常：", "option_a": "感到兴奋，愿意尝试", "option_b": "感到紧张，需要时间适应", "dimension": "EI", "a_value": "E"},
    # S/N 维度 (8题)
    {"id": 9, "text": "你更关注：", "option_a": "当前的事实和细节", "option_b": "未来的可能性和整体", "dimension": "SN", "a_value": "S"},
    {"id": 10, "text": "阅读时，你更喜欢：", "option_a": "按顺序逐字阅读", "option_b": "跳跃阅读，寻找关键信息", "dimension": "SN", "a_value": "S"},
    {"id": 11, "text": "学习新知识时，你倾向于：", "option_a": "从具体例子开始学习", "option_b": "先理解概念和原理", "dimension": "SN", "a_value": "S"},
    {"id": 12, "text": "你更信任：", "option_a": "自己的经验和观察", "option_b": "自己的直觉和灵感", "dimension": "SN", "a_value": "S"},
    {"id": 13, "text": "描述一件事时，你会：", "option_a": "详细描述具体细节", "option_b": "概括描述整体印象", "dimension": "SN", "a_value": "S"},
    {"id": 14, "text": "解决问题时，你倾向于：", "option_a": "使用已验证的方法", "option_b": "尝试新的创新方法", "dimension": "SN", "a_value": "S"},
    {"id": 15, "text": "你更喜欢哪种故事：", "option_a": "基于现实的真实故事", "option_b": "充满想象的虚构故事", "dimension": "SN", "a_value": "S"},
    {"id": 16, "text": "做决定时，你更看重：", "option_a": "已有的数据和事实", "option_b": "潜在的机会和趋势", "dimension": "SN", "a_value": "S"},
    # T/F 维度 (7题)
    {"id": 17, "text": "做决定时，你更看重：", "option_a": "逻辑分析和客观标准", "option_b": "人际关系和他人感受", "dimension": "TF", "a_value": "T"},
    {"id": 18, "text": "面对冲突时，你倾向于：", "option_a": "理性分析，找出解决方案", "option_b": "考虑各方感受，寻求和解", "dimension": "TF", "a_value": "T"},
    {"id": 19, "text": "评价他人时，你更看重：", "option_a": "能力和成就", "option_b": "品格和态度", "dimension": "TF", "a_value": "T"},
    {"id": 20, "text": "你更容易被什么打动：", "option_a": "有力的论证和数据", "option_b": "感人的故事和情感", "dimension": "TF", "a_value": "T"},
    {"id": 21, "text": "批评他人时，你会：", "option_a": "直接指出问题所在", "option_b": "委婉表达，顾及感受", "dimension": "TF", "a_value": "T"},
    {"id": 22, "text": "你认为更重要的是：", "option_a": "公平公正，按规则办事", "option_b": "仁慈宽容，特殊情况特殊处理", "dimension": "TF", "a_value": "T"},
    {"id": 23, "text": "帮助他人时，你倾向于：", "option_a": "提供实际可行的建议", "option_b": "给予情感上的支持和安慰", "dimension": "TF", "a_value": "T"},
    # J/P 维度 (7题)
    {"id": 24, "text": "你更喜欢：", "option_a": "制定计划，按计划行事", "option_b": "保持灵活，随机应变", "dimension": "JP", "a_value": "J"},
    {"id": 25, "text": "完成任务时，你倾向于：", "option_a": "提前完成，留出时间", "option_b": "在最后期限前完成", "dimension": "JP", "a_value": "J"},
    {"id": 26, "text": "你的工作环境通常是：", "option_a": "整洁有序，井井有条", "option_b": "随意灵活，可能有些凌乱", "dimension": "JP", "a_value": "J"},
    {"id": 27, "text": "面对日程安排，你倾向于：", "option_a": "喜欢明确的日程安排", "option_b": "喜欢保持开放和灵活", "dimension": "JP", "a_value": "J"},
    {"id": 28, "text": "做决定时，你倾向于：", "option_a": "尽快做出决定", "option_b": "收集更多信息后再决定", "dimension": "JP", "a_value": "J"},
    {"id": 29, "text": "你更看重：", "option_a": "完成结果和效率", "option_b": "过程体验和可能性", "dimension": "JP", "a_value": "J"},
    {"id": 30, "text": "旅行时，你倾向于：", "option_a": "提前规划路线和行程", "option_b": "随兴而行，探索未知", "dimension": "JP", "a_value": "J"},
]

MBTI_PROFILES = {
    'INTJ': {'name': '建筑师', 'as': '理科', 'majors': ['计算机科学', '数学', '物理学', '工程学', '哲学'], 'desc': '战略型思考者，独立解决复杂问题'},
    'INTP': {'name': '逻辑学家', 'as': '理科', 'majors': ['计算机科学', '数学', '物理学', '哲学'], 'desc': '创新思维者，对理论充满热情'},
    'ENTJ': {'name': '指挥官', 'as': '理科', 'majors': ['工商管理', '经济学', '法学', '金融学'], 'desc': '天生的领导者，善于战略执行'},
    'ENTP': {'name': '辩论家', 'as': '文理均可', 'majors': ['法学', '新闻学', '市场营销', '计算机科学'], 'desc': '机智善辩，喜欢智力挑战'},
    'INFJ': {'name': '提倡者', 'as': '文科', 'majors': ['心理学', '教育学', '文学', '社会学'], 'desc': '理想主义者，富有洞察力'},
    'INFP': {'name': '调停者', 'as': '文科', 'majors': ['文学', '心理学', '艺术设计', '新闻传播'], 'desc': '富有创造力，重视价值观'},
    'ENFJ': {'name': '主人公', 'as': '文科', 'majors': ['教育学', '心理学', '人力资源管理', '传播学'], 'desc': '天生教育者，善于激励他人'},
    'ENFP': {'name': '竞选者', 'as': '文科', 'majors': ['新闻传播', '心理学', '市场营销', '文学创作'], 'desc': '热情洋溢，富有创造力'},
    'ISTJ': {'name': '物流师', 'as': '理科', 'majors': ['会计学', '工程学', '法学', '医学'], 'desc': '务实可靠，注重事实细节'},
    'ISFJ': {'name': '守卫者', 'as': '文理均可', 'majors': ['护理学', '教育学', '医学', '社会工作'], 'desc': '忠诚的保护者，乐于助人'},
    'ESTJ': {'name': '总经理', 'as': '理科', 'majors': ['工商管理', '金融学', '法学', '工程管理'], 'desc': '优秀管理者，注重效率秩序'},
    'ESFJ': {'name': '执政官', 'as': '文科', 'majors': ['教育学', '护理学', '人力资源管理', '社会工作'], 'desc': '热心周到，善于照顾他人'},
    'ISTP': {'name': '鉴赏家', 'as': '理科', 'majors': ['机械工程', '计算机科学', '电子工程', '体育学'], 'desc': '动手能力强，喜欢探索原理'},
    'ISFP': {'name': '探险家', 'as': '文科', 'majors': ['艺术设计', '音乐表演', '护理学', '摄影'], 'desc': '灵活艺术家，重视美感和体验'},
    'ESTP': {'name': '企业家', 'as': '理科', 'majors': ['市场营销', '金融学', '工程管理', '体育管理'], 'desc': '精力充沛行动派，善于把握机会'},
    'ESFP': {'name': '表演者', 'as': '文科', 'majors': ['表演艺术', '旅游管理', '学前教育', '播音主持'], 'desc': '天生表演者，热爱生活社交'},
}

ZXF_ADVICE = {
    'R': ['工科是普通家庭孩子改变命运的高性价比选择，就业稳、薪资可期。',
         '合肥工业大学、哈工大威海——低调但工科就业杠杠的。'],
    'I': ['计算机专业是普通家庭孩子改变命运性价比最高的专业，但互联网高薪是用青春换的。',
         '学医是一条长线投资，30岁之前别想赚钱，但越老越吃香。'],
    'A': ['学设计学艺术，家里没矿真的别碰。投入大、回报慢，还得拼审美天赋。',
         '如果你真的热爱艺术，可以考虑数字媒体、UI设计——有技术底子的艺术生最吃香。'],
    'S': ['师范专业，铁饭碗中的铁饭碗。稳定、体面、有寒暑假——但别指望大富大贵。',
         '心理学听着高大上，但必须读到硕士才有出路。'],
    'E': ['金融专业——如果你家境一般、没有任何社会资源，真心不建议。',
         '你学了四年管理学，毕业去管谁？不如学个有技术门槛的专业。'],
    'C': ['会计是文科中的理科，越老越吃香。CPA证书比名校文凭还管用。',
         '财务、审计这类岗位最大的优点是——任何行业都需要，不用担心失业。'],
}


# ==================== 辅助函数 ====================

def _get_session_id(request):
    """获取或创建session ID"""
    if 'user_session_id' not in request.session:
        import uuid
        request.session['user_session_id'] = str(uuid.uuid4())
    return request.session['user_session_id']


def _load_majors():
    """加载专业数据库"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    majors_path = os.path.join(data_dir, 'majors.json')
    if os.path.exists(majors_path):
        with open(majors_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # majors.json 可能是列表或字典：如果是列表，按 category 分组成字典，兼容现有代码
            if isinstance(data, list):
                grouped = {}
                for m in data:
                    cat = m.get('category', '其他')
                    grouped.setdefault(cat, []).append(m)
                return grouped
            return data
    return []


# ==================== 页面视图 ====================

def home_page(request):
    """首页"""
    return render(request, 'assessment/home.html')


def mbti_test(request):
    """MBTI测试页面 - 30道真实题目"""
    if request.method == 'POST':
        scores = {'E': 0, 'I': 0, 'S': 0, 'N': 0, 'T': 0, 'F': 0, 'J': 0, 'P': 0}
        for q in MBTI_QUESTIONS:
            answer = request.POST.get(f'q{q["id"]}', '')
            dim = q['dimension']
            vals = dim
            if answer == 'A':
                scores[vals[0]] += 1
            elif answer == 'B':
                scores[vals[1]] += 1

        mbti_type = ''
        mbti_type += 'E' if scores['E'] >= scores['I'] else 'I'
        mbti_type += 'S' if scores['S'] >= scores['N'] else 'N'
        mbti_type += 'T' if scores['T'] >= scores['F'] else 'F'
        mbti_type += 'J' if scores['J'] >= scores['P'] else 'P'

        request.session['mbti'] = mbti_type
        request.session['mbti_scores'] = scores

        # 保存到数据库
        try:
            from . import db_utils
            sid = _get_session_id(request)
            db_utils.create_user(sid)
            db_utils.save_assessment(sid,
                                     holland_code=request.session.get('holland', ''),
                                     holland_scores=request.session.get('holland_scores', {}),
                                     mbti_type=mbti_type)
        except Exception:
            pass

        messages.success(request, f'MBTI测试完成！你的类型是：{mbti_type} - {MBTI_PROFILES.get(mbti_type, {}).get("name", "")}')
        return redirect('holland_test')

    return render(request, 'assessment/mbti_test.html', {
        'questions': MBTI_QUESTIONS,
        'total': len(MBTI_QUESTIONS),
    })


def holland_test(request):
    """霍兰德测试页面 - 30道真实题目"""
    if request.method == 'POST':
        scores = {'R': 0, 'I': 0, 'A': 0, 'S': 0, 'E': 0, 'C': 0}
        for q in HOLLAND_QUESTIONS:
            answer = request.POST.get(f'q{q["id"]}', '')
            if answer == 'yes':
                scores[q['type']] += 1

        sorted_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        holland_code = ''.join([t[0] for t in sorted_types[:3]])

        request.session['holland'] = holland_code
        request.session['holland_scores'] = scores

        # 保存到数据库
        try:
            from . import db_utils
            sid = _get_session_id(request)
            db_utils.create_user(sid)
            db_utils.save_assessment(sid,
                                     holland_code=holland_code,
                                     holland_scores=scores,
                                     mbti_type=request.session.get('mbti', ''))
        except Exception:
            pass

        top3 = []
        for code, score in sorted_types[:3]:
            profile = HOLLAND_PROFILES.get(code, {})
            top3.append({'code': code, 'name': profile.get('name', ''), 'score': score,
                         'traits': profile.get('traits', ''), 'majors': profile.get('majors', [])})
        request.session['holland_top3'] = top3

        messages.success(request, f'霍兰德测试完成！你的代码是：{holland_code}')
        return redirect('profile')

    return render(request, 'assessment/holland_test.html', {
        'questions': HOLLAND_QUESTIONS,
        'total': len(HOLLAND_QUESTIONS),
    })

#====================== 新函数 =================

def build_holland_top3_from_code(holland_code_input):
    """根据霍兰德三码生成top3详情（复用已有的 HOLLAND_PROFILES）"""
    code_upper = holland_code_input.upper()
    # 默认分数（根据优先级递减）
    default_points = {'R': 85, 'I': 88, 'A': 82, 'S': 90, 'E': 86, 'C': 80}
    result_list = []
    for idx, letter in enumerate(code_upper):
        point = default_points.get(letter, 80) - idx * 3
        if point < 65:
            point = 65
        # 复用已有的 HOLLAND_PROFILES
        profile = HOLLAND_PROFILES.get(letter, {})
        result_list.append({
            'type': letter,
            'name': profile.get('name', f'{letter}型'),
            'score': point,
            'trait': profile.get('traits', '特质待补充'),
            'majors': ', '.join(profile.get('majors', ['多学科方向'])[:3])  # 取前3个专业
        })
    return result_list


def profile_page(request):
    """个人信息页面"""
    if request.method == 'POST':
       
        # ========= 新增：处理MBTI手动修改 =====
        if 'manual_update_mbti' in request.POST:
            input_mbti_code = request.POST.get('manual_mbti_code', '').strip().upper()
            if input_mbti_code in MBTI_PROFILES:
                matched_profile = MBTI_PROFILES[input_mbti_code]
                request.session['mbti'] = input_mbti_code
                request.session['mbti_name'] = matched_profile.get('name', '')
                request.session['mbti_desc'] = matched_profile.get('desc', '')
                request.session['mbti_as'] = matched_profile.get('as', '')
                messages.success(request, f'MBTI 已更新为：{input_mbti_code} - {matched_profile["name"]}')
            else:
                messages.error(request, f'无效的MBTI类型：{input_mbti_code}，请输入有效的4字母组合（如 INTJ, ENFP）')
            return redirect('profile')
        
        # ========= 新增：处理 霍兰德职业测试 手动修改 =====
  
        if 'manual_update_holland' in request.POST:
            input_holland_code = request.POST.get('manual_holland_code', '').strip().upper()
            if len(input_holland_code) == 3 and all(ch in 'RIASEC' for ch in input_holland_code):
                request.session['holland'] = input_holland_code
                auto_top3 = build_holland_top3_from_code(input_holland_code)
                request.session['holland_top3'] = auto_top3
                messages.success(request, f'霍兰德已更新为：{input_holland_code}')
            else:
                messages.error(request, f'无效的霍兰德代码：{input_holland_code}，请输入3个字母（如 SEC, RIA）')
            return redirect('profile')
    
        
        
        #============== 原有的 ======================
        gaokao_score = request.POST.get('gaokao_score', '')
        province = request.POST.get('province', '')
        selected_subjects = request.POST.get('subject', '')
        interests = request.POST.get('interests', '')

        chinese_score = request.POST.get('chinese_score', '')
        math_score = request.POST.get('math_score', '')
        physics_score = request.POST.get('physics_score', '')
        history_score = request.POST.get('history_score', '')

        # 字符串转数字，空内容转为 None
        def to_int(val):
            val = val.strip()
            return int(val) if val else None

        update_data = {
            "gaokao_score": to_int(gaokao_score),
            "province": province,
            "selected_subjects": selected_subjects,
            "interests": interests,
            "chinese_score": to_int(chinese_score),
            "math_score": to_int(math_score),
            "physics_score": to_int(physics_score),
            "history_score": to_int(history_score)
        }

        # 存入 Session 用于页面回显
        for k, v in update_data.items():
            request.session[k] = v

        try:
            from . import db_utils
            sid = _get_session_id(request)
            db_utils.update_user(sid, **update_data)
        except Exception as e:
            # 控制台打印错误，方便调试
            print("保存用户数据出错：", e)

        messages.success(request, '个人信息已保存！')
        return redirect('recommend')

    # GET 请求：读取 Session 数据传给模板
    mbti = request.session.get('mbti', '')
    mbti_profile = MBTI_PROFILES.get(mbti, {})
    holland = request.session.get('holland', '')
    holland_top3 = request.session.get('holland_top3', [])
    holland_scores = request.session.get('holland_scores', {})

    return render(request, 'assessment/profile.html', {
        'mbti': mbti,
        'mbti_name': mbti_profile.get('name', ''),
        'mbti_desc': mbti_profile.get('desc', ''),
        'mbti_as': mbti_profile.get('as', ''),
        'mbti_majors': mbti_profile.get('majors', []),
        'holland': holland,
        'holland_top3': holland_top3,
        'holland_scores': holland_scores,
        'gaokao_score': request.session.get('gaokao_score', ''),
        'province': request.session.get('province', ''),
        'selected_subjects': request.session.get('selected_subjects', ''),
        'interests': request.session.get('interests', ''),
        'chinese_score': request.session.get('chinese_score', ''),
        'math_score': request.session.get('math_score', ''),
        'physics_score': request.session.get('physics_score', ''),
        'history_score': request.session.get('history_score', ''),
    })


def recommend_page(request):
    """初始推荐页面 - 使用TOPSIS算法"""
    mbti = request.session.get('mbti', '')
    holland = request.session.get('holland', '')
    holland_scores = request.session.get('holland_scores', {})
    gaokao_score = request.session.get('gaokao_score', 0)
    interests = request.session.get('interests', '')
    province = request.session.get('province', '')

    # ========= 新增：读取选科 + 单科分数 =========
    selected_subjects = request.session.get('selected_subjects', '')
    chinese_score = request.session.get('chinese_score')
    math_score = request.session.get('math_score')
    physics_score = request.session.get('physics_score')
    history_score = request.session.get('history_score')

    # 调试打印，确认拿到数据
    print("==== 推荐页 选科&分数 ====")
    print("选科组合:", selected_subjects)
    print("语文:", chinese_score, "数学:", math_score)
    print("物理:", physics_score, "历史:", history_score)

    # 使用TOPSIS算法生成推荐
    recommendations = []
    weights = {}
    try:
        from .algorithms.topsis import TOPSIS, get_initial_weights
        from .algorithms.semantic_matching import SemanticMatcher

        majors_data = _load_majors()
        # 将majors.json格式转为算法需要的格式
        all_majors = []
        for category, majors_list in majors_data.items():
            for m in majors_list:
                all_majors.append({
                    'id': all_majors.__len__() + 1,
                    'name': m.get('name', ''),
                    'category': category,
                    'keywords': m.get('keywords', []) if isinstance(m.get('keywords', []), list) else [m.get('keywords', '')],
                    'employment_rate': m.get('employment_rate', 0.8),
                    'salary_level': m.get('salary_level', 0.7),
                })

        # 语义匹配
        matcher = SemanticMatcher(all_majors) if all_majors else None
        matched = []
        if matcher and interests:
            matched = matcher.match_interests_to_majors(interests, top_k=50)
        # 计算对所有专业的 TF-IDF 余弦相似度（使兴趣影响能扩散到相关专业）
        from sklearn.metrics.pairwise import cosine_similarity as _cos_sim
        user_vec = matcher.vectorizer.transform([interests or '']) if matcher and interests else None
        sims_full = _cos_sim(user_vec, matcher.major_vectors)[0] if user_vec is not None else None

        # ========= 重点：调用新版权重函数，传入全部新参数 =========
        # 空值兼容：None/空转为0
        def safe_num(val):
            return val if val is not None else 0

        initial_weights = get_initial_weights(
            holland_code=holland,
            mbti=mbti,
            gaokao_score=int(gaokao_score) if gaokao_score else 0,
            province=province,
            selected_subjects=selected_subjects,
            chinese_score=safe_num(chinese_score),
            math_score=safe_num(math_score),
            physics_score=safe_num(physics_score),
            history_score=safe_num(history_score)
        )

        # 如果存在 AHP 权重（博弈结果），使用它来微调初始权重，使博弈优化生效
        ahp_weights = request.session.get('ahp_weights')
        def _apply_ahp_adjustments(base_weights, ahp):
            """将 AHP 霍兰德维度权重作为乘子作用到 TOPSIS 初始权重，然后归一化。
            ahp: {'R':0.15,'I':0.2,...}（和为1）
            处理：对每个影响的 TOPSIS 权重乘以 (1 + scale * ahp_val)
            """
            if not ahp:
                return base_weights
            scale = 2.0  # 放大系数（已由 0.8 增强至 2.0）以增强 AHP 对 TOPSIS 权重的影响
            w = base_weights.copy()
            for letter, val in ahp.items():
                try:
                    ahp_val = float(val)
                except Exception:
                    ahp_val = 0.0
                multiplier = 1.0 + scale * ahp_val
                if letter == 'I':
                    w['personality_fit'] *= multiplier
                    w['interest_match'] *= multiplier
                elif letter == 'E':
                    w['salary_level'] *= multiplier
                    w['employment_rate'] *= multiplier
                elif letter == 'R':
                    w['gaokao_fit'] *= multiplier
                elif letter == 'A':
                    w['interest_match'] *= multiplier
                elif letter == 'S':
                    w['personality_fit'] *= multiplier
                elif letter == 'C':
                    w['gaokao_fit'] *= multiplier

            # 归一化
            total = sum(w.values()) or 1
            for k in w:
                w[k] = round(w[k] / total, 4)
            return w

        # 构建评价矩阵：使用 TF-IDF 全量相似度作为 sim
        criteria_matrix = []
        for i, major in enumerate(all_majors):
            personality_score = 0.7
            sim = float(sims_full[i]) if sims_full is not None else 0.0
            # interest_score 映射（采用较宽基底，使更多专业受益）
            interest_score = 0.4 + 0.6 * sim
            gaokao_fit = 0.6
            criteria_matrix.append([
                personality_score,
                interest_score,
                gaokao_fit,
                major.get('employment_rate', 0.8),
                major.get('salary_level', 0.7),
            ])

        # 如果有 AHP 结果，调整初始权重（乘子方式）
        initial_weights = _apply_ahp_adjustments(initial_weights, ahp_weights)

        # 构建 numpy 矩阵并做列级归一化（支持 rank-normalize 与 min-max）
        import numpy as _np
        criteria_matrix = _np.array(criteria_matrix, dtype=float)
        if criteria_matrix.size == 0:
            criteria_matrix = _np.zeros((len(all_majors), 5))

        # 归一化策略开关：默认启用 rank-normalize（按列排名再映射到 [0,1]）
        use_rank_normalize = request.session.get('use_rank_normalize', True)
        if use_rank_normalize:
            # rank-normalize: 更稳健地抑制极端值对 TOPSIS 的主导性
            N, M = criteria_matrix.shape
            rank_matrix = _np.zeros_like(criteria_matrix, dtype=float)
            for col in range(M):
                col_vals = criteria_matrix[:, col]
                # 以降序排序（值越大排名越靠前）
                sorted_idx = _np.argsort(-col_vals)
                ranks = _np.empty(N, dtype=float)
                rank = 1
                i = 0
                # 手工计算平均排名以处理并列
                while i < N:
                    j = i + 1
                    while j < N and col_vals[sorted_idx[j]] == col_vals[sorted_idx[i]]:
                        j += 1
                    avg_rank = rank + (j - i - 1) / 2.0
                    ranks[sorted_idx[i:j]] = avg_rank
                    rank += (j - i)
                    i = j
                # 映射到 [0,1]
                if N > 1:
                    # 映射为 [0,1]，并保证值越大映射越接近1（rank 1 -> 1）
                    rank_matrix[:, col] = (N - ranks) / (N - 1)
                else:
                    rank_matrix[:, col] = 0.0
            norm_matrix = rank_matrix
        else:
            # min-max per column（原逻辑）
            mins = _np.min(criteria_matrix, axis=0)
            maxs = _np.max(criteria_matrix, axis=0)
            ranges = maxs - mins
            ranges[ranges == 0] = 1.0
            norm_matrix = (criteria_matrix - mins) / ranges

        # debug 打印归一化片段
        try:
            print("DEBUG: normalized criteria_matrix sample ->", norm_matrix[:5].tolist())
        except Exception:
            pass

        topsis = TOPSIS(weights=initial_weights)
        # 立即打印权重和部分评价矩阵，确保TOPSIS获得正确输入
        try:
            print("DEBUG: initial_weights ->", initial_weights)
            print("DEBUG: matched sample ->", matched[:5])
            print("DEBUG: criteria_matrix sample ->", criteria_matrix[:5])
        except Exception:
            pass
        ranked = topsis.rank_majors(all_majors, norm_matrix)

        recommendations = ranked[:10]
        # 计算并附加 TOPSIS 中间量（距离与相对接近度），便于调试为何得分差距很大
        try:
            # 使用 TOPSIS 内部归一化以保持一致性
            normalized_for_topsis = topsis._normalize_matrix(norm_matrix)
            weight_list = list(initial_weights.values())
            weighted_matrix = normalized_for_topsis * _np.array(weight_list)
            ideal_best = _np.max(weighted_matrix, axis=0)
            ideal_worst = _np.min(weighted_matrix, axis=0)
            d_pos = _np.array([_np.linalg.norm(weighted_matrix[i] - ideal_best) for i in range(weighted_matrix.shape[0])])
            d_neg = _np.array([_np.linalg.norm(weighted_matrix[i] - ideal_worst) for i in range(weighted_matrix.shape[0])])
            closeness = d_neg / (d_pos + d_neg + 1e-10)
            # 将这些值加入到 recommendations（匹配索引来自 ranked 的原索引）
            # ranked 列表中顺序为降序排序，ranked[i] 对应索引 ranked_indices[i]
            for r in recommendations:
                # 查找原始所在行（通过匹配 name）
                try:
                    idx = next(i for i, m in enumerate(all_majors) if m.get('name') == r.get('name'))
                except StopIteration:
                    idx = None
                if idx is not None:
                    r['d_pos'] = float(d_pos[idx])
                    r['d_neg'] = float(d_neg[idx])
                    r['closeness'] = float(closeness[idx])
        except Exception:
            pass
        # 将 topsis_score 转为百分制 score 字段用于页面展示
        for r in recommendations:
            try:
                r_score = float(r.get('topsis_score', 0.0))
            except Exception:
                r_score = 0.0
            r['score'] = round(r_score * 100, 2)
        weights = initial_weights

        # 日志：打印前十个推荐及权重信息，便于调试
        try:
            logger.info(f"TOPSIS initial weights: {initial_weights}")
            logger.info(f"Matched majors count: {len(matched) if matched else 0}")
            logger.info("Top 10 recommendations: %s", [r.get('name') for r in recommendations[:10]])
            # 兼容显示：也打印到 stdout，确保在 runserver 输出中可见
            print("TOPSIS initial weights:", initial_weights)
            print("Matched majors count:", len(matched) if matched else 0)
            print("Top 10 recommendations:", [r.get('name') for r in recommendations[:10]])
            # 打印每个推荐的中间量
            try:
                for r in recommendations:
                    print("REC:", r.get('name'),
                          "score:", round(r.get('topsis_score', 0), 4),
                          "d_pos:", round(r.get('d_pos', 0), 6),
                          "d_neg:", round(r.get('d_neg', 0), 6),
                          "closeness:", round(r.get('closeness', 0), 6))
            except Exception:
                pass
        except Exception:
            pass

        # 保存到数据库
        try:
            from . import db_utils
            sid = _get_session_id(request)
            assessment = db_utils.get_assessment(sid)
            if assessment:
                rec_list = []
                for i, r in enumerate(recommendations):
                    rec_list.append({
                        'name': r.get('name', ''),
                        'score': round(r.get('topsis_score', 0), 4),
                        'rank': i+1,
                        'd_pos': r.get('d_pos'),
                        'd_neg': r.get('d_neg'),
                        'closeness': r.get('closeness')
                    })
                db_utils.save_recommendation(sid, assessment.id, rec_list, weights, version=0)
        except Exception:
            pass

    except Exception as e:
        print("算法异常:", e)
        # 算法失败时使用基于霍兰德的简单推荐
        recommendations = _simple_recommend(mbti, holland)

    request.session['recommendations'] = recommendations
    request.session['current_weights'] = weights

    # 将权重转换为百分比传给模板（避免模板把0.25当作0.25%显示）
    percent_weights = {}
    if weights:
        for k, v in weights.items():
            try:
                percent_weights[k] = round(float(v) * 100, 2)
            except Exception:
                percent_weights[k] = 0.0
    else:
        percent_weights = weights

    mbti_profile = MBTI_PROFILES.get(mbti, {})
    holland_top3 = request.session.get('holland_top3', [])

    # 获取张雪峰建议
    zxf_advices = []
    for code, score in sorted(holland_scores.items(), key=lambda x: x[1], reverse=True)[:2]:
        advices = ZXF_ADVICE.get(code, [])
        zxf_advices.extend(advices)

    return render(request, 'assessment/recommend.html', {
        'mbti': mbti,
        'mbti_name': mbti_profile.get('name', ''),
        'mbti_as': mbti_profile.get('as', ''),
        'holland': holland,
        'holland_top3': holland_top3,
        'recommendations': recommendations,
        'weights': percent_weights,
        'zxf_advices': zxf_advices[:3],
        'gaokao_score': gaokao_score,
    })



def game_page(request):
    """博弈优化页面 - 使用AHP博弈引擎，显示7道成对比较问题"""
    from .algorithms.game_engine import GameEngine, GAME_QUESTIONS
    
    sid = _get_session_id(request)
    
    # 从session获取或创建游戏引擎状态
    if 'game_engine_state' not in request.session:
        request.session['game_engine_state'] = {
            'current_index': 0,
            'answers': [],
            'completed': False
        }
    
    game_state = request.session['game_engine_state']
    engine = GameEngine(sid)
    engine.current_index = game_state['current_index']
    engine.answers = game_state['answers']
    
    if request.method == 'POST':
        # 处理AJAX提交答案
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            import json
            data = json.loads(request.body)
            action = data.get('action')
            
            if action == 'submit_answer':
                question_id = data.get('question_id')
                answer = data.get('answer')  # 'a' 或 'b'
                
                if engine.submit_answer(question_id, answer):
                    game_state['current_index'] = engine.current_index
                    game_state['answers'] = engine.answers
                    request.session['game_engine_state'] = game_state
                    
                    # 获取下一题
                    next_q = engine.get_next_question()
                    if next_q:
                        return JsonResponse({
                            'success': True,
                            'completed': False,
                            'next_question': next_q
                        })
                    else:
                        # 所有问题回答完毕，计算权重
                        weights = engine.calculate_weights()
                        game_state['completed'] = True
                        game_state['weights'] = weights
                        request.session['game_engine_state'] = game_state
                        request.session['ahp_weights'] = weights
                        
                        # 保存到数据库
                        try:
                            from . import db_utils
                            rec = db_utils.get_latest_recommendation(sid)
                            if rec:
                                db_utils.save_dialogue(
                                    rec.id, 
                                    f"AHP博弈完成，回答了{len(engine.answers)}道题", 
                                    'ahp_complete', 
                                    {},
                                    weights,
                                    engine.answers,
                                    f"AHP权重计算完成：{weights}"
                                )
                        except Exception as e:
                            print(f"保存对话失败: {e}")
                        
                        return JsonResponse({
                            'success': True,
                            'completed': True,
                            'weights': weights
                        })
                else:
                    return JsonResponse({'success': False, 'error': '提交答案失败'})
            
            elif action == 'get_question':
                current_q = engine.get_next_question()
                if current_q:
                    return JsonResponse({
                        'success': True,
                        'question': current_q,
                        'progress': f"{engine.current_index + 1}/{len(GAME_QUESTIONS)}"
                    })
                else:
                    return JsonResponse({
                        'success': True,
                        'completed': True,
                        'weights': engine.calculate_weights() if engine.answers else {}
                    })
        
        # 处理表单提交（查看报告）
        if 'next' in request.POST:
            # 清理游戏状态
            if 'game_engine_state' in request.session:
                del request.session['game_engine_state']
            return redirect('report')
    
    # GET请求：获取当前问题
    current_question = engine.get_next_question()
    progress = f"{engine.current_index + 1}/{len(GAME_QUESTIONS)}" if current_question else f"{len(GAME_QUESTIONS)}/{len(GAME_QUESTIONS)}"
    completed = game_state.get('completed', False)
    final_weights = game_state.get('weights', {}) if completed else {}
    
    mbti = request.session.get('mbti', '')
    holland = request.session.get('holland', '')
    recommendations = request.session.get('recommendations', [])
    
    return render(request, 'assessment/game.html', {
        'mbti': mbti, 
        'holland': holland,
        'recommendations': recommendations,
        'current_question': current_question,
        'progress': progress,
        'completed': completed,
        'final_weights': final_weights,
        'total_questions': len(GAME_QUESTIONS),
    })


def report_page(request):
    """最终报告页面"""
    mbti = request.session.get('mbti', '')
    mbti_profile = MBTI_PROFILES.get(mbti, {})
    holland = request.session.get('holland', '')
    holland_top3 = request.session.get('holland_top3', [])
    holland_scores = request.session.get('holland_scores', {})
    #比例*20
    holland_scores = {k: v * 20 for k, v in holland_scores.items()}
    recommendations = request.session.get('recommendations', [])
    weights = request.session.get('current_weights', {})
    mbti_scores = request.session.get('mbti_scores', {})
    mbti_scores = {k: v * 10 for k, v in mbti_scores.items()}
    
    # 张雪峰建议
    zxf_advices = []
    for code, score in sorted(holland_scores.items(), key=lambda x: x[1], reverse=True)[:2]:
        zxf_advices.extend(ZXF_ADVICE.get(code, []))

    return render(request, 'assessment/report.html', {
        'mbti': mbti,
        'mbti_name': mbti_profile.get('name', ''),
        'mbti_desc': mbti_profile.get('desc', ''),
        'mbti_as': mbti_profile.get('as', ''),
        'mbti_majors': mbti_profile.get('majors', []),
        'mbti_scores': mbti_scores,
        'holland': holland,
        'holland_top3': holland_top3,
        'holland_scores': holland_scores,
        'recommendations': recommendations,
        'weights': weights,
        'zxf_advices': zxf_advices[:4],
        'gaokao_score': request.session.get('gaokao_score', ''),
        'province': request.session.get('province', ''),
        'selected_subjects': request.session.get('selected_subjects', ''),
        'interests': request.session.get('interests', ''),
    })


# ==================== API接口（保留兼容） ====================

def get_data(request):
    return JsonResponse({
        'holland_questions': HOLLAND_QUESTIONS,
        'holland_profiles': HOLLAND_PROFILES,
        'mbti_profiles': MBTI_PROFILES,
        'zxf_advice': ZXF_ADVICE,
    })


# ==================== 辅助函数 ====================

def _simple_recommend(mbti, holland):
    """简单推荐（算法失败时的降级方案）"""
    mbti_profile = MBTI_PROFILES.get(mbti, {})
    majors = mbti_profile.get('majors', [])
    result = []
    for i, name in enumerate(majors):
        result.append({'name': name, 'score': round(0.95 - i * 0.05, 4), 'rank': i + 1})
    return result


def _parse_intent(text):
    """简单的意图识别"""
    text = text.lower()
    if any(kw in text for kw in ['金融', '经济', '银行', '投资']):
        return 'finance'
    elif any(kw in text for kw in ['计算机', '编程', '代码', '软件']):
        return 'cs'
    elif any(kw in text for kw in ['医学', '医生', '临床']):
        return 'medical'
    elif any(kw in text for kw in ['教育', '老师', '师范']):
        return 'education'
    elif any(kw in text for kw in ['不喜欢', '不想', '排除']):
        return 'exclude'
    elif any(kw in text for kw in ['稳定', '铁饭碗', '公务员']):
        return 'stable'
    else:
        return 'general'


def _generate_response(intent, user_input):
    """生成系统回复"""
    responses = {
        'finance': '你对金融方向感兴趣。金融行业薪资高但竞争激烈，需要较强的数学和逻辑能力。我会适当提高薪资和就业前景的权重。',
        'cs': '计算机方向是当前热门选择，就业面广、薪资水平高。不过也要注意行业竞争和持续学习的压力。我会提高兴趣匹配的权重。',
        'medical': '医学是一条长线投资的道路，前期投入大但越老越吃香。需要较强的学习能力和耐心。我会综合考虑你的性格匹配度。',
        'education': '教育行业稳定且有寒暑假，适合喜欢帮助他人的人。师范类专业是文科生的优质选择之一。',
        'exclude': f'了解了，你不太倾向这个方向。我会将相关专业的排名降低，重新优化推荐方案。',
        'stable': '你更看重稳定性。公务员、师范、医学等方向会比较适合你，我会调整推荐权重。',
        'general': '我理解你的想法。让我根据你的反馈调整推荐方案的权重分配，重新为你优化专业推荐。',
    }
    return responses.get(intent, responses['general'])