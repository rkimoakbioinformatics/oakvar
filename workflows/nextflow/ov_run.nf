params.module = ""
params.outputdir = ""
//Generate input file
process examplefile{
    publishDir '/mnt/d/Bioinformatics/OakVar/oakvar/workflows/nextflow', mode: 'copy'
    script:
    """
    ov new exampleinput
    """
    output:
    path 'exampleinput'
}
//optional module process to install a module
process install_module{
    input:
    val module

    script:
    """
    ov module install -y $module
    """
}
//task for ov run
process ov_run{
    stageInMode 'copy'
    publishDir params.outputdir , mode: 'copy'
    input:
    path example_file

    script:
    """
    ov run $example_file -t vcf 
    """
    output:
    path "${example_file}.sqlite"
    path "${example_file}.vcf"
}
//task for ov report
process ov_report{
    stageInMode 'copy'
    publishDir params.outputdir , mode: 'copy'
    input:
    path sqlite_file
    script:
    file_name = sqlite_file.getSimpleName()
    """
    ov report $sqlite_file -t text
    """
    output:
    path "${file_name}.tsv"
}

workflow{
    examplefile()
    (sqlite_file, vcf_file) = ov_run(examplefile.out)
    sqlite_file.view {"$it.name"}
    ov_report(sqlite_file)
    //if you wish to install an oakvar module , uncomment the following line of code
    //install_module(params.module)

}