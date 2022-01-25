import os
import pandas as pd 
import torch
import numpy as np 
from enum import Enum
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn
from PIL import Image
import re
from torchvision import transforms

class MyDataset(Dataset):
    
    training_image_trasformation_parameter = {
        "crop":{
            "size": 224,
            "scale": (0.08,1.0),
            "ratio": (3. / 4., 4. / 3.),
        },
        "mean": torch.tensor([0.485, 0.456, 0.406]), # the mean of the training data on the 3 channels (RGB)
        "std_dev": torch.tensor([0.229, 0.224, 0.225]) # the standard deviation of the training data on the 3 channels (RGB)
    }
    
    evaluation_image_trasformation_parameter = {
        "crop":{
            "size": 256,
            "center": 224
        },
        "mean": torch.tensor([0.485, 0.456, 0.406]), # the mean of the training data on the 3 channels (RGB)
        "std_dev": torch.tensor([0.229, 0.224, 0.225]) # the standard deviation of the training data on the 3 channels (RGB)
    }
    
    def __init__(self, directory_of_data:str = None, percentage:int = 100, already_computed_dataframe: pd.DataFrame = None):
        """Create a new dataset from source files

        Args:
            directory_of_data (str): [description]
        """
        if already_computed_dataframe is not None:
            self.directory_of_data = directory_of_data
            self._dataset = already_computed_dataframe
            return
        
        if not os.path.exists(directory_of_data):
            raise ValueError(f"{directory_of_data} not Exist!")
        if not os.path.isdir(directory_of_data):
            raise ValueError(f"{directory_of_data} is not a directory!")
        
        _temp_dataset=pd.read_csv(f"{directory_of_data}/results.csv", sep="|", skipinitialspace=True)[["image_name","comment"]].sample(frac=1)
        self._dataset = _temp_dataset.head(int(len(_temp_dataset)*(percentage/100)))
        self.directory_of_data = directory_of_data
        
    def get_fraction_of_dataset(self, percentage: int): 
        _temp_df_moved = self._dataset.head(int(len(self._dataset)*(percentage/100)))
        _temp_df_copy = _temp_df_moved.copy()
        return MyDataset(directory_of_data=self.directory_of_data, already_computed_dataframe=_temp_df_copy)
    
    def get_all_distinct_words_in_dataset(self):
        words = []
        for idx,row in self._dataset.iterrows():
            for word in re.findall("[\\w]+|\.|\,", row["comment"].lower()):
                if word not in words:
                    words.append(word)
        return words
    
    def __len__(self):
        return self._dataset.shape[0]
    
    def __getitem__(self, idx):
        
        image, caption = Image.open(f"{self.directory_of_data}/images/{self._dataset.iloc[idx]['image_name']}").convert('RGB'), \
                            re.findall("[\\w]+|\.|\,", self._dataset.iloc[idx]["comment"].lower())
        
        return image, caption 
    
    def pack_minibatch_training(self, data, vocabulary):
        
        # Sort a data list by caption length (descending order).
        data.sort(key=lambda x: len(x[1]), reverse=True)
    
        images, captions = zip(*data)
        
        operations = transforms.Compose([
                transforms.RandomResizedCrop(MyDataset.training_image_trasformation_parameter["crop"]["size"], scale=MyDataset.training_image_trasformation_parameter["crop"]["scale"], ratio=MyDataset.training_image_trasformation_parameter["crop"]["ratio"]), # Crop a random portion of image and resize it to a given size.
                transforms.RandomHorizontalFlip(p=0), # Horizontally flip the given image randomly with a given probability.
                transforms.ToTensor(), # Convert a PIL Image or numpy.ndarray to tensor.  (H x W x C) in the range [0, 255] to a torch.FloatTensor of shape (C x H x W) in the range [0.0, 1.0] 
                transforms.Normalize(mean=MyDataset.training_image_trasformation_parameter["mean"], std=MyDataset.training_image_trasformation_parameter["std_dev"]),
        ])
        images = list(map(lambda image: operations(image),list(images)))
        
        # Merge images (from tuple of 3D tensor to 4D tensor).
        images = torch.stack(images, 0)
        
        caption_lengths = [len(caption) for caption in captions]
        captions_ids = [vocabulary.translate(caption) for caption in captions]
        captions_withoud_start_id = [vocabulary.translate(caption)[1:] for caption in captions]
        captions = nn.utils.rnn.pad_sequence(captions_ids, padding_value=0, batch_first=True)
        captions_withoud_start_id = nn.utils.rnn.pad_sequence(captions_withoud_start_id, padding_value=0, batch_first=True)
        return images,captions_withoud_start_id.type(torch.LongTensor),torch.tensor(caption_lengths),captions
    
    def pack_minibatch_evaluation(self, data):
        
        # Sort a data list by caption length (descending order).
        data.sort(key=lambda x: len(x[1]), reverse=True)
    
        images, captions = zip(*data)
        
        operations = transforms.Compose([
                transforms.Resize(MyDataset.evaluation_image_trasformation_parameter["crop"]["size"]), 
                transforms.CenterCrop(MyDataset.evaluation_image_trasformation_parameter["crop"]["center"]),  # Crops the given image at the center.
                transforms.ToTensor(),
                transforms.Normalize(mean=MyDataset.evaluation_image_trasformation_parameter["mean"], std=MyDataset.evaluation_image_trasformation_parameter["std_dev"])
        ])
        images = images.map(lambda image: operations(image))
        
        # Merge images (from tuple of 3D tensor to 4D tensor).
        images = torch.stack(images, 0)
        
        caption_lengths = [len(caption) for caption in captions]
        captions
        captions = nn.utils.rnn.pad_sequence(captions, padding_value=0, batch_first=True)
        return images,captions.type(torch.LongTensor),caption_lengths 
        