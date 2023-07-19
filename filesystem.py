class User:
    '''Represents user'''
    def __init__(self,name):
        self.name = name


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

class System:
    '''Represents the tree keeping track of node's status
    as well as taking commands from users'''
    def __init__(self):
        '''Construct initial attributes'''
        root = Node("/","dir",User("root"),"/")
        self.root = root
        self.work_dir = "/"
        self.user = User("root")
        self.users = [self.user]
        self.nodes = [self.root]
        self.abs_paths = ["/"]
    
    def put(self, parent_node, child_node):
        parent_node.add_child(child_node)

    def unput(self, parent_node, child_node):
        parent_node.remove_child(child_node)

    def get_node(self,name):
        for node in self.nodes:
            if node.name == name:
                return node

    def refine_path(self,path):
        '''Take the path inputed by user and convert to an absolute path for return'''
        # check if the given path is already an absolute path
        if not list(path)[0] == "/":
            if self.work_dir != "/":
                path = self.work_dir + "/" + path
            else:
                path = self.work_dir + path
        path2 = list(path)
        j = 0
        for st in path2:
            if st.isalnum():
                j += 1
        if j == 0:
            return "/"
        
        # handle . and ..
        f = path.split("/")
        while "." in f:
            f.remove(".")
        while ".." in f:
            if f[f.index("..")-1] != "":
                f.remove(f[f.index("..")-1])
            f.remove(f[f.index("..")])
        if f == ['']:
            return "/"
        return "/".join(f)
    
    def get_perm(self,path):
        '''Return permission list for current user'''
        path = self.refine_path(path)
        node = self.nodes[self.abs_paths.index(path)]
        perm = node.permission
        perm = list(perm)
        if self.user == node.owner:
            return perm[1:4]
        else:
            return perm[4:7]
    
    def path_exist(self,path):
        for p in self.abs_paths:
            if p == path:
                return True
        return False        

    def isFile(self,path):
        node = self.nodes[self.abs_paths.index(path)]
        return node.isFile()

    def isDir(self,path):
        node = self.nodes[self.abs_paths.index(path)]
        return node.isDir()
    
    def exist_user(self,user):
        for u in self.users:
            if u.name == user:
                return True
        return False
    
    def find_user(self,user):
        for u in self.users:
            if u.name == user:
                return u
    
    def adduser(self,name):
        '''Add an user'''
        if self.user.name == "root":
            if self.exist_user(name):
                print("adduser: The user already exists")
                return
            self.users.append(User(name))
        else:
            print("adduser: Operation not permitted")
    
    def deluser(self,name):
        '''Delete an user'''
        if self.user.name == "root":
            if not self.exist_user(name):
                print("deluser: The user does not exist")
                return
            if name == "root":
                print('''WARNING: You are just about to delete the root account
Usually this is never required as it may render the whole system unusable
If you really want this, call deluser with parameter --force
(but this `deluser` does not allow `--force`, haha)
Stopping now without having performed any action''')
                return
            user = self.find_user(name)
            self.users.remove(user)
        else:
            print("deluser: Operation not permitted")
    
    def su(self,name):
        '''Switch to another user'''
        if name == "":
            self.user = User("root")
            return
        if not self.exist_user(name):
            print("su: Invalid user")
            return
        self.user = self.find_user(name)

    def exit(self):
        '''Exit the program'''
        print("bye, {}".format(self.user.name))
        quit()

    def pwd(self):
        '''Print current directory'''
        print(self.work_dir)

    def cd(self, dir_path):
        '''Change directory'''
        dir_path = self.refine_path(dir_path)
        if not self.path_exist(dir_path):
            print("cd: No such file or directory")
            return
        if self.isFile(dir_path):
            print("cd: Destination is a file")
            return
        if self.user.name != "root":
            # check permission
            if self.get_perm(dir_path)[2] != "x":
                print("cd: Permission denied")
                return
        for path in self.abs_paths:
            if path == dir_path:
                # change the directory
                self.work_dir = path
                return
    
    def find_parent(self, path):
        '''Find the parent of a node given an absolute path, return a node'''
        path = path.split("/")
        # since splitting "/" returns ["",""]
        if len(path) == 2:
            return self.root
        # parent is the second last element
        parent = path[-2]
        for node in self.nodes:
            if node.name == parent:
                return node
    
    def find_existing_parent(self,dir_path):
        '''Find the number of existing ancestors of an absolute path, return an integer'''
        common = []
        dir_path = dir_path.split("/")
        while "" in dir_path:
            dir_path.remove("")
        # check for every absolute path in the system
        for path in self.abs_paths:
            path = path.split("/")
            path.remove("")
            i = 0
            j = len(path) if (len(path) <= len(dir_path)) else len(dir_path)
            while i < j:
                # if there is a folder that has the same name, increase i
                if path[i] == dir_path[i] and self.isDir(self.get_node(path[i]).abs_path):
                    i += 1
                else:
                    break
            common.append(i)
        # find the number of existing ancestors
        biggest = 0
        for com in common:
            if com > biggest:
                biggest = com
        return biggest

    def get_descendant(self,node):
        '''Given an existing node in the system, return a list of it's children nodes'''
        ls = []
        if len(node.children) != 0:
            for child in node.children:
                ls.append(child)
                ls.extend(self.get_descendant(child))
        if len(node.children) == 0:
            return ls
        return ls

    def ancestor_exist(self,dir_path):
        '''Check if all ancestors exist'''
        dir_path = self.refine_path(dir_path)
        biggest = self.find_existing_parent(dir_path)
        dir_path = dir_path.split("/")
        dir_path.remove("")
        # since this can be used for making new directory, 1 can be accepted
        if len(dir_path) - biggest > 1:
            return False
        return True

    def get_path(self,dir_path,index):
        '''Get a path from a given path depending on given index'''
        dir_path = dir_path.split("/")
        # remove directory name from the given index
        while index < len(dir_path) - 1:
            dir_path.remove(dir_path[index+1])
        dir_path = "/".join(dir_path)
        return dir_path

    def check_ancestor_perm(self,cmd,ancestor_bit,parent_bit,dir_path):
        '''Check if user has the given permission for ancestor directories, return a boolean'''
        if self.user.name == "root":
            return True
        if self.user.name != "root":
            # the directory is root (eg someuser:/$ ls )
            if dir_path == "/":
                if parent_bit in self.get_perm("/") and ancestor_bit in self.get_perm("/"):
                    return True
            if self.ancestor_exist(dir_path):
                ancestor = dir_path.split("/")
                ancestor.remove("")
                i = 0
                # length of 1 means that the file/directory is child of root
                if len(ancestor) == 1:
                    if parent_bit in self.get_perm("/") and ancestor_bit in self.get_perm("/"):
                        return True
                    print("{}: Permission denied".format(cmd))
                    return False
                else:
                    # check for ancestor permission
                    # i < len(ancestor) - 2 since the parent is excluded for checking parent_bit
                    while i < len(ancestor) - 2:
                        node = self.get_node(ancestor[i])
                        if not ancestor_bit in self.get_perm(node.abs_path):
                            print("{}: Permission denied".format(cmd))
                            return False
                        i += 1
                    # check for parent permission
                    parent = self.get_node(ancestor[-2])
                    if not ancestor_bit in self.get_perm(parent.abs_path):
                        print("{}: Permission denied".format(cmd))
                        return False
                    if not parent_bit in self.get_perm(parent.abs_path):
                        print("{}: Permission denied".format(cmd))
                        return False
            return True
    
    def mkdir(self,flag,dir_path):
        '''Make a new directory'''
        dir_path = self.refine_path(dir_path)
        # preserve the dir_path for later use
        dir_path2 = dir_path
        if flag == False:
            if not self.path_exist(dir_path2):
                dir_path = dir_path.split("/")
                dir_path.remove("")
                if not self.ancestor_exist(dir_path2):
                    print("mkdir: Ancestor directory does not exist")
                    return
            if self.path_exist(dir_path2):
                print("mkdir: File exists")
                return
            if not self.check_ancestor_perm("mkdir","x","w",dir_path2):
                return
            if not self.path_exist(dir_path2):
                dir_path = dir_path2.split("/")
                dir_path.remove("")

                # make a new node of type directory with the name being the
                # last element of given path
                new_dir = Node(dir_path[-1],"dir",self.user,dir_path2)

                # add the absolute path of new directory to system
                self.abs_paths.append(new_dir.abs_path)
                    
                # add the new node object to system
                self.nodes.append(new_dir)
                    
                # find the parent of the new node based on given path
                # and connect them 
                parent = self.find_parent(new_dir.abs_path)
                self.put(parent,new_dir)
        else:
            # if flagged, then recursively make new nodes
            if not self.path_exist(dir_path):
                dir_path = dir_path.split("/")
                dir_path.remove("")

                # all ancestors exist
                if len(dir_path) - self.find_existing_parent(dir_path2) == 1:
                    new_dir = Node(dir_path[-1],"dir",self.user,dir_path2)
                    self.abs_paths.append(new_dir.abs_path)
                    self.nodes.append(new_dir)
                    parent = self.find_parent(new_dir.abs_path)
                    self.put(parent,new_dir)
                # any of ancestors in the path do not exist
                else:
                    # recursively create new nodes and connect them
                    i = self.find_existing_parent(dir_path2)
                    while i < len(dir_path):
                        name = dir_path[i]
                        new_dir = Node(name,"dir",self.user,self.get_path(dir_path2,i+1))
                        self.abs_paths.append(new_dir.abs_path)
                        self.nodes.append(new_dir)
                        parent = self.find_parent(new_dir.abs_path)
                        self.put(parent,new_dir)
                        i += 1
    
    def rmdir(self,dir_path):
        ''' Remove an empty directory'''
        dir_path = self.refine_path(dir_path)
        if not self.path_exist(dir_path):
            print("rmdir: No such file or directory")
            return
        if not self.isDir(dir_path):
            print("rmdir: Not a directory")
            return
        dir = self.nodes[self.abs_paths.index(dir_path)]
        if len(dir.children)>0:
            print("rmdir: Directory not empty")
            return
        if self.work_dir == dir_path:
            print("rmdir: Cannot remove pwd")
            return
        if not self.check_ancestor_perm("rmdir","x","w",dir_path):
            return
        # find the parent and disconnect it from the child(the deleted one)
        parent = self.find_parent(dir.abs_path)
        self.unput(parent,dir)
        
        # remove its absolute path and nodes from the system
        self.abs_paths.remove(dir.abs_path)
        self.nodes.remove(dir)

    def touch(self,file_path):
        '''Make a new file'''
        file_path = self.refine_path(file_path)
        # preserve file_path
        file2 = file_path
        if not self.path_exist(file_path):
            file2 = file2.split("/")
            while "" in file2:
                file2.remove("")
            if len(file2) - self.find_existing_parent(file_path) > 1:
                print("touch: Ancestor directory does not exist")
                return
        if not self.check_ancestor_perm("touch","x","w",file_path):
            return
            # this is similar to making a new directory, except
            # this time the new node is of type file
        new_file = Node(file2[-1],"file",self.user,file_path)
        self.abs_paths.append(new_file.abs_path)
        self.nodes.append(new_file)
        parent = self.find_parent(new_file.abs_path)
        self.put(parent,new_file)

    def rm(self,file_path):
        '''Remove a file given its path'''
        file_path = self.refine_path(file_path)
        if not self.path_exist(file_path):
            print("rm: No such file")
            return
        if self.isDir(file_path):
            print("rm: Is a directory")
            return
        if not self.check_ancestor_perm("rm","x","w",file_path):
            return
        if self.user.name != "root":
            # check permission of user on this file
            if not "w" in self.get_perm(file_path):
                print("rm: Permission denied")
                return
        
        # this is similar to deleting a directory
        file = self.nodes[self.abs_paths.index(file_path)]
        self.abs_paths.remove(file.abs_path)
        self.nodes.remove(file)
        parent = self.find_parent(file.abs_path)
        self.unput(parent,file)

    def cp(self,src,dst):
        '''Copying a file to another location'''
        src = self.refine_path(src)
        dst = self.refine_path(dst)
        if not self.path_exist(src):
            print("cp: No such file")
            return
        if self.path_exist(dst):
            if self.isFile(dst):
                print("cp: File exists")
                return
            if self.isDir(dst):
                print("cp: Destination is a directory")
                return
        if self.isDir(src):
            print("cp: Source is a directory")
            return
        if not self.ancestor_exist(dst):
            print("cp: No such file or directory")
            return
        if not "r" in self.get_perm(src):
            print("cp: Permission denied")
            return
        if not self.check_ancestor_perm("cp","x","x",src):
            return
        if not self.check_ancestor_perm("cp","x","w",dst):
            return

        # after all erroes are passed, make a new file at the destination
        self.touch(dst)

    def mv(self,src,dst):
        '''Move a file to another location'''
        src = self.refine_path(src)
        dst = self.refine_path(dst)
        if not self.path_exist(src):
            print("mv: No such file")
            return
        if self.path_exist(dst):
            if self.isFile(dst):
                print("mv: File exists")
                return
            if self.isDir(dst):
                print("mv: Destination is a directory")
                return
        if self.isDir(src):
            print("mv: Source is a directory")
            return
        if not self.ancestor_exist(dst):
            print("mv: No such file or directory")
            return
        if not self.check_ancestor_perm("mv","x","w",src):
            return
        if not self.check_ancestor_perm("mv","x","w",dst):
            return
        # make a new file at the destination as well as remove the old one at the source
        self.touch(dst)
        self.rm(src)

    def chown(self,flag,user,path):
        '''Change the owner of a directory'''
        path = self.refine_path(path)
        if not self.exist_user(user):
            print("chown: Invalid user")
            return
        if not self.path_exist(path):
            print("chown: No such file or directory")
            return
        if not self.user.name == "root":
            print("chown: Operation not permitted")
            return
        # find the node associated with given path, change it's owner
        node = self.nodes[self.abs_paths.index(path)]
        user = self.find_user(user)
        node.owner = user
        
        # when the flag is inputted, change the owner the node's descendants
        if flag:
            descendant = self.get_descendant(node)
            for des in descendant:
                des.owner = user

    def chmod(self,flag,mode,path):
        path = self.refine_path(path)
        if not flag:
            mode_list = list(mode)
            uoa_list = ["u","o","a"]
            rwx_list = ["r","w","x"]
            sign= ["-","+","="]
            i = 0
            # check for valid number of signs in inputted mode
            for string in mode_list:
                if string in sign:
                    i += 1
            if i != 1:
                print("chmod: Invalid mode")
                return

            # find index of the sign to seperate uoa and rwx            
            for string in mode_list:
                if string in sign:
                    i = mode_list.index(string)
            uoa = mode_list[0:i]
            rwx = mode_list[i+1:len(mode_list)]
    
            if len(uoa) == 0:
                return
            # check for valid string in uoa and rwx
            for string in uoa:
                if not string in uoa_list:
                    print("chmod: Invalid mode")
                    return
            for string in rwx:
                if not string in rwx_list:
                    print("chmod: Invalid mode")
                    return
            # make element of those lists unique
            uoa = list(dict.fromkeys(uoa))
            rwx = list(dict.fromkeys(rwx))
            if not self.path_exist(path):
                print("chmod: No such file or directory")
                return
            if self.user.name != "root" and self.user.name != self.owner(path):
                print("chmod: Operation not permitted")
                return
            if not self.check_ancestor_perm("chmod","x","x",path):
                return
            # get the permission of the node
            node = self.nodes[self.abs_paths.index(path)]
            # perm_owner includes the bits indicating the node type(file or directory)
            perm_owner = list(node.permission)[0:4]
            perm_other = list(node.permission)[4:7]
            
            # if the sign is -
            if mode_list[i] == "-":
                if "u" in uoa:
                    for string in rwx:
                        if string in perm_owner:
                            perm_owner[perm_owner.index(string)] = "-"
                if "o" in uoa:
                    for string in rwx:
                        if string in perm_other:
                            perm_other[perm_other.index(string)] = "-"
                # change both for owner and other
                if "a" in uoa:
                    for string in rwx:
                        if string in perm_owner:
                            perm_owner[perm_owner.index(string)] = "-"
                    for string in rwx:
                        if string in perm_other:
                            perm_other[perm_other.index(string)] = "-"
            # if the sign is + , simply add mentioned bits to appropriate permission list
            if mode_list[i] == "+":
                if "u" in uoa:
                    for string in rwx:
                        if string == "r":
                            perm_owner[1]="r"
                        if string == "w":
                            perm_owner[2]="w"
                        if string == "x":
                            perm_owner[3] = "x"
                if "o" in uoa:
                    for string in rwx:
                        if string == "r":
                            perm_other[0]="r"
                        if string == "w":
                            perm_other[1]="w"
                        if string == "x":
                            perm_other[2] = "x"
                if "a" in uoa:
                    for string in rwx:
                        if string == "r":
                            perm_owner[1] = "r"
                            perm_other[0] = "r"
                        if string == "w":
                            perm_owner[2] = "w"
                            perm_other[1] = "w"
                        if string == "x":
                            perm_owner[3] = "x"
                            perm_other[2] = "x"
            # since - can not be in rwx, if sign is = and
            # rwx lacks any bits, erase that bit and set the mentioned bits
            if mode_list[i] == "=" and len(rwx) != 0:
                if "u" in uoa:
                    if node.isDir():
                        perm_owner=["d","-","-","-"]
                    else:
                        perm_owner=["-","-","-","-"]
                    for string in rwx:
                        if string == "r":
                            perm_owner[1] = "r"
                        if string == "w":
                            perm_owner[2] = "w"
                        if string == "x":
                            perm_owner[3] = "x"
                if "o" in uoa:
                    perm_other=["-","-","-"]
                    for string in rwx:
                        if string == "r":
                            perm_other[0] = "r"
                        if string == "w":
                            perm_other[1] = "w"
                        if string == "x":
                            perm_other[2] = "x"
                if "a" in uoa:
                    if node.isDir():
                        perm_owner=["d","-","-","-"]
                    else:
                        perm_owner=["-","-","-","-"]
                    perm_other=["-","-","-"]
                    for string in rwx:
                        if string == "r":
                            perm_owner[1] = "r"
                            perm_other[0] = "r"
                        if string == "w":
                            perm_owner[2] = "w"
                            perm_other[1] = "w"
                        if string == "x":
                            perm_owner[3] = "x"
                            perm_other[2] = "x"
            # if the sign is = and rwx is empty, erase the bits
            if mode_list[i] == "=" and len(rwx) == 0:
                if "u" in uoa:
                    if node.isDir():
                        perm_owner = ["d","-","-","-"]
                    else:
                        perm_owner = ["-","-","-","-"]
                if "o" in uoa:
                    perm_other = ["-","-","-"]
                if "a" in uoa:
                    if node.isDir():
                        perm_owner = ["d","-","-","-"]
                    else:
                        perm_owner = ["-","-","-","-"]
                    perm_other = ["-","-","-"]
            
            # join perm_other and perm_owner to assign as the new
            # permission attribute of the node
            perm_owner.extend(perm_other)
            new_perm = "".join(perm_owner)
            node.permission = new_perm
        
        # if flagged, then do chmod with no flag for the node and it's descendants
        if flag:
            node = self.nodes[self.abs_paths.index(path)]
            self.chmod(False,mode,node.abs_path)
            descendant = self.get_descendant(node)
            for des in descendant:
                self.chmod(False,mode,des.abs_path)
    
    def ls(self,flag,path):
        '''List the information of given directory'''
        # if no path is inputted, then list the information of current directory
        if path == "":
            path = self.work_dir
        path = self.refine_path(path)
        if not self.path_exist(path):
            print("ls: No such file or directory")
            return
        if self.isDir(path):
            if self.user.name != "root":
                if not "r" in self.get_perm(path):
                    print("ls: Permission denied")
                    return
        if self.isFile(path) or "-d" in flag:
            parent=self.find_parent(path)
            if self.user.name != "root":
                if not "r" in self.get_perm(parent.abs_path):
                    print("ls: Permission denied")
                    return
        if not self.check_ancestor_perm("ls","x","x",path):
            return

        node = self.nodes[self.abs_paths.index(path)]
        name = list(node.name)
        result = node.name

        if self.isFile(path):
            if "-l" in flag:
                perm = node.permission
                owner = node.owner.name
                name = node.name
                result = perm + " " + owner + " " + name
            if not "-a" in flag:
                if name[0] != ".":
                    print(result)
            if "-a" in flag:
                print(result)
                return
        
        if self.isDir(path):
            # list information of directory itself
            if "-d" in flag:
                if "-l" in flag:
                    perm = node.permission
                    owner = node.owner.name
                    name = node.name
                    result = perm + " " + owner + " " + name
                # ignore entries starting with "."
                if not "-a" in flag:
                    if name[0] != ".":
                        print(result)
                        return
                if "-a" in flag:
                    print(result)
                    return
            # list the children of directory
            if not "-d" in flag:
                # result contains the names
                result = []
                for child in node.children:
                    result.append(child.name)
                # sort the name
                result = sorted(result)
                if not "-a" in flag:
                    for name in result:
                        if list(name)[0] == ".":
                            result.remove(name)
                if "-l" in flag:
                    for name in result:
                        if path != "/":
                            node = self.nodes[self.abs_paths.index(path+"/"+name)]
                        else:
                            node = self.nodes[self.abs_paths.index(path+name)]
                        perm = node.permission
                        owner = node.owner.name
                        print(perm + " " + owner + " " + name)
                    return
                if not "-l" in flag:
                    for name in result:
                        print(name)
                    return

    def owner(self,path):
        '''Return owner name of a path'''
        path = self.refine_path(path)
        node = self.nodes[self.abs_paths.index(path)]
        user = node.owner
        return user.name

    def remove_quotation(self,string):
        string = list(string)
        while '"' in string:
            string.remove('"')
        string = "".join(string)
        return string

    def is_valid(self,string):
        '''Check if a string is valid'''
        valid = 'qwertyuiopasdfghjklzxcvbnm'
        valid += 'QWERTYUIOPASDFGHJKLZXCVBNM123456789"/ -._'
        valid = list(valid)
        string = list(string)
        for st in string:
            if st not in valid:
                return False
        # check if arguments with space are surrounded by ""
        if " " in string:
            if string[0] != '"' or string[len(string)-1] != '"':
                return False
        return True
    
    def split(self,cmd):
        '''Split the command given by user to valid arguments'''
        # initiate i as a random number
        i = -100
        # get rid of tabs
        cmd = cmd.replace("\t","")
        cmd = cmd.split(" ")
        to_be_removed = []
        while "" in cmd:
            cmd.remove("")
        # store flags that are repeated more than once in to_be_removed
        for st in cmd:
            if cmd.count(st) > 1 and "-" in st:
                to_be_removed.append(st)
        # keep only one unique flag
        for st in to_be_removed:
            while cmd.count(st) > 1:
                cmd.remove(st)
        # find the index of '"' in cmd
        for st in cmd:
            if '"' in st:
                i = cmd.index(st)
                break
        # this means there are '"' in the command since i has changed
        # thus concatenating strings between the quotation marks as one argument
        if i != -100:
            j = i
            last_st = ""
            while i < len(cmd) - 1:
                last_st += cmd[i] + " "
                i += 1
            last_st += cmd[i]
            cmd[j] = last_st
            # get the list of command arguments
            cmd = cmd[0:j+1]
        return cmd

    def execute(self,cmd):
        '''Handle the input and call to appropriate functions for different commands'''
        # if user does not input anything
        if cmd == "":
            return
        # if user only inputs spaces
        if cmd.isspace():
            return
        # get the command list
        cmd = self.split(cmd)
        length = len(cmd)

        # list of valid commands
        valid_cmd = ["exit","cd","mkdir","pwd","touch","cp","mv","rm"]
        valid_cmd.extend(["rmdir","chmod","chown","adduser","deluser","su","ls"])
        if not cmd[0] in valid_cmd:
            print("{}: Command not found".format(cmd[0]))
            return
        if cmd[0] == "exit":
            if length > 1:
                print("{}: Invalid syntax".format(cmd[0]))
                return
            self.exit()
        if cmd[0] == "pwd":
            if length > 1:
                print("{}: Invalid syntax".format(cmd[0]))
                return
            self.pwd()
        # remove all quotation marks for path, user name
        # before calling the function 
        if cmd[0] == "cd":
            # cd commands must have exactly 2 arguments
            # which are "cd" and a valid directory name 
            if length == 2 and self.is_valid(cmd[1]):
                self.cd(self.remove_quotation(cmd[1]))
            if length != 2 or not self.is_valid(cmd[1]):
                print("{}: Invalid syntax".format(cmd[0]))
        if cmd[0] == "mkdir":
            # mkdir can only have 2 or 3 arguments since
            # flag is optional
            if length == 2:
                # length is 2 means there must be no flags
                if not self.is_valid(cmd[1]):
                    print("{}: Invalid syntax".format(cmd[0]))
                    return
                self.mkdir(False,self.remove_quotation(cmd[1]))
                return
            if length == 3:
                # there is a flag 
                if not "-p" in cmd[1] or not self.is_valid(cmd[2]):
                    print("{}: Invalid syntax".format(cmd[0]))
                self.mkdir(True,self.remove_quotation(cmd[2]))
            if length != 3 and length !=2:
                print("{}: Invalid syntax".format(cmd[0]))
        if cmd[0] == "touch":
            # same as cd
            if length == 2 and self.is_valid(cmd[1]):
                self.touch(self.remove_quotation(cmd[1]))
            if length != 2 or not self.is_valid(cmd[1]):
                print("{}: Invalid syntax".format(cmd[0]))
        if cmd[0] == "cp":
            # cp must have exactly 3 arguments and path names must be valid
            if length == 3 and self.is_valid(cmd[1]) and self.is_valid(cmd[2]):
                self.cp(self.remove_quotation(cmd[1]),self.remove_quotation(cmd[2]))
            if length != 3 or not self.is_valid(cmd[1]) or not self.is_valid(cmd[2]):
                print("{}: Invalid syntax".format(cmd[0]))
        if cmd[0] == "mv":
            # same as cp
            if length == 3 and self.is_valid(cmd[1]) and self.is_valid(cmd[2]):
                self.mv(self.remove_quotation(cmd[1]),self.remove_quotation(cmd[2]))
            if length != 3 or not self.is_valid(cmd[1]) or not self.is_valid(cmd[2]):
                print("{}: Invalid syntax".format(cmd[0]))
        if cmd[0] == "rm":
            # same as cd
            if length == 2 and self.is_valid(cmd[1]):
                self.rm(self.remove_quotation(cmd[1]))
            if length != 2 or not self.is_valid(cmd[1]):
                print("{}: Invalid syntax".format(cmd[0]))
        if cmd[0] == "rmdir":
            # same as cd
            if length == 2 and self.is_valid(cmd[1]):
                self.rmdir(self.remove_quotation(cmd[1]))
            if length != 2 or not self.is_valid(cmd[1]):
                print("{}: Invalid syntax".format(cmd[0]))
        if cmd[0] == "chmod":
            if length == 3:
                # lack mode or path since the second argument is a flag
                if "-" in cmd[1] and cmd[1].index("-") ==0:
                    print("{}: Invalid syntax".format(cmd[0]))
                    return
                # this means the mode is of type uoa-rwx
                if "-" in cmd[1] and cmd[1].index("-") != 0:
                    if self.is_valid(cmd[2]):
                        self.chmod(False,cmd[1],self.remove_quotation(cmd[2]))
                    else:
                        print("{}: Invalid syntax".format(cmd[0]))
                        return
                # no flag and mode is uoa=+rwx
                if "-" not in cmd[1]:
                    if self.is_valid(cmd[2]):
                        self.chmod(False,cmd[1],self.remove_quotation(cmd[2]))
                    else:
                        print("{}: Invalid syntax".format(cmd[0]))
                        return
            if length == 4:
                # there must be a flag as length is 4
                if not "-r" in cmd[1] or not self.is_valid(cmd[3]):
                    print("{}: Invalid syntax".format(cmd[0]))
                    return
                self.chmod(True,cmd[2],self.remove_quotation(cmd[3]))
            if length != 3 and length != 4:
                print("{}: Invalid syntax".format(cmd[0]))
        if cmd[0] == "chown":
            # chown can have 3 or 4 arguments
            if length == 3 and self.is_valid(cmd[2]) and self.is_valid(cmd[1]):
                self.chown(False,self.remove_quotation(cmd[1]),self.remove_quotation(cmd[2]))
            if length == 4:
                # there must be a flag
                if not "-r" in cmd[1] or not self.is_valid(cmd[3]) or not self.is_valid(cmd[2]):
                    print("{}: Invalid syntax".format(cmd[0]))
                    return
                self.chown(True,self.remove_quotation(cmd[2]),self.remove_quotation(cmd[3]))
            if length != 3 and length != 4:
                print("{}: Invalid syntax".format(cmd[0]))
        if cmd[0] == "adduser":
            # same as cd
            if length == 2 and self.is_valid(cmd[1]):
                self.adduser(self.remove_quotation(cmd[1]))
            else:
                print("{}: Invalid syntax".format(cmd[0]))
        if cmd[0] == "deluser":
            # same as cd
            if length == 2 and self.is_valid(cmd[1]):
                self.deluser(self.remove_quotation(cmd[1]))
            else:
                print("{}: Invalid syntax".format(cmd[0]))
        if cmd[0] == "su":
            # su can have 1 or 2 arguments
            
            # if no user was inputted
            if length == 1:
                self.su("")
            if length == 2 and self.is_valid(cmd[1]):
                self.su(self.remove_quotation(cmd[1]))
            if length != 1 and length != 2:
                print("{}: Invalid syntax".format(cmd[0]))
        if cmd[0] == "ls":
            flags = []
            valid_flag = ["-a","-d","-l"]
            # check for valid flags and store them in list flags
            for st in cmd:
                if "-" in st and not st in valid_flag:
                    print("{}: Invalid syntax".format(cmd[0]))
                    return
                if "-" in st and st in valid_flag:
                    flags.append(st)
            # check if user inputted path, 1 is for the command name
            # no paths inputted
            if length - len(flags) - 1 == 0:
                self.ls(flags,"")
                return
            # path inpputed
            if length - len(flags) - 1 == 1:
                if not self.is_valid(cmd[length - 1]):
                    print("{}: Invalid syntax".format(cmd[0]))
                self.ls(flags,self.remove_quotation(cmd[length-1]))
            else:
                print("{}: Invalid syntax".format(cmd[0]))      


def main():
    # make a system object to handle inputs
    sys = System()
    
    # continues asking for inputs
    while True:
        cmd = input(sys.user.name+":"+sys.work_dir+"$ ")
        
        # call appropriate functions for different commands
        sys.execute(cmd)

if __name__ == '__main__':
	main()
