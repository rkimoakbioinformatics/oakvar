
#Work flow of Oakvar setup
workflow SetupOakVar{
    String email
    String pw
    String? modules_dir
    call pip
    call yaml_file { input: m_dir = modules_dir }
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
    String? m_dir
    command{
        echo "---" > setup.yaml && echo "${m_dir}" >> setup.yaml   
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