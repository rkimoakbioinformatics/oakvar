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
      HOME: $(inputs.home_directory)
      TMP: $(inputs.tmp_directory)

inputs:
  module_name:
    type: string[]?
    default:
      - a_string 
  home_directory: string
  tmp_directory: string
outputs: []