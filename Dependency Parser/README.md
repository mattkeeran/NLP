# Dependency Parser 
## By Matthew Keeran
Written in python 3.5.4 on Windows 8.1. Tested with python 3.6 on Ubuntu 16.

### Instructions:
Runs via python dependency_parser.py followed by a .txt file with an annotated sentence to parse.
I personally pipe the output to a text file, then enter the file names one by one followed by enter.	

python dependency_parser.py > output.txt

piper.txt

### Input 1:
Uses a hardcoded corpus to train on (in this case wsj-clean.txt), which contains sentences with parts of speech and heads of associated words denoting arcs. 
### Input 2:
Takes a .txt file with a sentence, each word separated by a '/' and a part of speech
### Output:
Outputs statistics related to corpus and the best dependency graph of the input sentence based on the arcs found in the corpus.
