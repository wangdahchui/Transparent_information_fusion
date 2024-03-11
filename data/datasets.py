import numpy as np
import torch
from torch.utils.data import Dataset

class THU_006_basic(Dataset):
    def __init__(self, args,data_dir = '/home/user/data/a_bearing/a_018_THU24_pro/',
                 flag='train',
                 task='1hz',
                 transform=None): # 1hz, 10hz, 15hz,IF
        self.flag = args.flag
        self.task = args.task
        self.transform = args.transform
        self.data_loader(args.data_dir)
        self.data_create()
        # Load data and labels 
    def data_loader(self,data_dir):
        self.data = np.load(data_dir + '_data.npy').astype(np.float32)
        self.labels = np.load(data_dir + '_label.npy').astype(np.float32)
        self.transform = transform
    def data_create(self):
        # Define split ratios
        train_ratio = 0.6
        val_ratio = 0.1
        # Calculate test_ratio to ensure ratios sum to 1
        test_ratio = 1 - (train_ratio + val_ratio)

        # Split indices for each label
        train_indices, val_indices, test_indices = [], [], []
        for label in np.unique(self.labels):
            label_indices = np.where(self.labels == label)[0]
            # np.random.shuffle(label_indices)
            
            n_train = int(len(label_indices) * train_ratio)
            n_val = int(len(label_indices) * val_ratio)
            # Remaining indices are for testing
            n_test = len(label_indices) - n_train - n_val

            # Append indices for each set
            train_indices.extend(label_indices[:n_train])
            val_indices.extend(label_indices[n_train:n_train + n_val])
            test_indices.extend(label_indices[n_train + n_val:])

        # Select indices based on the flag
        if self.flag == 'train':
            selected_indices = train_indices
        elif self.flag == 'val':
            selected_indices = val_indices
        elif flag == 'test':
            self.selected_indices = test_indices
        else:
            raise ValueError("Invalid flag. Please choose from 'train', 'val', or 'test'.")

        self.selected_data = self.data[selected_indices]
        self.selected_labels = self.labels[selected_indices]

    def __len__(self):
        return len(self.selected_data)

    def __getitem__(self, idx):
        sample = self.selected_data[idx]
        label = self.selected_labels[idx]
        
        if self.transform:
            sample = self.transform(sample)
        
        return sample, label

class THU_006_generalization(Dataset):
    def __init__(self, args,data_dir = '/home/user/data/a_bearing/a_006_THU_pro/LQ_fusion/',
                 flag='train',
                 target='1hz',
                 transform=None): # 1hz, 10hz, 15hz,IF
        # Load data and labels 
        self.flag = args.flag
        self.task = args.task
        self.transform = args.transform
        
        self.data_1hz = np.load(data_dir + '1hz_data.npy').astype(np.float32)
        self.labels_1hz = np.load(data_dir + '1hz_label.npy').astype(np.float32)
        self.data_10hz = np.load(data_dir + '10hz_data.npy').astype(np.float32)
        self.labels_10hz = np.load(data_dir + '10hz_label.npy').astype(np.float32)
        self.data_15hz = np.load(data_dir + '15hz_data.npy').astype(np.float32)
        self.labels_15hz = np.load(data_dir + '15hz_label.npy').astype(np.float32)
        
        if target == '1hz':
            self.train_data = torch.cat((self.data_10hz, self.data_15hz), 0)
            self.train_labels = torch.cat((self.labels_10hz, self.labels_15hz), 0)
            self.test_data = self.data_1hz
            self.test_labels = self.labels_1hz
        elif target == '10hz':
            self.train_data = torch.cat((self.data_1hz, self.data_15hz), 0)
            self.train_labels = torch.cat((self.labels_1hz, self.labels_15hz), 0)
            self.test_data = self.data_10hz
            self.test_labels = self.labels_10hz
        elif target == '15hz':
            self.train_data = torch.cat((self.data_1hz, self.data_10hz), 0)
            self.train_labels = torch.cat((self.labels_1hz, self.labels_10hz), 0)
            self.test_data = self.data_15hz
            self.test_labels = self.labels_15hz
            
        if flag == 'train':
            self.selected_data = self.train_data
            self.selected_labels = self.train_labels
        elif flag == 'val':
            self.selected_data = self.train_data
            self.selected_labels = self.train_labels
        elif flag == 'test':
            self.selected_data = self.test_data
            self.selected_labels = self.test_labels

    def __len__(self):
        return len(self.selected_data)

    def __getitem__(self, idx):
        sample = self.selected_data[idx]
        label = self.selected_labels[idx]
        
        if self.transform:
            sample = self.transform(sample)
        
        return sample, label


    
class THU_006_few_shot(Dataset):
    def __init__(self, args,data_dir, flag='train', task='1hz', transform=None, k_shot=5): # 1hz, 10hz, 15hz,IF
        # Load data and labels 
        self.flag = args.flag
        self.task = args.task
        self.transform = args.transform
        
        self.data = np.load(data_dir + '_data.npy').astype(np.float32)
        self.labels = np.load(data_dir + '_label.npy').astype(np.float32)
        self.transform = transform
        self.k_shot = k_shot

        # Define split ratios
        train_ratio = 0.6
        val_ratio = 0.1
        # Calculate test_ratio to ensure ratios sum to 1
        test_ratio = 1 - (train_ratio + val_ratio)

        # Split indices for each label
        train_indices, val_indices, test_indices = [], [], []
        for label in np.unique(self.labels):
            label_indices = np.where(self.labels == label)[0]
            # np.random.shuffle(label_indices)
            
            n_train = int(len(label_indices) * train_ratio)
            n_val = int(len(label_indices) * val_ratio)
            # Remaining indices are for testing
            n_test = len(label_indices) - n_train - n_val

            # Append indices for each set
            train_indices.extend(label_indices[:n_train][:self.k_shot])
            val_indices.extend(label_indices[n_train:n_train + n_val])
            test_indices.extend(label_indices[n_train + n_val:])

        # Select indices based on the flag
        if flag == 'train':
            selected_indices = train_indices
        elif flag == 'val':
            selected_indices = val_indices
        elif flag == 'test':
            selected_indices = test_indices
        else:
            raise ValueError("Invalid flag. Please choose from 'train', 'val', or 'test'.")

        self.selected_data = self.data[selected_indices]
        self.selected_labels = self.labels[selected_indices]

    def __len__(self):
        return len(self.selected_data)

    def __getitem__(self, idx):
        sample = self.selected_data[idx]
        label = self.selected_labels[idx]
        
        if self.transform:
            sample = self.transform(sample)
        
        return sample, label
# class THU_Voltage2Dataset(Dataset):
#     def __init__(self, data_dir, flag='train', task='IF', transform=None): # 1hz, 10hz, 15hz,IF
#         # Load data and labels
#         self.data = np.load(data_dir + f'/{task}_data.npy')
#         self.labels = np.load(data_dir + f'/{task}_label.npy')
#         self.transform = transform

#         # Define split ratios
#         train_ratio = 0.6
#         val_ratio = 0.1
#         # Calculate test_ratio to ensure ratios sum to 1
#         test_ratio = 1 - (train_ratio + val_ratio)

#         # Split indices for each label
#         train_indices, val_indices, test_indices = [], [], []
#         for label in np.unique(self.labels):
#             label_indices = np.where(self.labels == label)[0]
#             # np.random.shuffle(label_indices)
            
#             n_train = int(len(label_indices) * train_ratio)
#             n_val = int(len(label_indices) * val_ratio)
#             # Remaining indices are for testing
#             n_test = len(label_indices) - n_train - n_val

#             # Append indices for each set
#             train_indices.extend(label_indices[:n_train])
#             val_indices.extend(label_indices[n_train:n_train + n_val])
#             test_indices.extend(label_indices[n_train + n_val:])

#         # Select indices based on the flag
#         if flag == 'train':
#             selected_indices = train_indices
#         elif flag == 'val':
#             selected_indices = val_indices
#         elif flag == 'test':
#             selected_indices = test_indices
#         else:
#             raise ValueError("Invalid flag. Please choose from 'train', 'val', or 'test'.")

#         self.selected_data = self.data[selected_indices]
#         self.selected_labels = self.labels[selected_indices]

#     def __len__(self):
#         return len(self.selected_data)

#     def __getitem__(self, idx):
#         sample = self.selected_data[idx]
#         label = self.selected_labels[idx]
        
#         if self.transform:
#             sample = self.transform(sample)
        
#         return sample, label
    
if __name__ == '__main__':

    from torch.utils.data import DataLoader

    # 假设数据已经准备好在指定的目录中
    data_dir = '/home/user/data/a_bearing/a_006_THU_pro/LQ_fusion/1hz'  # 更新为你的数据目录

    # 创建数据集实例
    train_dataset = THU_VibVoltageDataset(data_dir=data_dir, flag='train', task='1hz')
    val_dataset = THU_VibVoltageDataset(data_dir=data_dir, flag='val', task='10hz')
    test_dataset = THU_VibVoltageDataset(data_dir=data_dir, flag='test', task='15hz')

    IF_data_set = THU_VibVoltageDataset(data_dir='/home/user/data/a_bearing/a_018_THU24_pro/IF', flag='train', task='IF')
    print(len(train_dataset))
    print(len(val_dataset))
    print(len(test_dataset))
    print(len(IF_data_set))
    
    # 创建DataLoader以便批量加载数据
    train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=4, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=4, shuffle=False)
    IF_loader = DataLoader(IF_data_set, batch_size=4, shuffle=False)

    # 展示训练集中的一些样本
    print("Training samples:")
    for data, labels in train_loader:
        
        print("Data batch shape:", data.shape)
        print("Labels batch shape:", labels.shape)
        break  # 只展示第一个批次
    print("Validation samples:")
    for data, labels in val_loader:
        print("Data batch shape:", data.shape)
        print("Labels batch shape:", labels.shape)
        break  # 只展示第一个批次
    print("Test samples:")
    for data, labels in test_loader:
        print("Data batch shape:", data.shape)
        print("Labels batch shape:", labels.shape)
        break  # 只展示第一个批次
    print("IF samples:")
    for data, labels in IF_loader:
        print("Data batch shape:", data.shape)
        print("Labels batch shape:", labels.shape)
        break  # 只展示第一个批次


