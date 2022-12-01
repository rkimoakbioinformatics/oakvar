from typing import Optional

serveradmindb = None
logger = None
servermode = False
server_ready = False
admindb_path = None
DEFAULT_PRIVATE_KEY = "default_private_key"
FIREBASE_PUBLIC_KEY_URL = "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"
PROJECT_ID = "fabled-pivot-305219"
COOKIE_KEY = "oakvar_token"


def get_servermode():
    global servermode
    return servermode


async def is_loggedin(request):
    if not get_servermode():
        return True
    email = get_email_from_request(request)
    if email:
        return True
    else:
        return False


async def is_admin_loggedin(request, email=None):
    from ...system.consts import ADMIN_ROLE

    if not email:
        email = get_email_from_request(request)
    if not email:
        return False
    admindb = await get_serveradmindb()
    role = await admindb.get_user_role_of_email(email, servermode=get_servermode())
    return role == ADMIN_ROLE


async def get_username(request):
    from aiohttp.web import json_response

    email = get_email_from_request(request)
    res = {"email": email}
    return json_response(res)


async def add_job_info(request, job) -> Optional[str]:
    admindb = await get_serveradmindb()
    email = get_email_from_request(request)
    uid = await admindb.add_job_info(email, job)
    return uid


def get_token(request):
    return request.cookies.get(COOKIE_KEY)


def get_email_from_request(request):
    from ...system.consts import DEFAULT_SERVER_DEFAULT_USERNAME

    global servermode
    global servermode
    if not servermode:
        return DEFAULT_SERVER_DEFAULT_USERNAME
    token = get_token(request)
    if token:
        email = get_email_from_oakvar_token(token)
    else:
        email = None
    return email


def get_email_from_oakvar_token(token):
    import jwt

    data = jwt.decode(token, DEFAULT_PRIVATE_KEY, ["HS256"])
    email = data.get("email")
    return email


async def loginsuccess(request):
    import jwt
    from aiohttp.web import json_response

    # from requests import get
    # from cryptography import x509
    # from cryptography.hazmat.backends import default_backend

    global logger
    data = await request.json()
    email = data.get("email")
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
    admin = await is_admin_loggedin(request, email=email)
    response = json_response({"status": "logged", "email": email, "admin": admin})
    admindb = await get_serveradmindb()
    await admindb.add_user_if_not_exist(email, "", "", "")
    oakvar_token = jwt.encode({"email": email}, DEFAULT_PRIVATE_KEY, algorithm="HS256")
    response.set_cookie(COOKIE_KEY, oakvar_token, httponly=True)
    return response


async def set_temp_password(request):
    if serveradmindb:
        queries = request.rel_url.query
        email = queries["email"]
        temppassword = await serveradmindb.set_temp_password(email)
        return temppassword


async def check_logged(request):
    from aiohttp.web import json_response
    from ...system.consts import DEFAULT_SERVER_DEFAULT_USERNAME

    global servermode
    email = get_email_from_request(request)
    if not email or (servermode and email == DEFAULT_SERVER_DEFAULT_USERNAME):
        response = {"logged": False}
    response = {
        "logged": True,
        "email": email,
        "admin": await is_admin_loggedin(request, email=email),
    }
    return json_response(response)


async def logout(_):
    from aiohttp.web import Response

    global servermode
    if servermode:
        response = Response(status=200)
        response.del_cookie(COOKIE_KEY)
    else:
        response = Response(status=403)
    return response


async def restart(request):
    from os import execvp
    from aiohttp.web import json_response

    global servermode
    if servermode:
        r = await is_admin_loggedin(request)
        if r == False:
            return json_response(
                {
                    "success": False,
                    "mgs": "Only logged-in admin can restart.",
                }
            )
    execvp("ov", ["ov", "gui", "--multiuser", "--headless"])


async def get_user_settings(request):
    from aiohttp.web import json_response

    admindb = await get_serveradmindb()
    if not admindb:
        return json_response({})
    email = get_email_from_request(request)
    response = await admindb.get_user_settings(email)
    return json_response(response)


async def update_user_settings(request, d):
    admindb = await get_serveradmindb()
    email = get_email_from_request(request)
    return await admindb.update_user_settings(email, d)


async def get_serveradmindb():
    from .serveradmindb import ServerAdminDb

    global serveradmindb
    if not serveradmindb:
        serveradmindb = ServerAdminDb()
    return serveradmindb


async def delete_token(_):
    from aiohttp.web import Response

    global servermode
    response = Response(status=200)
    response.del_cookie(COOKIE_KEY)
    return response


async def signup(request):
    from aiohttp.web import Response
    from aiohttp.web import json_response
    import jwt
    from ...store.ov.account import create

    global servermode
    if not servermode:
        return Response(status=403)
    data = await request.json()
    email = data.get("email")
    password = data.get("password")
    if not email:
        return json_response({"code": "auth/missing-email"}, status=403)
    if not password:
        return json_response({"code": "missing-password"}, status=403)
    serveradmindb = await get_serveradmindb()
    ret = create(email=email, pw=password)
    msg = ret.get("msg")
    if not ret.get("success"):
        return json_response({"code": msg}, status=401)
    await serveradmindb.add_user_if_not_exist(email, "", "", "")
    oakvar_token = jwt.encode({"email": email}, DEFAULT_PRIVATE_KEY, algorithm="HS256")
    response = json_response({"code": msg}, status=200)
    response.set_cookie(COOKIE_KEY, oakvar_token, httponly=True)
    return response


async def get_users(request):
    from aiohttp.web import Response
    from aiohttp.web import json_response

    if not get_servermode():
        return Response(status=403)
    if not await is_admin_loggedin(request):
        return Response(status=403)
    admindb = await get_serveradmindb()
    users = await admindb.get_users()
    return json_response(users)

async def make_admin(request):
    from aiohttp.web import Response

    if not get_servermode():
        return Response(status=403)
    if not await is_admin_loggedin(request):
        return Response(status=403)
    queries = request.rel_url.query
    email = queries.get("email")
    if not email:
        return Response(status=400)
    admindb = await get_serveradmindb()
    await admindb.make_admin(email)
    return Response(status=200)


async def remove_admin(request):
    from aiohttp.web import Response

    if not get_servermode():
        return Response(status=403)
    if not await is_admin_loggedin(request):
        return Response(status=403)
    queries = request.rel_url.query
    email = queries.get("email")
    if not email:
        return Response(status=400)
    admindb = await get_serveradmindb()
    await admindb.remove_admin(email)
    return Response(status=200)

def add_routes(router):
    from os.path import dirname
    from os.path import realpath
    from os.path import join

    router.add_route("POST", "/server/loginsuccess", loginsuccess)
    router.add_route("GET", "/server/logout", logout)
    router.add_route("GET", "/server/usersettings", get_user_settings)
    router.add_route("GET", "/server/checklogged", check_logged)
    router.add_route("GET", "/server/username", get_username)
    router.add_route("GET", "/server/deletetoken", delete_token)
    router.add_route("POST", "/server/signup", signup)
    router.add_route("GET", "/server/users", get_users)
    router.add_route("GET", "/server/makeadmin", make_admin)
    router.add_route("GET", "/server/removeadmin", remove_admin)
    router.add_static("/server", join(dirname(realpath(__file__))))

