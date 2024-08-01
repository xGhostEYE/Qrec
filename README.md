# Qrec
University project for CMPT 470 with Julian where we build a quick method recommendation system for Python.

**Pre-installations**:
You need at minimum **50 GB** for the project (depending on the training set)

**Installations**:
Please run ```pip install -r requirements.txt``` to install the required libraries

**Edit the config file**
Please edit the config file according to the comments

**Run the project**
Populate the train folder and test folder with training and testing projects
If the train/test folder is not populated, running the below command will automatically scrape the data from the url that is specified in config file.
Please run ```python3 parserproject.py```

If the model does not exist, then the project will train the model before running the test
If the model exists, then the project will run the test directly from the existing model

**Retrieving results**
The results of the test will be printed in the terminal. In order to save it, please run the project from a Screen session and enable logging.
Future improvement will include saving the results in a file


