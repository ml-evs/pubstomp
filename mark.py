#!/usr/bin/env python

import sys
import pymongo
import json
import subprocess

def write_file(filename, lines):
  '''
  Write a file containing the given lines.
  '''
  with open(filename, 'w') as f:
    for line in lines:
      f.write(line+'\r\n')

def clean_abstract(abstract):
  '''
  Cleans up an abstract.
  '''
  
  # Remove bad characters.
  bad_characters = '\r\n'
  for character in bad_characters:
    abstract = abstract.replace(character, ' ')
  
  return abstract

def main():
  '''
  Does stuff as what Mark wrote.
  '''
  
  # Constants.
  no_entries = 100
  glove_dir = '/home/mark/hc-4d/GloVe/build/'
  
  # vocab_count options.
  vocab_min_count = 5
  vocab_verbose = 2
  
  # Set up data getter from server.
  client = pymongo.MongoClient()
  data_getter = client.pubstomp.arXiv_v1.find()
  
  # Grab the first no_entries entries.
  data = []
  for i,entry in enumerate(data_getter):
    data.append(entry)
    if i==99:
      break
  
  # Concatenate abstracts, and write them to abstracts.txt.
  # The abstract is the longest string in each description.
  abstracts = []
  for datum in data:
    abstracts.append(clean_abstract(max(datum['description'],key=len)))
  write_file('abstracts.txt', abstracts)
  
  # Run vocab parser on abstracts.
  command = glove_dir+'vocab_count'
  subprocess.check_output(command+
                          ' -min-count '+str(vocab_min_count)+
                          ' -verbose '+str(vocab_verbose)+
                          ' <'+' abstracts.txt'+
                          ' >'+' vocab.txt',
                          shell=True
                         )
  

if __name__=='__main__':
  main()
