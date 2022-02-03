print("Coded with love by christiandimaio aka gnekt :* ")

from torch.utils.data import DataLoader
from NeuralModels.FactoryModels import *
from NeuralModels.Dataset import MyDataset
from NeuralModels.Vocabulary import Vocabulary




if __name__ == "__main__":
    
    dataset = MyDataset("./dataset/flickr30k_images", percentage=8)
    vocabulary = Vocabulary(dataset) 
    
    # Load Encoder and Decoder models
    attention = FactoryAttention(Attention.Attention)
    decoder = FactoryDecoder(Decoder.RNetvHCAttention)
    encoder = FactoryEncoder(Encoder.CResNet50Attention)
    
    # # Load the NeuralNet
    net = FactoryNeuralNet(NeuralNet.CaRNet)(
                                                encoder=encoder,
                                                decoder=decoder,
                                                attention=attention,
                                                net_name="CaRNetvHCAttention",
                                                encoder_dim= 1024,
                                                hidden_dim= 512,
                                                padding_index= vocabulary.predefined_token_idx()["<PAD>"],
                                                vocab_size= len(vocabulary.word2id.keys()),
                                                embedding_dim= vocabulary.embeddings.shape[1],
                                                device="cuda:0"
                                            )
    # Load the NeuralNet
    # net = FactoryNeuralNet(NeuralNet.CaRNet)(
    #                                             encoder=encoder,
    #                                             decoder=decoder,
    #                                             net_name="CaRNetvHC",
    #                                             encoder_dim= 1024,
    #                                             hidden_dim= 1024,
    #                                             padding_index= vocabulary.predefined_token_idx()["<PAD>"],
    #                                             vocab_size= len(vocabulary.word2id.keys()),
    #                                             embedding_dim= vocabulary.embeddings.shape[1],
    #                                             device="cpu"
    #                                         )
    
    dc = dataset.get_fraction_of_dataset(percentage=1, delete_transfered_from_source=True)
    df = dataset.get_fraction_of_dataset(percentage=1, delete_transfered_from_source=True)
    # use dataloader facilities which requires a preprocessed dataset
       
    
    dataloader_training = DataLoader(dc, batch_size=32,
                        shuffle=True, num_workers=2, collate_fn = lambda data: dataset.pack_minibatch_training(data,vocabulary))
    
    dataloader_evaluation = DataLoader(df, batch_size=32,
                        shuffle=True, num_workers=2, collate_fn = lambda data: dataset.pack_minibatch_evaluation(data,vocabulary))
    
    
    net.train(
                train_set=dataloader_training,
                validation_set=dataloader_evaluation,
                lr=1e-3,
                epochs=500,
                vocabulary=vocabulary
            )