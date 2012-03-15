#!/usr/bin/env python

import os
import numpy
import sys
import random
import itertools

    
# These are the frequent itemsets for all k's.
# Keys are '1', ..., 'k' and values are sets of 
# n-membered sets for each key 'n' in [1, k].
frequent_itemsets = dict()

# Frequencies of all the itemsets. Keys are forzensets and values are floats.
itemset_frequencies = dict()
    
# Percentage of the transactions which need to have certain itemset before it's
# considered 'frequent itemset'.
threshold = 0.5

#    Map names to indexes.
#
#    Parameters:
#        filepath -    (absolute) path to file to read.
#                      File should have one name / line.
#
#    Returns dictionary with keys as course names and 
#    values mapped to indexes starting from 0.
def map_course_names(filepath = None):
    
    if filepath is None:
        raise ValueError("There was no filepath given to map_course_names.")
        return None

    names = []

    try:
        f = open(filepath, "r")
        lines = f.readlines()
        index = 0
    
        for l in lines:
            items = l.split()
            for item in items:
                if item not in names:
                    names.append(item)
                    index = index + 1
             
    except IOError:
        print("Could not read the file in %s" % (filepath))
        return None
    
    # Sort the names so that indices will come in lexicographical order.
    names.sort()
    name_map = dict()
    index = 0
    
    for n in names:
        name_map[n] = index
        index = index + 1
        
    return name_map


#    Read transactions to matrix using given name map.
#
#    Supposes that given file contains one transaction 
#    in line and each item in transaction is separated by 
#    " ".
#
#    Parameters:
#        filepath -    (absolute) path to file to read.
#                      File should have one name / line.
#        name_map - dictionary with keys as names and values
#                   as column indexes for items. 
#
#    Returns transactions matrix with each transaction
#    in one row and each column index representing item 
#    that is mapped to that particular index in name_map.
#   
def read_transactions(filepath = None, name_map = None):
    
    if filepath is None:
        raise ValueError("There was no filepath given to read_transactions.")
        return None
    
    if name_map is None:
        raise ValueError("There was no name_map given to read_transactions.")
        return None
    
    f = None

    try:
        f = open(filepath, "r")    
    except IOError:
        print("Could not open the file in %s" % (filepath))
        return None
    
    lines = f.readlines()
    columns = len(name_map.keys())
    rows = len(lines)
    transactions = numpy.zeros((rows, columns), dtype = int)
    print ("%d course names and %d transactions" % (columns, rows))
    
    current_row = 0
    
    for l in lines:
        items = l.split()
        for item in items:
            transactions[current_row][name_map[item]] = 1 
        
        current_row = current_row + 1
             
    return transactions


# Sort the transactions (reverse-)lexicographically so that 
# transactions which have items in small indexes are 
# in the first rows. Resulting matrix could be something 
# like this for "boolean" values:
#
#    [1, 1, 0, ..., 0, 1, 0]
#    [1, 0, 1, ..., 1, 0, 1]
#    [0, 1, 0, ..., 0, 0, 1]
#    ...
#    [0, 0, 0, ..., 1, 1, 1]
#
#    Params:
#        matrix - 2d numpy.matrix object
#    
#    Returns the sorted transactions matrix.
def lexsort_2d_matrix(matrix = None):
    
    if matrix is None:
        raise ValueError("No matrix given as an argument for lexsort_2d_matrix.")
        return None
    
    # Generate sorting keys for numpy's lexsort.
    sort_keys = []
    item_count = matrix.shape[1]
    for x in range(item_count):
        sort_keys.append(matrix[:,x])
    
    sort_keys.reverse()
    
    # Get the indices by which the original matrix will be sorted
    # lexicographical order.
    indices = numpy.lexsort(sort_keys, axis = 0)
    
    # Flip the matrix to get it in right (ie. reversed) order.
    return numpy.flipud(matrix[indices])


#    Calculate frequency percentage in transactions for each k-itemset in 
#    itemsets.
#
#    Params:
#        itemsets     - sequence of k-membered sets. Each member representing column.
#        transactions - numpy.matrix from which the frequencies are 
#                       calculated from.
#
#    Returns dictionary with k-itemsets as keys and frequencies as values.
def calculate_frequencies(itemsets = None, transactions = None):
    
    transactions_count = transactions.shape[0] 
    
    for itemset in itemsets:
        # Extract only itemset's columns from transactions
        set_as_list = list(itemset)
        cur_columns = transactions[:, set_as_list]
        current_freq = 0
        for row in cur_columns:
            # If all columns in cur_columns are "true" add one into 
            # frequency counting.
            if row.all():
                current_freq = current_freq + 1
                
        # Store the percentage
        itemset_frequencies[itemset] = float(current_freq) / float(transactions_count)    

#    Prune off itemsets' which have lower frequency than threshold.
#    Store rest to frequent_itemsets. All itemsets must have same amount
#    of members.
#
#    Params:
#        itemsets    - set of itemset's to be pruned.      
def prune_itemsets(itemsets = None, threshold = 0.5):  
    
    k = len(random.choice(list(itemsets)))
    
    if k not in frequent_itemsets:
        frequent_itemsets[k] = set()   

    for itemset in itemsets:
        if itemset_frequencies[itemset] > threshold:
            frequent_itemsets[k].add(itemset) 
            print "%d: %s, %s" % (k, itemset, itemset_frequencies[frozenset(itemset)]) 
            
        
#    Generate k+1-itemsets from previous frequent itemsets.
#
#    Params:
#        k - positive integer. frequent_itemsets needs to have value for key k-1.
#
#    Returns new k+1-itemsets which have all their subsets in frequent_itemsets[k-1].
def generate_itemsets(k):
    
    if len(frequent_itemsets[k]) == 0:
        return None
        
    old_is1 = frequent_itemsets[k]
    old_is2 = frequent_itemsets[k]
    new_itemset = set()
    
    for itemset1 in old_is1:
        for itemset2 in old_is2:
            # If sets intersection is k-1 then they have exatcly one different
            # member in both of them.
            if len(itemset1.union(itemset2)) == k+1:
                cur_set = itemset1.union(itemset2)
                # Test that all the subsets of the candidate are in 
                #frequent_itemsets.
                for subset in set(itertools.combinations(cur_set, k)):
                    if subset not in frequent_itemsets[k]:
                        break
                new_itemset.add(cur_set)
                
    return new_itemset
            
                         
def main():
    
    if len(sys.argv) < 3:
        print("Usage: %s input_file %%-threshold" % (sys.argv[0]))
        sys.exit(0)
    
    input_file = sys.argv[1]
    threshold = float(sys.argv[2])
    
    name_map = map_course_names(input_file)
    transactions = read_transactions(input_file, name_map)
    transactions = lexsort_2d_matrix(transactions)
    
    # First create all 1-itemsets
    itemsets = set()
    for x in range(transactions.shape[1]):
        itemset = set()
        itemset.add(x)
        itemsets.add(frozenset(itemset))
        
    calculate_frequencies(itemsets, transactions)
    prune_itemsets(itemsets, threshold)
        
    # Then loop through the rest
    for x in range(5):
        k = x + 2
        new_itemsets = generate_itemsets(k-1) 
        if new_itemsets is None:
            break
        calculate_frequencies(new_itemsets, transactions)
        prune_itemsets(new_itemsets, threshold)
    
  
# make this runnable from commandline with arguments  
if __name__ == "__main__":

    
    main()
    
    
    
        
        
    
    
    