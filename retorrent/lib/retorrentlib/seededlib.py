import os

def is_seeded(args):
    seeddir=os.path.expanduser('~/seed')
    seed_map = [ (root,dirs,files) for root, dirs, files in os.walk(seeddir, followlinks=True) ] 
    
    seed_filepaths = []
    
    for root,dir,files in seed_map:
        # build a flat list of the defeferenced symlinks. 
        seed_filepaths.append(os.path.realpath(root))
        seed_filepaths.extend([os.path.realpath(os.path.join(root,file)) for file in files])    
    
    seeded = []
    unseeded = []
    for arg in args:
        if is_seeded_singleitem(arg,seed_filepaths):
            seeded += [arg]
        else:
            unseeded += [arg]
    
    return seeded,unseeded

# Passed a file -> Somewhere in seed is a symlink to that file
# Passed a dir ->     1./ Somewhere in seed is a symlink to that dir
#                    2./ Somewhere in seed is a symlink to the dir's contents
def is_seeded_singleitem(path, seed_filepaths):
    the_path = os.path.realpath(path)

    for each_file in seed_filepaths:
        if the_path in each_file: 
            return True 

    # let's now look at dir contents
    if os.path.isdir(the_path):
        for each_dir in os.listdir(the_path):
            if is_seeded_singleitem(\
                    os.path.join(the_path, each_dir),seed_filepaths):
                return True
    return False 

