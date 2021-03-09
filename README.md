# README #

This idea was born because of the need for a simple tool in order to automate execution for the simple analysis of logs of Nokia Sros router equipment configurations, which reads the content of a log in txt format, extracted with the taskAutom tool, which parses only the necessary information and compares the information, thus verifying if there are modifications in the specific values, said tool is designed to work in conjunction with the aforementioned.

## Setup ##

#### System Libraries
These libraries have been tested under Ubuntu 20.04 and Python3.8.

```bash
sudo pip3 install -r requirements.txt
```

#### Compile
You can run `logAnalyzer` directly from the CLI using Python. However, compiling improves performance.

```bash
python3 -m nuitka logAnalizer.py
```
Compiling has been tested succesfully under Ubuntu. Don't know if this is directly supported under Windows. If it fails, let me know. Nevertheless, as mentioned, you can run `logAnalyzer_win` directly from the CLI using Python

## Usage ##

The program needs three inputs: a) CSV file with data, b) a folder, which is containing templates for specific commands executed on routers and c) a folder, which is containing logs from `taskAutom`

#### CSV

The CSV file must have in its first column, the name of templates created for the specific commands

```csv
nokia_sros_show_router_bgp_summary.template
nokia_sros_show_router_interface.template
nokia_sros_show_service_sdp.template
```

#### Templates

The templates are in the Templates folder, which is next to the script, since the script reads the csv and uses the indicated template to perform the function of parsing the results and ordering them in an excel

#### Result

If `logAnalyzer` is invoked with option `jobType=0`, reads the specific content in the folder for a given command executed by `taskAutom` and then requested by the `logAnalyzer` template and then save the results in an excel.

```bash
$ python3 logAnalyzer.py -csv templateExample.csv -pre folderBytaskAutom/ -job 0
<_io.TextIOWrapper name='Templates/nokia_sros_show_service_sdp-using.template' mode='r' encoding='UTF-8'>
#####Plantillas Cargadas Exitosamente#####
#########Logs Cargados Exitosamente#########
ROUTER_EXAMPLE_rx.txt nokia_sros_show_service_sdp-using.template
#
#
Guardando

```

Otherwise, if `logAnalyzer` is invoked with option `jobType=1`, in this case it compares the content of pre and post log folders, such as if we run checks to see the status of the routers before and after a task and then save the results in an excel.

```bash
$ python3 logAnalyzer.py -csv templateExample.csv -pre folderBytaskAutomBefore/ -post folderBytaskAutomAfter/ -job 1
<_io.TextIOWrapper name='Templates/nokia_sros_show_service_sdp-using.template' mode='r' encoding='UTF-8'>
#####Plantillas Cargadas Exitosamente#####
#########Logs Cargados Exitosamente#########
#########Logs Cargados Exitosamente#########
ROUTER_EXAMPLE_rx.txt nokia_sros_show_service_sdp-using.template
ROUTER_EXAMPLE_rx.txt nokia_sros_show_service_sdp-using.template
#
#
Guardando

#### Configuration Options

`logAnalyzer` can be configured through CLI as shown below.

```bash
$ python3 logAnalyzer.py -h
usage: PROG [options]

Log Analysis

optional arguments:
  -h, --help            show this help message and exit
  -pre PREFOLDER, --preFolder PREFOLDER
                        Folder with PRE Logs. Debe terminar en "/"
  -post POSTFOLDER, --postFolder POSTFOLDER
                        Folder with POST Logs. Debe terminar en "/"
  -csv CSVTEMPLATE, --csvTemplate CSVTEMPLATE
                        CSV con templates a usar en el parsing.
  -job JOBTYPE, --jobType JOBTYPE
                        Tipo de trabajo de desea realizar, O Captura, 1 Ventana

```
