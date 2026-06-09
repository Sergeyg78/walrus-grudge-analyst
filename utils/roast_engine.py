"""
Roast & Grudge Engine — Claude claude-haiku-4-5-20251001 powered.
Free-tier friendly: short prompts, max_tokens capped at 200.
"""

import anthropic


def _client(api_key: str):
    return anthropic.Anthropic(api_key=api_key)


def _call(api_key: str, system: str, user: str, max_tokens: int = 200) -> str:
    msg = _client(api_key).messages.create(
        model="claude-haiku-4-5",
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return msg.content[0].text


def get_roast(api_key, username, prediction, actual_result, grudge_log, stats) -> str:
    past = "\n".join(
        [f"- {g['date']}: {g['prediction']} (wrong)" for g in grudge_log[-3:]]
    ) or "First wrong call."

    return _call(api_key,
        "You are a savage but funny FIFA World Cup 2026 prediction analyst. "
        "Roast wrong predictions in under 3 sentences. Be football-specific and brutal but fun. "
        "Reference past failures from the grudge log when available.",
        f"User: {username}\nPredicted: '{prediction}'\nActual: '{actual_result}'\n"
        f"Record: {stats.get('correct',0)}W/{stats.get('wrong',0)}L ({stats.get('win_rate','0%')})\n"
        f"Past failures:\n{past}\nRoast them!"
    )


def get_praise(api_key, username, prediction, stats, grudge_log) -> str:
    past = "\n".join([f"- {g['prediction']}" for g in grudge_log[-2:]]) or "None yet."
    return _call(api_key,
        "You give VERY grudging praise for correct predictions — always reminding them of past failures. "
        "Under 3 sentences. Football-specific.",
        f"User: {username} got '{prediction}' RIGHT.\n"
        f"Record: {stats.get('correct',0)}W/{stats.get('wrong',0)}L\n"
        f"Past wrong calls I still hold against them:\n{past}\nGrudging praise:"
    )


def get_debate_response(api_key, username, hot_take, past_takes) -> str:
    history = "\n".join(
        [f"- \"{t['take']}\" ({t['date']})" for t in past_takes[-4:]]
    ) or "No past takes."
    return _call(api_key,
        "You are a fiery WC2026 debate partner. Counter hot takes with logic and stats. "
        "Call out contradictions with past takes. Under 4 sentences. Direct and football-savvy.",
        f"{username} says: \"{hot_take}\"\nTheir past takes:\n{history}\nCounter this or call out contradictions:"
    )


def get_grudge_summary(api_key, username, grudge_log, stats) -> str:
    if not grudge_log:
        return f"No grudges yet for {username}... but I'm watching. 👀"
    failures = "\n".join(
        [f"- {g['date']}: predicted '{g['prediction']}' but '{g['actual']}' happened"
         for g in grudge_log]
    )
    return _call(api_key,
        "Generate a brutal but funny grudge report summarising all prediction failures. Under 5 sentences.",
        f"User: {username}\nRecord: {stats.get('correct',0)}W/{stats.get('wrong',0)}L "
        f"({stats.get('win_rate','0%')})\nAll failures:\n{failures}",
        max_tokens=300
    )
