def score_deviation(text: str) -> int:
    t = text.lower()

    high_terms = ["override", "bypass", "disable", "force", "break", "root", "kill"]
    if any(term in t for term in high_terms):
        return 7

    moderate_terms = ["contradiction", "deviation", "conflict", "reverse", "invert"]
    if any(term in t for term in moderate_terms):
        return 5

    return 3
