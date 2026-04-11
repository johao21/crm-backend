from slowapi import Limiter
from slowapi.util import get_remote_address

# Limiter global basado en IP
limiter = Limiter(key_func=get_remote_address)