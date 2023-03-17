cwlVersion: v1.2
class: CommandLineTool

baseCommand: ov
arguments: 
  - valueFrom: $(inputs.ex_file)
    prefix: new
requirements:
  EnvVarRequirement:
    envDef:
      TMP: $(inputs.tmp)
      HOME: $(inputs.home) 
inputs:
  ex_file:
    type: string
    default: exampleinput
  home: string
  tmp: string
outputs:
  exampleInput: 
    type: File[]
    outputBinding:
      glob: '*'