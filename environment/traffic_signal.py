import traci


class TrafficSignal:

    NS = 0
    EW = 2

    def __init__(self, ts_id, delta_time):
        self.id = ts_id
        self.time_on_phase = 0
        self.delta_time = delta_time
        self.min_green = 10
        self.edges = self._compute_edges()
        self.ns_stopped = [0, 0]
        self.ew_stopped = [0, 0]
        phases = [
            traci.trafficlight.Phase(42000, 42000, 42000, "GGGrrr"),   # north-south -> 0
            traci.trafficlight.Phase(2000, 2000, 2000, "yyyrrr"),
            traci.trafficlight.Phase(42000, 42000, 42000, "rrrGGG"),   # east-west -> 2
            traci.trafficlight.Phase(2000, 2000, 2000, "rrryyy"),
        ]
        logic = traci.trafficlight.Logic("new-program", 0, 0, 0, phases)
        traci.trafficlight.setCompleteRedYellowGreenDefinition(self.id, logic)

    @property
    def phase(self):
        return traci.trafficlight.getPhase(self.id)

    def keep(self):
        self.time_on_phase += self.delta_time
        traci.trafficlight.setPhaseDuration(self.id, self.delta_time)

    def change(self):
        if self.time_on_phase < self.min_green:  # min green time => do not change
            self.keep()
        else:
            self.time_on_phase = self.delta_time
            traci.trafficlight.setPhaseDuration(self.id, 0)

    def _compute_edges(self):
        """
        :return: Dict green phase to edge id
        """
        lanes = list(dict.fromkeys(traci.trafficlight.getControlledLanes(self.id)))  # remove duplicates and keep order
        return {self.NS: lanes[:2], self.EW: lanes[2:]}  # two lanes per edge

    def get_occupancy(self):
        ns_occupancy = sum([traci.lane.getLastStepOccupancy(lane) for lane in self.edges[self.NS]]) / len(self.edges[self.NS])
        ew_occupancy = sum([traci.lane.getLastStepOccupancy(lane) for lane in self.edges[self.EW]]) / len(self.edges[self.EW])
        return ns_occupancy, ew_occupancy

    def get_stopped_vehicles_num(self):
        self.ns_stopped[1], self.ew_stopped[1] = self.ns_stopped[0], self.ew_stopped[0]
        self.ns_stopped[0] = sum([traci.lane.getLastStepHaltingNumber(lane) for lane in self.edges[self.NS]])
        self.ew_stopped[0] = sum([traci.lane.getLastStepHaltingNumber(lane) for lane in self.edges[self.EW]])

        return self.ns_stopped[0], self.ew_stopped[0]