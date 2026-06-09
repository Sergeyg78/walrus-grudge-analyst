"""
FIFA World Cup 2026 Data
Groups, fixtures, and teams for prediction context.
"""

WC2026_GROUPS = {
    "Group A": ["USA", "Ecuador", "Panama", "Albania"],
    "Group B": ["Argentina", "Chile", "Peru", "Canada"],
    "Group C": ["Brazil", "Colombia", "Uruguay", "Bolivia"],
    "Group D": ["England", "Serbia", "Slovakia", "Netherlands"],
    "Group E": ["France", "Belgium", "Israel", "Paraguay"],
    "Group F": ["Spain", "Portugal", "Croatia", "Morocco"],
    "Group G": ["Germany", "Japan", "Mexico", "South Africa"],
    "Group H": ["Italy", "Australia", "Ivory Coast", "Honduras"],
    "Group I": ["Senegal", "Cameroon", "Ghana", "New Zealand"],
    "Group J": ["Saudi Arabia", "South Korea", "Iran", "Wales"],
    "Group K": ["Qatar", "Costa Rica", "Jamaica", "Benin"],
    "Group L": ["Tunisia", "Venezuela", "Cuba", "Uzbekistan"],
}

ALL_TEAMS = sorted(set(team for teams in WC2026_GROUPS.values() for team in teams))

PREDICTION_TEMPLATES = [
    "{team1} to win Group {group}",
    "{team1} to beat {team2}",
    "{team1} to reach the Quarter Finals",
    "{team1} to reach the Semi Finals",
    "{team1} to win the World Cup",
    "{team1} vs {team2} — {team1} wins",
    "{team1} vs {team2} — Draw",
    "{team1} to be top scorer",
    "{team1} to be eliminated in Group Stage",
    "Golden Boot: {team1} player scores 5+ goals",
]

NOTABLE_MATCHES = [
    "USA vs Ecuador (Group A)",
    "Argentina vs Chile (Group B)",
    "Brazil vs Colombia (Group C)",
    "England vs Netherlands (Group D)",
    "France vs Belgium (Group E)",
    "Spain vs Portugal (Group F)",
    "Germany vs Japan (Group G)",
    "Italy vs Australia (Group H)",
    "Senegal vs Cameroon (Group I)",
    "South Korea vs Iran (Group J)",
    "World Cup Final",
    "Semi Final 1",
    "Semi Final 2",
    "Quarter Final",
    "Round of 16",
]

HOST_CITIES = [
    "New York/New Jersey", "Los Angeles", "Dallas", "San Francisco Bay Area",
    "Miami", "Atlanta", "Seattle", "Houston", "Philadelphia", "Kansas City",
    "Boston", "Vancouver", "Toronto", "Guadalajara", "Mexico City", "Monterrey",
]

TOURNAMENT_INFO = {
    "name": "FIFA World Cup 2026",
    "hosts": ["USA", "Canada", "Mexico"],
    "dates": "June 11 – July 19, 2026",
    "teams": 48,
    "matches": 104,
    "final_venue": "MetLife Stadium, New York/New Jersey",
}
