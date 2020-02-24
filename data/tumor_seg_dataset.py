from torch.utils.data import Dataset
import torchvision.transforms as transforms
import torchvision.transforms.functional as TF
from PIL import Image
import os
import random
import numpy as np
from root_dir import ROOT_DIR

#DATASET_DIR = "/visinf/home/vilab22/Documents/RemoteProjects/cnn_interpretability/data/tumor_seg_data"
DATASET_DIR = os.path.join(ROOT_DIR, 'data/tumor_seg_data')
TRANSFORM = False
DEBUG = False

class TumorDataset(Dataset):
    """ Returns a TumorDataset class object which represents our tumor dataset.
    TumorDataset inherits from torch.utils.data.Dataset class.
    """

    def __init__(self, device):
        """ Constructor for our TumorDataset class.
        Parameters:
            root_dir(str): Directory with all the images.
            transform(bool): Flag to apply image random transformation.
            DEBUG(bool): To switch to debug mode for image transformation.

        Returns: None
        """
        self.device = device
        self.dataset_dir = DATASET_DIR
        self.transform = {'hflip': TF.hflip,
                          'vflip': TF.vflip,
                          'rotate': TF.rotate}
        self.default_transformation = transforms.Compose([
            transforms.Grayscale(),
            transforms.Resize((512, 512))
        ])
        self.DEBUG = DEBUG
        if not TRANSFORM:
            self.transform = None

    def __getitem__(self, index):
        """ Overridden method from inheritted class to support
        indexing of dataset such that datset[I] can be used
        to get Ith sample.
        Parameters:
            index(int): Index of the dataset sample

        Return:
            sample(dict): Contains the index, image, mask torch.Tensor.
                        'index': Index of the image.
                        'image': Contains the tumor image torch.Tensor.
                        'mask' : Contains the mask image torch.Tensor.
        """
        index += 3000
        image_name = os.path.join(self.dataset_dir, str(index) + '.png')
        mask_name = os.path.join(self.dataset_dir, str(index) + '_mask.png')

        image = Image.open(image_name)
        mask = Image.open(mask_name)

        image = self.default_transformation(image)
        mask = self.default_transformation(mask)

        # Custom transformations
        if self.transform:
            image, mask = self._random_transform(image, mask)

        image = TF.to_tensor(image)
        mask = np.array(mask, dtype=np.uint8)
        #mask = TF.to_tensor(mask).squeeze()

        image = image.to(self.device)
        sample = {"img": image, "gt": mask, "filepath": image_name}
        return sample

    def _random_transform(self, image, mask):
        """ Applies a set of transformation in random order.
        Each transformation has a probability of 0.5
        """
        choice_list = list(self.transform)
        for _ in range(len(choice_list)):
            choice_key = random.choice(choice_list)
            if self.DEBUG:
                print(f'Transform choose: {choice_key}')
            action_prob = random.randint(0, 1)
            if action_prob >= 0.5:
                if self.DEBUG:
                    print(f'\tApplying transformation: {choice_key}')
                if choice_key == 'rotate':
                    rotation = random.randint(15, 75)
                    if self.DEBUG:
                        print(f'\t\tRotation by: {rotation}')
                    image = self.transform[choice_key](image, rotation)
                    mask = self.transform[choice_key](mask, rotation)
                else:
                    image = self.transform[choice_key](image)
                    mask = self.transform[choice_key](mask)
            choice_list.remove(choice_key)

        return image, mask

    def __len__(self):
        """ Overridden method from inheritted class so that
        len(self) returns the size of the dataset.
        """
        error_msg = 'Part of dataset is missing!\nNumber of tumor and mask images are not same.'
        total_files = len(os.listdir(self.dataset_dir))

        assert (total_files % 2 == 0), error_msg
        return total_files//2
