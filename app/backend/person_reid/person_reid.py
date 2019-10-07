""" Person ReID Class. """
import os
import sys
import glob
import simplejson as json
from scipy import spatial
import numpy as np
__author__ = "Anh Tra"
__email__ = "anhtt@d-soft.com.vn"
__version__ = "0.0.1"


# optional params
_DATA_DIR = '/tmp/debug_videos'


def parse_person_embedding_from_json_file(json_filepath):
    """ Parse the person embeddings from the given json file.
    
    Args:
        json_filepath (str): path of the json file
        
    Returns:
        frame_img_paths (list): include paths of the original frame images
        bbox_img_paths (list): include paths of the bbox images
        bbox_embedding (list): include embedding vector of person objects
    """
    with open(json_filepath, 'r') as f:
        json_data = json.load(f)
        
    frame_img_paths = []
    bbox_img_paths = []
    bbox_embeddings = []
    bbox_indices = []
    frame_timestamp = []

    if 'obj_boxes' in json_data.keys():
        obj_boxes = json_data['obj_boxes']
        for i, obj_box in enumerate(obj_boxes):
            if 'bbox_url' in obj_box:
                frame_img_paths.append(json_data['frame_url'])
                bbox_img_paths.append(obj_box['bbox_url'])
                bbox_embeddings.append(obj_box['embedding'])
                bbox_indices.append(i) 
                frame_timestamp.append(json_data['timestamp'])
                
    return frame_img_paths, bbox_img_paths, bbox_embeddings, bbox_indices, frame_timestamp


class PersonReIdentifier(object):
    """ ReID class. """

    def __init__(self):
        """ Constructor of the PersonReIdentifier class. 

        Args:
            None.

        Returns:
            None.
        """
        self.data_dir = None
        self.frame_img_paths = None
        self.bbox_img_paths = None
        self.kd_tree = None
        
    def build_kdtree(self, data_dir=None):
        """ Build the KDTree for person ReID.

        Args:
            data_dir (str): path of the recored stream data

        Returns:
            None.
        """
        assert os.path.isdir(data_dir)
        self.data_dir = data_dir
        self.json_filepaths = glob.glob(os.path.join(self.data_dir, '*/json/*.json'))
        
        # parse json data
        frame_img_paths = []
        bbox_img_paths = []
        bbox_embeddings = []
        bbox_indices = []
        frame_timestamp = []
        for json_fp in self.json_filepaths:
            _frame_img_paths, _bbox_img_paths, _bbox_embeddings, _bbox_indices, _frame_timestamp = parse_person_embedding_from_json_file(json_fp)
            frame_img_paths += _frame_img_paths
            bbox_img_paths += _bbox_img_paths
            bbox_embeddings += _bbox_embeddings
            bbox_indices += _bbox_indices
            frame_timestamp += _frame_timestamp

        # build the kdtree
        kd_tree = spatial.KDTree(bbox_embeddings)

        # save the kd_tree and indexes for searching later
        self.frame_img_paths = frame_img_paths
        self.bbox_img_paths = bbox_img_paths
        self.bbox_indices = bbox_indices
        self.frame_timestamp = frame_timestamp
        self.kd_tree = kd_tree

    def search(self, bbox_embedding=None, top_num=None):
        """ Search the similar bbox images based on the given bbox_embedding.

        Args:
            bbox_embedding (np.array): ...
            top_num (int): ...
        
        Returns:
            None.
        """
        assert bbox_embedding is not None
        assert top_num is not None

        dists, indices = self.kd_tree.query(bbox_embedding, k=top_num)
        if indices.shape == ():
            dists = np.array([dists])
            indices = np.array([indices])
        retrieved_bboxes = [self.bbox_img_paths[i] for i in indices]
        retrieved_frames = [self.frame_img_paths[i] for i in indices]
        retrieved_bboxes_ids = [self.bbox_indices[i] for i in indices]
        retrieved_frames_timestamp = [self.frame_timestamp[i] for i in indices]
        retrieved_dists = dists
    
        return retrieved_dists, retrieved_bboxes, retrieved_frames, retrieved_bboxes_ids, retrieved_frames_timestamp
