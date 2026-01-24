
# ========================================
# 7. cli.py
# ========================================

"""
Command-line Interface
Enhanced CLI with more options
"""

import click
import sys
from pathlib import Path
from main import QuestionSearchSystem
import json


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """COS3701 Question Search System CLI"""
    pass


@cli.command()
@click.option('--database', default='database', help='Database directory path')
@click.option('--force', is_flag=True, help='Force re-extraction')
def extract(database, force):
    """Extract questions from exam papers"""
    click.echo("Extracting questions from exam papers...")
    
    system = QuestionSearchSystem(database_path=database)
    system.extract_all_questions(force_reextract=force)
    
    click.echo(f"✓ Extracted {len(system.all_questions)} questions")


@cli.command()
@click.option('--database', default='database', help='Database directory path')
def build(database):
    """Build search index"""
    click.echo("Building search index...")
    
    system = QuestionSearchSystem(database_path=database)
    
    # Load questions if not already loaded
    if not system.all_questions:
        system.extract_all_questions()
    
    system.build_search_index()
    
    click.echo("✓ Index built successfully")


@cli.command()
@click.argument('query')
@click.option('--database', default='database', help='Database directory path')
@click.option('--top-k', default=5, help='Number of results')
@click.option('--type', 'search_type', default='semantic', 
              type=click.Choice(['semantic', 'exact', 'typed']))
def search(query, database, top_k, search_type):
    """Search for questions"""
    system = QuestionSearchSystem(database_path=database)
    
    if not system.load_search_index():
        click.echo("Error: Index not found. Run 'build' first.", err=True)
        sys.exit(1)
    
    results = system.search_question(query, top_k=top_k, search_type=search_type)
    
    click.echo(f"\nFound {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        click.echo(f"{i}. {result['question'][:100]}...")
        click.echo(f"   Score: {result.get('combined_score', 0):.1%}")
        click.echo(f"   File: {Path(result['file']).name}")
        click.echo()


@cli.command()
@click.option('--database', default='database', help='Database directory path')
def stats(database):
    """Show database statistics"""
    system = QuestionSearchSystem(database_path=database)
    
    if not system.load_search_index():
        click.echo("Error: Index not found. Run 'build' first.", err=True)
        sys.exit(1)
    
    stats = system.generate_statistics()
    
    click.echo("\n" + "="*50)
    click.echo("Database Statistics")
    click.echo("="*50)
    click.echo(f"\nTotal Questions: {stats['total_questions']}")
    click.echo(f"\nQuestions by File:")
    
    for filename, count in stats['questions_by_file'].items():
        click.echo(f"  - {filename}: {count}")
    
    click.echo(f"\nQuestions by Type:")
    for q_type, count in stats['questions_by_type'].items():
        click.echo(f"  - {q_type}: {count}")
    click.echo()


@cli.command()
@click.option('--database', default='database', help='Database directory path')
def interactive(database):
    """Start interactive search session"""
    system = QuestionSearchSystem(database_path=database)
    system.interactive_search()


@cli.command()
@click.argument('output_file')
@click.option('--database', default='database', help='Database directory path')
@click.option('--format', 'fmt', default='json', 
              type=click.Choice(['json', 'csv']))
def export(output_file, database, fmt):
    """Export all questions to file"""
    system = QuestionSearchSystem(database_path=database)
    
    if not system.load_search_index():
        click.echo("Error: Index not found. Run 'build' first.", err=True)
        sys.exit(1)
    
    if fmt == 'json':
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(system.all_questions, f, indent=2, ensure_ascii=False)
    
    elif fmt == 'csv':
        import csv
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['question', 'file', 'type'])
            writer.writeheader()
            
            for q in system.all_questions:
                writer.writerow({
                    'question': q['question'],
                    'file': q['file'],
                    'type': q.get('type', 'unknown')
                })
    
    click.echo(f"✓ Exported {len(system.all_questions)} questions to {output_file}")


if __name__ == '__main__':
    cli()