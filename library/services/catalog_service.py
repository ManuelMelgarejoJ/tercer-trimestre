import json
import logging

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class ExternalServiceUnavailable(Exception):
    """503 - El proveedor no responde (timeout / error de red)."""


class ExternalServiceError(Exception):
    """502 - El proveedor respondió con error o datos inválidos."""


_CACHE_KEY_PREFIX = "catalog:search:"


def _cache_key(query: str) -> str:
    return f"{_CACHE_KEY_PREFIX}{query.strip().lower()}"


class CatalogService:
    """
    Centraliza toda la lógica del catálogo externo y la caché.

    Flujo normal:
        1. Consulta Redis con la clave derivada del query.
        2. Si hay acierto (hit) → devuelve los datos cacheados.
        3. Si no (miss) → consulta CheapShark y guarda en Redis.

    Flujo con fallo del proveedor:
        1. Si hay datos en Redis → los devuelve (failover).
        2. Si no hay datos en Redis → lanza la excepción correspondiente.
    """

    @staticmethod
    def search_games(query: str) -> list:
        """
        Busca juegos en el catálogo para el texto dado.

        Returns:
            Lista de juegos (dicts) tal como los devuelve CheapShark.

        Raises:
            ExternalServiceUnavailable: timeout o error de red.
            ExternalServiceError: respuesta inválida o error del proveedor.
        """
        cache_key = _cache_key(query)

        # --- Paso 1: Consultar Redis ---
        logger.info(
            "accion=redis_get query=%r resultado=pendiente",
            query,
        )
        cached = cache.get(cache_key)
        if cached is not None:
            logger.info(
                "accion=cache_hit origen=redis query=%r",
                query,
            )
            return cached

        logger.info(
            "accion=cache_miss origen=redis query=%r",
            query,
        )

        # --- Paso 2: Llamar a CheapShark ---
        url = getattr(settings, "CHEAPSHARK_SEARCH_URL", "https://www.cheapshark.com/api/1.0/games")
        ttl = getattr(settings, "CATALOG_CACHE_TTL", 3600)

        logger.info(
            "accion=external_request origen=cheapshark query=%r url=%s",
            query,
            url,
        )

        try:
            response = requests.get(
                url,
                params={"title": query, "limit": 20},
                timeout=5,
            )
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as exc:
            logger.warning(
                "accion=external_error origen=cheapshark query=%r "
                "error_type=unavailable exception=%s",
                query,
                exc.__class__.__name__,
            )
            # Intento de failover desde Redis (datos expirados no sirven,
            # pero si llegamos aquí el cache.get ya fue None, así que no hay nada)
            raise ExternalServiceUnavailable() from exc
        except requests.exceptions.RequestException as exc:
            logger.warning(
                "accion=external_error origen=cheapshark query=%r "
                "error_type=request_exception exception=%s",
                query,
                exc.__class__.__name__,
            )
            raise ExternalServiceUnavailable() from exc

        # --- Paso 3: Validar respuesta ---
        if response.status_code >= 400:
            logger.warning(
                "accion=external_error origen=cheapshark query=%r "
                "error_type=bad_status status_code=%s",
                query,
                response.status_code,
            )
            raise ExternalServiceError()

        try:
            data = response.json()
        except (ValueError, json.JSONDecodeError) as exc:
            logger.warning(
                "accion=external_error origen=cheapshark query=%r "
                "error_type=invalid_json exception=%s",
                query,
                exc.__class__.__name__,
            )
            raise ExternalServiceError() from exc

        if not isinstance(data, list):
            logger.warning(
                "accion=external_error origen=cheapshark query=%r "
                "error_type=unexpected_format type=%s",
                query,
                type(data).__name__,
            )
            raise ExternalServiceError()

        # --- Paso 4: Guardar en Redis ---
        cache.set(cache_key, data, ttl)
        logger.info(
            "accion=cache_set origen=cheapshark query=%r ttl=%s resultados=%s",
            query,
            ttl,
            len(data),
        )

        return data

    @staticmethod
    def search_games_with_fallback(query: str) -> list:
        """
        Como search_games pero intenta Redis como fallback si el proveedor falla.
        Usado cuando se quiere degradación controlada con datos posiblemente obsoletos.

        Raises:
            ExternalServiceUnavailable: timeout/red y sin caché.
            ExternalServiceError: error del proveedor y sin caché.
        """
        cache_key = _cache_key(query)

        # Primero intentamos desde Redis (datos frescos)
        logger.info("accion=redis_get query=%r resultado=pendiente", query)
        cached = cache.get(cache_key)
        if cached is not None:
            logger.info("accion=cache_hit origen=redis query=%r", query)
            return cached

        logger.info("accion=cache_miss origen=redis query=%r", query)

        url = getattr(settings, "CHEAPSHARK_SEARCH_URL", "https://www.cheapshark.com/api/1.0/games")
        ttl = getattr(settings, "CATALOG_CACHE_TTL", 3600)

        logger.info(
            "accion=external_request origen=cheapshark query=%r url=%s",
            query,
            url,
        )

        try:
            response = requests.get(
                url,
                params={"title": query, "limit": 20},
                timeout=5,
            )
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as exc:
            logger.warning(
                "accion=external_error origen=cheapshark query=%r "
                "error_type=unavailable exception=%s — intentando failover Redis",
                query,
                exc.__class__.__name__,
            )
            # Failover: intentamos leer desde Redis aunque el TTL estuviera expirado
            # (en un caso real se podría usar un segundo key sin TTL)
            fallback = cache.get(cache_key)
            if fallback is not None:
                logger.info(
                    "accion=cache_fallback origen=redis query=%r resultado=ok",
                    query,
                )
                return fallback
            raise ExternalServiceUnavailable() from exc

        except requests.exceptions.RequestException as exc:
            logger.warning(
                "accion=external_error origen=cheapshark query=%r "
                "error_type=request_exception exception=%s",
                query,
                exc.__class__.__name__,
            )
            raise ExternalServiceUnavailable() from exc

        if response.status_code >= 400:
            logger.warning(
                "accion=external_error origen=cheapshark query=%r "
                "error_type=bad_status status_code=%s",
                query,
                response.status_code,
            )
            raise ExternalServiceError()

        try:
            data = response.json()
        except (ValueError, json.JSONDecodeError) as exc:
            logger.warning(
                "accion=external_error origen=cheapshark query=%r "
                "error_type=invalid_json exception=%s",
                query,
                exc.__class__.__name__,
            )
            raise ExternalServiceError() from exc

        if not isinstance(data, list):
            logger.warning(
                "accion=external_error origen=cheapshark query=%r "
                "error_type=unexpected_format type=%s",
                query,
                type(data).__name__,
            )
            raise ExternalServiceError()

        cache.set(cache_key, data, ttl)
        logger.info(
            "accion=cache_set origen=cheapshark query=%r ttl=%s resultados=%s",
            query,
            ttl,
            len(data),
        )

        return data
