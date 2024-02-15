"""
Dropout layer for regularizing the machine learning model.
"""

__author__ = 'Dylan Warnecke'

__version__ = '1.0'

import numpy as np
from layers.layer import Layer


class Dropout(Layer):
    def __init__(self, rate: float):
        """
        Create a dropout layer that regularizes models by zeroing random
        units at a certain rate. These are especially useful in between
        dense layers of computer vision models.
        :param rate: The rate at which units are dropped out at
        """

        super().__init__(False)  # Call the super class initializer

        # Check and define the dropout rate
        if not 0 < rate < 1:
            raise ValueError("Dropout rate must be between 0 and 1.")
        self._RATE = rate

        self.units = None  # Define the layer units constant

        # Define the dropout filter retainer and random generator
        self._generator = np.random.default_rng()
        self._dropout_filter = None

    def compile(self, layer_idx: int, input_units: int):
        """
        Initialize the number of units this layer produces to connect the
        model together and prepare the layer for use.
        :param layer_idx: The layer number in the larger network
        :param input_units: The number of units leading into this layer
        """

        # Check and that layer index and input units are positive integers
        if layer_idx < 1:
            raise ValueError("Layer index must be greater than zero.")
        elif input_units < 1:
            raise ValueError("Input units must be greater than zero.")
        self.units = input_units

        # Set the network identification key
        self._network_id = 'Dropout' + str(layer_idx)

        self._is_compiled = True  # Change the compilation flag

    def forward(
            self,
            layer_inputs: np.ndarray,
            in_training: bool) -> np.ndarray:
        """
        Pass through this dropout layer in forward propagation. If the
        model is in training, certain units will be dropped out and the others
        will be adequately scaled. If not, the inputs are simply returned
        as the outputs.
        :param layer_inputs: The inputs to be possibly zeroed out.
        :param in_training: If the model is currently training
        :return: The layer inputs after dropping units.
        """

        # Check that the number of units is defined
        if not self._is_compiled:
            raise AttributeError("Number of units must be defined.")

        # Check that the inputs match the number of units
        if layer_inputs.shape[-1] != self.units:
            raise ValueError("Number of input units must be consistent.")

        # Filter certain input units with dropout
        if in_training:
            filter_values = self._generator.random(size=layer_inputs.shape)
            dropout_filter = filter_values > self._RATE
            filtered_inputs = np.where(dropout_filter, layer_inputs, 0)
            layer_outputs = filtered_inputs / (1 - self._RATE)

            # Cache the filter for later use
            self._dropout_filter = dropout_filter
        else:
            layer_outputs = layer_inputs

        return layer_outputs  # Return the possibly dropped outputs

    def backward(self, output_grads):
        """
        Pass through this layer in backpropagation. Gradients only will
        propagate if their respective input counterparts managed to pass the
        dropout filter.
        :param output_grads: The loss gradients respecting the outputs
        :return: The loss gradients respecting the layer inputs
        """

        # Check that the number of units is defined
        if not self._is_compiled:
            raise AttributeError("Number of units must be defined.")

        # Check that the inputs match the number of units
        if output_grads.shape[1] != self.units:
            raise ValueError("Number of input units must be consistent.")

        # Calculate the loss gradients respecting the inputs
        rescaled_grads = output_grads / (1 - self._RATE)
        input_grads = np.where(
            self._dropout_filter,
            rescaled_grads, 0)

        return input_grads  # Return the layer input gradients
