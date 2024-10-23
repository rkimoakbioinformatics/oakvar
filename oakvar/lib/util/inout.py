# OakVar
#
# Copyright (c) 2024 Oak Bioinformatics, LLC
#
# All rights reserved.
#
# Do not distribute or use this software without obtaining
# a license from Oak Bioinformatics, LLC.
#
# Do not use this software to develop another software
# which competes with the products by Oak Bioinformatics, LLC,
# without obtaining a license for such use from Oak Bioinformatics, LLC.
#
# For personal use of non-commercial nature, you may use this software
# after registering with `ov store account create`.
#
# For research use of non-commercial nature, you may use this software
# after registering with `ov store account create`.
#
# For use by commercial entities, you must obtain a commercial license
# from Oak Bioinformatics, LLC. Please write to info@oakbioinformatics.com
# to obtain the commercial license.
# ================
# OpenCRAVAT
#
# MIT License
#
# Copyright (c) 2021 KarchinLab
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import Union
from typing import Optional
from typing import Dict
from typing import Any
from pathlib import Path


class BaseFile(object):
    valid_types = ["string", "int", "float"]

    def __init__(self, path):
        from os.path import abspath

        self.path = abspath(path)
        self.columns: Dict[int, ColumnDefinition] = {}

    def _validate_col_type(self, col_type):
        if col_type not in self.valid_types:
            raise Exception(
                "Invalid column type {} in {}. Choose from {}".format(
                    col_type, self.path, ", ".join(self.valid_types)
                )
            )

    def get_col_def(self, col_index):
        return self.columns[col_index]

    def get_all_col_defs(self):
        return self.columns


class FileReader(BaseFile):
    def __init__(
        self, path, seekpos: int = 0, chunksize: Optional[int] = None, logger=None
    ):
        from .util import detect_encoding

        super().__init__(path)
        self.seekpos = seekpos
        self.chunksize = chunksize
        self.encoding = detect_encoding(self.path)
        self.annotator_name = ""
        self.annotator_displayname = ""
        self.annotator_version = ""
        self.index_columns = []
        self.report_substitution = None
        self.f = None
        self.csvfmt: bool = False
        self.logger = logger
        self._setup_definition()

    def _setup_definition(self):
        from json import loads
        from json.decoder import JSONDecodeError

        with open(self.path, encoding=self.encoding) as f:
            line = f.readline()[:-1]
            if line.startswith("#fmt=csv"):
                self.csvfmt = True
        for line in self._loop_definition():
            if line.startswith("#name="):
                self.annotator_name = line.split("=")[1]
            elif line.startswith("#displayname="):
                self.annotator_displayname = line.split("=")[1]
            elif line.startswith("#version="):
                self.annotator_version = line.split("=")[1]
            elif line.startswith("#index="):
                cols = line.split("=")[1].split(",")
                self.index_columns.append(cols)
            elif line.startswith("#column="):
                coldef = ColumnDefinition({})
                col_s = "=".join(line.split("=")[1:])
                try:
                    coldef.from_json(col_s)
                except JSONDecodeError:
                    if self.logger:
                        self.logger.error(f"column definition error: {col_s}")
                    coldef.from_var_csv(col_s)
                self._validate_col_type(coldef.type)
                self.columns[coldef.index] = coldef
            elif line.startswith("#report_substitution="):
                self.report_substitution = loads(line.split("=")[1])
            else:
                continue

    def get_index_columns(self):
        return self.index_columns

    def override_column(
        self, index, name, title=None, data_type="string", cats=[], category=None
    ):
        if title is None:
            title = " ".join(x.title() for x in name.split("_"))
        if index not in self.columns:
            self.columns[index] = ColumnDefinition({})
        self.columns[index].title = title
        self.columns[index].name = name
        self.columns[index].type = data_type
        self.columns[index].categories = cats
        self.columns[index].category = category

    def get_column_names(self):
        sorted_order = sorted(list(self.columns.keys()))
        return [self.columns[x].name for x in sorted_order]

    def get_annotator_name(self):
        return self.annotator_name

    def get_annotator_displayname(self):
        return self.annotator_displayname

    def get_annotator_version(self):
        return self.annotator_version

    def get_chunksize(self, num_core):
        f = open(self.path)
        max_data_line_no = 0
        max_line_no = 0
        for line in f:
            max_line_no += 1
            if line.startswith("#"):
                continue
            max_data_line_no += 1
        chunksize = max(int(max_data_line_no / num_core), 1)
        f.seek(0)
        poss = [[0, 0]]
        line_no = 0
        data_line_no = 0
        while True:
            line = f.readline()
            line_no += 1
            if not line.startswith("#"):
                data_line_no += 1
                if data_line_no % chunksize == 0 and len(poss) < num_core:
                    poss.append([f.tell(), chunksize])
            if line_no == max_line_no:
                break
        f.close()
        len_poss = len(poss)
        return max_line_no, chunksize, poss, len_poss, max_data_line_no

    def loop_data(self):
        from ..exceptions import BadFormatError
        from json import loads

        for lnum, toks in self._loop_data():
            out = {}
            if len(toks) < len(self.columns):
                err_msg = "Too few columns. Received %s. Expected %s." % (
                    len(toks),
                    len(self.columns),
                )
                return BadFormatError(err_msg)
            for col_index, col_def in self.columns.items():
                col_name = col_def.name
                col_type = col_def.type
                tok = toks[col_index]
                if tok == "":
                    out[col_name] = None
                else:
                    if col_type == "string":
                        out[col_name] = tok
                    elif col_type == "int":
                        try:
                            out[col_name] = int(tok)
                        except ValueError:
                            try:
                                out[col_name] = int(float(tok))
                            except Exception:
                                out[col_name] = None
                        except Exception:
                            out[col_name] = None
                    elif col_type == "float":
                        try:
                            tok = loads(tok)
                            if type(tok) == list:
                                out[col_name] = ",".join([str(v) for v in tok])
                            else:
                                out[col_name] = float(tok)
                        except Exception:
                            tok = None
            yield lnum, toks, out

    def get_data(self):
        all_data = [d for _, _, d in self.loop_data()]
        return all_data

    def _loop_definition(self):
        if self.csvfmt:
            f = open(self.path, newline="", encoding=self.encoding)
        else:
            f = open(self.path, encoding=self.encoding)
        for line in f:
            line = line.rstrip().lstrip()
            if line.startswith("#"):
                yield line
            else:
                break
        f.close()

    def _loop_data(self):
        if not self.encoding:
            return
        if self.csvfmt:
            with open(self.path, newline="") as f:
                f.seek(self.seekpos)
                lnum = 0
                import csv

                csv.field_size_limit(
                    1147483647
                )  # crude way. 2147483647 is the min of C long max.
                csvreader = csv.reader(f)
                num_data_rows = 0
                for row in csvreader:
                    if row[0].startswith("#"):
                        continue
                    yield csvreader.line_num, row
                    num_data_rows += 1
                    if self.chunksize and num_data_rows >= self.chunksize:
                        return
        else:
            with open(self.path, "rb") as f:
                if self.seekpos is not None:
                    f.seek(self.seekpos)
                lnum = 0
                for line in f:
                    line = line.decode(self.encoding)
                    if line.startswith("#"):
                        continue
                    else:
                        line = line.rstrip("\r\n")
                        yield lnum, line.split("\t")
                    lnum += 1
                    if self.chunksize is not None and lnum == self.chunksize:
                        break


class FileWriter(BaseFile):
    def __init__(
        self,
        path,
        include_definition=True,
        include_titles=True,
        titles_prefix="#",
        columns=[],
        mode="w",
        fmt="csv",
    ):
        from sys import platform

        super().__init__(path)
        self.csvfmt: bool = False
        if fmt == "csv":
            self.csvfmt = True
        self.csvwriter = None
        if fmt == "csv":
            self.wf = open(self.path, mode, newline="", encoding="utf-8")
            from csv import writer

            if platform == "win32":
                lineterminator = "\r\n"
            else:
                lineterminator: str = "\n"
            self.csvwriter = writer(self.wf, lineterminator=lineterminator)
            if mode == "w":
                self.wf.write("#fmt=csv\n")
        else:
            self.wf = open(self.path, mode, encoding="utf-8")
        self.mode: str = mode
        self.ready_to_write = False
        self.ordered_columns = []
        self.name_to_col_index = {}
        self.title_toks = []
        self.include_definition = include_definition
        self.include_titles = include_titles
        self.titles_prefix = titles_prefix
        self.add_columns(columns)

    def add_column(self, col_d):
        col_index = len(self.columns)
        col_d["index"] = col_index
        col_def = ColumnDefinition(col_d)
        for i in self.columns:
            if self.columns[i].name == col_def.name:
                continue
        self.columns[col_index] = col_def

    def insert_column_after(self, col_d, col_name):
        col_idx = None
        for i in range(len(self.columns)):
            if self.columns[i].name == col_name:
                col_idx = i
                break
        if col_idx is None:
            raise Exception(f"Column {col_name} not found")
        for i in range(len(self.columns) - 1, col_idx, -1):
            v = self.columns[i]
            self.columns[i + 1] = v
        self.columns[col_idx + 1] = ColumnDefinition(col_d)

    def add_columns(self, col_defs):
        for col_def in col_defs:
            self.add_column(col_def)

    def prep_for_write(self):
        if self.ready_to_write:
            return
        col_indices = sorted(self.columns.keys())
        correct_index = -1
        for col_index in col_indices:
            correct_index += 1
            if correct_index != col_index:
                raise Exception("Column %d must be defined" % correct_index)
            col_def = self.columns[col_index]
            self.ordered_columns.append(col_def)
            self.title_toks.append(col_def.title)
            self.name_to_col_index[col_def.name] = col_index
        self.ready_to_write = True

    def write_names(self, annotator_name, annotator_display_name, annotator_version):
        line = "#name={:}\n".format(annotator_name)
        self.wf.write(line)
        line = "#displayname={:}\n".format(annotator_display_name)
        self.wf.write(line)
        line = "#version={:}\n".format(annotator_version)
        self.wf.write(line)
        self.wf.flush()

    def add_index(self, index_columns):
        self.write_meta_line("index", ",".join(index_columns))

    def write_meta_line(self, key, value):
        line = "#{:}={:}\n".format(key, value)
        self.wf.write(line)
        self.wf.flush()

    def write_definition(self, conf=None):
        from json import dumps

        self.prep_for_write()
        for col_def in self.ordered_columns:
            self.write_meta_line("column", col_def.get_json())
        if conf and "report_substitution" in conf:
            self.write_meta_line(
                "report_substitution", dumps(conf["report_substitution"])
            )
        self.wf.flush()

    def write_input_paths(self, input_path_dict):
        from json import dumps

        s = "#input_paths={}\n".format(dumps(input_path_dict))
        self.wf.write(s)
        self.wf.flush()

    def write_data(self, data):
        if not data:
            return
        self.prep_for_write()
        wtoks = [data.get(col.name, None) for col in self.columns.values()]
        if self.csvfmt:
            if self.csvwriter is not None:
                try:
                    self.csvwriter.writerow(wtoks)
                except Exception:
                    import traceback

                    traceback.print_exc()
        else:
            self.wf.write("\t".join(wtoks) + "\n")

    def close(self):
        self.wf.close()


class CrxMapping(object):
    def __init__(self):
        from re import compile
        from typing import Optional

        self.protein: Optional[str] = None
        self.achange = None
        self.transcript: Optional[str] = None
        self.tchange = None
        self.so: Optional[str] = None
        self.gene = None
        self.tref = None
        self.tpos_start = None
        self.talt = None
        self.aref = None
        self.apos_start = None
        self.aalt = None
        self.mapping = None
        self.tchange_re = compile(r"([AaTtCcGgUuNn_-]+)(\d+)([AaTtCcGgUuNn_-]+)")
        self.achange_re = compile(r"([a-zA-Z_\*]+)(\d+)([AaTtCcGgUuNn_\*]+)")

    def load_tchange(self, tchange):
        self.tchange = tchange
        if tchange is not None:
            self.parse_tchange()

    def parse_tchange(self):
        if self.tchange is not None:
            tchange_match = self.tchange_re.match(self.tchange)
            if tchange_match:
                self.tref = tchange_match.group(1)
                self.tpos_start = int(tchange_match.group(2))
                self.talt = tchange_match.group(3)

    def load_achange(self, achange):
        self.achange = achange
        if self.achange is not None:
            self.parse_achange()

    def parse_achange(self):
        if self.achange is not None:
            achange_match = self.achange_re.match(self.achange)
            if achange_match:
                self.aref = achange_match.group(1)
                self.apos_start = int(achange_match.group(2))
                self.aalt = achange_match.group(3)


class AllMappingsParser(object):
    def __init__(self, s):
        from json import loads
        from collections import OrderedDict

        if isinstance(s, str):
            self._d = loads(s, object_pairs_hook=OrderedDict)
        else:
            self._d = s
        self._transc_index = 0
        self._tchange_index = 5
        self._achange_index = 6
        self._so_index = 7
        self._protein_index = 8
        self.mappings = self.get_all_mappings()

    def get_genes(self):
        return list(self._d.keys())

    def get_uniq_sos(self):
        sos = {}
        for mapping in self.mappings:
            for so in mapping.so.split(","):
                sos[so] = True
        sos = list(sos.keys())
        return sos

    def none_to_empty(self, s):
        if s is None:
            return ""
        else:
            return s

    def get_mapping(self, t):
        mapping = CrxMapping()
        mapping.transcript = self.none_to_empty(t[self._transc_index])
        mapping.so = self.none_to_empty(t[self._so_index])
        mapping.load_tchange(self.none_to_empty(t[self._tchange_index]))
        mapping.load_achange(self.none_to_empty(t[self._achange_index]))
        mapping.protein = self.none_to_empty(t[self._protein_index])
        return mapping

    def get_all_mappings(self):
        mappings = []
        for gene, ts in self._d.items():
            for t in ts:
                mapping = self.get_mapping(t)
                mapping.gene = gene
                mappings.append(mapping)
        return mappings

    def get_transcript_mapping(self, transcript):
        for mapping in self.mappings:
            if mapping.transcript == transcript:
                return mapping
        return None


class ColumnDefinition(object):
    csv_order = [
        "index",
        "title",
        "name",
        "type",
        "categories",
        "width",
        "desc",
        "hidden",
        "category",
        "filterable",
        "hide_from_gui_filter",
        "link_format",
        "genesummary",
    ]

    db_order = [  # TODO change name to denote legacy
        "col_name",
        "col_title",
        "col_type",
        "col_cats",
        "col_width",
        "col_desc",
        "col_hidden",
        "col_ctg",
        "col_filterable",
        "col_hide_from_gui_filter",
        "col_link_format",
    ]

    sql_map = {
        "col_name": "name",
        "col_title": "title",
        "col_type": "type",
        "col_cats": "categories",
        "col_width": "width",
        "col_desc": "desc",
        "col_hidden": "hidden",
        "col_ctg": "category",
        "col_filterable": "filterable",
        "col_hide_from_gui_filter": "hide_from_gui_filter",
        "col_link_format": "link_format",
        "col_genesummary": "genesummary",
    }

    def __init__(self, d):
        from copy import deepcopy

        self.index: int = 0
        self.name: str = ""
        self.title = None
        self.type = None
        self.categories = None
        self.width = None
        self.desc = None
        self.hidden = False
        self.category = None
        self.filterable = None
        self.hide_from_gui_filter = None
        self.link_format = None
        self.genesummary = None
        self.table = None
        self.level = None
        self.d: Dict[str, Any] = deepcopy(d)
        self._load_dict(d)

    def _load_dict(self, d):
        self.d["index"] = d.get("index", None)
        self.d["name"] = d.get("name", None)
        self.d["title"] = d.get("title")
        self.d["type"] = d.get("type")
        self.d["categories"] = d.get("categories", [])
        self.d["width"] = d.get("width", None)
        self.d["desc"] = d.get("desc")
        self.d["hidden"] = d.get("hidden", False)
        self.d["category"] = d.get("category")
        self.d["filterable"] = bool(d.get("filterable", "True"))
        self.d["hide_from_gui_filter"] = d.get("hide_from_gui_filter", False)
        self.d["link_format"] = d.get("link_format")
        if "genesummary" in d:
            genesummary = d.get("genesummary")
            if genesummary is None:
                genesummary = False
            elif isinstance(genesummary, str):
                genesummary = bool(genesummary)
        else:
            genesummary = False
        self.d["genesummary"] = genesummary
        self.d["table"] = bool(d.get("table", "False"))
        self.d["level"] = d.get("level")
        self.index = d.get("index")
        self.name = d.get("name")
        self.title = d.get("title")
        self.type = d.get("type")
        self.categories = d.get("categories", [])
        self.width = d.get("width")
        self.desc = d.get("desc")
        self.hidden = d.get("hidden")
        self.category = d.get("category")
        self.filterable = bool(d.get("filterable", True))
        self.hide_from_gui_filter = d.get("hide_from_gui_filter")
        self.link_format = d.get("link_format")
        self.genesummary = self.d["genesummary"]
        self.table = d.get("table", False)
        self.level = d.get("level")
        self.fhir = d.get("fhir")

    def change_name(self, name: str):
        self.name = name
        self.d["name"] = name

    def from_row(self, row, order=None):
        from json import loads

        if order is None:
            order = self.db_order
        d = {self.sql_map[column]: value for column, value in zip(order, row)}
        self._load_dict(d)
        if isinstance(self.categories, str):
            self.categories = loads(self.categories)

    def from_var_csv(self, row):
        from json import loads
        from csv import reader

        if self.index is not None:
            row = list(reader([row], dialect="oakvar"))[0]
            self._load_dict(dict(zip(self.csv_order[: len(row)], row)))
            self.index = int(self.index)
            if isinstance(self.categories, str):
                self.categories = loads(self.categories)
            if self.categories is None:
                self.categories = []
            if isinstance(self.hidden, str):
                self.hidden = loads(self.hidden.lower())
            if isinstance(self.filterable, str):
                self.filterable = loads(self.filterable.lower())
            if isinstance(self.hide_from_gui_filter, str):
                self.hide_from_gui_filter = loads(self.hide_from_gui_filter.lower())
            if self.link_format == "":
                self.link_format = None

    def from_json(self, sjson):
        from json import loads
        from copy import deepcopy

        d = loads(sjson)
        self.d = deepcopy(d)
        self._load_dict(d)

    def get_json(self):
        from json import dumps

        return dumps(self.d)

    def get_colinfo(self):
        return {
            "col_name": self.name,
            "col_title": self.title,
            "col_type": self.type,
            "col_cats": self.categories,
            "col_width": self.width,
            "col_desc": self.desc,
            "col_hidden": self.hidden,
            "col_ctg": self.category,
            "col_filterable": self.filterable,
            "col_hide_from_gui_filter": self.hide_from_gui_filter,
            "link_format": self.link_format,
            "col_genesummary": self.genesummary,
            "col_index": self.index,
            "table": self.table,
            "level": self.level,
            "fhir": self.d.get("fhir"),
        }

    def __iter__(self):  # Allows casting to dict
        for k, v in self.__dict__.items():
            yield k, v


def read_crv(fpath):
    import polars as pl

    # Read the CSV using the comment character
    df = pl.read_csv(
        fpath,
        comment_prefix="#",  # type: ignore
        has_header=False,
        new_columns=["uid", "chrom", "pos", "pos_end", "ref_base", "alt_base"],
    )

    # Select only the first 6 columns to return
    df = df.select(["uid", "chrom", "pos", "pos_end", "ref_base", "alt_base"])

    return df


def get_file_content_as_table(fpath: Union[Path, str], title: str, outer=None):
    from rich.table import Table

    if not outer:
        return
    table = Table(title=title, show_header=False)
    table.add_column("License")
    with open(fpath) as f:
        lines = "".join(f.readlines())
        table.add_row(lines)
    if hasattr(outer, "print"):
        outer.print(table)
    else:
        outer.write(table)


CravatReader = FileReader
CravatWriter = FileWriter
