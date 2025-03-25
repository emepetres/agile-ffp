# # from fasthtml.common import *

# # app, rt = fast_app()
# # router = APIRouter()


# # @router.get("/")
# # def index(session):
# #     session["test"] = session.get("test", "Hello, Default!")
# #     return Div(
# #         P(f"Session test value: {session["test"]}"),
# #         Div(A("Update session value", hx_put="/update_sync", hx_target="body")),
# #         Div(A("Update session value (async)", hx_put="/update_async", hx_target="body"))
# #     )


# # @ router.put("/update_sync")
# # def update_sync(session):
# #     session["test"] = "Hello, world sync update!"
# #     return Div(A("Check session values", href="/"))


# # @ router.put("/update_async")
# # async def update_async(request, session):
# #     form: FormData = await request.form()
# #     session["test"] = "Hello, world async update!"
# #     return Div(A("Check session values", href="/"))


# # router.to_app(app)

# # serve()
