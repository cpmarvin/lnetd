import time
import pprint
class Node:
        '''
        Class to contain the lspid seq and all data.
        '''
        def __init__(self, name,pseudonode,fragment,seq_no,data):
            self.name = name
            self.data = data
            self.pseudonode = pseudonode
            self.seq_no = seq_no
            self.fragment = fragment
        def __unicode__(self):
            full_name = ('%s-%d-%d') %(self.name,self.pseudonode,self.fragment)
            return str(full_name)
        def __cmp__(self, other):
		    self_tuple = (self.name, self.pseudonode, self.fragment)
		    other_tuple = (other.name, other.pseudonode, other.fragment)
		    if self_tuple > other_tuple:
		        return 1
		    elif self_tuple < other_tuple:
		        return -1
		    return 0
        def __repr__(self):
            full_name = ('%s-%d-%d') %(self.name,self.pseudonode,self.fragment)
            #print 'iside Node full_name: {} \n\n\n ------'.format(full_name)
            return str(full_name)
            
class Neighbour:
        '''
        Class to contain a neighbor name and the metric.
        '''
        def __init__(self, name, metric):
            self.name = name
            self.metric = metric
        def __unicode__(self):
            return self.name
        def __cmp__(self, other):
            if self.name > other.name:
                return 1
            elif self.name < other.name:
                return -1
            # The neighbour name is equal but dont match them is the metric is
            # different
            if self.metric > other.metric:
                return 1
            elif self.metric < other.metric:
                return -1
            else:
                return 0
        def to_json(self):
            return {'name': self.name, 'metric': self.metric}


