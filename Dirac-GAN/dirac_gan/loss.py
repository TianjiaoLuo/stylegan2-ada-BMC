from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F

from dirac_gan.config import HYPERPARAMETERS


class GANLossGenerator(nn.Module):
    """
    This class implements the standard generator GAN loss proposed in:
    https://papers.nips.cc/paper/2014/file/5ca3e9b122f61f8f06494c97b1afccf3-Paper.pdf
    """

    def __init__(self) -> None:
        """
        Constructor method.
        """
        # Call super constructor
        super(GANLossGenerator, self).__init__()

    def forward(self, discriminator_prediction_fake: torch.Tensor, **kwargs) -> torch.Tensor:
        """
        Forward pass.
        :param discriminator_prediction_fake: (torch.Tensor) Raw discriminator predictions for fake samples
        :return: (torch.Tensor) Standard generator GAN loss
        """
        # Loss can be computed by utilizing the softplus function since softplus combines both sigmoid and log
        return - F.softplus(discriminator_prediction_fake).mean()


class GANLossDiscriminator(nn.Module):
    """
    This class implements the standard discriminator GAN loss proposed in:
    https://papers.nips.cc/paper/2014/file/5ca3e9b122f61f8f06494c97b1afccf3-Paper.pdf
    """

    def __init__(self) -> None:
        """
        Constructor method.
        """
        # Call super constructor
        super(GANLossDiscriminator, self).__init__()

    def forward(self, discriminator_prediction_real: torch.Tensor,
                discriminator_prediction_fake: torch.Tensor, **kwargs) -> torch.Tensor:
        """
        Forward pass.
        :param discriminator_prediction_real: (torch.Tensor) Raw discriminator prediction for real samples
        :param discriminator_prediction_fake: (torch.Tensor) Raw discriminator predictions for fake samples
        :return: (torch.Tensor) Standard discriminator GAN loss
        """
        # Loss can be computed by utilizing the softplus function since softplus combines both sigmoid and log
        return F.softplus(- discriminator_prediction_real).mean() \
               + F.softplus(discriminator_prediction_fake).mean()


class NSGANLossGenerator(nn.Module):
    """
    This class implements the non-saturating generator GAN loss proposed in:
    https://papers.nips.cc/paper/2014/file/5ca3e9b122f61f8f06494c97b1afccf3-Paper.pdf
    """

    def __init__(self) -> None:
        """
        Constructor method.
        """
        # Call super constructor
        super(NSGANLossGenerator, self).__init__()

    def forward(self, discriminator_prediction_fake: torch.Tensor, **kwargs) -> torch.Tensor:
        """
        Forward pass.
        :param discriminator_prediction_fake: (torch.Tensor) Raw discriminator predictions for fake samples
        :return: (torch.Tensor) Non-saturating generator GAN loss
        """
        # Loss can be computed by utilizing the softplus function since softplus combines both sigmoid and log
        return F.softplus(- discriminator_prediction_fake).mean()


class NSGANLossDiscriminator(GANLossDiscriminator):
    """
    This class implements the non-saturating discriminator GAN loss proposed in:
    https://papers.nips.cc/paper/2014/file/5ca3e9b122f61f8f06494c97b1afccf3-Paper.pdf
    """

    def __init__(self) -> None:
        """
        Constructor method.
        """
        # Call super constructor
        super(NSGANLossDiscriminator, self).__init__()


class WassersteinGANLossGenerator(nn.Module):
    """
    This class implements the Wasserstein generator GAN loss proposed in:
    http://proceedings.mlr.press/v70/arjovsky17a/arjovsky17a.pdf
    """

    def __index__(self) -> None:
        """
        Constructor method.
        """
        # Call super constructor
        super(WassersteinGANLossGenerator, self).__index__()

    def forward(self, discriminator_prediction_fake: torch.Tensor, **kwargs) -> torch.Tensor:
        """
        Forward pass.
        :param discriminator_prediction_fake: (torch.Tensor) Raw discriminator predictions for fake samples
        :return: (torch.Tensor) Wasserstein Generator GAN loss with gradient
        """
        return - discriminator_prediction_fake.mean()


class WassersteinGANLossDiscriminator(nn.Module):
    """
    This class implements the Wasserstein generator GAN loss proposed in:
    http://proceedings.mlr.press/v70/arjovsky17a/arjovsky17a.pdf
    """

    def __init__(self) -> None:
        """
        Constructor method.
        """
        # Call super constructor
        super(WassersteinGANLossDiscriminator, self).__init__()

    def forward(self, discriminator_prediction_real: torch.Tensor,
                discriminator_prediction_fake: torch.Tensor, **kwargs) -> torch.Tensor:
        """
        Forward pass.
        :param discriminator_prediction_real: (torch.Tensor) Raw discriminator prediction for real samples
        :param discriminator_prediction_fake: (torch.Tensor) Raw discriminator predictions for fake samples
        :return: (torch.Tensor) Wasserstein generator GAN loss with gradient penalty
        """
        return - discriminator_prediction_real.mean() \
               + discriminator_prediction_fake.mean()


class WassersteinGANLossGPGenerator(WassersteinGANLossGenerator):
    """
    This class implements the Wasserstein generator GAN loss proposed in:
    https://proceedings.neurips.cc/paper/2017/file/892c3b1c6dccd52936e27cbd0ff683d6-Paper.pdf
    """

    def __index__(self) -> None:
        """
        Constructor method.
        """
        # Call super constructor
        super(WassersteinGANLossGPGenerator, self).__index__()


class WassersteinGANLossGPDiscriminator(nn.Module):
    """
    This class implements the Wasserstein generator GAN loss proposed in:
    https://proceedings.neurips.cc/paper/2017/file/892c3b1c6dccd52936e27cbd0ff683d6-Paper.pdf
    """

    def __init__(self) -> None:
        """
        Constructor method.
        """
        # Call super constructor
        super(WassersteinGANLossGPDiscriminator, self).__init__()

    def forward(self, discriminator_prediction_real: torch.Tensor,
                discriminator_prediction_fake: torch.Tensor,
                discriminator: nn.Module,
                real_samples: torch.Tensor,
                fake_samples: torch.Tensor,
                **kwargs) -> torch.Tensor:
        """
        Forward pass.
        :param discriminator_prediction_real: (torch.Tensor) Raw discriminator prediction for real samples
        :param discriminator_prediction_fake: (torch.Tensor) Raw discriminator predictions for fake samples
        :param discriminator: (nn.Module) Discriminator network
        :param real_samples: (torch.Tensor) Real samples
        :param fake_samples: (torch.Tensor) Fake samples
        :return: (torch.Tensor) Wasserstein discriminator GAN loss with gradient penalty
        """
        # Generate random alpha for interpolation
        alpha: torch.Tensor = torch.rand((real_samples.shape[0], 1), device=real_samples.device)
        # Make interpolated samples
        samples_interpolated: torch.Tensor = (alpha * real_samples + (1. - alpha) * fake_samples)
        samples_interpolated.requires_grad = True
        # Make discriminator prediction
        discriminator_prediction_interpolated: torch.Tensor = discriminator(samples_interpolated)
        # Calc gradients
        gradients: torch.Tensor = torch.autograd.grad(outputs=discriminator_prediction_interpolated.sum(),
                                                      inputs=samples_interpolated,
                                                      create_graph=True,
                                                      retain_graph=True)[0]
        # Calc gradient penalty
        gradient_penalty: torch.Tensor = (gradients.view(gradients.shape[0], -1).norm(dim=1) - 1.).pow(2).mean()
        return - discriminator_prediction_real.mean() \
               + discriminator_prediction_fake.mean() \
               + HYPERPARAMETERS["gp_w"] * gradient_penalty


class LSGANLossGenerator(nn.Module):
    """
    This class implements the least squares generator GAN loss proposed in:
    https://openaccess.thecvf.com/content_ICCV_2017/papers/Mao_Least_Squares_Generative_ICCV_2017_paper.pdf
    """

    def __init__(self) -> None:
        """
        Constructor method.
        """
        # Call super constructor
        super(LSGANLossGenerator, self).__init__()

    def forward(self, discriminator_prediction_fake: torch.Tensor, **kwargs) -> torch.Tensor:
        """
        Forward pass.
        :param discriminator_prediction_fake: (torch.Tensor) Raw discriminator predictions for fake samples
        :return: (torch.Tensor) Generator LSGAN loss
        """
        return - 0.5 * (discriminator_prediction_fake - 1.).pow(2).mean()


class LSGANLossDiscriminator(nn.Module):
    """
    This class implements the least squares discriminator GAN loss proposed in:
    https://openaccess.thecvf.com/content_ICCV_2017/papers/Mao_Least_Squares_Generative_ICCV_2017_paper.pdf
    """

    def __init__(self) -> None:
        """
        Constructor method.
        """
        # Call super constructor
        super(LSGANLossDiscriminator, self).__init__()

    def forward(self, discriminator_prediction_real: torch.Tensor,
                discriminator_prediction_fake: torch.Tensor, **kwargs) -> torch.Tensor:
        """
        Forward pass.
        :param discriminator_prediction_real: (torch.Tensor) Raw discriminator prediction for real samples
        :param discriminator_prediction_fake: (torch.Tensor) Raw discriminator predictions for fake samples
        :return: (torch.Tensor) Discriminator LSGAN loss
        """
        return 0.5 * ((- discriminator_prediction_real - 1.).pow(2).mean()
                      + discriminator_prediction_fake.pow(2).mean())


class HingeGANLossGenerator(WassersteinGANLossGenerator):
    """
    This class implements the Hinge generator GAN loss proposed in:
    https://arxiv.org/pdf/1705.02894.pdf
    """

    def __init__(self) -> None:
        """
        Constructor method.
        """
        # Call super constructor
        super(HingeGANLossGenerator, self).__init__()


class HingeGANLossDiscriminator(nn.Module):
    """
    This class implements the Hinge discriminator GAN loss proposed in:
    https://arxiv.org/pdf/1705.02894.pdf
    """

    def __init__(self) -> None:
        """
        Constructor method.
        """
        # Call super constructor
        super(HingeGANLossDiscriminator, self).__init__()

    def forward(self, discriminator_prediction_real: torch.Tensor,
                discriminator_prediction_fake: torch.Tensor, **kwargs) -> torch.Tensor:
        """
        Forward pass.
        :param discriminator_prediction_real: (torch.Tensor) Raw discriminator prediction for real samples
        :param discriminator_prediction_fake: (torch.Tensor) Raw discriminator predictions for fake samples
        :return: (torch.Tensor) Hinge discriminator GAN loss
        """
        return - torch.minimum(torch.tensor(0., dtype=torch.float, device=discriminator_prediction_real.device),
                               discriminator_prediction_real - 1.).mean() \
               - torch.minimum(torch.tensor(0., dtype=torch.float, device=discriminator_prediction_fake.device),
                               - discriminator_prediction_fake - 1.).mean()


class R1(nn.Module):
    """
    Implementation of the R1 GAN regularization.
    """

    def __init__(self):
        """
        Constructor method
        """
        # Call super constructor
        super(R1, self).__init__()

    def forward(self, prediction_real: torch.Tensor, real_sample: torch.Tensor) -> torch.Tensor:
        """
        Forward pass to compute the regularization
        :param prediction_real: (torch.Tensor) Prediction of the discriminator for a batch of real images
        :param real_sample: (torch.Tensor) Batch of the corresponding real images
        :return: (torch.Tensor) Loss value
        """
        # Calc gradient
        grad_real = torch.autograd.grad(outputs=prediction_real.sum(), inputs=real_sample, create_graph=True)[0]
        # Calc regularization
        regularization_loss: torch.Tensor = HYPERPARAMETERS["r1_w"] \
                                            * grad_real.pow(2).view(grad_real.shape[0], -1).sum(1).mean()
        return regularization_loss


class R2(nn.Module):
    """
    Implementation of the R2 GAN regularization.
    """

    def __init__(self):
        """
        Constructor method
        """
        # Call super constructor
        super(R2, self).__init__()

    def forward(self, prediction_fake: torch.Tensor, fake_sample: torch.Tensor) -> torch.Tensor:
        """
        Forward pass to compute the regularization
        :param prediction_real: (torch.Tensor) Prediction of the discriminator for a batch of real images
        :param fake_sample: (torch.Tensor) Batch of the corresponding real images
        :return: (torch.Tensor) Loss value
        """
        # Calc gradient
        grad_fake = torch.autograd.grad(outputs=prediction_fake.sum(), inputs=fake_sample, create_graph=True)[0]
        # Calc regularization
        regularization_loss: torch.Tensor = HYPERPARAMETERS["r2_w"] \
                                            * grad_fake.pow(2).view(grad_fake.shape[0], -1).sum(1).mean()
        return regularization_loss


class RLC(nn.Module):
    """
    Implementation of the RLC GAN regularization proposed in:
    https://arxiv.org/pdf/2104.03310.pdf
    """

    def __init__(self):
        """
        Constructor method
        """
        # Call super constructor
        super(RLC, self).__init__()

    def forward(self, discriminator_prediction_real: torch.Tensor,
                discriminator_prediction_fake: torch.Tensor) -> torch.Tensor:
        """
        Forward pass to compute the regularization
        :param discriminator_prediction_real: (torch.Tensor) Real prediction of the discriminator
        :param discriminator_prediction_fake: (torch.Tensor) Fake prediction of the discriminator
        """
        regularization_loss = (discriminator_prediction_real - HYPERPARAMETERS["rlc_af"]).norm(dim=-1).pow(2).mean() \
                              + (discriminator_prediction_fake - HYPERPARAMETERS["rlc_ar"]).norm(dim=-1).pow(2).mean()
        return HYPERPARAMETERS["rlc_w"] * regularization_loss


class DRAGANLossGenerator(GANLossGenerator):
    """
    This class implements the generator loss proposed in:
    https://arxiv.org/pdf/1705.07215.pdf
    """

    def __init__(self) -> None:
        """
        Constructor method
        """
        # Call super constructor
        super(DRAGANLossGenerator, self).__init__()


class DRAGANLossDiscriminator(nn.Module):
    """
    This class implements the generator loss proposed in:
    https://arxiv.org/pdf/1705.07215.pdf
    """

    def __init__(self) -> None:
        """
        Constructor method
        """
        # Call super constructor
        super(DRAGANLossDiscriminator, self).__init__()

    def forward(self, discriminator_prediction_real: torch.Tensor,
                discriminator_prediction_fake: torch.Tensor, real_samples: torch.Tensor, discriminator: nn.Module,
                **kwargs) -> torch.Tensor:
        """
        Forward pass.
        :param discriminator_prediction_real: (torch.Tensor) Raw discriminator prediction for real samples
        :param discriminator_prediction_fake: (torch.Tensor) Raw discriminator predictions for fake samples
        :return: (torch.Tensor) Hinge discriminator GAN loss
        """
        # Loss can be computed by utilizing the softplus function since softplus combines both sigmoid and log
        loss = F.softplus(- discriminator_prediction_real).mean() \
               + F.softplus(discriminator_prediction_fake).mean()
        # Compute regularization loss
        real_prediction = discriminator(real_samples + torch.randn_like(real_samples) * 0.1)
        grad_real = torch.autograd.grad(outputs=real_prediction.sum(), inputs=real_samples, create_graph=True)[0]
        loss = loss + HYPERPARAMETERS["dra_w"] * (grad_real.norm(dim=1) - 1.).pow(2)
        return loss
