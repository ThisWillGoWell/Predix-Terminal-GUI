import json

from npyscreen import TreeData

import os
def get_pretty_print(json_object):
    return json.dumps(json_object, sort_keys=True, indent=4, separators=(',', ': '))

def dictToTreeData( dictionary):
    baseNode = TreeData()
    baseNode.content = 'name'
    dictToTreeDataHelper(dictionary, baseNode)

    return baseNode

def dictToTreeDataHelper(  dictionary, parent):
    parent.name = json.dumps(dictionary)
    for key, value in dictionary.iteritems():
        child = parent.new_child()

        if isinstance(value, dict):
            child.set_content(key)
            dictToTreeDataHelper(value, child)

        elif isinstance(value, list):
            child.set_content(key)
            listToTreeDataHelper(value, child)

        else:
            child.name = str(value)
            child.set_content(key + ":\t" + str(value))



def listToTreeDataHelper( array, parent):
    parent.name = str(array)
    for ele in array:
        if isinstance(ele, dict):
            dictToTreeDataHelper(ele, parent)
        elif isinstance(ele, list):
            child =  parent.new_child()
            child.set_content(str(array))
            listToTreeDataHelper(array, child)
        else:
            child = parent.new_child()
            child.name = str(ele)
            child.set_content(str(ele))


def copyToClipboard(string):
    os.system("echo '%s' | pbcopy" % string)


class LogToFile:

    def log(self, value):
        f = open('log.txt', 'w')
        f.write(str(value) + '\n')
        f.close()


logger = LogToFile()