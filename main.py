
import Filesystem
def main():
    # make a system object to handle inputs
    sys = Filesystem.System()
    
    # continues asking for inputs
    while True:
        cmd = input(sys.user.name+":"+sys.work_dir+"$ ")
        
        # call appropriate functions for different commands
        sys.execute(cmd)

if __name__ == '__main__':
	main()
