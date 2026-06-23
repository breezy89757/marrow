import sys
from mcp.server.fastmcp import FastMCP
from marrow.config import DB_PATH
from marrow.database import init_db, search_entries, add_entry

mcp = FastMCP("Marrow")

@mcp.tool()
def search_team_knowledge(query: str, limit: int = 3) -> str:
    """Search the team knowledge base for solutions, workarounds, and configuration settings related to the query.
    Use this tool when you encounter errors, setup issues, or want to check if a problem has a known solution in the team memory.
    """
    try:
        init_db(DB_PATH)
        entries = search_entries(DB_PATH, query, limit=limit)
        if not entries:
            return "No matching team knowledge found."
        
        lines = []
        for entry in entries:
            author = entry.get("author", "@unknown")
            created_at = entry.get("created_at", "")[:10]  # YYYY-MM-DD
            lines.append(f"• {entry['content']} ({created_at}, {author})")
        return "\n".join(lines)
    except Exception as e:
        return f"Error searching knowledge: {e}"

@mcp.tool()
def add_team_knowledge(content: str) -> str:
    """Record a new engineering learning, library workaround, or configuration gotcha in the team knowledge base.
    Use this tool when you solve a hard-to-debug issue, set up a corporate environment override, or discover a specific workaround that other agents should know.
    Do NOT record trivial features or general coding tasks (e.g. 'added button', 'binary search').
    """
    try:
        init_db(DB_PATH)
        from marrow.utils import get_default_author
        author = get_default_author()
        
        # Check for duplicates before adding
        existing = search_entries(DB_PATH, content, limit=1)
        if existing and existing[0]["content"].strip().lower() == content.strip().lower():
            return f"Duplicate learning detected, skipping: {content}"
            
        add_entry(DB_PATH, content.strip(), author)
        return f"Successfully saved new knowledge: '{content}' by {author}"
    except Exception as e:
        return f"Error saving knowledge: {e}"

def run_mcp_server(host: str = "127.0.0.1", port: int = 7723):
    import uvicorn
    app = mcp.streamable_http_app()
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run_mcp_server()
