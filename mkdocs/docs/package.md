#### Annotate with a ov run configuration file

For repeated jobs, using a .yml file with job definition is handy.

For example, consider the following `ov run` job:

    ov run input.vcf -a clinvar cosmic dbsnp -t csv

The configuration of this job can be written in ovdef.yml file as follows:

    annotators: 
    - clinvar
    - cosmic
    - dbsnp
    report_types: csv

Then, this file can be used as follows.

    ov run input.vcf -c ovdef.yml

which will work in the same way as the first `ov run` command.

Below are the correspondence between `ov run` options and the fields in package .yml files.

| ov run option | type | package file (.yml) option |
|---------------|------|----------------------------|
| -a | list | annotators |
| -p | list | postaggregators |
| -t | list | report\_types |
| -n | string | run\_name |
| -d | string | output\_dir |
| --clean | bool | clean |
| --genome | string | genome |
| -i | string | input\_format |
| --startat | string | startat |
| --endat | string | endat |
| --skip | list | skip |
| --keep-temp | bool | keep\_temp |
| --mp | integer | mp |
| --primary-transcript | string | primary\_transcript |
| --module-options | dict | module\_options |
| --vcf2vcf | bool | vcf2vcf |
| --logtofile | bool | logtofile |
| --ignore-sample | bool | ignore\_sample |

