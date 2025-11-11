# validate.py
import os, json
from jsonschema import Draft202012Validator
from program_files import config_loader


def validate_json(data_path, schema_path) -> list:
    """Validate a JSON file against a JSON Schema.
       Returns a list of error messages (empty if valid).
    """
    with open(schema_path) as f:
        schema = json.load(f)
    with open(data_path) as f:
        instance = json.load(f)

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)

    # Return readable list of messages
    return [f"at /{'/'.join(map(str, e.path))}: {e.message}" for e in errors]


def system_to_queue(system_path):
    """Convert a System Description JSON file → Queueing Network JSON dict."""
    with open(system_path) as f:
        system_doc = json.load(f)

    comps = system_doc.get("system_description", [])

    # Find entry point (first node with no incoming edges)
    incoming = {c["id"]: 0 for c in comps}
    for c in comps:
        for e in c.get("edges", []):
            incoming[e["to"]] = incoming.get(e["to"], 0) + 1
    entry_candidates = [cid for cid, deg in incoming.items() if deg == 0]
    entry_id = entry_candidates[0] if entry_candidates else (comps[0]["id"] if comps else "")

    # Build queue list
    queues = []
    for c in comps:
        next_queue = []
        for e in c.get("edges", []):
            try:
                prob = float(e.get("weight", 0)) * 100.0
            except Exception:
                prob = 0.0
            next_queue.append({
                "id": e.get("to", ""),
                "probability": prob
            })
        queues.append({
            "id": c.get("id", ""),
            "service_rate": None,
            "next_queue": next_queue
        })

    # Build result
    return {
        "queue_network": {
            "lambda": None,
            "beta": None,
            "entry_points": entry_id,
            "constraint": {
                "entry_points": entry_id,
                "service_rate_sum": 0.0
            },
            "queues": queues
        }
    }


def queue_to_system(queue_path):
    """Convert a Queueing Network JSON file → System Description JSON dict."""
    with open(queue_path) as f:
        queue_doc = json.load(f)

    qn = queue_doc.get("queue_network", {})
    entry_id = qn.get("entry_points", "")
    queues = qn.get("queues", [])

    components = []
    for q in queues:
        cid = q.get("id", "")
        ctype = "connection" if cid == entry_id else "service"
        edges = []
        for nxt in q.get("next_queue", []):
            try:
                w = float(nxt.get("probability", 0)) / 100.0
            except Exception:
                w = 0.0
            edges.append({
                "to": nxt.get("id", ""),
                "weight": w
            })
        components.append({
            "id": cid,
            "type": ctype,
            "machine": "unknown",
            "description": "",
            "network_speed": None,
            "messages": [],
            "edges": edges
        })

    return {
        "system_description": components,
        "metadata": []
    }

def main():
    cfg = config_loader.get_config()

    sd_schema = cfg.get("paths", "system_description_schema")
    qn_schema = cfg.get("paths", "queueing_network_schema")
    sd_json   = cfg.get("paths", "system_description")
    qn_json   = cfg.get("paths", "queueing_network")
    out_dir   = cfg.get("paths", "converted_dir")
    out_file  = cfg.get("paths", "converted_queue_out")

    if True: #Debug - Change to True to see output
        print("\n[CONFIG]")
        print("  system_description_schema:", sd_schema, " exists:", os.path.exists(sd_schema))
        print("  queueing_network_schema  :", qn_schema, " exists:", os.path.exists(qn_schema))
        print("  system_description JSON  :", sd_json,   " exists:", os.path.exists(sd_json))
        print("  queueing_network JSON    :", qn_json,   " exists:", os.path.exists(qn_json))
        print("  output dir               :", out_dir)
        print("  output file              :", out_file)

    errors = validate_json(sd_json,sd_schema)

    if len(errors) > 0:
      print(errors)
      return;

    converted = system_to_queue(sd_json) #doesnt account for delay yet
    with open(out_file, 'w') as f:

        json.dump(converted,f,indent = 2)


if __name__ == "__main__":
    main()

