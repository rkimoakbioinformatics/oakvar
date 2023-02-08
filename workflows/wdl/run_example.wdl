workflow OakVarExample{
    call Install_module
    call GenerateExample
    call annotation { input: inputFile = GenerateExample.example_out }
    call excel_file { input: sqlite = annotation.annotation_sqlite }
}
#Install module required for variant calling
task Install_module{
    #Install annotation module (use -y flag for automated yes answer for installation) 
    command {
        ov module install -y clinvar
    }
    output {
        File install_out = stdout()
    }
}
#use built-in example
task GenerateExample{
    command {
        ov new exampleinput
    }
    output {
        File example_out = "exampleinput"
    }
}

#Run annotation job 
task annotation {
    File inputFile
    #Get input file from the generate example task
    #run VC on example 
    command{
        #export TMPDIR=/tmp
        ov run ${inputFile} -a clinvar -t vcf -d .
    }
    output{
	File out = stdout()
        File annotation_vcf = "exampleinput.vcf"
        File annotation_sqlite = "exampleinput.sqlite"
    }
}

task excel_file{
    #Initialize sql file variable
    File sqlite
    #get excel report of annotated variants
    command {
        ov report ${sqlite} -t excel -s annotated
    }
    output{
        File excel_output = "annotated.xlsx"
    }
}
