#!/usr/bin/env python3
#

from logging import DEBUG, ERROR, INFO, WARNING


class Data:

    items = []
    funcs = []
    diffs = {}
    saves = []
    table_1 = '''
create table if not exists updates (
    name text primary key,
    asat real not null
)
'''
    table_2 = '''
create table if not exists reads (
    name text primary key,
    asat real not null
)
'''
    insert = '''
insert or replace into updates(name, asat) values (?, ?)
'''

    
class BME280:

    items = ['temperature', 'humidity', 'pressure']
    funcs = []
    diffs = {
        'temperature': 0.5,
        'pressure': 5,
        'humidity': 1
    }
    saves = [
        'asat_real', 'temperature', 'humidity', 'pressure', 'pressure_05',
        'pressure_10', 'pressure_15'
    ]
    b = 17.62
    c = 243.12
    table = '''
create table if not exists bme280 (
    asat real primary key,
    temperature real not null,
    pressure real not null,
    humidity real not null,
    pressure_05 real not null,
    pressure_10 real not null,
    pressure_15 real not null
)
'''
    insert = '''
insert into bme280(asat, temperature, pressure, humidity, pressure_05, pressure_10, pressure_15) values (?, ?, ?, ?, ?, ?, ?)
'''

    
class LSM9DS1:
    
    items = ['acceleration', 'magnetic', 'gyro', 'temperature']
    funcs = []
    diffs = {
        'acceleration': 0.1,
        'acceleration_z': 0.2,
        'magnetic': 0.03,
        'magnetic_z': 0.05,
        'gyro': 0.1,
        'temperature': 1.5
        }
    saves = [
        'asat_real', 'acceleration_x', 'acceleration_y', 'acceleration_z',
        'magnetic_x', 'magnetic_y', 'magnetic_z', 'gyro_x', 'gyro_x',
        'gyro_x', 'temperature'
    ]
    tuples = ['acceleration', 'magnetic', 'gyro']
    axis = ['x', 'y', 'z']
    table = '''
create table if not exists lsm9ds1 (
    asat real primary key,
    acceleration_x real not null,
    acceleration_y real not null,
    acceleration_z real not null,
    magnetic_x real not null,
    magnetic_y real not null,
    magnetic_z real not null,
    gyro_x real not null,
    gyro_y real not null,
    gyro_z real not null,
    temperature real
)
'''
    insert = '''
insert into lsm9ds1(asat, acceleration_x, acceleration_y, acceleration_z, magnetic_x, magnetic_y, magnetic_z, gyro_x, gyro_y, gyro_z, temperature) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
'''

    
class GPS:

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
        'altitude': 0.3,
        'm_speed': 0.2,
        'm_climb': 0.2,
    }
    moves = ['speed', 'track', 'climb']
    saves = ['asat_real', 'mode', 'sats_valid', 'lat', 'lon', 'altitude',
                 'm_speed', 'm_track', 'm_climb']
    table = '''
create table if not exists gps (
    asat real primary key,
    mode integer not null,
    sats_valid integer not null,
    lat real not null,
    lon real not null,
    altitude real not null,
    m_speed real not null,
    m_track real not null,
    m_climb real not null
)
'''
    insert = '''
insert into gps(asat, mode, sats_valid, lat, lon, altitude, m_speed, m_track, m_climb) values (?, ?, ?, ?, ?, ?, ?, ?, ?)
'''
    
class CFG:

#    db_file = "/extra/boatsense/boatsense.db"
    db_file = ":memory:"
    log_file = '/tmp/boatsense-client.log'
    log_fmt_dt =  '%Y/%m/%d %H:%M:%S'
    log_fmt = '%(levelname)s:%(asctime)s:%(name)s:%(message)s'
    log_levels = {
        'debug': DEBUG,
        'info': INFO,
        'warning': WARNING,
        'error': ERROR
    }
    log_lvl = 'debug'
    name = 'BoatSense'
    timings = {
        'bme280': 5,
        'gps': 1,
        'lsm9ds1': 1,
        'heartbeat': 20
    }
    sensors = {
        'data': Data,
        'bme280': BME280,
        'lsm9ds1': LSM9DS1,
        'gps': GPS
    }
