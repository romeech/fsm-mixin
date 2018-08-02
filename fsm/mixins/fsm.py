class FinalStateMachineMixin(object):
    @property
    def state_field_name(self):
        raise NotImplementedError()

    @property
    def registered_messages(self):
        raise NotImplementedError()

    @property
    def state_transitions(self):
        raise NotImplementedError()

    @property
    def initial_state(self):
        return getattr(self, self.state_field_name)

    def accept_message(self, message, **kwargs):
        if not hasattr(self, '_transitions'):
            self._set_initial_state()

        if self.registered_messages and message not in self.registered_messages:
            raise Exception("FSM: Unexpected message ({}) is received.".format(message))

        if message in self._transitions:
            self._transitions[message](**kwargs)

    def _make_transition(self, state):
        return lambda: self.__go_to_state(state)

    def __go_to_state(self, state):
        setattr(self, self.state_field_name, state)
        self._transitions = self.state_transitions[state]

    def _set_initial_state(self):
        self.__go_to_state(self.initial_state)
