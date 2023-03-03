cwlVersion: v1.2
class: CommandLineTool

baseCommand: ov
arguments: 
  - valueFrom: $(inputs.ex_file)
    prefix: new

inputs:
  ex_file:
    type: string
outputs:
  example: 
    type: File
    outputBinding:
      glob: '*'