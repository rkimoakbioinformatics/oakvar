cwlVersion: v1.2
class: Workflow
inputs:
# home directory
  home_dir: string
#provide tmp directory 
  tmp_dir: string
#provide user's email
  email: string
#provide user's pw
  pw: string
outputs: []
steps:
#install oakvar using pip
  pip_install:
    run:
      class: CommandLineTool
      #bash command tool
      baseCommand: pip
      arguments:
        - valueFrom: install
        - valueFrom: oakvar
      inputs: []
      outputs: []
    in: []
    out: []
#Setup oakvar
  ov_setup:
    run: ovSystem.cwl
    in:
      home: home_dir
      tmp: tmp_dir
      mail: email
      password: pw
    out: []
