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

# pylint: disable=invalid-name

from cytomine.cytomine import Cytomine
from cytomine.models.collection import Collection
from cytomine.models.model import Model


class Ontology(Model):
    def __init__(self, name=None, **attributes):
        super().__init__()
        self.name = name
        self.user = None
        self.title = None
        self.attr = None
        self.data = None
        self.isFolder = None
        self.key = None
        self.children = None
        self.populate(attributes)


class OntologyCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super().__init__(Ontology, filters, max, offset)
        self._allowed_filters = [None]
        self.set_parameters(parameters)


class Term(Model):
    def __init__(
        self,
        name=None,
        id_ontology=None,
        color=None,
        id_parent=None,
        **attributes,
    ):
        super().__init__()
        self.name = name
        self.ontology = id_ontology
        self.parent = id_parent
        self.color = color
        self.populate(attributes)


class TermCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super().__init__(Term, filters, max, offset)
        self._allowed_filters = [None, "project", "ontology", "annotation"]
        self.set_parameters(parameters)


class RelationTerm(Model):
    def __init__(self, id_term1=None, id_term2=None, **attributes):
        super().__init__()
        self.term1 = id_term1
        self.term2 = id_term2
        self.populate(attributes)

    def uri(self):
        if not self.id:
            return "relation/parent/term.json"

        return f"relation/parent/term1/{self.term1}/term2/{self.term2}.json"

    def fetch(self, id_term1=None, id_term2=None):
        self.id = -1

        if self.term1 is None and id_term1 is None:
            raise ValueError("Cannot fetch a model with no term 1 ID.")

        if self.term2 is None and id_term2 is None:
            raise ValueError("Cannot fetch a model with no term 2 ID.")

        if id_term1 is not None:
            self.term1 = id_term1

        if id_term2 is not None:
            self.term2 = id_term2

        return Cytomine.get_instance().get_model(self, self.query_parameters)

    def update(self, *args, **kwargs):
        raise NotImplementedError("Cannot update a relation-term.")

    def __str__(self):
        return (
            f"[{self.callback_identifier}] {self.id} : "
            f"parent {self.term1} - child {self.term2}"
        )
