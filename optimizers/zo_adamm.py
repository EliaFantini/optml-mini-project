import torch
from torch.optim import Optimizer


class ZO_AdaMM(Optimizer):

    def __init__(self, params, lr=1e-03, betas=(0.9, 0.999), mu=1e-05, eps=1e-12):
        if lr < 0.0:
            raise ValueError("Invalid learning rate: (} - should be >= 0.0".format(lr))
        if not 0.0 <= betas[0] < 1.0:
            raise ValueError("Invalid beta parameter: (} - should be in [0.0, 1.0[".format(betas[0]))
        if not 0.0 <= betas[1] < 1.0:
            raise ValueError("Invalid beta parameter: {} - should be in [0.0, 1.0l".format(betas[1]))
        if not 0.0 <= mu < 1.0:
            raise ValueError("Invalid mu parameter: {} - should be in [0.0, 1.0l".format(mu))

        defaults = dict(lr=lr, betas=betas, mu=mu, eps=eps)
        super(ZO_AdaMM, self).__init__(params, defaults)

    def step(self, closure):

        for group in self.param_groups:
            beta1, beta2 = group['betas']

            size_params = 0

            for p in group['params']:
                size_params += p.view(-1).size()[0]

            # closure return the approximation for the gradient, we have to add some "option" to this function
            grad_est = closure(size_params, group["mu"])

            for i, p in enumerate(group['params']):
                state = self.state[p]

                # Lazy state initialization
                if len(state) == 0:
                    # Exponential moving average of gradient values
                    state['exp_avg'] = torch.zeros_like(p, memory_format=torch.preserve_format)

                    # Exponential moving average of squared gradient values
                    state['exp_avg_sq'] = torch.zeros_like(p, memory_format=torch.preserve_format)

                    # Maintains max of all exp. moving avg. of sq. grad. values
                    state['max_exp_avg_sq'] = torch.zeros_like(p, memory_format=torch.preserve_format)

                state['exp_avg'].mul_(beta1).add_(grad_est[i], alpha=(1.0 - beta1))
                state['exp_avg_sq'].mul_(beta2).addcmul_(grad_est[i], grad_est[i], value=(1.0 - beta2))
                state['max_exp_avg_sq'] = torch.maximum(state['max_exp_avg_sq'],
                                                        state['exp_avg_sq'])

                p.data.addcdiv_(state['exp_avg'], state['exp_avg_sq'].sqrt().add_(group['eps']), value=(-group['lr']))

