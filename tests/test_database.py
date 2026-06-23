import sqlite3
from marrow.database import add_entry, search_entries, list_entries, delete_entry, sanitize_fts_query

def test_add_and_list(temp_db):
    entry_id = add_entry(temp_db, "Forcepoint SSL: set NODE_EXTRA_CA_CERTS", "@alice")
    assert entry_id == 1
    
    entries = list_entries(temp_db)
    assert len(entries) == 1
    assert entries[0]["id"] == 1
    assert entries[0]["content"] == "Forcepoint SSL: set NODE_EXTRA_CA_CERTS"
    assert entries[0]["author"] == "@alice"

def test_search_fts(temp_db):
    add_entry(temp_db, "Forcepoint SSL: set NODE_EXTRA_CA_CERTS to corp cert path", "@alice")
    add_entry(temp_db, "LiteLLM context overflow: add output_key in ADK", "@bob")
    add_entry(temp_db, "React router: use HashRouter for static deployment", "@charlie")
    
    # Search for Forcepoint
    results = search_entries(temp_db, "Forcepoint")
    assert len(results) == 1
    assert "Forcepoint" in results[0]["content"]
    
    # Search for context overflow
    results = search_entries(temp_db, "context overflow")
    assert len(results) == 1
    assert "LiteLLM" in results[0]["content"]
    
    # Search for something non-existent
    results = search_entries(temp_db, "nonexistentword")
    assert len(results) == 0

def test_sanitize_query():
    assert sanitize_fts_query("Forcepoint!") == "Forcepoint"
    assert sanitize_fts_query("LiteLLM & context-overflow") == "LiteLLM OR context OR overflow"
    assert sanitize_fts_query("") == ""

def test_delete(temp_db):
    entry_id = add_entry(temp_db, "To be deleted soon", "@alice")
    entries_before = list_entries(temp_db)
    assert len(entries_before) == 1
    
    # Try deleting it
    deleted = delete_entry(temp_db, entry_id)
    assert deleted is True
    
    entries_after = list_entries(temp_db)
    assert len(entries_after) == 0
    
    # Try searching
    results = search_entries(temp_db, "deleted")
    assert len(results) == 0
