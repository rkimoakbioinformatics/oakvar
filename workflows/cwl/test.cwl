cwlVersion: v1.2
class: CommandLineTool
baseCommand: [ ov ]

inputs:
  cmd:
    type: string
    inputBinding:
      position: 1
  message:
    type: File
    inputBinding:
      position: 2

outputs:
  out:
    type: File
    outputBinding:
      glob: '*'

