#!/usr/bin/env python3
"""
数据分析脚本 - 分析收集的AI论文数据
提取技术趋势、主题演化、地理分布等信息
"""

import sys
import os
import json
import argparse
import logging
from collections import Counter, defaultdict
from datetime import datetime
import re
from typing import List, Dict, Tuple, Any

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *

# 配置日志
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PaperAnalyzer:
    """论文数据分析器"""
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self.output_dir = OUTPUT_DIR
        self.figures_dir = FIGURES_DIR
        
        self.papers_file = os.path.join(self.data_dir, "collected_papers.json")
        self.analysis_file = os.path.join(self.output_dir, "analysis_results.json")
        
        self.papers = []
        
    def load_papers(self) -> bool:
        """加载论文数据"""
        if not os.path.exists(self.papers_file):
            logger.error(f"论文数据文件不存在：{self.papers_file}")
            logger.error("请先运行数据收集脚本：python scripts/collect_papers.py")
            return False
        
        try:
            with open(self.papers_file, 'r', encoding='utf-8') as f:
                self.papers = json.load(f)
            
            # 修复：从published字段提取year
            fixed_count = 0
            for paper in self.papers:
                if not paper.get('year') and paper.get('published'):
                    year_str = paper['published'][:4]
                    if year_str.isdigit():
                        paper['year'] = int(year_str)
                        fixed_count += 1
            
            logger.info(f"成功加载 {len(self.papers)} 篇论文数据（修复了 {fixed_count} 篇的年份信息）")
            return True
        except Exception as e:
            logger.error(f"加载论文数据失败：{e}")
            return False
    
    def preprocess_text(self, text: str) -> str:
        """预处理文本（转小写、去除特殊字符）"""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def extract_keywords(self, text: str, top_n: int = 20) -> List[Tuple[str, int]]:
        """从文本中提取关键词（基于词频）"""
        # 停用词列表
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
                    'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                    'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can',
                    'need', 'dare', 'ought', 'used', 'we', 'you', 'they', 'it', 'he', 'she',
                    'this', 'that', 'these', 'those', 'i', 'me', 'my', 'mine', 'your', 'yours',
                    'his', 'her', 'hers', 'its', 'our', 'ours', 'their', 'theirs', 'what',
                    'which', 'who', 'whom', 'whose', 'how', 'when', 'where', 'why', 'all',
                    'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such',
                    'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
                    'just', 'now', 'also', 'here', 'there', 'then', 'than', 'about', 'between',
                    'through', 'during', 'before', 'after', 'above', 'below', 'between', 'among',
                    'using', 'use', 'used', 'based', 'approach', 'method', 'propose', 'present',
                    'paper', 'study', 'research', 'result', 'results', 'show', 'shows', 'shown',
                    'demonstrate', 'demonstrates', 'demonstrated', 'evaluate', 'evaluates', 'evaluated',
                    'experiment', 'experiments', 'experimental', 'analysis', 'analyze', 'analyzed',
                    'data', 'dataset', 'datasets', 'set', 'sets', 'model', 'models', 'algorithm',
                    'algorithms', 'system', 'systems', 'framework', 'frameworks', 'architecture',
                    'architectures', 'network', 'networks', 'neural', 'deep', 'learning', 'task',
                    'tasks', 'performance', 'accurate', 'accuracy', 'improve', 'improves', 'improved',
                    'state', 'art', 'novel', 'new', 'efficient', 'effective', 'better', 'best',
                    'high', 'low', 'large', 'small', 'different', 'various', 'multiple', 'several',
                    'many', 'much', 'more', 'most', 'least', 'least', 'less', 'few', 'little',
                    'good', 'great', 'important', 'significant', 'considerable', 'substantial',
                    'include', 'including', 'contains', 'contain', 'contained', 'provide', 'provides',
                    'provided', 'offer', 'offers', 'offered', 'support', 'supports', 'supported',
                    'enable', 'enables', 'enabled', 'allow', 'allows', 'allowed', 'help', 'helps',
                    'helped', 'assist', 'assists', 'assisted', 'make', 'makes', 'made', 'create',
                    'creates', 'created', 'develop', 'develops', 'developed', 'build', 'builds',
                    'built', 'design', 'designs', 'designed', 'implement', 'implements', 'implemented',
                    'test', 'tests', 'tested', 'compare', 'compares', 'compared', 'achieve', 'achieves',
                    'achieved', 'obtain', 'obtains', 'obtained', 'generate', 'generates', 'generated',
                    'produce', 'produces', 'produced', 'construct', 'constructs', 'constructed'}
        
        # 分词
        words = text.split()
        
        # 过滤停用词和短词
        filtered_words = [w for w in words if w not in stopwords and len(w) > 2]
        
        # 统计词频
        word_counts = Counter(filtered_words)
        
        # 返回前N个关键词
        return word_counts.most_common(top_n)
    
    def analyze_year_distribution(self) -> Dict[int, int]:
        """分析论文年份分布"""
        year_counts = Counter()
        
        for paper in self.papers:
            year = paper.get('year')
            if year:
                year_counts[year] += 1
        
        logger.info(f"年份分布：{dict(year_counts)}")
        return dict(year_counts)
    
    def analyze_category_distribution(self) -> Dict[str, int]:
        """分析论文类别分布"""
        category_counts = Counter()
        
        for paper in self.papers:
            categories = paper.get('categories', [])
            for cat in categories:
                category_counts[cat] += 1
        
        logger.info(f"类别分布（前10）：{category_counts.most_common(10)}")
        return dict(category_counts)
    
    def analyze_keywords_trend(self) -> Dict[int, List[Tuple[str, int]]]:
        """分析关键词随时间的变化趋势"""
        # 按年份分组
        papers_by_year = defaultdict(list)
        
        for paper in self.papers:
            year = paper.get('year')
            if year:
                papers_by_year[year].append(paper)
        
        # 每年提取关键词
        keywords_by_year = {}
        for year, papers in papers_by_year.items():
            # 合并所有论文的标题和摘要
            all_text = ' '.join([
                p.get('title', '') + ' ' + p.get('summary', '')
                for p in papers
            ])
            
            # 提取关键词
            keywords = self.extract_keywords(all_text, top_n=30)
            keywords_by_year[year] = keywords
            
            logger.info(f"{year}年关键词（前10）：{keywords[:10]}")
        
        return keywords_by_year
    
    def analyze_geo_distribution(self) -> Dict[str, int]:
        """分析论文的地理分布（基于作者机构）"""
        # 注意：ArXiv论文不一定有机构信息，这里尝试从摘要或作者信息推断
        # 简化处理：统计常见的国家/地区关键词
        
        country_keywords = {
            'USA': ['united states', 'usa', 'us ', 'american', 'stanford', 'mit', 'berkeley', 'cmu', 'princeton'],
            'China': ['china', 'chinese', 'beijing', 'shanghai', 'tsinghua', 'peking', 'zhejiang', 'tencent', 'alibaba', 'baidu'],
            'UK': ['united kingdom', 'uk ', 'british', 'oxford', 'cambridge', 'imperial', 'edinburgh'],
            'Germany': ['germany', 'german', 'max planck', 'munich', 'berlin', 'frankfurt'],
            'Canada': ['canada', 'canadian', 'toronto', 'montreal', 'waterloo', 'ubc'],
            'Japan': ['japan', 'japanese', 'tokyo', 'kyoto', 'osaka'],
            'France': ['france', 'french', 'paris', 'inria', 'ens '],
            'Australia': ['australia', 'australian', 'sydney', 'melbourne', 'anu'],
            'India': ['india', 'indian', 'iit ', 'iisc', 'bangalore', 'mumbai'],
            'Singapore': ['singapore', 'nus', 'ntu'],
            'South Korea': ['korea', 'korean', 'seoul', 'kaist'],
            'Israel': ['israel', 'israeli', 'technion', 'weizmann', 'tel aviv'],
            'Europe': ['europe', 'european', 'eu '],
        }
        
        country_counts = Counter()
        
        for paper in self.papers:
            text = paper.get('title', '') + ' ' + paper.get('summary', '')
            text_lower = text.lower()
            
            # 检查每个国家关键词
            matched = False
            for country, keywords in country_keywords.items():
                if any(kw in text_lower for kw in keywords):
                    country_counts[country] += 1
                    matched = True
                    break  # 只算第一个匹配的国家
            
            if not matched:
                country_counts['Unknown/Other'] += 1
        
        logger.info(f"地理分布（前10）：{country_counts.most_common(10)}")
        return dict(country_counts)
    
    def analyze_tech_trends(self) -> Dict[str, Any]:
        """分析技术趋势（基于关键词共现）"""
        # 定义技术主题关键词
        tech_topics = {
            'Large Language Models': ['llm', 'large language model', 'gpt', 'bert', 'transformer', 'attention'],
            'Computer Vision': ['computer vision', 'image', 'visual', 'cnn', 'convolutional', 'object detection'],
            'Reinforcement Learning': ['reinforcement learning', 'rl', 'q-learning', 'policy', 'reward'],
            'Generative AI': ['generative', 'gan', 'vae', 'diffusion', 'stable diffusion', 'midjourney'],
            'Multimodal AI': ['multimodal', 'clip', 'image-text', 'vision-language', 'audio-visual'],
            'Embodied AI': ['embodied', 'robot', 'robotics', 'navigation', 'manipulation'],
            'AI Safety': ['safety', 'alignment', 'interpretability', 'explainability', 'robustness'],
            'AI Ethics': ['ethics', 'fairness', 'bias', 'transparency', 'accountability'],
            'Edge AI': ['edge', 'mobile', 'iot', 'embedded', 'on-device'],
            'Federated Learning': ['federated', 'privacy-preserving', 'distributed learning'],
        }
        
        topic_counts = defaultdict(lambda: defaultdict(int))
        
        for paper in self.papers:
            year = paper.get('year', 'Unknown')
            text = (paper.get('title', '') + ' ' + paper.get('summary', '')).lower()
            
            for topic, keywords in tech_topics.items():
                if any(kw in text for kw in keywords):
                    topic_counts[year][topic] += 1
        
        # 转换为普通字典
        result = {}
        for year, topics in topic_counts.items():
            result[year] = dict(topics)
        
        logger.info(f"技术趋势分析完成，共 {len(result)} 个年份")
        return result
    
    def generate_visualizations(self, analysis_results: Dict) -> None:
        """生成数据可视化图表（保存为JSON，供后续渲染）"""
        # 这里只保存数据，实际图表生成在write_review.py中处理
        logger.info("跳过可视化生成（将在综述撰写阶段处理）")
        pass
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """运行完整的数据分析流程"""
        logger.info("=" * 60)
        logger.info("开始数据分析")
        logger.info("=" * 60)
        
        # 1. 加载数据
        if not self.load_papers():
            return {}
        
        # 2. 年份分布
        logger.info("-" * 60)
        logger.info("分析1/6：年份分布")
        logger.info("-" * 60)
        year_dist = self.analyze_year_distribution()
        
        # 3. 类别分布
        logger.info("-" * 60)
        logger.info("分析2/6：类别分布")
        logger.info("-" * 60)
        category_dist = self.analyze_category_distribution()
        
        # 4. 关键词趋势
        logger.info("-" * 60)
        logger.info("分析3/6：关键词趋势")
        logger.info("-" * 60)
        keywords_trend = self.analyze_keywords_trend()
        
        # 5. 地理分布
        logger.info("-" * 60)
        logger.info("分析4/6：地理分布")
        logger.info("-" * 60)
        geo_dist = self.analyze_geo_distribution()
        
        # 6. 技术趋势
        logger.info("-" * 60)
        logger.info("分析5/6：技术趋势")
        logger.info("-" * 60)
        tech_trends = self.analyze_tech_trends()
        
        # 7. 生成可视化
        logger.info("-" * 60)
        logger.info("分析6/6：生成可视化")
        logger.info("-" * 60)
        self.generate_visualizations({
            'year_dist': year_dist,
            'category_dist': category_dist,
            'keywords_trend': keywords_trend,
            'geo_dist': geo_dist,
            'tech_trends': tech_trends,
        })
        
        # 汇总结果
        results = {
            'analysis_time': datetime.now().isoformat(),
            'total_papers': len(self.papers),
            'year_distribution': year_dist,
            'category_distribution': category_dist,
            'keywords_trend': {str(k): v for k, v in keywords_trend.items()},  # 年份作为字符串键
            'geo_distribution': geo_dist,
            'tech_trends': tech_trends,
        }
        
        # 保存结果
        os.makedirs(self.output_dir, exist_ok=True)
        with open(self.analysis_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info("=" * 60)
        logger.info(f"数据分析完成！结果已保存：{self.analysis_file}")
        logger.info("=" * 60)
        
        return results


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AI论文数据分析')
    parser.add_argument('--papers-file', type=str, default=None,
                        help='指定论文数据文件（默认：data/collected_papers.json）')
    parser.add_argument('--output-file', type=str, default=None,
                        help='指定分析结果文件（默认：output/analysis_results.json）')
    
    args = parser.parse_args()
    
    # 创建分析器
    analyzer = PaperAnalyzer()
    
    # 如果指定了自定义文件，则覆盖默认值
    if args.papers_file:
        analyzer.papers_file = args.papers_file
    if args.output_file:
        analyzer.analysis_file = args.output_file
    
    # 运行分析
    results = analyzer.run_full_analysis()
    
    if results:
        logger.info("✅ 数据分析成功完成")
        return 0
    else:
        logger.error("❌ 数据分析失败")
        return 1


if __name__ == '__main__':
    exit(main())
