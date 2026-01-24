# ========================================
# 4. scripts/generate_reports.py
# ========================================

"""
Generate Analysis Reports
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from main import QuestionSearchSystem
import json
from datetime import datetime
import argparse


def generate_reports(database_path: str, output_dir: str):
    """Generate analysis reports"""
    system = QuestionSearchSystem(database_path=database_path)
    
    if not system.load_search_index():
        print("Error: Index not found. Run rebuild_index.py first.")
        return
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    stats = system.generate_statistics()
    
    # 1. Generate JSON statistics
    stats_file = output_path / 'statistics.json'
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    print(f"✓ Generated: {stats_file}")
    
    # 2. Generate Markdown report
    md_file = output_path / 'question_analysis.md'
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(generate_markdown_report(stats))
    print(f"✓ Generated: {md_file}")
    
    # 3. Generate HTML report
    html_file = output_path / 'exam_comparison.html'
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(generate_html_report(stats))
    print(f"✓ Generated: {html_file}")


def generate_markdown_report(stats: dict) -> str:
    """Generate Markdown report"""
    report = f"""# COS3701 Question Analysis Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

- **Total Questions**: {stats['total_questions']}
- **Total Exam Papers**: {len(stats['questions_by_file'])}

## Questions by File

| Exam Paper | Question Count |
|------------|----------------|
"""
    
    for filename, count in sorted(stats['questions_by_file'].items()):
        report += f"| {filename} | {count} |\n"
    
    report += "\n## Questions by Type\n\n"
    report += "| Type | Count | Percentage |\n"
    report += "|------|-------|------------|\n"
    
    total = stats['total_questions']
    for q_type, count in sorted(stats['questions_by_type'].items()):
        percentage = (count / total * 100) if total > 0 else 0
        report += f"| {q_type} | {count} | {percentage:.1f}% |\n"
    
    return report


def generate_html_report(stats: dict) -> str:
    """Generate HTML report"""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>COS3701 Exam Comparison</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: #2563eb;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #2563eb;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f9fafb;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: #f3f4f6;
            padding: 20px;
            border-radius: 8px;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #2563eb;
        }}
    </style>
</head>
<body>
    <h1>COS3701 Exam Comparison Report</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">{stats['total_questions']}</div>
            <div>Total Questions</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len(stats['questions_by_file'])}</div>
            <div>Exam Papers</div>
        </div>
    </div>
    
    <h2>Questions by File</h2>
    <table>
        <thead>
            <tr>
                <th>Exam Paper</th>
                <th>Question Count</th>
            </tr>
        </thead>
        <tbody>
"""
    
    for filename, count in sorted(stats['questions_by_file'].items()):
        html += f"            <tr><td>{filename}</td><td>{count}</td></tr>\n"
    
    html += """        </tbody>
    </table>
    
    <h2>Questions by Type</h2>
    <table>
        <thead>
            <tr>
                <th>Type</th>
                <th>Count</th>
                <th>Percentage</th>
            </tr>
        </thead>
        <tbody>
"""
    
    total = stats['total_questions']
    for q_type, count in sorted(stats['questions_by_type'].items()):
        percentage = (count / total * 100) if total > 0 else 0
        html += f"            <tr><td>{q_type}</td><td>{count}</td><td>{percentage:.1f}%</td></tr>\n"
    
    html += """        </tbody>
    </table>
</body>
</html>
"""
    
    return html


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate analysis reports')
    parser.add_argument('--database', default='database',
                       help='Database directory path')
    parser.add_argument('--output', '-o', default='reports',
                       help='Output directory')
    
    args = parser.parse_args()
    
    generate_reports(args.database, args.output)

