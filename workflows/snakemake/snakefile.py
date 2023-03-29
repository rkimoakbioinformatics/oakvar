rule run_ov:
    input:
        "exampleinput"

    output:
        "exampleinput.xlsx",
        "exampleinput.vcf"
        
    params:
        annotator = ["clinvar", "cosmic"],
        reporter = ["vcf", "excel"]

    shell:
        "ov run {input} -a {params.annotator} -t {params.reporter}"
