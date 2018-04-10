Collectd Solr Plugin
=========
[![Build Status](https://api.travis-ci.org/skarj/collectd-plugin-solr.svg?branch=master)](https://travis-ci.org/skarj/collectd-plugin-solr)

Collectd Plugin for Solr monitoring (tested with Solr 6.6)

Installation
------------

* Copy solr.py script to /usr/lib/collectd/modules/
* Add collectd plugin configuration
* Restart collectd

Collectd configuration
------------

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
