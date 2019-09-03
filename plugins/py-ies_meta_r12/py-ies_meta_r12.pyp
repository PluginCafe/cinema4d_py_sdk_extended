"""
Copyright: MAXON Computer GmbH
Author: XXX, Maxime Adam

Description:
    - Exporter, exporting all IES Meta information from the current document to a txt files.
    - Iterates all objects present in the cache of each objects in the scene to retrieve IES light.
    
Class/method highlighted:
    - c4d.plugins.SceneSaverData
    - SceneSaverData.Save()

Compatible:
    - Win / Mac
    - R12, R13, R14, R15, R16, R17, R18, R19, R20, R21
"""
import c4d
import os
import datetime


# Separate c4d_strings definitions
IDS_MANUFAC = 1001
IDS_LUMCAT = 1002
IDS_LUMINAIRE = 1003
IDS_LAMPCAT = 1004
IDS_LAMP = 1005
IDS_FOUND_IES = 1006
IDS_FOUND_LIGHTS = 1007
IDS_IES_META_CREATED = 1008
IDS_IES_HEADER = 1009

# Be sure to use a unique ID obtained from www.plugincafe.com
PLUGIN_ID = 1025281


class IESMeta(object):

    def __init__(self, ieslight):
        self.count = 1
        self._manufac = ieslight[c4d.LIGHT_PHOTOMETRIC_INFO_MANUFAC]
        self._lumcat = ieslight[c4d.LIGHT_PHOTOMETRIC_INFO_LUMCAT]
        self._luminaire = ieslight[c4d.LIGHT_PHOTOMETRIC_INFO_LUMINAIRE]
        self._lampcat = ieslight[c4d.LIGHT_PHOTOMETRIC_INFO_LAMPCAT]
        self._lamp = ieslight[c4d.LIGHT_PHOTOMETRIC_INFO_LAMP]

    def __eq__(self, other):
        return repr(self) == repr(other)

    def __str__(self):
        lbl_manufac = c4d.plugins.GeLoadString(IDS_MANUFAC)
        lbl_lumcat = c4d.plugins.GeLoadString(IDS_LUMCAT)
        lbl_luminaire = c4d.plugins.GeLoadString(IDS_LUMINAIRE)
        lbl_lampcat = c4d.plugins.GeLoadString(IDS_LAMPCAT)
        lbl_lamp = c4d.plugins.GeLoadString(IDS_LAMP)

        return "%s: %s\n%s: %s\n%s: %s\n%s: %s\n%s: %s\n" % (lbl_manufac, self._manufac, lbl_lumcat, self._lumcat, lbl_luminaire, self._luminaire, lbl_lampcat, self._lampcat, lbl_lamp, self._lamp)

    def __repr__(self):
        """Just used if two meta information are equal, see __eq__"""
        return "%s,%s,%s,%s,%s" % (self._manufac, self._lumcat, self._luminaire, self._lampcat, self._lamp)


class IESMetaSaverHelper(object):

    @staticmethod
    def HierarchyIterator(obj):
        """
        A Generator to iterate over the Hierarchy
        :param obj: The starting object of the generator (will be the first result)
        :return: All objects under and next of the `obj`
        """
        while obj:
            yield obj
            for opChild in IESMetaSaverHelper.HierarchyIterator(obj.GetDown()):
                yield opChild
            obj = obj.GetNext()

    @staticmethod
    def CacheIterator(op):
        """
        A Python Generator to iterate over all final objects (PolygonObject, CameraObject, Light....) of the passed BaseObject
        :param op: The BaseObject to retrieve all objects cached.
        """
        if not isinstance(op, c4d.BaseObject):
            raise TypeError("Expected a BaseObject or derived class got {0}".format(op.__class__.__name__))

        # Tries to retrieve the deformed cache of the object
        temp = op.GetDeformCache()
        if temp is not None:
            # If there is a deformed cache we iterate over him, a deformed cache can also contain deformed cache
            # e.g. in case of a nested deformer
            for obj in IESMetaSaverHelper.CacheIterator(temp):
                yield obj

        # Tries to retrieve the cache of the Object
        temp = op.GetCache()
        if temp is not None:
            # If there is a cache iterates over its, a cache can also contain deformed cache.
            # e.g. an instance, have a cache of its linked object but if this object is deformed, then you have a deformed cache as well
            for obj in IESMetaSaverHelper.CacheIterator(temp):
                yield obj

        # If op is not a generator / modifier
        if not op.GetBit(c4d.BIT_CONTROLOBJECT):
            yield op

        # Then finally iterates over the child of the current object to retrieve all objects.
        # e.g. in a cloner set to Instance mode, every clone is a new object.
        temp = op.GetDown()
        while temp:
            for obj in IESMetaSaverHelper.CacheIterator(temp):
                yield obj
            temp = temp.GetNext()


class IESMetaSaver(c4d.plugins.SceneSaverData, IESMetaSaverHelper):
    """IESMeta Exporter"""

    def Save(self, node, name, doc, filterflags):
        """
        Called by Cinema 4D when the document is asked to be saved in this format
        :param node: The node object representing the exporter.
        :type node: c4d.BaseList2D
        :param name: The filename of the file to save.
        :type name: str
        :param doc: The document that should be saved.
        :type doc: c4d.documents.BaseDocument
        :param filterflags: Options for the exporter.
        :type filterflags: SCENEFILTER
        :return: Status of the export process.
        :rtype: FILEERROR
        """
        # If there is no object in the scene, nothing to export.
        firstObj = doc.GetFirstObject()
        if firstObj is None:
            return c4d.FILEERROR_NONE

        # IESLightTotal stores the total amount of IES light found, while iesMetaList only store once an IES files
        IESLightTotal = 0
        iesMetaList = []

        # Iterates each object in the Scene
        for obj in IESMetaSaverHelper.HierarchyIterator(firstObj):

            # Iterates each object present in the cache that are not generator (PolygonObject, LightObject, CameraObject...)
            for cachedObj in IESMetaSaverHelper.CacheIterator(obj):

                # If the cached object is not a light, go to the next object.
                if not cachedObj.CheckType(c4d.Olight):
                    continue

                # If the light is not a photometric one or their is no ies file loaded, go to the next object.
                if cachedObj[c4d.LIGHT_TYPE] != c4d.LIGHT_TYPE_PHOTOMETRIC or not cachedObj[c4d.LIGHT_PHOTOMETRIC_FILE]:
                    continue

                minfo = IESMeta(cachedObj)
                if minfo is None:
                    raise MemoryError("Failed to create a IESMeta.")

                # Increment the total IES count, we are sure to log the IES if we are here
                IESLightTotal += 1

                # If there is already a meta file for this file in our list, increment the usage count
                try:
                    iesId = iesMetaList.index(minfo)
                    iesMetaList[iesId].count += 1
                except ValueError:
                    # If ValueError is thrown, that means the value was not found so we adds
                    iesMetaList.append(minfo)

        # If there is no IES files logged, there is nothing to export
        if len(iesMetaList) == 0:
            # Defines the warning method according if we are allowed to displayed Dialog box or not
            displayFn = c4d.gui.MessageDialog if filterflags & c4d.SCENEFILTER_DIALOGSALLOWED else __builtins__["print"]
            displayFn(c4d.FILEERROR_NONE)
            return c4d.FILEERROR_NONE

        # Opens the file in write mode
        with open(name, "w") as f:
            # Retrieves Data for the Header
            title = c4d.plugins.GeLoadString(IDS_IES_HEADER)
            created = c4d.plugins.GeLoadString(IDS_IES_META_CREATED)
            now = datetime.datetime.now()
            time = now.ctime()
            docpath = doc.GetDocumentPath()
            docname = doc.GetDocumentName()

            # Write the Header
            header = "%s\n%s: %s - %s\n\n" % (title, created, time, os.path.join(docpath, docname))
            f.write(header)

            # Write total light founds
            f.write("%s\n" % (c4d.plugins.GeLoadString(IDS_FOUND_IES, len(iesMetaList), IESLightTotal),))
            f.write("="*65 + "\n\n")

            # Write each Ies Meta
            for meta in iesMetaList:
                f.write("%s\n%s\n" % (c4d.plugins.GeLoadString(IDS_FOUND_LIGHTS, meta.count), str(meta),))
                f.write("-"*65 + "\n")

        return c4d.FILEERROR_NONE


if __name__ == '__main__':
    c4d.plugins.RegisterSceneSaverPlugin(id=PLUGIN_ID,
                                         str="Py-IES Meta (*.txt)",
                                         info=0,
                                         g=IESMetaSaver,
                                         description="",
                                         suffix="txt")
