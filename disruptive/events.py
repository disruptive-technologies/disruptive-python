# Project imports.
import disruptive.transforms as dttransforms
import disruptive.outputs as dtoutputs
import disruptive.datas as dtdatas

# This dictionary is created to bridge the three different naming conventions
# used for every single event. The REST API returns events with camel case,
# whereas in python we prefer snake casing, and classes fully cased. It also
# prevent recreating long if-statements when choosing an event by type.
EVENTS_MAP = {
    'touch': {
        'attr': 'touch',
        'class': dtdatas.Touch,
        'is_keyed': True,
    },
    'temperature': {
        'attr': 'temperature',
        'class': dtdatas.Temperature,
        'is_keyed': True,
    },
    'objectPresent': {
        'attr': 'object_present',
        'class': dtdatas.ObjectPresent,
        'is_keyed': True,
    },
    'humidity': {
        'attr': 'humidity',
        'class': dtdatas.Humidity,
        'is_keyed': True,
    },
    'objectPresentCount': {
        'attr': 'object_present_count',
        'class': dtdatas.ObjectPresentCount,
        'is_keyed': True,
    },
    'touchCount': {
        'attr': 'touch_count',
        'class': dtdatas.TouchCount,
        'is_keyed': True,
    },
    'waterPresent': {
        'attr': 'water_present',
        'class': dtdatas.WaterPresent,
        'is_keyed': True,
    },
    'networkStatus': {
        'attr': 'network_status',
        'class': dtdatas.NetworkStatus,
        'is_keyed': True,
    },
    'batteryStatus': {
        'attr': 'battery_status',
        'class': dtdatas.BatteryStatus,
        'is_keyed': True,
    },
    'labelsChanged': {
        'attr': 'labels_changed',
        'class': dtdatas.LabelsChanged,
        'is_keyed': False,
    },
    'connectionStatus': {
        'attr': 'connection_status',
        'class': dtdatas.ConnectionStatus,
        'is_keyed': True,
    },
    'ethernetStatus': {
        'attr': 'ethernet_status',
        'class': dtdatas.EthernetStatus,
        'is_keyed': True,
    },
    'cellularStatus': {
        'attr': 'cellular_status',
        'class': dtdatas.CellularStatus,
        'is_keyed': True,
    },
}


class Event(dtoutputs.OutputBase):

    def __init__(self, event_dict):
        # Inherit attributes from ResponseBase parent.
        dtoutputs.OutputBase.__init__(self, event_dict)

        # Unpack parts of event that is common for all types.
        self.__unpack()

    def __unpack(self):
        self.event_id = self.raw['eventId']
        self.event_type = self.raw['eventType']
        self.device_id = self.raw['targetName'].split('/')[-1]
        self.project_id = self.raw['targetName'].split('/')[1]

        # Initialize the appropriate data class.
        self.data = dtdatas.DataClass.from_event_type(
            self.raw['data'],
            self.event_type
        )

        # Convert ISO-8601 string to datetime format.
        self.timestamp = dttransforms.iso8601_to_datetime(
            self.raw['timestamp']
        )

    @classmethod
    def from_single(cls, event):
        child = cls.__classify_event_by_type(event)
        return child(event)

    @classmethod
    def from_mixed_list(cls, event_list):
        # Initialise output list.
        object_list = []

        # Iterate events in list.
        for event in event_list:
            # Initialize instance and append to output.
            object_list.append(Event(event))

        return object_list
