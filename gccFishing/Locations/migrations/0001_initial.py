# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Country'
        db.create_table(u'Locations_country', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=(), max_length=50, populate_from='name')),
            ('image', self.gf('sorl.thumbnail.fields.ImageField')(max_length=100)),
            ('flag', self.gf('sorl.thumbnail.fields.ImageField')(max_length=100)),
        ))
        db.send_create_signal(u'Locations', ['Country'])

        # Adding model 'City'
        db.create_table(u'Locations_city', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('image', self.gf('sorl.thumbnail.fields.ImageField')(max_length=100)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=50, populate_from='name', unique_with=())),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(related_name='cities', to=orm['Locations.Country'])),
        ))
        db.send_create_signal(u'Locations', ['City'])

        # Adding model 'Location'
        db.create_table(u'Locations_location', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['Locations.Country'])),
            ('city', self.gf('smart_selects.db_fields.ChainedForeignKey')(to=orm['Locations.City'])),
        ))
        db.send_create_signal(u'Locations', ['Location'])


    def backwards(self, orm):
        # Deleting model 'Country'
        db.delete_table(u'Locations_country')

        # Deleting model 'City'
        db.delete_table(u'Locations_city')

        # Deleting model 'Location'
        db.delete_table(u'Locations_location')


    models = {
        u'Locations.city': {
            'Meta': {'object_name': 'City'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cities'", 'to': u"orm['Locations.Country']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "'name'", 'unique_with': '()'})
        },
        u'Locations.country': {
            'Meta': {'object_name': 'Country'},
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