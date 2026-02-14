# Late style override to prevent DynamicImage lookups for missing gui/button assets.
# Keeps menus functional in MVP builds without bundled button png files.

init 1000:
    style button:
        background Solid("#1f2937")
        hover_background Solid("#374151")
        insensitive_background Solid("#111827")
        selected_background Solid("#334155")
        selected_hover_background Solid("#475569")
        selected_insensitive_background Solid("#1f2937")

    style button_text:
        color "#f9fafb"
        hover_color "#ffffff"
        insensitive_color "#9ca3af"

    style navigation_button is button
    style navigation_button_text is button_text
    style main_menu_button is button
    style main_menu_button_text is button_text
