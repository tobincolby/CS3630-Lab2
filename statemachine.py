''' Take a picture

Takes most recent image from Cozmo
Converts it to 8-bit black and white
Saves to destination
'''

import sys
import cozmo
import numpy
import datetime
import time
from imgclassification import ImageClassifier




def run(sdk_conn):
    img_clf = ImageClassifier()

    # load images
    (train_raw, train_labels) = img_clf.load_data_from_folder('./train/')

    # convert images into features
    train_data = img_clf.extract_image_features(train_raw)

    # train model and test on training data
    img_clf.train_classifier(train_data, train_labels)

    robot = sdk_conn.wait_for_robot()
    robot.camera.image_stream_enabled = True
    robot.camera.color_image_enabled = False
    robot.camera.enable_auto_exposure()

    robot.set_head_angle(cozmo.util.degrees(0)).wait_for_completed()
    robot.say_text('Ready').wait_for_completed()
    IDLE = 'idle'
    DRONE = 'drone'
    ORDER = 'order'
    INSPECTION = 'inspection'
    NONE = 'none'

    current_state = IDLE

    while True:
        if current_state == IDLE:
            latest_image = robot.world.latest_image
            new_image = latest_image.raw_image
            new_image = numpy.asarray(new_image)
            features = img_clf.extract_image_features([new_image])
            predicted = img_clf.predict_labels(features)[0]
            if predicted == DRONE:
                robot.say_text(predicted).wait_for_completed()
                current_state = DRONE
            elif predicted == ORDER:
                robot.say_text(predicted).wait_for_completed()
                current_state = ORDER
            elif predicted == INSPECTION:
                robot.say_text(predicted).wait_for_completed()
                current_state = INSPECTION
            elif not predicted == NONE:
                robot.say_text(predicted).wait_for_completed()
        elif current_state == DRONE:
            robot.turn_in_place(angle=cozmo.util.Angle(degrees=90),
                                speed=cozmo.util.Angle(degrees=90)).wait_for_completed()
            cube = robot.world.wait_for_observed_light_cube()
            robot.pickup_object(cube, num_retries=5).wait_for_completed()
            robot.drive_straight(cozmo.util.Distance(distance_mm=100), cozmo.util.Speed(speed_mmps=50)).wait_for_completed()
            robot.place_object_on_ground_here(cube).wait_for_completed()
            robot.drive_straight(cozmo.util.Distance(distance_mm=-100), cozmo.util.Speed(speed_mmps=50)).wait_for_completed()
            current_state = IDLE
        elif current_state == ORDER:
            robot.drive_wheels(l_wheel_speed=20, r_wheel_speed=40, duration=30)
            current_state = IDLE
        elif current_state == INSPECTION:
            robot.turn_in_place(angle=cozmo.util.Angle(degrees=90),
                                speed=cozmo.util.Angle(degrees=90)).wait_for_completed()
            for i in range(4):

                lift = robot.set_lift_height(height=1, max_speed=0.5, in_parallel=True)
                straight = robot.drive_straight(distance=cozmo.util.Distance(distance_mm=200), speed=cozmo.util.Speed(speed_mmps=50), in_parallel=True)
                lift.wait_for_completed()
                lower = robot.set_lift_height(height=0, max_speed=0.5, in_parallel=True)
                straight.wait_for_completed()
                lower.wait_for_completed()
                robot.turn_in_place(angle=cozmo.util.Angle(degrees=90),
                                           speed=cozmo.util.Angle(degrees=90)).wait_for_completed()
            robot.set_lift_height(height=0, max_speed=0.5, accel=0, in_parallel=True).wait_for_completed()
            current_state = IDLE









if __name__ == '__main__':
    cozmo.setup_basic_logging()

    try:
        cozmo.connect(run)
    except cozmo.ConnectionError as e:
        sys.exit("A connection error occurred: %s" % e)
