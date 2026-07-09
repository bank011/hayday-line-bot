KEYWORDS = [
    "update",
    "event",
    "maintenance",
    "farm pass",
    "double coin",
    "double xp",
    "valley",
    "derby",
    "birthday",
    "new decoration",
]


def is_important(title):

    t = title.lower()

    for k in KEYWORDS:
        if k in t:
            return True

    return False
