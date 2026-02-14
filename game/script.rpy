label before_main_menu:
    $ ensure_profile_defaults()
    $ all_cases, diagnostics_errors = load_all_cases()
    return

label start:
    scene black
    call hub
    return

label hub:
    menu:
        "CLINICAL DOMINION — Master the Case.":
            pass
        "Play":
            call screen choose_case_screen
            jump hub
        "Case Library":
            call screen case_library_screen
            jump hub
        "Profile":
            call screen profile_screen
            jump hub
        "Settings":
            call screen custom_settings
            jump hub
        "Credits":
            call screen credits_screen
            jump hub
        "Leaderboard":
            call screen leaderboard_screen
            jump hub
        "Diagnostics":
            jump diagnostics
        "Quit":
            return

label start_selected_case:
    if selected_case is None:
        $ renpy.notify(_("No case selected."))
        jump hub
    $ start_case_runtime(selected_case, selected_difficulty)
    jump run_case

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
    config.version = "1.1.0"
