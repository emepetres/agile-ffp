# # from fasthtml.common import *

# # app, rt = fast_app()
# # setup_toasts(app)
# # router = APIRouter()

# # call_count = 0


# # @router.get("/")
# # def index():
# #     global call_count
# #     call_count += 1
# #     print(f"GET calls: {call_count}")
# #     return Div(
# #         Div(A("GET toast test", hx_get="/test_toast", hx_swap="none")),
# #         Div(A("PUT toast test", hx_put="/test_toast", hx_swap="none")),
# #     )


# # @router.get("/test_toast")
# # def get_test_toast(session):
# #     add_toast(session, "GET test toast!", "success")
# #     return


# # @router.put("/test_toast")
# # def put_test_toast(session):
# #     add_toast(session, "PUT test toast!", "success")
# #     return


# # router.to_app(app)

# # serve()
