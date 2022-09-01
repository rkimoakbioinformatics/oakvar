There are a few workflows of using OakVar modules.

    ov run
    ov report
    ov gui

As mentioned, there are three workflows of using modules in OakVar.

    ov run
    ov report
    ov gui

#### ov run

When `ov run` is called, OakVar imports and executes modules in the following manner.

    input
    | recognizes input files' format with
    | converter modules' check_format function
    v
    converter module's convert_line function
    v
    mapper module's map function
    | imports annotator modules according to
    | -a option
    v
    annotator modules' annotate function
    | import postaggregator modules according to
    | -p option as well as default postaggregator
    | modules
    v
    postaggregator modules' annotate function
    | import reporter modules according to
    | -t option
    v
    reporter modules' write_preface, write_header, write_table_row functions
    |
    v
    report files

#### ov report

When `ov report` is called, OakVar imports and executes modules in the following manner.

    annotation database file
    | import reporter modules accorging to
    | -t option
    v
    reporter modules' write_preface, write_header, write_table_row functions
    |
    v
    report files

#### ov gui

Will be discussed later.

