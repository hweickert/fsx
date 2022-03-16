import os


def get_leaf_dirs(tree):
    res = []
    for root, dir_nodes, _ in tree.walk_nodes():
        if not dir_nodes:
            res.append(root)
    return res

def get_files(tree):
    res = []
    for root, _, file_nodes in tree.walk_nodes():
        for file_node in file_nodes:
            res.append(root + '/' + file_node.name)
    return res


def store(tree, path):
    ''' Stores `tree` and it's contents on the file system under `path`. '''

    # create directories
    for p in sorted(get_leaf_dirs(tree)):
        store_path = path + '/' + p
        try:
            os.makedirs(store_path)
        except:
            pass

    # store files
    for root, dir_nodes, file_nodes in tree.walk_nodes():
        for file_node in file_nodes:
            store_path = path + '/' + root + '/' + file_node.name

            with open(store_path, 'w') as file_:
                file_node.io.seek(0)
                file_.write(file_node.io.read())
                file_node.io.seek(0)

