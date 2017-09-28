import os
import numpy as np
import pandas as pd
import csv
from scipy import interpolate

"""
This file contains functions to load weather data from 'typical' and
'actual' (recorded) weather data files.
"""

__author__ = 'Parag Rastogi'

# ISSUES TO ADDRESS
# 1. Harmonize WMO numbers - if the incoming number is 5 digits,
# add leading zero (e.g., Geneva)
# 2. Implement something to convert GHI to DNI and DHI.
# Maybe use Erbs model like before.

# List of keywords that identify TMY and AMY files.
keywords = dict(tmy=('nrel', 'iwec', 'ishrae', 'cwec',
                     'igdg', 'tmy3', 'meteonorm'),
                amy=('ncdc', 'nsrdb', 'nrel_indiasolar',
                     'ms', 'WY2', 'nasa_saudi'))
wformats = ('epw', 'espr', 'csv')

# List of values that could be NaNs.
nanlist = ('9900', '-9900', '9999', '99', '-99', '9999.9', '999.9', ' ', '-')


# %%
def get_weather(stcode, fpath, ftype='espr', outpath='xxx'):

    # This function calls the relevant reader based on the ftype.

    # Initialise as a non-object.
    wdata = None

    if os.path.isfile(fpath):
        print('Running weather file reader for station ' + 
              '{0}. Expecting format {1}.\r\n'.format(stcode, ftype))
    else:
        print('I cannot find file {0}.'.format(fpath) + \
              ' Returning empty dataframe.\r\n')
        return wdata
    
    # Load data for given station.

    if ftype == 'pickle':
        try:
            ts_in = pd.read_pickle(fpath)
            return ts_in
        except:
            print('You asked me to read a pickle but I could not. ' + \
                  'Trying all other formats.\r\n')
            wdata = None

    elif ftype == 'epw':
        
        try:
            wdata, _ = read_epw(fpath, stcode)
        except:
            wdata = None

    elif ftype == 'espr':

        try:
            wdata, _ = read_espr(fpath, stcode)
        except:
            wdata = None

    elif ftype == 'csv':

        try:
            wdata = pd.read_csv(fpath, header=0)
            wdata.columns = ['month', 'day', 'hour', 'tdb', 'tdp', 'rh',
                             'ghi', 'dni', 'dhi', 'wspd', 'wdr']
        except:
            wdata = None

    # End ftype if statement.
    
    # The first try didn't work for some reason.

    if wdata is None:
        print('I could not read the file you gave me with the format ' + \
              'you specified. Trying all readers.\r\n')
        
        # Once more unto the breach.
        
        for fmt in wformats:
            if fmt == 'epw':
                try:
                    wdata, _ = read_epw(fpath, stcode)
                except:
                    wdata = None
            elif fmt == 'espr':
                try:
                    wdata, _ = read_espr(fpath, stcode)
                except:
                    wdata = None
            elif fmt == 'csv':
                try:
                    wdata = pd.read_csv(fpath, header=0)
                    wdata.columns = ['month', 'day', 'hour', 'tdb', 'tdp',
                                     'rh', 'ghi', 'dni', 'dhi', 'wspd', 'wdr']
                except:
                    wdata = None
            
            if wdata is not None:
                break

    # End wformats for loop and if wdata is None.

    if wdata is None:
        print('All attempts to read your file were unsuccesful, ' + \
              'returning empty table.')
        return wdata

    else:
        ts_in = (np.vstack([
                wdata.month.values,
                wdata.index.dayofyear, wdata.hour.values,
                wdata.tdb.values, wdata.tdp.values,
                wdata.rh.values, wdata.ghi.values,
                wdata.dni.values, wdata.dhi.values,
                wdata.wspd.values, wdata.wdr.values])).T

        return ts_in

    # Ignore this bit of code for now.

    # Load actual data for given station
    # force = False
    # actualdata = read_others(stcode, force, sources, outpath=outpath)
    # Always use NCDC in addition to the country-specific weather source
    # (like meteosuisse), since that can help fill data.


# %%


def read_epw(fpath, stcode):

    # Names of the columns in EPW files.
    tmy_colnames = ['Year', 'Month', 'Day', 'Hour', 'Minute', 'QualFlags',
                    'TDB', 'TDP', 'RH', 'ATMPR', 'ETRH', 'ETRN', 'HIR',
                    'GHI', 'DNI', 'DHI', 'GHE', 'DNE', 'DHE', 'ZL',
                    'WDR', 'WSPD', 'TSKY', 'OSKY', 'VIS', 'CHGT',
                    'PWO', 'PWC', 'PWT', 'AOPT', 'SDPT',
                    'SLAST', 'UnknownVar1', 'UnknownVar2', 'UnknownVar3']

    # Uniform date index for all tmy weather data tables.
    dates = pd.date_range('1/1/2017', periods=8760, freq='H')

    # Convert the names to lowercase.
    tmy_colnames = [x.lower() for x in tmy_colnames]

    # List of EPW files.
    tmy_filelist = []

    # Look in folder for weather data files.
    if os.path.isdir(fpath):
        filepaths = [os.path.join(fpath, f.lower())
                     for f in (os.listdir(fpath))]
    else:
        filepaths = fpath

    if isinstance(filepaths, (list, tuple)):
        for f in filepaths:
            # Avoid AMY files.
            if 'epw' in f \
                and any(s in f.lower() for s in keywords['tmy']) \
                    and not any(s in f.lower() for s in keywords['amy']):
                tmy_filelist.append(f)
    else:
        tmy_filelist = [filepaths]

    #    # If this particular station has already been processed, then there
    #    # might be a pickle file with the data. Load that, unless forced.
    #    if os.path.isfile(picklepath) and not force:
    #        print('Pickle file exists.\r\n')
    #        typdata = pd.read_pickle(picklepath)
    #        return typdata, tmy_filelist
    #    elif os.path.isfile(csvpath) and not force:
    #        typdata = pd.read_csv(csvpath)
    #        return typdata, tmy_filelist

    didx = 0
    typdata = pd.DataFrame()
    

    for f in tmy_filelist:
    
        # All stations were NOT requested.
        # If they were, then this conditional will not activate.
        #        if stcode is not 'all':
        #            if stcode in f.lower():
        #                # File comes from requested station code.
        #                print('Reading tmy file for station {0}.'.format(stcode))
        #            else:
        #                # Current file is not from station code requested.
        #                continue

        # Read table, ignoring header lines.
        wdata_typ = pd.read_csv(f, delimiter=',', skiprows=8, header=None,
                                names=tmy_colnames)
        wdata_typ.index = dates

        if len(wdata_typ.columns) == 35:
            # Some files have three extra columns
            # (usually the TMY files from USDOE).
            # Delete those columns if found.
            wdata_typ = wdata_typ.drop(['unknownvar1', 'unknownvar2',
                                        'unknownvar3'], axis=1)

        # Read header and assign all metadata.
        with open(f, 'r') as epwfile:
            read_header = csv.reader(epwfile, delimiter=',')
            header = next(read_header)
            location = np.repeat(header[1], wdata_typ.shape[0])
            loccode = np.repeat(header[1].upper()[0:3], wdata_typ.shape[0])
            wmo = np.repeat(header[5], wdata_typ.shape[0])
            latitude = np.repeat(header[6], wdata_typ.shape[0])
            longitude = np.repeat(header[7], wdata_typ.shape[0])
            tz = np.repeat(header[8], wdata_typ.shape[0])
            altitude = np.repeat(header[9], wdata_typ.shape[0])

        # Assign header information to table.
        wdata_typ = wdata_typ.assign(
                latitude=latitude, longitude=longitude,
                altitude=altitude, wmo=wmo, tz=tz,
                location=location, loccode=loccode)
        if didx == 0:
            typdata = wdata_typ
        else:
            typdata = typdata.append(wdata_typ)

        didx += 1
        
    if typdata.empty:

        print('Could not locate a file with given station name.' +
              ' Returning empty table.\r\n')

    return typdata, tmy_filelist

# ----------- END read_epw function -----------


def read_espr(fpath='./che_geneva.iwec.a'):
    
    # Missing functionality - reject call if path points to binary file.

    fpath_fldr, fpath_name = os.path.split(fpath)
    sitename = fpath_name.split(sep='.')
    sitename = sitename[0]

    with open(fpath) as f:
        content = f.readlines()

    content = [x.strip() for x in content]

    # Split the contents into a header and body.
    header = content[0:13]
    body = content[12:]
    del content

    # Find the lines with day tags.
    daylines = [[idx, line] for [idx, line] in enumerate(body)
                if 'day' in line]

    dataout = np.zeros([8760, 11])

    dcount = 0

    for idx, day in daylines:

        # Get the next 24 lines.
        daylist = np.asarray(body[idx+1:idx+25])

        # Split each line of the current daylist into separate strings.
        splitlist = [element.split() for element in daylist]

        # Convert each element to a integer, then convert the resulting
        # list to a numpy array.
        daydata = np.asarray([list(map(int, x)) for x in splitlist])

        # Today's time slice.
        dayslice = range(dcount, dcount+24, 1)

        # This will split the day-month header line on the gaps.
        splitday = day.split()

        # Month.
        dataout[dayslice, 1] = np.repeat(int(splitday[-1]), len(dayslice))

        # Day of year.
        dataout[dayslice, 1] = np.repeat(int(splitday[2]), len(dayslice))

        # Hour (of day).
        dataout[dayslice, 2] = np.arange(0, 24, 1)

        # tdb, input is in deci-degrees, convert to degrees.
        dataout[dayslice, 3] = daydata[:, 1]/10

        # rh, in percent.
        dataout[dayslice, 5] = daydata[:, 5]

        # ghi, in W/m2.
        dataout[dayslice, 7] = daydata[:, 0]

        # dni, in W/m2.
        dataout[dayslice, 8] = daydata[:, 2]

        # wdr, input is in deci-m/s.
        dataout[dayslice, 9] = daydata[:, 3]/10

        # wspd, clockwise deg from north.
        dataout[dayslice, 10] = daydata[:, 4]


        dcount += 24

    # tdp, calculated from tdb and rh.
    dataout[:, 4] = tdb2tdp(dataout[:, 3], dataout[:, 5])


    clmdata = pd.DataFrame(data=dataout,
            columns=['month', 'day', 'hour',
                     'tdb', 'tdp', 'rh',
                     'ghi', 'dni', 'dhi',
                     'wspd', 'wdr'])

    return clmdata, header

# ----------- END read_espr function -----------


def read_others(stcode, sources, outpath='xxx',
                path_actual_top=os.path.join(
                        '..', '..', 'WeatherData', 'HistoricalData')):

    print('Pickle file {0} not found,\r\n'.format(picklepath) +
          'continuing to load from raw files.\r\n')

    # Create an empty data frame to be appended to later.
    actualdata = pd.DataFrame()

    if 'ncdc' in sources:
        path_ncdc = os.path.join(path_actual_top, 'ncdc')
        ncdc_filelist = [os.path.join(path_ncdc, o)
                         for o in os.listdir(path_ncdc)
                         if not os.path.isdir(os.path.join(path_ncdc, o))]
        ncdc_colnames = ['date', 'time', 'wdr', 'wspd',
                         'tdb', 'tdp', 'atmpr', 'rh']

        wdata_ncdc = pd.DataFrame()

        for f in ncdc_filelist:
            if stcode is 'all':
                print('I cannot load NCDC data for all stations -- ' +
                      'the resulting dataframe would be too big.\r\n')
                break

            if ('ncdc' in f) and (stcode in f):
                print('Processing station {0}.\r\n'.format(stcode))
                wdata_ncdc = pd.read_csv(f, delimiter=',', skiprows=2,
                                         header=None,
                                         usecols=[2, 3, 7, 10,
                                                  12, 14, 16, 18],
                                         na_filter=True,
                                         na_values=nanlist,
                                         names=ncdc_colnames,
                                         dtype=dict(date=str,
                                                    time=str))
                dater = wdata_ncdc['date'].str.extract(
                    '(\d{4})(\d{2})(\d{2})', expand=False)
                dater.columns = ['year', 'month', 'day']
                timer = wdata_ncdc['time'].str.extract(
                    '(\d{2})(\d{2})', expand=False)
                timer.columns = ['hour', 'minute']
                wdata_ncdc = pd.concat([dater, timer, wdata_ncdc],
                                       axis=1, join='inner')
                wdata_ncdc = wdata_ncdc.drop(['date', 'time'], axis=1)
                wdata_ncdc.index = pd.to_datetime(wdata_ncdc[[
                    'year', 'month', 'day', 'hour', 'minute']])
                break
            else:
                continue

        # The dataframe wdata_ncdc is renamed to actualdata.
        # In case only NCDC data is found, actual data
        # returned will consist only of NCDC data.
        actualdata = actualdata.append(wdata_ncdc)
        del wdata_ncdc

    if 'nsrdb' in sources:
        path_nsrdb = os.path.join(path_actual_top, 'nsrdb')
        nsrdb_filelist = [os.path.join(path_nsrdb, o)
                          for o in os.listdir(path_nsrdb)
                          if not os.path.isdir(os.path.join(path_nsrdb, o))]
        nsrdb_colnames = ['date', 'time', 'GHI_metstat',
                          'DNI_metstat', 'DHI_metstat',
                          'GHI_suny', 'DNI_suny', 'DHI_suny',
                          'GHI_measure', 'DNI_measure', 'DHI_measure']

        # Create an empty data frame to be appended to later.
        wdata_nsrdb = pd.DataFrame()

        for f in nsrdb_filelist:
            if stcode is 'all':
                print('I cannot load NSRDB data for all stations -- ' +
                      'the resulting dataframe would be too big.\r\n')
                actualdata = actualdata.append(wdata_nsrdb)
                break

            if all(s in f for s in ('nsrdb', 'csv', stcode)):
                wdata_nsrdb = pd.read_csv(f, delimiter=',', skiprows=1,
                                          header=None,
                                          usecols=[0, 1, 6, 9, 12, 15,
                                                   17, 19, 27, 29, 31],
                                          na_filter=True,
                                          names=nsrdb_colnames,
                                          na_values=nanlist,
                                          dtype=dict(date=str, time=str))
                dater = wdata_nsrdb['date'].str.extract(
                    '(\d{4})-(\d{2})-(\d{2})', expand=False)
                dater.columns = ['year', 'month', 'day']
                timer = wdata_nsrdb['time'].str.extract(
                    '(\d{1,2}):(\d{2})', expand=False)
                timer.columns = ['hour', 'minute']
                wdata_nsrdb = pd.concat([dater, timer, wdata_nsrdb],
                                        axis=1, join='inner')
                wdata_nsrdb = wdata_nsrdb.drop(['date', 'time'], axis=1)
                wdata_nsrdb.index = pd.to_datetime(
                    wdata_nsrdb[['year', 'month', 'day', 'hour', 'minute']])

                # Little bit of code to pick best values from the three
                # solar radiation types available in the NSRDB files.
                wdata_nsrdb = nsrdb_solar_clean(wdata_nsrdb)
            else:
                continue

            actualdata = actualdata.append(wdata_nsrdb)

    if 'meteosuisse' in sources:
        path_ms = os.path.join(path_actual_top, 'ms')
        ms_filelist = [os.path.join(path_ms, o) for o in os.listdir(path_ms)
                       if not os.path.isdir(os.path.join(path_ms, o))]
        ms_colnames = ['datetime', 'ghi', 'atmpr', 'tdb',
                       'rh', 'tdp', 'wspd', 'wdr']

        # Create an empty data frame to be appended to later.
        wdata_ms = pd.DataFrame()

        for f in ms_filelist:
            if stcode is 'all':
                print('I cannot load MeteoSuisse data for all stations -- ' +
                      'the resulting dataframe would be too big.\r\n')
                actualdata = actualdata.append(wdata_ms)
                break

            if all(s in f for s in ('meteosuisse', 'txt', stcode)):
                wdata_ms = pd.read_csv(f, delimiter=';', skiprows=1,
                                       header=None,
                                       usecols=[1, 2, 3, 4, 5, 6, 7, 8],
                                       na_filter=True, na_values=nanlist,
                                       names=ms_colnames,
                                       dtype=dict(datetime=str,
                                                  ghi=np.float64,
                                                  atmpr=np.float64,
                                                  tdb=np.float64,
                                                  rh=np.float64,
                                                  tdp=np.float64,
                                                  wspd=np.float64,
                                                  wdr=np.float64))
                dater = wdata_ms['datetime'].str.extract(
                    '(\d{4})(\d{2})(\d{2})(\d{2})', expand=False)
                dater['minute'] = (np.zeros(dater.shape[0])).tolist()
                dater.columns = ['year', 'month', 'day', 'hour', 'minute']

                wdata_ms = pd.concat([dater, wdata_ms], axis=1, join='inner')
                wdata_ms = wdata_ms.drop(['datetime'], axis=1)
                wdata_ms.index = pd.to_datetime(
                    wdata_ms[['year', 'month', 'day', 'hour', 'minute']])

                # Put in dummies for DNI, DHI and WMO.
                wdata_ms['dni'] = (np.zeros(wdata_ms.shape[0])).tolist()
                wdata_ms['dhi'] = (np.zeros(wdata_ms.shape[0])).tolist()
                # wdata_ms['wmo'] = (np.zeros(wdata_ms.shape[0])).tolist()

            else:
                continue

            actualdata = actualdata.append(wdata_ms)

    # If blank, output blank.
    if actualdata.empty:
        print('Could not locate any files with given station name. ' +
              'Returning empty table.\r\n')
        return actualdata
    else:
        # delete  the minute column
        del actualdata['minute']
        # Reorganise columns and return.
        actualdata = actualdata[['year', 'month', 'day', 'hour',
                                 'tdb', 'tdp', 'rh',
                                 'ghi', 'dni', 'dhi',
                                 'wdr', 'wspd', 'atmpr']]

        # Convert time columns to numbers.
        actualdata.year = pd.to_numeric(actualdata.year)
        actualdata.month = pd.to_numeric(actualdata.month)
        actualdata.day = pd.to_numeric(actualdata.day)
        actualdata.hour = pd.to_numeric(actualdata.hour)

        tempdata = pd.DataFrame()
        for col in list(actualdata):
            tempdata[col] = actualdata.groupby(['year',
                    'month', 'day', 'hour'])[col].mean()

        # If all elements of a row are nans, then discard that row.
        tempnans = tempdata.apply(np.isnan, axis=1)
        nancheck = tempnans.all(axis=1).values

        actualdata = pd.DataFrame()

        for col in list(tempdata):
            actualdata[col] = tempdata[col][np.logical_not(nancheck)]

        del tempdata

        # Final sanity checks.
        notnans = actualdata.tdb.values[np.logical_not(
                np.isnan(actualdata.tdb.values))]
        notnanidx = np.logical_not(np.isnan(actualdata.tdb.values))
        notnans[(notnans > 55) | (notnans < -55)] = np.nan

        actualdata.tdb.values[notnanidx] = notnans

        notnans = actualdata.tdp.values[np.logical_not(
                np.isnan(actualdata.tdp.values))]
        notnanidx = np.logical_not(np.isnan(actualdata.tdp.values))
        notnans[(notnans > 60) | (notnans < -60)] = np.nan

        actualdata.tdp.values[notnanidx] = notnans

        # Reassing original index.
        actualdata.index = pd.to_datetime(
                    actualdata[['year', 'month', 'day', 'hour']])

        pd.to_pickle(actualdata, picklepath)
        actualdata.to_csv(csvpath, na_rep='NA')

        return actualdata

# ----------- END read_others function -----------


def nsrdb_solar_clean(wdata_nsrdb):

    wdata_copy = wdata_nsrdb.copy()

    metstat = wdata_copy.GHI_metstat
    measure = wdata_copy.GHI_measure

    idx = 0
    temp = wdata_copy.GHI_suny

    wdata_copy = wdata_copy.drop([
            'GHI_suny', 'GHI_metstat', 'GHI_measure'], axis=1)

    for e in temp:
        if not np.isnan(e):
            continue
        else:
            if not np.isnan(metstat[idx]):
                temp[idx] = metstat[idx]
            else:
                if not np.isnan(measure[idx]):
                    temp[idx] = measure[idx]
                else:
                    temp[idx] = float('nan')

        idx += 1

    wdata_copy = pd.concat([temp, wdata_copy], axis=1, join='inner')
    wdata_copy = wdata_copy.rename(columns={'GHI_suny': 'ghi'})

    # Do the same for the DNI columns.

    metstat = wdata_copy.DNI_metstat
    measure = wdata_copy.DNI_measure

    idx = 0
    temp = wdata_copy.DNI_suny

    wdata_copy = wdata_copy.drop([
            'DNI_suny', 'DNI_metstat', 'DNI_measure'], axis=1)

    for e in temp:
        if not np.isnan(e):
            continue
        else:
            if not np.isnan(metstat[idx]):
                temp[idx] = metstat[idx]
            else:
                if not np.isnan(measure[idx]):
                    temp[idx] = measure[idx]
                else:
                    temp[idx] = float('nan')

        idx += 1

    wdata_copy = pd.concat([temp, wdata_copy], axis=1, join='inner')
    wdata_copy = wdata_copy.rename(columns={'DNI_suny': 'dni'})

    # And for DHI.

    metstat = wdata_copy.DHI_metstat
    measure = wdata_copy.DHI_measure

    idx = 0
    temp = wdata_copy.DHI_suny

    wdata_copy = wdata_copy.drop([
            'DHI_suny', 'DHI_metstat', 'DHI_measure'], axis=1)

    for e in temp:
        if not np.isnan(e):
            continue
        else:
            if not np.isnan(metstat[idx]):
                temp[idx] = metstat[idx]
            else:
                if not np.isnan(measure[idx]):
                    temp[idx] = measure[idx]
                else:
                    temp[idx] = float('nan')

        idx += 1

    wdata_copy = pd.concat([temp, wdata_copy], axis=1, join='inner')
    wdata_copy = wdata_copy.rename(columns={'DHI_suny': 'dhi'})

    return wdata_copy


def weather_stats(data, key, stat):

    a = data.groupby(key)

    if stat is 'mean':
        b = a.mean()
    elif stat is 'sum':
        b = a.sum()
    elif stat is 'max':
        b = a.max()
    elif stat is 'min':
        b = a.min()
    elif stat is 'std':
        b = a.std()
    elif stat is 'q1':
        b = a.quantile(0.25)
    elif stat is 'q3':
        b = a.quantile(0.75)
    elif stat is 'med':
        b = a.median()

    return b


def tdb2tdp(tdb, rh):

    # Change relative humidity to fraction.
    phi = rh/100

    # Remove weird values.
    phi[phi>1] = 1
    phi[phi<0] = 0

    # Convert tdb to Kelvin.
    tdb_k = tdb + 273.15

    # Equations for calculating the saturation pressure
    # of water vapour, taken from ASHRAE Fundamentals 2009.
    # (Eq. 5 and 6, Psychrometrics)

    # Constants for Eq. 5, Temperature -200°C to 0°C.
    c1 = -5.6745359*10**3
    c2 = 6.3925247
    c3 = -9.6778430*10**-3
    c4 = 6.2215701*10**-7
    c5 = 2.0747825*10**-9
    c6 = -9.4840240*10**-13
    c7 = 4.1635019

    # Constants for Eq. 6, Temperature 0°C to 200°C.
    c8 = -5.8002206*10**3
    c9 = +1.3914993
    c10 = -4.8640239*10**-2
    c11 = +4.1764768*10**-5
    c12 = -1.4452093*10**-8
    c13 = +6.5459673

    # This is to distinguish between the two versions of equation 5.
    ice = tdb_k <= 273.15

    lnp_ws = np.zeros(tdb_k.shape)

    # Eq. 5, pg 1.2
    lnp_ws[ice] = c1/tdb_k[ice] + c2 + c3*tdb_k[ice] + c4*tdb_k[ice]**2 + \
        c5*tdb_k[ice]**3 + c6*tdb_k[ice]**4 + c7*np.log(tdb_k[ice])

    # Eq. 6, pg 1.2
    lnp_ws[np.logical_not(ice)] = c8/tdb_k[np.logical_not(ice)] + c9 + \
        c10*tdb_k[np.logical_not(ice)] + \
        c11*tdb_k[np.logical_not(ice)]**2 + \
        (c12*tdb_k[np.logical_not(ice)])**3 + \
        c13*np.log(tdb_k[np.logical_not(ice)])

    # Temperature in the above formulae must be absolute,
    # i.e. in Kelvin

    # THIS step is generating a lot of inf and nan - check against fundamentals handbook.

    # Continuing from eqs. 5 and 6
    p_ws = np.e**(lnp_ws)  # [Pa]

    # Eq. 24, pg 1.8
    p_w = (phi * p_ws) / 1000  # [kPa]

    # Constants for Eq. 39
    c14 = 6.54
    c15 = 14.526
    c16 = 0.7389
    c17 = 0.09486
    c18 = 0.4569

    alpha = np.log(p_w)
    idx = np.arange(0, alpha.size)
    duds = np.logical_or(np.isinf(alpha), np.isnan(alpha))
    int_func = interpolate.interp1d(
            idx, alpha, kind='nearest', fill_value='extrapolate')
    alpha[duds] = int_func(idx[duds])

    # Eq. 39
    tdp = c14 + c15*alpha + c16*(alpha**2) + c17*(alpha**3) + \
        c18*(p_w**0.1984)

    # Eq. 40, TDP less than 0°C and greater than 93°C
    tdp_ice = np.logical_or(tdp < 0, np.isnan(tdp), np.isinf(tdp))
    tdp[tdp_ice] = 6.09 + 12.608*alpha[tdp_ice] + 0.4959*(alpha[tdp_ice]**2)

    return tdp