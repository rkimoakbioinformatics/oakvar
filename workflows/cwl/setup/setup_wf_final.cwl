cwlVersion: v1.2
#Class of current cwl script
class: Workflow
#provide inline java script requirement to add some javascript
requirements:
  InlineJavascriptRequirement: {}
inputs:
  home_dir: string
  tmp_dir: string
  modules_path: string?
  email: string
  pw: string
outputs: []
#specify workflow steps
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
    #condition when to run the yaml file 
    in:
       modules_dir: modules_path
    when: $(inputs.modules_path == "a_string" || inputs.modules_path == "")
    out: [yaml_file]
#Setup oakvar
  ov_setup:
    run: ovSystem.cwl
    in:
      home: home_dir
      tmp: tmp_dir
      mail: email
      password: pw
      setup_yaml: make_yamlFile/yaml_file
    out: []