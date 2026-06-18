# AI趋势研究项目

基于ArXiv学术论文的AI技术趋势分析与综述撰写工具包

## 📋 项目概述

本项目提供一套完整的工具，用于：
1. **数据收集**：从ArXiv API自动收集2020-2025年AI相关学术论文元数据
2. **数据分析**：分析技术演进趋势、研究热点、地理分布等
3. **综述撰写**：自动生成结构完整的AI趋势综述论文（中文）

### 主要特点

- ✅ **自动化流程**：一键运行完整流程（数据收集→分析→撰写）
- ✅ **断点续传**：数据收集支持中断恢复，无需重新开始
- ✅ **模块化设计**：可单独运行某个阶段，灵活控制
- ✅ **详细日志**：完整的执行日志，便于调试和监控
- ✅ **可配置**：所有参数集中配置，易于调整

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+ 
- 网络连接（访问ArXiv API）
- 磁盘空间：至少1GB（用于存储论文数据）

### 2. 安装依赖

```bash
# 克隆或下载本项目到本地
cd ai_trend_research

# 安装Python依赖（如果需要数据可视化，可选）
pip install requests matplotlib numpy
```

**注意**：核心功能仅需Python标准库，无需额外依赖。`requests`用于更稳定的HTTP请求，`matplotlib`和`numpy`用于数据可视化（可选）。

### 3. 配置参数（可选）

编辑 `config.py` 文件，调整以下参数：

```python
# 收集年份范围
COLLECTION_YEARS = [2020, 2021, 2022, 2023, 2024, 2025]

# 每年最多收集的论文数（概念验证建议500-1000）
MAX_PAPERS_PER_YEAR = 1000

# 批次大小（每次API请求获取的论文数，建议100-500）
BATCH_SIZE = 200
```

### 4. 运行完整流程

```bash
# 运行完整流程：数据收集 → 数据分析 → 综述撰写
python main.py all
```

**预计时间**：
- 收集1000篇/年 × 6年 = 6000篇论文：约2-3小时（受ArXiv API速率限制）
- 数据分析：5-10分钟
- 综述撰写：1-2分钟

## 📖 详细使用说明

### 命令概览

```bash
# 查看帮助
python main.py --help

# 查看配置
python main.py config

# 只运行数据收集
python main.py collect

# 只运行数据分析
python main.py analyze

# 只运行综述撰写
python main.py write

# 运行完整流程
python main.py all
```

### 数据收集阶段 (`collect`)

```bash
# 基本用法
python main.py collect

# 指定年份（只收集2023-2025年）
python main.py collect --years 2023 2024 2025

# 指定每年最多论文数（概念验证用）
python main.py collect --max-per-year 500

# 不从进度恢复，开始新的收集
python main.py collect --no-resume
```

**输出**：
- `data/collection_progress.json` - 收集进度（断点续传用）
- `data/collected_papers.json` - 最终收集的论文数据（去重后）

### 数据分析阶段 (`analyze`)

```bash
# 基本用法（使用默认数据文件）
python main.py analyze

# 指定论文数据文件
python main.py analyze --papers-file data/my_papers.json
```

**输出**：
- `output/analysis_results.json` - 分析结果（JSON格式）
- 控制台输出分析摘要

### 综述撰写阶段 (`write`)

```bash
# 基本用法（使用默认分析结果）
python main.py write

# 指定分析结果文件
python main.py write --analysis-file output/my_analysis.json

# 指定输出文件路径
python main.py write --output-file output/my_review.md
```

**输出**：
- `output/ai_trend_review.md` - 综述论文（Markdown格式）

### 完整流程 (`all`)

```bash
# 基本用法（运行全部三个阶段）
python main.py all

# 跳过数据收集（使用已有数据）
python main.py all --skip-collect

# 跳过数据分析（使用已有分析结果）
python main.py all --skip-analyze

# 跳过综述撰写（只收集和分析数据）
python main.py all --skip-write

# 组合使用
python main.py all --skip-collect --skip-analyze  # 只撰写综述
```

## ⚙️ 配置说明

所有配置参数集中在 `config.py` 文件中，主要配置项：

### 路径配置
```python
PROJECT_ROOT = "..."  # 项目根目录（自动检测）
DATA_DIR = "..."      # 数据存放目录
OUTPUT_DIR = "..."    # 输出文件目录
FIGURES_DIR = "..."   # 图表存放目录
```

### 数据收集配置
```python
COLLECTION_YEARS = [2020, 2021, 2022, 2023, 2024, 2025]  # 收集年份
MAX_PAPERS_PER_YEAR = 1000  # 每年最多论文数
BATCH_SIZE = 200  # 每次API请求批量大小
ARXIV_CATEGORIES = [...]  # ArXiv类别过滤
```

### 数据分析配置
```python
NUM_TOPICS = 10  # 主题建模的主题数
TECH_EVOLUTION_KEYWORDS = [...]  # 技术演进关键词列表
GEO_KEYWORDS = {...}  # 地理分布关键词映射
```

### 综述撰写配置
```python
REVIEW_TITLE = "人工智能技术演进与未来趋势：2020-2025年学术文献综述"
REVIEW_LANGUAGE = "zh"  # 'zh'或'en'
REVIEW_OUTPUT_FORMAT = "markdown"  # 'markdown'或'word'
```

## 📊 输出文件说明

### 数据文件 (`data/`)

- `collected_papers.json` - 收集的论文元数据（主要输出）
  - 格式：JSON数组，每篇论文包含id、title、authors、summary、published、categories、url字段
  - 大小：6000篇论文约10-20MB

- `collection_progress.json` - 收集进度（断点续传用）
  - 格式：JSON对象，记录已收集数量、按年进度、已收集论文列表
  - 注意：此文件可能较大，正常完成后可删除

### 输出文件 (`output/`)

- `analysis_results.json` - 分析结果（主要输出）
  - 格式：JSON对象，包含publication_trends、research_topics、tech_evolution、geographic_distribution等部分
  - 大小：通常1-5MB

- `ai_trend_review.md` - 综述论文（主要输出）
  - 格式：Markdown文档，包含摘要、引言、方法论、分析章节、结论、参考文献
  - 大小：通常50-100KB（约2-5万字）

### 日志文件

- `ai_trend_research.log` - 执行日志
  - 格式：文本文件，记录所有执行过程的详细信息
  - 用途：调试错误、查看进度、性能分析

## 🔧 故障排除

### 问题1：ArXiv API连接超时

**症状**：运行`collect`命令时卡住或报错"连接超时"

**原因**：网络连接问题，可能无法访问ArXiv服务器

**解决方案**：
1. 检查网络连接，尝试ping arxiv.org
2. 如果使用代理，配置代理环境变量：
   ```bash
   export HTTP_PROXY=http://proxy.example.com:8080
   export HTTPS_PROXY=http://proxy.example.com:8080
   ```
3. 增加超时时间：编辑`scripts/collect_papers.py`，修改`urllib.request.urlopen`的timeout参数

### 问题2：收集的论文数量太少

**症状**：收集完成后，`collected_papers.json`中只有很少的论文

**原因**：
1. 年份范围设置过小
2. ArXiv类别过滤太严格
3. API请求被限制（速率限制）

**解决方案**：
1. 扩大年份范围：修改`config.py`中的`COLLECTION_YEARS`
2. 增加类别：修改`config.py`中的`ARXIV_CATEGORIES`，添加更多类别
3. 增加等待时间：修改`config.py`中的`ARXIV_RATE_LIMIT`（默认3秒）

### 问题3：数据分析阶段报错

**症状**：运行`analyze`命令时报错

**原因**：
1. `collected_papers.json`文件不存在或格式错误
2. 内存不足（论文数量过多）

**解决方案**：
1. 检查数据文件：确保已成功运行`collect`阶段
2. 减少论文数量：修改`config.py`中的`MAX_PAPERS_PER_YEAR`，重新收集
3. 分批分析：将论文数据分割为多个文件，分别分析

### 问题4：综述论文内容质量不高

**症状**：生成的`ai_trend_review.md`内容空洞、重复或错误

**原因**：自动生成的内容基于模板和简单分析，缺乏深度

**解决方案**：
1. **人工编辑**：将生成的Markdown作为初稿，进行人工润色和补充
2. **调整配置**：修改`config.py`中的分析参数，获得更好的分析结果
3. **使用真实数据**：确保数据收集阶段获取了足够多的高质量论文

### 问题5：中文字符显示乱码

**症状**：输出的中文内容显示为乱码

**原因**：文件编码问题

**解决方案**：
1. 确保使用支持UTF-8的文本编辑器（如VS Code、Notepad++）
2. 转换文件编码：使用`iconv`或Python脚本转换
3. 在Windows上，尝试使用PowerShell而不是cmd

## 📚 项目结构

```
ai_trend_research/
├── config.py              # 配置文件（集中管理所有参数）
├── main.py                # 主控制脚本（统一入口）
├── scripts/               # 脚本目录
│   ├── collect_papers.py  # 数据收集脚本
│   ├── analyze_papers.py  # 数据分析脚本
│   └── write_review.py   # 综述撰写脚本
├── data/                  # 数据目录（自动创建）
│   ├── collected_papers.json      # 收集的论文数据
│   └── collection_progress.json  # 收集进度
├── output/                # 输出目录（自动创建）
│   ├── analysis_results.json     # 分析结果
│   └── ai_trend_review.md      # 综述论文
├── figures/               # 图表目录（自动创建）
├── README.md              # 本说明文档
└── ai_trend_research.log  # 执行日志（自动创建）
```

## 🎯 使用场景

### 场景1：快速概念验证

**目标**：快速验证整个流程是否可行

**步骤**：
```bash
# 1. 修改配置：只收集2024-2025年，每年100篇
edit config.py
# COLLECTION_YEARS = [2024, 2025]
# MAX_PAPERS_PER_YEAR = 100

# 2. 运行完整流程
python main.py all

# 3. 查看输出
cat output/ai_trend_review.md
```

### 场景2：生产环境完整收集

**目标**：收集大量论文用于正式研究

**步骤**：
```bash
# 1. 修改配置：收集2020-2025年，每年5000篇
edit config.py
# COLLECTION_YEARS = [2020, 2021, 2022, 2023, 2024, 2025]
# MAX_PAPERS_PER_YEAR = 5000

# 2. 运行数据收集（可能需要数小时，可中断后恢复）
python main.py collect

# 3. 运行数据分析和综述撰写
python main.py all --skip-collect
```

### 场景3：只分析已有数据

**目标**：使用之前收集的数据，尝试不同的分析方法

**步骤**：
```bash
# 1. 修改分析配置
edit config.py
# NUM_TOPICS = 20  # 增加主题数

# 2. 只运行数据分析
python main.py analyze

# 3. 查看新分析结果
cat output/analysis_results.json
```

## ⚠️ 注意事项

1. **学术研究用途**：本项目仅供学术研究使用，请遵守ArXiv API使用条款
2. **速率限制**：ArXiv API有速率限制（建议每次请求后等待3秒），本项目已内置等待逻辑
3. **数据质量**：自动收集的数据可能包含噪音，建议人工抽查验证
4. **版权问题**：生成的综述论文仅供参考，引用他人成果时请遵守学术规范
5. **网络依赖**：数据收集阶段需要稳定的网络连接，建议使用有线网络

## 📞 支持与反馈

如有问题或建议，请通过以下方式联系：
- 提交Issue（如果使用Git仓库）
- 联系项目维护者

## 📄 许可证

（请根据实际情况填写许可证信息）

---

**祝研究顺利！** 🎓
