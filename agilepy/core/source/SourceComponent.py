class SourceComponent:

    def __init__(self):
        pass

    def getFreeParams(self):
        fp = []
        attributes = vars(self)
        for name, dictionary in attributes.items():
            if "free" in dictionary and dictionary["free"]:
                fp.append(name)
        return fp

    def getFreeableParams(self):
        fp = []
        attributes = vars(self)
        for name, dictionary in attributes.items():
            if "free" in dictionary:
                fp.append(name)
        return fp

    def get(self, paramName):
        return getattr(self, paramName)

    def getVal(self, paramName, strr=False):
        if strr:
            return str(getattr(self, paramName)["value"])
        else:
            return getattr(self, paramName)["value"]

    def getType(self):
        return type(self).__name__        