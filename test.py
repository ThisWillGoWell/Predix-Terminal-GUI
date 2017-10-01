import npyscreen
import app_utils

npyscreen.disableColor()


class TestApp(npyscreen.NPSApp):
    def main(self):
        self.logger = app_utils.logger
        F = npyscreen.Form(name="Testing Tree class", )
        wgtree = F.add(npyscreen.MLTreeAction)
        #wgtree = F.add(npyscreen.TreeData)
        self.F = F

        """
        treedata = npyscreen.TreeData(content='Parent', selectable=True)

        self.treedata = treedata
        c1 = treedata.new_child(content='Child 1', selectable=True, selected=True)
        c1.expanded = False
        c2 = treedata.new_child(content='Child 2', selectable=True)
        g1 = c1.new_child(content='Grand-child 1', selectable=True)
        g2 = c1.new_child(content='Grand-child 2', selectable=True)
        g3 = c1.new_child(content='Grand-child 3')
        gg1 = g1.new_child(content='Great Grand-child 1', selectable=True)
        gg2 = g1.new_child(content='Great Grand-child 2', selectable=True)
        gg3 = g1.new_child(content='Great Grand-child 3')
       
        """

        treeDic = {
            'root': {'child1': {'grandChild1': ['ele1', 'ele2', {'ele3dic':'Yeah'}]}, 'child2' : 420}
        }
        treedata = app_utils.dictToTreeData(treeDic)

        wgtree.values = treedata
        wgtree.actionHighlighted = self.toggleExpand
        self.wgtree = wgtree

        F.edit()




    def toggleExpand(self, act_on_this, key_press):
        if isinstance( act_on_this, npyscreen.TreeData):
            self.logger.log("Start")
            act_on_this.expanded =  not act_on_this.expanded

            self.wgtree.display()








if __name__ == "__main__":
    App = TestApp()
    App.run()



