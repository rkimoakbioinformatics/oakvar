# Registering OakVar Modules on OakVar Store

You can publish your OakVar modules to the OakVar store with OakVar command-line interface. For example, let's say you made an awesome OakVar annotation module named `awesome` and wants to share it with the world. You can do this in three steps. 

    ov module pack awesome

This will create one or two files, depending whether your module has data folder in it or not. Your module's code will be packed into `awesome__<version>__code.zip` where `version` is the version number defined in `awesome.yml` file in your module's directory, and if your module has `data` subdirectory, `awesome__<version>__data.zip` also will be created.

If your module is bigger than 1GB, `--split` option can be given. This will split the code and the data of your module into zip part files of 1GB each. For example, if `awesome` module is 2.5GB big and most of the size is from its data, 

    ov module pack awesome --split

will produce the following files.

    awesome__1.0.0__code.zip000
    awesome__1.0.0__data.zip000
    awesome__1.0.0__data.zip001
    awesome__1.0.0__data.zip002

Then, upload these zip files to somewhere people can download. Using their URLs,

    ov store register awesome --code-url ... --data-url ...

will register your module in the OakVar store. `--data-url` is needed only if your module produced a data zip file. If you have many split zip files, `-f` option can be given with a YAML format file with code and data URLs. For example, 

    ov store register awesome -f urls.txt

with `urls.txt` of the following content

    code_url:
    - https://dropbox.com/xxxxxxxx/awesome__1.0.0__code.zip000
    data_url:
    - https://dropbox.com/xxxxxxxx/awesome__1.0.0__data.zip000
    - https://dropbox.com/xxxxxxxx/awesome__1.0.0__data.zip001
    - https://dropbox.com/xxxxxxxx/awesome__1.0.0__data.zip002

will register the module.

This way, you have total control of your module's publication. You can just delete the module zip files from where you stored them and OakVar store will automatically deregister those deleted versions. If you move the module zip files to new locations you can just register them again with new URLs.
