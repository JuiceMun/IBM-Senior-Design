#!/usr/bin/env python3
"""
Utilities to validate and convert between:
  - system_description.schema.json  <->  queueing_network.schema.json

Usage examples:

  # Validate instances
  python convert_and_validate.py validate example_system_description.json system_description.schema.json
  python convert_and_validate.py validate example_queueing_network.json queueing_network.schema.json

  # Convert system -> queue
  python convert_and_validate.py to-queue example_system_description.json > out_queue.json

  # Convert queue -> system
  python convert_and_validate.py to-system example_queueing_network.json > out_system.json

If 'jsonschema' is installed, validation will be strict. If not, the script
will still perform conversions and will print a hint to install it.
"""
import json, sys, os

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def try_validate(instance, schema):
    try:
        import jsonschema
        jsonschema.validate(instance=instance, schema=schema)
        return True, None
    except ModuleNotFoundError:
        return None, "jsonschema not installed. Install with: pip install jsonschema"
    except Exception as e:
        return False, str(e)

def system_to_queueing(system_doc):
    nodes = []
    edges = []
    # Map components to nodes
    for comp in system_doc.get("system_description", []):
        node = {
            "id": comp["id"],
            "station_type": comp.get("type") or "queue",
            "arrival_rate": None,
            "service_rate": None,
            "servers": 1,
            "machine": comp.get("machine"),
            "description": comp.get("description"),
        }
        nodes.append(node)
        # Edges (weight -> prob if numeric)
        for e in comp.get("edges") or []:
            prob = None
            w = e.get("weight")
            if isinstance(w, (int, float)):
                prob = float(w)
            else:
                try:
                    prob = float(w)
                except Exception:
                    prob = None
            edges.append({"from": comp["id"], "to": e["to"], "prob": prob if prob is not None else 0.0})
    return {"nodes": nodes, "edges": edges, "metadata": system_doc.get("metadata", [])}

def queueing_to_system(queue_doc):
    system_components = []
    # Map nodes to components
    for node in queue_doc.get("nodes", []):
        comp = {
            "id": node["id"],
            "type": node.get("station_type") or "service",
            "machine": node.get("machine"),
            "description": node.get("description"),
            "network_speed": None,
            "messages": [],
            "edges": []
        }
        system_components.append(comp)
    # Build quick index
    comp_index = {c["id"]: c for c in system_components}
    # Map edges (prob -> weight)
    for e in queue_doc.get("edges", []):
        src = e["from"]
        if src in comp_index:
            comp_index[src].setdefault("edges", []).append({
                "to": e["to"],
                "weight": e.get("prob", 0.0)
            })
    return {"system_description": system_components, "metadata": queue_doc.get("metadata", [])}

def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd = argv[1]
    if cmd == "validate":
        if len(argv) != 4:
            print("Usage: validate <instance.json> <schema.json>", file=sys.stderr)
            return 2
        inst = load_json(argv[2])
        schema = load_json(argv[3])
        ok, err = try_validate(inst, schema)
        if ok is True:
            print("VALID ✅")
            return 0
        elif ok is None:
            print("Validation skipped (jsonschema not installed). Hint: pip install jsonschema")
            return 0
        else:
            print("INVALID ❌")
            print(err)
            return 1
    elif cmd == "to-queue":
        if len(argv) != 3:
            print("Usage: to-queue <system_instance.json>", file=sys.stderr)
            return 2
        inst = load_json(argv[2])
        out = system_to_queueing(inst)
        print(json.dumps(out, indent=2))
        return 0
    elif cmd == "to-system":
        if len(argv) != 3:
            print("Usage: to-system <queue_instance.json>", file=sys.stderr)
            return 2
        inst = load_json(argv[2])
        out = queueing_to_system(inst)
        print(json.dumps(out, indent=2))
        return 0
    else:
        print("Unknown command:", cmd, file=sys.stderr)
        print(__doc__)
        return 2

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
