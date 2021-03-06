"""Float class.

Represents an unbounded float using a widget.
"""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from .domwidget import DOMWidget
from .widget import register
from .trait_types import Color
from traitlets import (Unicode, CFloat, Bool, CaselessStrEnum,
                       Tuple, TraitError, validate)


class _Float(DOMWidget):
    value = CFloat(0.0, help="Float value").tag(sync=True)
    disabled = Bool(False, help="Enable or disable user changes").tag(sync=True)
    description = Unicode(help="Description of the value this widget represents").tag(sync=True)

    def __init__(self, value=None, **kwargs):
        if value is not None:
            kwargs['value'] = value
        super(_Float, self).__init__(**kwargs)


class _BoundedFloat(_Float):
    max = CFloat(100.0, help="Max value").tag(sync=True)
    min = CFloat(0.0, help="Min value").tag(sync=True)
    step = CFloat(0.1, help="Minimum step to increment the value (ignored by some views)").tag(sync=True)

    @validate('value')
    def _validate_value(self, proposal):
        """Cap and floor value"""
        value = proposal['value']
        if self.min > value or self.max < value:
            value = min(max(value, self.min), self.max)
        return value

    @validate('min')
    def _validate_min(self, proposal):
        """Enforce min <= value <= max"""
        min = proposal['value']
        if min > self.max:
            raise TraitError('Setting min > max')
        if min > self.value:
            self.value = min
        return min

    @validate('max')
    def _validate_max(self, proposal):
        """Enforce min <= value <= max"""
        max = proposal['value']
        if max < self.min:
            raise TraitError('setting max < min')
        if max < self.value:
            self.value = max
        return max


@register('Jupyter.FloatText')
class FloatText(_Float):
    """ Displays a float value within a textbox. For a textbox in
	which the value must be within a specific range, use BoundedFloatText.

	Parameters
	----------
	value : float
	    value displayed
	description : str
	    description displayed next to the text box
	color : str Unicode color code (eg. '#C13535'), optional
	    color of the value displayed
    """
    _view_name = Unicode('FloatTextView').tag(sync=True)
    _model_name = Unicode('IntTextModel').tag(sync=True)


@register('Jupyter.BoundedFloatText')
class BoundedFloatText(_BoundedFloat):
    """ Displays a float value within a textbox. Value must be within the range specified.
	For a textbox in which the value doesn't need to be within a specific range, use FloatText.

	Parameters
	----------
	value : float
	    value displayed
	min : float
	    minimal value of the range of possible values displayed
	max : float
	    maximal value of the range of possible values displayed
	description : str
	    description displayed next to the textbox
	color : str Unicode color code (eg. '#C13535'), optional
	    color of the value displayed
    """
    _view_name = Unicode('FloatTextView').tag(sync=True)
    _model_name = Unicode('IntTextModel').tag(sync=True)


@register('Jupyter.FloatSlider')
class FloatSlider(_BoundedFloat):
    """ Slider/trackbar of floating values with the specified range.

	Parameters
	----------
	value : float
	    position of the slider
	min : float
	    minimal position of the slider
	max : float
	    maximal position of the slider
	step : float
	    step of the trackbar
	description : str
	    name of the slider
	orientation : {'vertical', 'horizontal}, optional
        default is horizontal
	readout : {True, False}, optional
	    default is True, display the current value of the slider next to it
	slider_color : str Unicode color code (eg. '#C13535'), optional
	    color of the slider
	color : str Unicode color code (eg. '#C13535'), optional
	    color of the value displayed (if readout == True)
    """
    _view_name = Unicode('FloatSliderView').tag(sync=True)
    _model_name = Unicode('IntSliderModel').tag(sync=True)
    orientation = CaselessStrEnum(values=['horizontal', 'vertical'],
        default_value='horizontal', help="Vertical or horizontal.").tag(sync=True)
    _range = Bool(False, help="Display a range selector").tag(sync=True)
    readout = Bool(True, help="Display the current value of the slider next to it.").tag(sync=True)
    slider_color = Color(None, allow_none=True).tag(sync=True)
    continuous_update = Bool(True, help="Update the value of the widget as the user is sliding the slider.").tag(sync=True)


@register('Jupyter.FloatProgress')
class FloatProgress(_BoundedFloat):
    """ Displays a progress bar.

    Parameters
    -----------
    value : float
	    position within the range of the progress bar
    min : float
	    minimal position of the slider
    max : float
	    maximal position of the slider
    step : float
	    step of the progress bar
    description : str
	    name of the progress bar
    bar_style: {'success', 'info', 'warning', 'danger', ''}, optional
	    color of the progress bar, default is '' (blue)
	    colors are: 'success'-green, 'info'-light blue, 'warning'-orange, 'danger'-red
    """
    _view_name = Unicode('ProgressView').tag(sync=True)
    _model_name = Unicode('ProgressModel').tag(sync=True)
    orientation = CaselessStrEnum(values=['horizontal', 'vertical'],
        default_value='horizontal', help="Vertical or horizontal.").tag(sync=True)

    bar_style = CaselessStrEnum(
        values=['success', 'info', 'warning', 'danger', ''],
        default_value='', allow_none=True, help="""Use a predefined styling for
        the progess bar.""").tag(sync=True)


class _FloatRange(_Float):
    value = Tuple(CFloat(), CFloat(), default_value=(0.0, 1.0),
                  help="Tuple of (lower, upper) bounds").tag(sync=True)

    @property
    def lower(self):
        return self.value[0]

    @lower.setter
    def lower(self, lower):
        self.value = (lower, self.value[1])

    @property
    def upper(self):
        return self.value[1]

    @upper.setter
    def upper(self, upper):
        self.value = (self.value[0], upper)

    @validate('value')
    def _validate_value(self, proposal):
        lower, upper = proposal['value']
        if upper < lower:
            raise TraitError('setting lower > upper')
        return lower, upper


class _BoundedFloatRange(_FloatRange):
    step = CFloat(1.0, help="Minimum step that the value can take (ignored by some views)").tag(sync=True)
    max = CFloat(100.0, help="Max value").tag(sync=True)
    min = CFloat(0.0, help="Min value").tag(sync=True)

    def __init__(self, *args, **kwargs):
        min, max = kwargs.get('min', 0.0), kwargs.get('max', 100.0)
        if not kwargs.get('value', None):
            kwargs['value'] = (0.75 * min + 0.25 * max,
                               0.25 * min + 0.75 * max)
        super(_BoundedFloatRange, self).__init__(*args, **kwargs)

    @validate('min', 'max')
    def _validate_bounds(self, proposal):
        trait = proposal['trait']
        new = proposal['value']
        if trait.name == 'min' and new > self.lower:
            raise TraitError('setting min > lower')
        if trait.name == 'max' and new < self.upper:
            raise TraitError('setting max < upper')
        return new

    @validate('value')
    def _validate_value(self, proposal):
        lower, upper = super(_BoundedFloatRange, self)._validate_value(proposal)
        if lower < self.min:
            raise TraitError('setting lower < min')
        if upper > self.max:
            raise TraitError('setting upper > max')
        return lower, upper


@register('Jupyter.FloatRangeSlider')
class FloatRangeSlider(_BoundedFloatRange):
    """ Slider/trackbar that represents a pair of floats bounded by minimum and maximum value.

	Parameters
	----------
	value : float tuple
	    range of the slider displayed
	min : float
	    minimal position of the slider
	max : float
	    maximal position of the slider
	step : float
	    step of the trackbar
	description : str
	    name of the slider
	orientation : {'vertical', 'horizontal}, optional
            default is horizontal
	readout : {True, False}, optional
	    default is True, display the current value of the slider next to it
	slider_color : str Unicode color code (eg. '#C13535'), optional
	    color of the slider
	color : str Unicode color code (eg. '#C13535'), optional
	    color of the value displayed (if readout == True)
    """
    _view_name = Unicode('FloatSliderView').tag(sync=True)
    _model_name = Unicode('IntSliderModel').tag(sync=True)
    orientation = CaselessStrEnum(values=['horizontal', 'vertical'],
        default_value='horizontal', help="Vertical or horizontal.").tag(sync=True)
    _range = Bool(True, help="Display a range selector").tag(sync=True)
    readout = Bool(True, help="Display the current value of the slider next to it.").tag(sync=True)
    slider_color = Color(None, allow_none=True).tag(sync=True)
    continuous_update = Bool(True, help="Update the value of the widget as the user is sliding the slider.").tag(sync=True)
