from .base import *

import os

# Por defecto, usar configuración de desarrollo
if os.environ.get('DJANGO_ENV') == 'production':
    from .prod import *
else:
    from .dev import *