def extract_cast(data):
    """
    Extract cast information from TMDb data.

    Args:
        data (dict): The TMDb data.

    Returns:
        list: A list of dictionaries containing cast details.
    """
    return [
        {"name": person["name"], "character": person["character"]}
        for person in data.get("credits", {}).get("cast", [])
    ]

def extract_genres(data):
    """
    Extract genres from TMDb data.

    Args:
        data (dict): The TMDb data.

    Returns:
        list: A list of genre names.
    """
    return [genre["name"] for genre in data.get("genres", [])]

def extract_character_names(data):
    """
    Extract character names from TMDb data.

    Args:
        data (dict): The TMDb data.

    Returns:
        list: A list of character names.
    """
    return [cast_member["character"] for cast_member in data.get("credits", {}).get("cast", [])]
