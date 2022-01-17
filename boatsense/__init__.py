from logging import DEBUG, ERROR, INFO, WARNING
from logging import Logger, Formatter, StreamHandler
from logging import getLogger
from logging.handlers import TimedRotatingFileHandler
from os import environ

class Data:

    items = []
    funcs = []
    diffs = {}
    saves = []

class BME280(Data):

    items = ['temperature', 'humidity', 'pressure']
    diffs = {
        'temperature': 0.5,
        'pressure': 5,
        'humidity': 1
    }
    b = 17.62
    c = 243.12


class LSM9DS1(Data):

    items = ['acceleration', 'magnetic', 'gyro', 'temperature']
    diffs = {
        'acceleration': 0.1,
        'acceleration_z': 0.2,
        'magnetic': 0.03,
        'magnetic_z': 0.05,
        'gyro': 0.1,
        'temperature': 1.5
        }
    tuples = ['acceleration', 'magnetic', 'gyro']
    axis = ['x', 'y', 'z']


class GPS(Data):
    items = {
        '0': ['mode', 'sats', 'sats_valid'],
        '2': ['lat', 'lon', 'track', 'time', 'error'],
        '3': ['alt', 'climb']
        }
    funcs = {
        '0': [],
        '2': ['position', 'speed', 'position_precision', 'map_url'],
        '3': ['altitude', 'movement', 'speed_vertical'],
    }
    diffs = {
        'lat': 0.01,
        'lon': 0.01,
        'altitude': 1,
        'm_speed': 0.2,
        'm_climb': 0.2,
    }
    moves = ['speed', 'track', 'climb']


class CFG:
    '''config object class'''

    db_limit = environ.get('DB_LIMIT', 100)
    db_url = environ.get('DB_URL', "postgresql:///neal")
    initial_name_data = [
        {'name': 'heartbeat', 'sensor': False, 'asat': None},
        {'name': 'upload', 'sensor': False, 'asat': None},
        {'name': 'bme280', 'sensor': True, 'asat': None},
        {'name': 'lsm9ds1', 'sensor': True, 'asat': None},
        {'name': 'gps', 'sensor': True, 'asat': None}
    ]
    log_count =3
    log_file = '/tmp/boatsense.log'
    log_fmt_dt =  '%Y/%m/%d %H:%M:%S'
    log_fmt = '%(levelname)s:%(asctime)s:%(name)s:%(message)s'
    log_levels = {
        'debug': DEBUG,
        'info': INFO,
        'warning': WARNING,
        'error': ERROR
    }
    log_lvl = 'debug'
    log_when = 'midnight'
    map_data = {
        'lat': {'s': "{:>3d}*{:>5.2f}'{:1s}", 'p': 'N', 'n': 'S'},
        'lon': {'s': "{:>03d}*{:>5.2f}'{:1s}", 'p': 'E', 'n': 'W'}
    }
    name = 'boatsense'
    out = {
        'bme280': [
            'Temp: {temperature:>5.1f}C',
            'Humid: {humidity:>3.1f}%',
            'Press: {pressure:>4d} Pa',
            'Press 05: {pressure_05:>+4d} Pa',
            'Press 10: {pressure_10:>+4d} Pa',
            'Press 15: {pressure_15:>+4d} Pa',
            ''
        ],
        'lsm9ds1': [
            'A: {acceleration_x:>+7.3}x',
            '   {acceleration_y:>+7.3}y',
            '   {acceleration_z:>+7.3}z',
            'G: {gyro_x:>+7.3}x',
            '   {gyro_y:>+7.3}y',
            '   {gyro_z:>+7.3}z',
            'C: TBD'
        ],
        'gps': [
            'La: {lat_map}',
            'Lo: {lon_map}',
            'Speed: {m_speed:>-6.2f}',
            'Course: {m_track:3.1f}',
            'Alt: {altitude:5.1} {m_climb:-4.1}',
            'Lat: {lat:>-9.5f}*',
            'Lon: {lon:>-9.5f}*'
        ]
    },
    sensors = {
        'data': Data,
        'bme280': BME280,
        'lsm9ds1': LSM9DS1,
        'gps': GPS
    }
    timings = {
        'bme280': 20,
        'gps': 5,
        'lsm9ds1': 5,
        'heartbeat': 30,
        'upload': 60
    }
    mqtt = '192.168.15.148'
    mqtt_topic = "sensors/{}"
    udp_addr = ('192.168.15.255', 22001)

LG = getLogger(CFG.name)
LG.propagate = False

def setup_logger(lg: Logger):
    sth = StreamHandler()
    form1 = Formatter(CFG.log_fmt, datefmt=CFG.log_fmt_dt)
    sth.setFormatter(form1)
    lg.addHandler(sth)
    fh = TimedRotatingFileHandler(CFG.log_file, when=CFG.log_when, backupCount=CFG.log_count)
    form2 = Formatter(CFG.log_fmt, datefmt=CFG.log_fmt_dt)
    fh.setFormatter(form2)
    lg.addHandler(fh)
    lg.setLevel(CFG.log_levels[CFG.log_lvl])

setup_logger(LG)
