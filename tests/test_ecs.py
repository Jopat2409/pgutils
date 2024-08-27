import pytest

from pgutils.ecs import components
from pgutils.exceptions import InitialisationError, RegistrationError

@pytest.fixture
def controller():
    from pgutils.ecs.controller import Controller
    Controller.init(1000, False)
    yield Controller
    Controller.reset()

def test_register_component_uninitialised():
    from pgutils.ecs.controller import Controller

    # Can't register components on uninitialised controller
    with pytest.raises(InitialisationError):
        Controller.register_component(components.Transform)

def test_register_component(controller):

    assert controller.initialised

    # Basic addition
    controller.register_component(components.Transform)
    assert components.Transform.ECS_COMPONENT_INDEX == 1
    assert components.Transform.ECS_COMPONENT_MASK == 2

    # component index incremements properly
    controller.register_component(components.Render)
    assert components.Render.ECS_COMPONENT_INDEX == 2
    assert components.Render.ECS_COMPONENT_MASK == 4

    # component index remains after being re-imported
    from pgutils.ecs.components import Transform, Render
    assert Transform.ECS_COMPONENT_INDEX == 1
    assert Transform.ECS_COMPONENT_MASK == 2
    assert Render.ECS_COMPONENT_INDEX == 2
    assert Render.ECS_COMPONENT_MASK == 4

    # Can't add the same component
    with pytest.raises(RegistrationError):
        controller.register_component(components.Transform)

    # Can't add more than 63 custom components
    for i in range(61):
        class Test:
            pass
        controller.register_component(Test)

    with pytest.raises(ValueError):
        class Test:
            pass
        controller.register_component(Test)

def test_register_components(controller):
    controller.register_components(components.Transform, components.Render)
    assert components.Transform.ECS_COMPONENT_INDEX == 1
    assert components.Transform.ECS_COMPONENT_MASK == 2
    assert components.Render.ECS_COMPONENT_INDEX == 2
    assert components.Render.ECS_COMPONENT_MASK == 4

def test_get_component_mask(controller):
    controller.register_components(components.Transform, components.Render)

    assert controller.get_component_mask(components.Transform, components.Render) == 6
    assert controller.get_component_mask(components.Transform, components.Render) & 2
    assert controller.get_component_mask(components.Transform, components.Render) & 4

def test_get_next_entity(controller):
    for i in range(0, 1000):
        assert controller.get_next_entity_index() == i
