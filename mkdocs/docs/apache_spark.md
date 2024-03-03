OakVar is natively integrated with Apache Spark, allowing annotation on the big genome project scale.

Let's see how it is done.

First, create a Spark session.

```python
import pyspark
from pyspark.sql import SparkSession

conf = pyspark.SparkConf().setAppName("ov")
sc = pyspark.SparkContext(conf=conf)
spark = SparkSession(sc)
```

Then, let's make a test set of variants as a Spark DataFrame.

```python
data = [
        {"chrom": "chr7", "pos":140734758, "ref_base": "T", "alt_base": "C"},
        {"chrom": "chr7", "pos":140734780, "ref_base": "-", "alt_base": "G"},
        {"chrom": "chr7", "pos":140736487, "ref_base": "GTGCGA", "alt_base": "-"},
        {"chrom": "chr7", "pos":140736487, "ref_base": "GTGCGAT", "alt_base": "-"},
        {"chrom": "chr7", "pos":140742186, "ref_base": "-", "alt_base": "T"},
        {"chrom": "chr7", "pos":140753351, "ref_base": "A", "alt_base": "G"},
        {"chrom": "chr7", "pos":140800417, "ref_base": "CT", "alt_base": "-"},
        {"chrom": "chr7", "pos":140800417, "ref_base": "CTG", "alt_base": "-"},
        {"chrom": "chr7", "pos":140807936, "ref_base": "A", "alt_base": "-"},
        {"chrom": "chr7", "pos":140924703, "ref_base": "A", "alt_base": "T"},
        {"chrom": "chr7", "pos":148847298, "ref_base": "A", "alt_base": "T"},
        {"chrom": "chr7", "pos":27199497, "ref_base": "C", "alt_base": "G"},
        {"chrom": "chr7", "pos":2958506, "ref_base": "A", "alt_base": "T"},
        {"chrom": "chr7", "pos":50319062, "ref_base": "A", "alt_base": "T"},
        {"chrom": "chr7", "pos":55019278, "ref_base": "A", "alt_base": "T"},
        {"chrom": "chr7", "pos":55019338, "ref_base": "G", "alt_base": "A"},
        {"chrom": "chr7", "pos":55181319, "ref_base": "-", "alt_base": "GGGTTG"},
        {"chrom": "chr8", "pos":127738263, "ref_base": "A", "alt_base": "T"},
        {"chrom": "chr8", "pos":43018497, "ref_base": "A", "alt_base": "G"},
        {"chrom": "chr9", "pos":107489172, "ref_base": "A", "alt_base": "T"},
        {"chrom": "chr9", "pos":130714320, "ref_base": "A", "alt_base": "T"},
        {"chrom": "chr9", "pos":132928872, "ref_base": "A", "alt_base": "T"},
        {"chrom": "chr9", "pos":136545786, "ref_base": "A", "alt_base": "T"},
        {"chrom": "chr9", "pos":21968622, "ref_base": "C", "alt_base": "-"},
        {"chrom": "chr9", "pos":21974827, "ref_base": "A", "alt_base": "T"},
        {"chrom": "chr9", "pos":37034031, "ref_base": "A", "alt_base": "T"},
        {"chrom": "chr9", "pos":5021988, "ref_base": "A", "alt_base": "T"},
]
for uid in range(len(data)):
    data[uid]["uid"] = uid
df = spark.createDataFrame(data)
print("Original DataFrame")
df.show()
```
Output:
```
Original DataFrame
+--------+-----+---------+--------+---+
|alt_base|chrom|      pos|ref_base|uid|
+--------+-----+---------+--------+---+
|       C| chr7|140734758|       T|  0|
|       G| chr7|140734780|       -|  1|
|       -| chr7|140736487|  GTGCGA|  2|
|       -| chr7|140736487| GTGCGAT|  3|
|       T| chr7|140742186|       -|  4|
|       G| chr7|140753351|       A|  5|
|       -| chr7|140800417|      CT|  6|
|       -| chr7|140800417|     CTG|  7|
|       -| chr7|140807936|       A|  8|
|       T| chr7|140924703|       A|  9|
|       T| chr7|148847298|       A| 10|
|       G| chr7| 27199497|       C| 11|
|       T| chr7|  2958506|       A| 12|
|       T| chr7| 50319062|       A| 13|
|       T| chr7| 55019278|       A| 14|
|       A| chr7| 55019338|       G| 15|
|  GGGTTG| chr7| 55181319|       -| 16|
|       T| chr8|127738263|       A| 17|
|       G| chr8| 43018497|       A| 18|
|       T| chr9|107489172|       A| 19|
+--------+-----+---------+--------+---+
only showing top 20 rows
```

Then, we create a Spark Resilient Distributed Dataset (RDD).

```python
rdd = sc.parallelize(data, 4)
```

Then, let's define a custom function which will be run in each worker node and for a partition of the RDD.

```python
import oakvar as ov

def get_ov_annotation(iterator):
    mapper = ov.get_mapper("gencode")
    clinvar = ov.get_annotator("clinvar")
    for row in iterator:
        ret = mapper.map(row)
        ret = clinvar.append_annotation(ret)
        yield ret
```

This function will be run as a standalone function in worker nodes, so the worker nodes should already have OakVar installed and their Python should have access to the installed OakVar package.

This function loads a `gencode` mapper and a `clinvar` annotation module, and for variant, runs the mapper and the annotator.

Let's apply this custom function to the variant RDD.

```python
ret = rdd.mapPartitions(get_ov_annotation).collect()
```

`ret` will be a `list` of `dict`, each `dict` corresponding to one annotated variant.

Let's create a new RDD with annotated variants. We'll use GENCODE mapper (`gencode`) and ClinVar annotator (`clinvar`). They should be already installed in the worker nodes.

```python
schema = ov.lib.util.run.get_spark_schema(["gencode", "clinvar"])
df = spark.createDataFrame(ret, schema)
```

The annotated variants can be saved as Parquet files.

```python
df.write.parquet("annotated_variants.parquet")
```

Or, quick inspection:
```python
df = df.toPandas()
print(df)
```
Output:
```
Annotated DataFrame
    uid chrom  ...  clinvar__id clinvar__sig_conf
0     0  chr7  ...    1410272.0              None
1     1  chr7  ...    1334201.0              None
2     2  chr7  ...          NaN              None
3     3  chr7  ...          NaN              None
4     4  chr7  ...          NaN              None
5     5  chr7  ...     376290.0              None
6     6  chr7  ...          NaN              None
7     7  chr7  ...          NaN              None
8     8  chr7  ...          NaN              None
9     9  chr7  ...          NaN              None
10   10  chr7  ...          NaN              None
11   11  chr7  ...          NaN              None
12   12  chr7  ...          NaN              None
13   13  chr7  ...          NaN              None
14   14  chr7  ...          NaN              None
15   15  chr7  ...     848579.0              None
16   16  chr7  ...          NaN              None
17   17  chr8  ...          NaN              None
18   18  chr8  ...          NaN              None
19   19  chr9  ...          NaN              None
20   20  chr9  ...          NaN              None
21   21  chr9  ...          NaN              None
22   22  chr9  ...          NaN              None
23   23  chr9  ...          NaN              None
24   24  chr9  ...          NaN              None
25   25  chr9  ...          NaN              None
26   26  chr9  ...          NaN              None

[27 rows x 21 columns]
```

We are considering adding more helper methods to OakVar to make this process more ergonomic. Please let us know what you think at our Discord server at [https://discord.gg/wZfkTMKTjG](https://discord.gg/wZfkTMKTjG)
