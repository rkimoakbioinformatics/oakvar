from typing import Optional
from typing import List
from typing import Dict


def report(
    dbpath: str,
    report_types: List[str],
    filterpath: Optional[str] = None,
    filter=None,
    filtersql: Optional[str] = None,
    filtername: Optional[str] = None,
    filterstring: Optional[str] = None,
    savepath: Optional[str] = None,
    confpath: Optional[str] = None,
    module_name: Optional[str] = None,
    nogenelevelonvariantlevel: bool = False,
    inputfiles: Optional[List[str]] = None,
    separatesample: bool = False,
    output_dir: Optional[str] = None,
    system_option: List[str] = [],
    includesample: Optional[List[str]] = [],
    excludesample: Optional[List[str]] = None,
    package: Optional[str] = None,
    modules_dir: Optional[str] = None,
    cols: Optional[List[str]] = None,
    level: Optional[str] = None,
    user: Optional[str] = None,
    no_summary: bool = False,
    serveradmindb=None,
    module_options: Dict[str, Dict] = {},
    outer=None,
    loop=None,
):
    from os.path import dirname
    from os.path import basename
    from os.path import join
    from ..lib.util.asyn import get_event_loop
    from ..lib.util.util import is_compatible_version
    from importlib.util import spec_from_file_location
    from importlib.util import module_from_spec
    from ..lib.exceptions import ModuleNotExist
    from ..lib.exceptions import IncompatibleResult
    from ..lib.module.local import get_local_module_info
    from . import handle_exception

    compatible_version, _, _ = is_compatible_version(dbpath)
    if not compatible_version:
        raise IncompatibleResult()
    if not report_types:
        if package:
            m_info = get_local_module_info(package)
            if m_info:
                package_conf = m_info.conf
                package_conf_reports = package_conf.get("run", {}).get("reports")
                if package_conf_reports:
                    report_types = package_conf_reports
    if not output_dir:
        output_dir = dirname(dbpath)
    if not savepath:
        run_name = basename(dbpath).rstrip("sqlite").rstrip(".")
        savepath = join(output_dir, run_name)
    else:
        savedir = dirname(savepath)
        if savedir != "":
            output_dir = savedir
    response = {}
    module_names = [v + "reporter" for v in report_types]
    for report_type, module_name in zip(report_types, module_names):
        try:
            module_info = get_local_module_info(module_name)
            if module_info is None:
                raise ModuleNotExist(report_type + "reporter")
            if outer:
                outer.write(f"Generating {report_type} report...")
            spec = spec_from_file_location(  # type: ignore
                module_name, module_info.script_path  # type: ignore
            )
            if not spec:
                continue
            module = module_from_spec(spec)  # type: ignore
            if not module or not spec.loader:
                continue
            spec.loader.exec_module(module)
            reporter_module_options = module_options.get(module_name, {})
            reporter = module.Reporter(
                dbpath,
                report_types=report_types,
                filterpath=filterpath,
                filter=filter,
                filtersql=filtersql,
                filtername=filtername,
                filterstring=filterstring,
                savepath=savepath,
                confpath=confpath,
                module_name=module_name,
                nogenelevelonvariantlevel=nogenelevelonvariantlevel,
                inputfiles=inputfiles,
                separatesample=separatesample,
                output_dir=output_dir,
                system_option=system_option,
                includesample=includesample,
                excludesample=excludesample,
                package=package,
                modules_dir=modules_dir,
                cols=cols,
                level=level,
                user=user,
                no_summary=no_summary,
                serveradmindb=serveradmindb,
                module_options=reporter_module_options,
                outer=outer,
            )
            response_t = None
            # uvloop cannot be patched.
            # nest_asyncio patch is necessary for use in Jupyter notebook.
            # old_loop = loop
            # new_loop = asyncio.new_event_loop()
            # asyncio.set_event_loop(new_loop)
            # nest_asyncio.apply(new_loop)
            if not loop:
                loop = get_event_loop()
            response_t = loop.run_until_complete(reporter.run())
            # asyncio.set_event_loop(old_loop)
            output_fns = None
            if type(response_t) == list:
                output_fns = " ".join(response_t)
            else:
                output_fns = response_t
            if output_fns is not None and type(output_fns) == str:
                if outer:
                    outer.write(f"report created: {output_fns}")
            response[report_type] = response_t
        except Exception as e:
            handle_exception(e)
    return response
