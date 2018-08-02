# fsm-mixin
A mixin-class to turn an object into a final state machine

## setup
```
pip install -r requirements.txt
```

## usage
1. Inherit a target class from FinalStateMachineMixin
2. Implement the property **state_field_name**, make it return a string with name of field which stores current state
3. Implement the property **registered_messages** - return a collection of acceptable messages. Or just return an empty collection to accept everything.
4. Implement the property **state_transitions** - return a dictionary with states as keys and functions returning a new state. You can use **_make_transition** method to create a simple transition to a specified state.
5. Optionally override the property **initial_state** (if there's no initial value in the field defined by **state_field_name**).

## run tests
```
pytest fsm/tests
```