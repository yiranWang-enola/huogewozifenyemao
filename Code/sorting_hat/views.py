from django.shortcuts import render, redirect
from django.contrib import messages
import json

# ==================== MBTI测试题目 ====================
# 30道题目，覆盖4个维度：E/I(外向/内向), S/N(感觉/直觉), T/F(思考/情感), J/P(判断/知觉)
# 每个维度约7-8道题，选择A得维度前项分数，选择B得维度后项分数

MBTI_QUESTIONS = [
    # E/I 维度 (外向 vs 内向) - 8题
    {"id": 1, "text": "在社交聚会中，你通常：", "option_a": "主动与许多人交谈，包括陌生人", "option_b": "只与几个熟悉的朋友深入交谈", "dimension": "EI", "a_value": "E"},
    {"id": 2, "text": "当你独处时，你通常感觉：", "option_a": "感到无聊，希望有人陪伴", "option_b": "感到放松，享受独处时光", "dimension": "EI", "a_value": "I"},
    {"id": 3, "text": "面对新环境时，你倾向于：", "option_a": "主动探索，很快融入其中", "option_b": "先观察了解，慢慢适应", "dimension": "EI", "a_value": "E"},
    {"id": 4, "text": "周末时，你更喜欢：", "option_a": "参加聚会或外出活动", "option_b": "在家休息或做自己喜欢的事", "dimension": "EI", "a_value": "E"},
    {"id": 5, "text": "在团队中，你通常：", "option_a": "积极发言，带动讨论", "option_b": "倾听思考，适时表达观点", "dimension": "EI", "a_value": "E"},
    {"id": 6, "text": "遇到问题时，你倾向于：", "option_a": "找人讨论，寻求建议", "option_b": "独自思考，自己解决", "dimension": "EI", "a_value": "E"},
    {"id": 7, "text": "你更喜欢哪种工作方式：", "option_a": "与团队合作，共同完成", "option_b": "独立工作，专注任务", "dimension": "EI", "a_value": "E"},
    {"id": 8, "text": "在陌生场合，你通常：", "option_a": "感到兴奋，愿意尝试", "option_b": "感到紧张，需要时间适应", "dimension": "EI", "a_value": "E"},
    
    # S/N 维度 (感觉 vs 直觉) - 8题
    {"id": 9, "text": "你更关注：", "option_a": "当前的事实和细节", "option_b": "未来的可能性和整体", "dimension": "SN", "a_value": "S"},
    {"id": 10, "text": "阅读时，你更喜欢：", "option_a": "按顺序逐字阅读", "option_b": "跳跃阅读，寻找关键信息", "dimension": "SN", "a_value": "S"},
    {"id": 11, "text": "学习新知识时，你倾向于：", "option_a": "从具体例子开始学习", "option_b": "先理解概念和原理", "dimension": "SN", "a_value": "S"},
    {"id": 12, "text": "你更信任：", "option_a": "自己的经验和观察", "option_b": "自己的直觉和灵感", "dimension": "SN", "a_value": "S"},
    {"id": 13, "text": "描述一件事时，你会：", "option_a": "详细描述具体细节", "option_b": "概括描述整体印象", "dimension": "SN", "a_value": "S"},
    {"id": 14, "text": "解决问题时，你倾向于：", "option_a": "使用已验证的方法", "option_b": "尝试新的创新方法", "dimension": "SN", "a_value": "S"},
    {"id": 15, "text": "你更喜欢哪种故事：", "option_a": "基于现实的真实故事", "option_b": "充满想象的虚构故事", "dimension": "SN", "a_value": "S"},
    {"id": 16, "text": "做决定时，你更看重：", "option_a": "已有的数据和事实", "option_b": "潜在的机会和趋势", "dimension": "SN", "a_value": "S"},
    
    # T/F 维度 (思考 vs 情感) - 7题
    {"id": 17, "text": "做决定时，你更看重：", "option_a": "逻辑分析和客观标准", "option_b": "人际关系和他人感受", "dimension": "TF", "a_value": "T"},
    {"id": 18, "text": "面对冲突时，你倾向于：", "option_a": "理性分析，找出解决方案", "option_b": "考虑各方感受，寻求和解", "dimension": "TF", "a_value": "T"},
    {"id": 19, "text": "评价他人时，你更看重：", "option_a": "能力和成就", "option_b": "品格和态度", "dimension": "TF", "a_value": "T"},
    {"id": 20, "text": "你更容易被什么打动：", "option_a": "有力的论证和数据", "option_b": "感人的故事和情感", "dimension": "TF", "a_value": "T"},
    {"id": 21, "text": "批评他人时，你会：", "option_a": "直接指出问题所在", "option_b": "委婉表达，顾及感受", "dimension": "TF", "a_value": "T"},
    {"id": 22, "text": "你认为更重要的是：", "option_a": "公平公正，按规则办事", "option_b": "仁慈宽容，特殊情况特殊处理", "dimension": "TF", "a_value": "T"},
    {"id": 23, "text": "帮助他人时，你倾向于：", "option_a": "提供实际可行的建议", "option_b": "给予情感上的支持和安慰", "dimension": "TF", "a_value": "T"},
    
    # J/P 维度 (判断 vs 知觉) - 7题
    {"id": 24, "text": "你更喜欢：", "option_a": "制定计划，按计划行事", "option_b": "保持灵活，随机应变", "dimension": "JP", "a_value": "J"},
    {"id": 25, "text": "完成任务时，你倾向于：", "option_a": "提前完成，留出时间", "option_b": "在最后期限前完成", "dimension": "JP", "a_value": "J"},
    {"id": 26, "text": "你的工作环境通常是：", "option_a": "整洁有序，井井有条", "option_b": "随意灵活，可能有些凌乱", "dimension": "JP", "a_value": "J"},
    {"id": 27, "text": "面对日程安排，你倾向于：", "option_a": "喜欢明确的日程安排", "option_b": "喜欢保持开放和灵活", "dimension": "JP", "a_value": "J"},
    {"id": 28, "text": "做决定时，你倾向于：", "option_a": "尽快做出决定", "option_b": "收集更多信息后再决定", "dimension": "JP", "a_value": "J"},
    {"id": 29, "text": "你更看重：", "option_a": "完成结果和效率", "option_b": "过程体验和可能性", "dimension": "JP", "a_value": "J"},
    {"id": 30, "text": "旅行时，你倾向于：", "option_a": "提前规划路线和行程", "option_b": "随兴而行，探索未知", "dimension": "JP", "a_value": "J"},
]

# MBTI类型描述
MBTI_DESCRIPTIONS = {
    "INTJ": {"name": "建筑师", "desc": "富有想象力和战略性的思想家，一切皆在计划之中"},
    "INTP": {"name": "逻辑学家", "desc": "富有创造力的发明家，知识渊博，永不停止思考"},
    "ENTJ": {"name": "指挥官", "desc": "大胆、富有想象力的领导者，总能找到解决方法"},
    "ENTP": {"name": "辩论家", "desc": "聪明好奇的思想家，无法抗拒智力挑战"},
    "INFJ": {"name": "提倡者", "desc": "安静而有影响力，理想主义者，致力于帮助他人"},
    "INFP": {"name": "调停者", "desc": "富有想象力的理想主义者，被内心的价值观引导"},
    "ENFJ": {"name": "主人公", "desc": "富有魅力的领导者，能够激励听众"},
    "ENFP": {"name": "竞选者", "desc": "热情、有创造力的社交者，总能找到微笑的理由"},
    "ISTJ": {"name": "检查者", "desc": "务实、有条理，重视传统和忠诚"},
    "ISFJ": {"name": "守护者", "desc": "温暖、尽职尽责，致力于保护传统和组织"},
    "ESTJ": {"name": "总经理", "desc": "出色的管理者，善于管理人和事"},
    "ESFJ": {"name": "执政官", "desc": "热心、善于合作，渴望和谐的人际关系"},
    "ISTP": {"name": "鉴赏家", "desc": "大胆、实际的实验者，善于使用各种工具"},
    "ISFP": {"name": "探险家", "desc": "灵活、有魅力的艺术家，随时准备探索新事物"},
    "ESTP": {"name": "企业家", "desc": "聪明、精力充沛，善于感知，真正享受生活边缘"},
    "ESFP": {"name": "表演者", "desc": "自发、精力充沛的娱乐者，让生活永远不无聊"},
}

# ==================== 霍兰德测试题目 ====================
# 30道题目，覆盖6种类型：R(现实型)、I(研究型)、A(艺术型)、S(社会型)、E(企业型)、C(常规型)
# 每种类型5道题，选择"是"得该类型分数，选择"否"得0分

HOLLAND_QUESTIONS = [
    # R - 现实型 (Realistic) - 5题
    {"id": 1, "text": "我喜欢使用工具或机械进行操作和修理工作", "type": "R"},
    {"id": 2, "text": "我擅长动手制作或修理物品", "type": "R"},
    {"id": 3, "text": "我更喜欢在户外工作而不是在办公室", "type": "R"},
    {"id": 4, "text": "我对汽车、电子设备或机械原理感兴趣", "type": "R"},
    {"id": 5, "text": "我喜欢从事需要体力和技巧的工作", "type": "R"},
    
    # I - 研究型 (Investigative) - 5题
    {"id": 6, "text": "我喜欢分析和研究复杂的问题", "type": "I"},
    {"id": 7, "text": "我对科学发现和技术创新感兴趣", "type": "I"},
    {"id": 8, "text": "我喜欢阅读专业书籍或学术文章", "type": "I"},
    {"id": 9, "text": "我擅长逻辑推理和数据分析", "type": "I"},
    {"id": 10, "text": "我喜欢探索未知领域和解决难题", "type": "I"},
    
    # A - 艺术型 (Artistic) - 5题
    {"id": 11, "text": "我喜欢创作艺术作品（绘画、音乐、写作等）", "type": "A"},
    {"id": 12, "text": "我对艺术展览、音乐会或文学作品感兴趣", "type": "A"},
    {"id": 13, "text": "我喜欢表达自己的想法和情感", "type": "A"},
    {"id": 14, "text": "我擅长想象和创新，喜欢非传统的工作方式", "type": "A"},
    {"id": 15, "text": "我喜欢自由发挥，不喜欢严格的规则和程序", "type": "A"},
    
    # S - 社会型 (Social) - 5题
    {"id": 16, "text": "我喜欢帮助他人解决问题", "type": "S"},
    {"id": 17, "text": "我擅长倾听和与人沟通", "type": "S"},
    {"id": 18, "text": "我对教育、咨询或社会工作感兴趣", "type": "S"},
    {"id": 19, "text": "我喜欢团队合作和集体活动", "type": "S"},
    {"id": 20, "text": "我关心他人的感受和福祉", "type": "S"},
    
    # E - 企业型 (Enterprising) - 5题
    {"id": 21, "text": "我喜欢领导和管理他人", "type": "E"},
    {"id": 22, "text": "我擅长说服和影响他人", "type": "E"},
    {"id": 23, "text": "我对商业、销售或创业感兴趣", "type": "E"},
    {"id": 24, "text": "我喜欢竞争和追求成功", "type": "E"},
    {"id": 25, "text": "我善于制定计划和组织活动", "type": "E"},
    
    # C - 常规型 (Conventional) - 5题
    {"id": 26, "text": "我喜欢有条理、有规则的工作", "type": "C"},
    {"id": 27, "text": "我擅长处理数据和文件管理", "type": "C"},
    {"id": 28, "text": "我对会计、行政或办公室工作感兴趣", "type": "C"},
    {"id": 29, "text": "我喜欢按照既定的程序和方法工作", "type": "C"},
    {"id": 30, "text": "我注重细节和准确性", "type": "C"},
]

# 霍兰德类型描述
HOLLAND_DESCRIPTIONS = {
    "R": {"name": "现实型", "desc": "喜欢使用工具、机器，擅长动手操作，务实稳重"},
    "I": {"name": "研究型", "desc": "喜欢分析、研究，擅长逻辑思考，追求知识"},
    "A": {"name": "艺术型", "desc": "喜欢创作、表达，富有想象力和创造力"},
    "S": {"name": "社会型", "desc": "喜欢帮助他人，擅长沟通，富有同理心"},
    "E": {"name": "企业型", "desc": "喜欢领导、管理，擅长说服，追求成就"},
    "C": {"name": "常规型", "desc": "喜欢有序、规则，擅长数据处理，注重细节"},
}


def home_page(request):
    """首页 - 选择测试类型"""
    return render(request, 'sorting_hat/home.html')


def mbti_test(request):
    """MBTI测试页面 - 30道题目"""
    if request.method == 'POST':
        # 计算MBTI结果
        scores = {'E': 0, 'I': 0, 'S': 0, 'N': 0, 'T': 0, 'F': 0, 'J': 0, 'P': 0}
        
        for question in MBTI_QUESTIONS:
            answer = request.POST.get(f'q{question["id"]}', '')
            if answer == 'A':
                if question['dimension'] == 'EI':
                    if question['a_value'] == 'E':
                        scores['E'] += 1
                    else:
                        scores['I'] += 1
                elif question['dimension'] == 'SN':
                    if question['a_value'] == 'S':
                        scores['S'] += 1
                    else:
                        scores['N'] += 1
                elif question['dimension'] == 'TF':
                    if question['a_value'] == 'T':
                        scores['T'] += 1
                    else:
                        scores['F'] += 1
                elif question['dimension'] == 'JP':
                    if question['a_value'] == 'J':
                        scores['J'] += 1
                    else:
                        scores['P'] += 1
            elif answer == 'B':
                # 选择B则得分给另一个维度
                if question['dimension'] == 'EI':
                    if question['a_value'] == 'E':
                        scores['I'] += 1
                    else:
                        scores['E'] += 1
                elif question['dimension'] == 'SN':
                    if question['a_value'] == 'S':
                        scores['N'] += 1
                    else:
                        scores['S'] += 1
                elif question['dimension'] == 'TF':
                    if question['a_value'] == 'T':
                        scores['F'] += 1
                    else:
                        scores['T'] += 1
                elif question['dimension'] == 'JP':
                    if question['a_value'] == 'J':
                        scores['P'] += 1
                    else:
                        scores['J'] += 1
        
        # 确定MBTI类型
        mbti_type = ''
        mbti_type += 'E' if scores['E'] >= scores['I'] else 'I'
        mbti_type += 'S' if scores['S'] >= scores['N'] else 'N'
        mbti_type += 'T' if scores['T'] >= scores['F'] else 'F'
        mbti_type += 'J' if scores['J'] >= scores['P'] else 'P'
        
        # 保存结果到session
        request.session['mbti'] = mbti_type
        request.session['mbti_scores'] = scores
        request.session['mbti_desc'] = MBTI_DESCRIPTIONS.get(mbti_type, {"name": "未知", "desc": ""})
        
        messages.success(request, f'MBTI测试完成！你的类型是：{mbti_type}')
        return redirect('holland_test')
    
    return render(request, 'sorting_hat/mbti_test.html', {
        'questions': MBTI_QUESTIONS,
        'total': len(MBTI_QUESTIONS)
    })


def holland_test(request):
    """霍兰德测试页面 - 30道题目"""
    if request.method == 'POST':
        # 计算霍兰德结果
        scores = {'R': 0, 'I': 0, 'A': 0, 'S': 0, 'E': 0, 'C': 0}
        
        for question in HOLLAND_QUESTIONS:
            answer = request.POST.get(f'q{question["id"]}', '')
            if answer == 'yes':
                scores[question['type']] += 1
        
        # 排序得到霍兰德代码（前三项）
        sorted_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        holland_code = ''.join([t[0] for t in sorted_types[:3]])
        
        # 保存结果到session
        request.session['holland'] = holland_code
        request.session['holland_scores'] = scores
        
        # 获取前三项类型描述
        top_types = [HOLLAND_DESCRIPTIONS.get(t[0], {"name": "未知", "desc": ""}) for t in sorted_types[:3]]
        request.session['holland_types_desc'] = [
            {"code": sorted_types[0][0], "name": top_types[0]["name"], "desc": top_types[0]["desc"], "score": sorted_types[0][1]},
            {"code": sorted_types[1][0], "name": top_types[1]["name"], "desc": top_types[1]["desc"], "score": sorted_types[1][1]},
            {"code": sorted_types[2][0], "name": top_types[2]["name"], "desc": top_types[2]["desc"], "score": sorted_types[2][1]},
        ]
        
        messages.success(request, f'霍兰德测试完成！你的代码是：{holland_code}')
        return redirect('profile')
    
    return render(request, 'sorting_hat/holland_test.html', {
        'questions': HOLLAND_QUESTIONS,
        'total': len(HOLLAND_QUESTIONS)
    })


def profile_page(request):
    """画像页面 - 个人画像"""
    if request.method == 'POST':
        score = request.POST.get('score')
        subject = request.POST.get('subject')
        interest = request.POST.get('interest')
        request.session['score'] = score
        request.session['subject'] = subject
        request.session['interest'] = interest
        messages.success(request, '个人画像已生成！')
        return redirect('recommend')
    
    mbti = request.session.get('mbti', '')
    mbti_desc = request.session.get('mbti_desc', {"name": "", "desc": ""})
    holland = request.session.get('holland', '')
    holland_types = request.session.get('holland_types_desc', [])
    
    return render(request, 'sorting_hat/profile.html', {
        'mbti': mbti,
        'mbti_name': mbti_desc.get('name', ''),
        'mbti_desc_text': mbti_desc.get('desc', ''),
        'holland': holland,
        'holland_types': holland_types,
    })


def recommend_page(request):
    """推荐页面 - 推荐结果"""
    if request.method == 'POST':
        messages.success(request, '推荐已生成！')
        return redirect('game')
    
    context = {
        'mbti': request.session.get('mbti', ''),
        'mbti_desc': request.session.get('mbti_desc', {"name": "", "desc": ""}),
        'holland': request.session.get('holland', ''),
        'holland_types': request.session.get('holland_types_desc', []),
        'score': request.session.get('score', ''),
        'subject': request.session.get('subject', ''),
        'interest': request.session.get('interest', ''),
    }
    return render(request, 'sorting_hat/recommend.html', context)


def game_page(request):
    """博弈页面"""
    if request.method == 'POST':
        if 'next' in request.POST:
            return redirect('report')
    return render(request, 'sorting_hat/game.html')


def report_page(request):
    """报告页面"""
    context = {
        'mbti': request.session.get('mbti', ''),
        'mbti_desc': request.session.get('mbti_desc', {"name": "", "desc": ""}),
        'mbti_scores': request.session.get('mbti_scores', {}),
        'holland': request.session.get('holland', ''),
        'holland_types': request.session.get('holland_types_desc', []),
        'holland_scores': request.session.get('holland_scores', {}),
        'score': request.session.get('score', ''),
        'subject': request.session.get('subject', ''),
        'interest': request.session.get('interest', ''),
    }
    return render(request, 'sorting_hat/report.html', context)