def extract_cast(data):
    """
    Extract cast information from TMDb data, including actor name, character, and gender.
    Includes both main cast and guest stars.

    Args:
        data (dict): The TMDb data.

    Returns:
        list: A list of dictionaries containing cast details.
    """
    def map_gender(gender_id):
        return {0: "Unknown", 1: "Female", 2: "Male", 3: "Nonbinary"}.get(gender_id, "Unknown")

    # Combine main cast and guest stars
    all_cast = data.get("credits", {}).get("cast", []) + data.get("credits", {}).get("guest_stars", [])
    return [
        {
            "name": person["name"],
            "character": person["character"],
            "gender": map_gender(person.get("gender"))  # Convert gender ID to string
        }
        for person in all_cast
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
    Includes both main cast and guest stars.

    Args:
        data (dict): The TMDb data.

    Returns:
        list: A list of character names.
    """
    # Combine main cast and guest stars
    all_cast = data.get("credits", {}).get("cast", []) + data.get("credits", {}).get("guest_stars", [])
    return [cast_member["character"] for cast_member in all_cast]
