"""One fully learned evaluation network and policy head.

No fixed material buffer, classical score, blending coefficient or fallback.
The direct linear path is a trainable neural layer, initialized to zero.
"""
import torch
from torch import nn
from pure_features import DIM,MOVES

class PureNet(nn.Module):
    def __init__(self,width=512):
        super().__init__()
        if width not in (256,512):raise ValueError('Width must be 256 or 512')
        self.width=width
        self.fc1=nn.Linear(DIM,width)
        self.fc2=nn.Linear(width,32)
        self.value=nn.Linear(32,1)
        self.linear=nn.Linear(DIM,1)
        self.policy=nn.Linear(width,len(MOVES))
        self.dropout=nn.Dropout(.1)
        nn.init.zeros_(self.linear.weight);nn.init.zeros_(self.linear.bias)
        nn.init.normal_(self.value.weight,std=.01);nn.init.zeros_(self.value.bias)

    def forward(self,x):
        first=torch.relu(self.fc1(x));h=torch.relu(self.fc2(self.dropout(first)))
        cp=600*(self.value(h)+self.linear(x)).squeeze(-1)
        return cp.clamp(-10000,10000),self.policy(first)
