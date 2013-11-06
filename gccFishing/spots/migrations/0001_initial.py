# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Spot'
        db.create_table(u'spots_spot', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('position', self.gf('geoposition.fields.GeopositionField')(max_length=42)),
        ))
        db.send_create_signal(u'spots', ['Spot'])


    def backwards(self, orm):
        # Deleting model 'Spot'
        db.delete_table(u'spots_spot')


    models = {
        u'spots.spot': {
            'Meta': {'object_name': 'Spot'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'position': ('geoposition.fields.GeopositionField', [], {'max_length': '42'})
        }
    }

    complete_apps = ['spots']