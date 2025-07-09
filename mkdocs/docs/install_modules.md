## Installing OakVar Modules through OakVar Store

The OakVar Store is where OakVar's modules are registered, found, and distributed. If you used OpenCRAVAT, OpenCRAVAT's modules are also available through OakVar Store if there is no updated OakVar version of the same module exists. To know which modules are available through the OakVar Store, do

```
ov module ls -a
```

This will list the OakVar modules available through the OakVar Store. To know more details of a specific module, do

```
ov module info module_name # module_name such as clinvar
```

To install modules, do

```
ov module install module_name [module_name] ...
```

A regular expression can be given as *module_name*. Thus, 

```
ov module install clin.*
```

will install all modules the name of which starts with `clin`.

## Installing through GitHub

OakVar can install custom modules directly from GitHub. It is as easy as simply giving the module's name and the URL of the folder of the module on GitHub to `ov module install`. Let's say you have a custom module hosted on the `dev` branch of your GitHub repo `yourorganization/yourrepo` in the following folder:

```
https://github.com/yourorganization/yourrepo/
    oakvar_modules/
        annotators/
            awesomeannotator/
                awssomeannotator.py
                awssomeannotator.yml
                awssomeannotator.md
                data/
                    awesomeannotator.sqlite
```

Your colleagues can install `awesomeannotator` module with the following command.

```
ov module install awesomeannotator \
 https://github.com/yourorganization/yourrepo/\
 tree/dev/oakvar_modules/annotators/awssomeannotator
```

will download the content of only the `awesomeannotator` folder in the `dev` branch of the repository, figure out that the module is an `annotator`, and put the `awesomeannotator` module under the appropriate `annotators` category folder inside your system's OakVar modules root directory.

This way, your custom module under development can be easily shared with your colleagues.

It is important to give the module's name as a separate argument and also to use a full GitHub tree URL, which has `/tree/<branch name>`, to the module's folder. If the module files are hosted at the root folder of a repository, the tree URL should end with `/tree/<branch name>`.

