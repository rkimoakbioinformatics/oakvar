cwlVersion: v1.2
class: CommandLineTool

baseCommand: ov

arguments:
  - valueFrom: module
  - valueFrom: module_name
    prefix: install
  - valueFrom: -y
inputs:
  module_name:
    type: string?

outputs: []