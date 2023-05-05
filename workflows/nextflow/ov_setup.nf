params.email = ""
params.pw = ""

process ov_setup{
    input:
    debug true
    val email
    val pw
    script:
    if(params.email != '' && params.pw != '')
        """
        pip install oakvar
        ov system setup --email $email --pw $pw
        """
    else
        """
        echo "Please enter email and pw values in the nextflow script or as Command Line arguments for example:\n nextflow run ov_setup.nf --email yourmail@doman.com --pw yourpw"
        """
    output:
    stdout
}

workflow {
    ov_setup(params.email,params.pw)
}
