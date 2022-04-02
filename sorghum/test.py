# %%
import albumentations as A
from torch.utils.data import DataLoader
from pytorch_lightning import Trainer
from albumentations.pytorch.transforms import ToTensorV2
from train import SorghumLitModel
from src.data import SorghumDataset
from src.constants import BACKBONE_IMG_SIZE

# %%
# Tried
# CHK_PATH = '/home/brian/github/kaggle_herbarium_2022/sorghum/tb_logs/20220323_105943/epoch=18-val_loss=0.31.ckpt'
# CHK_PATH = '/home/brian/github/kaggle_herbarium_2022/sorghum/tb_logs/20220323_225103/epoch=16-val_loss=0.20.ckpt' # 0.507
# CHK_PATH = '/home/brian/github/kaggle_herbarium_2022/sorghum/tb_logs/20220324_094248/epoch=16-val_loss=0.11.ckpt' # 0.553
# CHK_PATH = '/home/brian/github/kaggle_herbarium_2022/sorghum/tb_logs/20220324_111631_Added dropout layer, turned off horz vert flips/epoch=23-val_loss=0.09.ckpt'
# CHK_PATH = '/home/brian/github/kaggle_herbarium_2022/sorghum/tb_logs/20220325_214512_Added dropout layer, turned on normalization, left on flips/epoch=23-val_loss=0.07.ckpt'
# CHK_PATH = '/home/brian/github/kaggle_herbarium_2022/sorghum/tb_logs/20220329_024615_Added dropout layer, turned on normalization, left on flips/epoch=25-val_loss=0.08.ckpt' # 0.575
# CHK_PATH = '/home/brian/github/kaggle_herbarium_2022/sorghum/tb_logs/20220402_103938_Dropout, RandomResizedCrop, Flips, UnNormalized/epoch=28-val_loss=0.25.ckpt'
# CHK_PATH = "/home/brian/github/kaggle_herbarium_2022/sorghum/tb_logs/20220402_135655_SH1R0's transforms, without normalization and ISONoise/epoch=28-val_loss=2.27.ckpt"
# CHK_PATH = "/home/brian/github/kaggle_herbarium_2022/sorghum/tb_logs/20220402_195622_SH1R0's transforms, without normalization and ISONoise/epoch=23-val_loss=0.38.ckpt"

# To Try
CHK_PATH = ""
# CHK_PATH = ""
# CHK_PATH = ""
# CHK_PATH = ""
# CHK_PATH = ""
# CHK_PATH = ""
# CHK_PATH = ""

# %%
# Need to have caled self.save_hyperparameters() in model init for the below to work!
model = SorghumLitModel.load_from_checkpoint(checkpoint_path=CHK_PATH) 

transform = A.Compose([
                A.Resize(height=BACKBONE_IMG_SIZE[model.backbone], width=BACKBONE_IMG_SIZE[model.backbone]),
                # A.Normalize(IMAGENET_NORMAL_MEAN, IMAGENET_NORMAL_STD),
                ToTensorV2(), # np.array HWC image -> torch.Tensor CHW
            ])

test_dataset = SorghumDataset(csv_fullpath='test.csv', testset=True, transform=transform) # xception: 299, vit: 384
dl_test = DataLoader(dataset=test_dataset, shuffle=False, batch_size=512, num_workers=16)

trainer = Trainer(gpus=1)
results = trainer.test(model=model, dataloaders=dl_test, verbose=True)
