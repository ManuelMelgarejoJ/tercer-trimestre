import json

from django.contrib.auth.models import User
from django.test import TestCase

from library.models import LibraryEntry


class HealthTests(TestCase):
    def test_health(self):
        response = self.client.get("/api/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


class ChangePasswordTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="password123")

    def test_change_password_ok(self):
        self.client.login(username="alice", password="password123")

        response = self.client.post(
            "/api/users/me/password/",
            data=json.dumps(
                {"current_password": "password123", "new_password": "nueva1234"}
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"ok": True})
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("nueva1234"))

    def test_change_password_empty_json_returns_400(self):
        self.client.login(username="alice", password="password123")

        response = self.client.post(
            "/api/users/me/password/",
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "validation_error")

    def test_change_password_requires_authentication(self):
        response = self.client.post(
            "/api/users/me/password/",
            data=json.dumps(
                {"current_password": "password123", "new_password": "nueva1234"}
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"], "unauthorized")


class LibraryEntryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="password123")
        self.other_user = User.objects.create_user(username="bob", password="password123")
        self.entry = LibraryEntry.objects.create(
            external_game_id="game-1",
            status="wishlist",
            hours_played=1,
            user=self.user,
        )
        self.other_entry = LibraryEntry.objects.create(
            external_game_id="game-2",
            status="playing",
            hours_played=8,
            user=self.other_user,
        )

    def test_list_entries_uses_main_collection_route(self):
        self.client.login(username="alice", password="password123")

        response = self.client.get("/api/library/entries/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["external_game_id"], "game-1")

    def test_put_entry_ok(self):
        self.client.login(username="alice", password="password123")

        response = self.client.put(
            f"/api/library/entries/{self.entry.id}/",
            data=json.dumps(
                {
                    "external_game_id": "game-1-remastered",
                    "status": "completed",
                    "hours_played": 35,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.entry.refresh_from_db()
        self.assertEqual(self.entry.external_game_id, "game-1-remastered")
        self.assertEqual(self.entry.status, "completed")
        self.assertEqual(self.entry.hours_played, 35)

    def test_put_entry_validates_hours_played(self):
        self.client.login(username="alice", password="password123")

        response = self.client.put(
            f"/api/library/entries/{self.entry.id}/",
            data=json.dumps(
                {
                    "external_game_id": "game-1",
                    "status": "completed",
                    "hours_played": -1,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "validation_error")

    def test_put_entry_returns_404_for_other_user_resource(self):
        self.client.login(username="alice", password="password123")

        response = self.client.put(
            f"/api/library/entries/{self.other_entry.id}/",
            data=json.dumps(
                {
                    "external_game_id": "game-2",
                    "status": "completed",
                    "hours_played": 10,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"], "not_found")


class LogoutAndDeleteUserTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="password123")
        LibraryEntry.objects.create(
            external_game_id="game-1",
            status="wishlist",
            hours_played=1,
            user=self.user,
        )

    def test_logout_then_profile_returns_401(self):
        self.client.login(username="alice", password="password123")

        logout_response = self.client.post("/api/auth/logout/")
        profile_response = self.client.get("/api/users/me/")

        self.assertEqual(logout_response.status_code, 204)
        self.assertEqual(profile_response.status_code, 401)

    def test_delete_user_removes_account_and_entries(self):
        self.client.login(username="alice", password="password123")

        response = self.client.delete("/api/users/me/")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(User.objects.filter(username="alice").exists())
        self.assertEqual(LibraryEntry.objects.count(), 0)
        self.assertEqual(self.client.get("/api/users/me/").status_code, 401)

    def test_delete_user_requires_authentication(self):
        response = self.client.delete("/api/users/me/")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"], "unauthorized")
