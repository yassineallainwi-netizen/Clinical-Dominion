define e = Character("", kind=narrator)

default all_cases = []
default diagnostics_errors = []
default selected_case = None
default selected_difficulty = "MED3"
default game_state = {}
default case_nodes = {}
default timer_left = 0
default timer_enabled = False
default timer_expired = False
default current_node = None
default debrief_data = {}

default score_parts = {"dx": 0, "stability": 0, "critical": 0, "resources": 0, "time": 0}

define DIFFICULTIES = ["MED3", "INTERN", "PGY1", "PGY4", "SPECIALIST"]

define TIMER_BY_DIFFICULTY = {"MED3": 0, "INTERN": 25, "PGY1": 20, "PGY4": 15, "SPECIALIST": 12}

define STABILITY_LABELS = [
    (80, _("Stable")),
    (60, _("Guarded")),
    (40, _("Concerning")),
    (20, _("Critical")),
    (0, _("Decompensating")),
]

init python:
    def tr(localized):
        if not isinstance(localized, dict):
            return localized
        if renpy.game.preferences.language == "french":
            return localized.get("fr", localized.get("en", ""))
        return localized.get("en", localized.get("fr", ""))

    def difficulty_timer_seconds(diff):
        if diff == "INTERN" and not persistent.optional_timer_intern:
            return 0
        return TIMER_BY_DIFFICULTY.get(diff, 0)

    def build_case_index(case_data):
        return {n["id"]: n for n in case_data.get("nodes", [])}

    def start_case_runtime(case_data, difficulty):
        global selected_case, selected_difficulty, case_nodes, current_node, timer_expired
        selected_case = case_data
        selected_difficulty = difficulty
        case_nodes = build_case_index(case_data)
        current_node = case_data["startNode"]
        timer_expired = False
        reset_state()

    def reset_state():
        global game_state, score_parts
        game_state = {
            "stability": 85,
            "suspectedDx": "",
            "redFlagsMissed": 0,
            "resourcesUsed": 0,
            "stepIndex": 0,
            "branchingPath": [],
            "criticalHits": 0,
            "delayCount": 0,
            "actions": [],
            "eventLog": [],
        }
        score_parts = {"dx": 0, "stability": 0, "critical": 0, "resources": 0, "time": 0}

    def stability_view_text():
        s = game_state["stability"]
        if selected_difficulty in ("MED3", "INTERN"):
            return str(s)
        for threshold, label in STABILITY_LABELS:
            if s >= threshold:
                return label
        return _("Unknown")

    def setup_timer():
        global timer_left, timer_enabled
        timer_left = difficulty_timer_seconds(selected_difficulty)
        timer_enabled = timer_left > 0

    def find_delay_choice(node):
        for ch in node.get("choices", []):
            if ch.get("isDelay"):
                return ch
        return None

    def apply_effects(choice):
        eff = choice.get("effects", {}).get(selected_difficulty, choice.get("effects", {}).get("default", {}))
        game_state["stability"] = max(0, min(100, game_state["stability"] + eff.get("stability", 0)))
        game_state["redFlagsMissed"] += eff.get("redFlags", 0)
        game_state["resourcesUsed"] += eff.get("resources", 0)
        if eff.get("critical"):
            game_state["criticalHits"] += 1
        if eff.get("setDx"):
            game_state["suspectedDx"] = eff["setDx"]
        if eff.get("delay"):
            game_state["delayCount"] += 1

        game_state["actions"].append(choice.get("id", "action"))
        game_state["branchingPath"].append(choice.get("nextNodeId", choice.get("next", "")))

    def apply_timeout(node):
        delay_choice = find_delay_choice(node)
        if delay_choice:
            apply_effects(delay_choice)
            game_state["eventLog"].append("timer_expiry_delay")
            return delay_choice.get("nextNodeId", delay_choice.get("next"))
        game_state["stability"] = max(0, game_state["stability"] - 10)
        game_state["delayCount"] += 1
        game_state["eventLog"].append("timer_expiry_fallback")
        return node.get("timeoutNext", "END")

    def score_case(case_data):
        correct = case_data.get("correctDiagnosis", "")
        dx_match = 40 if game_state["suspectedDx"] == correct else 12 if game_state["suspectedDx"] else 0
        stab_score = max(0, min(25, int(game_state["stability"] / 4)))
        critical_total = case_data.get("criticalActionCount", 3)
        critical_score = min(20, int((game_state["criticalHits"] / float(max(1, critical_total))) * 20))
        resource_penalty = min(10, game_state["resourcesUsed"])
        resource_score = max(0, 10 - resource_penalty)
        time_score = max(0, 5 - game_state["delayCount"])

        score_parts["dx"] = dx_match
        score_parts["stability"] = stab_score
        score_parts["critical"] = critical_score
        score_parts["resources"] = resource_score
        score_parts["time"] = time_score

        total = dx_match + stab_score + critical_score + resource_score + time_score

        if total >= 75 and game_state["stability"] >= 60:
            outcome = "Success"
        elif total >= 45:
            outcome = "Partial"
        else:
            outcome = "Poor"

        return {
            "score": total,
            "outcome": outcome,
            "correctDx": correct,
            "stability_end": game_state["stability"],
        }

label run_case:
    $ update_daily_streak()
    while current_node != "END":
        $ node = case_nodes.get(current_node)
        if node is None:
            call screen runtime_error_screen(_("Case graph error. Moving safely to debrief."))
            jump end_case

        $ game_state["stepIndex"] += 1
        $ setup_timer()

        call screen case_node_screen(node)

        if timer_expired:
            $ nxt = apply_timeout(node)
            $ timer_expired = False
            if nxt == "END":
                $ current_node = "END"
            else:
                $ current_node = nxt
        else:
            $ choice = _return
            if choice is None:
                $ current_node = "END"
            else:
                python:
                    try:
                        apply_effects(choice)
                        nxt = choice.get("nextNodeId", choice.get("next"))
                    except Exception:
                        nxt = None
                if not nxt:
                    call screen runtime_error_screen(_("Choice is missing nextNodeId. Moving safely to debrief."))
                    $ current_node = "END"
                else:
                    $ current_node = nxt

    label end_case:
        $ debrief_data = score_case(selected_case)
        $ total_xp, coins = grant_case_rewards(debrief_data)
        $ add_to_leaderboard({
            "player": persistent.profile_name,
            "case": tr(selected_case.get("title", {})),
            "score": debrief_data["score"],
            "outcome": debrief_data["outcome"],
            "stability_end": debrief_data["stability_end"],
        })
        $ register_weak_areas(selected_case.get("topics", []), debrief_data["score"])
        $ renpy.save_persistent()
        call screen debrief_screen(total_xp, coins)
        return
