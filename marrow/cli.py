import os
import click

@click.group()
def cli():
    """marrow: Team Knowledge Injection Proxy for AI Coding Agents."""
    pass

@cli.command()
def init():
    """Initialize the marrow database."""
    from marrow.config import DB_PATH
    from marrow.database import init_db
    init_db(DB_PATH)
    click.echo(f"Initialized marrow database at {DB_PATH}")

@cli.command()
@click.option("--host", default="127.0.0.1", help="Host to bind the HTTP server to")
@click.option("--port", default=7723, type=int, help="Port to run the HTTP server on")
@click.option("--db-path", help="Path to the SQLite database file")
def start(host, port, db_path):
    """Start the marrow MCP server over HTTP (Streamable) transport."""
    if db_path:
        os.environ["MARROW_DB_PATH"] = db_path
        
    from marrow.config import DB_PATH
    from marrow.database import init_db
    init_db(DB_PATH)
    
    click.echo(f"Starting marrow MCP server over HTTP (Streamable)...")
    click.echo(f"  URL: http://{host}:{port}/mcp")
    click.echo(f"  DB:  {DB_PATH}")
    
    from marrow.mcp_server import run_mcp_server
    run_mcp_server(host=host, port=port)

@cli.command()
@click.argument("content")
@click.option("--author", help="Author of the entry (defaults to git config name or system user)")
def add(content, author):
    """Manually add a knowledge entry to the database."""
    from marrow.config import DB_PATH
    from marrow.database import init_db, add_entry
    from marrow.utils import get_default_author
    init_db(DB_PATH)
    if not author:
        author = get_default_author()
    entry_id = add_entry(DB_PATH, content, author)
    click.echo(f"Successfully added entry #{entry_id} by {author}")

@cli.command(name="list")
def list_cmd():
    """List all knowledge entries in the database."""
    from marrow.config import DB_PATH
    from marrow.database import init_db, list_entries
    init_db(DB_PATH)
    entries = list_entries(DB_PATH)
    if not entries:
        click.echo("No entries found in database.")
        return
    for e in entries:
        click.echo(f"#{e['id']} [{e['created_at'][:10]}] ({e['author']}): {e['content']}")

@cli.command()
@click.argument("query")
@click.option("--limit", default=5, type=int, help="Maximum number of results to display")
def search(query, limit):
    """Search knowledge entries in the database using FTS5 BM25."""
    from marrow.config import DB_PATH
    from marrow.database import init_db, search_entries
    init_db(DB_PATH)
    results = search_entries(DB_PATH, query, limit=limit)
    if not results:
        click.echo("No matching entries found.")
        return
    click.echo(f"Top {len(results)} matches for '{query}':")
    for r in results:
        rank_val = r.get("rank", 0.0)
        click.echo(f"#{r['id']} (rank: {rank_val:.4f}) [{r['created_at'][:10]}] ({r['author']}): {r['content']}")

@cli.command()
@click.argument("entry_id", type=int)
def delete(entry_id):
    """Delete a specific knowledge entry by ID."""
    from marrow.config import DB_PATH
    from marrow.database import init_db, delete_entry
    init_db(DB_PATH)
    success = delete_entry(DB_PATH, entry_id)
    if success:
        click.echo(f"Successfully deleted entry #{entry_id}")
    else:
        click.echo(f"Entry #{entry_id} not found.")

if __name__ == "__main__":
    cli()
