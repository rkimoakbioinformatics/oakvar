cwlVersion: v1.2
class: CommandLineTool
requirements:
  InitialWorkDirRequirement:
    listing:
      - $(inputs.vcf_file)
  EnvVarRequirement:
    envDef:
      TMP: $(inputs.tmp)
      HOME: $(inputs.home) 
baseCommand: ov

arguments:
  - valueFrom: $(inputs.vcf_file)
    prefix: run
  - valueFrom: $(inputs.module_name)
    prefix: -a
  - valueFrom: vcf
    prefix: -t


inputs:
  vcf_file:
    type: File
  tmp:
    type: string
  home:
    type: string
  module_name: 
    type: string?
outputs:
  sqlite:
    type: File
    outputBinding:
      glob: "*.sqlite"
  
  vcf:
    type: File
    outputBinding:
      glob: "*.vcf"