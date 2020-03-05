from pathlib import Path
import sys


def is_git_repo(folder_path):
    """
    Return True if folder contains a .git folder
    """
    return Path(folder_path).joinpath('.git').is_dir()


def find_bigfiles(data_folder, gte_size=100, verbose=False):
    """
    Return a list of file paths (truncated from the name 
    part of data_folder.name) for all file exceeding 
    gte_size MB.
    gte_size: multiple of 1 MB => 100 MB default.
           :: github file size limit = 100 * 2^20
    """
    if gte_size == 0:
        print('No file size limit: gte_size=0.')
        return

    mb = 2**20  #kb = 2**10   #gb = 2**30
    size_limit = gte_size *  mb
    
    out = []
    p = Path(data_folder)
    
    # output only parts from data_folder name, i.e.: data/file.csv
    for f in p.glob('**/*.*'):
        if f.stat().st_size >= size_limit:
            parent_idx = f.parts.index(p.name)
            fout = '/'.join(f for f in f.parts[parent_idx:])
            out.append(fout)
            
            if verbose: print(f, '\t', f.stat().st_size)
    return out


def update_git_info_exclude(top_folder_path, data_folder_name):
    """Update the $GIT_DIR/info/exclude file with path of
       found big files, so that separate .gitignore file
       stays generic (portable).
    """
    import sys
    
    repo = Path(top_folder_path)
    if not is_git_repo(repo):
        msg = f'Folder: {top_folder_path} is not a repo.'
        msg += '\nType `>git init .` to initialize.'
        print(msg)
        return

    data_folder = repo.joinpath(data_folder_name)
    bigones = find_bigfiles(data_folder)
    if len(bigones) == 0:
        print(f'No GitHub big files (>= 100 MB) found in {data_folder}.')
        return
    
    git_exclude = repo.joinpath('.git', 'info', 'exclude')

    with git_exclude.open(mode='r+') as fh:
        content = [line.strip('\n') for line in fh.readlines()]
        for fname in bigones:
            if fname not in content:
                n = fh.write('\n' + fname)
                
    msg = 'Updated .git/info/exclude file.\n'            
    if 'ipykernel_launcher.py' in sys.argv[0]:               
        msg += 'Enter `%load .git/info/exclude` in a cell to verify.'
    print(msg)
    return


def test_ipkernel(verbose=False):
    found = 'ipykernel_launcher.py' in sys.argv[0]
    if verbose:
        verb = 'IS' if found else 'IS NOT'
        msg = f'Code *{verb}* running in Jupyter platform (notebook, lab, etc.)'       
        print(msg)
    return found