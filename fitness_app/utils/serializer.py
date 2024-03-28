from bson import ObjectId


def serialize_doc(doc):
    """Recursively convert MongoDB document's ObjectIds to strings."""
    if isinstance(doc, ObjectId):
        return str(doc)
    elif isinstance(doc, dict):
        for k, v in doc.items():
            doc[k] = serialize_doc(v)
    elif isinstance(doc, list):
        doc = [serialize_doc(v) for v in doc]
    return doc


def serialize_documents(query):
    return [serialize_doc(doc.to_mongo().to_dict()) for doc in query]
