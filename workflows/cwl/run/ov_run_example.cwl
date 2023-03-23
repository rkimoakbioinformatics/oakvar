cwlVersion: v1.2
class: CommandLineTool
requirements:
  InlineJavascriptRequirement: {}
  InitialWorkDirRequirement:
    listing:
      - $(inputs.input_files)
  EnvVarRequirement:
    envDef:
      TMP: $(inputs.tmp_directory)
      HOME: $(inputs.home_directory) 
baseCommand: ov

arguments:
  - valueFrom: $(inputs.input_files)
    prefix: run
  - valueFrom: $(inputs.module_name)
    prefix: -a
  - valueFrom: vcf
    prefix: -t


inputs:
  input_files:
    type: File[]
  tmp_directory:
    type: string
  home_directory:
    type: string
  module_name: 
    type: string?
outputs:
  sqlite:
    type: File[]
    outputBinding:
      glob: $(inputs.input_files + ".sqlite")
  
  output_files:
    type:
      type: array
      items: File
    outputBinding:
      glob: "*"