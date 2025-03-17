from pandas import DataFramefrom pandas import DataFramefrom pandas.core.interchange.dataframe_protocol import DataFrame

# pyDeltafile

pyDeltafile is an open-source tool for comparing data files (CSV, Excel) and generating the delta between them. 
The project identifies added, removed, and modified rows, providing a detailed report of the differences.

## Features

Produce a fast, customizable way to compare data into files (CSV) and produce a file with the differences.


```bash
pip install pyDeltafile
```

## Usage

```python
import pyDeltafile as td
td.delta_csv('file_A.csv', 'file_B.csv', 'delta.csv', 'id', 0)
```

or

```python
import pyDeltafile as td
from pandas import DataFrame

def delete_callback(dataframe: DataFrame) -> DataFrame:
    df = dataframe.copy()  # Create a copy to avoid SettingWithCopyWarning
    df['Delete'] = 1
    return df

def add_callback(dataframe:DataFrame) -> DataFrame:
    df = dataframe.copy()  # Create a copy to avoid SettingWithCopyWarning
    df['Delete'] = 0
    return df

td.delta_csv('file_A.csv', 'file_B.csv', 'delta.csv', 'id', 0, delete_callback, add_callback)
```


## Example

Suppose we have two CSV files, `file_A.csv` and `file_B.csv`, with the following content:

**file\_A.csv:**

```csv
id,first_name,last_name,email,gender,ip_address
1,Leonard,Gerran,lgerran0@meetup.com,Male,142.106.215.156
2,Josepha,Checklin,jchecklin1@wiley.com,Female,45.0.210.191
3,Flemming,Dursley,fdursley2@yahoo.com,Male,239.238.145.163
4,Park,Bowkley,pbowkley3@google.ca,Male,96.119.231.172
5,Raoul,Boreland,rboreland4@sbwire.com,Male,89.227.7.140
6,Glynnis,Cotilard,gcotilard5@ed.gov,Female,14.169.23.61
7,Maure,Gerhartz,mgerhartz6@cbsnews.com,Female,211.144.32.239
8,Jameson,Klesel,jklesel7@oaic.gov.au,Male,182.253.243.211
9,Maxim,Sambrok,msambrok8@e-recht24.de,Male,204.141.194.90
10,Stella,Grossman,sgrossman9@infoseek.co.jp,Female,235.130.153.140
```

**file\_B.csv:**

```csv
id,first_name,last_name,email,gender,ip_address
1,Leonard,Gerran,lgerran0@meetup.com,Male,142.106.215.156
3,Flemming,Dursley,fdursley2@yahoo.com,Male,239.238.145.163
5,Raoul,Boreland,rboreland4@sbwire.com,Male,89.227.7.140
7,Maure,Gerhartz,mgerhartz6@cbsnews.com,Female,211.144.32.239
9,Maxim,Sambrok,msambrok8@e-recht24.de,Male,204.141.194.90
11,Christi,Braben,cbrabena@npr.org,Female,165.49.144.201
13,Gabby,Gladdin,ggladdinc@virginia.edu,Male,153.56.64.234
15,Mill,Chadwell,mchadwelle@archive.org,Male,15.126.32.220
17,Egbert,Normavell,enormavellg@cisco.com,Male,235.130.153.140
```

Using pyDeltafile with `keys=['ip_address']`, the generated delta into a file:

**delta.csv:**
```csv
id,first_name,last_name,email,gender,ip_address
2,Josepha,Checklin,jchecklin1@wiley.com,Female,45.0.210.191
4,Park,Bowkley,pbowkley3@google.ca,Male,96.119.231.172
6,Glynnis,Cotilard,gcotilard5@ed.gov,Female,14.169.23.61
8,Jameson,Klesel,jklesel7@oaic.gov.au,Male,182.253.243.211
11,Christi,Braben,cbrabena@npr.org,Female,165.49.144.201
13,Gabby,Gladdin,ggladdinc@virginia.edu,Male,153.56.64.234
15,Mill,Chadwell,mchadwelle@archive.org,Male,15.126.32.220
```

Using pyDeltafile with `keys=['ip_address']`, the generated delta with second scenario into a file:

**delta2.csv:**
```csv
id,first_name,last_name,email,gender,ip_address,Delete
2,Josepha,Checklin,jchecklin1@wiley.com,Female,45.0.210.191,1
4,Park,Bowkley,pbowkley3@google.ca,Male,96.119.231.172,1
6,Glynnis,Cotilard,gcotilard5@ed.gov,Female,14.169.23.61,1
8,Jameson,Klesel,jklesel7@oaic.gov.au,Male,182.253.243.211,1
11,Christi,Braben,cbrabena@npr.org,Female,165.49.144.201,0
13,Gabby,Gladdin,ggladdinc@virginia.edu,Male,153.56.64.234,0
15,Mill,Chadwell,mchadwelle@archive.org,Male,15.126.32.220,0
```

## Contributing

Issues and pull requests are welcome. For more substantial contributions, please discuss the proposed changes first.

## License
Creative Commons Legal Code - CC0 1.0 Universal
