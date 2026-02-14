# Deterministic smoke checks callable by Ren'Py test runner.

label automated_smoke_test:
    $ ensure_profile_defaults()
    $ all_cases, diagnostics_errors = load_all_cases()
    $ assert len(all_cases) >= 10, "Expected at least 10 cases"
    $ assert len(diagnostics_errors) == 0, "Diagnostics should be clean"

    # Language toggle checks
    $ renpy.change_language(None)
    $ assert tr({"en": "Hello", "fr": "Bonjour"}) == "Hello"
    $ renpy.change_language("french")
    $ assert tr({"en": "Hello", "fr": "Bonjour"}) == "Bonjour"
    $ renpy.change_language(None)

    # Deterministic case traversal: always first choice for 3 steps.
    $ first = all_cases[0]
    $ start_case_runtime(first, "MED3")
    python:
        for _i in range(3):
            node = case_nodes.get(current_node)
            assert node is not None, "Node should exist"
            assert node.get("choices"), "Node should have choices"
            c = node["choices"][0]
            apply_effects(c)
            current_node = c.get("nextNodeId", c.get("next", "END"))

    # Force completion, then verify debrief computes.
    $ current_node = "END"
    $ debrief_data = score_case(first)
    $ assert "score" in debrief_data and "outcome" in debrief_data

    return
