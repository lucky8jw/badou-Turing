#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
@Project ：badou-Turing 
@File    ：BCELoss.py
@Author  ：luigi
@Date    ：2021/9/2 10:55 上午 
'''
import numpy as np


class BCELoss():

    def __init__(self):
        pass

    def __call__(self, y_pred, y_true):
        return self.forward(y_pred, y_true)

    def forward(self, y_pred, y):
        eps = np.finfo(float).eps
        y_pred = np.clip(y_pred, eps, 1 - eps)

        loss = -np.sum(y * np.log(y_pred) + (1 - y) * (np.log(1 - y_pred)))
        return loss

    def grad(self, y_pred, y):
        if y == 1:
            -1 / y_pred
        else:
            1 / (1 - y_pred)
