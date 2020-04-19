from datetime import date


def clean_whitespace(lastname):
    string_split = lastname.split()
    return " ".join(string_split)

def validate_lastname(lastname):
    char_len = len(lastname) < 16
    not_blank = lastname != ""
    passed_both_tests = char_len and not_blank
    return passed_both_tests

def format_lastname(idx, lastname):
    today = date.today().strftime("%Y%m%d")
    lastname["lastname"] = clean_whitespace(lastname["lastname"])
    lastname["niche"] = (
        clean_whitespace(lastname["niche"]).replace(" ", "-").lower()
    )
    # Add two because we're not counting headers or 0.
    lastname["row"] = idx + 2
    lastname["name"] = f"{lastname['niche']}_{lastname['row']}_{today}"
    return lastname