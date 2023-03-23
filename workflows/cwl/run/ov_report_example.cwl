cwlVersion: v1.2
class: CommandLineTool

baseCommand: ov

arguments: 
  - valueFrom: $(inputs.sqlite_file)
    prefix: report
  - valueFrom: excel
    prefix: -t
requirements:
  InitialWorkDirRequirement:
    listing:
      - $(inputs.sqlite_file)
  EnvVarRequirement:
    envDef:
      TMP: $(inputs.tmp_directory)
      HOME: $(inputs.home_directory) 
  InitialWorkDirRequirement: {}
inputs: 
  sqlite_file:
    type: File
  home_directory: string
  tmp_directory: string
outputs:
  excel_file:
    type: File
    outputBinding:
      glob: $(inputs.sqlite_file)