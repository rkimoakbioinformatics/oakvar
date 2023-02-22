from typing import Optional
from typing import List
from typing import Dict


def run(
    inputs: List[str],
    annotators: List[str] = [],
    annotators_replace: List[str] = [],
    excludes: List[str] = [],
    run_name: List[str] = [],
    output_dir: List[str] = [],
    startat: Optional[str] = None,
    endat: Optional[str] = None,
    skip: List[str] = [],
    confpath: Optional[str] = None,
    conf: dict = {},
    report_types: List[str] = [],
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
):
    """run.

    Args:
        inputs (List[str]): inputs
        annotators (List[str]): annotators
        annotators_replace (List[str]): annotators_replace
        excludes (List[str]): excludes
        run_name (List[str]): run_name
        output_dir (List[str]): output_dir
        startat (Optional[str]): startat
        endat (Optional[str]): endat
        skip (List[str]): skip
        confpath (Optional[str]): confpath
        conf (dict): conf
        report_types (List[str]): report_types
        genome (Optional[str]): genome
        cleandb (bool): cleandb
        newlog (bool): newlog
        note (str): note
        mp (Optional[int]): mp
        keep_temp (bool): keep_temp
        writeadmindb (bool): writeadmindb
        job_name (Optional[List[str]]): job_name
        separatesample (bool): separatesample
        primary_transcript (List[str]): primary_transcript
        clean (bool): clean
        module_options (Dict): module_options
        system_option (Dict): system_option
        package (Optional[str]): package
        filtersql (Optional[str]): filtersql
        includesample (Optional[List[str]]): includesample
        excludesample (Optional[List[str]]): excludesample
        filter (Optional[str]): filter
        filterpath (Optional[str]): filterpath
        modules_dir (Optional[str]): modules_dir
        preparers (List[str]): preparers
        mapper_name (List[str]): mapper_name
        postaggregators (List[str]): postaggregators
        vcf2vcf (bool): vcf2vcf
        logtofile (bool): logtofile
        loglevel (str): loglevel
        combine_input (bool): combine_input
        input_format (Optional[str]): input_format
        input_encoding (Optional[str]): input_encoding
        uid (Optional[str]): uid
        loop:
        outer:
    """
    from ..lib.base.runner import Runner
    from ..lib.util.asyn import get_event_loop

    # nested asyncio
    # nest_asyncio.apply()
    # Custom system conf
    module = Runner(
        inputs=inputs,
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
