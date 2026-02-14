init -1:
    image bg er = Solid("#1f2a44")
    image bg icu = Solid("#1d3a3a")
    image bg ward = Solid("#3a3a1d")
    image bg clinic = Solid("#3a1d3a")

    image char patient = Solid("#88a")
    image char nurse = Solid("#8a8")
    image char attending = Solid("#a88")

style panel_frame is frame:
    background Frame(Solid("#0f172aDD"), 12, 12)
    padding (18, 14)

screen hud_panel():
    frame style "panel_frame":
        xalign 0.02
        yalign 0.02
        has vbox
        text _("Difficulty: [selected_difficulty]")
        text _("Stability: [stability_view_text()]")
        text _("Step: [game_state['stepIndex']]")

screen case_node_screen(node):
    $ bg_name = "bg " + node.get("background", "ward")
    add bg_name
    add "char " + node.get("speaker", "patient") xpos 0.78 ypos 0.25 xsize 220 ysize 420

    use hud_panel

    frame style "panel_frame":
        xalign 0.5
        yalign 0.62
        xsize 1250
        has vbox
        spacing 10
        text tr(node.get("text", {})) size 34

        if node.get("labs"):
            frame style "panel_frame":
                xfill True
                text _("Labs/ABG: [tr(node['labs'])]") size 24

        if persistent.show_dosing and node.get("dosing"):
            frame style "panel_frame":
                xfill True
                text _("Educational only — verify with guidelines.") size 20 color "#ffd966"
                text tr(node.get("dosing", {})) size 20

    vbox:
        xalign 0.5
        yalign 0.92
        spacing 8
        for c in node.get("choices", []):
            textbutton tr(c.get("text", {})) action Return(c) xsize 1100

    if timer_enabled:
        frame style "panel_frame":
            xalign 0.95
            yalign 0.05
            text _("Time: [timer_left]s")

        timer 1.0 repeat True action [
            SetVariable("timer_left", timer_left - 1),
            If(timer_left <= 1, true=[SetVariable("timer_expired", True), Return(None)])
        ]

screen debrief_screen(total_xp, coins):
    tag menu
    add Solid("#101827")
    frame style "panel_frame":
        xalign 0.5
        yalign 0.5
        xsize 1300
        ysize 680
        has vbox
        spacing 10
        text _("Case Debrief") size 42
        text _("Outcome: [debrief_data['outcome']]")
        text _("Score: [debrief_data['score']] / 100")
        text _("Correct diagnosis: [debrief_data['correctDx']]")
        text _("What went well: [tr(selected_case['debrief']['wentWell'])]")
        text _("Critical misses: [tr(selected_case['debrief']['misses'])]")
        text _("Ideal management: [tr(selected_case['debrief']['idealPlan'])]")
        text _("XP gained: [total_xp] | Coins gained: [coins]")
        text _("Rank: [persistent.rank] | Level: [persistent.level]")
        text _("Breakdown DX [score_parts['dx']] / Stability [score_parts['stability']] / Critical [score_parts['critical']] / Resources [score_parts['resources']] / Time [score_parts['time']]") size 22
        textbutton _("Return to Main Menu") action MainMenu()

screen diagnostics_screen():
    tag menu
    use game_menu(_("Diagnostics"), scroll="viewport"):
        vbox:
            spacing 8
            text _("Loaded cases: [len(all_cases)]")
            if diagnostics_errors:
                text _("Validation errors:") color "#ff6666"
                for err in diagnostics_errors:
                    text err size 20
            else:
                text _("No validation errors.") color "#66ff99"

screen profile_hud():
    frame style "panel_frame":
        xalign 0.98
        yalign 0.02
        has vbox
        text _("[persistent.profile_name]")
        text _("Rank: [persistent.rank]")
        text _("Lvl [persistent.level]  XP [persistent.xp]/[xp_to_next_level(persistent.level)]")
        text _("Coins: [persistent.coins]")
        text _("Daily streak: [persistent.daily_streak]")

screen choose_case_screen():
    tag menu
    add Solid("#111827")
    use profile_hud
    frame style "panel_frame":
        xalign 0.5
        yalign 0.5
        xsize 1400
        ysize 760
        has hbox
        spacing 22

        vbox:
            spacing 10
            text _("Select Case") size 36
            viewport:
                mousewheel True
                draggable True
                ysize 600
                vbox:
                    spacing 6
                    for c in all_cases:
                        textbutton "[tr(c['title'])] ([c['specialty']])" action SetVariable("selected_case", c)

        vbox:
            spacing 12
            text _("Difficulty") size 32
            for d in DIFFICULTIES:
                textbutton d action SetVariable("selected_difficulty", d)
            text _("Selected: [selected_difficulty]")
            text _("Timer: [difficulty_timer_seconds(selected_difficulty)]s")
            textbutton _("Start") action [
                If(selected_case is None, true=Notify(_("Pick a case first."))),
                If(selected_case is not None, true=Jump("start_selected_case"))
            ]
            textbutton _("Back") action MainMenu()


screen case_load_error_screen():
    tag menu
    add Solid("#1f2937")
    frame style "panel_frame":
        xalign 0.5
        yalign 0.5
        xsize 1000
        has vbox
        spacing 10
        text _("Case loading issue") size 38
        text _("One or more case files failed validation. The game stayed safe and did not crash.")
        if diagnostics_errors:
            for err in diagnostics_errors:
                text err size 20
        textbutton _("Open Diagnostics") action ShowMenu("diagnostics_screen")
        textbutton _("Back to Main Menu") action Return()

screen runtime_error_screen(message):
    modal True
    frame style "panel_frame":
        xalign 0.5
        yalign 0.5
        xsize 1100
        has vbox
        spacing 10
        text _("Safe Runtime Fallback") size 36
        text "[message]"
        textbutton _("Continue to Debrief") action Return()
