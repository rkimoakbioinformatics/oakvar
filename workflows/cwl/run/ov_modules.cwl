cwlVersion: v1.2
class: CommandLineTool

baseCommand: ov

arguments:
  - valueFrom: module
  - valueFrom: module_name
    prefix: install
  - valueFrom: module_update
    prefix: update
  - valueFrom: -y
inputs:
  module_name:
    type: string?
  update_module:
    type: string?

outputs: []