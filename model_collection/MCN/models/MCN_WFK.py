
# Description: Signal processing collaborated with deep learning aims to establish a novel causal network architecture and the proposed MCN achieved
# an interpretable expression with high accuracy. It should be noted that multiplication and convolution modules are mathematically connected as a 
# combination of BPNN and CNN, where the interpretable designed filters enhances the data mining ability.
# Authors   : Rui Liu, Xiaoxi Ding
# URL       : https://github.com/CQU-BITS/MCN-main
# The related reference : R. Liu, X. Ding*, Q. Wu, Q. He and Y. Shao, "An Interpretable Multiplication-Convolution Network for Equipment
# Intelligent Edge Diagnosis", IEEE Transactions on Systems, Man and Cybernetics: Systems,
# DOI: 10.1109/TSMC.2023.3346398
# Date     : 2024/01/16
# Version: v0.1.0
# Copyright by CQU-BITS

############################################## multiple_channel_version please refer the MCN_GFK.py ##############################################
import numpy as np
import torch
from torch import nn


class Wiener_fast(nn.Module):
    def __init__(self, ff, num_MFKs=8):
        super(Wiener_fast, self).__init__()

        self.num = num_MFKs  # MFKs个数，决定输出模态个数
        # fc >> [self.num, 1]  中心频率
        self.fc = nn.Parameter(torch.linspace(0, ff[-1], self.num).view(-1, 1), requires_grad=True)
        # alpha >> [self.num, 1] 带宽惩罚因子
        self.alpha = nn.Parameter(torch.linspace(25000, 15000, self.num).view(-1, 1), requires_grad=True)
        self.w = nn.Parameter(torch.linspace(0, ff[-1], steps=len(ff)).view(-1, len(ff)), requires_grad=False)

    def forward(self, waveforms):
        fft_wave = torch.fft.rfft(waveforms, dim=2, norm='ortho')
        self.filters = 1 / (1 + 2 * self.alpha * (self.w - self.fc) ** 2)  # [self.num, 1024]
        self.yout = torch.tensor([]).to(waveforms.device)
        modal_remainder = waveforms
        for ii in range(self.num):
            current_model = torch.mul(modal_remainder, self.filters[ii, :])
            self.yout = torch.cat((self.yout, current_model), dim=1)
            modal_remainder = modal_remainder - current_model
        return self.yout


class MCN_WFK(nn.Module):
    def __init__(self, ff, in_channels=1, num_MFKs=8, num_classes=5):
        super(MCN_WFK, self).__init__()
        self.features = Wiener_fast(ff=ff, num_MFKs=num_MFKs)
        self.conv = nn.Sequential(
            nn.Conv1d(num_MFKs, 64, kernel_size=7, stride=3, padding=1),
            nn.ReLU(inplace=True),
        )
        self.AdpAvgpool = nn.AdaptiveAvgPool1d(10)
        self.flatten = nn.Flatten()
        self.fc = nn.Sequential(
            nn.Linear(64 * 10, num_classes),
        )

    def forward(self, inputs):
        out = self.features(inputs)
        out = self.conv(out)
        out = self.AdpAvgpool(out)
        out = self.flatten(out)
        out = self.fc(out)
        return out

class MultiChannel_MCN_WFK(nn.Module):
    def __init__(self, ff, in_channels=1, num_MFKs=8, num_classes=5):
        super(MultiChannel_MCN_WFK, self).__init__()
        self.features = nn.ModuleList([Wiener_fast(ff=ff, num_MFKs=num_MFKs) for _ in range(in_channels)])
        self.conv = nn.Sequential(
            nn.Conv1d(in_channels * num_MFKs, 64, kernel_size=7, stride=3, padding=1),
            nn.ReLU(inplace=True),
        )
        self.AdpAvgpool = nn.AdaptiveAvgPool1d(10)
        self.flatten = nn.Flatten()
        self.fc = nn.Sequential(
            nn.Linear(64 * 10, num_classes),
        )

    def forward(self, inputs):
        out = torch.cat([self.features[i](inputs[:, i].unsqueeze(1))for i in range(len(self.features))], dim=1)
        out = self.conv(out.real)
        out = self.AdpAvgpool(out)
        out = self.flatten(out)
        out = self.fc(out)
        return out

if __name__ == '__main__':
    device = torch.device('cuda:0')
    temp = torch.randn([1, 1, 1024]).to(device)
    ff = np.arange(0, 1024) / 1024
    model = MCN_WFK(ff=ff, in_channels=1, num_MFKs=8, num_classes=5).to(device)

    out = model(temp)
    print(out.shape)

