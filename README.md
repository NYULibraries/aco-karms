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
                      marcxml_in/
                              FOO_0004567_marcxml.xml
                              FOO_9871234_marcxml.xml
                              ...
     QXX/
         QXX_20140401/
                      handles.csv
                      marcxml_in/
                              QXX_1234567_marcxml.xml
                              QXX_9876543_marcxml.xml
                              ...
```
#### CSV file format:
```
<header row>
<data rows>

header row = 003,001,handle
data   row = NNU,123456789,http://hdl.handle.net/2333.1/<NOID>
```
#### Example handles.csv File
```
003,001,handle
FOO,0004567,http://hdl.handle.net/10676/x4mw6mmm
FOO,9871234,http://hdl.handle.net/10676/y7mxqr32
```
