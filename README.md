# Collectd Solr Plugin
Collectd Plugin for Solr monitoring (tested with Solr 6.6)

# Installation
1. Copy solr.py script to /usr/lib/collectd/modules/
2. Add collectd plugin configuration
3. Restart collectd

# Collectd configuration
```
LoadPlugin python
<Plugin python>
  ModulePath "/usr/lib/collectd/modules/"
  Import "solr"
  <Module "solr">
    Host "127.0.0.1"
    Port 8983
    Interval 60
    Instance "solr"
  </Module>
</Plugin>
```
