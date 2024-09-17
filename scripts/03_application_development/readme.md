# Application Development

## Introduction

The Cinema API as well as the MAXON API provide generic application development components to handle threads, files, GUI elements etc.

## Content

* **files_media**: *The Cinema API and MAXON API provide tools and classes to handle file and media data. If possible, the classes of the MAXON API should be preferred.*

* **gui**: *The Cinema 4D GUI is based on "dialog" windows based on the GeDialog class. A plugin can create custom dialog windows for user interaction or creates new managers.*
  
  * **description**: *Stores information on how parameters are to be displayed in the GUI (Attribute Manager).*
  
  * **dialog**: *The Cinema 4D GUI is based on "popup dialog" windows for user interaction.*
  
* **threading**: *Cinema 4D is a multi-threaded application that handles different tasks in different threads. Certain operations can only be performed from within the main thread. So a plugin must know its current thread context.*
