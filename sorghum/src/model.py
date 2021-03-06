# %%
import torch
import torch.nn.functional as F
import torch.nn as nn

from pretrainedmodels import xception
from efficientnet_pytorch import EfficientNet
# Also try densenet, efficientnet, swin, etc.

# %%
class Identity(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, x):
        return x

# %%
class XceptionModel(nn.Module):
    def __init__(self, num_classes, pretrained, n_hidden_nodes, dropout_rate, freeze_backbone=False):
        super(XceptionModel, self).__init__()
        self.n_hidden_nodes = n_hidden_nodes
        self.dropout = nn.Dropout(p=dropout_rate)

        # INPUT_SIZE = 3 x 299 x 299
        self.backbone              = xception(num_classes=1000, pretrained='imagenet' if pretrained else False) 
        self.backbone.last_linear  = nn.Identity() # Outputs 2048

        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False

        n_backbone_out          = 2048
        self.target_size        = 299

        if self.n_hidden_nodes is None:
            self.img_fc1 = nn.Linear(n_backbone_out, num_classes)
        else:
            self.img_fc1 = nn.Linear(n_backbone_out, n_hidden_nodes) # 2048 to 4096
            self.relu1 = nn.ReLU()
            self.fc2 = nn.Linear(n_hidden_nodes, n_hidden_nodes//2) # 4096 to 2048
            self.relu2 = nn.ReLU()
            self.fc3 = nn.Linear(n_hidden_nodes//2, n_hidden_nodes//4) # 2048 to 1024
            self.relu3 = nn.ReLU()
            self.fc4 = nn.Linear(n_hidden_nodes//4, num_classes) # 1024 to 100
            self.relu4 = nn.ReLU()

    def forward(self, x):
        if self.n_hidden_nodes is not None:
            out = self.backbone(x)
            out = self.dropout(out)
            out = self.img_fc1(out)
            out = self.relu1(out)
            out = self.dropout(out)
            out = self.fc2(out)
            out = self.relu2(out)
            out = self.dropout(out)
            out = self.fc3(out)
            out = self.relu4(out)
            out = self.fc4(out) # No activation and no softmax at the end (contained in F.cross_entropy())
        else:
            out = self.backbone(x)
            out = self.dropout(out)
            out = self.img_fc1(out)
        return out
# %%
class EfficientNetModel(nn.Module):
    def __init__(self, n_hidden_nodes, dropout_rate, freeze_backbone=False, version='b3'):
        super(EfficientNetModel, self).__init__()
        self.dropout = nn.Dropout(p=dropout_rate)
        num_classes  = 100

        model_name = 'efficientnet-' + version
        self.backbone= EfficientNet.from_pretrained(model_name) # Load pretrained model by default
        self.target_size = 1024 # The loaded backbone supports different input sizes; this is not fixed.
        n_backbone_out = 1000 # This one is fixed though.

        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False

        self.img_fc1 = nn.Linear(n_backbone_out, n_hidden_nodes//2)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(n_hidden_nodes//2, n_hidden_nodes//4)
        self.relu2 = nn.ReLU()
        self.fc3 = nn.Linear(n_hidden_nodes//4, num_classes)
        self.relu3 = nn.ReLU()
    
    def forward(self, x):
        out = self.backbone(x)
        out = self.dropout(out)
        out = self.img_fc1(out)
        out = self.relu1(out)
        out = self.dropout(out)
        out = self.fc2(out)
        out = self.relu2(out)
        out = self.dropout(out)
        out = self.fc3(out) # No activation and no softmax at the end (contained in F.cross_entropy())
        return out

class ResNeSt269(nn.Module):
    def __init__(self, n_hidden_nodes, dropout_rate, freeze_backbone=False):
        super(ResNeSt269, self).__init__()
        self.dropout = nn.Dropout(p=dropout_rate)
        num_classes  = 100

        # https://github.com/zhanghang1989/ResNeSt#pretrained-models
        torch.hub.list('zhanghang1989/ResNeSt', force_reload=True)
        self.backbone = torch.hub.load('zhanghang1989/ResNeSt', 'resnest50', pretrained=True) # Load pretrained model by default
        self.target_size = 512 # The loaded backbone supports different input sizes; this is not fixed.

        n_backbone_out = 1000 # This one is fixed.

        if freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False

        self.img_fc1 = nn.Linear(n_backbone_out, n_hidden_nodes//2)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(n_hidden_nodes//2, n_hidden_nodes//4)
        self.relu2 = nn.ReLU()
        self.fc3 = nn.Linear(n_hidden_nodes//4, num_classes)
        self.relu3 = nn.ReLU()
    
    def forward(self, x):
        out = self.backbone(x)
        out = self.dropout(out)
        out = self.img_fc1(out)
        out = self.relu1(out)
        out = self.dropout(out)
        out = self.fc2(out)
        out = self.relu2(out)
        out = self.dropout(out)
        out = self.fc3(out) # No activation and no softmax at the end (contained in F.cross_entropy())
        return out

# %%
if __name__=='__main__':
    model = EfficientNet(n_hidden_nodes=1024, dropout_rate=0.5)
    model = ResNeSt269(n_hidden_nodes=1024, dropout_rate=0.5)

    print(model)

