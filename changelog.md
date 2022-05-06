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