from typing import Optional

admindb = None
logger = None
servermode = False
server_ready = False
admindb_path = None
DEFAULT_PRIVATE_KEY = "default_private_key"
FIREBASE_PUBLIC_KEY_URL = "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"
PROJECT_ID = "fabled-pivot-305219"
COOKIE_KEY = "oakvar_token"

def get_session_key():
    from cryptography import fernet
    fernet_key = fernet.Fernet.generate_key()
    session_key = str(fernet_key)
    return session_key

def get_servermode():
    global servermode
    return servermode

async def is_loggedin (request):
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
    admindb = await get_admindb()
    role = await admindb.get_user_role_of_email(email, servermode=get_servermode())
    return role == ADMIN_ROLE

async def get_username(request):
    from aiohttp.web import json_response
    email = get_email_from_request(request)
    res = {"email": email}
    return json_response(res)

async def get_username_str(request) -> Optional[str]:
    email = get_email_from_request(request)
    res = {"email": email}
    return res.get("email")

async def add_job_info(request, job):
    admindb = await get_admindb()
    email = get_email_from_request(request)
    await admindb.add_job_info(email, job)

def create_user_dir_if_not_exist (username):
    from os.path import join
    from os.path import exists
    from os import mkdir
    from ...system import get_jobs_dir
    root_jobs_dir = get_jobs_dir()
    user_job_dir = join(root_jobs_dir, username)
    if exists(user_job_dir) == False:
        mkdir(user_job_dir)

def get_email_from_request(request):
    from ...system.consts import DEFAULT_SERVER_DEFAULT_USERNAME
    global servermode
    email = None
    token = request.cookies.get(COOKIE_KEY)
    if token:
        email = get_email_from_oakvar_token(token)
    elif not servermode:
        email = DEFAULT_SERVER_DEFAULT_USERNAME
    return email

def get_email_from_oakvar_token(token):
    import jwt
    data = jwt.decode(token, DEFAULT_PRIVATE_KEY, ["HS256"])
    email = data.get("email")
    return email

async def loginsuccess(request):
    from aiohttp.web import json_response
    from aiohttp.web import HTTPNotFound
    import jwt
    from requests import get
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend

    global logger
    data = await request.json()
    token = data.get("login_token")
    if not token:
        return HTTPNotFound()
    kid = jwt.get_unverified_header(token)["kid"]
    r = get(FIREBASE_PUBLIC_KEY_URL)
    x509_key = r.json()[kid]
    key = x509.load_pem_x509_certificate(x509_key.encode("utf-8"), backend=default_backend)
    try:
        payload = jwt.decode(token, key.public_key(), ["RS256"], audience=PROJECT_ID) # type: ignore
    except:
        if logger:
            logger.error(f"JWT decode error: {token}")
        return json_response({"status": "error"})
    email = payload.get("email")
    if not email:
        return HTTPNotFound()
    response = json_response({"status": "loggedin"})
    admindb = await get_admindb()
    await admindb.add_user_if_not_exist(email, "", "", "")
    oakvar_token = jwt.encode({"email": email}, DEFAULT_PRIVATE_KEY, algorithm="HS256")
    response.set_cookie(COOKIE_KEY, oakvar_token, httponly=True)
    return response

async def set_temp_password (request):
    if admindb:
        queries = request.rel_url.query
        email = queries['email']
        temppassword = await admindb.set_temp_password(email)
        return temppassword

async def check_logged (request):
    from aiohttp.web import json_response
    from ...system.consts import DEFAULT_SERVER_DEFAULT_USERNAME
    global servermode
    email = get_email_from_request(request)
    if not email or (servermode and email == DEFAULT_SERVER_DEFAULT_USERNAME):
        response = {"logged": False}
    response = {'logged': True, 'email': email, 'admin': await is_admin_loggedin(request, email=email)}
    return json_response(response)

async def logout (_):
    from aiohttp.web import json_response
    global servermode
    if servermode:
        response = json_response({"status": "success"})
        response.del_cookie(COOKIE_KEY)
    else:
        response = json_response({"status": "error"})
    return response

async def get_input_stat (request):
    from aiohttp.web import json_response
    global servermode
    if not servermode or not admindb:
        return json_response('no multiuser mode')
    r = await is_admin_loggedin(request)
    if r == False:
        return json_response('no admin')
    queries = request.rel_url.query
    start_date = queries['start_date']
    end_date = queries['end_date']
    rows = await admindb.get_input_stat(start_date, end_date)
    return json_response(rows)

async def get_user_stat (request):
    from aiohttp.web import json_response
    global servermode
    if not servermode or not admindb:
        return json_response('no multiuser mode')
    r = await is_admin_loggedin(request)
    if r == False:
        return json_response('no admin')
    queries = request.rel_url.query
    start_date = queries['start_date']
    end_date = queries['end_date']
    rows = await admindb.get_user_stat(start_date, end_date)
    return json_response(rows)

async def get_job_stat (request):
    from aiohttp.web import json_response
    global servermode
    if not servermode:
        return json_response('no multiuser mode')
    r = await is_admin_loggedin(request)
    if r == False:
        return json_response('no admin')
    queries = request.rel_url.query
    start_date = queries['start_date']
    end_date = queries['end_date']
    if admindb:
        response = await admindb.get_job_stat(start_date, end_date)
    else:
        response = {}
    return json_response(response)

async def get_api_stat (request):
    from aiohttp.web import json_response
    global servermode
    if not servermode:
        return json_response('no multiuser mode')
    r = await is_admin_loggedin(request)
    if r == False:
        return json_response('no admin')
    queries = request.rel_url.query
    start_date = queries['start_date']
    end_date = queries['end_date']
    if admindb:
        response = await admindb.get_api_stat(start_date, end_date)
    else:
        response = {}
    return json_response(response)

async def get_annot_stat (request):
    from aiohttp.web import json_response
    global servermode
    if not servermode:
        return json_response('no multiuser mode')
    r = await is_admin_loggedin(request)
    if r == False:
        return json_response('no admin')
    queries = request.rel_url.query
    start_date = queries['start_date']
    end_date = queries['end_date']
    if admindb:
        response = await admindb.get_annot_stat(start_date, end_date)
    else:
        response = {}
    return json_response(response)

async def get_assembly_stat (request):
    from aiohttp.web import json_response
    global servermode
    if not servermode:
        return json_response('no multiuser mode')
    r = await is_admin_loggedin(request)
    if r == False:
        return json_response('no admin')
    queries = request.rel_url.query
    start_date = queries['start_date']
    end_date = queries['end_date']
    if admindb:
        response = await admindb.get_assembly_stat(start_date, end_date)
    else:
        response = {}
    return json_response(response)

async def restart (request):
    from os import execvp
    from aiohttp.web import json_response
    global servermode
    if servermode:
        r = await is_admin_loggedin(request)
        if r == False:
            return json_response({'success': False, 'mgs': 'Only logged-in admin can change the settings.'})
    execvp('wcravat', ['wcravat', '--multiuser', '--headless'])

async def show_login_page (request):
    from os.path import join
    from os.path import dirname
    from os.path import abspath
    from aiohttp.web import HTTPFound
    from aiohttp.web import FileResponse
    global servermode
    global server_ready
    global logger
    if not servermode or not server_ready:
        if logger:
            logger.info('Login page requested but no multiuser mode. Redirecting to submit index...')
        return HTTPFound('/submit/index.html')
    r = await is_loggedin(request)
    if r == False:
        p = join(dirname(abspath(__file__)), 'nocache', 'login.html')
        return FileResponse(p)
    else:
        if logger:
            logger.info('Login page requested but already logged in. Redirecting to submit index...')
        return HTTPFound('/submit/index.html')

async def get_user_settings (request):
    from aiohttp.web import json_response
    admindb = await get_admindb()
    if not admindb:
        return json_response({})
    email = get_email_from_request(request)
    response = await admindb.get_user_settings(email)
    return json_response(response)

async def update_user_settings (request, d):
    admindb = await get_admindb()
    email = get_email_from_request(request)
    return await admindb.update_user_settings(email, d)

async def get_admindb():
    from .serveradmindb import ServerAdminDb
    global admindb
    if not admindb:
        admindb = ServerAdminDb()
    return admindb

def add_routes (router):
    from os.path import dirname
    from os.path import realpath
    from os.path import join
    router.add_route('POST', '/server/loginsuccess', loginsuccess)
    router.add_route('GET', '/server/logout', logout)
    router.add_route('GET', '/server/usersettings', get_user_settings)
    router.add_route('GET', '/server/checklogged', check_logged)
    router.add_route('GET', '/server/username', get_username)
    """
    router.add_route('GET', '/server/login', login)
    router.add_route('GET', '/server/passwordquestion', get_password_question)
    router.add_route('GET', '/server/passwordanswer', check_password_answer)
    router.add_route('GET', '/server/changepassword', change_password)
    router.add_route('GET', '/server/inputstat', get_input_stat)
    router.add_route('GET', '/server/userstat', get_user_stat)
    router.add_route('GET', '/server/jobstat', get_job_stat)
    router.add_route('GET', '/server/apistat', get_api_stat)
    router.add_route('GET', '/server/annotstat', get_annot_stat)
    router.add_route('GET', '/server/assemblystat', get_assembly_stat)
    router.add_route('GET', '/server/restart', restart)
    router.add_route('GET', '/server/nocache/login.html', show_login_page)
    """
    router.add_static('/server', join(dirname(realpath(__file__))))

