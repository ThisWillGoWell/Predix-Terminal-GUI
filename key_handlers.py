import app_utils
class KeyHandelers:
    def __init__(self):
        self.keyHandlers = {}
        self.notify = self.notifyPress
        self.keyHandlers[ord('q')] = self.qKeyPressed
        self.keyHandlers[ord('w')] = self.wKeyPressed
        self.keyHandlers[ord('e')] = self.eKeyPressed
        self.keyHandlers[ord('r')] = self.rKeyPressed
        self.keyHandlers[ord('t')] = self.tKeyPressed
        self.keyHandlers[ord('y')] = self.yKeyPressed
        self.keyHandlers[ord('u')] = self.uKeyPressed
        self.keyHandlers[ord('i')] = self.iKeyPressed
        self.keyHandlers[ord('o')] = self.oKeyPressed
        self.keyHandlers[ord('p')] = self.pKeyPressed
        self.keyHandlers[ord('a')] = self.aKeyPressed
        self.keyHandlers[ord('s')] = self.sKeyPressed
        self.keyHandlers[ord('d')] = self.dKeyPressed
        self.keyHandlers[ord('f')] = self.fKeyPressed
        self.keyHandlers[ord('g')] = self.gKeyPressed
        self.keyHandlers[ord('h')] = self.hKeyPressed
        self.keyHandlers[ord('j')] = self.jKeyPressed
        self.keyHandlers[ord('k')] = self.kKeyPressed
        self.keyHandlers[ord('l')] = self.lKeyPressed
        self.keyHandlers[ord('z')] = self.zKeyPressed
        self.keyHandlers[ord('x')] = self.xKeyPressed
        self.keyHandlers[ord('c')] = self.cKeyPressed
        self.keyHandlers[ord('v')] = self.cKeyPressed
        self.keyHandlers[ord('b')] = self.vKeyPressed
        self.keyHandlers[ord('m')] = self.mKeyPressed
        self.keyHandlers[ord('n')] = self.nKeyPressed


    def notifyPress(self, ch):
        app_utils.logger.log(ch)

    def qKeyPressed(self):
        self.notify(ord('q'))

    def wKeyPressed(self):
        self.notify(ord('w'))

    def eKeyPressed(self):
        self.notify(ord('e'))

    def rKeyPressed(self):
        self.notify(ord('r'))

    def tKeyPressed(self):
        self.notify(ord('t'))

    def yKeyPressed(self):
        self.notify(ord('y'))

    def uKeyPressed(self):
        self.notify(ord('u'))

    def iKeyPressed(self):
        self.notify(ord('i'))

    def oKeyPressed(self):
        self.notify(ord('o'))

    def pKeyPressed(self):
        self.notify(ord('p'))

    def lKeyPressed(self):
        self.notify(ord('a'))

    def jKeyPressed(self):
        self.notify(ord('s'))

    def kKeyPressed(self):
        self.notify(ord('d'))

    def hKeyPressed(self):
        self.notify(ord('f'))

    def gKeyPressed(self):
        self.notify(ord('g'))

    def fKeyPressed(self):
        self.notify(ord('h'))

    def dKeyPressed(self):
        self.notify(ord('j'))

    def sKeyPressed(self):
        self.notify(ord('k'))


    def aKeyPressed(self, value):
        self.notify(ord('l'))

    def zKeyPressed(self):
        self.notify(ord('z'))

    def xKeyPressed(self):
        self.notify(ord('x'))

    def cKeyPressed(self):
        self.notify(ord('c'))

    def vKeyPressed(self):
        self.notify(ord('v'))

    def bKeyPressed(self):
        self.notify(ord('b'))

    def nKeyPressed(self):
        self.notify(ord('n'))

    def mKeyPressed(self):
        self.notify(ord('m'))



