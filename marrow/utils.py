import os
import subprocess
import getpass

def get_default_author() -> str:
    author = os.getenv("MARROW_AUTHOR")
    if author:
        return author
        
    # Try git config
    try:
        res = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True,
            text=True,
            check=True,
            timeout=2.0
        )
        name = res.stdout.strip()
        if name:
            return f"@{name}"
    except Exception:
        pass
        
    # Fallback to system user
    try:
        user = getpass.getuser()
        if user:
            return f"@{user}"
    except Exception:
        pass
        
    return "@unknown"
