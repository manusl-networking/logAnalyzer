[2.0.0 - 2022-06-24]

- Starting major version `2.0.0`.
- ReWrite of function `constructExcel()`
    - If data is empty, because parsing detected nothing, tab color is now blue. This will help identify easily when parsing is not working.
    - Nex `index` tab implemented, with hyperlinks to all sheets.

[2022-05-06]

- Function `readLog()` modified.
    - New paramterer `jsonFormat` to distinguish the type of the logs.
    - If the host OS is not Windows or Linux, quits.

- Function `readLogJson()` removed.

- Function `readTemplate()` not returning variable `results_template` anymore.

- Function `parseResults()` modified.
    - changes inside the funcion
    - better handling of `json` files
    - input parameter `read_template` removed

- File `templateShow.csv` to match the contents of the `Template` folder.