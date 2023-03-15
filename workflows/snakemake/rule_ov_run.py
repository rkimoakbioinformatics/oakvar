rule run_ov:
    input:
        "exampleinput"
        
    params:
        annotator = ["clinvar", "cosmic"],
        reporter = ["vcf", "excel"]

    shell:
        "python wrapper.py {input} --annotator {params.annotator} --reporter {params.reporter}"

