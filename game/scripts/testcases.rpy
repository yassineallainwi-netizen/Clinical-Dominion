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

    # Golden regression traversal by deterministic choices.
    python:
        golden = None
        for c in all_cases:
            if c.get("id") == "test_golden_001":
                golden = c
                break
        assert golden is not None, "test_golden_001 must exist"

    $ start_case_runtime(golden, "MED3")

    python:
        planned_choices = [
            "abc_monitor",
            "dx_hyperk",
            "bundle_complete",
            "consult_neph",
            "prepare_dialysis",
            "safe_disposition",
            "confirm_dx",
            "complete_case",
        ]

        for choice_id in planned_choices:
            node = case_nodes.get(current_node)
            assert node is not None, "Node should exist"
            options = node.get("choices", [])
            assert options, "Node should have choices"

            selected = None
            for c in options:
                if c.get("id") == choice_id:
                    selected = c
                    break
            assert selected is not None, "Expected deterministic choice id not found"

            apply_effects(selected)
            current_node = selected.get("nextNodeId", selected.get("next", "END"))

        assert current_node == "END", "Golden path should reach terminal END"

    $ debrief_data = score_case(golden)
    $ assert debrief_data.get("score") is not None
    $ assert debrief_data.get("outcome") is not None
    $ assert debrief_data.get("correctDx") is not None
    $ assert debrief_data.get("stability_end") is not None

    return
