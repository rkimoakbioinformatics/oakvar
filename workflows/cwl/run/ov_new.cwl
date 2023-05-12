cwlVersion: v1.2
class: CommandLineTool

baseCommand: ov
arguments: 
  - valueFrom: $(inputs.ex_file)
    prefix: new
requirements:
  EnvVarRequirement:
    envDef:
      TMP: $(inputs.tmp_directory)
      HOME: $(inputs.home_directory) 
inputs:
  ex_file:
    type: string
    default: exampleinput
  home_directory: string
  tmp_directory: string
outputs:
  exampleInput: 
    type: File[]
    outputBinding:
      glob: '*'