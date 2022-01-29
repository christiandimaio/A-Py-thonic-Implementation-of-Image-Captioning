from .Encoder.CResNet50 import CResNet50
from .Decoder.RNetvHC import RNetvHC
from .Decoder.RNetvI import RNetvI
from .Decoder.RNetvH import RNetvH
from .CaRNet import CaRNet
from enum import Enum


class Encoder(Enum):
    CResNet50 = 0

def FactoryEncoder(encoder: Encoder):
    if encoder == Encoder.CResNet50:
        return CResNet50
    raise NotImplementedError("This encoder is not implemented yet")

####################################################################

class Decoder(Enum):
    RNetvI = 0
    RNetvH = 1
    RNetvHC = 2

def FactoryDecoder(decoder: Decoder):
    if decoder == decoder.RNetvI:
        return RNetvI
    if decoder == decoder.RNetvH:
        return RNetvH
    if decoder == decoder.RNetvHC:
        return RNetvHC
    raise NotImplementedError("This decoder is not implemented yet")

#####################################################################

class NeuralNet(Enum):
    CaRNet = 0

def FactoryNeuralNet(net: NeuralNet):
    if net == NeuralNet.CaRNet:
        return CaRNet
    raise NotImplementedError("This neural net is not implemented yet")