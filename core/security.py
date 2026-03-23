import uuid
from fastapi import HTTPException, status

def validate_uuid(user_id: str) -> str:
    """
    Acts as a bouncer. Verifies that the string provided by the mobile app 
    is actually a valid UUID v4 format before we let it touch the database.
    """
    try:
        # Attempt to parse the string into a UUID object
        valid_uuid = uuid.UUID(user_id, version=4)
        return str(valid_uuid)
    except ValueError:
        # If it fails, someone is sending bad data. Reject the request immediately.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid User ID format. Nice try, hacker!"
        )