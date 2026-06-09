"""
Roast & Grudge Engine
Uses Claude claude-haiku-4-5-20251001 to generate savage roasts and track grudges.
Designed to be cost-efficient on free-tier Anthropic API keys.
"""

import anthropic
from typing import Optional


def get_roast(
    api_key: str,
    username: str,
    prediction: str,
    actual_result: str,
    grudge_log: list,
    stats: dict,
) -> str:
    """
    Generate a savage but fun roast for a wrong prediction.
    Includes grudge history context so the agent remembers past failures.
    """
    client = anthropic.Anthropic(api_key=api_key)

    past_failures = ""
    if grudge_log:
        recent = grudge_log[-3:]  # last 3 grudges for context
        past_failures = "\n".join(
            [f"- {g['date']}: {g['prediction']} (was wrong)" for g in recent]
        )

    system_prompt = """You are a savage but hilarious FIFA World Cup 2026 prediction analyst. 
Your job is to roast users when they get predictions wrong. You hold grudges — you remember 
past wrong calls and bring them up. Keep roasts under 3 sentences. Be funny, football-specific, 
and slightly brutal. Never be offensive about real people, just about the predictions."""

    user_prompt = f"""User: {username}
Their prediction: "{prediction}"
What actually happened: "{actual_result}"
Their record: {stats.get('correct', 0)} correct, {stats.get('wrong', 0)} wrong, 
win rate: {stats.get('win_rate', '0%')}

Past failures I remember (grudge log):
{past_failures if past_failures else "This is their first wrong call."}

Roast them for this wrong prediction. If they have past failures, reference at least one grudgingly."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{"role": "user", "content": user_prompt}],
        system=system_prompt,
    )
    return message.content[0].text


def get_praise(
    api_key: str,
    username: str,
    prediction: str,
    stats: dict,
    grudge_log: list,
) -> str:
    """
    Grudgingly praise a correct prediction — but still bring up past failures.
    """
    client = anthropic.Anthropic(api_key=api_key)

    past_failures = ""
    if grudge_log:
        recent = grudge_log[-2:]
        past_failures = "\n".join([f"- {g['prediction']}" for g in recent])

    system_prompt = """You are a reluctant, grudge-holding FIFA World Cup 2026 analyst. 
When someone gets a prediction right, you give VERY grudging praise — always bringing up their 
past failures to keep them humble. Keep it under 3 sentences. Be funny and football-specific."""

    user_prompt = f"""User: {username}
Correct prediction: "{prediction}"
Their record: {stats.get('correct', 0)} correct, {stats.get('wrong', 0)} wrong

Past wrong predictions I still hold grudges about:
{past_failures if past_failures else "No past failures yet — but I'm watching."}

Give very grudging praise for getting this one right."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=150,
        messages=[{"role": "user", "content": user_prompt}],
        system=system_prompt,
    )
    return message.content[0].text


def get_debate_response(
    api_key: str,
    username: str,
    hot_take: str,
    past_takes: list,
) -> str:
    """
    Engage in a debate, remembering past hot takes.
    """
    client = anthropic.Anthropic(api_key=api_key)

    history_context = ""
    if past_takes:
        history_context = "\n".join(
            [f"- \"{t['take']}\" (said on {t['date']})" for t in past_takes[-4:]]
        )

    system_prompt = """You are a fiery FIFA World Cup 2026 debate partner who never forgets 
what you've been told. You counter hot takes with stats, logic, and by calling out 
contradictions with past takes. Keep responses under 4 sentences. Be passionate but fair."""

    user_prompt = f"""User {username} says: "{hot_take}"

Their past hot takes I remember:
{history_context if history_context else "This is their first hot take."}

Counter this take OR call out if it contradicts their past opinions. Be direct and football-savvy."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{"role": "user", "content": user_prompt}],
        system=system_prompt,
    )
    return message.content[0].text


def get_grudge_summary(api_key: str, username: str, grudge_log: list, stats: dict) -> str:
    """
    Generate a brutal grudge report summarising all past failures.
    """
    client = anthropic.Anthropic(api_key=api_key)

    if not grudge_log:
        return f"No grudges yet for {username}... but I'm watching. 👀"

    failures = "\n".join(
        [f"- {g['date']}: predicted '{g['prediction']}' but '{g['actual']}' happened" 
         for g in grudge_log]
    )

    system_prompt = """You are a World Cup prediction grudge keeper. 
Summarise someone's prediction failures in a brutal but funny roast report. 
Keep it under 5 sentences. Reference specific wrong calls."""

    user_prompt = f"""Generate a grudge report for {username}.
Record: {stats.get('correct', 0)} correct / {stats.get('wrong', 0)} wrong 
({stats.get('win_rate', '0%')} win rate)

All their wrong predictions:
{failures}"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=250,
        messages=[{"role": "user", "content": user_prompt}],
        system=system_prompt,
    )
    return message.content[0].text
