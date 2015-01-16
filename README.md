## aco-karms

This repo contains MARCXML files for the ACO project and is used as a
coordination point between NYU DLTS and NYU KARMS metadata processing.

```
Directory structure is as follows:

bin/            stores scripts
marcxml/<003>   stores source MARCXML files from partners

work/<partner>/<003>_<dstamp>              stores .csv file with format specified below
work/<partner>/<003>_<dstamp>/handles.csv  file with MARC 003, MARC 001, and handle URLs
work/<partner>/<003>_<dstamp>/marcxml      contains all MARCXML files mentioned in the CSV file
```
#### Example Directory
```
work/
     FOO/
         FOO_20140330/
                      handles.csv
                      bsn-se-map.csv
                      marcxml_in/
                              FOO_0004567_marcxml.xml
                              FOO_9871234_marcxml.xml
                              ...
     QXX/
         QXX_20140401/
                      handles.csv
                      bsn-se-map.csv
                      marcxml_in/
                              QXX_1234567_marcxml.xml
                              QXX_9876543_marcxml.xml
                              ...
```
#### handles.csv file format:
```
<header row>
<data rows>

header row = 003,001,handle
data   row = <003>,<001>,<handle URL>
```
#### Example handles.csv File
```
003,001,handle
FOO,0004567,http://hdl.handle.net/10676/x4mw6mmm
FOO,9871234,http://hdl.handle.net/10676/y7mxqr32
```

#### bsn-se-map.csv file format:
```
<data rows>

data   row = <001><SE_LIST>
SE_LIST    = SE[|SE|...]
SE         = DIGI_ID[:VOLUME_LABEL]
```

#### Example bsn-se-map.csv File
```
2297940,nyu_aco000438
1581834,nyu_aco000097:v.1|nyu_aco000098:v.2|nyu_aco000099:v.3
1680246,nyu_aco000095:v.1
1470030,nyu_aco000425
1585912,nyu_aco000061:v.1|nyu_aco000062:v.2|nyu_aco000063:v.3|nyu_aco000064:v.4|nyu_aco000065:v.5
```
