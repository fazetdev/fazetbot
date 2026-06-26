import os
import re
import psycopg2
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# 1. Initialize Configuration
API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

if not API_KEY:
    raise ValueError("Missing GEMINI_API_KEY environment variable.")
if not DATABASE_URL:
    raise ValueError("Missing DATABASE_URL environment variable.")

client = genai.Client(api_key=API_KEY)
EMBEDDING_MODEL = "gemini-embedding-001"

# 2. Connect to Neon Database
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

def parse_markdown_by_sections(file_path):
    """Splits a markdown file by headers, grouping content under sections."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    sections = re.split(r'\n(?=#+\s)', content)
    chunks = []
    current_title = "General Context"
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
            
        lines = section.split('\n')
        if lines[0].startswith('#'):
            current_title = lines[0].lstrip('#').strip()
            section_content = '\n'.join(lines[1:]).strip()
        else:
            section_content = section
            
        if section_content:
            chunks.append({
                "title": current_title,
                "content": f"### {current_title}\n{section_content}"
            })
            
    return chunks

def sync_knowledge_base():
    print("Clearing out old knowledge base records in Neon...")
    cursor.execute("TRUNCATE TABLE fazetbot_chunks;")
    
    knowledge_dir = "knowledge"
    
    if not os.path.exists(knowledge_dir):
        print(f"⚠️ Error: '{knowledge_dir}' directory not found!")
        return
        
    for root, _, files in os.walk(knowledge_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                print(f"Syncing content from: {file_path}")
                
                chunks = parse_markdown_by_sections(file_path)
                
                for chunk in chunks:
                    # Requesting 768 dimensions explicitly to fit your pgvector schema
                    response = client.models.embed_content(
                        model=EMBEDDING_MODEL,
                        contents=chunk["content"],
                        config=types.EmbedContentConfig(
                            output_dimensionality=768
                        )
                    )
                    vector = response.embeddings[0].values
                    
                    cursor.execute("""
                        INSERT INTO fazetbot_chunks (file_path, section_title, content, embedding)
                        VALUES (%s, %s, %s, %s);
                    """, (file_path, chunk["title"], chunk["content"], vector))
                    
    conn.commit()
    print("✨ Knowledge base completely synced to Neon Cloud!")

if __name__ == "__main__":
    sync_knowledge_base()
    cursor.close()
    conn.close()
