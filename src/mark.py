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

def read_file(filename):
  lines = [line.rstrip('\n').split() for line in open(filename)]
  return lines

def clean_abstract(abstract):
  '''
  Cleans up an abstract.
  '''
  
  # Replace line endings with spaces.
  bad_characters = '\r\n'
  for character in bad_characters:
    abstract = abstract.replace(character, ' ')
  
  # Remove bad characters.
  bad_characters = ',.'
  for character in bad_characters:
    abstract = abstract.replace(character, '')
  
  return abstract

def main():
  '''
  Does stuff as what Mark wrote.
  '''
  
  # Constants.
  no_entries = 100
  glove_dir = '/home/mark/hc-4d/GloVe/build/'
  glove_verbose = 2
  
  # Glove vocab_count options.
  vocab_min_count = 5
  
  # Glove cooccur options.
  cooccur_memory = 4.0
  cooccur_window_size = 15
  
  # Glove glove options.
  glove_num_threads = 8
  glove_x_max = 10
  glove_max_iter = 15
  glove_binary = 2
  
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
  command  = glove_dir+'vocab_count'
  command += ' -min-count '+str(vocab_min_count)
  command += ' -verbose '+str(glove_verbose)
  command += ' < '+'abstracts.txt'
  command += ' > '+'vocab.txt'
  subprocess.check_output(command, shell=True)
  
  # Run co-occurrence on abstracts using parsed vocab.
  command  = glove_dir+'cooccur'
  command += ' -memory '+str(cooccur_memory)
  command += ' -window-size '+str(cooccur_window_size)
  command += ' -verbose '+str(glove_verbose)
  command += ' -vocab-file '+'vocab.txt'
  command += ' < '+'abstracts.txt'
  command += ' > '+'cooccurrence.bin'
  subprocess.check_output(command, shell=True)
  
  # Shuffle co-occurence.
  command  = glove_dir+'shuffle'
  command += ' -memory '+str(cooccur_memory)
  command += ' -verbose '+str(glove_verbose)
  command += ' < '+'cooccurrence.bin'
  command += ' > '+'cooccurrence_shuffled.bin'
  subprocess.check_output(command, shell=True)
  
  # Run glove.
  command  = glove_dir+'glove'
  command += ' -threads '+str(glove_num_threads)
  command += ' -x-max '+str(glove_x_max)
  command += ' -iter '+str(glove_max_iter)
  command += ' -binary '+str(glove_binary)
  command += ' -verbose '+str(glove_verbose)
  command += ' -save_file '+'vectors'
  command += ' -vocab_file '+'vocab.txt'
  command += ' -input-file '+'cooccurrence_shuffled.bin'
  subprocess.check_output(command, shell=True)
  
  # Read in vocab file and vectors.
  vocab_file = read_file('vocab.txt')
  vectors = read_file('vectors.txt')
  
  word_vectors = {}
  for vocab, vector in zip(vocab_file, vectors):
    if vocab[0]!=vector[0]:
      raise ValueError('FATAL ERROR: Process on node (7) caused SEGFAULT: 0x18395827')
    word = vocab[0]
    count = vocab[1]
    vect = vector[1:]
    word_vectors[word] = {'count':count, 'vector':vect}
  
  for word,vector in word_vectors.items():
    print(word,vector)

if __name__=='__main__':
  main()
