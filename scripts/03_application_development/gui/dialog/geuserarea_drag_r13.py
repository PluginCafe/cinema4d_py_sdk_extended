"""
Copyright: MAXON Computer GmbH
Author: Maxime Adam

Description:
    - Creates and attaches a GeUserArea to a Dialog.
    - Creates a series of aligned squares, that can be dragged and swapped together.

Note:
    - This example uses weakref, I encourage you to read https://pymotw.com/2/weakref/.

Class/method highlighted:
    - c4d.gui.GeUserArea
    - GeUserArea.DrawMsg
    - GeUserArea.InputEvent
    - GeUserArea.MouseDragStart
    - GeUserArea.MouseDrag
    - GeUserArea.MouseDragEnd
    - c4d.gui.GeDialog
    - GeDialog.CreateLayout
    - GeDialog.AddUserArea
    - GeDialog.AttachUserArea


"""
import c4d
import weakref

# Global variable to determine the Size of our Square.
SIZE = 100


class Square(object):
    """Abstract class to represent a Square in a GeUserArea."""

    def __init__(self, geUserArea, index):
        self.index = index  # The initial square index (only used to differentiate square between each others)
        self.w = SIZE       # The width of the square
        self.h = SIZE       # The height of the square
        self.col = c4d.Vector(0.5)  # The default color of the square
        self.parentGeUserArea = weakref.ref(geUserArea)  # A weak reference to the host GeUserArea

    def GetParentedIndex(self):
        """Returns the current index in the parent list.

        Returns:
            int: The index or c4d.NOTOK if there is no parent.
        """
        parent = self.GetParent()
        if parent is None:
            return c4d.NOTOK

        return parent._squareList.index(self)

    def GetParent(self):
        """Retrieves the parent instance, stored in the weakreaf self.parentGeUserArea.

        Returns:
            c4d.gui.GeUserArea: The parent instance of the Square.
        """
        if self.parentGeUserArea:
            geUserArea = self.parentGeUserArea()
            if geUserArea is None:
                raise RuntimeError("GeUserArea parent is not valid.")
            return geUserArea

        return None

    def DrawNormal(self, x, y):
        """Called by the parent GeUserArea to draw the Square normally.

        Args:
            x: X position to draw.
            y: Y position to draw.
        """
        geUserArea = self.GetParent()
        geUserArea.DrawSetPen(self.col)
        geUserArea.DrawRectangle(x, y,
                                 x + self.w, y + self.h)

        geUserArea.DrawText(str(self.index), x, y)

    def DrawDraggedInitial(self, x, y):
        """Called by the parent GeUserArea when the Square is dragged
        with the initial position (same coordinate than DrawNormal).

        Args:
            x: X position to draw.
            y: Y position to draw.
        """
        geUserArea = self.GetParent()
        geUserArea.DrawBorder(c4d.BORDER_ACTIVE_1,
                              x, y,
                              x + self.w, y + self.h)

    def DrawDragged(self, x, y):
        """Called by the parent GeUserArea when the Square is dragged
        with the current mouse position.

        Args:
            x: X position to draw.
            y: Y position to draw.
        """
        geUserArea = self.GetParent()
        geUserArea.DrawSetPen(c4d.Vector(1))
        geUserArea.DrawRectangle(int(x), int(y),
                                 int(x + self.w), int(y + self.h))

        geUserArea.DrawText(str(self.index), int(x + (SIZE / 2.0)), int(y + (SIZE / 2.0)))


class DraggingArea(c4d.gui.GeUserArea):
    """Custom implementation of a GeUserArea that creates 4 squares and lets you drag them."""

    def __init__(self):
        self._squareList = []   # Stores a list of Square that will be draw in the GeUserArea.

        self.draggedObj = None  # None if not dragging, Square if dragged
        self.clickedPos = None  # None if not dragging, tuple(X, Y) if dragged

        # Creates 4 squares
        self.CreateSquare()
        self.CreateSquare()
        self.CreateSquare()
        self.CreateSquare()

    # ===============================
    #  Square management
    # ===============================
    def CreateSquare(self):
        """Creates a square that will be draw later.

        Returns:
            Square: The created square
        """
        square = Square(self, len(self._squareList))
        self._squareList.append(square)
        return square

    def GetXYFromId(self, index):
        """Retrieves the X, Y op, left position according to an index in order.
        This produces an array of Square correctly aligned.

        Args:
            index (int): The index to retrieve X, Y from.

        Returns:
            tuple(x left position, y top position).
        """
        x = SIZE * index
        xPadding = 5 * index
        x += xPadding
        y = 5

        return x, y

    def GetIdFromXY(self, xIn, yIn):
        """Retrieves the square id stored in self._squareList according to its normal (not dragged) position.

        Args:
            xIn (int): The position in x.
            yIn (int): The position in y.

        Returns:
            int: The id or c4d.NOTOK (-1) if not found.
        """

        # We could optimize the method by reversing the algorithm  from GetXYFromID,
        # But for now we just iterate all squares and see which one is correct.
        for squareId, square in enumerate(self._squareList):
            x, y = self.GetXYFromId(squareId)

            if x < xIn < x + SIZE and y < yIn < y + SIZE:
                return squareId

        return c4d.NOTOK

    # ===============================
    #  Drawing management
    # ===============================

    def DrawSquares(self):
        """Called in DrawMsg.
        Draws all squares contained in self._squareList
        """
        for squareId, square in enumerate(self._squareList):
            x, y = self.GetXYFromId(squareId)
            if square is not self.draggedObj:
                square.DrawNormal(x, y)

            else:
                square.DrawDraggedInitial(x, y)

    def DrawDraggedSquare(self):
        """Called in DrawMsg.
        Draws the dragged squares
        """
        if self.draggedObj is None or self.clickedPos is None:
            return

        x, y = self.clickedPos

        self.draggedObj.DrawDragged(x, y)

    def DrawMsg(self, x1, y1, x2, y2, msg):
        """This method is called automatically when Cinema 4D Draw the Gadget.

        Args:
            x1 (int): The upper left x coordinate.
            y1 (int): The upper left y coordinate.
            x2 (int): The lower right x coordinate.
            y2 (int): The lower right y coordinate.
            msg_ref (c4d.BaseContainer): The original mesage container.
            msg: 
        """

        # Initializes draw region
        self.OffScreenOn()
        self.SetClippingRegion(x1, y1, x2, y2)

        # Get default Background color
        defaultColorRgbDict = self.GetColorRGB(c4d.COLOR_BG)
        defaultColorRgb = c4d.Vector(defaultColorRgbDict["r"], defaultColorRgbDict["g"], defaultColorRgbDict["b"])
        defaultColor = defaultColorRgb / 255.0

        self.DrawSetPen(defaultColor)
        self.DrawRectangle(x1, y1, x2, y2)

        # First draw pass, we draw all not dragged object
        self.DrawSquares()

        # Last draw pass, we draw the dragged object, this way dragged square is drawn on top of everything.
        self.DrawDraggedSquare()

    # ===============================
    #  Dragging management
    # ===============================
    @property
    def isCurrentlyDragged(self):
        """Checks if a dragging operation currently occurs.

        Returns:
            bool: True if a dragging operation currently occurs otherwise False.
        """
        return self.clickedPos is not None and self.draggedObj is not None

    def GetDraggedSquareWithPosition(self):
        """Retrieves the clicked square during a drag event from the click position.

        Returns:
            Union[Square, None]: The square or None if there is nothing dragged.
        """
        if self.clickedPos is None:
            return None

        x, y = self.clickedPos
        squareId = self.GetIdFromXY(x, y)
        if squareId == c4d.NOTOK:
            return None

        return self._squareList[squareId]

    def InputEvent(self, msg):
        """Called by Cinema 4D, when there is a user interaction (click) on the GeUserArea.
        This is the place to catch and handle drag interaction.

        Args:
            msg (c4d.BaseContainer): The event container.

        Returns:
            bool: True if the event was handled, otherwise False.
        """
        # Do nothing if it's not a left mouse click event
        if msg[c4d.BFM_INPUT_DEVICE] != c4d.BFM_INPUT_MOUSE and msg[c4d.BFM_INPUT_CHANNEL] != c4d.BFM_INPUT_MOUSELEFT:
            return True
        
        # Retrieves the initial position of the click
        mouseX = msg[c4d.BFM_INPUT_X]
        mouseY = msg[c4d.BFM_INPUT_Y]

        # Initializes the start of the dragging process (needs to be initialized with the original mouseX, mouseY).
        self.MouseDragStart(c4d.KEY_MLEFT, mouseX, mouseY, c4d.MOUSEDRAGFLAGS_DONTHIDEMOUSE | c4d.MOUSEDRAGFLAGS_NOMOVE)
        isFirstTick = True

        # MouseDrag needs to be called all time to update information about the current drag process.
        # This allow to catch when the mouse is released and leave the infinite loop.
        while True:

            # Updates the current mouse information
            result, deltaX, deltaY, channels = self.MouseDrag()
            if result != c4d.MOUSEDRAGRESULT_CONTINUE:
                break

            # The first tick is ignored as deltaX/Y include the mouse clicking behavior with a deltaX/Y always equal to 4.0.
            # However it can be useful to do some initialization or even trigger single click event
            if isFirstTick:
                isFirstTick = False
                continue

            # If the mouse didn't move, don't need to do anything
            if deltaX == 0.0 and deltaY == 0.0:
                continue

            # Updates mouse position with the updated delta
            mouseX -= deltaX
            mouseY -= deltaY
            self.clickedPos = mouseX, mouseY

            # Retrieves the clicked square
            square = self.GetDraggedSquareWithPosition()

            # Defines the draggedObj only if the user clicked on a square and is not yet already defined
            if square is not None and self.draggedObj is None:
                self.draggedObj = square

            # Redraw the GeUserArea (it will call DrawMsg)
            self.Redraw()

        # Asks why we leave the while loop
        endState = self.MouseDragEnd()

        # If the drag process was ended because the user releases the mouse.
        # Note that while we are not anymore really in the Drag Pooling, from our implementation we consider we are still
        # and don't clear directly the data, so self.clickedPos and self.draggedObj still refer to the last tick of the
        # MouseDrag pool and we will clear it once we don't need anymore those data (after this if statement).
        if endState == c4d.MOUSEDRAGRESULT_FINISHED:

            # Checks a dragged object is set
            # in case of a simple click without mouse movement nothing has to be done.
            if self.isCurrentlyDragged:
                # Retrieves the initial index of the dragged object.
                currentIndex = self.draggedObj.GetParentedIndex()

                # Retrieves the index where the drag operation ended. If we find an ID, swap both items.
                releasedSquare = self.GetDraggedSquareWithPosition()
                if releasedSquare is not None:
                    targetIndex = releasedSquare.GetParentedIndex()

                    # Swap items only if source index and target index are different
                    if targetIndex != currentIndex:
                        self._squareList[currentIndex], self._squareList[targetIndex] = self._squareList[targetIndex], \
                                                                                        self._squareList[currentIndex]

                # In case the user release the mouse not on another square.
                # Swaps the current square to either the first position or last position.
                else:
                    # if current Index is already the first one, make no sense to inserts it
                    if currentIndex != 0:
                        # If the X position is before the X position of the first square
                        # Removes and inserts it back to the first position.
                        if self.clickedPos[0] < self.GetXYFromId(0)[0]:
                            self._squareList.remove(self.draggedObj)
                            self._squareList.insert(0, self.draggedObj)

                    # Retrieves the last index
                    lastIndex = len(self._squareList) - 1
                    # if current Index is already the last one, make no sense to insert it
                    if currentIndex != lastIndex:
                        if self.clickedPos[0] > self.GetXYFromId(lastIndex)[0] + SIZE:
                            # If the X position is after the X position of the last square (and its size)
                            # Removes and inserts it back to the last position.
                            self._squareList.remove(self.draggedObj)
                            self._squareList.insert(lastIndex, self.draggedObj)

        # Cleanup and refresh information if we dragged something
        if self.clickedPos is not None or self.draggedObj is not None:
            self.clickedPos = None
            self.draggedObj = None
            self.Redraw()

        return True


class MyDialog(c4d.gui.GeDialog):
    """Creates a Dialog with only a GeUserArea within."""

    def __init__(self):
        # It's important to stores our Python implementation instance of the GeUserArea in class variable,
        # This way we are sure the GeUserArea instance live as long as the GeDialog.
        self.area = DraggingArea()

    def CreateLayout(self):
        """This method is called automatically when Cinema 4D Create the Layout (display) of the Dialog."""
        self.AddUserArea(1000, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT)
        self.AttachUserArea(self.area, 1000)
        return True


def main():
    # Creates a new dialog
    dialog = MyDialog()

    # Opens it
    dialog.Open(dlgtype=c4d.DLG_TYPE_MODAL_RESIZEABLE, defaultw=500, defaulth=500)


if __name__ == '__main__':
    main()