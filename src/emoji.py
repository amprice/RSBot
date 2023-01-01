import typing
from discord import Guild

rsmod_order = ["nosanc", 
               "dart",
               "barrage",
               "laser",
               "dual_laser",
               "mass",
               "batt",
               "omega_shield",
               "passive_shield",
               "barrier",
               "suppress",
               "unity",
               "emp",
               "rse",
               "tw",
               "veng",
               "destiny",
               "remote",
               "alpha_drone",
               "mining_drone",
               "tele",
               "solo1",
               "solo2"]

emoji : typing.Dict[str, str] = {
    "nosanc": "<:nosanc:1032935233298903100>",
    "dart" : "<:dart1:1032938403941060648>",
    "barrage" : "<:barrage:1032938379475685376>",
    "laser" : "<:laser:1032938402141720576>",
    "dual_laser": "<:dual_laser:1032943690135650314>",
    "mass" : "<:mass:1032938405786570813>",
    "batt" : "<:batt:1032938399830650911>",
    "omega_shield": "<:omega_shield:1032943691981139998>",
    "passive_shield" : "<:passive_shield:1032938383170875423>",
    "suppress" : "<:suppress:1032938392603873350>",
    "unity" : "<:unity:1032938390812897330>",
    "emp" : "<:emp:1057798691773239367>",
    "rse" : "<:rse:1032938388896104478>",
    "tw" : "<:tw:1032938387021254657>",
    "bond" : "<:bond:1032938381266649098>",
    "barrier" : "<:barrier:1057824314184957963>",
    "veng" : "<:veng:1032938377680535552>",
    "destiny" : "<:destiny:1057799385804718121>",
    "remote" : "<:remote:1032938375629520926>",
    "alpha_drone" : "<:alpha_drone:1057801799874117653>",
    "mining_drone" : "<:mining_drone:1057801802692710482>",
    "tele" : "<:tele:1032938373658185768>",
    "solo1": "<:solo1:1032939571777904681>",
    "solo2" : "🦾",
    "no_tele" :"<:notele:1033163905540821063>",
    "croid" : "<:croid:1032938396353560576>",
    "time": "🕒",
     "obstain" : "✊",
     "upvote" : "👍",
     "downvote" : "👎",
     "guest" : "👤",
     "guest1" : "👥"
}

class Mods():
    def __init__(self) -> None:
        self.status : typing.Dict[str, bool] = {}
        self.buildRSModDict()
        self.guild : Guild = None
    
    def buildRSModDict(self):
        for i in range(len(rsmod_order)):
            # print (f"{rsmod_order[i]}")
            key = rsmod_order[i]
            self.status[key] = False
            
    def modString(self) -> str:
        s = ""
        for key in self.status:
            if (self.status[key]):
                s += emoji[key]  
        return s
    
    def sortDictByKey(self):
        sortedDict = {}
        for i in range(len(rsmod_order)):
            key = rsmod_order[i]
            if key in self.status:
                sortedDict[key] = self.status[key]
            else:
                sortedDict[key] = False
        self.status = sortedDict