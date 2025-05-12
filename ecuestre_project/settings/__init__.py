from .base import *
from .dev import *
from .production import *

import os

# Por defecto, usar configuración de desarrollo
if os.environ.get('DJANGO_ENV') == 'production':
    from .production import *
else:
    from .dev import *