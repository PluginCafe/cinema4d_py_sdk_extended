"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Loops over all jobs of the render queue.
    - Prints the path if the jobs is not yet render.

Class/method highlighted:
    - c4d.documents.BatchRender
    - c4d.documents.GetBatchRender()
    - BatchRender.GetElementCount()
    - BatchRender.GetElementStatus()
    - BatchRender.GetElement()

Compatible:
    - Win / Mac
    - R13, R14, R15, R16, R17, R18, R19, R20, R21, S22
"""
import c4d


def main():
    # Retrieves the batch render instance
    br = c4d.documents.GetBatchRender()
    if br is None:
        raise RuntimeError("Failed to retrieve the batch render instance.")

    # Loops over the elements
    for i in range(br.GetElementCount()):
        # If the element is not finished, prints the path
        if br.GetElementStatus(i) != c4d.RM_FINISHED:
            print(br.GetElement(i))


if __name__ == "__main__":
    main()
