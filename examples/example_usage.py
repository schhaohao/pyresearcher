"""
使用示例
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from researcher.main import ResearchAgent


def main():
    """示例：使用研究智能体进行文献调研"""
    
    # 创建智能体
    agent = ResearchAgent()
    
    # 执行调研
    topic = "大语言模型在代码生成中的应用"
    print(f"开始调研主题: {topic}")
    
    result = agent.research(topic=topic, max_papers=5)
    
    print(f"\n找到 {len(result['papers'])} 篇论文")
    print(f"完成分析: {len(result['analyses'])} 篇")
    print(f"完成摘要: {len(result['summaries'])} 篇")
    
    # 生成报告
    if result.get('report'):
        print("\n生成的报告:")
        print(result['report'][:500] + "...")  # 只显示前500字符
        
        # 保存报告
        from researcher.tools.report_tools import save_report
        output_path = save_report(result['report'])
        print(f"\n报告已保存至: {output_path}")
    else:
        report = agent.generate_report(result)
        print("\n生成的报告:")
        print(report[:500] + "...")
        
        from researcher.tools.report_tools import save_report
        output_path = save_report(report)
        print(f"\n报告已保存至: {output_path}")


if __name__ == "__main__":
    main()

