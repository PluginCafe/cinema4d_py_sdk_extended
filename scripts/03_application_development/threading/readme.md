# Threading

Cinema 4D is a multi-threaded application that handles different tasks in different threads. Certain operations can only be performed from within the main thread.
So a plugin must know its current thread context.

Both the classic API and the MAXON API provide tools to handle threads, create custom threads to perform multi-threaded operations.

Classic API:
- **c4d.threading.C4DThread**: *The base class for custom classic threads in Cinema 4D. Operations can be done on multiple cores or in the background.*

## Examples

### threading_basic
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac

    Demonstrates how to handle C4DThread from a script.

### threading_testdbreak
Version: R13, R14, R15, R16, R17, R18, R19, R20, R21, S22, R23 - Win/Mac

    Uses TestDBreak to define a custom condition to leave a thread.
