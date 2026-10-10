from database.mongodb import get_users_collection


def create_user(user_data):
    """
    Create a new user in MongoDB.
    """
    return get_users_collection().insert_one(user_data)


def find_user_by_email(email):
    """
    Find a user using their email address.
    """
    return get_users_collection().find_one({
        "email": email
    })


def get_user_by_email(email):
    """
    Find a user using their email address.
    Alternative function name for compatibility.
    """
    return find_user_by_email(email)


def get_user_by_id(user_id):
    """
    Find a user using their MongoDB ObjectId.
    """
    return get_users_collection().find_one({
        "_id": user_id
    })


def update_user(user_id, update_data):
    """
    Update an existing user's details.
    """
    return get_users_collection().update_one(
        {
            "_id": user_id
        },
        {
            "$set": update_data
        }
    )


def delete_user(user_id):
    """
    Delete a user from MongoDB.
    """
    return get_users_collection().delete_one({
        "_id": user_id
    })