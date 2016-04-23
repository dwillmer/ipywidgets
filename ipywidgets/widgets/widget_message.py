"""
MessageInterceptorWidget

Represents a widget that can be used to intercept display messages.
"""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from .domwidget import DOMWidget
from traitlets import (
    Unicode, List, Instance, default, observe
)
from IPython.display import clear_output
from IPython import get_ipython
from ipykernel.displayhook import ZMQMessageHook
from ipykernel.hookmanager import MessageHookFor
from ipykernel.zmqshell import ZMQDisplayPublisher
from jupyter_client.session import Message

from .widget import register


@register('Jupyter.MessageWidget')
class MessageWidget(DOMWidget):
    """ Widget used as a context manager to display hooked messages.

    This widget can capture and display any 'display_data' messages.

    Example
    -------
    >>> import ipywidgets as widgets
    >>> from IPython.display import display
    >>> my_widget = widgets.MessageWidget('display_data')
    >>> display(my_widget)
    >>> print('prints to output area')
    >>> with my_widget.capture():
            display('prints to message widget')
    """
    _view_name = Unicode('MessageWidgetView').tag(sync=True)
    _model_name = Unicode('MessageWidgetModel').tag(sync=True)
    _model_module = Unicode('jupyter-js-widgets').tag(sync=True)
    _view_module = Unicode('jupyter-js-widgets').tag(sync=True)

    # Currently defaulting to `display_data`. To intercept other
    # messages, change this attribute name.
    _message_type = Unicode('display_data')

    # The list of messages stored by the hook when activated
    # (in context).
    #
    stored_messages = List().tag(sync=True)

    # The context manager for capturing the messages.
    #
    capture = Instance(MessageHookFor)

    @default('_std_buffer')
    def _std_buffer_default(self):
        return StringIO()

    def clear_output(self, *args, **kwargs):
        self.clear()

    def capture(self, message_type=None):
        msg_type = message_type or self._message_type
        return MessageHookFor(msg_type, parent=self)

    def clear(self):
        """
        Clear the stored messages list.
        """
        self.stored_messages = []
        self.value = []

    def store(self, item):
        """
        Store an item in the stored messages list.
        """
        # TODO : get traitlets to fire on list append?
        temp = self.stored_messages[:]
        temp.append(item)
        self.stored_messages = temp
        self.value = temp
