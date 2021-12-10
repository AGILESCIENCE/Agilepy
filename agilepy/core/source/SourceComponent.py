class SourceComponent:

    def __init__(self):
        pass

    def getFreeParams(self):
        fp = []
        attributes = vars(self)
        print("attributes:",attributes)
        for name, dictionary in attributes.items():
            if "free" in dictionary and dictionary["free"] is True:
                fp.append(name)
        return fp