cwlVersion: v1.2
class: Workflow

requirements:
  InlineJavascriptRequirement: {}
  EnvVarRequirement:
    envDef:
      HOME: $(inputs.home)
      TMP: $(inputs.tmp)

inputs: 
  home_dir: string
  tmp_dir: string
  module: string[]? 
  module_run:
    type: string?
outputs:
  example_file:
    type: File[]
    outputSource: ov_new/exampleInput
  vcf_file:
     type: File[]
     outputSource: ov_run_example/output_files
  file_sqlite:
     type: File
     outputSource: ov_run_example/sqlite
  file_report:
     type: File
     outputSource: ov_report/excel_file

steps:
  ov_new:
    run: ov_new.cwl
    in: 
      home: home_dir
      tmp: tmp_dir
    out: [exampleInput]

  ov_module:
    run: ov_modules.cwl
    in: 
      module_name: module
      home: home_dir
      tmp: tmp_dir
    when: $(inputs.module_name != "a_string")
    out: []
  ov_run_example:
    run: ov_run_example.cwl
    in:
      input_files: ov_new/exampleInput
      home: home_dir
      tmp: tmp_dir
      module_name: module_run
    out: [sqlite, output_files]
  ov_report:
    run: ov_report_example.cwl
    in: 
      sqlite_file: ov_run_example/sqlite
      home: home_dir
      tmp: tmp_dir
    out: [excel_file]