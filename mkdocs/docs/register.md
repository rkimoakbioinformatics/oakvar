You can publish your OakVar modules to the OakVar store with OakVar command-line interface. For example, let's say you made an awesome OakVar annotation module named `awesome` and wants to share it with the world. You can do this in three steps. 

    ov module pack awesome

This will create one or two files, depending whether your module has data folder in it or not. Your module's code will be packed into `awesome__<version>__code.zip` where `version` is the version number defined in `awesome.yml` file in your module's directory, and if your module has `data` subdirectory, `awesome__<version>__data.zip` also will be created.

Then, upload these zip files to somewhere people can download. Using their URLs,

    ov store register awesome --code-url ... --data-url ...

will register your module in the OakVar store. `--data-url` is needed only if your module produced a data zip file.

This way, you have total control of your module's publication. You can just delete the module zip files from where you stored them and OakVar store will automatically deregister those deleted versions. If you move the module zip files to new locations you can just register them again with new URLs.
