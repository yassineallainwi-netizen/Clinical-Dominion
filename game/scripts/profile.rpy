init -2 python:
    import datetime

    RANKS = ["Bronze", "Silver", "Gold", "Platinum", "Diamond"]

    def ensure_profile_defaults():
        if not hasattr(persistent, "profile_name"):
            persistent.profile_name = "Resident"
        if not hasattr(persistent, "xp"):
            persistent.xp = 0
        if not hasattr(persistent, "level"):
            persistent.level = 1
        if not hasattr(persistent, "coins"):
            persistent.coins = 0
        if not hasattr(persistent, "rank"):
            persistent.rank = "Bronze"
        if not hasattr(persistent, "daily_streak"):
            persistent.daily_streak = 0
        if not hasattr(persistent, "last_played_date"):
            persistent.last_played_date = None
        if not hasattr(persistent, "diagnostic_streak"):
            persistent.diagnostic_streak = 0
        if not hasattr(persistent, "leaderboard"):
            persistent.leaderboard = []
        if not hasattr(persistent, "weak_areas"):
            persistent.weak_areas = {}
        if not hasattr(persistent, "show_dosing"):
            persistent.show_dosing = True
        if not hasattr(persistent, "optional_timer_intern"):
            persistent.optional_timer_intern = False

    def xp_to_next_level(level):
        return 100 + (level - 1) * 50

    def update_level_and_rank():
        while persistent.xp >= xp_to_next_level(persistent.level):
            persistent.xp -= xp_to_next_level(persistent.level)
            persistent.level += 1
            persistent.coins += 25

        if persistent.level >= 25:
            persistent.rank = "Diamond"
        elif persistent.level >= 18:
            persistent.rank = "Platinum"
        elif persistent.level >= 12:
            persistent.rank = "Gold"
        elif persistent.level >= 6:
            persistent.rank = "Silver"
        else:
            persistent.rank = "Bronze"

    def update_daily_streak():
        today = datetime.date.today()
        if persistent.last_played_date is None:
            persistent.daily_streak = 1
        else:
            try:
                last = datetime.date.fromisoformat(persistent.last_played_date)
                delta = (today - last).days
                if delta == 1:
                    persistent.daily_streak += 1
                elif delta > 1:
                    persistent.daily_streak = 1
            except Exception:
                persistent.daily_streak = 1

        persistent.last_played_date = today.isoformat()

    def add_to_leaderboard(entry):
        persistent.leaderboard.append(entry)
        persistent.leaderboard = sorted(
            persistent.leaderboard,
            key=lambda e: (e.get("score", 0), e.get("stability_end", 0)),
            reverse=True,
        )[:20]

    def register_weak_areas(topics, score):
        if score >= 70:
            return
        for topic in topics:
            persistent.weak_areas[topic] = persistent.weak_areas.get(topic, 0) + 1

    def grant_case_rewards(result):
        base_xp = 50 + int(result["score"] * 1.2)
        if result["outcome"] == "Success":
            bonus = 40
            persistent.diagnostic_streak += 1
        elif result["outcome"] == "Partial":
            bonus = 15
            persistent.diagnostic_streak = 0
        else:
            bonus = 0
            persistent.diagnostic_streak = 0

        streak_bonus = min(50, persistent.diagnostic_streak * 5)
        total_xp = base_xp + bonus + streak_bonus
        coins = int(result["score"] / 4) + (5 if result["outcome"] == "Success" else 0)

        persistent.xp += total_xp
        persistent.coins += coins
        update_level_and_rank()
        renpy.save_persistent()

        return total_xp, coins
