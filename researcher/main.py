"""
主程序入口
"""
import argparse
from typing import Optional
from researcher.graph.research_graph import ResearchGraph


class ResearchAgent:
    """文献调研智能体主类"""
    
    def __init__(self, config: Optional[dict] = None):
        """
        初始化调研智能体
        
        Args:
            config: 配置字典
        """
        self.graph = ResearchGraph(config)
    
    def research(self, topic: str, max_papers: int = 10) -> dict:
        """
        执行文献调研
        
        Args:
            topic: 调研主题
            max_papers: 最大论文数量
            
        Returns:
            调研结果字典
        """
        return self.graph.run(topic=topic, max_papers=max_papers)
    
    def generate_report(self, research_result: dict) -> str:
        """
        生成综述报告
        
        Args:
            research_result: 调研结果
            
        Returns:
            生成的报告文本
        """
        return self.graph.generate_report(research_result)


def main():
    """命令行主函数"""
    parser = argparse.ArgumentParser(description="多智能体文献调研系统")
    parser.add_argument(
        "--topic",
        type=str,
        required=True,
        help="调研主题"
    )
    parser.add_argument(
        "--max-papers",
        type=int,
        default=10,
        help="最大论文数量（默认：10）"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./outputs/reports/report.md",
        help="输出文件路径"
    )
    
    args = parser.parse_args()
    
    # 创建智能体并执行调研
    agent = ResearchAgent()
    result = agent.research(topic=args.topic, max_papers=args.max_papers)
    
    # 生成报告
    report = agent.generate_report(result)
    
    # 保存报告
    import os
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"调研完成！报告已保存至: {args.output}")
    return 0


if __name__ == "__main__":
    main()

