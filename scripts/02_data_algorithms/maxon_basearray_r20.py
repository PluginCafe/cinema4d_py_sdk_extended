"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Creates a BaseArray of maxon.Int (any maxon type is working).

Class/method highlighted:
    - maxon.BaseArray
    - BaseArray.Resize()

"""
import maxon


def main():
    # Creates a BaseArray of a maxon.Int
    intArray = maxon.BaseArray(maxon.Int)

    # Resizes the BaseArray
    intArray.Resize(10)

    # Iterates over the BaseArray and assign values
    for i in range(len(intArray)):
        intArray[i] = i

        print(intArray[i])


if __name__ == "__main__":
    main()