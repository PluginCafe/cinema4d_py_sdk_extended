"""
Copyright: MAXON Computer GmbH
Author: Yannick Puech

Description:
    - Hides the objects of the active LOD object 'op' current level.

Class/method highlighted:
    - LodObject.GetCurrentLevel()
    - LodObject.GetShowControlDescID()

Compatible:
    - Win / Mac
    - R19, R20, R21
"""
import c4d

def main():
    # Checks if there is an active object
    if op: return

    # Checks if active object is a LOD object
    if not op.CheckType(c4d.Olod): return

    # Gets active LOD object current level
    currentLevel = op.GetCurrentLevel()

    # Hides current level
    showControlID = op.GetShowControlDescID(currentLevel)
    if showControlID is not None:
        op[showControlID] = False

        # Pushes an update event to Cinema 4D
        c4d.EventAdd()

if __name__ == '__main__':
    main()