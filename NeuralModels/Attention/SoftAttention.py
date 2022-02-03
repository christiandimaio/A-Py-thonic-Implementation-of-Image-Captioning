from re import S
import torch.nn as nn
import torch
import torchvision.models as models
from typing import Tuple

class SoftAttention(nn.Module):
    """
        Simple implementation of Bahdanau Attention model.
    """
    
    def __init__(self, encoder_dim: int , hidden_dim: int, attention_dim: int, number_of_splits: int = 7):
        """Constructor for a SoftAttention model 

        Args:
            encoder_dim (int): 
                The number of features extracted from the image.
            hidden_dim (int): 
                The capacity of the LSTM.
            attention_dim (int): 
                The capacity of the Attention Model.
            number_of_splits (int):
                Number of image portions for Heigth (square resolution)
        """
        super(SoftAttention, self).__init__()
        
        self.attention_dim = attention_dim
        
        self.encoder_dim = encoder_dim
        
        self.number_of_splits = number_of_splits
        
        self.image_attention_projection = nn.Linear(encoder_dim, attention_dim)
        
        self.lstm_hidden_state_attention_projection = nn.Linear(hidden_dim, attention_dim)
        
        self.attention = nn.Linear(attention_dim, 1)
        
        self.ReLU = nn.ReLU()
        
        self.out = nn.Softmax(dim=1)
        
        
    def forward(self, images: torch.Tensor, lstm_hidden_states: torch.Tensor) -> Tuple[torch.Tensor,torch.Tensor]:
        """Compute z_t given images and hidden state at t-1 for all the element in the batch.

        Args:
            images (torch.Tensor): `(batch_dim, image_portions, encoder_dim)`
                The tensor of the images in the batch.  
            lstm_hidden_states (torch.Tensor): `(batch_dim, hidden_dim)`
                The hidden states at t-1 of all the element in the batch. 

        Returns:
            (Tuple[torch.Tensor,torch.Tensor]): `[(batch_dim, encoder_dim), (batch_dim, image_portions)]`
                Z_t and the alphas evaluated for each portion of the image, for each image in the batch.
        """
        
        _images_attention = self.image_attention_projection(images) # IN: (batch_dim, image_portions, encoder_dim) -> Out: (batch_dim, image_portions, attention_dim)
        
        _lstm_attention = self.lstm_hidden_state_attention_projection(lstm_hidden_states) # IN: (batch_dim, hidden_dim) -> Out: (batch_size, attention_dim)
        
        # (batch_size, image_portions, attention_dim) + (batch_size, 1, attention_dim) -> Broadcast on dim 2 -> (batch_size, image_portions, attention_dim)
        _attention = self.attention(self.ReLU(_images_attention + _lstm_attention.unsqueeze(1))).squeeze(2) # IN: (batch_dim, image_portions, attention_dim) -> Out: (batch_size, image_portions)
        
        _alphas_t = self.out(_attention) # Out: (batch_dim, image_portions)
        
        # Retrieve z_t
        attention_weighted_encoding = (images * _alphas_t.unsqueeze(2)).sum(dim=1) # Out: (batch_dim, encoder_dim)
        
        return attention_weighted_encoding, _alphas_t
        