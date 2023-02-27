serveradmindb = None
logger = None
servermode = False
admindb_path = None


class MultiuserHandlers:
    def __init__(self, servermode=None):
        self.servermode = servermode
        self.routes = []
        self.add_routes()

    def add_routes(self):
        self.routes = []
        self.routes.append(["POST", "/server/loginsuccess", self.loginsuccess])
        self.routes.append(["GET", "/server/logout", self.logout])
        self.routes.append(["GET", "/server/usersettings", self.get_user_settings])
        self.routes.append(["GET", "/server/checklogged", self.check_logged])
        self.routes.append(["GET", "/server/username", self.get_username])
        self.routes.append(["GET", "/server/deletetoken", self.delete_token])
        self.routes.append(["POST", "/server/signup", self.signup])
        self.routes.append(["GET", "/server/users", self.get_users])
        self.routes.append(["GET", "/server/makeadmin", self.make_admin])
        self.routes.append(["GET", "/server/removeadmin", self.remove_admin])
        self.routes.append(["GET", "/server/removeuser", self.remove_user])

    async def remove_admin(self, request):
        from aiohttp.web import Response
        from .serveradmindb import get_serveradmindb

        if not self.servermode:
            return Response(status=403)
        if not await self.is_admin_loggedin(request):
            return Response(status=403)
        queries = request.rel_url.query
        email = queries.get("email")
        if not email:
            return Response(status=400)
        admindb = await get_serveradmindb()
        await admindb.remove_admin(email)
        return Response(status=200)

    async def remove_user(self, request):
        from aiohttp.web import Response
        from .serveradmindb import get_serveradmindb

        if not self.servermode:
            return Response(status=403)
        if not await self.is_admin_loggedin(request):
            return Response(status=403)
        queries = request.rel_url.query
        email = queries.get("email")
        if not email:
            return Response(status=400)
        admindb = await get_serveradmindb()
        await admindb.remove_user(email)
        return Response(status=200)

    async def make_admin(self, request):
        from aiohttp.web import Response
        from .serveradmindb import get_serveradmindb

        if not self.servermode:
            return Response(status=403)
        if not await self.is_admin_loggedin(request):
            return Response(status=403)
        queries = request.rel_url.query
        email = queries.get("email")
        if not email:
            return Response(status=400)
        admindb = await get_serveradmindb()
        await admindb.make_admin(email)
        return Response(status=200)

    async def get_users(self, request):
        from aiohttp.web import Response
        from aiohttp.web import json_response
        from .serveradmindb import get_serveradmindb

        if not self.servermode:
            return Response(status=403)
        if not await self.is_admin_loggedin(request):
            return Response(status=403)
        admindb = await get_serveradmindb()
        users = await admindb.get_users()
        return json_response(users)

    async def signup(self, request):
        from aiohttp.web import json_response
        import jwt
        from ..lib.store.ov.account import create
        from .serveradmindb import get_serveradmindb
        from .serveradmindb import setup_serveradmindb
        from .consts import DEFAULT_PRIVATE_KEY
        from .consts import COOKIE_KEY

        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        new_setup = data.get("newSetup", False)
        if not email:
            return json_response({"code": "auth/missing-email"}, status=403)
        if not password:
            return json_response({"code": "missing-password"}, status=403)
        if new_setup:
            serveradmindb = setup_serveradmindb()
        else:
            serveradmindb = await get_serveradmindb(new_setup=new_setup)
        ret = create(email=email, pw=password)
        msg = ret.get("msg")
        if not ret.get("success"):
            return json_response({"code": msg}, status=401)
        await serveradmindb.add_user_if_not_exist(email, "", "", "")
        oakvar_token = jwt.encode(
            {"email": email}, DEFAULT_PRIVATE_KEY, algorithm="HS256"
        )
        response = json_response({"code": msg}, status=200)
        response.set_cookie(COOKIE_KEY, oakvar_token, httponly=True)
        return response

    async def delete_token(self, _):
        from aiohttp.web import Response
        from .consts import COOKIE_KEY

        global servermode
        response = Response(status=200)
        response.del_cookie(COOKIE_KEY)
        return response

    async def get_username(self, request):
        from aiohttp.web import json_response
        from .util import get_email_from_request

        email = get_email_from_request(request, self.servermode)
        res = {"email": email}
        return json_response(res)

    async def check_logged(self, request):
        from aiohttp.web import json_response
        from ..lib.system.consts import DEFAULT_SERVER_DEFAULT_USERNAME
        from .util import get_email_from_request

        global servermode
        email = get_email_from_request(request, self.servermode)
        if not email or (servermode and email == DEFAULT_SERVER_DEFAULT_USERNAME):
            response = {"logged": False}
        response = {
            "logged": True,
            "email": email,
            "admin": await self.is_admin_loggedin(request, email=email),
        }
        return json_response(response)

    async def get_user_settings(self, request):
        from aiohttp.web import json_response
        from .serveradmindb import get_serveradmindb
        from .util import get_email_from_request

        admindb = await get_serveradmindb()
        if not admindb:
            return json_response({})
        email = get_email_from_request(request, self.servermode)
        response = await admindb.get_user_settings(email)
        return json_response(response)

    async def logout(self, _):
        from aiohttp.web import Response
        from .consts import COOKIE_KEY

        global servermode
        if servermode:
            response = Response(status=200)
            response.del_cookie(COOKIE_KEY)
        else:
            response = Response(status=403)
        return response

    async def loginsuccess(self, request):
        import jwt
        from aiohttp.web import json_response
        from .serveradmindb import get_serveradmindb
        from .consts import DEFAULT_PRIVATE_KEY
        from .consts import COOKIE_KEY

        # from requests import get
        # from cryptography import x509
        # from cryptography.hazmat.backends import default_backend

        global logger
        data = await request.json()
        email = data.get("email")
        if not email:
            response = json_response(
                {"status": "error", "email": email, "admin": False}
            )
            return response
        # token = data.get("login_token")
        # if not token:
        #    return Response(status=404)
        # kid = jwt.get_unverified_header(token)["kid"]
        # r = get(FIREBASE_PUBLIC_KEY_URL)
        # x509_key = r.json()[kid]
        # key = x509.load_pem_x509_certificate(x509_key.encode("utf-8"), backend=default_backend)
        # try:
        #    payload = jwt.decode(token, key.public_key(), ["RS256"], audience=PROJECT_ID) # type: ignore
        # except:
        #    if logger:
        #        logger.error(f"JWT decode error: {token}")
        #    return json_response({"status": "error"})
        # email = payload.get("email")
        # if not email:
        #    return HTTPNotFound()
        admin = await self.is_admin_loggedin(request, email=email)
        response = json_response({"status": "logged", "email": email, "admin": admin})
        admindb = await get_serveradmindb()
        await admindb.add_user_if_not_exist(email, "", "", "")
        oakvar_token = jwt.encode(
            {"email": email}, DEFAULT_PRIVATE_KEY, algorithm="HS256"
        )
        response.set_cookie(COOKIE_KEY, oakvar_token, httponly=True)
        return response

    async def is_admin_loggedin(self, request, email=None):
        from ..lib.system.consts import ADMIN_ROLE
        from .serveradmindb import get_serveradmindb
        from .util import get_email_from_request

        assert self.servermode is not None
        if not email:
            email = get_email_from_request(request, self.servermode)
        if not email:
            return False
        admindb = await get_serveradmindb()
        role = await admindb.get_user_role_of_email(email, servermode=self.servermode)
        return role == ADMIN_ROLE

    async def update_user_settings(self, request, d):
        from .serveradmindb import get_serveradmindb
        from .util import get_email_from_request

        admindb = await get_serveradmindb()
        email = get_email_from_request(request, self.servermode)
        return await admindb.update_user_settings(email, d)
