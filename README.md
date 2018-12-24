# Getting Started


In order to use the tension analysis tool, run the following command on
the terminal:


```shell
$ python main.py models/model.h5 models/variables.p datasets/interview_transcripts/BertheKayitesi.docx output.csv
```

**NOTE:**
The above command requires five arguments:

1. *main.py* (this file can be found in ***Tension Analysis*** folder)
2. *models/model.h5* (relative path for the trained model for emotion recognition)
3. *models/variables.p* (relative path for stored variables)
4. *datasets/interview_transcripts/ENTREVUE AVEC BERTHE KAYITESI-LS-English Translation.docx* (path to the interview file)
5. *output.csv* (Name of the output file)


### For Developers

Follow the steps provided below in order to get everything set up:

1. Install Python
```shell
$ python3 --version
Python 3.6.7rc1
```
2. Install Git and download this repository
```shell
$ sudo apt install git
$ git clone https://github.com/jumayel06/Tension-Analysis.git
```
3. Download the following files from this link (https://drive.google.com/drive/folders/1_A_KORVFA3yjkdwDtaDyywQq3H97sfUS):
```
model.h5
variables.p
stanford-corenlp-full-2018-02-27.zip
```
4. Copy the first two files (*model.h5* and *variables.p*) in a new folder called **models**.
5. Copy the last file in the **resources** folder.