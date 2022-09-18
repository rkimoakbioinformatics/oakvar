from aiohttp import web
from oakvar.system import get_system_conf

admindb = None
logger = None
servermode = False
server_ready = False
admindb_path = None
DEFAULT_PRIVATE_KEY = "default_private_key"
firebase_public_key_url = "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"
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

async def is_admin_loggedin(request):
    from ...system.consts import ADMIN_ROLE
    email = get_email_from_request(request)
    if not email:
        return False
    admindb = await get_admindb()
    role = await admindb.get_user_role_of_email(email)
    return role == ADMIN_ROLE

async def get_username(request, return_str=False):
    email = get_email_from_request(request)
    res = {"email": email}
    if return_str:
        return res.get("email")
    return web.json_response(res)

async def add_job_info (request, job):
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
    email = None
    token = request.cookies.get(COOKIE_KEY)
    if token:
        email = get_email_from_oakvar_token(token)
    return email

def get_email_from_oakvar_token(token):
    import jwt
    data = jwt.decode(token, DEFAULT_PRIVATE_KEY, ["HS256"])
    email = data.get("email")
    return email

async def loginsuccess(request):
    import jwt
    from requests import get
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend

    data = await request.json()
    token = data.get("login_token")
    if not token:
        return web.json_response({"status": "error"})
    kid = jwt.get_unverified_header(token)["kid"]
    r = get(firebase_public_key_url)
    x509_key = r.json()[kid]
    key = x509.load_pem_x509_certificate(x509_key.encode("utf-8"), backend=default_backend)
    try:
        payload = jwt.decode(token, key.public_key(), ["RS256"], audience=PROJECT_ID) # type: ignore
    except:
        global logger
        if logger:
            logger.error(f"JWT decode error: {token}")
        return web.json_response({"status": "error"})
    email = payload.get("email")
    if not email:
        return web.json_response({"status": "error"})
    response = web.json_response({"status": "loggedin"})
    admindb = await get_admindb()
    await admindb.add_user_if_not_exist(email, "", "", "")
    oakvar_token = jwt.encode({"email": email}, DEFAULT_PRIVATE_KEY, algorithm="HS256")
    response.set_cookie(COOKIE_KEY, oakvar_token, httponly=True)
    return response

async def get_password_question (request):
    global servermode
    if servermode and not enable_remote_user_header and admindb:
        queries = request.rel_url.query
        email = queries['email']
        question = await admindb.get_password_question(email)
        if question is None:
            response = {'status':'fail', 'msg':'No such email'}
        else:
            response = {'status':'success', 'msg': question}
    else:
        response = {'status':'fail', 'msg':'no multiuser mode'}
    return web.json_response(response)

async def check_password_answer (request):
    from hashlib import sha256
    global servermode
    if servermode and not enable_remote_user_header and admindb:
        queries = request.rel_url.query
        email = queries['email']
        answer = queries['answer']
        m = sha256()
        m.update(answer.encode('utf-16be'))
        answerhash = m.hexdigest()
        correct = await admindb.check_password_answer(email, answerhash)
        if correct:
            temppassword = await set_temp_password(request)
            response = {'success': True, 'msg': temppassword}
        else:
            response = {'success': False, 'msg': 'Wrong answer'}
    else:
        response = {'success': False, 'msg': 'no multiuser mode'}
    return web.json_response(response)

async def set_temp_password (request):
    if admindb:
        queries = request.rel_url.query
        email = queries['email']
        temppassword = await admindb.set_temp_password(email)
        return temppassword

async def check_logged (request):
    email = get_email_from_request(request)
    if not email:
        response = {"logged": False}
    response = {'logged': True, 'email': email, 'admin': await is_admin_loggedin(request)}
    return web.json_response(response)

async def logout (_):
    global servermode
    if servermode:
        response = web.json_response({"status": "success"})
        response.del_cookie(COOKIE_KEY)
    else:
        response = web.json_response({"status": "error"})
    return response

async def get_input_stat (request):
    global servermode
    if not servermode or not admindb:
        return web.json_response('no multiuser mode')
    r = await is_admin_loggedin(request)
    if r == False:
        return web.json_response('no admin')
    queries = request.rel_url.query
    start_date = queries['start_date']
    end_date = queries['end_date']
    rows = await admindb.get_input_stat(start_date, end_date)
    return web.json_response(rows)

async def get_user_stat (request):
    global servermode
    if not servermode or not admindb:
        return web.json_response('no multiuser mode')
    r = await is_admin_loggedin(request)
    if r == False:
        return web.json_response('no admin')
    queries = request.rel_url.query
    start_date = queries['start_date']
    end_date = queries['end_date']
    rows = await admindb.get_user_stat(start_date, end_date)
    return web.json_response(rows)

async def get_job_stat (request):
    global servermode
    if not servermode:
        return web.json_response('no multiuser mode')
    r = await is_admin_loggedin(request)
    if r == False:
        return web.json_response('no admin')
    queries = request.rel_url.query
    start_date = queries['start_date']
    end_date = queries['end_date']
    if admindb:
        response = await admindb.get_job_stat(start_date, end_date)
    else:
        response = {}
    return web.json_response(response)

async def get_api_stat (request):
    global servermode
    if not servermode:
        return web.json_response('no multiuser mode')
    r = await is_admin_loggedin(request)
    if r == False:
        return web.json_response('no admin')
    queries = request.rel_url.query
    start_date = queries['start_date']
    end_date = queries['end_date']
    if admindb:
        response = await admindb.get_api_stat(start_date, end_date)
    else:
        response = {}
    return web.json_response(response)

async def get_annot_stat (request):
    global servermode
    if not servermode:
        return web.json_response('no multiuser mode')
    r = await is_admin_loggedin(request)
    if r == False:
        return web.json_response('no admin')
    queries = request.rel_url.query
    start_date = queries['start_date']
    end_date = queries['end_date']
    if admindb:
        response = await admindb.get_annot_stat(start_date, end_date)
    else:
        response = {}
    return web.json_response(response)

async def get_assembly_stat (request):
    global servermode
    if not servermode:
        return web.json_response('no multiuser mode')
    r = await is_admin_loggedin(request)
    if r == False:
        return web.json_response('no admin')
    queries = request.rel_url.query
    start_date = queries['start_date']
    end_date = queries['end_date']
    if admindb:
        response = await admindb.get_assembly_stat(start_date, end_date)
    else:
        response = {}
    return web.json_response(response)

async def restart (request):
    from os import execvp
    global servermode
    if servermode:
        r = await is_admin_loggedin(request)
        if r == False:
            return web.json_response({'success': False, 'mgs': 'Only logged-in admin can change the settings.'})
    execvp('wcravat', ['wcravat', '--multiuser', '--headless'])

async def show_login_page (request):
    from os.path import join
    from os.path import dirname
    from os.path import abspath
    global servermode
    global server_ready
    global logger
    if not servermode or not server_ready:
        if logger:
            logger.info('Login page requested but no multiuser mode. Redirecting to submit index...')
        return web.HTTPFound('/submit/index.html')
    r = await is_loggedin(request)
    if r == False:
        p = join(dirname(abspath(__file__)), 'nocache', 'login.html')
        return web.FileResponse(p)
    else:
        if logger:
            logger.info('Login page requested but already logged in. Redirecting to submit index...')
        return web.HTTPFound('/submit/index.html')

async def get_user_settings (request):
    admindb = await get_admindb()
    if not admindb:
        return web.json_response({})
    email = get_email_from_request(request)
    response = await admindb.get_user_settings(email)
    return web.json_response(response)

async def update_user_settings (request, d):
    admindb = await get_admindb()
    email = get_email_from_request(request)
    return await admindb.update_user_settings(email, d)

async def get_admindb():
    from .serveradmindb import ServerAdminDb
    global admindb
    if not admindb:
        admindb = ServerAdminDb()
        await admindb.init()
    return admindb

system_conf = get_system_conf()
enable_remote_user_header = system_conf.get('enable_remote_user_header', False)

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

