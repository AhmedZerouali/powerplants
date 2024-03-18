class PowerPlant:
    """
    A class that represents a powerplant and only include powerplant params
    :param element: characteristics of a powerplant 
    """
    def __init__(self, element, wind=None):
        self.name = element.get('name',None)
        self.type = element.get('type',None)
        self.efficiency = element.get('efficiency',None)
        self.pmin = element.get('pmin',0)
        self.pmax = element.get('pmax',None)
        if wind != None:
            self.wind = wind
            self.pmax = round(self.pmax*wind/100,1)
            
        if self.type == "gasfired":
            self.co2_cost = 0.3

    def cost(self, price):
        """
        Computes the price depending on the efficiency and the given price
        :param price: current price of the fuel
        :return: the actual cost
        """
        if (price and self.efficiency):
            return price / self.efficiency
        return 0

class GeneratePower:
    """
    A class that represents a generator that orchestrate between powerplants
    :param powerplants: available powerplants 
    """
    def __init__(self, powerplants):
        self.powerplants, self.kerosine_price, self.gas_price, self.load = powerplants
        # order powerplants based on how costy they are
        self.powerplants = sorted(self.powerplants, key=lambda x: self.calculate_sort_key(x))

    def calculate_sort_key(self, powerplant):
        """
        This is used to sort the powerplants based on their cost
        :param powerplant: one specific powerplant
        :return: the actual cost of a powerplant
        """
        if powerplant.type == "windturbine":
            return 0 
        elif powerplant.type == "gasfired":
            return powerplant.cost(self.gas_price)
        else:
            return powerplant.cost(self.kerosine_price)

    def generate(self):
        """
        Finds the powerplants that will be used and how much power they will produce
        :return: the powerplants that will be used and the ones that will not be used
        """
        power = 0 # no power is produced yet
        pps = [] # For powerplants that will will be used
        pps_0 = [] # For powerplants generating 0 power

        for pp in self.powerplants:
            if self.load > power and pp.pmax>0: # if we still need power and the current powerplant can generate any
                power_to_add = round(min(self.load-power, pp.pmax), 1) # take the max or what is left to produce
                if power_to_add < pp.pmin: # what is left is less than the minimum
                    power_to_add  = pp.pmin # we set the minimum of the current powerplant to be added 
                    reduce  =  power + power_to_add - self.load # prapare the added amount to remove it from the previous powerplant
                    pps[-1][1] = pps[-1][1] - reduce # remove the extra power from the previous powerplant
                    power = power - reduce + power_to_add # increase the amount of power produced
                else:# if no issues then just take the power we prepare
                    power = power + power_to_add 
                pps.append([pp, power_to_add]) # save the current powerplant which the power that it will produce
            else:
                pps_0.append([pp, 0]) # save the powerplant that cannot produce any power
        return pps+pps_0 # return both lists ordered

    def export(self):
        """
        Exports the results in a json format
        :return: a list of dictionaries
        """
        to_json = []
        for i in self.generate():
            to_json.append({'name': i[0].name, 'p': i[1]})
        return to_json

class Payload:
    """
    A class that is used to prepare the payload
    :param payload: the payload received from the client
    """
    def __init__(self, payload):
        self.load = payload.get('load', None)
        self.fuels = payload.get('fuels', None)
        self.gas_price = self.fuels.get('gas(euro/MWh)', None)
        self.kerosine_price = self.fuels.get('kerosine(euro/MWh)', None)
        self.co2 = self.fuels.get('co2(euro/ton)', None)
        self.wind = self.fuels.get('wind(%)', None)
        self.powerplants = payload['powerplants']

    def create_powerplants(self):
        if not (self.load and self.fuels and self.powerplants):
            return None
        # The following could be improved based on the values given in the payload
        # I am assuming that powerplants' values will be included in the payload
        pp = [PowerPlant(element) if element['type'] != "windturbine" 
                       else PowerPlant(element, self.wind) 
                       for element in self.powerplants] 

        return pp, self.kerosine_price, self.gas_price, self.load