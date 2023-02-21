cwlVersion: v1.2
class: CommandLineTool
baseCommand: [ ov, run ]

inputs:
  message:
    type: string
    default: exampleinput

outputs:
  out:
    type: File
    outputBinding:
      glob: '*'

