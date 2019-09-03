"""
Copyright: MAXON Computer GmbH
Author: Rick Barrett, Maxime Adam

Description:
    - Creates a Dialog which display the latest RSS feed of Cineversity.
    - Opens the web browser of the current displayed news when the user click a button.

Note:
    - Dialog options are saved in the World Container to set them back at each launch of Cinema 4D.

Class/method highlighted:
    - c4d.plugins.CommandData
    - CommandData.Execute()
    - c4d.gui.GeDialog
    - GeDialog.CreateLayout()
    - GeDialog.InitValues()
    - GeDialog.Timer()
    - GeDialog.Command()

Compatible:
    - Win / Mac
    - R15, R16, R17, R18, R19, R20, R21
"""
import c4d
import os
import urllib
import webbrowser
import xml

# Be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 1025244

# Container ids
FEED = 1000
ITEMS = 1001
SCROLL = 1002
INTERVAL = 1003
CUSTOM_URLS = 1004

# Feed
MNU_PLAYLIST = {"id": 1006, "name": "Cineversity Playlists", "url": "http://www.cineversity.com/search/playlists_rss/"}
MNU_TUTORIAL = {"id": 1006, "name": "Cineversity Tutorials", "url": "http://www.cineversity.com/search/tutorials_rss/"}
MNU_TW_CIN = {"id": 1007, "name": "Twitter @cineversity", "url": "http://twitter.com/statuses/user_timeline/18199026.rss"}
MNU_MAXONNEWS = {"id": 1008, "name": "MAXON News", "url": "http://www.maxon.net/index.php?id=1164&type=100&L=0"}
MNU_TW_MAXON3D = {"id": 1009, "name": "Twitter @maxon3d", "url": "http://twitter.com/statuses/user_timeline/18089167.rss"}
MNU_CUSTOM = {"id": 1010, "name": "Custom", "url": ""}

# Items
ITEMS_5 = {"id": 1011, "name": "5", "private": 5}
ITEMS_10 = {"id": 1012, "name": "10", "private": 10}
ITEMS_25 = {"id": 1013, "name": "25", "private": 25}
ITEMS_50 = {"id": 1014, "name": "50", "private": 50}
ITEMS_100 = {"id": 1015, "name": "100", "private": 100}

# Scroll
SCROLL_5 = {"id": 1016, "name": "1 sec", "private": 1}
SCROLL_10 = {"id": 1017, "name": "5 sec", "private": 5}
SCROLL_15 = {"id": 1018, "name": "10 sec", "private": 10}
SCROLL_30 = {"id": 1019, "name": "30 sec", "private": 30}
SCROLL_60 = {"id": 1020, "name": "60 sec", "private": 60}

# Interval
INTERVAL_1 = {"id": 1021, "name": "1 min", "private": 1}
INTERVAL_5 = {"id": 1022, "name": "5 min", "private": 5}
INTERVAL_10 = {"id": 1023, "name": "10 min", "private": 10}
INTERVAL_30 = {"id": 1024, "name": "30 min", "private": 30}
INTERVAL_60 = {"id": 1025, "name": "60 min", "private": 60}

# About
ABOUT = {"id": 1026, "name": "About"}

# Gui elements
TXT_LABEL = {"id": 1027, "name": "Cinversity Tutorials: "}
BTN_NEXT = {"id": 1028, "name": ">", "width": 8, "height": 8}


class MyDialog(c4d.gui.GeDialog):

    def __init__(self):
        self.element = None
        self.button = None
        self.rss_items = []
        self.rss_url = "http://www.cineversity.com/search/playlists_rss/"
        self.current_item = 0
        self.scroll_items = 5
        self.scroll_time = 1000 * 10
        self.update_time = 1000 * 60 * 10
        self.last_update = 0
        self.CVRssData = None

    def CreateLayout(self):
        """
        This Method is called automatically when Cinema 4D Create the Layout (display) of the Dialog.
        """
        # Defines the title
        self.SetTitle("Cineversity RSS")
        
        # Creates the menu
        self.MenuFlushAll()

        # Feed menu
        if self.MenuSubBegin("Feed"):
            self.MenuAddString(MNU_PLAYLIST["id"], MNU_PLAYLIST["name"])
            self.MenuAddString(MNU_TUTORIAL["id"], MNU_TUTORIAL["name"])
            self.MenuAddString(MNU_TW_CIN["id"], MNU_TW_CIN["name"])
            self.MenuAddString(MNU_MAXONNEWS["id"], MNU_MAXONNEWS["name"])
            self.MenuAddString(MNU_TW_MAXON3D["id"], MNU_TW_MAXON3D["name"])
            self.MenuAddSeparator()
            self.MenuAddString(MNU_CUSTOM["id"], MNU_CUSTOM["name"])
        self.MenuSubEnd()

        # Scroll menu
        if self.MenuSubBegin("Scroll"):
            self.MenuAddString(SCROLL_5["id"],  SCROLL_5["name"]+"&c&")
            self.MenuAddString(SCROLL_10["id"], SCROLL_10["name"])
            self.MenuAddString(SCROLL_15["id"], SCROLL_15["name"])
            self.MenuAddString(SCROLL_30["id"], SCROLL_30["name"])
            self.MenuAddString(SCROLL_60["id"], SCROLL_60["name"])
        self.MenuSubEnd()

        # Items menu
        if self.MenuSubBegin("Items"):
            self.MenuAddString(ITEMS_5["id"], ITEMS_5["name"])
            self.MenuAddString(ITEMS_10["id"], ITEMS_10["name"])
            self.MenuAddString(ITEMS_25["id"], ITEMS_25["name"])
            self.MenuAddString(ITEMS_50["id"], ITEMS_50["name"])
            self.MenuAddString(ITEMS_100["id"], ITEMS_100["name"])
        self.MenuSubEnd()

        # Update menu
        if self.MenuSubBegin("Update"):
            self.MenuAddString(INTERVAL_1["id"], INTERVAL_1["name"])
            self.MenuAddString(INTERVAL_5["id"], INTERVAL_5["name"])
            self.MenuAddString(INTERVAL_10["id"], INTERVAL_10["name"])
            self.MenuAddString(INTERVAL_30["id"], INTERVAL_30["name"])
            self.MenuAddString(INTERVAL_60["id"], INTERVAL_60["name"])
        self.MenuSubEnd()

        # About/branding menu
        if self.MenuSubBegin("Cineversity RSS"):
            self.MenuAddString(ABOUT["id"], ABOUT["name"])
        self.MenuSubEnd()

        self.MenuFinished()
        
        # Adds a static text label and a button
        if self.GroupBegin(id=0, flags=c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, cols=30, rows=1, title="", groupflags=0):
            self.element = self.AddStaticText(id=TXT_LABEL["id"],
                                              flags=c4d.BFH_SCALEFIT,
                                              initw=0,
                                              inith=0,
                                              name=TXT_LABEL["name"],
                                              borderstyle=c4d.BORDER_THIN_IN)

            self.button = self.AddButton(id=BTN_NEXT["id"], flags=c4d.BFH_RIGHT,
                                         initw=BTN_NEXT["width"],
                                         inith=BTN_NEXT["height"],
                                         name=BTN_NEXT["name"])
        self.GroupEnd()
        return True
    
    def InitValues(self):
        """
        Called after CreateLayout being called to define the values in the UI
        :return: 	True if successful, or False to signalize an error.
        """
        # Retrieves saved values from the world container of this plugin
        self.CVRssData = c4d.plugins.GetWorldPluginData(PLUGIN_ID)
        if self.CVRssData:
            self.rss_url = self.CVRssData[FEED]
            self.scroll_items = self.CVRssData[ITEMS]
            self.scroll_time = self.CVRssData[SCROLL]
            self.update_time = self.CVRssData[INTERVAL]
        else:
            self.CVRssData = c4d.BaseContainer()

        # Retrieves the RSS feed information
        self.UpdateRss()

        # Defines how often the Timer method will be called
        self.SetTimer(self.scroll_time)
        return True

    def Timer(self, msg):
        """
        This method is called automatically by Cinema 4D according to the timer set with GeDialog.SetTimer method.
        :param msg: The timer message
        """
        # Scroll RSS function
        self.UpdateToNextRss()

    def UpdateToNextRss(self):
        """
        Called to update the Dialog Title with the next Title available in the RSS feed.
        """
        
        # If updates time has been reached
        if c4d.GeGetTimer() < self.last_update + self.update_time:
            return

        # Updates data according the feed
        self.UpdateRss()
        
        # Retrieves the item, the XML parser delivers unicode - has to be encoded first (from unicode to ascii)
        title = "No RSS feeds" if not self.rss_items else self.rss_items[self.current_item]['title'].encode("utf-8")
        
        # Updates the "string" in dialog
        self.SetString(self.element, title)
        
        # Updates the current_item variable for the next call
        self.current_item = self.current_item + 1

        # If we've reached the last item or max scroll_items, resets the next item ID to be displayed
        if self.current_item >= min(len(self.rss_items), self.scroll_items):
            self.current_item = 0

    def UpdateRss(self):
        """
        Retrieves the RSS Feed, updates internal data and UI if needed
        """

        # Retrieves the RSS Url and parse its XML
        print "Updating... " + self.rss_url
        dom = xml.dom.minidom.parse(urllib.urlopen(self.rss_url))

        # Resets the rss_items list - otherwise the new ones get tacked on the old
        self.rss_items = []

        # Loops through the XML "item" nodes
        for node in dom.getElementsByTagName("item"):
            pubData = None

            # If "pubDate" key exists, retrieves the publication date
            if node.getElementsByTagName('pubDate'):
                pubData = node.getElementsByTagName('pubDate')[0].firstChild.data

            # If "dc:date" key exists, retrieves the publication date
            elif node.getElementsByTagName('dc:date'):
                pubData = node.getElementsByTagName('dc:date')[0].firstChild.data

            # If there is no pubData go to the next element
            if not pubData:
                continue

            # Appends the title, link and pubdate to the rss_items list
            self.rss_items.append({
                'title': node.getElementsByTagName('title')[0].firstChild.data,
                'link': node.getElementsByTagName('link')[0].firstChild.data,
                'pubdata': pubData
            })
        
        # Resets the last_update variable so we know when the update happened
        self.last_update = c4d.GeGetTimer()
        
        # Updates the dialog with the ScrollRss function
        self.UpdateToNextRss()
        
    def GoToUrl(self):
        """
        Opens the web browser to the current displayed rss page
        """
        url = self.rss_items[self.current_item-1]['link'].encode('utf-8')
        webbrowser.open(url, 2, True)
        return True
    
    def Command(self, id, msg):
        """
         This Method is called automatically when the user clicks on a gadget and/or changes its value this function will be called.
         It is also called when a string menu item is selected.
        :param id: The ID of the gadget that triggered the event.
        :param msg: The original message container
        :return: False if there was an error, otherwise True.
        """

        # Clicks on any items of Scroll menu
        if id == SCROLL_5["id"]:
            self.SetScrollTime(SCROLL_5["private"])
            self.MenuInitString(SCROLL_5["id"], True, True)
            self.MenuInitString(SCROLL_10["id"], True, False)
            self.MenuInitString(SCROLL_15["id"], True, False)
            self.MenuInitString(SCROLL_30["id"], True, False)
            self.MenuInitString(SCROLL_60["id"], True, False)
        elif id == SCROLL_10["id"]:
            self.SetScrollTime(SCROLL_10["private"])
            self.MenuInitString(SCROLL_5["id"], True, False)
            self.MenuInitString(SCROLL_10["id"], True, True)
            self.MenuInitString(SCROLL_15["id"], True, False)
            self.MenuInitString(SCROLL_30["id"], True, False)
            self.MenuInitString(SCROLL_60["id"], True, False)
        elif id == SCROLL_15["id"]:
            self.SetScrollTime(SCROLL_15["private"])
            self.MenuInitString(SCROLL_5["id"], True, False)
            self.MenuInitString(SCROLL_10["id"], True, False)
            self.MenuInitString(SCROLL_15["id"], True, True)
            self.MenuInitString(SCROLL_30["id"], True, False)
            self.MenuInitString(SCROLL_60["id"], True, False)
        elif id == SCROLL_30["id"]:
            self.SetScrollTime(SCROLL_30["private"])
            self.MenuInitString(SCROLL_5["id"], True, False)
            self.MenuInitString(SCROLL_10["id"], True, False)
            self.MenuInitString(SCROLL_15["id"], True, False)
            self.MenuInitString(SCROLL_30["id"], True, True)
            self.MenuInitString(SCROLL_60["id"], True, False)
        elif id == SCROLL_60["id"]:
            self.SetScrollTime(SCROLL_60["private"])
            self.MenuInitString(SCROLL_5["id"], True, False)
            self.MenuInitString(SCROLL_10["id"], True, False)
            self.MenuInitString(SCROLL_15["id"], True, False)
            self.MenuInitString(SCROLL_30["id"], True, False)
            self.MenuInitString(SCROLL_60["id"], True, True)

        # Clicks on any items of Feed menu
        elif id == MNU_TUTORIAL["id"]:
            self.SetFeedUrl(MNU_TUTORIAL["url"])
        elif id == MNU_TW_CIN["id"]:
            self.SetFeedUrl(MNU_TW_CIN["url"])
        elif id == MNU_MAXONNEWS["id"]:
            self.SetFeedUrl(MNU_MAXONNEWS["url"])
        elif id == MNU_TW_MAXON3D["id"]:
            self.SetFeedUrl(MNU_TW_MAXON3D["url"])
        elif id == MNU_CUSTOM["id"]:
            self.SetFeedUrl(MNU_CUSTOM["url"])

        # Clicks on any items of Items menu
        elif id == ITEMS_5["id"]:
            self.SetScrollItems(ITEMS_5["private"])
        elif id == ITEMS_10["id"]:
            self.SetScrollItems(ITEMS_10["private"])
        elif id == ITEMS_25["id"]:
            self.SetScrollItems(ITEMS_25["private"])
        elif id == ITEMS_50["id"]:
            self.SetScrollItems(ITEMS_50["private"])
        elif id == ITEMS_100["id"]:
            self.SetScrollItems(ITEMS_100["private"])

        # Clicks on any items of Update menu
        elif id == INTERVAL_1["id"]:
            self.SetUpdateTime(INTERVAL_1["private"])
        elif id == INTERVAL_5["id"]:
            self.SetUpdateTime(INTERVAL_5["private"])
        elif id == INTERVAL_10["id"]:
            self.SetUpdateTime(INTERVAL_10["private"])
        elif id == INTERVAL_30["id"]:
            self.SetUpdateTime(INTERVAL_30["private"])
        elif id == INTERVAL_60["id"]:
            self.SetUpdateTime(INTERVAL_60["private"])

        # Clicks on About entry of Cineversity RSS
        elif id == ABOUT["id"]:
            self.About()

        # Clicks on the Open Url
        elif id == BTN_NEXT["id"]:
            self.GoToUrl()
        
        return True
    
    def SetFeedUrl(self, private):
        """
        Sets the url feed
        :param private: the url feed to set, if empty asks for it
        """

        # If private is empty ask for it in a popup dialog
        if private == "":
            self.rss_url = c4d.gui.InputDialog("Custom URL", self.rss_url)
        else:
            self.rss_url = private

        # If the rss feed is still not, return False
        if not self.rss_url:
            return False

        # Updates the dlg and the data stored in the preference
        self.UpdateRss()
        self.UpdatePrefs()
        return True  

    def SetScrollItems(self, private):
        """
        Sets scroll_items variable
        :param private: how many items to scroll through.
        """
        self.scroll_items = private

        # Updates the data stored in the preference
        self.UpdatePrefs()
        return True

    def SetScrollTime(self, private):
        """
        # Sets the amount of time to show each item
        :param private: time in seconds
        """
        # Translates time in milliseconds
        self.scroll_time = private * 1000

        # Resets the dialog timer
        self.SetTimer(self.scroll_time)

        # Updates the data stored in the preference
        self.UpdatePrefs()
        return True

    def SetUpdateTime(self, private):
        """
        Sets the amount of time between updating RSS
        :param private: time in minutes
        """
        # Translates time in milliseconds
        self.update_time = private*1000*60

        # Updates the data stored in the preference
        self.UpdatePrefs()
        return True

    def About(self):
        """
        Opens the About dialog
        """
        c4d.gui.MessageDialog("Cineversity RSS v0.7\nby Rick Barrett (SDG)", c4d.GEMB_OK)
        return True
        
    def UpdatePrefs(self):
        """
        Updates the data stored in the world container (used to retrieve settings when Cinema 4D leaves)
        """
        self.CVRssData.SetString(FEED, self.rss_url)
        self.CVRssData.SetInt32(ITEMS, self.scroll_items)
        self.CVRssData.SetInt32(SCROLL, self.scroll_time)
        self.CVRssData.SetInt32(INTERVAL, self.update_time)
        c4d.plugins.SetWorldPluginData(PLUGIN_ID, self.CVRssData)


class CVRss(c4d.plugins.CommandData):
    """
    Command Data class that holds the CVRssDialog instance.
    """
    dialog = None
    
    def Execute(self, doc):
        """
        Called when the user Execute the command (CallCommand or a clicks on the Command from the plugin menu)
        :param doc: the current active document
        :type doc: c4d.documents.BaseDocument
        :return: True if the command success
        """
        # Creates the dialog if its not already exists
        if self.dialog is None:
            self.dialog = MyDialog()

        # Opens the dialog
        return self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID, defaultw=400, defaulth=32)

    def RestoreLayout(self, sec_ref):
        """
        Used to restore an asynchronous dialog that has been placed in the users layout.
        :param sec_ref: The data that needs to be passed to the dlg (almost no use of it).
        :type sec_ref: PyCObject
        :return: True if the restore success
        """
        # Creates the dialog if its not already exists
        if self.dialog is None:
            self.dialog = MyDialog()

        # Restores the layout
        return self.dialog.Restore(pluginid=PLUGIN_ID, secret=sec_ref)


# main
if __name__ == "__main__":
    # Retrieves the icon path
    directory, _ = os.path.split(__file__)
    fn = os.path.join(directory, "res", "icon.tif")

    # Creates a BaseBitmap
    bmp = c4d.bitmaps.BaseBitmap()
    if bmp is None:
        raise MemoryError("Failed to create a BaseBitmap.")

    # Init the BaseBitmap with the icon
    if bmp.InitWith(fn)[0] != c4d.IMAGERESULT_OK:
        raise MemoryError("Failed to initialize the BaseBitmap.")

    # Registers the plugin
    c4d.plugins.RegisterCommandPlugin(id=PLUGIN_ID,
                                      str="Py-Cineversity RSS",
                                      info=0,
                                      help="Displays a chosen RSS feed",
                                      dat=CVRss(),
                                      icon=bmp)
