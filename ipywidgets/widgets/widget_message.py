"""
MessageInterceptorWidget

Represents a widget that can be used to intercept display messages.
"""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from .domwidget import DOMWidget
import sys
from io import StringIO
from traitlets import (
    Unicode, List, Instance, default, observe, Any
)
from IPython.display import clear_output
from IPython import get_ipython
from ipykernel.displayhook import ZMQMessageHook
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
    >>> hooked = widgets.MessageWidget('display_data')
    >>> display(hooked)
    >>> print('prints to output area')
    >>> with hooked:
            display('prints to message widget')
    """
    _view_name = Unicode('MessageWidgetView').tag(sync=True)
    _model_name = Unicode('MessageWidgetModel').tag(sync=True)
    _model_module = Unicode('jupyter-js-widgets').tag(sync=True)
    _view_module = Unicode('jupyter-js-widgets').tag(sync=True)

    # Currently defaulting to `display_data`. To intercept other
    # messages, change this attribute name.
    _message_type = Unicode('display_data')

    _message_hook = Instance(ZMQMessageHook)

    # Hookable messages are only implemented on the ZMQDisplayPublisher
    #
    _pub = Instance(ZMQDisplayPublisher)

    # The list of messages stored by the hook when activated
    # (in context).
    #
    stored_messages = List().tag(sync=True)

    #
    # String buffer to catch stdout / stderr
    #
    _std_buffer = Any()

    @default('_message_hook')
    def _message_hook_default(self):
        return ZMQMessageHook(self._message_type, self.store)

    @default('_pub')
    def _pub_default(self):
        return get_ipython().display_pub

    @default('_std_buffer')
    def _std_buffer_default(self):
        return StringIO()

    def clear_output(self, *args, **kwargs):
        with self:
            self.clear()

    def __enter__(self):
        """
        Called when entering MessageWidget context manager
        """
        self._pub.register_hook(self._message_hook)
        self._old_clear = self._pub.clear_output
        self._pub.clear_output = self.clear_output

        self._old_stdout = sys.stdout
        self._old_stderr = sys.stderr
        sys.stdout = self._std_buffer
        sys.stderr = self._std_buffer
        return self

    def __exit__(self, tp, value, tb):
        """
        Called when exiting MessageWidget context manager.
        """
        if tp is not None:
            # TODO : Exception occurred... log and continue.
            pass

        self._pub.unregister_hook(self._message_hook)
        self._pub.clear_output = self._old_clear
        sys.stdout = self._old_stdout
        sys.stderr = self._old_stderr

        # TODO : remove this when rendermime working in frontend.
        std = self._std_buffer.getvalue()
        if std:
            temp = {'content': {'data': {'text/plain': self._std_buffer.getvalue()}}}
            self.store(temp)
            self._std_buffer.truncate(0)

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
