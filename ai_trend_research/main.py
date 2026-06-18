#!/usr/bin/env python3
"""
主控制脚本 - AI趋势研究项目统一入口
协调数据收集、数据分析、综述撰写三个阶段
"""

import sys
import os
import argparse
import logging
import subprocess
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
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


class MainController:
    """主控制器"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.scripts_dir = os.path.join(self.project_root, "scripts")
        
    def run_collect(self, args):
        """运行数据收集阶段"""
        logger.info("=" * 60)
        logger.info("阶段 1/3：数据收集")
        logger.info("=" * 60)
        
        # 构建命令
        cmd = [sys.executable, os.path.join(self.scripts_dir, "collect_papers.py")]
        
        if args.no_resume:
            cmd.append("--no-resume")
        
        if args.years:
            cmd.extend(["--years"] + [str(y) for y in args.years])
        
        if args.max_per_year:
            cmd.extend(["--max-per-year", str(args.max_per_year)])
        
        # 执行命令
        logger.info(f"执行命令：{' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, check=True)
            logger.info("数据收集阶段完成")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"数据收集阶段失败：{e}")
            return False
    
    def run_analyze(self, args):
        """运行数据分析阶段"""
        logger.info("=" * 60)
        logger.info("阶段 2/3：数据分析")
        logger.info("=" * 60)
        
        # 构建命令
        cmd = [sys.executable, os.path.join(self.scripts_dir, "analyze_papers.py")]
        
        if getattr(args, 'papers_file', None):
            cmd.extend(["--papers-file", args.papers_file])
        
        # 执行命令
        logger.info(f"执行命令：{' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, check=True)
            logger.info("数据分析阶段完成")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"数据分析阶段失败：{e}")
            return False
    
    def run_write(self, args):
        """运行综述撰写阶段"""
        logger.info("=" * 60)
        logger.info("阶段 3/3：综述撰写")
        logger.info("=" * 60)
        
        # 构建命令
        cmd = [sys.executable, os.path.join(self.scripts_dir, "write_review.py")]
        
        if getattr(args, 'analysis_file', None):
            cmd.extend(["--analysis-file", args.analysis_file])
        
        if getattr(args, 'output_file', None):
            cmd.extend(["--output-file", args.output_file])
        
        # 执行命令
        logger.info(f"执行命令：{' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, check=True)
            logger.info("综述撰写阶段完成")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"综述撰写阶段失败：{e}")
            return False
    
    def run_all(self, args):
        """运行全部三个阶段"""
        logger.info("=" * 60)
        logger.info("AI趋势研究项目 - 完整流程")
        logger.info("=" * 60)
        logger.info(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        start_time = datetime.now()
        
        # 阶段1：数据收集
        if not args.skip_collect:
            success = self.run_collect(args)
            if not success:
                logger.error("数据收集失败，停止执行")
                return False
        else:
            logger.info("跳过数据收集阶段（--skip-collect）")
        
        # 阶段2：数据分析
        if not args.skip_analyze:
            success = self.run_analyze(args)
            if not success:
                logger.error("数据分析失败，停止执行")
                return False
        else:
            logger.info("跳过数据分析阶段（--skip-analyze）")
        
        # 阶段3：综述撰写
        if not args.skip_write:
            success = self.run_write(args)
            if not success:
                logger.error("综述撰写失败，停止执行")
                return False
        else:
            logger.info("跳过综述撰写阶段（--skip-write）")
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info("=" * 60)
        logger.info("所有阶段完成！")
        logger.info(f"结束时间：{end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"总耗时：{duration}")
        logger.info("=" * 60)
        
        return True
    
    def show_config(self):
        """显示配置信息"""
        from config import print_config_summary
        print_config_summary()
    
    def run(self, args):
        """运行主控制器"""
        if args.command == "collect":
            return self.run_collect(args)
        elif args.command == "analyze":
            return self.run_analyze(args)
        elif args.command == "write":
            return self.run_write(args)
        elif args.command == "all":
            return self.run_all(args)
        elif args.command == "config":
            self.show_config()
            return True
        else:
            logger.error(f"未知命令：{args.command}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='AI趋势研究项目 - 主控制脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法：
  # 运行完整流程（数据收集 → 数据分析 → 综述撰写）
  python main.py all
  
  # 只运行数据收集（每年最多500篇）
  python main.py collect --max-per-year 500
  
  # 只运行数据分析
  python main.py analyze
  
  # 只运行综述撰写
  python main.py write
  
  # 运行完整流程但跳过数据收集（使用已有数据）
  python main.py all --skip-collect
  
  # 查看配置
  python main.py config
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # collect 命令
    collect_parser = subparsers.add_parser('collect', help='运行数据收集阶段')
    collect_parser.add_argument('--no-resume', action='store_true', help='不从进度文件恢复，开始新的收集')
    collect_parser.add_argument('--years', type=int, nargs='+', help='指定收集的年份（默认：2020-2025）')
    collect_parser.add_argument('--max-per-year', type=int, help='每年最多收集的论文数（默认：1000）')
    
    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='运行数据分析阶段')
    analyze_parser.add_argument('--papers-file', type=str, help='指定论文数据文件（默认：data/collected_papers.json）')
    
    # write 命令
    write_parser = subparsers.add_parser('write', help='运行综述撰写阶段')
    write_parser.add_argument('--analysis-file', type=str, help='指定分析结果文件（默认：output/analysis_results.json）')
    write_parser.add_argument('--output-file', type=str, help='指定输出文件路径（默认：output/ai_trend_review.md）')
    
    # all 命令
    all_parser = subparsers.add_parser('all', help='运行完整流程（数据收集 → 数据分析 → 综述撰写）')
    all_parser.add_argument('--no-resume', action='store_true', help='不从进度文件恢复，开始新的收集')
    all_parser.add_argument('--years', type=int, nargs='+', help='指定收集的年份（默认：2020-2025）')
    all_parser.add_argument('--max-per-year', type=int, help='每年最多收集的论文数（默认：1000）')
    all_parser.add_argument('--skip-collect', action='store_true', help='跳过数据收集阶段')
    all_parser.add_argument('--skip-analyze', action='store_true', help='跳过数据分析阶段')
    all_parser.add_argument('--skip-write', action='store_true', help='跳过综述撰写阶段')
    all_parser.add_argument('--papers-file', type=str, help='指定论文数据文件（默认：data/collected_papers.json）')
    all_parser.add_argument('--analysis-file', type=str, help='指定分析结果文件（默认：output/analysis_results.json）')
    all_parser.add_argument('--output-file', type=str, help='指定输出文件路径（默认：output/ai_trend_review.md）')
    
    # config 命令
    config_parser = subparsers.add_parser('config', help='查看配置信息')
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 1
    
    # 创建控制器并运行
    controller = MainController()
    success = controller.run(args)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
