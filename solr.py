# solr-collectd-plugin - solr.py
#
# Author: Sergey Baranov
# Description: This is a collectd plugin which runs under the Python plugin to
# collect metrics from solr.

import collectd
import urllib2, json

VERBOSE_LOGGING = False

SOLR_METRICS = [
# JVM metrics:
    'memory.heap.committed',
    'memory.heap.init',
    'memory.heap.max',
    'memory.heap.used',
    'threads.blocked.count',
    'threads.count',
    'threads.daemon.count',
    'threads.deadlock.count',
    'threads.new.count',
    'threads.runnable.count',
    'threads.terminated.count',
    'threads.timed_waiting.count',
    'threads.waiting.count',
# Jetty metrics:
    'org.eclipse.jetty.util.thread.QueuedThreadPool.qtp985934102.jobs',
    'org.eclipse.jetty.util.thread.QueuedThreadPool.qtp985934102.size',
    'org.eclipse.jetty.util.thread.QueuedThreadPool.qtp985934102.utilization',
    'org.eclipse.jetty.util.thread.QueuedThreadPool.qtp985934102.utilization-max',
    'org.eclipse.jetty.server.handler.DefaultHandler.1xx-responses',
    'org.eclipse.jetty.server.handler.DefaultHandler.2xx-responses',
    'org.eclipse.jetty.server.handler.DefaultHandler.3xx-responses',
    'org.eclipse.jetty.server.handler.DefaultHandler.4xx-responses',
    'org.eclipse.jetty.server.handler.DefaultHandler.5xx-responses',
    'org.eclipse.jetty.server.handler.DefaultHandler.active-dispatches',
    'org.eclipse.jetty.server.handler.DefaultHandler.active-requests',
    'org.eclipse.jetty.server.handler.DefaultHandler.active-suspended',
    'org.eclipse.jetty.server.handler.DefaultHandler.async-dispatches',
    'org.eclipse.jetty.server.handler.DefaultHandler.async-timeouts',
    'org.eclipse.jetty.server.handler.DefaultHandler.connect-requests',
    'org.eclipse.jetty.server.handler.DefaultHandler.delete-requests',
    'org.eclipse.jetty.server.handler.DefaultHandler.dispatches',
    'org.eclipse.jetty.server.handler.DefaultHandler.get-requests',
    'org.eclipse.jetty.server.handler.DefaultHandler.head-requests',
    'org.eclipse.jetty.server.handler.DefaultHandler.move-requests',
    'org.eclipse.jetty.server.handler.DefaultHandler.options-requests',
    'org.eclipse.jetty.server.handler.DefaultHandler.other-requests',
    'org.eclipse.jetty.server.handler.DefaultHandler.post-requests',
    'org.eclipse.jetty.server.handler.DefaultHandler.put-requests',
    'org.eclipse.jetty.server.handler.DefaultHandler.requests',
    'org.eclipse.jetty.server.handler.DefaultHandler.trace-requests',
# Node metrics:
    'UPDATE.updateShardHandler.leasedConnections',
    'UPDATE.updateShardHandler.pendingConnections',
    'UPDATE.updateShardHandler.maxConnections',
    'UPDATE.updateShardHandler.availableConnections',
    'UPDATE.updateShardHandler.threadPool.recoveryExecutor.running',
    'QUERY.httpShardHandler.maxConnections',
    'QUERY.httpShardHandler.availableConnections',
    'QUERY.httpShardHandler.pendingConnections',
    'QUERY.httpShardHandler.leasedConnections',
    'QUERY.httpShardHandler.threadPool.httpShardExecutor.running',
    'CONTAINER.fs.usableSpace',
    'CONTAINER.cores.loaded',
    'CONTAINER.cores.unloaded',
    'CONTAINER.fs.totalSpace',
    'CONTAINER.cores.lazy',
    'CACHE.fieldCache',
    'CONTAINER.threadPool.coreContainerWorkExecutor.running',
    'CONTAINER.threadPool.coreLoadExecutor.running',
# Core metrics:
    'UPDATE.updateHandler.adds',
    'UPDATE.updateHandler.deletesByQuery',
    'UPDATE.updateHandler.deletesById',
    'UPDATE.updateHandler.docsPending',
    'UPDATE.updateHandler.autoCommits',
    'UPDATE.updateHandler.errors',
    'UPDATE.updateHandler.softAutoCommits',
    'CORE.fs.totalSpace',
    'CORE.refCount',
    'CORE.fs.usableSpace',
    'TLOG.buffered.ops',
    'TLOG.replay.remaining.bytes',
    'TLOG.replay.remaining.logs',
    'INDEX.sizeInBytes',
    'CACHE.searcher.filterCache',
    'CACHE.searcher.queryResultCache',
    'CACHE.searcher.perSegFilter',
    'CACHE.searcher.fieldValueCache',
    'CACHE.searcher.documentCache',
    'CACHE.core.fieldCache'
]


def log_verbose(msg):
    if not VERBOSE_LOGGING:
        return
    collectd.info('Collectd-Solr Plugin: {}'.format(msg))


class Solr(object):
    def __init__(self, host='localhost', port=8983):
        self.host = host
        self.port = port


    def get_metrics(self, group):
        url = 'http://{}:{}/solr/admin/metrics?wt=json&group={}'.format(self.host, self.port, group)
        try:
            response = urllib2.urlopen(url)
            reply = json.loads(response.read())
            if response.getcode() == 200:
                if group == 'core':
                    reply = reply['metrics']
                else:
                    reply = reply['metrics']['solr.' + group]
        except urllib2.HTTPError as error:
            log_verbose('collectd-solr plugin: can\'t get {} metrics, with error message {}'.format(group, error.read()))
        return reply


class SolrPlugin(object):
    def __init__(self):
        self.SOLR_HOST = 'localhost'
        self.SOLR_PORT = 8983
        self.SOLR_INTERVAL = 10
        self.SOLR_INSTANCE = "solr"


    def configure_callback(self, conf):
        """Read configuration"""
        for node in conf.children:
            if node.key == 'Host':
                self.SOLR_HOST = node.values[0]
            elif node.key == 'Port':
                self.SOLR_PORT = int(node.values[0])
            elif node.key == 'Interval':
                self.SOLR_INTERVAL = int(float(node.values[0]))
            elif node.key == 'Instance':
                self.SOLR_INSTANCE = node.values[0]
            else:
                collectd.warning('collectd-solr plugin: Unknown config key: {}.'.format(node.key))
        log_verbose('Configured: host={}, port={}, interval={}, instance={}'.format(self.SOLR_HOST, self.SOLR_PORT, self.SOLR_INTERVAL, self.SOLR_INSTANCE))


    def dispatch_value(self, type_instance, value, value_type, plugin_instance):
        val = collectd.Values(plugin='solr')
        val.type_instance = type_instance
        val.type = value_type
        val.values = [value]
        val.plugin_instance = plugin_instance
        val.dispatch()


    def read_callback(self):
        log_verbose('Read Callback Called')
        solr = Solr(self.SOLR_HOST, self.SOLR_PORT)
        units = {'bytes': 1, 'KB': 10**3, 'MB': 10**6, 'GB': 10**9, 'TB': 10**12}

        for group in 'jvm', 'jetty', 'node':
            for metric, value in solr.get_metrics(group).items():
                if metric in SOLR_METRICS:
                    if 'value' in value.keys():
                        data = value['value']
                        mtype = 'gauge'
                    elif 'count' in value.keys():
                        data = value['count']
                        mtype = 'counter'
                    if isinstance(data, dict):
                        for submetric, value in data.items():
                            if not 'entry#' in submetric:
                                metricname = metric + '.' + submetric
                                for unit, multip in units.items():
                                    if unit in str(value):
                                        value = int(float(value.split(' ')[0]) * units[unit])
                                self.dispatch_value(metricname, value, mtype, self.SOLR_INSTANCE + '.' + group)
                    else:
                        self.dispatch_value(metric, data, mtype, self.SOLR_INSTANCE + '.' + group)

        for corename, values in solr.get_metrics('core').items():
            for metricname, value in values.items():
                if metricname in SOLR_METRICS:
                    if 'value' in value.keys():
                        data = value['value']
                        mtype = 'gauge'
                    elif 'count' in value.keys():
                        data = value['count']
                        mtype = 'counter'
                    if isinstance(data, dict):
                        for submetric, value in data.items():
                            if not 'entry#' in submetric:
                                metric = metricname + '.' + submetric
                                for unit, multip in units.items():
                                    if unit in str(value):
                                        value = int(float(value.split(' ')[0]) * units[unit])
                                self.dispatch_value(metric, value, mtype, corename)
                    else:
                        self.dispatch_value(metricname, data, mtype, corename)


plugin = SolrPlugin()
collectd.register_config(plugin.configure_callback)
collectd.register_read(plugin.read_callback, plugin.SOLR_INTERVAL)
