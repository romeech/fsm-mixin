import pytest

from mixins.fsm import FinalStateMachineMixin

MSG_START = 'start'
MSG_COMPLETE = 'complete'
MSG_BREAK = 'break'
MSG_RESTART = 'repair'
MSG_UNREGISTERED = 'unknown'


class SampleTask(FinalStateMachineMixin):
    STATE_NEW = 'new'
    STATE_RUNNING = 'running'
    STATE_READY = 'ready'
    STATE_FAILED = 'failed'

    def __init__(self):
        self.status = self.initial_state

    @property
    def state_field_name(self):
        return 'status'

    @property
    def registered_messages(self):
        return [MSG_START, MSG_COMPLETE, MSG_BREAK, MSG_RESTART]

    @property
    def state_transitions(self):
        return {
            self.STATE_NEW: {
                MSG_START: self._make_transition(self.STATE_RUNNING),
                MSG_COMPLETE: self._make_transition(self.STATE_READY),
            },
            self.STATE_RUNNING: {
                MSG_COMPLETE: self._make_transition(self.STATE_READY),
                MSG_BREAK: self._make_transition(self.STATE_FAILED),
            },
            self.STATE_READY: {
                # all messages are ignored
            },
            self.STATE_FAILED: {
                MSG_RESTART: self._make_transition(self.STATE_RUNNING),
            },
        }

    @property
    def initial_state(self):
        return self.STATE_NEW


@pytest.fixture
def sample_task():
    return SampleTask()


def test_fsm_uses_state(sample_task):
    sample_task.status = SampleTask.STATE_READY
    assert getattr(sample_task, sample_task.state_field_name) == sample_task.status


def test_full_succes_path(sample_task):
    assert sample_task.status == SampleTask.STATE_NEW

    sample_task.accept_message(MSG_START)
    assert sample_task.status == SampleTask.STATE_RUNNING

    sample_task.accept_message(MSG_BREAK)
    assert sample_task.status == SampleTask.STATE_FAILED

    sample_task.accept_message(MSG_RESTART)
    assert sample_task.status == SampleTask.STATE_RUNNING

    sample_task.accept_message(MSG_COMPLETE)
    assert sample_task.status == SampleTask.STATE_READY


def test_unregistered_msg_causes_failure(sample_task):
    expected_msg = "FSM: Unexpected message ({}) is received.".format(MSG_UNREGISTERED)
    with pytest.raises(Exception, message=expected_msg):
        sample_task.accept_message(MSG_UNREGISTERED)


def test_short_success_path(sample_task):
    assert sample_task.status == SampleTask.STATE_NEW

    sample_task.accept_message(MSG_BREAK)
    assert sample_task.status == SampleTask.STATE_NEW

    sample_task.accept_message(MSG_COMPLETE)
    assert sample_task.status == SampleTask.STATE_READY

    for msg in [MSG_RESTART, MSG_START, MSG_BREAK]:
        sample_task.accept_message(msg)
        assert sample_task.status == SampleTask.STATE_READY


class UnrestrictedFsm(SampleTask):
    @property
    def registered_messages(self):
        return []


@pytest.fixture
def unrestricted_fsm():
    return UnrestrictedFsm()


def test_unregistred_msg_ignored(unrestricted_fsm):
    assert unrestricted_fsm.status == SampleTask.STATE_NEW
    unrestricted_fsm.accept_message(MSG_UNREGISTERED)
    assert unrestricted_fsm.status == SampleTask.STATE_NEW


def test_unregistred_but_effective_msg(unrestricted_fsm):
    assert unrestricted_fsm.status == SampleTask.STATE_NEW
    unrestricted_fsm.accept_message(MSG_COMPLETE)
    assert unrestricted_fsm.status == SampleTask.STATE_READY


class NotImplementedFsm(FinalStateMachineMixin):
    pass


@pytest.fixture
def incomplete_fsm():
    return NotImplementedFsm()


def test_state_field_name(incomplete_fsm):
    with pytest.raises(NotImplementedError):
        incomplete_fsm.state_field_name


def test_registered_messages(incomplete_fsm):
    with pytest.raises(NotImplementedError):
        incomplete_fsm.registered_messages


def test_state_transitions(incomplete_fsm):
    with pytest.raises(NotImplementedError):
        incomplete_fsm.state_transitions
