import torch
from typing import Type, Any, Callable, Union, List, Optional
from torch import Tensor
from torch import nn
import torchvision
import complex_activations as compact
import complexnn as comp
from einops import rearrange

class ComplexToFloat(nn.Module): 
    def __init__(self):
        super().__init__()

    def forward(self, input):
        if not input.is_complex():
            raise ValueError(f"input should be a complex tensor. Got {input.dtype}")

        real, imag = input.real, input.imag

        return torch.cat([real, imag], dim= 1)

class Complex_mod(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, input):
        absolute_val = input.abs()
        angle = input.angle()

        return torch.stack([absolute_val, angle], dim= 1)
        # return absolute_val

class CDS_E(nn.Module):
    def __init__(self, num_classes: int= 10, dropout= 0.5):
        super().__init__()
        self.dropout = dropout
        self.num_classes= num_classes
        self.features = nn.Sequential(
                comp.ComplexConv2d(3, 8, kernel_size= 3, stride= 2),
                compact.CPReLU(),
                # comp.ComplexMaxPool2d(),
                comp.ComplexConv2d(8, 16, kernel_size= 3, stride= 2),
                compact.CPReLU(),
                comp.ComplexConv2d(16, 32, kernel_size= 3, stride= 2),
                compact.CPReLU(),
                comp.ComplexConv2d(32, 32, kernel_size= 3, stride= 2),
                compact.CPReLU(),
                )
        self.avgpool = comp.ComplexAdaptiveAvgPool2d((2, 2))
        self.classifier = nn.Sequential(
                # comp.ComplexConv2d(64*2*2, 128, kernel_size= 1),
                # compact.CPReLU(),
                comp.ComplexConv2d(32*2*2, self.num_classes, kernel_size= 1)
                )

    def forward(self, x):
        x = self.features(x)
        x = self.avgpool(x)
        # print(f"Shape of x after avgpool: {x.shape}")

        x = rearrange(x, 'b c h w -> b (c h w) 1 1')

        x = self.classifier(x)
        # print(f"shape of features after features: {x.shape}")

        return x




# def CDS_large(outsize=10, *args, **kwargs):
#     channels = {'prep': 64,
#                 'layer1': 128, 'layer2': 256, 'layer3': 256}
#     n = [
#         comp.ComplexConv2d(3, channels['prep'], kernel_size=3, padding=1, groups=1),
#
#         # layers.ConjugateLayer(channels['prep'], kern_size=1, use_one_filter=True),
#
#         # conv_bn_complex(channels['prep'], channels['prep'], groups=2),
#         # conv_bn_complex(channels['prep'], channels['layer1'], groups=2),
#         comp.ComplexNaiveBatchNorm2d(channels['prep']),
#         comp.ComplexMaxPool2d(2, 2),
#         residual_complex(channels['layer1'], groups=2),
#         conv_bn_complex(channels['layer1'], channels['layer2'], groups=4),
#         layers.MaxPoolMag(2),
#         conv_bn_complex(channels['layer2'], channels['layer3'], groups=2),
#         layers.MaxPoolMag(2),
#         residual_complex(channels['layer3'], groups=4),
#         layers.MaxPoolMag(4),
#         flatten(),
#         nn.Linear(channels['layer3']*2, outsize, bias=False),
#         mul(0.125),
#     ]
#     return nn.Sequential(*n)
#
#

# Alexnet implementation in complex numbers

class AlexNet(nn.Module):
    def __init__(self, num_classes: int = 10, dropout= 0.5):
        super().__init__()
        self.dropout= dropout
        self.num_classes= num_classes
        self.features = nn.Sequential(
                comp.ComplexConv2d(3, 64, kernel_size= 11, stride= 4, padding= 2),
                compact.CPReLU(),
                comp.ComplexMaxPool2d(3, 2),
                comp.ComplexConv2d(64, 192, kernel_size= 5, padding= 2),
                compact.CPReLU(),
                comp.ComplexMaxPool2d(3, 2),
                comp.ComplexConv2d(192, 384, kernel_size= 3, padding= 1),
                compact.CPReLU(),
                comp.ComplexConv2d(384, 256, kernel_size= 3, padding= 1),
                compact.CPReLU(),
                comp.ComplexConv2d(256, 256, kernel_size= 3, padding= 1),
                compact.CPReLU(),
                comp.ComplexMaxPool2d(3, 2),
                )
        self.avgpool = comp.ComplexAdaptiveAvgPool2d((3, 3))

        # self.convert_float = ComplexToFloat()
        # self.convert_float = Complex_mod()

        self.classifier = nn.Sequential(
                comp.ComplexConv2d(256, 4096, kernel_size= 3),
                compact.CPReLU(),
                comp.ComplexConv2d(4096, 4096, kernel_size= 1),
                compact.CPReLU(),
                comp.ComplexConv2d(4096, self.num_classes, kernel_size= 1)
                )

        # self.classifier = nn.Sequential(
        #         nn.Dropout(p= self.dropout),
        #         nn.Linear(2 * 256 * 1 * 1, 4096),
        #         nn.ReLU(inplace= True),
        #         nn.Dropout(p= self.dropout),
        #         nn.Linear(4096, 4096),
        #         nn.ReLU(inplace= True),
        #         nn.Linear(4096, self.num_classes),
        #         )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = self.avgpool(x)
        # x = self.convert_float(x)
        # x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x



cfg = {
        'Vgg11':[64, 'M', 128, 'M', 256, 256, 'M', 512, 512, 'M', 512, 512, 'M'],
        'Vgg13':[64, 64, 'M', 128, 128, 'M', 256, 256, 'M', 512, 512, 'M', 512, 512, 'M'],
        'Vgg16':[64, 64, 'M', 128, 128, 'M', 256, 256, 256, 'M', 512, 512, 512, 'M', 512, 512, 512, 'M'],
        'Vgg19':[64, 64, 'M', 128, 128, 'M', 256, 256, 256, 256, 'M', 512, 512, 512, 512, 'M', 512, 512, 512, 512, 'M'],
        }

class VGG(nn.Module):
    def __init__(self, vgg_name, num_classes= 10):
        super().__init__()
        self.features = self._make_layers(cfg[vgg_name])
        self.avgpool = comp.ComplexAdaptiveAvgPool2d((7, 7))
        # self.classifier = nn.Linear(2*512*7*7, num_classes)
        self.classifier = comp.ComplexConv2d(512*7*7, num_classes, kernel_size= 1)
        # self.classifier = nn.Sequential(
        #         nn.Linear(2* 512 * 7 * 7, 4096),
        #         nn.ReLU(inplace= True),
        #         nn.Dropout(),
        #         nn.Linear(4096, 4096),
        #         nn.ReLU(inplace= True),
        #         nn.Dropout(),
        #         nn.Linear(4096, num_classes),
        #         )
        # self.convert_float = ComplexToFloat()

    def forward(self, x):
        x = self.features(x)
        # print(f"Shape of x : {x.shape}")
        # out = self.convert_float(out)
        # out = torch.flatten(out, 1)
        x = rearrange(x, 'b c h w -> b (c h w) 1 1')
        out = self.classifier(x)

        return out

    def _make_layers(self, cfg):
        layers = []
        in_channels = 3

        for x in cfg:
            if x == 'M':
                layers += [comp.ComplexMaxPool2d(kernel_size= 2, stride= 2)]
            else:
                layers += [comp.ComplexConv2d(in_channels, x, kernel_size= 3, padding= 1),
                            # comp.ComplexBatchNorm2d(x),
                            comp.ComplexNaiveBatchNorm2d(x),
                            compact.CPReLU(),
                        ]
                in_channels= x

        layers += [comp.ComplexAdaptiveAvgPool2d((7, 7)),]
                

        return nn.Sequential(*layers)
        

# ResNet networks 

__all__ = ['ResNet', 'resnet18', 'resnet34', 'resnet50', 'resnet101',
           'resnet152', 'resnext50_32x4d', 'resnext101_32x8d',
           'wide_resnet50_2', 'wide_resnet101_2']


model_urls = {
    'resnet18': 'https://download.pytorch.org/models/resnet18-f37072fd.pth',
    'resnet34': 'https://download.pytorch.org/models/resnet34-b627a593.pth',
    'resnet50': 'https://download.pytorch.org/models/resnet50-0676ba61.pth',
    'resnet101': 'https://download.pytorch.org/models/resnet101-63fe2227.pth',
    'resnet152': 'https://download.pytorch.org/models/resnet152-394f9c45.pth',
    'resnext50_32x4d': 'https://download.pytorch.org/models/resnext50_32x4d-7cdf4587.pth',
    'resnext101_32x8d': 'https://download.pytorch.org/models/resnext101_32x8d-8ba56ff5.pth',
    'wide_resnet50_2': 'https://download.pytorch.org/models/wide_resnet50_2-95faca4d.pth',
    'wide_resnet101_2': 'https://download.pytorch.org/models/wide_resnet101_2-32ee1156.pth',
}


def conv3x3(in_planes: int, out_planes: int, stride: int = 1, groups: int = 1, dilation: int = 1):
    """3x3 convolution with padding"""
    return comp.ComplexConv2d(in_planes, out_planes, kernel_size=3, stride=stride,
                     padding=dilation, groups=groups, dilation=dilation)


def conv1x1(in_planes: int, out_planes: int, stride: int = 1):
    """1x1 convolution"""
    return comp.ComplexConv2d(in_planes, out_planes, kernel_size=1, stride=stride)


class BasicBlock(nn.Module):
    expansion: int = 1

    def __init__(
        self,
        inplanes: int,
        planes: int,
        stride: int = 1,
        downsample: Optional[nn.Module] = None,
        groups: int = 1,
        base_width: int = 64,
        dilation: int = 1,
        norm_layer: Optional[Callable[..., nn.Module]] = None
    ) -> None:
        super(BasicBlock, self).__init__()
        if norm_layer is None:
            # norm_layer = nn.BatchNorm2d
            norm_layer = comp.ComplexNaiveBatchNorm2d
        if groups != 1 or base_width != 64:
            raise ValueError('BasicBlock only supports groups=1 and base_width=64')
        if dilation > 1:
            raise NotImplementedError("Dilation > 1 not supported in BasicBlock")
        # Both self.conv1 and self.downsample layers downsample the input when stride != 1
        self.conv1 = conv3x3(inplanes, planes, stride)
        self.bn1 = norm_layer(planes)
        self.prelu = compact.CPReLU()
        self.conv2 = conv3x3(planes, planes)
        self.bn2 = norm_layer(planes)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x: Tensor) -> Tensor:
        identity = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.prelu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        if self.downsample is not None:
            identity = self.downsample(x)

        out += identity
        out = self.prelu(out)

        return out


class Bottleneck(nn.Module):
    # Bottleneck in torchvision places the stride for downsampling at 3x3 convolution(self.conv2)
    # while original implementation places the stride at the first 1x1 convolution(self.conv1)
    # according to "Deep residual learning for image recognition"https://arxiv.org/abs/1512.03385.
    # This variant is also known as ResNet V1.5 and improves accuracy according to
    # https://ngc.nvidia.com/catalog/model-scripts/nvidia:resnet_50_v1_5_for_pytorch.

    expansion: int = 4

    def __init__(
        self,
        inplanes: int,
        planes: int,
        stride: int = 1,
        downsample: Optional[nn.Module] = None,
        groups: int = 1,
        base_width: int = 64,
        dilation: int = 1,
        norm_layer: Optional[Callable[..., nn.Module]] = None
    ) -> None:
        super(Bottleneck, self).__init__()
        if norm_layer is None:
            # norm_layer = nn.BatchNorm2d
            norm_layer = comp.ComplexNaiveBatchNorm2d
        width = int(planes * (base_width / 64.)) * groups
        # Both self.conv2 and self.downsample layers downsample the input when stride != 1
        self.conv1 = conv1x1(inplanes, width)
        self.bn1 = norm_layer(width)
        self.conv2 = conv3x3(width, width, stride, groups, dilation)
        self.bn2 = norm_layer(width)
        self.conv3 = conv1x1(width, planes * self.expansion)
        self.bn3 = norm_layer(planes * self.expansion)
        self.prelu = compact.CPReLU()
        self.downsample = downsample
        self.stride = stride

    def forward(self, x: Tensor) -> Tensor:
        identity = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.prelu(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = self.prelu(out)

        out = self.conv3(out)
        out = self.bn3(out)

        if self.downsample is not None:
            identity = self.downsample(x)

        out += identity
        out = self.prelu(out)

        return out


class ResNet(nn.Module):

    def __init__(
        self,
        block: Type[Union[BasicBlock, Bottleneck]],
        layers: List[int],
        num_classes: int = 1000,
        zero_init_residual: bool = False,
        groups: int = 1,
        width_per_group: int = 64,
        replace_stride_with_dilation: Optional[List[bool]] = None,
        norm_layer: Optional[Callable[..., nn.Module]] = None
    ) -> None:
        super(ResNet, self).__init__()
        if norm_layer is None:
            # norm_layer = nn.BatchNorm2d
            norm_layer = comp.ComplexNaiveBatchNorm2d
        self._norm_layer = norm_layer

        self.inplanes = 64
        self.dilation = 1
        if replace_stride_with_dilation is None:
            # each element in the tuple indicates if we should replace
            # the 2x2 stride with a dilated convolution instead
            replace_stride_with_dilation = [False, False, False]
        if len(replace_stride_with_dilation) != 3:
            raise ValueError("replace_stride_with_dilation should be None "
                             "or a 3-element tuple, got {}".format(replace_stride_with_dilation))
        self.groups = groups
        self.base_width = width_per_group
        self.conv1 = comp.ComplexConv2d(3, self.inplanes, kernel_size=7, stride=2, padding=3)
        self.bn1 = norm_layer(self.inplanes)
        self.prelu = compact.CPReLU()
        # self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        self.maxpool = comp.ComplexMaxPool2d(kernel_size=3, stride=2, padding= 1)
        self.layer1 = self._make_layer(block, 64, layers[0])
        self.layer2 = self._make_layer(block, 128, layers[1], stride=2,
                                       dilate=replace_stride_with_dilation[0])
        self.layer3 = self._make_layer(block, 256, layers[2], stride=2,
                                       dilate=replace_stride_with_dilation[1])
        self.layer4 = self._make_layer(block, 512, layers[3], stride=2,
                                       dilate=replace_stride_with_dilation[2])
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.convert_float = ComplexToFloat()
        # self.fc = nn.Linear(2 * 512 * block.expansion, num_classes)
        self.fc = comp.ComplexConv2d(512 * block.expansion, num_classes, kernel_size= 1)

        # for m in self.modules():
            # if isinstance(m, nn.Conv2d):
                # nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            # elif isinstance(m, (nn.BatchNorm2d, nn.GroupNorm)):
                # nn.init.constant_(m.weight, 1)
                # nn.init.constant_(m.bias, 0)

        # Zero-initialize the last BN in each residual branch,
        # so that the residual branch starts with zeros, and each residual block behaves like an identity.
        # This improves the model by 0.2~0.3% according to https://arxiv.org/abs/1706.02677
        # if zero_init_residual:
            # for m in self.modules():
                # if isinstance(m, Bottleneck):
                    # nn.init.constant_(m.bn3.weight, 0)  # type: ignore[arg-type]
                # elif isinstance(m, BasicBlock):
                    # nn.init.constant_(m.bn2.weight, 0)  # type: ignore[arg-type]

    def _make_layer(self, block: Type[Union[BasicBlock, Bottleneck]], planes: int, blocks: int,
                    stride: int = 1, dilate: bool = False) -> nn.Sequential:
        norm_layer = self._norm_layer
        downsample = None
        previous_dilation = self.dilation
        if dilate:
            self.dilation *= stride
            stride = 1
        if stride != 1 or self.inplanes != planes * block.expansion:
            downsample = nn.Sequential(
                conv1x1(self.inplanes, planes * block.expansion, stride),
                norm_layer(planes * block.expansion),
            )

        layers = []
        layers.append(block(self.inplanes, planes, stride, downsample, self.groups,
                            self.base_width, previous_dilation, norm_layer))
        self.inplanes = planes * block.expansion
        for _ in range(1, blocks):
            layers.append(block(self.inplanes, planes, groups=self.groups,
                                base_width=self.base_width, dilation=self.dilation,
                                norm_layer=norm_layer))

        return nn.Sequential(*layers)

    def _forward_impl(self, x: Tensor) -> Tensor:
        # See note [TorchScript super()]
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.prelu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = self.avgpool(x)
        # x = self.convert_float(x)
        # x = torch.flatten(x, 1)
        x = self.fc(x)

        return x

    def forward(self, x: Tensor) -> Tensor:
        return self._forward_impl(x)


def _resnet(
    arch: str,
    block: Type[Union[BasicBlock, Bottleneck]],
    layers: List[int],
    pretrained: bool,
    progress: bool,
    **kwargs: Any
) -> ResNet:
    model = ResNet(block, layers, **kwargs)
    if pretrained:
        pass
        # state_dict = load_state_dict_from_url(model_urls[arch],
                                              # progress=progress)
        # model.load_state_dict(state_dict)
    return model


def resnet18(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> ResNet:
    r"""ResNet-18 model from
    `"Deep Residual Learning for Image Recognition" <https://arxiv.org/pdf/1512.03385.pdf>`_.
    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
        progress (bool): If True, displays a progress bar of the download to stderr
    """
    return _resnet('resnet18', BasicBlock, [2, 2, 2, 2], pretrained, progress,
                   **kwargs)


def resnet34(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> ResNet:
    r"""ResNet-34 model from
    `"Deep Residual Learning for Image Recognition" <https://arxiv.org/pdf/1512.03385.pdf>`_.
    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
        progress (bool): If True, displays a progress bar of the download to stderr
    """
    return _resnet('resnet34', BasicBlock, [3, 4, 6, 3], pretrained, progress,
                   **kwargs)


def resnet50(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> ResNet:
    r"""ResNet-50 model from
    `"Deep Residual Learning for Image Recognition" <https://arxiv.org/pdf/1512.03385.pdf>`_.
    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
        progress (bool): If True, displays a progress bar of the download to stderr
    """
    return _resnet('resnet50', Bottleneck, [3, 4, 6, 3], pretrained, progress,
                   **kwargs)


def resnet101(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> ResNet:
    r"""ResNet-101 model from
    `"Deep Residual Learning for Image Recognition" <https://arxiv.org/pdf/1512.03385.pdf>`_.
    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
        progress (bool): If True, displays a progress bar of the download to stderr
    """
    return _resnet('resnet101', Bottleneck, [3, 4, 23, 3], pretrained, progress,
                   **kwargs)


def resnet152(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> ResNet:
    r"""ResNet-152 model from
    `"Deep Residual Learning for Image Recognition" <https://arxiv.org/pdf/1512.03385.pdf>`_.
    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
        progress (bool): If True, displays a progress bar of the download to stderr
    """
    return _resnet('resnet152', Bottleneck, [3, 8, 36, 3], pretrained, progress,
                   **kwargs)


def resnext50_32x4d(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> ResNet:
    r"""ResNeXt-50 32x4d model from
    `"Aggregated Residual Transformation for Deep Neural Networks" <https://arxiv.org/pdf/1611.05431.pdf>`_.
    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
        progress (bool): If True, displays a progress bar of the download to stderr
    """
    kwargs['groups'] = 32
    kwargs['width_per_group'] = 4
    return _resnet('resnext50_32x4d', Bottleneck, [3, 4, 6, 3],
                   pretrained, progress, **kwargs)


def resnext101_32x8d(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> ResNet:
    r"""ResNeXt-101 32x8d model from
    `"Aggregated Residual Transformation for Deep Neural Networks" <https://arxiv.org/pdf/1611.05431.pdf>`_.
    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
        progress (bool): If True, displays a progress bar of the download to stderr
    """
    kwargs['groups'] = 32
    kwargs['width_per_group'] = 8
    return _resnet('resnext101_32x8d', Bottleneck, [3, 4, 23, 3],
                   pretrained, progress, **kwargs)


def wide_resnet50_2(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> ResNet:
    r"""Wide ResNet-50-2 model from
    `"Wide Residual Networks" <https://arxiv.org/pdf/1605.07146.pdf>`_.
    The model is the same as ResNet except for the bottleneck number of channels
    which is twice larger in every block. The number of channels in outer 1x1
    convolutions is the same, e.g. last block in ResNet-50 has 2048-512-2048
    channels, and in Wide ResNet-50-2 has 2048-1024-2048.
    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
        progress (bool): If True, displays a progress bar of the download to stderr
    """
    kwargs['width_per_group'] = 64 * 2
    return _resnet('wide_resnet50_2', Bottleneck, [3, 4, 6, 3],
                   pretrained, progress, **kwargs)


def wide_resnet101_2(pretrained: bool = False, progress: bool = True, **kwargs: Any) -> ResNet:
    r"""Wide ResNet-101-2 model from
    `"Wide Residual Networks" <https://arxiv.org/pdf/1605.07146.pdf>`_.
    The model is the same as ResNet except for the bottleneck number of channels
    which is twice larger in every block. The number of channels in outer 1x1
    convolutions is the same, e.g. last block in ResNet-50 has 2048-512-2048
    channels, and in Wide ResNet-50-2 has 2048-1024-2048.
    Args:
        pretrained (bool): If True, returns a model pre-trained on ImageNet
        progress (bool): If True, displays a progress bar of the download to stderr
    """
    kwargs['width_per_group'] = 64 * 2
    return _resnet('wide_resnet101_2', Bottleneck, [3, 4, 23, 3],
                   pretrained, progress, **kwargs)
