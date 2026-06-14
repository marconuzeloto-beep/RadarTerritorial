import os
from app.routing.base import IsochroneProvider
from app.routing.ors_provider import ORSProvider


_PROVIDERS = {
    "ors": ORSProvider,
    # Future: "graphhopper": GraphHopperProvider,
}


def get_provider() -> IsochroneProvider:
    """Instantiate the configured routing provider from env vars."""
    provider_name = os.getenv("ROUTING_PROVIDER", "ors").lower()
    api_key = os.getenv("ORS_API_KEY", "")

    if not api_key:
        raise EnvironmentError(
            "ORS_API_KEY não configurada. "
            "Defina a variável de ambiente ORS_API_KEY com sua chave do OpenRouteService "
            "(https://openrouteservice.org/dev/#/signup)."
        )

    cls = _PROVIDERS.get(provider_name)
    if cls is None:
        raise ValueError(f"Provedor de roteamento desconhecido: '{provider_name}'.")

    return cls(api_key)
