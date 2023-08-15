class Node:
    '''Represent files and folders'''
    def __init__(self,name,type,owner,path):
        '''Constructing attributes for node object'''
        self.name = name
        self.owner = owner
        self.abs_path = path
        self.parent = None
        self.children = []
        if type == "file":
            self.permission = "-rw-r--"
        if type == "dir":
            self.permission = "drwxr-x"

    def add_child(self, node):
        '''Connect a parent node and child node'''
        self.children.append(node)
        node.parent = self
    
    def remove_child(self, node):
        '''Remove connection between parent and child node'''
        self.children.remove(node)
        node.parent = None

    def isFile(self):
        '''Check if is a node is file'''
        return list(self.permission)[0] == "-"

    def isDir(self):
        '''Check if is a node is directory'''
        return list(self.permission)[0] == "d"