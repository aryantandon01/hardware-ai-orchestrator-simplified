import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import json
import os
from pathlib import Path

def initialize_chromadb():
    """Initialize and populate ChromaDB with components and standards"""
    
    # Initialize ChromaDB client with persistence
    client = chromadb.Client(Settings(
        persist_directory="./data/chromadb",
        is_persistent=True
    ))
    
    # Initialize embedding model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Create collections
    components_collection = client.get_or_create_collection(
        name="hardware_components",
        metadata={"description": "Hardware component specifications"}
    )
    
    standards_collection = client.get_or_create_collection(
        name="compliance_standards", 
        metadata={"description": "Compliance and safety standards"}
    )
    
    # Load and add components
    components_data = load_components_data()
    if components_data:
        add_components_to_db(components_collection, components_data, model)
    
    # Load and add standards
    standards_data = load_standards_data()
    if standards_data:
        add_standards_to_db(standards_collection, standards_data, model)
    
    print("✅ ChromaDB vector database initialized successfully!")
    return client

def load_components_data():
    """Load component data from JSON files"""
    components = []
    components_dir = Path("src/data/components")
    
    if not components_dir.exists():
        print("❌ Components directory not found")
        return []
    
    for json_file in components_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                components.extend(data.get('components', []))
        except Exception as e:
            print(f"❌ Error loading {json_file}: {e}")
    
    print(f"✅ Loaded {len(components)} components")
    return components

def load_standards_data():
    """Load standards data from JSON files"""
    standards = []
    standards_dir = Path("src/data/standards")
    
    if not standards_dir.exists():
        print("❌ Standards directory not found")
        return []
    
    for json_file in standards_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                standards.append(data)
        except Exception as e:
            print(f"❌ Error loading {json_file}: {e}")
    
    print(f"✅ Loaded {len(standards)} standards")
    return standards

def add_components_to_db(collection, components, model):
    """Add components to ChromaDB collection"""
    documents = []
    metadatas = []
    ids = []
    
    for comp in components:
        # Create searchable text from component data
        doc_text = f"""
        {comp.get('name', '')} {comp.get('manufacturer', '')} 
        {comp.get('description', '')} {comp.get('category', '')}
        {' '.join(comp.get('key_features', []))}
        {' '.join(comp.get('applications', []))}
        {' '.join(comp.get('keywords', []))}
        """.strip()
        
        documents.append(doc_text)
        metadatas.append({
            'type': 'component',
            'category': comp.get('category', ''),
            'manufacturer': comp.get('manufacturer', ''),
            'automotive_qualified': comp.get('automotive_qualified', False)
        })
        ids.append(f"comp_{comp.get('component_id', len(ids))}")
    
    if documents:
        # Generate embeddings
        embeddings = model.encode(documents).tolist()
        
        # Add to collection
        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        print(f"✅ Added {len(documents)} components to vector database")

def add_standards_to_db(collection, standards, model):
    """Add standards to ChromaDB collection"""
    documents = []
    metadatas = []
    ids = []
    
    for std in standards:
        # Create searchable text from standard data
        doc_text = f"""
        {std.get('name', '')} {std.get('standard_id', '')}
        {std.get('description', '')} {std.get('scope', '')}
        {std.get('organization', '')}
        """.strip()
        
        # Add requirements text
        for req in std.get('requirements', []):
            doc_text += f" {req.get('title', '')} {req.get('description', '')} {req.get('acceptance_criteria', '')}"
        
        documents.append(doc_text)
        metadatas.append({
            'type': 'standard',
            'standard_id': std.get('standard_id', ''),
            'organization': std.get('organization', ''),
        })
        ids.append(f"std_{std.get('standard_id', len(ids))}")
    
    if documents:
        # Generate embeddings
        embeddings = model.encode(documents).tolist()
        
        # Add to collection
        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        print(f"✅ Added {len(documents)} standards to vector database")

if __name__ == "__main__":
    initialize_chromadb()
