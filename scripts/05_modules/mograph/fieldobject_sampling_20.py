"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Samples arbitrary points within a random field.

Class/method highlighted:
    - c4d.modules.mograph.FieldObject
    - c4d.modules.mograph.FieldInput
    - c4d.modules.mograph.FieldInfo
    - c4d.modules.mograph.FieldOutput

Compatible:
    - Win / Mac
    - R20, R21
"""
import c4d


def main():
    # Checks if the selected object is a random field object
    if op is None:
        raise ValueError("op is none, please select one object.")

    if not op.CheckType(c4d.Frandom):
        raise TypeError("Selected object is not a random field.")

    # Creates a list of 10 points to sample
    sampleCount = 10
    positions = []
    offset = 0.0
    for i in xrange(sampleCount):
        positions.append(c4d.Vector(offset, 0, 0))
        offset += 10.0

    # Creates FieldInput
    input = c4d.modules.mograph.FieldInput(positions, sampleCount)
    if input is None:
        raise MemoryError("Failed to create a FieldInput.")

    # Creates FieldInfo
    flags = c4d.FIELDSAMPLE_FLAG_VALUE
    thread = c4d.threading.GeGetCurrentThread()
    currentThreadIndex = 0
    threadCount = 1
    info = c4d.modules.mograph.FieldInfo.Create(flags, thread, doc, currentThreadIndex, threadCount, input)
    if info is None:
        raise MemoryError("Failed to create a FieldInfo.")

    # Creates FieldOutput
    output = c4d.modules.mograph.FieldOutput()
    if output is None:
        raise MemoryError("Failed to create a FieldOutput.")
    output.Resize(sampleCount, c4d.FIELDSAMPLE_FLAG_VALUE)

    # Samples the data
    op.InitSampling(info)
    op.Sample(input, output.GetBlock(), info, c4d.FIELDOBJECTSAMPLE_FLAG_DISABLEDIRECTIONFALLOFF)
    op.FreeSampling(info)

    # Prints the values for the sampled points
    print(output)


if __name__ == '__main__':
    main()