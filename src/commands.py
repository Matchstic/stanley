from typing import Tuple
from pymavlink import mavutil
from dronekit import LocationGlobal, LocationGlobalRelative, Vehicle
from constants import ALTITUDE, MINIMUM_DISTANCE
from convert import get_location_metres
import time
import math

ROI_STATE = False
LAST_YAW_UPDATE = 0

def setYaw(vehicle: Vehicle, yawRate: float) -> None:
    global LAST_YAW_UPDATE

    # Skip first call if the last update was never
    if LAST_YAW_UPDATE == 0:
        return

    now = time.time()

    timeDifference = now - LAST_YAW_UPDATE
    headingChange = yawRate * timeDifference

    msg = vehicle.message_factory.command_long_encode(
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_CMD_CONDITION_YAW,
        0, #confirmation
        headingChange,    # param 1, yaw in degrees
        yawRate,          # param 2, yaw speed deg/s
        1 if headingChange >= 0 else -1, # param 3, direction -1 ccw, 1 cw
        1, # param 4, relative offset 1, absolute angle 0
        0, 0, 0)    # param 5 ~ 7 not used

    vehicle.send_mavlink(msg)

def setROI(vehicle: Vehicle, position: Tuple[float, float, float], clear = False) -> None:
    lat, lon, alt = position

    msg = vehicle.message_factory.command_long_encode(
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_CMD_DO_SET_ROI,
        0, # confirmation
        3 if clear is False else 0, # ROI mode
        0, 0, 0, # params 2-4
        lat,
        lon,
        alt)

    vehicle.send_mavlink(msg)

def clearROI(vehicle: Vehicle) -> None:
    setROI(vehicle, (0, 0, 0), True)

def setPositionTarget(vehicle: Vehicle, position: Tuple[float, float], relativeYawRate: float) -> None:
    global ROI_STATE
    global LAST_YAW_UPDATE

    localNorth, localEast = position

    roiPosition = positionTarget(vehicle, position)

    # Set yaw either via ROI, or explicit rotation
    if localNorth != 0 and \
        localEast != 0:

        ROI_STATE = True

        # Handle yaw by setting ROI to the exact position
        setROI(vehicle, roiPosition)
    else:
        # Clear ROI state if set to freely control yaw
        if ROI_STATE is True:
            clearROI(vehicle)
            ROI_STATE = False

        setYaw(relativeYawRate)

    LAST_YAW_UPDATE = time.time()

    # Ensure the localNorth (i.e., depth) is reduced by 2 meters to maintain a safe distance away
    # This is allowed to go negative, to result in "backwards" navigation
    localNorth -= float(MINIMUM_DISTANCE)

    # Find altitude target
    currentAltitude = vehicle.location.global_relative_frame.alt
    targetAltOffset = ALTITUDE - currentAltitude

    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED, # Use offset from current position
        0b0000111111111000, # type_mask (only positions enabled)
        localNorth, localEast, targetAltOffset,
        0, 0, 0, # x, y, z velocity in m/s  (not used)
        0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)

    vehicle.send_mavlink(msg)

def positionTarget(vehicle: Vehicle, position: Tuple[float, float]) -> (LocationGlobal or LocationGlobalRelative):
    '''Computes a new global position target that is
    equal to the target position'''

    localNorth, localEast = position

    currentPosition = vehicle.location.global_relative_frame

    yaw = vehicle.attitude.yaw # radians
    east = (localEast * math.cos(yaw)) - (localNorth * math.sin(yaw))
    north = (localEast * math.sin(yaw)) + (localNorth * math.cos(yaw))

    return get_location_metres(currentPosition, north, east)