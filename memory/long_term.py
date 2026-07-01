import chromadb
from configs.config import settings


## joinend strings with "|"  : Use back in retrieval 

## chroma client
client = chromadb.PersistentClient(path='/chroma_db')


## collection created with name study_node
collection = client.get_or_create_collection(
  name = "study_notes", 
  embedding_function=settings.embedding_model)   # type:ignore

## store notes function : Upsert notes in chromadb
def store_notes(notes, topic, level, current_day):
  subtopic = notes.get('subtopic','')
  # ID formatting
  subtopic_id = subtopic.lower().replace(" ", "_").replace(":", "").replace("&", "and")

  # Extract string values 
  summary = notes.get('summary','')
  ## joinend strings with "|"  : Use back in retrieval 
  full_key_concept = "|".join(concept for concept in notes.get('key_concepts',[]))
  facts = "|".join(fact for fact in notes.get("important_facts",[]))
  study_tips = "|".join(fact for fact in notes.get("study_tips",[]))

  base_meta = {"subtopic":subtopic,
                "topic":topic, 
                "level": level, 
                "day":current_day, 
                "sources":"|".join(notes.get("sources_used",[])),
                "section":"summary"}

  # Build the raw documents
  raw_docs = [
    {"id": f"{subtopic_id}_summary", "text": summary, "section": "summary", "sources": "|".join(notes.get("sources_used", []))},
    {"id": f"{subtopic_id}_key_concepts", "text": full_key_concept, "section": "key_concepts", "sources": ""},
    {"id": f"{subtopic_id}_important_facts", "text": facts, "section": "important_facts", "sources": ""},
    {"id": f"{subtopic_id}_study_tips", "text": study_tips, "section": "study_tips", "sources": ""}
  ]

  docs = []
  ids =  []
  metadatas = []

  for item in raw_docs:
    if item["text"].strip(): 
      ids.append(item["id"])
      docs.append(item["text"])   

      # Merge base metadata with section specific info
      meta = base_meta.copy()
      meta["section"] = item["section"]
      if item["sources"]:
        meta["sources"] = item["sources"]
        
      metadatas.append(meta)
  
  if not docs:
      print("Warning: No text content found to store.")
      return False
  
  try:  
    collection.upsert(
      ids = ids,
      documents=docs,
      metadatas = metadatas
    )
    return True
  except Exception as e:
    print(f"ChromaDB Upsert Error:{e}")
    return False

## retriever
def retrieve_notes(subtopic: str, threshold: float = 1.5):
    """
    Retrieve exact subtopic notes from ChromaDB.
    Returns reconstructed notes dict if found, else None.
    """
    try:
        results = collection.query(
            query_texts=[subtopic],
            n_results=4,
            where={"subtopic": subtopic}
        )

        if not results['documents'] or not results['documents'][0]:
            return None

        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results['distances'][0]

        # check if best match is close enough
        if distances[0] > threshold:
            return None

        # reconstruct notes dict from sections
        notes = {"subtopic": subtopic}
        sources = []

        for doc, meta in zip(documents, metadatas):
            section = meta['section']

            if section == "summary":
                notes["summary"] = doc
                sources = meta.get("sources", "").split("|") if meta.get("sources") else []
            elif section == "key_concepts":
                notes["key_concepts"] = doc.split("|")
            elif section == "important_facts":
                notes["important_facts"] = doc.split("|")
            elif section == "study_tips":
                notes["study_tips"] = doc.split("|")

        notes["sources_used"] = sources
        return notes

    except Exception as e:
        print(f"Retrieve error: {e}")
        return None


def semantic_search(query: str, n_results: int = 5):
    """
    Free text semantic search across all stored notes.
    Returns list of matching documents with metadata and distance.
    """
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )

        matches = []
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results['distances'][0]

        for doc, meta, dist in zip(documents, metadatas, distances):
            matches.append({
                "content": doc,
                "subtopic": meta.get('subtopic'),
                "section": meta.get('section'),
                "topic": meta.get('topic'),
                "distance": dist
            })

        return matches

    except Exception as e:
        print(f"Search error: {e}")
        return []
