from authlib.integrations.starlette_client import OAuth
from fasthtml.common import (
    A,
    Beforeware,
    Container,
    Div,
    Img,
    P,
    RedirectResponse,
    Script,
    Titled,
    fast_app,
    serve,
)
from monsterui.all import (
    ButtonT,
    DivCentered,
    DivHStacked,
    Theme,
)

from agileffp import yaml_editor
from agileffp.roadmap import charts
from agileffp.settings import app_settings

headers = (
    Theme.blue.headers(),
    # # Link(rel="icon", type="image/x-icon", href="/images/favicons/favicon.ico"),
    Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js"),
    Script(src="https://cdn.plot.ly/plotly-2.24.1.min.js"),
)

charts_id = "main-content"

if not app_settings.DISABLE_AUTH:
    oauth = OAuth()
    oauth.register(
        name='microsoft',
        client_id=app_settings.MICROSOFT_CLIENT_ID,
        client_secret=app_settings.MICROSOFT_CLIENT_SECRET,
        server_metadata_url='https://login.microsoftonline.com/plain.onmicrosoft.com/v2.0/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

# Auth beforeware
login_redir = RedirectResponse('/login', status_code=303)


def auth_before(req, sess):
    auth = req.scope['auth'] = sess.get('auth', None)
    if not auth:
        return login_redir


beforeware = Beforeware(
    auth_before,
    skip=[r'/favicon\.ico', r'/images/.*',
          r'.*\.css', r'.*\.js', '/login', '/auth', '/auth/callback', '/']
)

app, rt = fast_app(hdrs=headers, static_path="static", before=beforeware)
yaml_editor.build_api(app, charts_id, prefix="/editor")

# Add login routes


@rt("/login")
def get(session):
    if app_settings.DISABLE_AUTH:
        # Set the auth in session for beforeware
        session['auth'] = "dev@plainconcepts.com"
        return RedirectResponse('/', status_code=303)
    # Only redirect to auth if the user explicitly clicked the login button
    return Titled(
        "AgileFFP - Redirecting to Microsoft login",
        Container(
            DivCentered(
                Div(
                    P("Redirecting to Microsoft login...", cls="text-xl mb-4"),
                    # Provide manual link in case redirect doesn't happen automatically
                    A("Click here if you're not redirected automatically",
                      href="/auth",
                      cls=f"{ButtonT.primary}"),
                    # JavaScript to handle the redirect
                    Script("window.location.href = '/auth';",
                           type="text/javascript"),
                    cls="text-center py-12"
                )
            )
        )
    )


@rt("/auth", name="auth")
async def auth(request):
    client = oauth.create_client('microsoft')
    return await client.authorize_redirect(request, request.url_for('auth_callback'))


@rt("/auth/callback", name="auth_callback")
async def auth_callback(request, session):
    client = oauth.create_client('microsoft')
    token = await client.authorize_access_token(request)
    user = await client.userinfo(token=token)

    # Set the auth in session for beforeware
    session['auth'] = user.email

    # Add the auth to the request scope immediately for this request
    request.scope['auth'] = user.email

    # Redirect directly to the root path
    return RedirectResponse('/', status_code=303)


@rt("/logout")
def logout(session):
    session.clear()
    return RedirectResponse('/', status_code=303)


@rt("/")
def index(session, auth=None):
    # First check if auth is passed (from beforeware in other routes)
    # If not, try to get it from the session directly
    if not auth:
        auth = session.get('auth', None)

    # Now check if we have auth from either source
    if not auth:
        # Landing page for non-authenticated users
        return Titled(
            "AgileFFP - a tool by Javier Carnero",
            Container(
                DivCentered(
                    Div(
                        # Logo or app name
                        Img(src="images/logo.png",
                            cls="h-48 mx-auto mb-6"),
                        # Subtitle
                        P("Feature and Feature Point Visualization Tool",
                          cls="text-xl mb-8"),
                        # Login button with MonsterUI styling
                        A(
                            "Login with Microsoft",
                            href="/login",
                            cls=f"{ButtonT.primary} py-4 px-8 text-lg"
                        ),
                        cls="text-center py-12",
                    )
                )
            ),
        )

    # Authenticated user view
    # Create a header with title, user email and logout button
    header = DivCentered(
        Div(
            P(auth),
            A("Logout", href="/logout", cls="button"),
            cls="flex items-center gap-2"
        )
    )

    return Titled(
        "AgileFFP - a tool by Javier Carnero",
        Container(
            Div(
                # Header
                header,
                # Main content
                DivHStacked(
                    # Main content (spans all width)
                    charts.initialize(charts_id),
                    # Right content (spans 1/3 width)
                    yaml_editor.initialize(session),
                    cls="gap-4",
                ),
                cls="flex flex-col gap-4"
            ),
        ),
        Img(
            id="spinner",
            cls="htmx-indicator fixed inset-0 m-auto",
            src="images/loading-spinner.svg",
            alt="Computing charts...",
        ),
    )


if __name__ == "__main__":
    print("----Development environment----")

    serve(appname="agileffp.app", app="app", reload=True)
