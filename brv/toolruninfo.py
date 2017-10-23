#!/usr/bin/env python

class ToolRunInfo(object):
    """
    Represents one tool in a given version with provided settings and environment
    (like CPAchecker of version XX ran with these params on this data)
    """
    def __init__(self, _id = None):
        self._id = _id

    def getID(self):
        return self._id

    def tool(self):
        raise NotImplemented

    def tool_version(self):
        raise NotImplemented

    def date(self):
        raise NotImplemented

    def options(self):
        raise NotImplemented

    def timelimit(self):
        raise NotImplemented

    def memlimit(self):
        raise NotImplemented

    def getResults(self):
        return self._runs

    def getStats(self):
        return self._stats

    def getLimits(self):
        return timelimit() + ' ' + memlimit()

    def addRun(self, r):
        """
        Add a run result to this tool run
        """
        self._runs.append(r)

class DBToolRunInfo(ToolRunInfo):
    def __init__(self, idtf, tool = None, vers = None, date = None,
                 opts = None, tlimit = None, mlimit = None):
        ToolRunInfo.__init__(self, idtf)

        # a descriptor of this run
        # FIXME: store only the query and use the query
        self._tool = tool
        self._tool_version = vers
        self._date = date
        self._options = opts
        self._timelimit = tlimit
        self._memlimit = mlimit
        # list of results (RunInfo objects)
        self._stats = None
        self._runs = []

    def tool(self):
        return self._tool

    def tool_version(self):
        return self._tool_version

    def date(self):
        return self._date

    def options(self):
        return self._options

    def timelimit(self):
        return self._timelimit

    def memlimit(self):
        return self._memlimit

    def getRuns(self):
        return self._runs

    def getStats(self):
        return self._stats

def sum_elems(lhs, rhs):
    "Sum elements in tuples pair-wise"
    return (lhs[0] + rhs[0], lhs[1] + rhs[1])

class RunsStats(object):
    def __init__(self, cat, bset_id):
        # '(status, classification)' -> count
        self._stats = {}
        self._benchmarks_name = cat
        self._benchmarks_id = bset_id
        # aggregated time that it took to run on this bset
        self._cpu_time = 0

    def addStat(self, classification, cnt, time):
        self._stats[classification]\
            = sum_elems(self._stats.setdefault(classification, (0,0)), (cnt, time))

    def get(self, classification):
            return self._stats.get(classification)

    def getStat(self, classification):
        n = self._stats.get(classification)
        if n is None:
            return (0,0)
        else:
            return n

    def accumulateTime(self, solved_only = False):
        self._cpu_time = 0
        if solved_only:
            for (key, val) in self._stats.items():
                if key[1] == 'correct' or key[1] == 'incorrect':
                    self._cpu_time += val[1]
        else:
            for (cnt, time) in self._stats.values():
                self._cpu_time += time

    def getAccTime(self):
        return self._cpu_time

    def getCount(self, classification):
        return self.getStat(classification)[0]

    def getTime(self, classification):
        return self.getStat(classification)[1]

    def getStats(self):
        return self._stats

    def getBenchmarksName(self):
        return self._benchmarks_name

    def getBenchmarksID(self):
        return self._benchmarks_id

    def getClassifications(self):
        return list(self._stats.keys())

    def prune(self):
        """
        Merge all false(...) and timeouts and other results.
        """
        newstats = {}
        for (key, stats) in self._stats.items():
            # key is a pair (status, classification)
            # value is a pair (count, consumed time)
            new_key =('other', 'error')
            for new_result in ['false', 'true', 'unknown', 'timeout', 'error']:
                if key[0].lower().startswith(new_result):
                    if key[1] is None:
                        new_key = (new_result, 'error')
                    else:
                        new_key = (new_result, key[1])
                    break

            newstats[new_key] =\
                sum_elems(newstats.setdefault(new_key, (0,0)), stats)

        self._stats = newstats

class ToolRunInfoStats(object):
    def __init__(self):
        self._stats = {}
        # mapping of names of categories to id's
        # of the benchmark sets
        self._name_to_id = {}

    def getAllStats(self):
        return self._stats

    def getStatsByID(self, bset_id):
        return self._stats.get(bset_id)

    def _addNameToIDMapping(self, cat, bset_id):
        if cat in self._name_to_id:
            self._name_to_id[cat].add(bset_id)
        else:
            self._name_to_id[cat] = set([bset_id])

    def getOrCreateStats(self, bset_id, cat):
        if bset_id in self._stats:
            stats = self._stats[bset_id]
        else:
            stats = RunsStats(cat, bset_id)
            self._stats[bset_id] = stats
            self._addNameToIDMapping(cat, bset_id)

        return stats

    def getBenchmarksSetsNames(self):
        return self._name_to_id.keys()

    def getBenchmarksSets(self):
        return self._stats.keys()


class RunInfosTable(object):
    """
    Table of RunInfo objects:

                 tool1  tool2  ...
    benchmark1   ri11    ri12  ...
    benchmark2   ri21    ri22  ...
       ...       ...     ...
    """

    def __init__(self):
        # benchmarks_name -> list of runinfos
        self._benchmarks = {}
        self._tools_num = 0

    def add(self, runinfos):
        """ add results from one tool run"""

        for info in runinfos:
            name = info.fullname()
            infos = self._benchmarks.setdefault(name, [])

            ## missing some tools? Fill in the gap
            self._fill_blank(infos)
            infos.append(info)

        self._tools_num += 1

    def _fill_blank(self, infos):
        l = len(infos)
        assert l <= self._tools_num

        while l < self._tools_num:
            infos.append(None)
            l += 1

        assert len(infos) == self._tools_num

    def _fill_blank_all(self):
        for infos in self._benchmarks.values():
            self._fill_blank(infos)

    def getRunInfos(self, benchmark):
        info = self._benchmarks.get(benchmark)
        if info:
            self._fill_blank(info)

        return info

    def getRows(self):
        self._fill_blank_all()
        return self._benchmarks

