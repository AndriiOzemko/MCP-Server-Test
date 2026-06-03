# MCP Notes Server

A Model Context Protocol (MCP) server for managing notes with full CRUD operations, tagging, and search capabilities.

## Features

- ✅ Create, read, update, and delete notes
- ✅ Tag-based organization and filtering
- ✅ Full-text search across notes
- ✅ Persistent storage (JSON file-based)
- ✅ Resource exposure via MCP protocol
- ✅ Compatible with Claude Desktop

## Setup Instructions

### Prerequisites

- Python 3.12 or higher
- pip package manager

### Installation

1. **Clone or download this repository**
   ```bash
   cd "d:\Projects\AI Engineering course\MCP Server"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Claude Desktop**
   
   Edit your Claude Desktop configuration file:
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

   Add the notes server configuration:
   ```json
   {
     "mcpServers": {
       "notes": {
         "command": "python",
         "args": [
           "d:\\Projects\\AI Engineering course\\MCP Server\\server.py"
         ]
       }
     }
   }
   ```
   
   **Note**: Adjust the path to match your actual installation directory.

4. **Restart Claude Desktop**
   
   After updating the configuration, completely quit and restart Claude Desktop for the changes to take effect.

## Available Tools

### 1. `create_note`
Creates a new note with content and optional metadata.

**Parameters:**
- `content` (required): The content of the note
- `title` (optional): Title for the note (defaults to first line of content)
- `tags` (optional): Array of tags for categorization

**Example:**
```json
{
  "content": "Remember to buy groceries tomorrow",
  "title": "Shopping Reminder",
  "tags": ["personal", "todo"]
}
```

### 2. `list_notes`
Lists all notes with optional filtering and pagination.

**Parameters:**
- `tag` (optional): Filter notes by specific tag
- `limit` (optional): Maximum number of notes to return

**Example:**
```json
{
  "tag": "work",
  "limit": 5
}
```

### 3. `get_note`
Retrieves the full content of a specific note.

**Parameters:**
- `note_id` (required): The ID of the note to retrieve

**Example:**
```json
{
  "note_id": "1"
}
```

### 4. `update_note`
Updates an existing note's content, title, or tags.

**Parameters:**
- `note_id` (required): The ID of the note to update
- `content` (optional): New content for the note
- `title` (optional): New title for the note
- `tags` (optional): New list of tags

**Example:**
```json
{
  "note_id": "1",
  "title": "Updated Title",
  "tags": ["work", "important"]
}
```

### 5. `delete_note`
Deletes a note by ID.

**Parameters:**
- `note_id` (required): The ID of the note to delete

**Example:**
```json
{
  "note_id": "1"
}
```

### 6. `search_notes`
Searches notes by keyword in title or content.

**Parameters:**
- `query` (required): Search keyword or phrase
- `tag` (optional): Optional tag filter to narrow search

**Example:**
```json
{
  "query": "meeting",
  "tag": "work"
}
```

## Available Resources

### 1. `note://{note_id}`
Provides direct access to individual notes via URI.

**Example:** `note://1`

### 2. `notes://list`
Provides a JSON list of all notes with metadata.

**Example:** `notes://list`

## Example Dialogues

### Example 1: Creating and Managing a Todo List

**User:** Create a note for my grocery shopping list with items: milk, eggs, bread, and cheese.

**Claude:** I'll create a shopping list note for you.

*[Uses create_note tool with content and tags]*

**Response:** ✓ Note created successfully!
- ID: 1
- Title: Grocery Shopping List
- Tags: shopping, personal

---

**User:** Show me all my notes.

**Claude:** Let me list all your notes.

*[Uses list_notes tool]*

**Response:** Found 1 note(s):
- ID: 1 | Grocery Shopping List [shopping, personal]
  Items needed: milk, eggs, bread, and cheese

---

**User:** Add apples to my shopping list.

**Claude:** I'll update your shopping list to include apples.

*[Uses update_note tool with note_id: "1"]*

**Response:** ✓ Note 1 updated successfully!
Updated fields: content

### Example 2: Work Notes and Search

**User:** Create a note about tomorrow's team meeting at 10 AM. Tag it as work and important.

**Claude:** I'll create a note for your team meeting.

*[Uses create_note tool]*

**Response:** ✓ Note created successfully!
- ID: 2
- Title: Team Meeting - Tomorrow at 10 AM
- Tags: work, important

---

**User:** Create another note: "Review Q4 budget proposal before Friday meeting" with work and finance tags.

**Claude:** Creating your budget review note.

*[Uses create_note tool]*

**Response:** ✓ Note created successfully!
- ID: 3
- Title: Review Q4 budget proposal before Friday meeting
- Tags: work, finance

---

**User:** Find all my notes about meetings.

**Claude:** I'll search for notes containing "meeting".

*[Uses search_notes tool with query: "meeting"]*

**Response:** Found 2 note(s) matching 'meeting':
- ID: 2 | Team Meeting - Tomorrow at 10 AM [work, important]
  Discuss project updates and timeline...
- ID: 3 | Review Q4 budget proposal before Friday meeting [work, finance]
  Review Q4 budget proposal before Friday meeting

### Example 3: Organizing with Tags

**User:** Show me all my work-related notes.

**Claude:** I'll list all notes tagged with "work".

*[Uses list_notes tool with tag: "work"]*

**Response:** Found 2 note(s):
- ID: 2 | Team Meeting - Tomorrow at 10 AM [work, important]
  Discuss project updates and timeline...
- ID: 3 | Review Q4 budget proposal before Friday meeting [work, finance]
  Review Q4 budget proposal before Friday meeting

---

**User:** Delete the meeting note, I don't need it anymore.

**Claude:** I'll delete note ID 2.

*[Uses delete_note tool with note_id: "2"]*

**Response:** ✓ Note 'Team Meeting - Tomorrow at 10 AM' (ID: 2) deleted successfully.

---

**User:** What notes do I still have?

**Claude:** Let me show you your remaining notes.

*[Uses list_notes tool]*

**Response:** Found 2 note(s):
- ID: 1 | Grocery Shopping List [shopping, personal]
  Items needed: milk, eggs, bread, cheese, and apples
- ID: 3 | Review Q4 budget proposal before Friday meeting [work, finance]
  Review Q4 budget proposal before Friday meeting

## Known Limitations

1. **Single-User Design**: The server stores notes in a local JSON file without user authentication or multi-user support.

2. **No Concurrent Access Protection**: Multiple simultaneous operations may lead to race conditions. The server is designed for single-client (Claude Desktop) usage.

3. **Limited Storage Capacity**: Uses JSON file storage which may become slow with thousands of notes. Not suitable for large-scale note databases.

4. **No Attachment Support**: Currently only supports text content. Images, files, or rich media are not supported.

5. **Basic Search**: Search is case-insensitive substring matching. No support for regex, fuzzy matching, or advanced query syntax.

6. **No Note History**: Updates overwrite existing content without maintaining version history or undo capability.

7. **No Export/Import**: Currently no built-in functionality to export notes to other formats (Markdown, PDF, etc.) or import from external sources.

8. **Tags Are Case-Sensitive**: Tags like "Work" and "work" are treated as different tags.

9. **No Nested Tags or Hierarchies**: Flat tag structure only; no support for tag hierarchies or nested categories.

10. **Storage File Location**: The `notes_storage.json` file is created in the same directory as `server.py`. Make sure this directory is writable.

## Troubleshooting

### Server Not Showing Up in Claude Desktop

1. Verify the path in `claude_desktop_config.json` is correct and uses absolute paths
2. Check that Python 3.12+ is in your PATH
3. Restart Claude Desktop completely (quit and reopen)
4. Check Claude Desktop logs for errors

### Notes Not Persisting

1. Ensure the server directory is writable
2. Check if `notes_storage.json` is being created in the correct location
3. Verify no permission errors in the console output

### Tool Calls Failing

1. Verify all required parameters are provided
2. Check note IDs are valid strings (not integers)
3. Ensure the MCP package is properly installed

## Technical Details

- **Protocol**: Model Context Protocol (MCP)
- **Transport**: stdio (standard input/output)
- **Storage**: JSON file (`notes_storage.json`)
- **Python Version**: 3.12+
- **Dependencies**: `mcp` (official MCP Python SDK)

## License

This project is provided as-is for educational purposes.

## Contributing

Feel free to submit issues or pull requests to improve the server functionality.
