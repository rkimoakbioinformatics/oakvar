cwlVersion: v1.2
class: CommandLineTool
baseCommand: ov
requirements:
  EnvVarRequirement:
    envDef:
      HOME: $(inputs.home)
      TMPDIR: $(inputs.tmp)
arguments:
  - valueFrom: system
  - valueFrom: setup
  - valueFrom: $(inputs.setup_yaml)
    prefix: -f
  - valueFrom: $(inputs.mail)
    prefix: --email
  - valueFrom: $(inputs.password)
    prefix: --pw
inputs:
  setup_yaml:
    type: File?
  home: string
  tmp: string
  mail:
    type: string?
  password:
    type: string?
outputs: []