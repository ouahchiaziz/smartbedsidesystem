from src.smart_bedside_error import SmartBedsideError

try:
    import RPi.GPIO as GPIO
except ImportError:
    from mock import GPIO

try:
    from pinpong.libs.dfrobot_max30102 import DFRobot_BloodOxygen_S
except ImportError:
    from mock.max30102 import DFRobot_BloodOxygen_S


class SmartBedsideSystem:

    # BOARD (physical) numbers of the pins the components are connected to.
    BUZZER_PIN = 22  # KY-012 active buzzer used as the alarm (see User Story #2).
    BUTTON_PIN = 16  # B3F-1020 pushbutton used to stop the alarm (see User Story #3).
    O2_SERVO_PIN = 12  # MG90S servo motor controlling the oxygen delivery valve (see User Story #4).

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)  # Refer to the GPIO pins by their physical number on the board.
        GPIO.setwarnings(False)  # Disable warnings.

        self.spo2_hr_sensor = DFRobot_BloodOxygen_S()
        self.spo2_hr_sensor.begin()
        self.spo2_hr_sensor.sensor_start_collect()

        GPIO.setup(self.BUTTON_PIN, GPIO.IN)
        GPIO.setup(self.BUZZER_PIN, GPIO.OUT)
        GPIO.setup(self.O2_SERVO_PIN, GPIO.OUT)

        self.alarm_on = False  # Replace None by initializing the alarm status (see User Story #2).

        self.o2_servo = GPIO.PWM(self.O2_SERVO_PIN, 50)  # Replace None by initializing the servo motor's PWM instance (see User Story #4).
        self.o2_servo.start(5.0)

        self.o2_valve_angle = 0.0  # Replace None by initializing the valve angle, in degrees (see User Story #4).

    def read_vital_signs(self) -> int:
        spo2 = self.spo2_hr_sensor.get_spo2()

        if spo2 == -1:
            raise SmartBedsideError()

        return spo2

    def manage_alarm(self) -> None:
        spo2 = self.read_vital_signs()

        if spo2 < 88:
            GPIO.output(self.BUZZER_PIN, True)
            self.alarm_on = True
        else:
            GPIO.output(self.BUZZER_PIN, False)
            self.alarm_on = False
        # See User Story #2.

    def stop_alarm(self) -> None:
        if GPIO.input(self.BUTTON_PIN):
            GPIO.output(self.BUZZER_PIN, False)
            self.alarm_on = False
        # See User Story #3.

    def set_o2_valve_angle(self, angle: float) -> None:
        if angle < 0 or angle > 180:
            raise SmartBedsideError()

        duty_cycle = 5.0 + (angle / 180.0) * 5.0

        self.o2_servo.ChangeDutyCycle(duty_cycle)
        self.o2_valve_angle = angle

        # See User Story #4.

    def manage_oxygen_valve(self) -> None:
        spo2 = self.read_vital_signs()

        if spo2 < 95:
            self.set_o2_valve_angle(180)
        else:
            self.set_o2_valve_angle(0)
        # See User Storry #5.
