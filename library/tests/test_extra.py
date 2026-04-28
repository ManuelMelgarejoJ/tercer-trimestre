import json

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase, override_settings

from library.models import LibraryEntry
from library.validators import (
    validate_create_payload,
    validate_login_payload,
    validate_password_change_payload,
    validate_patch_payload,
    validate_put_payload,
)


# ============================
#   MODEL TESTS (20)
# ============================

class TestExtraLibraryEntryModel(SimpleTestCase):
    pass


MODEL_LIMIT = 20
VALIDATOR_LIMIT = 15
PASSWORD_LIMIT = 3
API_LIMIT = 9


MODEL_METHOD_CASES = [
    ("length_single_char", {"external_game_id": "x"}, "external_id_length", 1),
    ("length_two_words", {"external_game_id": "game id"}, "external_id_length", 7),
    ("length_with_dash", {"external_game_id": "abc-123"}, "external_id_length", 7),
    ("length_with_spaces_inside", {"external_game_id": "a b c"}, "external_id_length", 5),
    ("length_leading_space", {"external_game_id": " abc"}, "external_id_length", 4),
    ("length_trailing_space", {"external_game_id": "abc "}, "external_id_length", 4),
    ("length_numeric_string", {"external_game_id": "00123"}, "external_id_length", 5),
    ("length_mixed_case", {"external_game_id": "AbC"}, "external_id_length", 3),
    ("length_max_field_size", {"external_game_id": "x" * 255}, "external_id_length", 255),
    ("length_letters_and_symbols", {"external_game_id": "g_1-2"}, "external_id_length", 5),
    ("upper_lowercase", {"external_game_id": "abc"}, "external_id_upper", "ABC"),
    ("upper_alphanumeric", {"external_game_id": "abc-123"}, "external_id_upper", "ABC-123"),
    ("upper_already_upper", {"external_game_id": "READY"}, "external_id_upper", "READY"),
    ("upper_mixed_words", {"external_game_id": "mixed CASE"}, "external_id_upper", "MIXED CASE"),
    ("upper_underscore", {"external_game_id": "with_under_score"}, "external_id_upper", "WITH_UNDER_SCORE"),
    ("upper_digits_first", {"external_game_id": "123abc"}, "external_id_upper", "123ABC"),
    ("upper_dash_name", {"external_game_id": "dash-name"}, "external_id_upper", "DASH-NAME"),
    ("upper_space_name", {"external_game_id": "space name"}, "external_id_upper", "SPACE NAME"),
    ("upper_repeated_letter", {"external_game_id": "xxxxx"}, "external_id_upper", "XXXXX"),
    ("upper_keeps_punctuation", {"external_game_id": "done!"}, "external_id_upper", "DONE!"),
]


def make_model_method_test(attrs, method_name, expected):
    def test(self):
        entry = LibraryEntry(**attrs)
        result = getattr(entry, method_name)()
        self.assertEqual(result, expected)
    return test


for case_name, attrs, method_name, expected in MODEL_METHOD_CASES[:MODEL_LIMIT]:
    setattr(
        TestExtraLibraryEntryModel,
        f"test_extra_model_{case_name}",
        make_model_method_test(attrs, method_name, expected),
    )


# ============================
#   VALIDATOR TESTS (15)
# ============================

class TestExtraValidator(SimpleTestCase):
    pass


VALIDATOR_CASES = [
    ("create_valid_wishlist_zero_hours", validate_create_payload,
     {"external_game_id": "game-1", "status": "wishlist", "hours_played": 0}, {}),
    ("create_valid_completed_many_hours", validate_create_payload,
     {"external_game_id": "game-2", "status": "completed", "hours_played": 99}, {}),
    ("create_missing_external_game_id", validate_create_payload,
     {"status": "wishlist", "hours_played": 0}, {"external_game_id": "required"}),
    ("create_external_game_id_must_be_string", validate_create_payload,
     {"external_game_id": 1, "status": "wishlist", "hours_played": 0}, {"external_game_id": "must_be_string"}),
    ("create_missing_status", validate_create_payload,
     {"external_game_id": "game-1", "hours_played": 0}, {"status": "required"}),
    ("create_status_must_be_string", validate_create_payload,
     {"external_game_id": "game-1", "status": 1, "hours_played": 0}, {"status": "must_be_string"}),
    ("create_status_invalid_choice", validate_create_payload,
     {"external_game_id": "game-1", "status": "paused", "hours_played": 0}, {"status": "invalid_choice"}),
    ("create_missing_hours", validate_create_payload,
     {"external_game_id": "game-1", "status": "wishlist"}, {"hours_played": "required"}),
    ("create_hours_must_be_integer", validate_create_payload,
     {"external_game_id": "game-1", "status": "wishlist", "hours_played": "1"}, {"hours_played": "must_be_integer"}),
    ("create_hours_bool_is_not_integer", validate_create_payload,
     {"external_game_id": "game-1", "status": "wishlist", "hours_played": True}, {"hours_played": "must_be_integer"}),
    ("create_hours_negative", validate_create_payload,
     {"external_game_id": "game-1", "status": "wishlist", "hours_played": -1}, {"hours_played": "must_be_greater_or_equal_to_0"}),
    ("create_empty_payload_marks_all_required", validate_create_payload,
     {}, {"external_game_id": "required", "status": "required", "hours_played": "required"}),
    ("put_valid_full_payload", validate_put_payload,
     {"external_game_id": "game-1", "status": "playing", "hours_played": 3}, {}),
    ("put_rejects_unknown_field", validate_put_payload,
     {"external_game_id": "game-1", "status": "playing", "hours_played": 3, "title": "X"}, {"title": "unknown_field"}),
    ("put_empty_payload_marks_all_required", validate_put_payload,
     {}, {"external_game_id": "required", "status": "required", "hours_played": "required"}),
]


def make_validator_test(validator, payload, expected):
    def test(self):
        self.assertEqual(validator(payload), expected)
    return test


for case_name, validator, payload, expected in VALIDATOR_CASES[:VALIDATOR_LIMIT]:
    setattr(
        TestExtraValidator,
        f"test_extra_validator_{case_name}",
        make_validator_test(validator, payload, expected),
    )


# ============================
#   PASSWORD TESTS (3)
# ============================

class PasswordCheckUser:
    def __init__(self, expected_password):
        self.expected_password = expected_password

    def check_password(self, password):
        return password == self.expected_password


PASSWORD_VALIDATOR_CASES = [
    ("password_change_valid_payload",
     {"current_password": "oldpass123", "new_password": "newpass123"},
     PasswordCheckUser("oldpass123"), {}),
    ("password_change_wrong_current_password",
     {"current_password": "wrongpass", "new_password": "newpass123"},
     PasswordCheckUser("oldpass123"), {"current_password": "incorrect"}),
    ("password_change_short_new_password",
     {"current_password": "oldpass123", "new_password": "short"},
     PasswordCheckUser("oldpass123"), {"new_password": "min_length_8"}),
]


def make_password_validator_test(payload, user, expected):
    def test(self):
        self.assertEqual(validate_password_change_payload(payload, user), expected)
    return test


for case_name, payload, user, expected in PASSWORD_VALIDATOR_CASES[:PASSWORD_LIMIT]:
    setattr(
        TestExtraValidator,
        f"test_extra_validator_{case_name}",
        make_password_validator_test(payload, user, expected),
    )


# ============================
#   API TESTS (9)
# ============================

@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class TestExtraApiContract(TestCase):
    def setUp(self):
        User = get_user_model()
        self.password = "password123"
        self.user = User.objects.create_user(username="extra_ana", password=self.password)
        self.other_user = User.objects.create_user(username="extra_bea", password=self.password)

    def request_json(self, method, url, payload=None, raw=None):
        data = raw if raw is not None else json.dumps(payload) if payload is not None else None
        return self.client.generic(
            method,
            url,
            data=data,
            content_type="application/json",
        )

    def login_as(self, user=None):
        self.client.force_login(user or self.user)

    def create_entry(self, external_game_id="extra-game", status="wishlist", hours_played=0, user=None):
        return LibraryEntry.objects.create(
            user=user or self.user,
            external_game_id=external_game_id,
            status=status,
            hours_played=hours_played,
        )

    def assert_json_response(self, response, status_code, expected_json):
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(response.headers["Content-Type"], "application/json")
        self.assertEqual(response.json(), expected_json)


API_CASES = [
    ("health_put_method_not_allowed", "PUT", "/api/health/", None, {"error": "method_not_allowed"}, 405),
    ("register_put_method_not_allowed", "PUT", "/api/auth/register/", None, {"error": "method_not_allowed"}, 405),
    ("login_delete_method_not_allowed", "DELETE", "/api/auth/login/", None, {"error": "method_not_allowed"}, 405),
    ("logout_get_method_not_allowed", "GET", "/api/auth/logout/", None, {"error": "method_not_allowed"}, 405),
    ("me_put_method_not_allowed", "PUT", "/api/users/me/", None, {"error": "method_not_allowed"}, 405),
    ("password_delete_method_not_allowed", "DELETE", "/api/users/me/password/", None, {"error": "method_not_allowed"}, 405),
    ("entries_patch_method_not_allowed", "PATCH", "/api/library/entries/", None, {"error": "method_not_allowed"}, 405),
    ("detail_post_method_not_allowed", "POST", "/api/library/entries/1/", None, {"error": "method_not_allowed"}, 405),
    ("detail_delete_method_not_allowed", "DELETE", "/api/library/entries/1/", None, {"error": "method_not_allowed"}, 405),
]


def make_api_contract_test(case_name, method, url, payload_or_raw, expected_json, expected_status):
    def test(self):
        if "{entry_id}" in url:
            self.login_as()
            entry = self.create_entry()
            resolved_url = url.format(entry_id=entry.id)
        else:
            resolved_url = url

        raw = payload_or_raw if isinstance(payload_or_raw, str) else None
        payload = None if raw is not None else payload_or_raw

        response = self.request_json(method, resolved_url, payload=payload, raw=raw)
        self.assert_json_response(response, expected_status, expected_json)

    return test


for case_name, method, url, payload_or_raw, expected_json, expected_status in API_CASES[:API_LIMIT]:
    setattr(
        TestExtraApiContract,
        f"test_extra_api_{case_name}",
        make_api_contract_test(case_name, method, url, payload_or_raw, expected_json, expected_status),
    )
