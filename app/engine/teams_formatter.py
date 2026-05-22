def build_teams_message(intervention: dict) -> str:
    """
    Build a simple, Teams-friendly text message.
    """

    # Shorten reasoning trace for readability
    short_trace = intervention.get("reasoning_trace", [])[:4]

    reasoning_summary = "\n".join(short_trace)

    return (
        f"**SAAM Intervention**\n"
        f"Cue: {intervention['cue']}\n\n"
        f"{intervention['message']}\n\n"
        f"**Reasoning Summary**\n"
        f"{reasoning_summary}"
    )
