"""
MCP Notes Server
A simple notes management server that demonstrates MCP protocol implementation.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# Storage file for notes
NOTES_FILE = Path("notes_storage.json")

# In-memory notes storage
notes_db = {}
next_id = 1


def load_notes():
    """Load notes from storage file."""
    global notes_db, next_id
    if NOTES_FILE.exists():
        try:
            with open(NOTES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                notes_db = data.get('notes', {})
                next_id = data.get('next_id', 1)
        except Exception as e:
            print(f"Error loading notes: {e}")
            notes_db = {}
            next_id = 1
    else:
        notes_db = {}
        next_id = 1


def save_notes():
    """Save notes to storage file."""
    try:
        with open(NOTES_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'notes': notes_db,
                'next_id': next_id
            }, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving notes: {e}")


# Create server instance
server = Server("notes-server")


@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List available note resources."""
    resources = []
    
    # Add individual note resources
    for note_id, note in notes_db.items():
        resources.append(
            types.Resource(
                uri=f"note://{note_id}",
                name=f"Note: {note['title']}",
                description=f"Note created on {note['created_at']}",
                mimeType="text/plain",
            )
        )
    
    # Add notes list resource
    resources.append(
        types.Resource(
            uri="notes://list",
            name="All Notes",
            description=f"List of all {len(notes_db)} notes",
            mimeType="application/json",
        )
    )
    
    return resources


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read a specific note resource."""
    if uri == "notes://list":
        # Return list of all notes
        notes_list = []
        for note_id, note in notes_db.items():
            notes_list.append({
                "id": note_id,
                "title": note["title"],
                "preview": note["content"][:100] + "..." if len(note["content"]) > 100 else note["content"],
                "tags": note["tags"],
                "created_at": note["created_at"],
                "updated_at": note["updated_at"]
            })
        return json.dumps(notes_list, indent=2, ensure_ascii=False)
    
    elif uri.startswith("note://"):
        # Extract note ID from URI
        note_id = uri[7:]  # Remove "note://" prefix
        
        if note_id in notes_db:
            note = notes_db[note_id]
            return f"""Title: {note['title']}
Created: {note['created_at']}
Updated: {note['updated_at']}
Tags: {', '.join(note['tags'])}

{note['content']}"""
        else:
            raise ValueError(f"Note with ID {note_id} not found")
    
    else:
        raise ValueError(f"Unknown resource URI: {uri}")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="create_note",
            description="Create a new note with content and optional title/tags",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The content of the note"
                    },
                    "title": {
                        "type": "string",
                        "description": "Optional title for the note (defaults to first line of content)"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of tags for categorization"
                    }
                },
                "required": ["content"]
            }
        ),
        types.Tool(
            name="list_notes",
            description="List all notes with optional filtering and pagination",
            inputSchema={
                "type": "object",
                "properties": {
                    "tag": {
                        "type": "string",
                        "description": "Filter notes by tag"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of notes to return (default: all)",
                        "minimum": 1
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="get_note",
            description="Get the full content of a specific note by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_id": {
                        "type": "string",
                        "description": "The ID of the note to retrieve"
                    }
                },
                "required": ["note_id"]
            }
        ),
        types.Tool(
            name="update_note",
            description="Update an existing note's content, title, or tags",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_id": {
                        "type": "string",
                        "description": "The ID of the note to update"
                    },
                    "content": {
                        "type": "string",
                        "description": "New content for the note"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title for the note"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "New list of tags"
                    }
                },
                "required": ["note_id"]
            }
        ),
        types.Tool(
            name="delete_note",
            description="Delete a note by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_id": {
                        "type": "string",
                        "description": "The ID of the note to delete"
                    }
                },
                "required": ["note_id"]
            }
        ),
        types.Tool(
            name="search_notes",
            description="Search notes by keyword in title or content",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search keyword or phrase"
                    },
                    "tag": {
                        "type": "string",
                        "description": "Optional tag filter to narrow search"
                    }
                },
                "required": ["query"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests."""
    global next_id
    
    if arguments is None:
        arguments = {}
    
    if name == "create_note":
        content = arguments["content"]
        title = arguments.get("title", "")
        tags = arguments.get("tags", [])
        
        # Auto-generate title from first line if not provided
        if not title:
            title = content.split('\n')[0][:50]
        
        # Create note
        note_id = str(next_id)
        next_id += 1
        
        timestamp = datetime.now().isoformat()
        notes_db[note_id] = {
            "title": title,
            "content": content,
            "tags": tags,
            "created_at": timestamp,
            "updated_at": timestamp
        }
        save_notes()
        
        return [
            types.TextContent(
                type="text",
                text=f"✓ Note created successfully!\nID: {note_id}\nTitle: {title}\nTags: {', '.join(tags) if tags else 'none'}"
            )
        ]
    
    elif name == "list_notes":
        tag_filter = arguments.get("tag")
        limit = arguments.get("limit")
        
        # Filter notes
        filtered_notes = []
        for note_id, note in notes_db.items():
            if tag_filter and tag_filter not in note["tags"]:
                continue
            filtered_notes.append((note_id, note))
        
        # Apply limit
        if limit:
            filtered_notes = filtered_notes[:limit]
        
        if not filtered_notes:
            return [types.TextContent(type="text", text="No notes found.")]
        
        # Format output
        output = f"Found {len(filtered_notes)} note(s):\n\n"
        for note_id, note in filtered_notes:
            preview = note["content"][:80] + "..." if len(note["content"]) > 80 else note["content"]
            tags_str = f" [{', '.join(note['tags'])}]" if note['tags'] else ""
            output += f"• ID: {note_id} | {note['title']}{tags_str}\n  {preview}\n\n"
        
        return [types.TextContent(type="text", text=output.strip())]
    
    elif name == "get_note":
        note_id = arguments["note_id"]
        
        if note_id not in notes_db:
            return [types.TextContent(type="text", text=f"✗ Note with ID '{note_id}' not found.")]
        
        note = notes_db[note_id]
        output = f"""📝 Note ID: {note_id}
Title: {note['title']}
Created: {note['created_at']}
Updated: {note['updated_at']}
Tags: {', '.join(note['tags']) if note['tags'] else 'none'}

Content:
{note['content']}"""
        
        return [types.TextContent(type="text", text=output)]
    
    elif name == "update_note":
        note_id = arguments["note_id"]
        
        if note_id not in notes_db:
            return [types.TextContent(type="text", text=f"✗ Note with ID '{note_id}' not found.")]
        
        note = notes_db[note_id]
        updated_fields = []
        
        if "content" in arguments:
            note["content"] = arguments["content"]
            updated_fields.append("content")
        
        if "title" in arguments:
            note["title"] = arguments["title"]
            updated_fields.append("title")
        
        if "tags" in arguments:
            note["tags"] = arguments["tags"]
            updated_fields.append("tags")
        
        if updated_fields:
            note["updated_at"] = datetime.now().isoformat()
            save_notes()
            return [types.TextContent(
                type="text",
                text=f"✓ Note {note_id} updated successfully!\nUpdated fields: {', '.join(updated_fields)}"
            )]
        else:
            return [types.TextContent(type="text", text="✗ No fields to update.")]
    
    elif name == "delete_note":
        note_id = arguments["note_id"]
        
        if note_id not in notes_db:
            return [types.TextContent(type="text", text=f"✗ Note with ID '{note_id}' not found.")]
        
        deleted_note = notes_db.pop(note_id)
        save_notes()
        
        return [types.TextContent(
            type="text",
            text=f"✓ Note '{deleted_note['title']}' (ID: {note_id}) deleted successfully."
        )]
    
    elif name == "search_notes":
        query = arguments["query"].lower()
        tag_filter = arguments.get("tag")
        
        # Search notes
        results = []
        for note_id, note in notes_db.items():
            # Apply tag filter if specified
            if tag_filter and tag_filter not in note["tags"]:
                continue
            
            # Search in title and content
            if query in note["title"].lower() or query in note["content"].lower():
                results.append((note_id, note))
        
        if not results:
            return [types.TextContent(type="text", text=f"No notes found matching '{query}'.")]
        
        # Format output
        output = f"Found {len(results)} note(s) matching '{query}':\n\n"
        for note_id, note in results:
            preview = note["content"][:80] + "..." if len(note["content"]) > 80 else note["content"]
            tags_str = f" [{', '.join(note['tags'])}]" if note['tags'] else ""
            output += f"• ID: {note_id} | {note['title']}{tags_str}\n  {preview}\n\n"
        
        return [types.TextContent(type="text", text=output.strip())]
    
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Main entry point for the server."""
    # Load existing notes
    load_notes()
    
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="notes-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
