## aco-karms : dlts/ subdirectory

This directory and subdirectories contains the DLTS-specific
work-directory generation code and test framework.

## Prerequisites:
All WIP directories must be structured as:
```
  <wip>/handle
  <wip>/data/<marcxml file>
```

Each WIP directory MUST:
* have a ```<wip>/data``` directory that contains only ONE MARCXML file with the suffix ```_marcxml.xml```
  * the MARCXML file must validate against the MARC21slim.xsd schema.
  * the MARCXML file must contain ```<controlfield tag="003">``` an ```<controlfield tag="001">``` elements
* contain a ```handle``` file containing a string ```<prefix>/<suffix>```
  * e.g., ```2333.1/s4mw6wxyz```

## Sample invocation:

```
$ WIPS='TEST-2bvq8nm TEST-2fqz6kb TEST-2ngf2ds TEST-2rbp0bf TEST-31zcs3n ...'
$ ruby ~/dl/dev/aco-karms/dlts/bin/gen-work-dirs.rb ~/dl/dev/aco-karms/work $WIPS
```
