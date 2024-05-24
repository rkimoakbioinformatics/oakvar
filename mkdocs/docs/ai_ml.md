**This page will be updated with more content in the future.**

One of OakVar's main aims is easy integration of genomic variant analysis results with AI/ML frameworks.

The first step toward that goal is the conversion of analysis results into DataFrames.

OakVar provides the following method to convert the analysis results in SQLite tables into [Polars](https://docs.pola.rs/py-polars/html/reference/) DataFrame.

    import oakvar as ov
    df = ov.get_df_from_db("oakvar_example.vcf.sqlite")

This will load the content of `variant` table into `df` as a Polars DataFrame.

If you want to use Pandas DataFrame instead, 

    df.to_pandas(use_pyarrow_extension_array = True)

will produce a Pandas version of the same DataFrame.

Back to `get_df_from_db` method, you can specify which table to load and a SQL expression for filtering the content.

    df = ov.get_df_from_db(
        "oakvar_example.vcf.sqlite", table_name="sample"
    )

will load the `sample` table into `df` as a DataFrame.

    df = ov.get_df_from_db(
        "oakvar_example.vcf.sqlite", 
        table_name="variant", 
        sql="base__so='MIS' and clinvar__sig like '%Pathogenic%'"
    )

will load the `variant` table, but with the filter for the variants whose consequence is missense and whose ClinVar clinical significance include `Pathogenic`.


