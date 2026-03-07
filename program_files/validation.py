'''Validation of queue network conversions before sending to data generator'''

from typing import Any, Dict, List, Tuple

from annotated_types import doc # for type annotations

EXTERNAL_NODE_ID = "external"


def validate(model: Dict[str, Any]) -> List[str]:
    """Check logical rules and return a list of error messages. If the list is empty, the model is valid."""
    errors: List[str] = []

    queues = model.get("queues", [])

    queue_ids = [q["id"] for q in queues] # Collect queue IDs

    # Check if duplicate queue IDs exist
    if len(queue_ids) != len(set(queue_ids)):
        errors.append("Duplicate queue IDs found")

    return errors

def enforce(model: Dict[str, Any]) -> Dict[str, Any]:
    """Finds a model, validates it, and returns a dictionary with the status, assumptions, and errors."""
    assumptions: List[str] = []
    
    try:
        model = get_model(doc)
    except Exception as e:
        return {"status": "error", "errors": [str(e)]}
    errors = validate(model)

    if errors:
        return {"status": "error", "errors": errors}
    
    return {"status": "ok", "model": doc, "assumptions": assumptions}


"""Helper Functions"""
def get_model(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Extract the queue network model from the JSON produced by converter."""
    if "system" not in doc:
        raise ValueError("JSON must contain a 'system' key")
    
    if not isinstance(doc["system"], dict):
        raise ValueError("'system' must be a dictionary")
    
    return doc["system"]