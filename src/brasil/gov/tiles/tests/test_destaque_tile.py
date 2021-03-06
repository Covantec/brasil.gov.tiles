# -*- coding: utf-8 -*-
from brasil.gov.tiles.testing import INTEGRATION_TESTING
from brasil.gov.tiles.tiles.destaque import DestaqueTile
from collective.cover.tiles.base import IPersistentCoverTile
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.uuid.interfaces import IUUID
from zope.component import getMultiAdapter
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

import unittest


class DestaqueTileTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.request = self.layer['request']
        self.name = u"destaque"
        self.cover = self.portal['frontpage']
        self.tile = getMultiAdapter((self.cover, self.request), name=self.name)
        self.tile = self.tile['test']

    def test_interface(self):
        self.assertTrue(IPersistentCoverTile.implementedBy(DestaqueTile))
        self.assertTrue(verifyClass(IPersistentCoverTile, DestaqueTile))

        tile = DestaqueTile(None, None)
        self.assertTrue(IPersistentCoverTile.providedBy(tile))
        self.assertTrue(verifyObject(IPersistentCoverTile, tile))

    def test_default_configuration(self):
        self.assertTrue(self.tile.is_configurable)
        self.assertTrue(self.tile.is_droppable)
        self.assertFalse(self.tile.is_editable)

    def test_tile_is_empty(self):
        self.assertTrue(self.tile.is_empty())

    def test_crud(self):
        # we start with an empty tile
        self.assertTrue(self.tile.is_empty())

        # now we add a couple of objects to the destaque
        obj1 = self.portal['my-document']
        obj2 = self.portal['my-image']
        self.tile.populate_with_object(obj1)
        self.tile.populate_with_object(obj2)

        # tile's data attributed is cached so we should re-instantiate the tile
        tile = getMultiAdapter((self.cover, self.request), name=self.name)
        tile = tile['test']
        self.assertEqual(len(tile.results()), 2)
        self.assertTrue(obj1 in tile.results())
        self.assertTrue(obj2 in tile.results())

        # next, we replace the destaque of objects with a different one
        obj3 = self.portal['my-news-item']
        tile.replace_with_objects([IUUID(obj3, None)])
        # tile's data attributed is cached so we should re-instantiate the tile
        tile = getMultiAdapter((self.cover, self.request), name=self.name)
        tile = tile['test']
        self.assertTrue(obj1 not in tile.results())
        self.assertTrue(obj2 not in tile.results())
        self.assertTrue(obj3 in tile.results())

        # finally, we remove it from the destaque; the tile must be empty again
        tile.remove_item(obj3.UID())
        # tile's data attributed is cached so we should re-instantiate the tile
        tile = getMultiAdapter((self.cover, self.request), name=self.name)
        tile = tile['test']
        self.assertTrue(tile.is_empty())

    def test_populate_with_uids(self):
        # we start with an empty tile
        self.assertTrue(self.tile.is_empty())

        # now we add a couple of objects to the destaque
        obj1 = self.portal['my-document']
        obj2 = self.portal['my-image']
        self.tile.populate_with_uids([IUUID(obj1, None),
                                      IUUID(obj2, None)])

        # tile's data attributed is cached so we should re-instantiate the tile
        tile = getMultiAdapter((self.cover, self.request), name=self.name)
        tile = tile['test']
        self.assertEqual(len(tile.results()), 2)
        self.assertTrue(obj1 in tile.results())
        self.assertTrue(obj2 in tile.results())

    def test_accepted_content_types(self):
        # all content types are accepted
        # XXX: return None don't work
        # self.assertEqual(self.tile.accepted_ct(), None)
        self.assertEqual(self.tile.accepted_ct(),
                         ['Collection', 'Document', 'File', 'Form Folder',
                          'Image', 'Link', 'News Item'])

    def test_render_empty(self):
        msg = "Please add up to 2 objects to the tile."
        self.assertTrue(msg in self.tile())
