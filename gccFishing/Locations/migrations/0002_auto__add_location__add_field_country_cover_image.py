# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Location'
        db.create_table(u'Locations_location', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Locations.Country'])),
            ('city', self.gf('smart_selects.db_fields.ChainedForeignKey')(to=orm['Locations.City'])),
        ))
        db.send_create_signal(u'Locations', ['Location'])

        # Adding field 'Country.cover_image'
        db.add_column(u'Locations_country', 'cover_image',
                      self.gf('sorl.thumbnail.fields.ImageField')(max_length=100, null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Location'
        db.delete_table(u'Locations_location')

        # Deleting field 'Country.cover_image'
        db.delete_column(u'Locations_country', 'cover_image')


    models = {
        u'Locations.city': {
            'Meta': {'object_name': 'City'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cities'", 'to': u"orm['Locations.Country']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "'name'"})
        },
        u'Locations.country': {
            'Meta': {'object_name': 'Country'},
            'cover_image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'flag': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "'name'"})
        },
        u'Locations.location': {
            'Meta': {'object_name': 'Location'},
            'city': ('smart_selects.db_fields.ChainedForeignKey', [], {'to': u"orm['Locations.City']"}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['Locations.Country']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['Locations']