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
  - valueFrom: vcf
    prefix: -t


inputs:
  vcf_file:
    type: File
  tmp:
    type: string
  home:
    type: string
outputs:
  out_file:
    type: 
      type: array
      items: File
    outputBinding:
      glob: '*'
