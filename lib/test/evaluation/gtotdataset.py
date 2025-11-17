import numpy as np
from lib.test.evaluation.data import Sequence, BaseDataset, SequenceList
from lib.test.utils.load_text import load_text
import os


class gtotDataset(BaseDataset):

    def __init__(self, split):
        super().__init__()
        # Split can be test, val, or ltrval (a validation split consisting of videos from the official train set)
        if split == 'gtot' or split == 'val':
            self.base_path = os.path.join(self.env_settings.gtot_path, split)
        else:
            self.base_path = os.path.join(self.env_settings.gtot_path, 'train')

        self.sequence_list = self._get_sequence_list(split)
        self.split = split

    def get_sequence_list(self):
        return SequenceList([self._construct_sequence(s) for s in self.sequence_list])

    def _construct_sequence(self, sequence_name):
        anno_path = os.path.join(self.base_path, sequence_name, 'init.txt')
        ground_truth_rect = load_text(str(anno_path), delimiter=',', dtype=np.float64)

        frames_path_i = os.path.join(self.base_path, sequence_name, 'i')
        frames_path_v = os.path.join(self.base_path, sequence_name, 'v')
        frame_list_i = [frame for frame in os.listdir(frames_path_i) if frame.endswith(".png")]
        frame_list_i.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
        frame_list_v = [frame for frame in os.listdir(frames_path_v) if frame.endswith(".png")]
        frame_list_v.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
        frames_list_i = [os.path.join(frames_path_i, frame) for frame in frame_list_i]
        frames_list_v = [os.path.join(frames_path_v, frame) for frame in frame_list_v]
        frames_list = [frames_list_v, frames_list_i]
        return Sequence(sequence_name, frames_list, 'gtot', ground_truth_rect.reshape(-1, 4))

    def __len__(self):
        return len(self.sequence_list)

    def _get_sequence_list(self, split):
        with open(os.path.join(self.base_path, '{}List.txt'.format(split))) as f:
            sequence_list = f.read().splitlines()

        if split == 'ltrval':
            with open(os.path.join(self.env_settings.dataspec_path, 'got10k_val_split.txt')) as f:
                seq_ids = f.read().splitlines()

            sequence_list = [sequence_list[int(x)] for x in seq_ids]
        return sequence_list