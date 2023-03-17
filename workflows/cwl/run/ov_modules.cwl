cwlVersion: v1.2
class: CommandLineTool

baseCommand: ov

arguments:
  - valueFrom: module
  - valueFrom: $(inputs.module_name)
    prefix: install
  - valueFrom: -y
requirements:
  EnvVarRequirement:
    envDef:
      HOME: $(inputs.home)
      TMP: $(inputs.tmp)

inputs:
  module_name:
    type: string[]?
    default:
      - a_string 
  home: string
  tmp: string
outputs: []