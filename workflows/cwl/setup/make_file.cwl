cwlVersion: v1.2
#Class of cwl script
class: CommandLineTool
#base bash command
baseCommand: echo

arguments:
# echoing modules_dir: 
  - valueFrom: $(inputs.modules_pre)
#echoing user's desired input
  - valueFrom: $(inputs.modules_dir)

inputs:
  modules_pre:
    type: string
    default: "modules_dir: "
  modules_dir:
    type: string?

outputs:
  yaml_file:
    type: stdout
#stdout as yaml file
stdout: setup.yaml

