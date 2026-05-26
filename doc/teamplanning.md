# 霍格沃兹分业帽 · 6人分工明细表

| 人员 | 角色 | 负责模块 | 具体任务 | 代码文件 | 第2天结束前产出 | 第3天结束前产出 | 第4天结束前产出 |
|------|------|----------|----------|----------|------------------|------------------|------------------|
| **钟鑫平** | 数据模型 | `models.py` + 数据库 | 1. 设计UserProfile、AssessmentResult、RecommendationResult、DialogueLog模型<br>2. 运行迁移创建数据库<br>3. 编写数据存取工具函数 | `assessment/models.py`<br>`assessment/db_utils.py` | 完成4个Model定义 | 完成数据库迁移 + 增删改查工具函数 | 与后端联调，确保数据能正确存取 |
| **王琪** | 后端API | `views.py` + `urls.py` | 1. 编写API接口：`/api/submit_holland`、`/api/submit_mbti`、`/api/recommend`、`/api/feedback`<br>2. 串联所有算法模块<br>3. 返回JSON响应 | `assessment/views.py`<br>`assessment/urls.py` | 搭建API骨架（空接口返回假数据） | 完成所有API逻辑，能串联算法模块 | 与前端联调，修复bug |
| **奉乐乐** | 排序算法 | `topsis.py` + `weight_manager.py` | 1. 实现TOPSIS多属性排序算法<br>2. 实现权重归一化和动态调整<br>3. 实现根据霍兰德/MBTI/分数初始化权重 | `assessment/algorithm/topsis.py`<br>`assessment/algorithm/weight_manager.py` | 完成TOPSIS核心函数（能跑通） | 完成权重初始化逻辑（个性化权重） | 单元测试 + 与API集成 |
| **李佳润** | 语义匹配 | `semantic_matcher.py` + `trend_analyzer.py` | 1. 实现词向量/TF-IDF语义匹配（专业↔兴趣）<br>2. 实现热词→专业的前瞻性打分<br>3. 维护热词表更新机制 | `assessment/algorithm/semantic_matcher.py`<br>`assessment/algorithm/trend_analyzer.py` | 完成TF-IDF语义匹配基础版 | 完成热词→专业打分逻辑 | 支持热词表动态加载 |
| **余天骜** | 博弈引擎 | `game_engine.py` | 1. 实现交互式博弈的6-8个二选一问题<br>2. 实现从用户选择反推权重（成对比较）<br>3. 记录对话日志 | `assessment/algorithm/game_engine.py` | 设计6个博弈问题的题库 | 完成博弈逻辑 + 权重反推算法 | 与API集成 + 对话日志存储 |
| **王漪冉** | 前端开发 | `index.html` + `main.js` | 1. 实现4步界面：信息填写→霍兰德测试→MBTI测试→结果展示<br>2. 嵌入博弈问题弹窗<br>3. 调用后端API并渲染结果 | `assessment/templates/assessment/index.html`<br>`assessment/static/js/main.js` | 完成HTML结构 + CSS样式 | 完成霍兰德+MBTI测试题的交互 | 完成所有API对接 + 结果可视化 |

---

## 项目架构图（Django版）

```
huogewozifenyemao/ # Django项目根目录
│
├── config/ # Django配置
│ ├── settings.py
│ └── urls.py
│
├── assessment/ # 主应用（测评+推荐）
│ ├── init.py
│ ├── admin.py
│ ├── apps.py
│ │
│ ├── models.py # 🔴 钟鑫平
│ ├── views.py # 🔴 王琪
│ ├── urls.py # 🔴 王琪
│ │
│ ├── algorithm/ # 算法模块（新建）
│ │ ├── init.py
│ │ ├── topsis.py # 🔴 奉乐乐
│ │ ├── weight_manager.py # 🔴 奉乐乐
│ │ ├── semantic_matcher.py # 🔴 李佳润
│ │ ├── trend_analyzer.py # 🔴 李佳润
│ │ └── game_engine.py # 🔴 余天骜
│ │
│ ├── static/ # 静态文件
│ │ ├── css/
│ │ │ └── style.css
│ │ └── js/
│ │ └── main.js # 🔴 王漪冉
│ │
│ └── templates/ # 模板文件
│ └── assessment/
│ └── index.html # 🔴 王漪冉
│
├── data/ # 数据文件（新建）
│ ├── majors.json # 专业库
│ ├── hotwords.json # 行业热词表
│ └── mapping_rules.json # 霍兰德+MBTI→专业映射
│
├── manage.py
└── requirements.txt
```

---

## 联调依赖关系

```
┌─────────────────────────────────────────────────────────┐
│ 王琪（后端API） │
│ 串联所有模块 │
└───────────────┬─────────────────┬───────────────────────┘
│ │
┌───────────────┼─────────────────┼───────────────────────┐
│ │ │ │
▼ ▼ ▼ ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ 钟鑫平 │ │ 奉乐乐 │ │ 李佳润 │ │ 余天骜 │
│ models.py │ │ topsis.py │ │semantic匹配 │ │ game_engine │
│ 提供数据存取 │ │ 提供排序 │ │ 提供匹配 │ │ 提供博弈 │
└───────┬───────┘ └───────┬───────┘ └───────┬───────┘ └───────┬───────┘
│ │ │ │
└─────────────────┴─────────────────┴───────────────────────┘
│
▼
┌───────────────────────┐
│ 王漪冉（前端） │
│ 调用API展示结果 │
└───────────────────────┘
```