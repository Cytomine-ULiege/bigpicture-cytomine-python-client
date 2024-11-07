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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


import os
import re

from cytomine.cytomine import Cytomine
from cytomine.models.collection import Collection, CollectionPartialUploadException
from cytomine.models.model import Model
from ._utilities import generic_image_dump, generic_download, is_false


class Annotation(Model):
    def __init__(self, location=None, id_image=None, id_terms=None, id_project=None, id_tracks=None, id_slice=None,
                 **attributes):
        super().__init__()
        self.location = location
        self.image = id_image
        self.slice = id_slice
        self.project = id_project
        self.term = id_terms
        self.track = id_tracks
        self.geometryCompression = None
        self.area = None
        self.areaUnit = None
        self.perimeter = None
        self.perimeterUnit = None
        self.cropURL = None

        self.populate(attributes)

    def __str__(self):
        return f"[{self.callback_identifier}] {self.id}"

    def review(self, id_terms=None):
        if self.id is None:
            raise ValueError("Cannot review an annotation with no ID.")

        if not id_terms:
            id_terms = []
        data = {"id": self.id, "terms": id_terms}
        return Cytomine.get_instance().post(
            f"{self.callback_identifier}/{self.id}/review.json",
            data,
        )

    def dump(self, dest_pattern="{id}.jpg", override=True, mask=False, alpha=False, bits=8,
             zoom=None, max_size=None, increase_area=None, contrast=None, gamma=None, colormap=None, inverse=None,
             complete=True):
        """
        Download the annotation crop, with optional image modifications.

        Parameters
        ----------
        dest_pattern : str, optional
            Destination path for the downloaded image. "{X}" patterns are replaced by the value of X attribute
            if it exists. The extension must be jpg, png or tif.
        override : bool, optional
            True if a file with same name can be overrided by the new file.
        mask : bool, optional
            True if a binary mask based on given annotations must be returned, False otherwise.
        alpha : bool, optional
            True if image background (outside annotations) must be transparent, False otherwise.
        zoom : int, optional
            Optional image zoom number
        bits : int (8,16,32) or str ("max"), optional
            Bit depth (bit per channel) of returned image. "max" returns the original image bit depth
        max_size : int, optional
            Maximum size (width or height) of returned image. None to get original size.
        increase_area : float, optional
            Increase the crop size. For example, an annotation whose bounding box size is (w,h) will have
            a crop dimension of (w*increase_area, h*increase_area).
        contrast : float, optional
            Optional contrast applied on returned image.
        gamma : float, optional
            Optional gamma applied on returned image.
        colormap : int, optional
            Cytomine identifier of a colormap to apply on returned image.
        inverse : bool, optional
            True to inverse color mapping, False otherwise.
        complete: bool, optional. Default: True
            True to use the annotation without simplification in masks and alphaMasks

        Returns
        -------
        downloaded : bool
            True if everything happens correctly, False otherwise. As a side effect, object attribute "filename"
            is filled with downloaded file path.
        """
        if self.id is None:
            raise ValueError("Cannot dump an annotation with no ID.")

        parameters = {
            "zoom": zoom,
            "maxSize": max_size,
            "increaseArea": increase_area,
            "contrast": contrast,
            "gamma": gamma,
            "colormap": colormap,
            "inverse": inverse,
            "bits": bits,
            "complete": complete
        }

        def dump_url_fn(model, file_path, **kwargs):
            extension = os.path.basename(file_path).split(".")[-1]
            if mask and alpha:
                image = "alphamask"
                if extension == "jpg":
                    extension = "png"
            elif mask:
                image = "mask"
            else:
                image = "crop"
            return model.cropURL.replace(
                "crop.png",
                f"{image}.{extension}"
            ).replace(
                "crop.jpg",
                f"{image}.{extension}"
            )

        files = generic_image_dump(dest_pattern, self, dump_url_fn, override=override, **parameters)

        if len(files) == 0:
            return False

        self.filenames = files
        self.filename = files[0]

        return True


class AnnotationCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super().__init__(Annotation, filters, max, offset)
        self._allowed_filters = [None]

        self.showBasic = True
        self.showMeta = True
        self.showWKT = None
        self.showGIS = None
        self.showTerm = None
        self.showTrack = None
        self.showAlgo = None
        self.showUser = None
        self.showImage = None
        self.showSlice = None
        self.showImageGroup = None
        self.showLink = None
        self.reviewed = None
        self.noTerm = None
        self.noAlgoTerm = None
        self.multipleTerm = None

        self.project = None

        self.user = None
        self.users = None

        self.image = None
        self.images = None

        self.slice = None
        self.slices = None

        self.term = None
        self.terms = None
        self.suggestedTerm = None
        self.userForTermAlgo = None

        self.track = None
        self.tracks = None

        self.group = None
        self.groups = None

        self.bbox = None
        self.bboxAnnotation = None
        self.baseAnnotation = None
        self.maxDistanceBaseAnnotation = None

        self.included = False
        self.annotation = None

        self.set_parameters(parameters)

    def uri(self, without_filters=False):
        if self.included:
            self.add_filter("imageinstance", self.image)
        uri = super().uri(without_filters)
        if self.included:
            return uri.replace(".json", "/included.json")

        return uri

    def dump_crops(self, dest_pattern, n_workers=0, override=True, **dump_params):
        """Download the crops of the annotations
        Parameters
        ----------
        dest_pattern : str, optional
            Destination path for the downloaded image. "{X}" patterns are replaced by the value of X attribute
            if it exists.
        override : bool, optional
            True if a file with same name can be overrided by the new file.
        n_workers: int
            Number of workers to use (default: uses all the available processors)
        dump_params: dict
            Parameters for dumping the annotations (see Annotation.dump)

        Returns
        -------
        annotations: AnnotationCollection
            Annotations that have been successfully downloaded (containing a `filenames` attribute)
        """

        def dump_crop(an):
            if is_false(an.dump(dest_pattern=dest_pattern, override=override, **dump_params)):
                return False
            else:
                return an

        results = generic_download(self, download_instance_fn=dump_crop, n_workers=n_workers)

        # check errors
        count_fail = 0
        failed = list()
        for in_annot, out_annot in results:
            if is_false(out_annot):
                count_fail += 1
                failed.append(in_annot.id)

        logger = Cytomine.get_instance().logger
        if count_fail > 0:
            n_annots = len(self)
            ratio = 100 * count_fail / float(n_annots)
            logger.info(
                f"Failed to download crops for {count_fail}/{n_annots} "
                f"annotations ({ratio:3.2f} %)."
            )
            logger.debug("Annotation with crop download failure: %s", failed)

        collection = AnnotationCollection()
        collection.extend([an for _, an in results if not isinstance(an, bool) or an])
        return collection


class AnnotationTerm(Model):
    def __init__(self, id_annotation=None, id_term=None, **attributes):
        super().__init__()
        self.userannotation = id_annotation
        self.term = id_term
        self.user = None
        self.populate(attributes)

    def uri(self):
        return f"annotation/{self.userannotation}/term/{self.term}.json"

    def fetch(self, id_annotation=None, id_term=None):
        self.id = -1

        if self.userannotation is None and id_annotation is None:
            raise ValueError("Cannot fetch a model with no annotation ID.")
        elif self.term is None and id_term is None:
            raise ValueError("Cannot fetch a model with no term ID.")

        if id_annotation is not None:
            self.userannotation = id_annotation

        if id_term is not None:
            self.term = id_term

        return Cytomine.get_instance().get_model(self, self.query_parameters)

    def update(self, *args, **kwargs):
        raise NotImplementedError("Cannot update a annotation-term.")

    def __str__(self):
        return (
            f"[{self.callback_identifier}] Annotation {self.userannotation} "
            f"- Term {self.term}"
        )


class AlgoAnnotationTerm(Model):
    def __init__(self, id_annotation=None, id_term=None, id_expected_term=None, rate=1.0, **attributes):
        super().__init__()
        self.annotation = id_annotation
        self.annotationIdent = id_annotation
        self.term = id_term
        self.expectedTerm = id_expected_term
        self.user = None
        self.rate = rate
        self.populate(attributes)

    def uri(self):
        return f"annotation/{self.annotation}/term/{self.term}.json"

    def fetch(self, id_annotation=None, id_term=None):
        self.id = -1

        if self.annotation is None and id_annotation is None:
            raise ValueError("Cannot fetch a model with no annotation ID.")
        elif self.term is None and id_term is None:
            raise ValueError("Cannot fetch a model with no term ID.")

        if id_annotation is not None:
            self.annotation = id_annotation

        if id_term is not None:
            self.term = id_term

        return Cytomine.get_instance().get_model(self, self.query_parameters)

    def update(self, *args, **kwargs):
        raise NotImplementedError("Cannot update a annotation-term.")

    def __str__(self):
        return f"[{self.callback_identifier}] Annotation {self.annotation} - Term {self.term}"


class AnnotationFilter(Model):
    def __init__(self, name=None, users=None, terms=None, **attributes):
        super().__init__()
        self.name = name
        self.users = users
        self.terms = terms
        self.populate(attributes)


class AnnotationFilterCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super().__init__(AnnotationFilter, filters, max, offset)
        self._allowed_filters = [None]
        self.project = None
        self.set_parameters(parameters)

    def save(self, *args, **kwargs):
        raise NotImplementedError("Cannot save an annotation filter collection by client.")


class AnnotationGroup(Model):
    def __init__(self, id_project=None, id_image_group=None, type="SAME_OBJECT", **attributes):
        super().__init__()
        self.project = id_project
        self.imageGroup = id_image_group
        self.type = type
        self.populate(attributes)

    def merge(self, id_other_annotation_group):
        if self.id is None:
            raise ValueError("Cannot merge an annotaiton group with no ID.")

        return Cytomine.get_instance().post(
            f"annotationgroup/{self.id}/annotationgroup/"
            f"{id_other_annotation_group}/merge.json"
        )


class AnnotationGroupCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super().__init__(AnnotationGroup, filters, max, offset)
        self._allowed_filters = ["project", "imagegroup"]
        self.set_parameters(parameters)


class AnnotationLink(Model):
    def __init__(self, annotation_class_name=None, id_annotation=None, id_annotation_group=None, **attributes):
        super().__init__()
        self.annotationClassName = annotation_class_name
        self.annotationIdent = id_annotation
        self.group = id_annotation_group
        self.populate(attributes)

    def uri(self):
        if self.is_new():
            return f"{self.callback_identifier}.json"

        return f"annotationgroup/{self.group}/annotation/{self.annotationIdent}.json"

    def fetch(self, id_annotation=None, id_annotation_group=None):
        self.id = -1

        if self.annotationIdent is None and id_annotation is None:
            raise ValueError("Cannot fetch a model with no annotation ID.")
        elif self.group is None and id_annotation_group is None:
            raise ValueError("Cannot fetch a model with no annotation group ID.")

        if id_annotation is not None:
            self.annotationIdent = id_annotation

        if id_annotation_group is not None:
            self.group = id_annotation_group

        return Cytomine.get_instance().get_model(self, self.query_parameters)

    def update(self, *args, **kwargs):
        raise NotImplementedError("Cannot update an annotation link.")

    def __str__(self):
        return (
            f"[{self.callback_identifier}] Annotation {self.annotationIdent} "
            f"- Annotation group {self.group}"
        )

class AnnotationLinkCollection(Collection):
    def __init__(self, filters=None, max=0, offset=0, **parameters):
        super().__init__(AnnotationLink, filters, max, offset)
        self._allowed_filters = ["annotationgroup", "annotation"]
        self.set_parameters(parameters)
