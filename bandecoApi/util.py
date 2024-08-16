import re

def format_names(text):
    """
    Formats the name of a meal by capitalizing the first letter and 
    lowercasing the rest. It also replaces any matched abbreviations 
    with their corresponding full names.

    Parameters
    ----------
    text : str
        The description of the meal.

    Returns
    -------
    str
        The formatted meal name.
    """
    restaurants = {
        'ra': 'RA',
        'rs': 'RS',
        'ru': 'RU',
        'hc': 'HC',
    }

    # Capitalize the first letter of the text and lowercase the rest
    formatted_text = text[0].upper() + text[1:].lower()

    # Function to replace matched abbreviation with its corresponding full name
    def replace_abbr(match):
        abbr = match.group(0).lower()
        return restaurants.get(abbr, match.group(0))

    # Use regex to find and replace whole word matches
    pattern = re.compile(r'\b(?:' + '|'.join(re.escape(key) for key in restaurants.keys()) + r')\b', re.IGNORECASE)

    formatted_text = pattern.sub(replace_abbr, formatted_text)

    return formatted_text



