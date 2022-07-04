[3.1.1 - 2022-07-04]
- Parameter `-json` with default = yes.
- Updates on when platform is windows (equal to win64 or win32), to handle with paths correctly:
    - In function `readLog()`: update of listContent.
    - In function `main()`: condition to replace `/` in templateFolder

[3.1.0 - 2022-07-03]

- The folder of the templates can now be specified by the parameter `--templateFolder`. The default is `TemplatesTextFSM/`.
- The file `--csvTemplate` is now optional. If omitted, then all the templates under the folder `--templateFolder` will be considered for parsing.
- Templates can be of type `textFSM` or `ttp`. To choose, use the parameter `-te/--templateEngine`.
    - Be sure to point to the correct folder of templates, when changing the engine.


[3.0.0 - 2022-07-01]

- ReWrite of functions `readTemplate()` , `readLog()` and `parseResults()`.

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
