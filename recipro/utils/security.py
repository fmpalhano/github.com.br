from datetime import date

# Contador em memória por IP/data para limitar abusos sem armazenar conteúdo sensível.
REQUEST_COUNTS: dict[tuple[str, str], int] = {}


def check_daily_limit(ip: str, limit: int = 5) -> bool:
    key = (ip, date.today().isoformat())
    REQUEST_COUNTS[key] = REQUEST_COUNTS.get(key, 0) + 1
    return REQUEST_COUNTS[key] <= limit
