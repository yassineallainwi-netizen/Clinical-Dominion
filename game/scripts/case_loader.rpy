init -2 python:
    import json
    import os

    CASE_REQUIRED_KEYS = [
        "id", "specialty", "difficultyEffects", "topics", "startNode",
        "nodes", "debrief", "correctDiagnosis", "title"
    ]

    NODE_REQUIRED_KEYS = ["id", "background", "speaker", "text", "choices"]

    def load_all_cases():
        base = renpy.loader.transfn("cases")
        loaded = []
        errors = []

        if not os.path.isdir(base):
            errors.append("Missing folder: game/cases")
            return loaded, errors

        for fname in sorted(os.listdir(base)):
            if not fname.endswith(".json"):
                continue
            path = os.path.join(base, fname)
            try:
                with open(path, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                valid_errors = validate_case(data, fname)
                if valid_errors:
                    errors.extend(valid_errors)
                else:
                    loaded.append(data)
            except Exception as exc:
                errors.append("%s: %s" % (fname, str(exc)))

        return loaded, errors

    def validate_case(case_data, fname):
        errs = []
        for key in CASE_REQUIRED_KEYS:
            if key not in case_data:
                errs.append("%s missing key '%s'" % (fname, key))

        if "title" in case_data:
            if "en" not in case_data["title"] or "fr" not in case_data["title"]:
                errs.append("%s title needs en/fr" % fname)

        nodes = case_data.get("nodes", [])
        node_ids = set()
        for i, node in enumerate(nodes):
            for key in NODE_REQUIRED_KEYS:
                if key not in node:
                    errs.append("%s node[%d] missing '%s'" % (fname, i, key))
            if "id" in node:
                node_ids.add(node["id"])
            if "text" in node and ("en" not in node["text"] or "fr" not in node["text"]):
                errs.append("%s node[%d] text needs en/fr" % (fname, i))
            for j, choice in enumerate(node.get("choices", [])):
                if "text" not in choice or ("nextNodeId" not in choice and "next" not in choice):
                    errs.append("%s node[%d] choice[%d] missing text/nextNodeId" % (fname, i, j))
                elif "en" not in choice["text"] or "fr" not in choice["text"]:
                    errs.append("%s node[%d] choice[%d] text needs en/fr" % (fname, i, j))

        start = case_data.get("startNode")
        if start and start not in node_ids:
            errs.append("%s startNode '%s' not found" % (fname, start))

        return errs
