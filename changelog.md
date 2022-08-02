[3.2.2 - 2022-08-02]
- When the amount of templates for pre vs post comparison is different, an exception ocurred. Either control this by using a csv file or having the same amount of templates in each template folder.

[3.2.1 - 2022-08-01]
- Typo.

[3.2.0 - 2022-08-01]
- In the definition of the templates files, a new comment must be included `#majorDown:`. This comment should be followed by the keywords.
    - Example: `#majorDown: open,connect` will also count for major down on the analysis.
- The default folder for templates is `Templates/` under the option `-tf`
- New options for folders: `-tf-post`. Some times, a different folder is needed for comparison, for example, when there is a operating system change between tasks. With this option, a different set of templates can be used for the `post` folder.

[3.1.2 - 2022-07-24]
- In function `parseResults()`, better detection of `json` files.
    - When the name had a dot `.` in its name, parsing was not being performed. Is solved now.

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
