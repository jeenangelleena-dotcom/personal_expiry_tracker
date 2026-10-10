from database.mongodb import get_objects_collection


def create_object(object_data):
    """
    Create a new personal object.
    """

    objects = get_objects_collection()

    result = objects.insert_one(object_data)

    return result.inserted_id


def get_object_by_id(object_id):
    """
    Find one object using its MongoDB ID.
    """

    objects = get_objects_collection()

    return objects.find_one({
        "_id": object_id
    })


def get_objects_by_user(user_id):
    """
    Return all objects belonging to a user.
    """

    objects = get_objects_collection()

    return list(
        objects.find({
            "user_id": user_id
        })
    )


def get_all_objects():
    """
    Return all stored objects.
    """

    objects = get_objects_collection()

    return list(objects.find())


def update_object(object_id, update_data):
    """
    Update an existing object.
    """

    objects = get_objects_collection()

    result = objects.update_one(
        {
            "_id": object_id
        },
        {
            "$set": update_data
        }
    )

    return result.modified_count


def delete_object(object_id):
    """
    Delete an object.
    """

    objects = get_objects_collection()

    result = objects.delete_one({
        "_id": object_id
    })

    return result.deleted_count