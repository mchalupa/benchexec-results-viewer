import json

class GroupingBucket:

    def __init__(self, b):
        """
        Create bucket from configuration file section.
        @b is expected to contain "displayName" and "classifications" keys.
            "displayName" is string
            "classifications" is array of dictionaries with "type" and "cat" keys
        """
        self._display_name = b["displayName"]
        self._name_class = b["nameClass"]
        self._classes = {}
        self._classifications = list(map(lambda x: (x["type"], x["cat"]), b["classifications"]))

    def getClassifications(self):
        """
        Return list of classifications that belong in this bucket.
        The return type is list of tuples in this format: (type, category, numClass)
        Where:
            @type       could be 'true', 'error', ...
            @category   could be 'correct-unconfirmed', ...
            @numClass   is CSS class for the <span> tag that contains the stat
        """
        return self._classifications

    def getDisplayName(self):
        return self._display_name

    def getNameClass(self):
        return self._name_class

class Grouping:
    def __init__(self, g):
        """
        Create grouping from configuration file section.
        @g is expected to contain "displayName" and "buckets" keys.
            "displayName" is string,
            "buckets" is array of dictionaries
        """
        self._display_name = g["displayName"]
        self._buckets = list(map(lambda x: GroupingBucket(x), g["buckets"]))

    def getBuckets(self):
        return self._buckets

    def getDisplayName(self):
        return self._display_name

    def getNameClass(self):
        return self._name_class

class GroupingManager:

    """
    Manages available classification groupings.
    Grouping allows multiple classifications to be displayed on one line with custom description.
    """

    def __init__(self):
        self._groupings = []
        self._config = {}
        self._choices = []
        self._loadGroupings()

    def _loadGroupings(self):
        groupings = []
        with open('brv/grouping.json') as grouping_file:
            self._config = json.load(grouping_file)
            groupings = self._config["groupings"]

        if groupings is None:
            groupings = []

        for (g,i) in zip(groupings, range(len(groupings))):
            grouping = Grouping(g)
            self._groupings.append(grouping)
            self._choices.append((grouping.getDisplayName(), i))

        if not groupings:
            # TODO config file is empty, add default grouping(no grouping)
            pass

    def getGroupingChoices(self):
        """
        Returns list of tuples in following format: (display_name, id)
        where:
            @display_name is human-readable string to be displayed as representation of a grouping
            @id is machine-readable representation of the specified grouping (number)
        """
        return self._choices

    def getGrouping(self, id):
        return self._groupings[id]
