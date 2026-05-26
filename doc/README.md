# 霍格沃兹分业帽 - Django 版本

## 项目说明

这是一个基于 Django 框架的高中生专业选择测评系统，结合霍兰德职业兴趣测试和MBTI人格类型测试，帮助学生：
- 判断适合文科还是理科
- 推荐新高考选科组合
- 匹配大学专业方向
- 提供张雪峰风格的择业建议

## 项目结构

```
huogewozifenyemao/
├── config/              # Django项目配置
│   ├── settings.py      # 项目设置
│   ├── urls.py          # URL路由配置
│   └── wsgi.py
├── assessment/          # 测评应用
│   ├── views.py         # 视图层，处理测试数据
│   ├── models.py        # 数据模型
│   └── apps.py
├── templates/           # 模板文件
│   └── index.html       # 主页面（包含完整JavaScript）
├── manage.py            # Django管理脚本
├── db.sqlite3           # SQLite数据库
└── venv/                # Python虚拟环境
```

## 环境要求

- Python 3.8+
- Django 6.0.5

## 安装与运行

### 1. 激活虚拟环境

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install django
```

### 3. 运行数据库迁移

```bash
python manage.py migrate
```

### 4. 启动开发服务器

```bash
python manage.py runserver
```

服务器将在 `http://localhost:8000` 启动

## API 端点

- `GET /` - 主页面，显示完整的测评应用
- `GET /api/data/` - 获取测评数据的JSON格式（用于API调用）

## 功能特性

### 霍兰德职业兴趣测试
- 30个问题，分为6个类型：R(现实型)、I(研究型)、A(艺术型)、S(社会型)、E(企业型)、C(常规型)
- 支持按页分组显示（每页5题）
- 实时进度条显示答题进度

### MBTI人格类型测试
- 4个维度测试
- 生成完整的MBTI类型代码

### 智能分析引擎
- 根据霍兰德和MBTI结果自动计算文理倾向
- 生成文理分科建议和选科方案
- 推荐TOP 10专业列表
- 提供知名教育博主张雪峰的择业建议

### 响应式设计
- 完全适配移动设备
- 使用CSS变量实现灵活的主题系统
- 流畅的动画和交互体验

## 技术栈

- **后端**：Django 6.0
- **前端**：原生HTML5 + CSS3 + Vanilla JavaScript
- **数据库**：SQLite
- **样式**：CSS Grid + Flexbox

## 测试方法

1. 打开浏览器访问 `http://localhost:8000`
2. 点击"开始测评"
3. 完成30题霍兰德测试
4. 完成4维MBTI测试
5. 查看完整测评报告
6. 可选：重新测试或截图分享

## 数据说明

所有测试数据在服务端定义，包括：
- 霍兰德30个测试问题
- 6种职业兴趣类型配置
- 16种MBTI类型映射
- 张雪峰建议库

## 浏览器兼容性

- Chrome/Edge (推荐)
- Firefox
- Safari
- 移动浏览器

## 注意事项

- 数据不会上传到服务器，完全本地计算
- 当前使用SQLite数据库，不适合生产环境高并发
- 建议配合Nginx/Apache进行生产部署

## 后续扩展建议

1. 添加用户登录系统
2. 保存测评结果到数据库
3. 生成测评历史报告
4. 添加报表导出功能（PDF）
5. 实现多语言支持
6. 添加更多的学科和职业数据库

## 许可证

基于霍兰德RIASEC理论 & MBTI人格类型理论
