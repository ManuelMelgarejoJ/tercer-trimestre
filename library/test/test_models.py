from django.test import TestCase
from library.models import LibraryEntry
from django.test import TestCase
from django.urls import reverse

class LibraryEntryModelTests(TestCase):

    # --- external_id_length ---
    def test_external_id_length(self):
        entry = LibraryEntry(external_game_id="abc123")
        self.assertEqual(entry.external_id_length(), 6)

    # --- external_id_upper ---
    def test_external_id_upper(self):
        entry = LibraryEntry(external_game_id="abc123")
        self.assertEqual(entry.external_id_upper(), "ABC123")

    def test_external_id_upper_empty(self):
        entry = LibraryEntry(external_game_id="")
        self.assertEqual(entry.external_id_upper(), "")

    # --- hours_played_label ---
    def test_hours_played_label_none(self):
        entry = LibraryEntry(hours_played=0)
        self.assertEqual(entry.hours_played_label(), "none")

    def test_hours_played_label_low(self):
        entry = LibraryEntry(hours_played=5)
        self.assertEqual(entry.hours_played_label(), "low")

    def test_hours_played_label_high(self):
        entry = LibraryEntry(hours_played=20)
        self.assertEqual(entry.hours_played_label(), "high")

    # --- status_value ---
    def test_status_value_wishlist(self):
        entry = LibraryEntry(status=LibraryEntry.STATUS_WISHLIST)
        self.assertEqual(entry.status_value(), 0)

    def test_status_value_playing(self):
        entry = LibraryEntry(status=LibraryEntry.STATUS_PLAYING)
        self.assertEqual(entry.status_value(), 1)

    def test_status_value_completed(self):
        entry = LibraryEntry(status=LibraryEntry.STATUS_COMPLETED)
        self.assertEqual(entry.status_value(), 2)

    def test_status_value_dropped(self):
        entry = LibraryEntry(status=LibraryEntry.STATUS_DROPPED)
        self.assertEqual(entry.status_value(), 3)

    def test_status_value_invalid(self):
        entry = LibraryEntry(status="unknown")
        self.assertEqual(entry.status_value(), -1)

class HealthViewTests(TestCase):

    def test_health_get_ok(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_health_wrong_method(self):
        response = self.client.post("/api/health/")
        self.assertEqual(response.status_code, 405)