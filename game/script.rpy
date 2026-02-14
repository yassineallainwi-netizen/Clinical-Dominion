label before_main_menu:
    $ ensure_profile_defaults()
    $ all_cases, diagnostics_errors = load_all_cases()
    return

label start:
    call screen mvp_main_menu
    return

label start_selected_case:
    if selected_case is None:
        $ renpy.notify(_("No case selected."))
        jump start

    python:
        try:
            start_case_runtime(selected_case, selected_difficulty)
        except Exception:
            renpy.call_screen("runtime_error_screen", _("Failed to start case safely."))
            renpy.jump("start")

    jump run_case

screen mvp_main_menu():
    tag menu
    add Solid("#0f172a")

    frame style "panel_frame":
        xalign 0.5
        yalign 0.45
        xsize 900
        has vbox
        spacing 12

        text "CLINICAL DOMINION" size 48 xalign 0.5
        text "Master the Case." size 28 xalign 0.5

        textbutton _("Play") action If(len(all_cases) > 0, true=ShowMenu("choose_case_screen"), false=ShowMenu("case_load_error_screen"))
        textbutton _("Case Library") action ShowMenu("case_library_screen")
        textbutton _("Profile") action ShowMenu("profile_screen")
        textbutton _("Settings") action ShowMenu("custom_settings")
        textbutton _("Credits") action ShowMenu("credits_screen")
        textbutton _("Quit") action Quit(confirm=False)

    text "Clinical Dominion v0.1" xalign 0.5 yalign 0.97 size 22

screen custom_settings():
    tag menu
    use game_menu(_("Settings"), scroll="viewport"):
        vbox:
            spacing 10
            textbutton _("English") action Language(None)
            textbutton _("Français") action Language("french")
            textbutton _("Show educational dosing: [persistent.show_dosing]") action ToggleField(persistent, "show_dosing")
            textbutton _("INTERN optional timer: [persistent.optional_timer_intern]") action ToggleField(persistent, "optional_timer_intern")

screen leaderboard_screen():
    tag menu
    use game_menu(_("Leaderboard"), scroll="viewport"):
        vbox:
            spacing 8
            if persistent.leaderboard:
                for i, row in enumerate(persistent.leaderboard, start=1):
                    text "#[i] [row['player']] - [row['case']] - [row['score']] ([row['outcome']])"
            else:
                text _("No runs yet.")

screen profile_screen():
    tag menu
    use game_menu(_("Profile"), scroll="viewport"):
        vbox:
            spacing 8
            text _("Name: [persistent.profile_name]")
            text _("Rank: [persistent.rank]")
            text _("Level: [persistent.level]")
            text _("XP: [persistent.xp]/[xp_to_next_level(persistent.level)]")
            text _("Coins: [persistent.coins]")
            text _("Daily streak: [persistent.daily_streak]")
            text _("Diagnostic streak: [persistent.diagnostic_streak]")
            text _("Weak areas:")
            if persistent.weak_areas:
                for topic, count in persistent.weak_areas.items():
                    text "- [topic]: [count]"
            else:
                text _("No weak areas tracked yet.")

screen case_library_screen():
    tag menu
    use game_menu(_("Case Library"), scroll="viewport"):
        vbox:
            spacing 8
            for c in all_cases:
                text "[tr(c['title'])] | [c['specialty']] | [', '.join(c['topics'])]"

screen credits_screen():
    tag menu
    use game_menu(_("Credits"), scroll="viewport"):
        vbox:
            spacing 8
            text _("Clinical Dominion MVP")
            text _("Design: Clinical Simulation Team")
            text _("Engine: Ren'Py")
            text _("Educational only — verify with guidelines.")

init python:
    config.name = "CLINICAL DOMINION"
    config.version = "0.1"
