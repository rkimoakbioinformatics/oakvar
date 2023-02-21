OV_STORE_EMAIL_KEY = "ov_store_email"
OV_STORE_PW_KEY = "ov_store_pw"
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
    "min_pkg_ver",  # Minimum OakVar packgae version for a module
]
logo_size = (275, 170)
MODULE_PACK_SPLIT_FILE_SIZE = 100 * 1024 * 1024
pack_ignore_fnames = [".DS_Store", "__pycache__"]
store_url_key = "store_url"
