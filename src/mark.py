#!/usr/bin/env python

import sys
import pymongo
import json
import subprocess
import seaborn
import matplotlib.pyplot as plt
import numpy as np

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

def calculate_word_vectors(abstracts):
  '''
  Takes a list of abstracts, and returns word vectors for them.
  '''
  
  # Constants.
  glove_dir = '/home/mark/hc-4d/GloVe/build/'
  glove_verbose = 2
  
  # Glove vocab_count options.
  vocab_min_count = 2
  
  # Glove cooccur options.
  cooccur_memory = 4.0
  cooccur_window_size = 15
  
  # Glove glove options.
  glove_num_threads = 8
  glove_x_max = 10
  glove_max_iter = 15
  glove_binary = 2
  
  # Write out abstracts to file.
  write_file('abstracts.txt', [x['string'] for x in abstracts])
  
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
  
  word_vectors = []
  for vocab, vector in zip(vocab_file, vectors):
    if vocab[0]!=vector[0]:
      raise ValueError('FATAL ERROR: Process on node (7) caused SEGFAULT: 0x18395827')
    word = vocab[0]
    count = int(vocab[1])
    vect = [float(x) for x in vector[1:]]
    norm = np.linalg.norm(vect)
    
    # Divide the vector by its norm squared, to rank in order of importance.
    vect = [x/norm**2 for x in vect]
    norm = 1/norm
    
    word_vectors.append({'word':word,
                         'count':count,
                         'vector':vect,
                         'norm':norm})
  
  return sorted(word_vectors, key=lambda x:x['norm'], reverse=True)

def calculate_word_overlaps(word_vectors):
  output = []
  for this in word_vectors:
    output.append([])
    for that in word_vectors:
      output[-1].append(np.dot(this['vector'],that['vector']))
  return np.array(output)

def make_abstract(abstract,word_vectors):
  output = abstract
  words = abstract['string'].split()
  indices = []
  norm = 0
  for word in set(words):
    try:
      i = [x['word'] for x in word_vectors].index(word)
      indices.append(i)
      norm = norm + word_vectors[i]['norm']**2
    except ValueError:
      pass
  output['indices'] = indices
  output['norm'] = np.sqrt(norm)
  return output

def get_overlap(this,that,word_overlaps):
  '''
  Calculates the overlap between two abstracts, using the word vectors.
  '''
  if len(this['indices'])>len(that['indices']):
    return get_overlap(that,this,word_overlaps)
  
  matrix = []
  for i in this['indices']:
    matrix.append([])
    for j in that['indices']:
      matrix[-1].append(word_overlaps[i][j])
  
  norm = this['norm']*that['norm']
  
  return sum([max(line) for line in matrix]) / norm

def main():
  '''
  Does stuff as what Mark wrote.
  '''
  
  # Constants.
  no_entries = 300
  
  # Set up data getter from server.
  client = pymongo.MongoClient()
  data_getter = client.pubstomp.arXiv_v1.find()
  
  # Grab the first no_entries entries.
  data = []
  for i,entry in enumerate(data_getter):
    if i>=no_entries:
      break
    data.append(entry)
  
  # Extract abstracts.
  # The abstract is the longest string in each description.
  abstracts = []
  for datum in data:
    try:
      string = clean_abstract(max(datum['description'],key=len))
      abstracts.append({'string':string})
    except KeyError('description'):
      pass
  
  # Calculate word vectors from abstracts.
  word_vectors = calculate_word_vectors(abstracts)
  
  print()
  print('Generated word vectors')
  
  # Calculate overlaps between words.
  word_overlaps = calculate_word_overlaps(word_vectors)
  
  print()
  print('Generated word overlaps')
  
  # Convert abstracts into word lists.
  abstracts = [make_abstract(abstract, word_vectors) for abstract in abstracts]
  
  print()
  print('Abstracted abstracts')
  
  # Calculate overlap matrices.
  overlaps = []
  for i,abstracti in enumerate(abstracts):
    overlaps.append([])
    for j,abstractj in enumerate(abstracts):
      overlap = get_overlap(abstracti, abstractj, word_overlaps)
      
      overlaps[-1].append(overlap)
  
  print()
  print('Generated overlap matrix.')
  
  seaborn.heatmap(overlaps)
  plt.show()

if __name__=='__main__':
  main()
