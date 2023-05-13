cwlVersion: v1.2
class: CommandLineTool
requirements:
  InlineJavascriptRequirement:
    expressionLib:
      - |
        ${ include }
        function getTmpDir(dir) {
          if (dir) {
            return dir;
          } else {
            return ".";
          }
        }
        function getHomeDir(dir) {
          if (dir) {
            return dir;
          } else {
            return ".";
          }
        }
        function getModulesDir(dir) {
          if (dir) {
            return dir;
          } else {
            var fs = require("fs");
            var YAML = require("js-yaml");
            var doc = YAML.load(fs.readFileSync(`{inputs.root_dir}/conf/system.yml` , 'utf8'));
            var moules_dir = doc["modules_dir"];
            return modules_dir;
          }
        }
  InitialWorkDirRequirement:
    listing:
      - $(inputs.input_files)
  EnvVarRequirement:
    envDef:
      TMP: $(getTmpDir(inputs.tmp_dir))
      HOME: $(getHomeDir(inputs.home_dir))
      OV_ROOT_DIR: $(inputs.root_dir)
      OV_MODULES_DIR: $(getModulesDir(inputs.modules_dir))

baseCommand: [ov, run]

arguments:
  - valueFrom: $(inputs.input_files)
  - valueFrom: $(inputs.module_name)
    prefix: -a
  - valueFrom: vcf
    prefix: -t

inputs:
  input_files:
    type: File[]
  tmp_dir:
    type: string?
  home_dir:
    type: string?
  root_dir:
    type: string
  modules_dir:
    type: string?
  module_name: 
    type: string?

outputs:
  sqlite_out:
    type: File[]
    outputBinding:
      outputEval: |        
        ${ var inputFiles = [].concat(inputs.input_files);
          var outputFiles = [];
        for (var i = 0; i < inputFiles.length ; i++){
          var fileName = inputFiles[i].basename;
          var outFile = fileName.concat(".sqlite");
          outputFiles.push({ class: "File", path: outFile })
        }
        return outputFiles;}

 
  vcf_out:
    type: File[]
    outputBinding:
      outputEval: | 
        ${ var inputFiles = [].concat(inputs.input_files);
          var outputFiles = [];
        for (var i = 0; i < inputFiles.length ; i++){
          var fileName = inputFiles[i].basename;
          var outFile = fileName.concat(".vcf");
          outputFiles.push({ class: "File", path: outFile })
        }
        return outputFiles;}
