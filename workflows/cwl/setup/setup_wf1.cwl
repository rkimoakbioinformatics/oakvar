cwlVersion: v1.2
class: Workflow

requirements:
  InitialWorkDirRequirement:
    listing:
      - $(inputs.modules_path)
inputs:
  home_dir: string
  tmp_dir: string
  modules_path: string
  email: string
  pw: string
outputs: []

steps:
#install oakvar using pip
  pip_install:
    run:
      class: CommandLineTool
      baseCommand: pip
      arguments:
        - valueFrom: install
        - valueFrom: oakvar
      inputs: []
      outputs: []
    in: []
    out: []
#Make setup.yaml file
  make_yamlFile:
    #Import makefile cwl script that outputs yaml file
    run: make_file.cwl
    in:
       modules_dir: modules_path
    out: [yaml_file]
#Setup oakvar
  ov_setup:
    run: ovSystem.cwl
    in: 
      home: home_dir
      tmp: tmp_dir      
      mail: email
      password: pw 
    out: []
      
