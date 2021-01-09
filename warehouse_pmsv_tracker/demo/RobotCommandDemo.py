from warehouse_pmsv_tracker.robot.lib import NRF24
from RPi import GPIO
from spidev import SpiDev
import time

GPIO.setmode(GPIO.BCM)

pipes = [[0xE0, 0xE0, 0xF1, 0xF1, 0xE4], [0xE0, 0xE0, 0xF1, 0xF1, 0xE4]]
radio = NRF24(GPIO, SpiDev())
radio.begin(0, 17)
radio.setPayloadSize(32)
radio.setChannel(50)
radio.setDataRate(NRF24.BR_1MBPS)
radio.setPALevel(NRF24.PA_HIGH)
radio.setAutoAck(False)
radio.enableDynamicPayloads()

radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1, pipes[1])
radio.powerUp()

radio.printDetails()


def robot_command_demo():
    current_message_id = 0

    while True:
        print("Choose a category:")
        print("0 - General Commands")
        print("1 - Action Commands")
        print("2 - Measurement Commands")
        print("3 - Exit Program")

        cat = int(input("Enter your choice: "))

        if cat == 3:
            exit(0)

        while True:
            print("Choose a command:")
            cmd = 100
            params = []
            if cat == 0:
                print("0 - Set communication activemode")
                print("100 - Go back")
                cmd = int(input("Choose Command"))
            if cat == 1:
                print("0 - Cancel Movement")
                print("1 - Start Move CM")
                print("2 - Start Rotate Degrees")
                print("3 - Set Speed")
                print("100 - Go back")
                cmd = int(input("Choose Command"))

                if cmd == 0:
                    pass
                elif cmd == 1:
                    cm = int(input("Amount of MM to move? (0-65535)"))
                    params.append(cm >> 8)
                    params.append(cm & 0xFF)
                    dir = input("Direction to move in? (0/1) (Optional)")
                    if len(dir.strip()) > 0:
                        params.append(int(dir))
                elif cmd == 2:
                    degrees = int(input("Angle in degrees to rotate? (0-65535)"))
                    params.append(degrees >> 8)
                    params.append(degrees & 0xF)
                    dir = input("Direction to rotate in? (left=0,right=1)")
                    if len(dir.strip()) > 0:
                        params.append(int(dir))
                elif cmd == 3:
                    steps = int(input("New Speed? (0-255)"))
                    params.append(steps)

            cmd_lst = [
                cat << 5 | (cmd & 0x1f),
                current_message_id,
                *params
            ]

            current_message_id += 1

            print("Status: " + hex(radio.get_status()))
            print("Message: " + str(cmd_lst))
            radio.stopListening()
            print("Code: " + str(radio.write(cmd_lst)))  # just write the message to radio
            radio.startListening()
            start = time.time()  # start the time for checking delivery time

            while (time.time() - start) < 15:
                pip = [0]
                if radio.available(pip):
                    print("wahoo")
                    print(pip)
                    break



if __name__ == '__main__':
    robot_command_demo()