def create_actor_entry(actor_name, role, gender_id):
    """
    Creates a dictionary entry for an actor with their name, role, and gender ID.

    Args:
        actor_name (str): The name of the actor.
        role (str): The role played by the actor.
        gender_id (int): The gender ID of the actor.

    Returns:
        dict: A dictionary containing the actor's details.
    """
    return {
        "actor": actor_name,
        "role": role,
        "gender_id": gender_id
    }

def main():
    """
    Main function to process multiple actor entries based on user input.
    """
    num_entries = int(input("How many actor entries would you like to process? "))
    actor_entries = []

    for _ in range(num_entries):
        actor_name = input("Enter actor name: ")
        role = input("Enter role: ")
        gender_id = int(input("Enter gender ID: "))
        actor_entries.append(create_actor_entry(actor_name, role, gender_id))

    print("All actor entries:")
    print(actor_entries)

# Example usage:
if __name__ == "__main__":
    main()