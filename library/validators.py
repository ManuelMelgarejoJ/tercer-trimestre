# library/validators.py

VALID_STATUSES = {"wishlist", "playing", "completed"}


def validate_create_payload(payload):
    errors = {}

    # external_game_id
    if "external_game_id" not in payload:
        errors["external_game_id"] = "required"
    elif not isinstance(payload["external_game_id"], str):
        errors["external_game_id"] = "must_be_string"

    # status
    if "status" not in payload:
        errors["status"] = "required"
    elif not isinstance(payload["status"], str):
        errors["status"] = "must_be_string"
    elif payload["status"] not in VALID_STATUSES:
        errors["status"] = "invalid_choice"

    # hours_played
    if "hours_played" not in payload:
        errors["hours_played"] = "required"
    elif not isinstance(payload["hours_played"], int) or isinstance(payload["hours_played"], bool):
        errors["hours_played"] = "must_be_integer"
    elif payload["hours_played"] < 0:
        errors["hours_played"] = "must_be_greater_or_equal_to_0"

    return errors


def validate_put_payload(payload):
    errors = {}

    allowed_fields = {"external_game_id", "status", "hours_played"}

    # unknown fields
    for key in payload:
        if key not in allowed_fields:
            errors[key] = "unknown_field"

    # external_game_id
    if "external_game_id" not in payload:
        errors["external_game_id"] = "required"
    elif not isinstance(payload["external_game_id"], str):
        errors["external_game_id"] = "must_be_string"

    # status
    if "status" not in payload:
        errors["status"] = "required"
    elif not isinstance(payload["status"], str):
        errors["status"] = "must_be_string"
    elif payload["status"] not in VALID_STATUSES:
        errors["status"] = "invalid_choice"

    # hours_played
    if "hours_played" not in payload:
        errors["hours_played"] = "required"
    elif not isinstance(payload["hours_played"], int) or isinstance(payload["hours_played"], bool):
        errors["hours_played"] = "must_be_integer"
    elif payload["hours_played"] < 0:
        errors["hours_played"] = "must_be_greater_or_equal_to_0"

    return errors


def validate_patch_payload(payload):
    errors = {}

    allowed_fields = {"external_game_id", "status", "hours_played"}

    for key in payload:
        if key not in allowed_fields:
            errors[key] = "unknown_field"

    if "external_game_id" in payload:
        if not isinstance(payload["external_game_id"], str):
            errors["external_game_id"] = "must_be_string"

    if "status" in payload:
        if not isinstance(payload["status"], str):
            errors["status"] = "must_be_string"
        elif payload["status"] not in VALID_STATUSES:
            errors["status"] = "invalid_choice"

    if "hours_played" in payload:
        if not isinstance(payload["hours_played"], int) or isinstance(payload["hours_played"], bool):
            errors["hours_played"] = "must_be_integer"
        elif payload["hours_played"] < 0:
            errors["hours_played"] = "must_be_greater_or_equal_to_0"

    return errors


def validate_login_payload(payload):
    errors = {}

    if "username" not in payload:
        errors["username"] = "required"
    elif not isinstance(payload["username"], str):
        errors["username"] = "must_be_string"

    if "password" not in payload:
        errors["password"] = "required"
    elif not isinstance(payload["password"], str):
        errors["password"] = "must_be_string"

    return errors


def validate_password_change_payload(payload, user):
    errors = {}

    if "current_password" not in payload:
        errors["current_password"] = "required"
    elif not user.check_password(payload["current_password"]):
        errors["current_password"] = "incorrect"

    if "new_password" not in payload:
        errors["new_password"] = "required"
    elif len(payload["new_password"]) < 8:
        errors["new_password"] = "min_length_8"

    return errors
