"""
配置文件 - AI趋势研究项目
集中管理所有配置参数
"""

import os

# ==================== 项目路径配置 ====================
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
FIGURES_DIR = os.path.join(PROJECT_ROOT, "figures")

# 确保目录存在
for dir_path in [DATA_DIR, OUTPUT_DIR, FIGURES_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# ==================== ArXiv API配置 ====================
ARXIV_API_URL = "http://export.arxiv.org/api/query"
ARXIV_RATE_LIMIT = 3  # 每次请求后等待秒数（遵守ArXiv API限制）

# ==================== 数据收集配置 ====================
# 收集年份范围
COLLECTION_YEARS = list(range(2020, 2026))  # [2020, 2021, 2022, 2023, 2024, 2025]

# 每年最多收集的论文数（10000篇 ÷ 6年 = 1667篇/年）
MAX_PAPERS_PER_YEAR = 1667

# ArXiv查询类别（AI相关主要类别）
ARXIV_CATEGORIES = [
    "cs.AI",    # Artificial Intelligence
    "cs.LG",    # Machine Learning
    "cs.CL",    # Computation and Language (NLP)
    "cs.CV",    # Computer Vision
    "cs.RO",    # Robotics (具身智能)
    "stat.ML",  # Machine Learning (Statistics)
    "cs.NE",    # Neural and Evolutionary Computing
    "cs.SI",    # Social and Information Networks
]

# 查询语句模板
ARXIV_QUERY_TEMPLATE = " OR ".join([f"cat:{cat}" for cat in ARXIV_CATEGORIES])

# 每次API请求的最大论文数（ArXiv限制为2000，建议设为100-500以避免超时）
BATCH_SIZE = 200

# ==================== 数据分析配置 ====================
# 主题建模参数
NUM_TOPICS = 10  # LDA主题数
NUM_WORDS_PER_TOPIC = 10  # 每个主题显示的关键词数

# 技术演进分析配置
TECH_EVOLUTION_KEYWORDS = [
    "large language model", "LLM", "GPT", "BERT", "transformer",
    "multimodal", "vision-language", "CLIP", "DALL-E",
    "embodied AI", "robot learning", "reinforcement learning",
    "diffusion model", "stable diffusion", "image generation",
    "prompt engineering", "in-context learning", "few-shot",
    "chain-of-thought", "reasoning", "planning",
    "AI ethics", "fairness", "alignment", "safety",
    "federated learning", "privacy-preserving", "differential privacy"
]

# 地理分布分析配置（国家/地区关键词）
GEO_KEYWORDS = {
    "USA": ["USA", "United States", "Stanford", "MIT", "Berkeley", "CMU", "Google", "Microsoft", "OpenAI"],
    "China": ["China", "Chinese", "Tsinghua", "Peking University", "CAS", "Tencent", "Alibaba", "Baidu"],
    "Europe": ["Europe", "UK", "Germany", "France", "Oxford", "Cambridge", "ETH", "Max Planck"],
    "Other": []  # 其他地区
}

# ==================== 综述撰写配置 ====================
# 论文输出配置
REVIEW_TITLE = "人工智能技术演进与未来趋势：2020-2025年学术文献综述"
REVIEW_LANGUAGE = "zh"  # 'zh'为中文，'en'为英文
REVIEW_OUTPUT_FORMAT = "markdown"  # 'markdown' 或 'word'

# 章节配置
REVIEW_SECTIONS = [
    "摘要",
    "1. 引言",
    "2. 研究方法与数据来源",
    "3. 人工智能技术演进分析",
    "4. 行业应用热点与趋势",
    "5. 伦理、安全与监管发展",
    "6. 地理分布与国际合作",
    "7. 讨论与展望",
    "8. 结论",
    "参考文献"
]

# ==================== 日志配置 ====================
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = os.path.join(PROJECT_ROOT, "ai_trend_research.log")

# ==================== 函数：获取配置摘要 ====================
def print_config_summary():
    """打印配置摘要"""
    print("=" * 60)
    print("AI趋势研究项目 - 配置摘要")
    print("=" * 60)
    print(f"\n📁 项目路径：")
    print(f"  根目录：{PROJECT_ROOT}")
    print(f"  数据目录：{DATA_DIR}")
    print(f"  输出目录：{OUTPUT_DIR}")
    print(f"  图表目录：{FIGURES_DIR}")
    
    print(f"\n📊 数据收集配置：")
    print(f"  年份范围：{COLLECTION_YEARS[0]}-{COLLECTION_YEARS[-1]}")
    print(f"  每年最多论文数：{MAX_PAPERS_PER_YEAR}")
    print(f"  查询类别：{', '.join(ARXIV_CATEGORIES)}")
    print(f"  批次大小：{BATCH_SIZE}")
    
    print(f"\n🔍 数据分析配置：")
    print(f"  主题数：{NUM_TOPICS}")
    print(f"  技术演进关键词数：{len(TECH_EVOLUTION_KEYWORDS)}")
    
    print(f"\n📝 综述撰写配置：")
    print(f"  论文标题：{REVIEW_TITLE}")
    print(f"  输出语言：{REVIEW_LANGUAGE}")
    print(f"  输出格式：{REVIEW_OUTPUT_FORMAT}")
    
    print(f"\n⚙️ 其他配置：")
    print(f"  日志级别：{LOG_LEVEL}")
    print(f"  日志文件：{LOG_FILE}")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    print_config_summary()
