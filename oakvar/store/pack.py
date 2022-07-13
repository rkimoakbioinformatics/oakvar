from typing import Tuple


def get_module_name_and_module_dir(args) -> Tuple[str, str]:
    from os.path import exists
    from os.path import basename

    module_name = args.get("module")
    if not module_name:
        from ..exceptions import ArgumentError

        raise ArgumentError(msg="argument module is missing")
    if exists(module_name):
        module_dir = module_name
        module_name = basename(module_dir)
    else:
        from ..module.local import get_module_dir

        module_dir = get_module_dir(module_name)
    if not module_dir:
        from ..exceptions import ModuleLoadingError

        raise ModuleLoadingError(module_name)
    return module_name, module_dir


def get_pack_dir_out_dir(kind: str, args: dict, module_dir: str) -> Tuple[str, str]:
    from os.path import exists
    from os.path import join

    outdir = args.get("outdir", ".")
    if not exists(outdir):
        from os import mkdir

        mkdir(outdir)
    if kind == "code":
        pack_dir = module_dir
    elif kind == "data":
        pack_dir = join(module_dir, "data")
    else:
        from ..exceptions import ArgumentError

        raise ArgumentError(msg=f"argument kind={kind} is wrong.")
    return pack_dir, outdir


def pack_module_zip(args: dict, kind: str):
    from os.path import join
    from zipfile import ZipFile
    from os import walk
    from os import sep
    from os.path import basename
    from os.path import exists
    from os import sep
    from ..util.util import quiet_print
    from ..module.local import get_module_code_version

    module_name, module_dir = get_module_name_and_module_dir(args)
    version = get_module_code_version(module_name)
    pack_dir, outdir = get_pack_dir_out_dir(kind, args, module_dir)
    if exists(pack_dir):
        pack_fn = f"{module_name}__{version}__{kind}.zip"
        pack_path = join(outdir, pack_fn)
        with ZipFile(pack_path, "w") as z:
            for root, _, files in walk(pack_dir):
                root_basename = basename(root)
                if root_basename.startswith(".") or root_basename.startswith("_"):
                    continue
                if kind == "code" and root_basename == "data":
                    continue
                for file in files:
                    if (
                        file.startswith(".")
                        or file == "startofinstall"
                        or file == "endofinstall"
                    ):
                        continue
                    p = join(root, file)
                    arcname = join(root, file)
                    if pack_dir in arcname:
                        arcname = arcname[len(pack_dir) :].lstrip(sep)
                    if kind == "code":
                        arcname = arcname  # join(module_name, arcname)
                    elif kind == "data":
                        arcname = join("data", arcname)
                    z.write(p, arcname=arcname)
            quiet_print(f"{pack_path} written", args=args)


def pack_module(args):
    pack_module_zip(args, "code")
    pack_module_zip(args, "data")
    return True
