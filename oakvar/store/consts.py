oc_store_url = "https://store.opencravat.org"
oc_publish_url = "https://publish.opencravat.org"
oc_store_module_url = oc_store_url + "/modules"
oc_manifest_url = oc_store_url + "/manifest.yml"
oc_manifest_fn = "oc_manifest.yml"
ov_store_email_key = "ov_store_email"
ov_store_pw_key = "ov_store_pw"
ov_store_cache_fn = "store.sqlite"
ov_store_last_updated_col = "last_updated"
ov_store_id_token_fname = ".token"
summary_table_cols = ["name", "store", "title", "type", "tags", "email", "publish_time"]
versions_table_cols = [
    "name",
    "store",
    "code_version",
    "data_version",
    "data_source",
    "code_size",
    "data_size",
    "publish_time",
]
logo_size = (275, 170)
ov_store_split_file_size = 1_000_000_000 # 1 GB parts
#ov_store_split_file_size = 100_000_000 # 100 MB parts
pack_ignore_fnames = [
    ".DS_Store",
    "__pycache__"
]
