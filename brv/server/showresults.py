#!/usr/bin/python

from . rendering import render_template
from . util import get_elem, getDescriptionOrVersion
from math import ceil
from .. import groupingmanager

def showResults(wfile, datamanager, opts):
    if not 'run' in opts:
        wfile.write(b'<h2>No runs of tools given</h2>')
        return

    def hasAnswers(runs, bset_id, classif):
        assert not runs is None
        assert not bset_id is None

        for run in runs:
            if bset_id != -1:
                # get stats for one of the categories
                stats = run.getStats().getStatsByID(bset_id)
            else:
                # get the overall stats
                stats = run.getStats().getSummary(_showTimesOnlySolved)
            if not stats is None and stats.getCount(classif) != 0:
                return True

        return False

    def bucketHasAnswers(runs, bucket):
        classifs = bucket.getClassifications()
        for classif in classifs:
            if hasAnswers(runs, -1, classif):
                return True
        return False

    class BSet(object):
        def __init__(self, name, bid):
            self.name = name
            self.id = bid

        def __hash__(self):
            return self.id

        def __eq__(self, oth):
            return self.id == oth.id

    _showTimes = 'show_times' in opts
    _showTimesOnlySolved = 'show_times_only_solved' in opts
    groupingId = 0
    if 'grouping' in opts:
        groupingId = int(opts['grouping'][0])
    grouping = datamanager.getGrouping(groupingId)
    if grouping is None:
        grouping = datamanager.getGrouping(0)
    _inlineView = 'inline_view' in opts
    buckets = grouping.getBuckets()
    # list of ToolRun objects
    run_ids = list(map(int, opts['run']))
    runs = datamanager.getToolRuns(run_ids)
    categories = set()
    # there's few of classifications usually, it will be faster in list
    classifications = []
    for run in runs:
        run._stats = datamanager.getToolInfoStats(run.getID())
        for stats in run._stats.getAllStats().values():
            stats.accumulateTime(_showTimesOnlySolved)
            # a pair (name, id)
            categories.add(BSet(stats.getBenchmarksName(), stats.getBenchmarksID()))
            for c in stats.getClassifications():
                if c not in classifications:
                    classifications.append(c)

    # extend the selected grouping to avoid hiding non-configured results
    for c in classifications:
        found = False
        for b in buckets:
            if c in b.getClassifications():
                found = True
        if not found:
            display_name = c[0]
            if display_name == None or len(display_name) == 0:
                display_name = "<i>&lt;missing classification&gt;</i>"
            buckets.append(groupingmanager.GroupingBucket(display_name, "classif status-{0}".format(c[1]), [c]))

    buckets = list(filter(lambda b: bucketHasAnswers(runs, b), buckets))
    # give it some fixed order
    cats = [x for x in categories]

    def _toolsGETList():
        s = ''
        for x in opts['run']:
            s += '&run={0}'.format(x)
        return s

    def _getStats(run, bset_id):
        assert not run is None
        assert not bset_id is None

        return run.getStats().getStatsByID(bset_id)

    def _getCount(stats, classif):
        if stats:
            return stats.getCount(classif)
        else:
            return 0

    def _getBucketCount(stats, bucket):
        if stats:
            result = 0
            for classif in bucket.getClassifications():
                result += _getCount(stats, classif)
            return result
        else:
            return 0


    def _getTime(stats, classif):
        if stats:
            return ceil(stats.getTime(classif))
        else:
            return 0

    def _getBucketTime(stats, bucket):
        if stats:
            result = 0
            for classif in bucket.getClassifications():
                result += _getTime(stats, classif)
            return result
        else:
            return 0

    def _getTotalStats(run):
        assert not run is None

        return run.getStats().getSummary(_showTimesOnlySolved)

    def _lenPlus(o, a):
        return len(o) + a

    def _formatTime(time):
        "Transform time in seconds to hours, minutes and seconds"
        if not time:
            return '0 s'
        ret = ''
        time = ceil(time)
        if time >= 3600:
            hrs = time // 3600
            time = time - hrs*3600
            ret = '{0} h'.format(int(hrs))
        if time >= 60 or ret != '':
            mins = time // 60
            time = time - mins*60
            ret += ' {0} min'.format(int(mins))
        if ret != 0:
            return ret + ' {0} s'.format(int(time))
        else:
            return ret + '{0} s'.format(int(time))

    def _packStatsFunc(bset_id):
        return (lambda run: _getStats(run, bset_id))

    render_template(wfile, 'results.html',
                     {'runs':runs, 'benchmarks_sets' : cats,
                      'toolsGETList' : _toolsGETList,
                      'getStats' : _getStats,
                      'getTotalStats' : _getTotalStats,
                      'getBucketCount' : _getBucketCount,
                      'getCount' : _getCount,
                      'getTime' : _getTime,
                      'getBucketTime' : _getBucketTime,
                      'get' : get_elem,
                      'showTimes' : _showTimes,
                      'showTimesOnlySolved' : _showTimesOnlySolved,
                      'formatTime' : _formatTime,
                      'descr' : getDescriptionOrVersion,
                      'buckets': buckets,
                      'groupingId': groupingId,
                      'lenPlus': _lenPlus,
                      'packStatsFunc': _packStatsFunc,
                      'inlineView': _inlineView,
                      'groupings': datamanager.getGroupingChoices() })

