# API Main

OakVar functionality is available through Python API. For example, OakVar's annotation pipeline can be started with the following:

    >>> import oakvar as ov
    >>> ov.api.run(inputs=["input.vcf"], annotators=["clinvar"], report_types=["vcf"])

There is 1 to 1 correspondence between command-line interface commands and Python API functions. The table below shows such correspondence.

CLI | Python API | Functionality
----|------------|--------------
ov config system | [oakvar.api.config.system](/api/config/#oakvar.api.config.system) | Gets or sets system configuration.
ov config user | [oakvar.api.config.user](/api/config/#oakvar.api.config.user) | Gets user configuration.
ov issue | [oakvar.api.report_issues](/api/oakvar_api/#oakvar.api.report_issue) | Opens a webpage to report OakVar issues.
ov license | [oakvar.api.license](/api/oakvar_api/#oakvar.api.license) | Gets the OakVar license information.
ov module info | [oakvar.api.module.info](/api/module/#oakvar.api.module.info) | Gets information on a module.
ov module install | [oakvar.api.module.install](/api/module/#oakvar.api.module.install) | Installs modules.
ov module installbase | [oakvar.api.module.installbase](/api/module/#oakvar.api.module.installbase) | Installs system modules.
ov module ls | [oakvar.api.module.ls](/api/module/#oakvar.api.module.ls) | Lists modules.
ov module pack | [oakvar.api.module.pack](/api/module/#oakvar.api.module.pack) | Packs a module for registration at OakVar store.
ov module uninstall | [oakvar.api.module.uninstall](/api/module/#oakvar.api.module.uninstall) | Uninstalls modules.
ov module update | [oakvar.api.module.update](/api/module/#oakvar.api.module.update) | Updates modules.
ov new exampleinput | [oakvar.api.new.exampleinput](/api/new/#oakvar.api.new.exampleinput) | Creates an example input file.
ov new module | [oakvar.api.new.module](/api/new/#oakvar.api.new.module) | Creates a template for a new module.
ov report | [oakvar.api.report](/api/oakvar_api/#oakvar.api.report) | Generates report files from OakVar result databases.
ov run | [oakvar.api.run](/api/oakvar_api#oakvar.api.run) | Runs the OakVar annotation pipeline.
ov store delete | [oakvar.api.store.delete](/api/store/#oakvar.api.store.delete) | Deletes a module from the OakVar store.
ov store fetch | [oakvar.api.store.fetch](/api/store/#oakvar.api.store.fetch) | Fetches the OakVar store cache.
ov store login | [oakvar.api.store.login](/api/store/#oakvar.api.store.login) | Logs in to the OakVar store.
ov store logout | [oakvar.api.store.logout](/api/store/#oakvar.api.store.logout) | Logs out from the OakVar store.
ov store register | [oakvar.api.store.register](/api/store/#oakvar.api.store.register) | Register a module at the OakVar store.
ov store url | [oakvar.api.store.url](/api/store/#oakvar.api.store.url) | Gets the URL of the OakVar store.
ov store account change | [oakvar.api.store.account.change](/api/store_account/#oakvar.api.store.account.change) | Changes the password of an OakVar store account.
ov store account check | [oakvar.api.store.account.check](/api/store_account/#oakvar.api.store.account.check) | Checks if logged in at the OakVar store.
ov store account create | [oakvar.api.store.account.create](/api/store_account/#oakvar.api.store.account.create) | Creats an OakVar store account.
ov store account delete | [oakvar.api.store.account.delete](/api/store_account/#oakvar.api.store.account.delete) | Deletes an OakVar store account.
ov store account reset | [oakvar.api.store.account.reset](/api/store_account/#oakvar.api.store.account.reset) | Invokes a password change email for an OakVar store account.
ov system account check | [oakvar.api.system.check](/api/system/#oakvar.api.system.check) | Checks OakVar installation on the system.
ov system md | [oakvar.api.system.md](/api/system/#oakvar.api.system.md) | Gets or sets the OakVar modules directory.
ov system setup | [oakvar.api.system.setup](/api/system/#oakvar.api.system.setup) | Sets up OakVar in the system.
ov update | [oakvar.api.update](/api/oakvar_api/#oakvar.api.update) | Gets OakVar version.
ov version | [oakvar.api.version](/api/oakvar_api/#oakvar.api.version) | Gets OakVar version.

OakVar Python API has a utility function to help data science with genomic data. If an OakVar analysis produced `ov_result.sqlite` result database file, the following will produce a Polars DataFrame from `variant` level data of the result database.

    >>> import oakvar as ov
    >>> df = ov.get_df_from_db("ov_result.sqlite", table="variant")

