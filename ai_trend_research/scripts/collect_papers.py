#!/usr/bin/env python3
"""
数据收集脚本 - 从ArXiv API收集AI论文元数据
使用requests库（自动走系统代理）+ 日期范围查询
"""

import sys
import os
import time
import json
import argparse
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Any, Optional

# 尝试导入requests，如果失败则提示安装
try:
    import requests
except ImportError:
    print("错误：需要安装requests库")
    print("请运行：pip install requests")
    sys.exit(1)

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


class ArxivCollector:
    """ArXiv论文收集器 - 使用requests + 日期范围查询"""
    
    def __init__(self):
        self.api_url = ARXIV_API_URL
        self.rate_limit = ARXIV_RATE_LIMIT
        self.data_dir = DATA_DIR
        self.progress_file = os.path.join(self.data_dir, "collection_progress.json")
        self.papers_file = os.path.join(self.data_dir, "collected_papers.json")
        
        # 创建session，支持连接复用
        self.session = requests.Session()
        # 设置超时（连接超时10秒，读取超时60秒）
        self.session.timeout = (10, 60)
        
    def build_query(self, year: int) -> str:
        """
        构建ArXiv查询语句
        格式：(cat:cs.AI OR cat:cs.LG) AND submittedDate:[20200101 TO 20201231]
        """
        category_query = " OR ".join([f"cat:{cat}" for cat in ARXIV_CATEGORIES])
        start_date = f"{year}0101"
        end_date = f"{year}1231"
        date_query = f"submittedDate:[{start_date} TO {end_date}]"
        
        # 用括号包裹类别查询，确保逻辑正确
        full_query = f"({category_query}) AND {date_query}"
        return full_query
    
    def load_progress(self) -> Dict[str, Any]:
        """加载收集进度"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    progress = json.load(f)
                logger.info(f"加载进度：已收集 {progress.get('total_collected', 0)} 篇论文")
                return progress
            except Exception as e:
                logger.error(f"加载进度文件失败：{e}")
        
        # 返回默认进度
        return {
            'total_collected': 0,
            'by_year': {str(year): {'collected': 0, 'start': 0} for year in COLLECTION_YEARS},
            'papers': []
        }
    
    def save_progress(self, progress: Dict[str, Any]):
        """保存收集进度"""
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)
            logger.debug(f"进度已保存：{progress['total_collected']} 篇论文")
        except Exception as e:
            logger.error(f"保存进度文件失败：{e}")
    
    def fetch_papers_batch(self, query: str, start: int, max_results: int) -> Optional[List[Dict[str, Any]]]:
        """获取一批论文（使用requests，自动走系统代理）"""
        
        params = {
            'search_query': query,
            'start': start,
            'max_results': max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'ascending'  # 升序：从旧到新
        }
        
        try:
            logger.debug(f"请求API：start={start}, max_results={max_results}")
            response = self.session.get(self.api_url, params=params, timeout=(10, 120))
            response.raise_for_status()  # 检查HTTP错误
            
            data = response.text
            
            # 解析XML
            root = ET.fromstring(data)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            papers = []
            for entry in root.findall('atom:entry', ns):
                paper = self._parse_entry(entry, ns)
                if paper:
                    papers.append(paper)
            
            logger.debug(f"获取到 {len(papers)} 篇论文")
            return papers
            
        except requests.exceptions.ProxyError as e:
            logger.error(f"代理错误：{e}")
            logger.error("提示：检查系统代理设置，或临时关闭代理")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"连接错误：{e}")
            logger.error("提示：检查网络连接，或ArXiv是否可访问")
            return None
        except requests.exceptions.Timeout:
            logger.error(f"请求超时（120秒）")
            return None
        except Exception as e:
            logger.error(f"获取论文批次失败 (start={start})：{e}")
            return None
    
    def _parse_entry(self, entry, ns) -> Optional[Dict[str, Any]]:
        """解析单个论文条目"""
        try:
            paper_id = entry.find('atom:id', ns).text.split('/abs/')[-1]
            title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
            summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
            published = entry.find('atom:published', ns).text
            updated = entry.find('atom:updated', ns)
            updated = updated.text if updated is not None else published
            
            authors = []
            for author in entry.findall('atom:author', ns):
                name_elem = author.find('atom:name', ns)
                if name_elem is not None and name_elem.text:
                    authors.append(name_elem.text)
            
            categories = []
            for category in entry.findall('atom:category', ns):
                term = category.get('term')
                if term:
                    categories.append(term)
            
            # 提取主要类别（arxiv:primary_category）
            primary_category = None
            for cat in entry.findall('arxiv:primary_category', {'arxiv': 'http://arxiv.org/schemas/atom'}):
                primary_category = cat.get('term')
            
            return {
                'id': paper_id,
                'title': title,
                'authors': authors,
                'summary': summary,
                'published': published,
                'updated': updated,
                'categories': categories,
                'primary_category': primary_category,
                'url': f"https://arxiv.org/abs/{paper_id}"
            }
        except Exception as e:
            logger.warning(f"解析论文条目失败：{e}")
            return None
    
    def collect_year(self, year: int, max_papers: int, start_offset: int = 0) -> List[Dict[str, Any]]:
        """收集指定年份的论文（使用日期范围查询，无需过滤）"""
        logger.info(f"开始收集 {year} 年的论文（最多 {max_papers} 篇，起始偏移 {start_offset}）")
        
        query = self.build_query(year)
        logger.info(f"  查询语句：{query[:100]}...")
        
        collected = 0
        start = start_offset
        papers = []
        empty_count = 0  # 连续空返回计数
        max_empty = 3    # 连续3次空返回则停止
        
        while collected < max_papers and empty_count < max_empty:
            remaining = max_papers - collected
            batch_size = min(BATCH_SIZE, remaining)
            
            logger.info(f"  [{year}] 批次：start={start}, batch_size={batch_size}, 已收集={collected}")
            
            batch_papers = self.fetch_papers_batch(query, start, batch_size)
            
            if batch_papers is None:
                logger.error(f"  [{year}] 获取批次失败，等待 {self.rate_limit * 2} 秒后重试...")
                time.sleep(self.rate_limit * 2)
                continue
            
            if not batch_papers:
                empty_count += 1
                logger.info(f"  [{year}] 无更多论文（连续空返回 {empty_count}/{max_empty}）")
                if empty_count >= max_empty:
                    logger.info(f"  [{year}] 连续{max_empty}次无数据，停止收集")
                    break
            else:
                empty_count = 0  # 重置空计数
                # 日期范围查询已经过滤了年份，无需再过滤
                papers.extend(batch_papers)
                collected += len(batch_papers)
                logger.info(f"  [{year}] 本批获取 {len(batch_papers)} 篇，累计 {collected} 篇")
            
            start += batch_size
            
            # 遵守速率限制
            logger.info(f"  [{year}] 等待 {self.rate_limit} 秒...")
            time.sleep(self.rate_limit)
        
        logger.info(f"[{year}] 收集完成：{collected} 篇论文")
        return papers
    
    def run(self, resume: bool = True):
        """运行收集流程"""
        logger.info("=" * 60)
        logger.info("开始AI论文数据收集")
        logger.info("=" * 60)
        
        # 加载进度
        if resume and os.path.exists(self.progress_file):
            progress = self.load_progress()
            logger.info("恢复之前的收集进度")
        else:
            progress = self.load_progress()
            logger.info("开始新的收集任务")
        
        # 收集每一年份的论文
        for year in COLLECTION_YEARS:
            year_str = str(year)
            
            # 检查该年份是否已收集完成
            if progress['by_year'].get(year_str, {}).get('collected', 0) >= MAX_PAPERS_PER_YEAR:
                logger.info(f"[{year}] 已收集完成（{progress['by_year'][year_str]['collected']} 篇），跳过")
                continue
            
            # 获取该年份的进度
            year_progress = progress['by_year'].get(year_str, {'collected': 0, 'start': 0})
            start_offset = year_progress['start']
            
            # 收集该年份的论文
            year_papers = self.collect_year(year, MAX_PAPERS_PER_YEAR - year_progress['collected'], start_offset)
            
            # 更新进度
            progress['papers'].extend(year_papers)
            progress['by_year'][year_str] = {
                'collected': year_progress['collected'] + len(year_papers),
                'start': year_progress['start'] + len(year_papers)
            }
            progress['total_collected'] = len(progress['papers'])
            
            # 保存进度
            self.save_progress(progress)
            logger.info(f"[{year}] 进度已保存：已收集 {progress['by_year'][year_str]['collected']} 篇")
        
        # 去重并保存最终结果
        logger.info("收集完成，去重并保存最终结果...")
        final_papers = self.deduplicate_papers(progress['papers'])
        
        with open(self.papers_file, 'w', encoding='utf-8') as f:
            json.dump(final_papers, f, ensure_ascii=False, indent=2)
        
        logger.info("=" * 60)
        logger.info(f"数据收集完成！")
        logger.info(f"总计收集：{len(final_papers)} 篇论文（去重后）")
        logger.info(f"数据文件：{self.papers_file}")
        logger.info("=" * 60)
        
        # 打印统计信息
        self.print_statistics(final_papers)
    
    def deduplicate_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重论文（基于ID）"""
        seen_ids = set()
        unique_papers = []
        
        for paper in papers:
            if paper['id'] not in seen_ids:
                seen_ids.add(paper['id'])
                unique_papers.append(paper)
        
        logger.info(f"去重：{len(papers)} -> {len(unique_papers)} 篇论文")
        return unique_papers
    
    def print_statistics(self, papers: List[Dict[str, Any]]):
        """打印统计信息"""
        logger.info("\n统计信息：")
        logger.info(f"  总论文数：{len(papers)}")
        
        # 按年份统计
        year_counts = {}
        for paper in papers:
            year = paper['published'][:4]
            year_counts[year] = year_counts.get(year, 0) + 1
        
        logger.info("\n  按年份分布：")
        for year in sorted(year_counts.keys()):
            logger.info(f"    {year}: {year_counts[year]} 篇")
        
        # 按类别统计（前10）
        category_counts = {}
        for paper in papers:
            for cat in paper['categories']:
                category_counts[cat] = category_counts.get(cat, 0) + 1
        
        logger.info("\n  热门类别（前10）：")
        top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for cat, count in top_categories:
            logger.info(f"    {cat}: {count} 篇")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='从ArXiv收集AI论文元数据')
    parser.add_argument('--no-resume', action='store_true', help='不从进度文件恢复，开始新的收集')
    parser.add_argument('--years', type=int, nargs='+', help='指定收集的年份（默认：2020-2025）')
    parser.add_argument('--max-per-year', type=int, help='每年最多收集的论文数（默认：1000）')
    
    args = parser.parse_args()
    
    # 如果指定了年份或最大论文数，临时修改配置
    if args.years:
        global COLLECTION_YEARS, MAX_PAPERS_PER_YEAR
        COLLECTION_YEARS = args.years
        logger.info(f"指定年份：{COLLECTION_YEARS}")
    
    if args.max_per_year:
        MAX_PAPERS_PER_YEAR = args.max_per_year
        logger.info(f"指定每年最多论文数：{MAX_PAPERS_PER_YEAR}")
    
    # 创建收集器并运行
    collector = ArxivCollector()
    collector.run(resume=not args.no_resume)


if __name__ == "__main__":
    main()
