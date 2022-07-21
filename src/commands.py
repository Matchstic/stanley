from typing import Tuple
from pymavlink import mavutil
from dronekit import Vehicle
from constants import ALTITUDE, SPEED

IS_LOITER = False
LOITER_POSITION = {
    "latitude": 0,
    "longitude": 0
}

def setYaw(vehicle: Vehicle, relativeYaw: float) -> None:
    msg = vehicle.message_factory.command_long_encode(
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_CMD_CONDITION_YAW,
        0, #confirmation
        abs(relativeYaw),    # param 1, yaw in degrees
        0,          # param 2, yaw speed deg/s
        1 if relativeYaw >= 0 else -1, # param 3, direction -1 ccw, 1 cw
        1, # param 4, relative offset 1, absolute angle 0
        0, 0, 0)    # param 5 ~ 7 not used

    vehicle.send_mavlink(msg)
    vehicle.flush()

def setPositionTarget(vehicle: Vehicle, position: Tuple[float, float], relativeYaw: float) -> None:
    global IS_LOITER

    localNorth, localEast = position

    if localNorth == 0 and localEast == 0:
        # Loiter in place with guided mode
        setLoiterGuided(vehicle)
    else:
        IS_LOITER = False

        # Find altitude target for NED frame
        currentAltitude = vehicle.location.global_relative_frame.alt
        targetAltOffset = 0.0 - (ALTITUDE - currentAltitude) # up is negative

        msg = vehicle.message_factory.set_position_target_local_ned_encode(
            0,       # time_boot_ms (not used)
            0, 0,    # target system, target component
            mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED, # Use offset from current position
            0b0000111111111000, # type_mask (only positions enabled)
            localNorth, localEast, targetAltOffset,
            SPEED, SPEED, SPEED, # x, y, z velocity in m/s  (not used)
            0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
            0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)

        vehicle.send_mavlink(msg)

    setYaw(vehicle, relativeYaw)

def setLoiterGuided(vehicle: Vehicle) -> None:
    global IS_LOITER
    global LOITER_POSITION

    if IS_LOITER != True:
        IS_LOITER = True

        # update position
        frame = vehicle.location.global_relative_frame
        LOITER_POSITION = {
            "latitude": frame.lat,
            "longitude": frame.lon
        }

    msg = vehicle.message_factory.set_position_target_global_int_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT, # frame
        0b0000111111111000, # type_mask (only speeds enabled)
        int(LOITER_POSITION["latitude"] * 1e7), # lat_int - X Position in WGS84 frame in 1e7 * meters
        int(LOITER_POSITION["longitude"] * 1e7), # lon_int - Y Position in WGS84 frame in 1e7 * meters
        ALTITUDE,
        SPEED, # X velocity in NED frame in m/s
        SPEED, # Y velocity in NED frame in m/s
        SPEED, # Z velocity in NED frame in m/s
        0, 0, 0, # afx, afy, afz acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)

    vehicle.send_mavlink(msg)
