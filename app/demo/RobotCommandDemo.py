import time

import RPi.GPIO as GPIO
import spidev

from lib.lib_nrf24.lib_nrf24 import NRF24

GPIO.setmode(GPIO.BCM)

pipes = [[0xE0, 0xE0, 0xF1, 0xF1, 0xE0], [0xF1, 0xF1, 0xF0, 0xF0, 0xE0]]
radio = NRF24(GPIO, spidev.SpiDev())
radio.begin(1, 4)
radio.setPayloadSize(32)
radio.setChannel(50)
radio.setDataRate(NRF24.BR_1MBPS)
radio.setPALevel(NRF24.PA_HIGH)
radio.setAutoAck(False)
radio.enableDynamicPayloads()

radio.openWritingPipe(pipes[0])
radio.powerUp()
radio.printDetails()


def main():
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
                print("1 - Start Move Steps")
                print("2 - Start Move CM")
                print("3 - Start Rotate Degrees")
                print("4 - Start Rotate Steps")
                print("5 - Set Speed")
                print("100 - Go back")
                cmd = int(input("Choose Command"))

                if cmd == 0:
                    pass
                elif cmd == 1:
                    steps = int(input("Amount of steps to move? (0-65535)"))
                    params.append(steps >> 8)
                    params.append(steps & 0xFF)
                    print(params)
                    dir = input("Direction to move in? (0/1) (Optional)")
                    if len(dir.strip()) > 0:
                        params.append(int(dir))
                elif cmd == 2:
                    cm = int(input("Amount of CM to move? (0-65535)"))
                    params.append(cm >> 8)
                    params.append(cm & 0xF)
                    dir = input("Direction to move in? (0/1) (Optional)")
                    if len(dir.strip()) > 0:
                        params.append(int(dir))
                elif cmd == 3:
                    degrees = int(input("Angle in degrees to rotate? (0-65535)"))
                    params.append(degrees >> 8)
                    params.append(degrees & 0xF)
                    dir = input("Direction to rotate in? (left=0,right=1)")
                    if len(dir.strip()) > 0:
                        params.append(int(dir))
                elif cmd == 4:
                    steps = int(input("Amount of steps to rotate? (0-65535)"))
                    params.append(steps >> 8)
                    params.append(steps & 0xF)
                    dir = input("Direction to rotate in? (left=0,right=1)")
                    if len(dir.strip()) > 0:
                        params.append(int(dir))
                elif cmd == 6:
                    steps = int(input("New Speed? (0-255)"))
                    params.append(steps)

            cmd_lst = [
                cat << 5 | (cmd & 0x1f),
                current_message_id,
                *params
            ]

            current_message_id += 1

            start = time.time()  # start the time for checking delivery time
            print("Status: " + hex(radio.get_status()))
            print("Message: " + str(cmd_lst))
            print("Code: " + str(radio.write(cmd_lst)))  # just write the message to radio


if __name__ == '__main__':
    main()