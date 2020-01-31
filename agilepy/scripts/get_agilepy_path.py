import agilepy


if len(agilepy.__path__) == 0:
    print("Cant find the directory of the agilepy library. Report this issue to the developers.")
    exit(1)

print(agilepy.__path__[0])
