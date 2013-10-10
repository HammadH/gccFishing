# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Textpost'
        db.delete_table(u'wall_textpost')

        # Deleting model 'Imagepost'
        db.delete_table(u'wall_imagepost')

        # Deleting model 'Comment'
        db.delete_table(u'wall_comment')

        # Deleting model 'Wallpost'
        db.delete_table(u'wall_wallpost')


    def backwards(self, orm):
        # Adding model 'Textpost'
        db.create_table(u'wall_textpost', (
            ('text', self.gf('django.db.models.fields.TextField')()),
            (u'wallpost_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['wall.Wallpost'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'wall', ['Textpost'])

        # Adding model 'Imagepost'
        db.create_table(u'wall_imagepost', (
            ('text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('image', self.gf('sorl.thumbnail.fields.ImageField')(max_length=100)),
            (u'wallpost_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['wall.Wallpost'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'wall', ['Imagepost'])

        # Adding model 'Comment'
        db.create_table(u'wall_comment', (
            ('wallpost', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wall.Wallpost'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('posted_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authtools.User'])),
        ))
        db.send_create_signal(u'wall', ['Comment'])

        # Adding model 'Wallpost'
        db.create_table(u'wall_wallpost', (
            ('points', self.gf('django.db.models.fields.IntegerField')(default=0)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('posted_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authtools.User'])),
        ))
        db.send_create_signal(u'wall', ['Wallpost'])


    models = {
        
    }

    complete_apps = ['wall']