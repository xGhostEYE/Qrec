# Qrec
University project for CMPT 470 with Julian where we build a quick method recommendation system for Python.<br />

**Pre-installations**:<br />
You need at minimum **50 GB** for the project (depending on the training set)<br /><br />

**Installations**:<br />
Please run ```pip install -r requirements.txt``` to install the required libraries<br /><br />

**Edit the config file**:<br />
Please edit the config file according to the comments<br /><br />

**Run the project**<br />
Populate the train folder and test folder with training and testing projects<br />
If the train/test folder is not populated, running the below command will automatically scrape the data from the url that is specified in config file.<br />
Please run ```python3 parserproject.py```<br />

1. If the model does not exist, then the project will train the model before running the test<br />
2. If the model exists, then the project will run the test directly from the existing model<br /><br />

**Retrieving results**<br />
The results of the test will be printed in the terminal. In order to save it, please run the project from a Screen session and enable logging.<br />
Future improvement will include saving the results in a file<br />
