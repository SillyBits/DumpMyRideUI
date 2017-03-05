###############################
# Nodes.py
#
# Class 'Nodes' will deal with all the ugly details:
# - Keeps treeview in sync
# - Handle recursive loading
# - Handles caching (TBD)
#
###############################

import os

from Helpers import shorten_path
from processors.ProcessorFactory import ProcessorFactory


'''
Single node in tree
TODO: Caching for 'lengthly' nodes?
'''
class Node:
    
    def __init__(self, parent, iid, label, info, processor, extract_to, 
                 exists, details=None, hexdump=None, childs=[]):
        self.parent = parent
        self.iid = iid
        self.label = label
        self.processor = processor
        self.info = info
        self.extract_to = extract_to
        self.exists = exists
        self.static_details = details
        self.static_hexdump = hexdump
        self.childs = []
        self.child_lookup = {}
        if childs and len(childs):
            for child in childs: self.add_child(child)

    def __str__(self):
        exists = "(X)" if self.exists else "(-)" if self.exists==False else ""
        processor = (str(type(self.processor)).\
                     replace("<class '","").replace("'>","").\
                     split(".")[-1]
                    ) if self.processor else "?"
        extract_to = shorten_path(self.extract_to)
        return "{}:{} {} -> {}".format(self.label, exists, processor, extract_to)


    def add_child(self, child):
        self.childs.append(child)
        self.child_lookup[child.iid] = child

    def get_child(self, iid):
        assert iid in self.child_lookup
        return self.child_lookup[iid]


    def get_details(self, callback=None):
        if self.static_details:
            return self.static_details
        if self.exists == False:
            return "No data to display, file needs to be extracted first"
        if self.processor:
            if self.processor.has_details:
                return self.processor.get_details(callback)
            return "No details avail for this type of file"
        return ""

    def set_details(self, details):
        self.static_details = details


    def get_hexdump(self, callback=None):
        if self.static_hexdump:
            return self.static_hexdump
        if self.exists == False:
            return "No data to display, file needs to be extracted first"
        if self.processor:
            if self.processor.has_hexdump:
                return self.processor.get_hexdump(callback)
            return "No hex dump avail for this type of file"
        return ""

    def set_hexdump(self, hexdump):
        self.static_hexdump = hexdump


'''
Nodes handling
'''
class Nodes:

    def __init__(self, tree):
        self.tree = tree # Or better 'app' to get access to other functions too?
        self.nodes = {}


    '''
    Add given file to tree
    Both label and info can be passed instead of being generated here, 
    same with static versions of hexdump and details (as used with root node)
    '''
    def add(self, parent, file, label=None, info=None, extract_to=None, 
            details=None, hexdump=None, lazy=True, callback=None):
        assert file

        processor = ProcessorFactory.create(file)
        #assert processor # Not allowed to have NO processor!
        if not processor:
            return None

        parent_iid = parent.iid if parent else ""

        basename = os.path.basename(file)
        filename,ext = os.path.splitext(basename)
        is_folder = os.path.isdir(file)
        is_archive = ext.lower() in (".zip",".cab")

        if not label:
            label = basename

        if not info:
            info = "(" + processor.description + ")"

        if not extract_to: 
            extract_to = self.nodes[parent_iid].extract_to
            if is_archive:
                extract_to = os.path.join(extract_to,filename)
            else:
                extract_to = os.path.join(extract_to,basename)
        
        if is_archive:
            exists = os.path.exists(extract_to) #TODO: Check whole tree
        else:
            exists = os.path.exists(file)

        iid = self.tree.add(parent_iid, label, info, exists, open=not lazy)
        assert iid

        node = Node(parent, iid, label, info, processor, extract_to, exists, 
                    details, hexdump)
        self.nodes[iid] = node
        if parent:
            parent.add_child(node)

        #TODO: Lazy and other checks to decide further actions (adding dummy for example)
        if is_folder or is_archive:
            if lazy:
                dummy = self.tree.add(iid, "dummy", "dummy", None, False)
            else:
                self._tree_populate(node, open=not lazy, callback=callback, max_levels=1)

        return node


    '''
    Expand given node, extracting childs if told so
    '''
    def expand(self, iid, extract=True, callback=None):#???
        assert iid
        assert iid in self.nodes
        self._tree_expanding(self.nodes[iid], callback, max_levels=1)
   

    '''
    Extract given node and all childs if told so
    TODO: Replaced by method above?
    ' ''
    def extract(self, node, all=False, callback=None):
        '' '
        values = self.values[self.tree.current]
        print("\nThis will extract selected item only: {}\n{}".\
            format(self.tree.current,self.prettify_values(values)))
        processor = values["processor"]
        if processor and processor.can_save:
            processor.save(values["extract_to"], callback=self.extract_callback)
            #self.update_ui()
            self.tree_populate(self.tree.current)
        '' '
        pass
    '''


    '''
    Container support by wrapping nodes dict
    '''
    def __len__(self):
        return len(self.nodes)

    def __contains__(self, key):
        return key in self.nodes

    def __iter__(self):
        return self.nodes.__iter__()

    def __getitem__(self, key):
        assert key in self.nodes
        return self.nodes[key]

    def __setitem__(self, key, value):
        raise Exception("Not allowed to set values this way")

    def __delitem__(self, key):
        raise Exception("Not allowed to delete values this way")


    '''
    Recursive tree population
    '''
    def _tree_populate(self, node, open=False, callback=None, max_levels=None):
        assert node
        assert node.iid
        assert node.iid in self.nodes 
        assert node.processor

        # Get childs ...
        if callback: callback()
        content = node.processor.get_childs(callback) or {}
        if not len(content):
            return
        # ... and fill tree
        if callback: callback()
        print(content,"\n")
        if max_levels:
            max_levels += node.iid.count("/")

        def recurs_fill(curr, parent, open):
            if callback: callback()
            print("Node.Populate for:",parent)

            depth = parent.iid.count("/")+1

            # Non-path childs first
            for file in sorted( [key for key in curr.keys() if len(curr[key]) == 0] ):
                if callback: callback()
                print("- File:",file)
                file = os.path.join(parent.extract_to,file)
                # Adding might trigger another call into _tree_populate if
                # file is a cabinet
                node = self.add(parent, file, lazy=not open, callback=callback)
            # Paths second
            for path in sorted( [key for key in curr.keys() if len(curr[key]) > 0] ):
                if callback: callback()
                print("- Path:",path)
                full_path = os.path.join(parent.extract_to,path)
                node = self.add(parent, full_path, lazy=not open, callback=callback)
                if node:
                    recurs_fill(curr[path], node, depth<2)

        recurs_fill(content["\\"], node, open)


    '''
    Expand given node, updating on-the-fly if lazy open was used
    '''
    def _tree_expanding(self, node, callback=None, max_levels=1):
        assert node
        assert node.iid
        assert node.iid in self.nodes
         
        print("Node.Expand for ",node)
        childs = self.tree.childs(node.iid)
        print("  -",childs)
        if len(childs) == 1 and childs[0].endswith("/dummy"):
            self.tree.delete(childs)
            self.tree_populate(node, True, callback, max_levels)
        
