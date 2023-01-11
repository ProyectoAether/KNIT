__version__ = "0.1.0"
__author__ = "Jorge Rodriguez-Revello <rodriguezrevellojj@uma.es>"
__group__ = "Khaos Research <khaos.uma.es>"

HEADER = "\n".join(
    [
        r"                                                  ",
        r"           ____  __.      .__  __                 ",
        r"          |    |/ _| ____ |__|/  |_               ",
        r"          |      <  /    \|  \   __\              ",
        r"          |    |  \|   |  \  ||  |                ",
        r"          |____|__ \___|  /__||__|                ",
        r"                  \/    \/                        ",
        "                                                   ",
        f" ver. {__version__}     group  {__group__}     ",
        f"author {__author__}                            ",
        "                                               ",
    ]
)
print(HEADER)