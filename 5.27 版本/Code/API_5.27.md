# 5.27 版本 API 架构概览

本文档汇总 `5.27 版本`（目录：`Code`）中可被前端或第三方调用的接口、路由、请求方式、输入输出与对应视图。

**代码位置**: [Code/assessment/views.py](Code/assessment/views.py)

---

## 接口总表

| 接口名称 | 接口功能 | 请求方式 | 路由 | 输入方式 | 输出方式 | 对应视图 |
| --- | --- | --- | --- | --- | --- | --- |
| `mbti_test` | 处理 MBTI 测评，接收 30 道题的答案 | `POST` | `/mbti/` | 表单字段 `q1`~`q30`（答案：`A`/`B`） | 重定向到下一页，结果存于 session | `views.mbti_test` |
| `holland_test` | 处理霍兰德测评，接收 30 道题的答案 | `POST` | `/holland/` | 表单字段 `q1`~`q30`（答案：`yes` / 空） | 重定向到下一页，结果存于 session | `views.holland_test` |
| `profile_page` | 保存用户资料 | `POST` | `/profile/` | 表单字段：`gaokao_score`, `province`, `subject`, `interests` | 重定向 + Django message | `views.profile_page` |
| `recommend_page` | 生成推荐结果，调用 TOPSIS 和语义匹配算法 | `POST` | `/recommend/` | 基于 session 中已有测评结果和用户资料 | 渲染推荐结果页面 | `views.recommend_page` |
| `game_page` | AHP 游戏式对话优化 | `GET` / `POST` | `/game/` | AJAX 请求：`action=submit_answer` 或 `action=get_question` | JSON（题目或完成状态） | `views.game_page` |
| `report_page` | 查看最终推荐报告 | `GET` | `/report/` | 从 session 读取数据 | 渲染报告页面 | `views.report_page` |
| `get_data` | 返回题库和量表配置 | `GET` | `/api/data/` | 无参数 | JSON：完整题库与配置 | `views.get_data` |

---

## 详细接口说明

### `POST /mbti/`
- 功能：提交 MBTI 测评答案。
- 输入：表单字段 `q1`~`q30`，每题值为 `A` 或 `B`。
- 处理：计算 MBTI 四字母类型，将结果写入 `request.session['mbti']`、`request.session['mbti_scores']`，并尝试保存到数据库。
- 输出：重定向到霍兰德测评页面 `holland_test`。
- 实现位置：`Code/assessment/views.py` 中 `mbti_test`。

### `POST /holland/`
- 功能：提交霍兰德测评答案。
- 输入：表单字段 `q1`~`q30`，答案为 `yes` 或留空。
- 处理：统计六类分数，生成霍兰德三字母代码 `holland_code`，将结果写入 `request.session['holland']` 与 `request.session['holland_scores']`，并尝试保存到数据库。
- 输出：重定向到个人资料页面 `profile_page`。
- 实现位置：`Code/assessment/views.py` 中 `holland_test`。

### `POST /profile/`
- 功能：保存用户资料。
- 输入：表单字段 `gaokao_score`, `province`, `subject`, `interests`，以及可选的单科分数字段。
- 处理：将数据写入 session，并调用 `assessment/db_utils.py` 中的 `update_user` 保存到数据库。
- 输出：重定向到推荐页面 `recommend_page`，同时通过 Django messages 反馈结果。
- 实现位置：`Code/assessment/views.py` 中 `profile_page`。

### `POST /recommend/`
- 功能：生成推荐结果。
- 输入：不直接接收新的测评数据，依赖于 session 中已有的 `mbti`、`holland`、`gaokao_score`、`interests` 等。
- 处理：调用 `Code/assessment/algorithms/topsis.py` 和 `Code/assessment/algorithms/semantic_matching.py`，计算推荐列表并保存到 session 和数据库。
- 输出：渲染 `assessment/recommend.html` 页面，展示推荐结果。
- 实现位置：`Code/assessment/views.py` 中 `recommend_page`。

### `GET/POST /game/`
- 功能：AHP 游戏式对话优化和权重调整。
- 输入：AJAX 请求，JSON body 包含 `action` 字段：
  - `action=get_question`
  - `action=submit_answer`
- 处理：`views.game_page` 使用 `GameEngine` 维护 `request.session['game_engine_state']`，逐题获取下一题或提交答案，完成后计算权重并保存对话日志。
- 输出：JSON 响应，返回当前题目或完成状态。
- 实现位置：`Code/assessment/views.py` 中 `game_page`。

### `GET /report/`
- 功能：查看最终推荐报告。
- 输入：无额外参数，直接从 session 读取数据。
- 处理：将 session 中的测评结果、推荐结果、权重等传入模板。
- 输出：渲染 `assessment/report.html` 页面。
- 实现位置：`Code/assessment/views.py` 中 `report_page`。

### `GET /api/data/`
- 功能：返回题库与量表配置。
- 输入：无参数。
- 输出：JSON 包含 `holland_questions`、`holland_profiles`、`mbti_profiles` 和 `zxf_advice`。
- 实现位置：`Code/assessment/views.py` 中 `get_data`。

---

## 备注
- `/mbti/`, `/holland/`, `/profile/`, `/recommend/`, `/report/` 均为页面型路由，主要通过 template 渲染返回 HTML。
- `/game/` 是唯一一个明确的 AJAX 程序化接口，使用 JSON 请求与响应。
- `/api/data/` 也属于公开 JSON API，用于前端初始化题库与说明数据。
- 目前并无独立 `save_profile`、`recommend_major_career`、`adjust_recommendation` 等函数名，实际接口以路由和 view 为准。

---

## 代码索引
- 页面与接口实现：`Code/assessment/views.py`
- 路由配置：`Code/config/urls.py`
- AHP 游戏引擎：`Code/assessment/algorithms/game_engine.py`
- 推荐算法：`Code/assessment/algorithms/topsis.py`, `Code/assessment/algorithms/semantic_matching.py`

如需，我可以继续生成这份文档的 OpenAPI 风格版本。
