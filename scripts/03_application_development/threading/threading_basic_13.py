"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Demonstrates how to handle C4DThread from a script.

Class/method highlighted:
    - c4d.threading.C4DThread

Compatible:
    - Win / Mac
    - R13, R14, R15, R16, R17, R18, R19, R20, R21, S22, R23
"""
import c4d
import time


class MyThread(c4d.threading.C4DThread):

    def Main(self):

        # Iterates over 100
        for i in range(100):

            # Checks if thread is asked to quit
            if self.TestBreak():
                print("Leaving at 10")
                break

            print("Current:", i)
            time.sleep(1/25.)


def main():
    # Creates our thread
    thread = MyThread()

    # Starts our thread
    thread.Start()

    # Waits a bit to give the thread some time to perform some operations
    time.sleep(1)

    # Asks to close our Thread (making TestBreak returns True)
    thread.End()


if __name__ == '__main__':
    main()
