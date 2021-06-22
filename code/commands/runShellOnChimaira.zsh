#!/bin/zsh
srun --exclusive --gres=gpu --constraint=chimaira --pass-tgt=on --export=INFOSUN_TICKET --mem=22000 --pty /bin/bash
