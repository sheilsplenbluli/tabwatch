"""tabwatch REST API package.

Exposes the Flask `app` instance so it can be imported by WSGI servers
or the test suite without circular imports.

Usage::

    from app.api import app
    app.run(debug=True)
"""

from app.api.routes import app  # noqa: F401
