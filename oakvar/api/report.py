def report(args, __name__="report"):
    from os.path import dirname
    from os.path import basename
    from os.path import join
    from ..lib.util.asyn import get_event_loop
    from ..lib.util.util import is_compatible_version
    from importlib.util import spec_from_file_location
    from importlib.util import module_from_spec
    from ..lib.exceptions import ModuleNotExist
    from ..lib.exceptions import IncompatibleResult
    from ..lib.util.util import quiet_print
    from ..lib.module.local import get_local_module_info
    from ..lib.system import consts
    from . import handle_exception
    from ..lib.consts import MODULE_OPTIONS_KEY

    dbpath = args.get("dbpath")
    compatible_version, _, _ = is_compatible_version(dbpath)
    if not compatible_version:
        raise IncompatibleResult()
    report_types = args.get("reports")
    md = args.get("md")
    if md:
        consts.custom_modules_dir = md
    package = args.get("package")
    if not report_types:
        if package:
            m_info = get_local_module_info(package)
            if m_info:
                package_conf = m_info.conf
                if "run" in package_conf and "reports" in package_conf["run"]:
                    report_types = package_conf["run"]["reports"]
    output_dir = args.get("output_dir")
    if not output_dir:
        output_dir = dirname(dbpath)
    savepath = args.get("savepath")
    if not savepath:
        run_name = basename(dbpath).rstrip("sqlite").rstrip(".")
        args["savepath"] = join(output_dir, run_name)
    else:
        savedir = dirname(savepath)
        if savedir != "":
            output_dir = savedir
    module_options = {}
    module_option = args.get("module_option")
    if module_option:
        for opt_str in module_option:
            toks = opt_str.split("=")
            if len(toks) != 2:
                quiet_print(
                    "Ignoring invalid module option {opt_str}. module-option should be module_name.key=value.",
                    args,
                )
                continue
            k = toks[0]
            if k.count(".") != 1:
                quiet_print(
                    "Ignoring invalid module option {opt_str}. module-option should be module_name.key=value.",
                    args,
                )
                continue
            [module_name, key] = k.split(".")
            if module_name not in module_options:
                module_options[module_name] = {}
            v = toks[1]
            module_options[module_name][key] = v
    loop = get_event_loop()
    response = {}
    module_names = [v + "reporter" for v in report_types]
    for report_type, module_name in zip(report_types, module_names):
        try:
            module_info = get_local_module_info(module_name)
            if module_info is None:
                raise ModuleNotExist(report_type + "reporter")
            quiet_print(f"Generating {report_type} report... ", args)
            module_name = module_info.name
            spec = spec_from_file_location(  # type: ignore
                module_name, module_info.script_path  # type: ignore
            )
            if not spec:
                continue
            module = module_from_spec(spec)  # type: ignore
            if not module or not spec.loader:
                continue
            spec.loader.exec_module(module)
            args["module_name"] = module_name
            if module_name in module_options:
                args[MODULE_OPTIONS_KEY] = module_options[module_name]
            reporter = module.Reporter(args)
            response_t = None
            response_t = loop.run_until_complete(reporter.run())
            output_fns = None
            if type(response_t) == list:
                output_fns = " ".join(response_t)
            else:
                output_fns = response_t
            if output_fns is not None and type(output_fns) == str:
                quiet_print(f"report created: {output_fns}", args)
            response[report_type] = response_t
        except Exception as e:
            handle_exception(e)
    return response

