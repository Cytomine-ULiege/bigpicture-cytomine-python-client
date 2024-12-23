# -*- coding: utf-8 -*-

# * Copyright (c) 2009-2024. Authors: see NOTICE file.
# *
# * Licensed under the Apache License, Version 2.0 (the "License");
# * you may not use this file except in compliance with the License.
# * You may obtain a copy of the License at
# *
# *      http://www.apache.org/licenses/LICENSE-2.0
# *
# * Unless required by applicable law or agreed to in writing, software
# * distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.

# pylint: disable=invalid-name,unused-argument

import json

import six

from cytomine.cytomine import Cytomine


class Model:
    def __init__(self, **attributes):
        # In some cases, a model can have some request parameters.
        self._query_parameters = {}

        # Attributes common to all models
        self.id = None
        self.created = None
        self.updated = None
        self.deleted = None
        self.name = None

    def fetch(self, id=None):
        if self.id is None and id is None:
            raise ValueError("Cannot fetch a model with no ID.")
        if id is not None:
            self.id = id

        return Cytomine.get_instance().get_model(self, self.query_parameters)

    def save(self):
        if self.id is None:
            return Cytomine.get_instance().post_model(self)

        return self.update()

    def delete(self, id=None):
        if self.id is None and id is None:
            raise ValueError("Cannot delete a model with no ID.")
        if id is not None:
            self.id = id

        return Cytomine.get_instance().delete_model(self)

    def update(self, id=None, **attributes):
        if self.id is None and id is None:
            raise ValueError("Cannot update a model with no ID.")
        if id is not None:
            self.id = id

        if attributes:
            self.populate(attributes)
        return Cytomine.get_instance().put_model(self)

    def is_new(self):
        return self.id is None

    def populate(self, attributes):
        if attributes:
            for key, value in six.iteritems(attributes):
                if key.startswith("id_"):
                    key = key[3:]
                if key == "uri":
                    key = "uri_"
                if not key.startswith("_"):
                    if key == "class":
                        key += "_"
                    setattr(self, key, value)
        return self

    def to_json(self, **dump_parameters):
        d = dict(
            (k, v)
            for k, v in six.iteritems(self.__dict__)
            if v is not None and not k.startswith("_")
        )
        if "uri_" in d:
            d["uri"] = d.pop("uri_")
        return json.dumps(d, **dump_parameters)

    def uri(self):
        if self.is_new():
            return f"{self.callback_identifier}.json"

        return f"{self.callback_identifier}/{self.id}.json"

    @property
    def query_parameters(self):
        return self._query_parameters

    @property
    def callback_identifier(self):
        return self.__class__.__name__.lower()

    def __str__(self):
        return f"[{self.callback_identifier}] {self.id} : {self.name}"


class DomainModel(Model):
    def __init__(self, object, **attributes):
        super().__init__(**attributes)

        if object.is_new():
            raise ValueError("The object must be fetched or saved before.")

        self.domainClassName = None
        self.domainIdent = None
        self.obj = object

    def uri(self):
        if self.is_new():
            return (
                f"domain/{self.domainClassName}/{self.domainIdent}/"
                f"{self.callback_identifier}.json"
            )

        return (
            f"domain/{self.domainClassName}/{self.domainIdent}/"
            f"{self.callback_identifier}/{self.id}.json"
        )

    @property
    def obj(self):
        return self._object

    @obj.setter
    def obj(self, value):
        self._object = value
        self.domainClassName = value.class_
        self.domainIdent = value.id
