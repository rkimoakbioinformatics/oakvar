
#Work flow of Oakvar setup
workflow SetupOakVar{
    String email
    String pw
    call pip
    call yaml_file
    call ov { input: setup = yaml_file.yaml_output ,id = email, password = pw
    }

}

task pip{
    command{
        pip install oakvar
    }
    output{
        File pip_output = stdout()
    }
}
task yaml_file{
    #write yaml file 
    command{
        echo "---" > setup.yaml && echo "modules_dir: ~/oakvar_modules" >> setup.yaml  && echo "log_dir: ~/oakvar_logs" >> setup.yaml 
    }
    #output the value of stdoutput 
    output{
        File yaml_output = "setup.yaml"
    }
}

task ov{
    #input is the output yaml file from yaml_file task
    File setup
    String id
    String password

    #Setup withh yaml file
    command{
        ov system setup -f ${setup} --email ${id} --pw ${password}
    }
    output{
        File ov_output = stdout()
    }
}