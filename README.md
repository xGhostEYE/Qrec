# Qrec
University project for CMPT 470 with Julian where we build a quick method recommendation system for Python.<br />

**Pre-installations**:<br />
You need at minimum **50 GB** for the project (depending on the training set)<br /><br />

**Installations**:<br />
Please run ```pip install -r requirements.txt``` to install the required libraries<br /><br />

**Edit the config file**:<br />
Please edit the config file according to the comments<br /><br />

**Run the project**<br />

<ins>Synchronous Run</ins>: <br/><br/>
Please run ```python3 parserproject.py --[FLAGS]``` to run the project<br />

The [FLAGS] options are: <br/>

`-a` or `--all`: A flag to request everything (except for --project and --outputfile). This flag has the highest priority <br/> 
`-r` or `--run`: A flag to request running training and testing only for the default train and test dataset <br/>
    
`-p` or `--project`: A flag to specify the project/commit to be extracted. Run with --outputfile flag to specify the output file <br/>
`-f` or `--outputfile`: A flag to specify the csv file name for the extracted dataset. Run with --project flag to specify the project to be extracted <br/>

`-n` or `--csv_train`: A flag to request creating training dataset (in csv) <br/>
`-t` or `--csv_test`: A flag to request creating testing dataset (in csv) <br/>
`-d` or `--scrape_train`: A flag to request scrapping projects for train data <br/>
`-c` or `--scrape_test`: A flag to request srapping projects for test data <br/>
`-i` or `--train`: A flag to request running training <br/>
`-o` or `--test`: A flag to request running testing <br/>

For example, if you want to run the program with every options, you can run: <br/>
```python3 parserproject.py --all``` or ```python3 parserproject.py -a``` <br/>

<ins>Concurrent Run<ins>: <br/>

Please make sure you specify the number of core on your machine in the config.ini under [System]'s `num_core`
To run the program concurrently, please run ```java -jar target/Qrec-1.0-SNAPSHOT.jar```



