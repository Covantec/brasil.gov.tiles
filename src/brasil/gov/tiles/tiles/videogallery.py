# -*- coding: utf-8 -*-

from collective.cover import _
from collective.cover.tiles.list import IListTile
from collective.cover.tiles.list import ListTile
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema


class IVideoGalleryTile(IListTile):
    """
    """

    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
    )

    subtitle = schema.TextLine(
        title=_(u'Subtitle'),
        required=False,
        readonly=False,
    )

    footer_text = schema.TextLine(
        title=_(u'Footer Link'),
        required=False,
        readonly=False,
    )

    uuids = schema.List(
        title=_(u'Videos'),
        value_type=schema.TextLine(),
        required=False,
        readonly=True,
    )


class VideoGalleryTile(ListTile):
    index = ViewPageTemplateFile("templates/videogallery.pt")
    is_configurable = True
    is_editable = True
    limit = 6

    def populate_with_object(self, obj):
        super(ListTile, self).populate_with_object(obj)  # check permission

        #here we should check if the embeded item has its a video
        # XXX

        self.set_limit()
        uuid = IUUID(obj, None)
        data_mgr = ITileDataManager(self)

        old_data = data_mgr.get()
        old_data['uuids'] = [uuid]
        data_mgr.set(old_data)

    def get_uid(self, obj):
        return IUUID(obj)

    def thumbnail(self, item):
        scales = item.restrictedTraverse('@@images')
        try:
            return scales.scale('image', width=80, height=60)
        except:
            return None

    def accepted_ct(self):
        """ Return a list of content types accepted by the tile.
        """
        return ['Collection', 'Folder']

    def get_elements(self, obj):
        results = []
        if obj:
            portal_type = obj.getPortalTypeName()

            limit = 0
            catalog_results = []
            if portal_type == 'Collection':
                catalog_results = obj.results()
                limit = catalog_results.length if catalog_results else 0
            elif portal_type == 'Folder':
                catalog_results = obj.getFolderContents({"portal_type": "sc.embedder"})
                limit = len(catalog_results) if catalog_results else 0

            if catalog_results:
                limit = limit if limit <= self.limit else self.limit
                for i in xrange(limit):
                    results.append(catalog_results[i].getObject())

        return results
