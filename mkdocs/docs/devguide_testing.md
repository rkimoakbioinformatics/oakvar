OakVar has a command for testing the modules you are developing. 

```
ov test -m MODULE_NAME [MODULE_NAME]...
```

For example,

```
ov test -m clinvar
```

will test `clinvar` module, if it is in your annotators directory.

For this test to work, your module's Python script (`clinvar.py` in `clinvar` module) should have `test` method.

For example, let's say you want to test if your annotator module's `annotate` method works well for some test input. `clinvar.py` can have something like the following.

```
def test(*args, **kwargs):
    m = Annotator()
    m.base_setup()
    out = m.annotate({
        "chrom": "chr1", 
        "pos": 925952, 
        "ref_base": "G", 
        "alt_base": "A"
    })
    expected = {
        'sig': 'Uncertain significance', 
        'disease_refs': 'MedGen:CN517202', 
        'disease_names': 'not provided', 
        'rev_stat': 'criteria provided, single submitter', 
        'id': 1019397, 
        'sig_conf': None
    }
    if out == expected:
        return True, ""
    else:
        return False, \
            f"annotated output does not match expected: {out} != {expected}"
```

`Annotator()` to create an instance of your annotator and call `base_setup()` to set up the annotator instance. In the code above, expected and actual output are compared. The return value of `test` is always `Tuple[bool, str]`. `bool` shows whether the test was successful or not. `str` can have an arbitrary message.

With the `test` code above in `clinvar.py`, `ov test -m clinvar` will produce the following.

```
>ov test -m clinvar
[2024/11/10 09:08:06] clinvar: testing...
[2024/11/10 09:08:06] clinvar: ok
[2024/11/10 09:08:06] passed 1 failed 0
```

`ov test` will create `oakvar_module_test` folder under the current directory. To wipe out the test folder and perform a clean test, give `--clean` option.

`test` method can have any test logic. Below is a test example for `csvreporter`.

```
def test(*args, **kwagrs):
    from pathlib import Path
    import subprocess
    from oakvar import get_module_test_dir
    import csv

    test_dir = get_module_test_dir("csvreporter", module_type="reporter")
    if not test_dir:
        return False, "could not find csvreporter test dir."
    input_path = (test_dir / "oakvar_example.vcf").resolve()
    subprocess.run(["ov", "run", str(input_path), 
        "-t", "csvreporter", "-d", "."])
    output_path = Path(".") / (input_path.name + ".variant.csv")
    if not output_path.exists():
        return False, f"ov run did not produce {output_path}."
    reference_path = test_dir / "oakvar_example.vcf.variant.csv"
    with open(output_path, mode="r") as f:
        reader = csv.reader(f, )
        out = [row for row in reader if not row[0].startswith("#")]
    with open(reference_path, mode="r") as f:
        reader = csv.reader(f)
        ref = [row for row in reader if not row[0].startswith("#")]
    if out == ref:
        return True, ""
    else:
        return False, "output does not match reference."
```

The method invokes OakVar to do a complete run to produce the output file of the reporter module. Then, it compares the output with the reference data. 

For convenience, OakVar provides `get_module_test_dir` method, which will give the path to the `test` folder under the tested module's directory. This way, you can add input files and reference output files in the `test` folder and conveniently access them from within the `test` method.

Since `test` method is a regular Python method and the only requirement for the method is the `Tuple[bool, str]` return value, `test` can even connect to internet sources and do comparison as well.

`*args` and `**kwargs` arguments are not currently used, but reserved for future expansion of the method.

If tested modules do not have `test` method, then the test will pass.

```
ov test -m biogrid go
[2024/11/10 09:27:14] biogrid: testing...
[2024/11/10 09:27:14] biogrid: no test function. Skipping.
[2024/11/10 09:27:14] go: testing...
[2024/11/10 09:27:14] go: no test function. Skipping.
[2024/11/10 09:27:14] passed 2 failed 0
```

Testing can be done with Python API as well.

```
➜ python
Python 3.12.3
Type "help", "copyright", "credits" or "license" for more information.
>>> import oakvar as ov
>>> ov.api.test.test(["clinvar", "go"])
[2024/11/10 09:28:55] clinvar: testing...
[2024/11/10 09:28:56] clinvar: ok
[2024/11/10 09:28:56] go: testing...
[2024/11/10 09:28:56] go: no test function. Skipping.
[2024/11/10 09:28:56] passed 2 failed 0
{
    'passed': True, 
    'details': {
        'clinvar': {
            'passed': True, 
            'msg': ''
        }, 
        'go': {
            'passed': True, 
            'msg': 'no test function'
        }
    }, 
    'num_passed': 2, 
    'num_failed': 0
}
```

The return value of `oakvar.api.test.test` is a `dict`:

```
passed: bool. True if all modules passed or False
details: a dict. Keys are module names. Values are:
    passed: bool. True if the module passed or False
    msg: str. Any return message from the module's test method.
num_passed: int. Number of modules which passed
num_failed: int. Number of modules which did not pass
```

