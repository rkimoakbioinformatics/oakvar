from typing import Optional
from typing import Any
from typing import List
from typing import Dict
from typing import Union
from pathlib import Path
from .test import test as do_test
from . import new
from . import store
from . import config
from . import module
from . import system
from . import util

_ = do_test or config or module or new or store or system or util


def report_issue():
    """Opens a webpage to report issues."""
    from ..lib.util.admin_util import report_issue

    return report_issue()


def run(
    inputs: Union[Union[Path, str], List[Union[Path, str]]],
    annotators: List[str] = [],
    report_types: Union[str, List[str]] = [],
    annotators_replace: List[str] = [],
    excludes: List[str] = [],
    run_name: List[str] = [],
    output_dir: List[str] = [],
    startat: Optional[str] = None,
    endat: Optional[str] = None,
    skip: List[str] = [],
    confpath: Optional[str] = None,
    conf: dict = {},
    genome: Optional[str] = None,
    cleandb: bool = False,
    newlog: bool = False,
    note: str = "",
    mp: Optional[int] = None,
    keep_temp: bool = False,
    writeadmindb: bool = False,
    job_name: Optional[List[str]] = None,
    separatesample: bool = False,
    primary_transcript: List[str] = ["mane"],
    clean: bool = False,
    module_options: Dict = {},
    system_option: Dict = {},
    package: Optional[str] = None,
    filtersql: Optional[str] = None,
    includesample: Optional[List[str]] = None,
    excludesample: Optional[List[str]] = None,
    filter: Optional[str] = None,
    filterpath: Optional[str] = None,
    modules_dir: Optional[str] = None,
    preparers: List[str] = [],
    mapper_name: List[str] = [],
    postaggregators: List[str] = [],
    vcf2vcf: bool = False,
    logtofile: bool = False,
    loglevel: str = "INFO",
    combine_input: bool = False,
    input_format: Optional[str] = None,
    input_encoding: Optional[str] = None,
    uid: Optional[str] = None,
    loop=None,
    outer=None,
) -> Optional[Dict[str, Any]]:
    """Performs OakVar pipeline from conversion -> mapping -> annotation -> database generation -> post annotation -> report generation.

    Args:
        inputs (List[Union[Path, str]]): Paths to input files. URLs can be used as well, in which the files will be downloaded.
        combine_input (bool): If True, all input files will be combined as one input.
        annotators (List[str]): Annotator modules to run
        report_types (Union[str, List[str]]): Report types. If given, report files of given types will be generated. If `vcfreporter` is installed in your system, giving `vcf` will invoke the module.
        clean (bool): Cleans all output and intermediate files and then starts the pipeline.
        vcf2vcf (bool): If True, the pipeline will run in vcf2vcf mode, where input and output should be VCF format files and result database files will not be generated. This can increase the speed of the pipeline significantly.
        logtofile (bool): If True, .log and .err log files will be generated for normal and error logs.
        input_format (Optional[str]): Overrides automatic detection of input file format.
        postaggregators (List[str]): Postaggregator modules to run
        preparers (List[str]): Preparer modules to run
        mapper_name (List[str]): Mapper module to run
        output_dir (List[str]): Output directories. The order of inputs and output_dir elements should match.
        startat (Optional[str]): Start at the specified step. Options are `converter`, `mapper`, `annotator`, `aggregator`, `postaggregator`, and `reporter`.
        endat (Optional[str]): End at the specified step. Options are `converter`, `mapper`, `annotator`, `aggregator`, `postaggregator`, and `reporter`.
        skip (List[str]): Skip the specified steps. Options are `converter`, `mapper`, `annotator`, `aggregator`, `postaggregator`, and `reporter`.
        genome (Optional[str]): Genome assembly of all input files. If not given, genome assembly will be figured out or default to what is defined in lib/system/consts.py:default_assembly.
        input_encoding (Optional[str]): input_encoding
        mp (Optional[int]): Number of cores to use. Default value can be changed by `ov config system max_num_concurrent_annotators_per_job <value>`.
        primary_transcript (List[str]): primary_transcript
        modules_dir (Optional[str]): modules_dir
        run_name (List[str]): run_name
        annotators_replace (List[str]): annotators_replace
        excludes (List[str]): excludes
        confpath (Optional[str]): confpath
        conf (dict): conf
        cleandb (bool): cleandb
        newlog (bool): newlog
        note (str): note
        keep_temp (bool): keep_temp
        writeadmindb (bool): writeadmindb
        job_name (Optional[List[str]]): job_name
        separatesample (bool): separatesample
        module_options (Dict): module_options
        system_option (Dict): system_option
        package (Optional[str]): package
        filtersql (Optional[str]): filtersql
        includesample (Optional[List[str]]): includesample
        excludesample (Optional[List[str]]): excludesample
        filter (Optional[str]): filter
        filterpath (Optional[str]): filterpath
        loglevel (str): loglevel
        uid (Optional[str]): uid
        loop:
        outer:

    Returns:
        None or a dict of reporter names and their return values
    """
    from ..lib.base.runner import Runner
    from ..lib.util.asyn import get_event_loop

    # nested asyncio
    # nest_asyncio.apply()
    # Custom system conf
    input_paths: List[str] = []
    if isinstance(inputs, str):
        input_paths = [inputs]
    elif isinstance(inputs, Path):
        input_paths = [str(inputs)]
    elif isinstance(inputs, List):
        for el in inputs:
            if isinstance(el, Path):
                input_paths.append(str(el))
            elif isinstance(el, str):
                input_paths.append(el)
    if isinstance(report_types, str):
        report_types = [report_types]
    module = Runner(
        inputs=input_paths,
        annotators=annotators,
        annotators_replace=annotators_replace,
        excludes=excludes,
        run_name=run_name,
        output_dir=output_dir,
        startat=startat,
        endat=endat,
        skip=skip,
        confpath=confpath,
        conf=conf,
        report_types=report_types,
        genome=genome,
        cleandb=cleandb,
        newlog=newlog,
        note=note,
        mp=mp,
        keep_temp=keep_temp,
        writeadmindb=writeadmindb,
        job_name=job_name,
        separatesample=separatesample,
        primary_transcript=primary_transcript,
        clean=clean,
        module_options=module_options,
        system_option=system_option,
        package=package,
        filtersql=filtersql,
        includesample=includesample,
        excludesample=excludesample,
        filter=filter,
        filterpath=filterpath,
        modules_dir=modules_dir,
        preparers=preparers,
        mapper_name=mapper_name,
        postaggregators=postaggregators,
        vcf2vcf=vcf2vcf,
        logtofile=logtofile,
        loglevel=loglevel,
        combine_input=combine_input,
        input_format=input_format,
        input_encoding=input_encoding,
        uid=uid,
        outer=outer,
    )
    if isinstance(inputs, str):
        inputs = [inputs]
    if isinstance(output_dir, str):
        output_dir = [output_dir]
    if isinstance(run_name, str):
        run_name = [run_name]
    if not loop:
        loop = get_event_loop()
    return loop.run_until_complete(module.main())


def report(
    dbpath: Union[Path, str],
    report_types: Optional[Union[str, List[str]]] = None,
    module_paths: Optional[List[Union[str, Path]]] = None,
    filterpath: Optional[str] = None,
    filter: Optional[dict] = None,
    filtersql: Optional[str] = None,
    filtername: Optional[str] = None,
    filterstring: Optional[str] = None,
    savepath: Optional[str] = None,
    confpath: Optional[str] = None,
    nogenelevelonvariantlevel: bool = False,
    inputfiles: Optional[List[str]] = None,
    separatesample: bool = False,
    output_dir: Optional[str] = None,
    includesample: Optional[List[str]] = [],
    excludesample: Optional[List[str]] = None,
    package: Optional[str] = None,
    cols: Optional[List[str]] = None,
    level: Optional[str] = None,
    user: Optional[str] = None,
    no_summary: bool = False,
    serveradmindb=None,
    module_options: Dict[str, Dict] = {},
    outer=None,
    loop=None,
) -> Dict[str, Any]:
    """Generates OakVar report files based on an OakVar result database file.

    Args:
        dbpath (str): Path to an OakVar result database file
        report_types (Optional[Union[str, List[str]]]): Report types. For example, if `vcfreporter` module is installed, `"vcf"` will invoke the reporter.
        module_paths (Union[str, List[Path]]): Paths to report modules can be directly given. This option will override report_types. For example, if `customreporter` module is installed at `/home/user/ov_dev/customreporter`, this value can be given.
        output_dir (Optional[str]): Directory to store reports
        module_options (Dict[str, Dict]): Reporter module-specific options. For example, to tell `vcfreporter` to combine all OakVar result fields under one field, `{"vcfreporter": {"type": "combined"}}` can be used.
        cols (Optional[List[str]]): Result columns to include. By default, all result columns are included in reports. For example, `["base__uid", "base__chrom", "base__pos", "base__ref_base", "base__alt_base", "clinvar__sig"]` will include only the variants and ClinVar significances.
        includesample (Optional[List[str]]): Samples to include in filtered reports
        excludesample (Optional[List[str]]): Samples to exclude from filtered reports
        filterpath (Optional[str]): filterpath
        filter (Optional[dict]): filter as dict
        filtersql (Optional[str]): filter sql
        filtername (Optional[str]): filter file
        filterstring (Optional[str]): filter dict as str
        savepath (Optional[str]): savepath
        confpath (Optional[str]): confpath
        nogenelevelonvariantlevel (bool): nogenelevelonvariantlevel
        inputfiles (Optional[List[str]]): inputfiles
        separatesample (bool): separatesample
        package (Optional[str]): package
        modules_dir (Optional[str]): modules_dir
        level (Optional[str]): level
        user (Optional[str]): user
        no_summary (bool): no_summary
        serveradmindb:
        outer:
        loop:

    Returns:
        None or a dict of reporter names and their return values
    """
    from os.path import dirname
    from os.path import basename
    from os.path import join
    from ..lib.util.asyn import get_event_loop
    from ..lib.util.util import is_compatible_version
    from importlib.util import spec_from_file_location
    from importlib.util import module_from_spec
    from ..lib.exceptions import IncompatibleResult
    from ..lib.module.local import get_local_module_info
    from ..lib.module.local import LocalModule
    from . import handle_exception

    if not report_types:
        if package:
            m_info = get_local_module_info(package)
            if m_info:
                package_conf = m_info.conf
                package_conf_reports = package_conf.get("run", {}).get("reports")
                if package_conf_reports:
                    report_types = package_conf_reports
    if isinstance(report_types, str):
        report_types = [report_types]
    compatible_version, _, _ = is_compatible_version(dbpath)
    if not compatible_version:
        raise IncompatibleResult()
    if not output_dir:
        output_dir = dirname(dbpath)
    if not savepath:
        run_name = basename(dbpath).rstrip("sqlite").rstrip(".")
        savepath = join(output_dir, run_name)
    else:
        savedir = dirname(savepath)
        if savedir != "":
            output_dir = savedir
    response: Dict[str, Any] = {}
    module_infos: Dict[str, LocalModule] = {}
    if module_paths:
        for module_path in module_paths:
            module_info = get_local_module_info(module_path)
            if module_info:
                module_infos[module_info.name] = module_info
            else:
                if outer:
                    outer.error(f"{module_path} does not exist.")
    elif report_types:
        module_names = [v + "reporter" for v in report_types]
        for module_name in module_names:
            module_info = get_local_module_info(module_name)
            if module_info:
                module_infos[module_info.name] = module_info
            else:
                if outer:
                    outer.error(f"{module_name} does not exist.")
    else:
        return response
    for module_name, module_info in module_infos.items():
        try:
            if outer:
                outer.write(f"Generating {module_name} report...")
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
                includesample=includesample,
                excludesample=excludesample,
                package=package,
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
            response[module_name] = response_t
        except Exception as e:
            handle_exception(e)
    return response


def version() -> str:
    """Gets OakVar version."""
    from ..lib.util.admin_util import oakvar_version

    ret = oakvar_version()
    return ret


def license(outer=None):
    from ..lib.system import show_license

    show_license(outer=outer)


def update(outer=None):
    from ..lib.system import update

    update(outer=outer)


def handle_exception(e: Exception):
    """handle_exception.

    Args:
        e (Exception): e
    """
    from sys import stderr
    from traceback import print_exc
    from ..lib.exceptions import ExpectedException
    import sys

    msg = getattr(e, "msg", None)
    if msg:
        stderr.write(msg)
        stderr.write("\n")
        stderr.flush()
    trc = getattr(e, "traceback", None)
    if trc:
        print_exc()
    isatty = hasattr(sys, "ps1")  # interactive shell?
    halt = getattr(e, "halt", False)
    returncode = getattr(e, "returncode", 1)
    if hasattr(e, "traceback") and getattr(e, "traceback"):
        import traceback

        traceback.print_exc()
    if isinstance(e, ExpectedException):
        if halt:
            if isatty:
                return False
            else:
                exit(returncode)
        else:
            if isatty:
                return False
            else:
                return False
    elif isinstance(e, KeyboardInterrupt):
        pass
    else:
        raise e
