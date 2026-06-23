import pytest
from unittest.mock import patch
from marrow.mcp_server import search_team_knowledge, add_team_knowledge
from marrow.database import init_db, list_entries

def test_search_team_knowledge_empty(temp_db):
    with patch("marrow.mcp_server.DB_PATH", temp_db):
        res = search_team_knowledge("anything")
        assert res == "No matching team knowledge found."

def test_add_and_search_team_knowledge(temp_db):
    with patch("marrow.mcp_server.DB_PATH", temp_db), patch("marrow.utils.get_default_author", return_value="@bob"):
        # Test adding knowledge
        res_add = add_team_knowledge("Forcepoint SSL: set NODE_EXTRA_CA_CERTS to cert path")
        assert "Successfully saved new knowledge" in res_add
        assert "@bob" in res_add
        
        # Test searching knowledge
        res_search = search_team_knowledge("SSL")
        assert "Forcepoint SSL: set NODE_EXTRA_CA_CERTS to cert path" in res_search
        assert "@bob" in res_search

def test_add_duplicate_knowledge(temp_db):
    with patch("marrow.mcp_server.DB_PATH", temp_db), patch("marrow.utils.get_default_author", return_value="@bob"):
        res1 = add_team_knowledge("Forcepoint SSL: set NODE_EXTRA_CA_CERTS to cert path")
        assert "Successfully saved" in res1
        
        res2 = add_team_knowledge("Forcepoint SSL: set NODE_EXTRA_CA_CERTS to cert path")
        assert "Duplicate learning detected" in res2
        
        # Database should only contain 1 entry
        entries = list_entries(temp_db)
        assert len(entries) == 1
