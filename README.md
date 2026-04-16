
# Paper_Agent

Paper_Agent 是一个用于学术论文监控、论文搜索、结构化摘要、架构提取、文献综述生成、论文对比和趋势分析的 Python AI Agent 项目。它被设计为一个可用于面试展示的 Agent 系统，而不仅仅是简单的脚本集合。

默认的生成后端是本地 Ollama，例如 `qwen3:3b`。如果 Ollama、在线 API、PDF 解析或图表提取失败，项目会通过明确的降级机制继续运行。

## 核心功能

- 按订阅关键词进行每日论文监控
- 从 arXiv 和 Semantic Scholar 搜索论文
- 通过论文 ID 或标准化标题进行去重
- 使用 Ollama 和启发式降级机制进行论文摘要
- 在可能的情况下从 PDF 中提取模型概览图
- 当图表提取不稳定时，降级为文本架构摘要
- 生成结构化的文献综述
- 横向对比多篇论文
- 分析跨年份、方法、骨干网络、数据集和指标的研究趋势
- 导出 Markdown 和 JSON 格式的报告
- 使用 APScheduler 调度每日任务

## 架构设计

```text
用户任务
  -> PaperAssistantAgent
  -> IntentRouter（意图路由）
  -> TaskPlanner（任务规划）
  -> Skill Loader（技能加载器）
  -> Services（服务层）
  -> Tools（工具层）
  -> Memory + Storage（记忆与存储）
  -> Markdown / JSON Reports（报告输出）
```

核心类是 [`PaperAssistantAgent`](agent/paper_agent.py)。它接收任务字典，进行意图路由、步骤规划、加载技能 markdown 文件、调用服务和工具、更新记忆，并导出产物。

## 目录结构

```text
Paper_Agent/
├── README.md
├── requirements.txt
├── .env.example
├── main.py
├── config/
│   ├── settings.yaml
│   └── prompts.yaml
├── agent/
│   ├── __init__.py
│   ├── base_agent.py
│   ├── paper_agent.py
│   ├── planner.py
│   ├── router.py
│   ├── memory.py
│   └── scheduler.py
├── skills/
│   ├── search_papers.md
│   ├── summarize_papers.md
│   ├── build_review.md
│   ├── compare_papers.md
│   ├── extract_architecture.md
│   └── trend_analysis.md
├── tools/
│   ├── __init__.py
│   ├── arxiv_tool.py
│   ├── semantic_scholar_tool.py
│   ├── pdf_tool.py
│   ├── figure_tool.py
│   ├── ollama_tool.py
│   └── storage_tool.py
├── services/
│   ├── __init__.py
│   ├── paper_service.py
│   ├── review_service.py
│   └── report_service.py
├── models/
│   ├── __init__.py
│   └── schemas.py
├── data/
│   ├── cache/
│   ├── papers/
│   └── reports/
├── examples/
│   ├── daily_monitor_demo.py
│   ├── search_demo.py
│   ├── review_demo.py
│   └── compare_demo.py
└── tests/
    ├── test_agent.py
    ├── test_router.py
    └── test_tools.py
```

## 安装

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

在 macOS 或 Linux 上：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ollama 配置

从 https://ollama.com 安装 Ollama，然后在本地启动：

```bash
ollama serve
```

拉取默认模型：

```bash
ollama pull qwen3:3b
```

默认配置如下：

```yaml
llm:
  provider: ollama
  base_url: http://localhost:11434
  model: qwen3:3b
```

## 快速开始

运行论文搜索：

```bash
python main.py --intent paper_search --keyword "open-vocabulary object detection" --years 3 --top-k 5
```

生成文献综述：

```bash
python main.py --intent review_generation --keyword "visual grounding" --years 5 --top-k 8
```

运行示例：

```bash
python examples/search_demo.py
python examples/review_demo.py
python examples/compare_demo.py
python examples/daily_monitor_demo.py
```

运行测试：

```bash
pytest
```

## Python API

```python
from agent.paper_agent import PaperAssistantAgent

agent = PaperAssistantAgent(skill_dir="skills")

result = agent.run({
    "intent": "review_generation",
    "keyword": "open-vocabulary object detection",
    "years": 3,
    "top_k": 10,
})

print(result.message)
print(result.artifacts)
```

支持的意图类型：

- `daily_monitor`（每日监控）
- `paper_search`（论文搜索）
- `review_generation`（综述生成）
- `paper_compare`（论文对比）
- `trend_analysis`（趋势分析）

## 输出示例

报告以 Markdown 和 JSON 格式导出到 `data/reports/` 目录。论文报告包含：

- 日期
- 关键词
- 论文标题
- 论文链接
- 来源
- 作者
- 年份
- 摘要
- 亮点
- 方法标签
- 架构图路径或架构文本降级内容

文献综述报告包含：

- 研究背景
- 问题定义
- 技术路线
- 代表性方法
- 数据集和评估指标
- 挑战
- 未来方向
- 参考文献

## 架构图提取

架构图提取采用保守策略：

1. 系统尝试下载并解析 PDF
2. 扫描前几页寻找概览类信号，包括 `overview`、`architecture`、`framework`、`pipeline` 和 `model`
3. 如果找到可能的图表，将提取的图片保存到 `data/papers/figures/` 目录下
4. 如果提取失败，返回包含输入、骨干网络、模块和输出的结构化文本架构摘要

这是一个启发式功能。对于生产环境，建议添加标题检测、布局解析和多模态图表分类。

## 数据源

项目目前支持：

- arXiv API
- Semantic Scholar Graph API

Semantic Scholar 在小规模使用时无需 API 密钥，但可能会受到速率限制。如需使用，可在 `.env` 或 `config/settings.yaml` 中添加 `SEMANTIC_SCHOLAR_API_KEY`。

未来可以通过实现具有相同 `search(...) -> list[Paper]` 行为的新工具来添加更多数据源，例如 ACL Anthology、OpenReview、PubMed 或 DBLP。

## 任务调度

[`DailyMonitorScheduler`](agent/scheduler.py) 封装了 APScheduler。示例：

```python
from agent.paper_agent import PaperAssistantAgent
from agent.scheduler import DailyMonitorScheduler

agent = PaperAssistantAgent(skill_dir="skills")
scheduler = DailyMonitorScheduler(agent)
scheduler.start(["visual grounding", "embodied navigation"], hour=9, minute=0)
```

一次性演示：

```bash
python examples/daily_monitor_demo.py
```

## 扩展思路

- 添加 ACL Anthology 和 OpenReview 数据源
- 使用 SQLite 或 PostgreSQL 存储论文历史
- 添加邮件、Slack 或飞书推送通知
- 通过布局感知的标题匹配改进 PDF 图表提取
- 添加引用图谱分析
- 添加向量数据库记忆以实现长期研究跟踪
- 添加云端 LLM 适配器，同时保持统一的 `OllamaLLM` 风格接口

## 注意事项

由于网络限制、速率限制或元数据不可用，在线 API 可能会失败。演示路径设计为通过模拟和启发式降级机制保持可运行。这使得该仓库在本地面试场景中具有实用性，同时保持架构 ready 以支持更强大的生产级集成。
