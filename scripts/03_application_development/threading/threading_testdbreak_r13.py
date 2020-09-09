"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Uses TestDBreak to define a custom condition to leave a thread.

Class/method highlighted:
    - c4d.threading.C4DThread
    - C4DThread.TestDBreak()

Compatible:
    - Win / Mac
    - R13, R14, R15, R16, R17, R18, R19, R20, R21, S22, R23
"""
import c4d
import time


class MyThread(c4d.threading.C4DThread):
    def __init__(self):
        self.count = 0

    # Called by self.TestBreak in Main
    def TestDBreak(self):
        if self.count == 10:
            return True
        return False

    # Called when MyThread.Start() is called
    def Main(self):

        # Iterates over 100
        for i in range(100):
            self.count = i

            # Checks if the thread is asked to quit and call TestDBreak for custom breaking condition
            if self.TestBreak():
                print("Leaving at 10")
                break

            print("Current:", i)
            time.sleep(1/25.)


def main():
    # Initializes the thread
    thread = MyThread()

    # Starts the thread
    thread.Start()

    # Waits until it's finished
    thread.Wait(False)

    # Closes the thread
    thread.End()


if __name__ == '__main__':
    main()
