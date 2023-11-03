import json
from psychopy.hardware import base


class ButtonResponse:
    def __init__(self, t, channel, value):
        self.t = t
        self.channel = channel
        self.value = value

    def __repr__(self):
        return f"<ButtonResponse: t={self.t}, channel={self.channel}, value={self.value}>"

    def getJSON(self):
        message = {
            'type': "hardware_response",
            'class': "PhotodiodeResponse",
            'data': {
                't': self.t,
                'channel': self.channel,
                'value': self.value,
            }
        }

        return json.dumps(message)


class BaseButtonGroup(base.BaseDevice):
    def __init__(self, parent, channels=1):
        # store reference to parent device (usually a button box)
        self.parent = parent
        # store number of channels
        self.channels = channels
        # attribute in which to store current state
        self.state = [None] * channels
        # list in which to store messages in chronological order
        self.responses = []
        # list of listener objects
        self.listeners = []

    def clearResponses(self):
        self.parent.dispatchMessages()
        self.responses = []

    def addListener(self, listener):
        """
        Add a listener, which will receive all the same messages as this Button.

        Parameters
        ----------
        listener : hardware.listener.BaseListener
            Object to duplicate messages to when received by this Button.
        """
        self.listeners.append(listener)

    def getResponses(self, state=None, channel=None, clear=True):
        """
        Get responses which match a given on/off state.

        Parameters
        ----------
        state : bool or None
            True to get button "on" responses, False to get button "off" responses, None to get all responses.
        channel : int
            Which button to get responses from?
        clear : bool
            Whether or not to remove responses matching `state` after retrieval.

        Returns
        -------
        list[ButtonResponse]
            List of matching responses.
        """
        # make sure device dispatches messages
        self.parent.dispatchMessages()
        # array to store matching responses
        matches = []
        # check messages in chronological order
        for resp in self.responses.copy():
            # does this message meet the criterion?
            if state is None or resp.value == state:
                if channel is None or resp.channel == channel:
                    # if clear, remove the response
                    if clear:
                        i = self.responses.index(resp)
                        resp = self.responses.pop(i)
                    # append the response to responses array
                    matches.append(resp)

        return matches

    def receiveMessage(self, message):
        assert isinstance(message, ButtonResponse), (
            "{ownType}.receiveMessage() can only receive messages of type PhotodiodeResponse, instead received "
            "{msgType}. Try parsing the message first using {ownType}.parseMessage()"
        ).format(ownType=type(self).__name__, msgType=type(message).__name__)
        # update current state
        self.state[message.channel] = message.value
        # add message to responses
        self.responses.append(message)
        # relay message to listener
        for listener in self.listeners:
            listener.receiveMessage(message)

    def getState(self, channel):
        # dispatch messages from device
        self.parent.dispatchMessages()
        # return state after update
        return self.state[channel]

    def parseMessage(self, message):
        raise NotImplementedError()
