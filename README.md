# Getting Started

*(Recommended operating systems: macOS or Linux)*

Follow the steps provided below in order to get everything set up:

1. Install Python
```console
$ python3 --version
Python 3.6.7rc1
```
2. Install Git and download this repository
```console
$ sudo apt install git
$ git clone https://github.com/jumayel06/Tension-Analysis.git
```
3. Download the following files from this link: https://goo.gl/PUDAKv
* model.h5
* variables.p
* stanford-corenlp-full-2018-02-27.zip

4. Copy the first two files (*model.h5* and *variables.p*) in a new folder called **models**.
5. Copy the last file (*stanford-corenlp-full-2018-02-27.zip*) in the **resources** folder and unzip it.
6. Install the following packages from terminal:
```console
$ sudo apt install python3-pip
$ sudo apt install default-jre
$ pip3 install bs4
$ pip3 install mammoth
```
7. Install nltk and other dependencies
```
$ pip3 install nltk
$ python3
> import nltk
> nltk.download('punkt')
> nltk.download('wordnet')
> exit()
```
8. Install other packages
```
$ pip3 install psutil
$ pip3 install vaderSentiment
$ pip3 install numpy
$ pip3 install keras
$ pip3 install tensorflow
$ pip3 install emoji
$ pip3 install sklearn
```


### For Users
In order to use the tension analysis tool, run the following command on
the terminal:


```console
$ python3 main.py models/model.h5 models/variables.p datasets/interview_transcripts/BertheKayitesi.docx output.csv
```

**NOTE:**
The above command requires five arguments:

1. *main.py* (this file can be found in ***Tension Analysis*** folder)
2. *models/model.h5* (relative path for the trained model for emotion recognition)
3. *models/variables.p* (relative path for stored variables)
4. *datasets/interview_transcripts/BertheKayitesi.docx* (path to the interview file)
5. *output.csv* (Name of the output file)

The above command will analyze the provided interview transcript and generate
a csv file similar like this:

<img src="sample.png" width="500" height="250" />


***Important:*** Provided interview transcript should be in the right
format for this tool to work correctly.


**Tutorial:** https://goo.gl/cegbjB