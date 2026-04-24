import json
from types import SimpleNamespace

from django.test import RequestFactory, SimpleTestCase

from library.api_helpers import (
    duplicate_error,
    method_not_allowed,
    not_found_error,
    parse_json_body,
    serialize_entry,
    serialize_user,
    unauthorized_error,
    validation_error,
)
from library.models import LibraryEntry
from library.validators import (
    validate_create_payload,
    validate_patch_payload,
    validate_put_payload,
)


def response_json(response):
    return json.loads(response.content.decode("utf-8"))


def make_model_method_test(attrs, method_name, expected):
    def test(self):
        entry = LibraryEntry(**attrs)

        result = getattr(entry, method_name)()

        self.assertEqual(result, expected)

    return test


class Extra200ModelLengthTests(SimpleTestCase):
    pass


LENGTH_CASES = [
    (f"generated_length_{number}", f"game-{number}", len(f"game-{number}"))
    for number in range(1, 31)
]

for case_name, external_game_id, expected in LENGTH_CASES:
    setattr(
        Extra200ModelLengthTests,
        f"test_extra_200_{case_name}",
        make_model_method_test(
            {"external_game_id": external_game_id},
            "external_id_length",
            expected,
        ),
    )


class Extra200ModelUpperTests(SimpleTestCase):
    pass


UPPER_CASES = [
    (
        f"generated_upper_{number}",
        f"game-{number}-abc",
        f"GAME-{number}-ABC",
    )
    for number in range(1, 31)
]

for case_name, external_game_id, expected in UPPER_CASES:
    setattr(
        Extra200ModelUpperTests,
        f"test_extra_200_{case_name}",
        make_model_method_test(
            {"external_game_id": external_game_id},
            "external_id_upper",
            expected,
        ),
    )


class Extra200ModelHoursTests(SimpleTestCase):
    pass


def expected_hours_label(hours_played):
    if hours_played <= 0:
        return "none"
    if hours_played < 10:
        return "low"
    return "high"


HOURS_CASES = [
    (
        f"generated_hours_{hours_played}".replace("-", "minus_"),
        hours_played,
        expected_hours_label(hours_played),
    )
    for hours_played in range(-10, 20)
]

for case_name, hours_played, expected in HOURS_CASES:
    setattr(
        Extra200ModelHoursTests,
        f"test_extra_200_{case_name}",
        make_model_method_test(
            {"hours_played": hours_played},
            "hours_played_label",
            expected,
        ),
    )


class Extra200ModelStatusTests(SimpleTestCase):
    pass


STATUS_CASES = [
    ("status_wishlist", "wishlist", 0),
    ("status_playing", "playing", 1),
    ("status_completed", "completed", 2),
    ("status_dropped", "dropped", 3),
    ("status_empty", "", -1),
    ("status_paused", "paused", -1),
    ("status_upper_playing", "PLAYING", -1),
    ("status_trailing_space", "playing ", -1),
    ("status_leading_space", " completed", -1),
    ("status_none", None, -1),
    ("status_number_one", 1, -1),
    ("status_number_zero", 0, -1),
    ("status_true", True, -1),
    ("status_false", False, -1),
    ("status_abandoned", "abandoned", -1),
    ("status_finished", "finished", -1),
    ("status_todo", "todo", -1),
    ("status_newline", "wishlist\n", -1),
    ("status_dot", "dropped.", -1),
    ("status_slash", "completed/dropped", -1),
]

for case_name, status, expected in STATUS_CASES:
    setattr(
        Extra200ModelStatusTests,
        f"test_extra_200_{case_name}",
        make_model_method_test({"status": status}, "status_value", expected),
    )


def make_validator_test(validator, payload, expected):
    def test(self):
        self.assertEqual(validator(payload), expected)

    return test


class Extra200CreateValidValidatorTests(SimpleTestCase):
    pass


VALID_STATUSES = ["wishlist", "playing", "completed", "dropped"]
CREATE_VALID_CASES = [
    (
        f"create_valid_{number}",
        {
            "external_game_id": f"valid-game-{number}",
            "status": VALID_STATUSES[number % len(VALID_STATUSES)],
            "hours_played": number,
        },
        {},
    )
    for number in range(20)
]

for case_name, payload, expected in CREATE_VALID_CASES:
    setattr(
        Extra200CreateValidValidatorTests,
        f"test_extra_200_{case_name}",
        make_validator_test(validate_create_payload, payload, expected),
    )


class Extra200CreateInvalidValidatorTests(SimpleTestCase):
    pass


VALID_CREATE_PAYLOAD = {
    "external_game_id": "base-game",
    "status": "wishlist",
    "hours_played": 0,
}

CREATE_INVALID_CASES = [
    (
        "create_missing_external_game_id",
        {"status": "wishlist", "hours_played": 0},
        {"external_game_id": "required"},
    ),
    (
        "create_missing_status",
        {"external_game_id": "base-game", "hours_played": 0},
        {"status": "required"},
    ),
    (
        "create_missing_hours_played",
        {"external_game_id": "base-game", "status": "wishlist"},
        {"hours_played": "required"},
    ),
]

for index, value in enumerate([1, 1.5, True, [], None], start=1):
    payload = {**VALID_CREATE_PAYLOAD, "external_game_id": value}
    CREATE_INVALID_CASES.append(
        (
            f"create_external_game_id_wrong_type_{index}",
            payload,
            {"external_game_id": "must_be_string"},
        )
    )

for index, value in enumerate([1, 1.5, True, [], None], start=1):
    payload = {**VALID_CREATE_PAYLOAD, "status": value}
    CREATE_INVALID_CASES.append(
        (
            f"create_status_wrong_type_{index}",
            payload,
            {"status": "must_be_string"},
        )
    )

for index, value in enumerate(
    ["paused", "PLAYING", "", " playing", "completed ", "done", "0"],
    start=1,
):
    payload = {**VALID_CREATE_PAYLOAD, "status": value}
    CREATE_INVALID_CASES.append(
        (
            f"create_status_invalid_choice_{index}",
            payload,
            {"status": "invalid_choice"},
        )
    )

for index, value in enumerate(["1", 1.5, True, [], None], start=1):
    payload = {**VALID_CREATE_PAYLOAD, "hours_played": value}
    CREATE_INVALID_CASES.append(
        (
            f"create_hours_wrong_type_{index}",
            payload,
            {"hours_played": "must_be_integer"},
        )
    )

for index, value in enumerate([-1, -2, -5, -10, -99], start=1):
    payload = {**VALID_CREATE_PAYLOAD, "hours_played": value}
    CREATE_INVALID_CASES.append(
        (
            f"create_hours_negative_{index}",
            payload,
            {"hours_played": "must_be_greater_or_equal_to_0"},
        )
    )

for case_name, payload, expected in CREATE_INVALID_CASES:
    setattr(
        Extra200CreateInvalidValidatorTests,
        f"test_extra_200_{case_name}",
        make_validator_test(validate_create_payload, payload, expected),
    )


class Extra200PutPatchValidatorTests(SimpleTestCase):
    pass


PUT_PATCH_CASES = [
    (
        "put_missing_status_and_hours",
        validate_put_payload,
        {"external_game_id": "game-1"},
        {"status": "required", "hours_played": "required"},
    ),
    (
        "put_missing_external_and_hours",
        validate_put_payload,
        {"status": "playing"},
        {"external_game_id": "required", "hours_played": "required"},
    ),
    (
        "put_missing_external_and_status",
        validate_put_payload,
        {"hours_played": 4},
        {"external_game_id": "required", "status": "required"},
    ),
    (
        "put_invalid_all_fields",
        validate_put_payload,
        {"external_game_id": 2, "status": [], "hours_played": "4"},
        {
            "external_game_id": "must_be_string",
            "status": "must_be_string",
            "hours_played": "must_be_integer",
        },
    ),
    (
        "put_unknown_title",
        validate_put_payload,
        {
            "external_game_id": "game-1",
            "status": "playing",
            "hours_played": 4,
            "title": "Title",
        },
        {"title": "unknown_field"},
    ),
    (
        "put_unknown_rating",
        validate_put_payload,
        {
            "external_game_id": "game-1",
            "status": "playing",
            "hours_played": 4,
            "rating": 5,
        },
        {"rating": "unknown_field"},
    ),
    (
        "put_invalid_status",
        validate_put_payload,
        {"external_game_id": "game-1", "status": "paused", "hours_played": 4},
        {"status": "invalid_choice"},
    ),
    (
        "put_negative_hours",
        validate_put_payload,
        {"external_game_id": "game-1", "status": "playing", "hours_played": -1},
        {"hours_played": "must_be_greater_or_equal_to_0"},
    ),
    (
        "patch_valid_status",
        validate_patch_payload,
        {"status": "playing"},
        {},
    ),
    (
        "patch_valid_hours",
        validate_patch_payload,
        {"hours_played": 8},
        {},
    ),
    (
        "patch_valid_status_and_hours",
        validate_patch_payload,
        {"status": "completed", "hours_played": 30},
        {},
    ),
    (
        "patch_rejects_external_game_id",
        validate_patch_payload,
        {"external_game_id": "game-2"},
        {"external_game_id": "unknown_field"},
    ),
    (
        "patch_rejects_title",
        validate_patch_payload,
        {"title": "Title"},
        {"title": "unknown_field"},
    ),
    (
        "patch_rejects_invalid_status",
        validate_patch_payload,
        {"status": "paused"},
        {"status": "invalid_choice"},
    ),
    (
        "patch_rejects_upper_status",
        validate_patch_payload,
        {"status": "PLAYING"},
        {"status": "invalid_choice"},
    ),
    (
        "patch_rejects_string_hours",
        validate_patch_payload,
        {"hours_played": "8"},
        {"hours_played": "must_be_integer"},
    ),
    (
        "patch_rejects_bool_hours",
        validate_patch_payload,
        {"hours_played": True},
        {"hours_played": "must_be_integer"},
    ),
    (
        "patch_rejects_negative_hours",
        validate_patch_payload,
        {"hours_played": -3},
        {"hours_played": "must_be_greater_or_equal_to_0"},
    ),
    (
        "patch_rejects_two_unknown_fields",
        validate_patch_payload,
        {"title": "Title", "rating": 5},
        {"title": "unknown_field", "rating": "unknown_field"},
    ),
    (
        "patch_rejects_unknown_and_invalid_value",
        validate_patch_payload,
        {"rating": 5, "status": "paused"},
        {"rating": "unknown_field", "status": "invalid_choice"},
    ),
]

for case_name, validator, payload, expected in PUT_PATCH_CASES:
    setattr(
        Extra200PutPatchValidatorTests,
        f"test_extra_200_{case_name}",
        make_validator_test(validator, payload, expected),
    )


class Extra200ApiHelperTests(SimpleTestCase):
    pass


def make_response_test(response_factory, expected_status, expected_body):
    def test(self):
        response = response_factory()

        self.assertEqual(response.status_code, expected_status)
        self.assertEqual(response_json(response), expected_body)

    return test


HELPER_RESPONSE_CASES = [
    (
        "validation_error_without_details",
        lambda: validation_error(),
        400,
        {"error": "validation_error", "message": "Datos de entrada inv\u00e1lidos"},
    ),
    (
        "validation_error_with_details",
        lambda: validation_error({"field": "required"}),
        400,
        {
            "error": "validation_error",
            "message": "Datos de entrada inv\u00e1lidos",
            "details": {"field": "required"},
        },
    ),
    (
        "duplicate_error",
        duplicate_error,
        400,
        {
            "error": "duplicate_entry",
            "message": "El juego ya existe en la biblioteca",
            "details": {"external_game_id": "duplicate"},
        },
    ),
    (
        "not_found_error",
        not_found_error,
        404,
        {"error": "not_found", "message": "La entrada solicitada no existe"},
    ),
    (
        "unauthorized_error",
        lambda: unauthorized_error("No autenticado"),
        401,
        {"error": "unauthorized", "message": "No autenticado"},
    ),
    (
        "method_not_allowed",
        method_not_allowed,
        405,
        {"error": "method_not_allowed"},
    ),
]

for case_name, response_factory, expected_status, expected_body in HELPER_RESPONSE_CASES:
    setattr(
        Extra200ApiHelperTests,
        f"test_extra_200_helper_{case_name}",
        make_response_test(response_factory, expected_status, expected_body),
    )


def make_parse_json_test(raw_body, expected_data, expected_status, expected_body):
    def test(self):
        request = RequestFactory().post(
            "/test/",
            data=raw_body,
            content_type="application/json",
        )

        data, error_response = parse_json_body(request)

        self.assertEqual(data, expected_data)
        if expected_status is None:
            self.assertIsNone(error_response)
        else:
            self.assertEqual(error_response.status_code, expected_status)
            self.assertEqual(response_json(error_response), expected_body)

    return test


PARSE_JSON_CASES = [
    ('{"name": "ana"}', {"name": "ana"}, None, None),
    ('{"hours_played": 0}', {"hours_played": 0}, None, None),
    ('{"status": "playing"}', {"status": "playing"}, None, None),
    (
        '{"name":',
        None,
        400,
        {
            "error": "validation_error",
            "message": "Datos de entrada inv\u00e1lidos",
            "details": {"body": "invalid_json"},
        },
    ),
    (
        "[]",
        None,
        400,
        {
            "error": "validation_error",
            "message": "Datos de entrada inv\u00e1lidos",
            "details": {"body": "invalid_format"},
        },
    ),
    (
        '"text"',
        None,
        400,
        {
            "error": "validation_error",
            "message": "Datos de entrada inv\u00e1lidos",
            "details": {"body": "invalid_format"},
        },
    ),
    (
        "{}",
        None,
        400,
        {
            "error": "validation_error",
            "message": "Datos de entrada inv\u00e1lidos",
            "details": {"body": "empty"},
        },
    ),
]

for index, (raw_body, expected_data, expected_status, expected_body) in enumerate(
    PARSE_JSON_CASES,
    start=1,
):
    setattr(
        Extra200ApiHelperTests,
        f"test_extra_200_parse_json_{index}",
        make_parse_json_test(raw_body, expected_data, expected_status, expected_body),
    )


def make_serialize_entry_test(entry, expected):
    def test(self):
        self.assertEqual(serialize_entry(entry), expected)

    return test


SERIALIZE_ENTRY_CASES = [
    LibraryEntry(
        id=number,
        external_game_id=f"game-{number}",
        status=VALID_STATUSES[number % len(VALID_STATUSES)],
        hours_played=number * 2,
    )
    for number in range(1, 5)
]

for entry in SERIALIZE_ENTRY_CASES:
    setattr(
        Extra200ApiHelperTests,
        f"test_extra_200_serialize_entry_{entry.id}",
        make_serialize_entry_test(
            entry,
            {
                "id": entry.id,
                "external_game_id": entry.external_game_id,
                "status": entry.status,
                "hours_played": entry.hours_played,
            },
        ),
    )


def make_serialize_user_test(user, expected):
    def test(self):
        self.assertEqual(serialize_user(user), expected)

    return test


for number in range(1, 4):
    user = SimpleNamespace(id=number, username=f"user_{number}", password="hidden")
    setattr(
        Extra200ApiHelperTests,
        f"test_extra_200_serialize_user_{number}",
        make_serialize_user_test(
            user,
            {
                "id": number,
                "username": f"user_{number}",
            },
        ),
    )