def print_module_info(module_info={}, outer=None):
    from rich.console import Console

    console = Console(file=outer)
    readme_table = get_module_info_readme_table(module_info=module_info)
    basic_table = get_module_info_basic_table(module_info=module_info)
    developer_table = get_module_info_developer_table(module_info=module_info)
    version_table = get_module_info_version_table(module_info=module_info)
    output_table = get_module_info_output_table(module_info=module_info)
    if readme_table:
        console.print(readme_table)
    console.print(basic_table)
    if developer_table:
        console.print(developer_table)
    console.print(version_table)
    if output_table:
        console.print(output_table)


def get_module_info_readme_table(module_info={}):
    from rich.table import Table
    from rich import box

    readme = module_info.get("readme")
    if not readme:
        return
    readme_table = Table(
        title="README", title_style="bold", show_header=False, box=box.SQUARE
    )
    readme_table.add_column("Readme")
    readme_table.add_row(readme)
    return readme_table


def get_module_info_basic_table(module_info={}):
    from rich.table import Table
    from rich import box

    table = Table(show_header=False, title_style="bold", box=box.SQUARE)
    table.add_column("Category")
    table.add_column("Value")
    for k, v in module_info.items():
        if k in ["readme", "output_columns", "versions", "developer"]:
            continue
        if type(v) == list:
            v = ", ".join(v)
        table.add_row(k, str(v))
    return table


def add_module_info_developer_table_rows(developer_table, developers):
    developer_table.add_row("Name", str(developers.get("name")))
    developer_table.add_row("Organization", str(developers.get("organization")))
    developer_table.add_row("Email", str(developers.get("email")))
    developer_table.add_row("Website", str(developers.get("website")))
    developer_table.add_row("Citation", str(developers.get("citation")))


def get_module_info_developer_table(module_info={}):
    from rich.table import Table
    from rich import box

    developers = module_info.get("developer")
    if not developers:
        return
    developer_table = Table(
        title="Developers", title_style="bold", show_header=False, box=box.SQUARE
    )
    developer_table.add_column("Category")
    developer_table.add_column("Value")
    if "name" in developers:
        add_module_info_developer_table_rows(developer_table, developers)
    else:
        if "module" in developers:
            developer_table.add_row("[bold]Module[/bold]", "")
            add_module_info_developer_table_rows(
                developer_table, developers.get("module")
            )
        if "data" in developers:
            developer_table.add_row("[bold]Data[/bold]", "")
            add_module_info_developer_table_rows(
                developer_table, developers.get("data")
            )
    return developer_table


def get_module_info_version_table(module_info={}):
    from rich.table import Table
    from rich import box
    from packaging.version import Version

    versions = module_info.get("versions")
    if not versions:
        return None
    version_table = Table(title="Versions", title_style="bold", box=box.SQUARE)
    version_table.add_column("Version")
    version_table.add_column("Data version")
    version_table.add_column("Data source")
    version_table.add_column("Minimum OakVar version")
    code_vers = [v for v in versions.keys()]
    code_vers.sort(key=lambda x: Version(x))
    for code_ver in code_vers:
        dd = versions.get(code_ver)
        version_table.add_row(
            code_ver,
            dd.get("data_version"),
            dd.get("data_source"),
            dd.get("min_pkg_ver"),
        )
    return version_table


def get_module_info_output_table(module_info={}):
    from rich.table import Table
    from rich import box

    output_columns = module_info.get("output_columns")
    if not output_columns:
        return
    output_table = Table(title="Output", title_style="bold", box=box.SQUARE)
    output_table.add_column("Name")
    output_table.add_column("Title")
    output_table.add_column("Description")
    output_table.add_column("Type")
    for col in output_columns:
        ty = col.get("type", "string")
        output_table.add_row(col.get("name"), col.get("title"), col.get("desc"), ty)
    return output_table
