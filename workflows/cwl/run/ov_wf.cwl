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
  module: string? 
outputs:
  example_file:
    type: File
    outputSource: ov_new/exampleInput
  vcf_file:
     type: File
     outputSource: ov_run/vcf
  file_sqlite:
     type: File
     outputSource: ov_run/sqlite
  file_anno:
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
  ov_run:
    run: ov_run.cwl
    in:
      vcf_file: ov_new/exampleInput
      home: home_dir
      tmp: tmp_dir
    out: [sqlite, vcf]
  ov_report:
    run: ov_report.cwl
    in: 
      sqlite_file: ov_run/sqlite
      home: home_dir
      tmp: tmp_dir
    out: [excel_file]
    