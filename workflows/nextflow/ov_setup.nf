params.email = ""
params.pw = ""

process ov_setup{
    input:
    debug true
    val email
    val pw
    script:
    """
    pip install oakvar
    ov system setup --email $email --pw $pw
    """
    output:
    stdout
}

workflow {
    ov_setup(params.email,params.pw)
}
