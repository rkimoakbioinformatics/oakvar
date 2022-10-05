import markdown


def get_remote_manifest(handler):
    manifest = handler.get_remote_manifest()
    return manifest


def get_module_readme(request):
    from aiohttp.web import Response
    from ..module import get_readme

    module_name = request.match_info["module"]
    version = request.match_info["version"]
    if version == "latest":
        version = None
    readme_md = get_readme(module_name)
    if readme_md is None:
        response = Response(status=404)
    else:
        readme_html = markdown.markdown(readme_md)
        response = Response(body=readme_html, content_type="text/html")
    return response


def get_local_manifest():
    from aiohttp.web import json_response
    from ..module import list_local
    from ..module.local import get_local_module_info

    module_names = list_local()
    out = {}
    for module_name in module_names:
        local_info = get_local_module_info(module_name)
        if local_info is not None:
            out[module_name] = {
                "version": local_info.version,
                "type": local_info.type,
                "title": local_info.title,
                "description": local_info.description,
                "developer": local_info.developer,
            }
    return json_response(out)


def install_module(request):
    from aiohttp.web import Response
    from ..module import install_module

    module = request.json()
    module_name = module["name"]
    version = module["version"]
    install_module(module_name, version=version)
    return Response()


def uninstall_module(request):
    from aiohttp.web import Response
    from ..module import uninstall_module

    module = request.json()
    module_name = module["name"]
    uninstall_module(module_name)
    return Response()
