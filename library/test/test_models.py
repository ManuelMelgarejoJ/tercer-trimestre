from library.models import LibraryEntry

class DemoTest(TestCase):
    def test_demo(self):
        # Comprueba que dos valores son exactamente iguales.
        self.assertEqual(4, 2+2)
        # Comprueba si una condición se cumple o no.
        self.assertTrue(4 == 4)
        self.assertFalse(5 == 4)
        # Permiten distinguir entre None y otros valores como cadenas vacías o ceros.
        self.assertIsNone(None)
        # Comprueba que una acción provoca un error concreto.
        with self.assertRaises(ZeroDivisionError):
            # Codigo que lanza la excepcion
            4/0

class LibraryEntryExternalIdLengthTests(TestCase):
    def test_external_id_length_counts_regular_string(self):
        # Precondiciones
        entry = LibraryEntry(external_game_id="abc")

        # Llamada
        longitud = entry.external_id_length()

        # Comprobaciones
        self.assertEqual(longitud, 3)

    def test_external_id_length_counts_empty_string_as_zero(self):
        # Precondiciones
        entry = LibraryEntry(external_game_id="")

        # Llamada
        longitud = entry.external_id_length()

        # Comprobaciones
        self.assertEqual(longitud, 0)

    def test_external_id_length_returns_zero_when_external_id_is_none(self):
        entry = LibraryEntry(external_game_id=None)

        longitud = entry.external_id_length()

        self.assertEqual(longitud, 0)

    def test_external_id_length_counts_whitespace(self):
        # Precondiciones
        entry = LibraryEntry(external_game_id="   ")

        # Llamada
        longitud = entry.external_id_length()

        # Comprobaciones
        self.assertEqual(longitud, 3)

    def test_external_id_length_counts_max_length_boundary_100(self):
        # Precondiciones
        entry = LibraryEntry(external_game_id="x" * 100)

        # Llamada
        longitud = entry.external_id_length()

        # Comprobaciones
        self.assertEqual(longitud, 100)

    def test_external_id_length_raises_type_error_if_not_string_or_none(self):
        # Caso anómalo: asignación indebida en memoria.
        # Precondiciones
        entry = LibraryEntry(external_game_id=123)

        # Llamada
        # Comprobaciones
        with self.assertRaises(TypeError):
            entry.external_id_length()


class LibraryEntryExternalIdUpperTests(TestCase):
    def test_external_id_upper_converts_regular_string_to_uppercase(self):
        entry = LibraryEntry(external_game_id="abc-123")

        resultado = entry.external_id_upper()

        self.assertEqual(resultado, "ABC-123")

    def test_external_id_upper_returns_empty_string_when_external_id_is_empty(self):
        entry = LibraryEntry(external_game_id="")

        resultado = entry.external_id_upper()

        self.assertEqual(resultado, "")

    def test_external_id_upper_returns_empty_string_when_external_id_is_none(self):
        entry = LibraryEntry(external_game_id=None)

        resultado = entry.external_id_upper()

        self.assertEqual(resultado, "")


class LibraryEntryHoursPlayedLabelTests(TestCase):
    def test_hours_played_label_returns_none_when_hours_are_zero(self):
        entry = LibraryEntry(hours_played=0)

        etiqueta = entry.hours_played_label()

        self.assertEqual(etiqueta, "none")

    def test_hours_played_label_returns_low_when_hours_are_between_one_and_nine(self):
        entry = LibraryEntry(hours_played=9)

        etiqueta = entry.hours_played_label()

        self.assertEqual(etiqueta, "low")

    def test_hours_played_label_returns_high_when_hours_are_ten_or_more(self):
        entry = LibraryEntry(hours_played=10)

        etiqueta = entry.hours_played_label()

        self.assertEqual(etiqueta, "high")


class LibraryEntryStatusValueTests(TestCase):
    def test_status_value_returns_expected_number_for_each_known_status(self):
        casos = (
            (LibraryEntry.STATUS_WISHLIST, 0),
            (LibraryEntry.STATUS_PLAYING, 1),
            (LibraryEntry.STATUS_COMPLETED, 2),
            (LibraryEntry.STATUS_DROPPED, 3),
        )

        for estado, valor_esperado in casos:
            with self.subTest(estado=estado):
                entry = LibraryEntry(status=estado)

                valor = entry.status_value()

                self.assertEqual(valor, valor_esperado)

    def test_status_value_returns_minus_one_for_unknown_status(self):
        entry = LibraryEntry(status="unknown")

        valor = entry.status_value()

        self.assertEqual(valor, -1)