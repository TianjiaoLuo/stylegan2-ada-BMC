import matplotlib.pyplot as plt
import torch
import torch.nn as nn

from dirac_gan import *

loss_list = [#(GANLossGenerator, GANLossDiscriminator, "standard_gan"),
              #     (NSGANLossGenerator, NSGANLossDiscriminator, "non_saturating_gan"),
                    #(WassersteinGANLossGenerator, WassersteinGANLossDiscriminator, "wasserstein_gan"),
                    # (WassersteinGANLossGenerator, WassersteinGANLossDiscriminator, "brownian_gan"),
                   (WassersteinGANLossGPGenerator, WassersteinGANLossGPDiscriminator, "wasserstein_gp_gan"),
                   #(LSGANLossGenerator, LSGANLossDiscriminator, "ls_gan"),
                   #(HingeGANLossGenerator, HingeGANLossDiscriminator, "hinge_gan"),
                   #(DRAGANLossGenerator, DRAGANLossDiscriminator, "dra_gan")
                   ]

if __name__ == '__main__':
    for losses in loss_list:
        # Get name
        name = losses[-1]
        # Init loss functions
        generator_loss = losses[0]()
        discriminator_loss = losses[1]()
        # Init generator and discriminator
        generator = Generator()
        discriminator = Discriminator()
        # Init optimizers
        generator_optimizer: torch.optim.Optimizer = torch.optim.SGD(params=generator.parameters(),
                                                                     lr=HYPERPARAMETERS["lr"],
                                                                     momentum=0.)
        discriminator_optimizer: torch.optim.Optimizer = torch.optim.SGD(params=discriminator.parameters(),
                                                                         lr=HYPERPARAMETERS["lr"],
                                                                         momentum=0.)
        # Make model wrapper
        model_wrapper = ModelWrapper(generator=generator,
                                     discriminator=discriminator,
                                     generator_optimizer=generator_optimizer,
                                     discriminator_optimizer=discriminator_optimizer,
                                     generator_loss_function=generator_loss,
                                     discriminator_loss_function=discriminator_loss,
                                     regularization_loss=None,
                                     use_brown_motion=True)
        # Get trajectory
        parameters, gradients = model_wrapper.generate_trajectory(instance_noise=False)
        # Perform training
        parameter_history: torch.Tensor = model_wrapper.train(instance_noise=False)
        # Plot results
        plt.figure()
        #plt.subplot(121)
        plt.plot(range(0, parameter_history.shape[0]), parameter_history[..., 0])
        plt.savefig(f"my-images/{name}-grad.png", dpi=300, bbox_inches='tight', pad_inches=0)
        plt.savefig(f"my-images/{name}-grad.pdf", dpi=300, bbox_inches='tight', pad_inches=0)
        #plt.subplot(122)
        plt.figure()
        plt.grid()
        plt.xlim((-2.1, 2.1))
        plt.ylim((-2.1, 2.1))
        plt.quiver(parameters[..., 0], parameters[..., 1], -gradients[..., 0], -gradients[..., 1])
        plt.scatter(parameter_history[..., 0], parameter_history[..., 1])
        plt.scatter([1.], [1.], color="red")
        plt.xlabel("$\\theta$")
        plt.ylabel("$\\psi$")



        plt.savefig(f"my-images/{name}-conv.png", dpi=300, bbox_inches='tight', pad_inches=0)
        plt.savefig(f"my-images/{name}-conv.pdf", dpi=300, bbox_inches='tight', pad_inches=0)
        plt.close()
