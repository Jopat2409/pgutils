import pytest

from pgutils.ecs import components

@pytest.fixture
def controller():
    from pgutils.ecs.controller import Controller
    Controller.init(1000, False)
    yield Controller
    Controller.reset()

def test_register_component_uninitialised():
    from pgutils.ecs.controller import Controller

    # Can't register components on uninitialised controller
    with pytest.raises(RuntimeError):
        Controller.register_component(components.Transform)


def test_register_component(controller):

    assert controller.initialised

    # Basic addition
    controller.register_component(components.Transform)
    assert components.Transform.ECS_COMPONENT_INDEX == 1

    # component index incremements properly
    controller.register_component(components.Render)
    assert components.Render.ECS_COMPONENT_INDEX == 2

    # component index remains after being re-imported
    from pgutils.ecs.components import Transform, Render
    assert Transform.ECS_COMPONENT_INDEX == 1
    assert Render.ECS_COMPONENT_INDEX == 2

    # Can't add the same component
    with pytest.raises(RuntimeError):
        controller.register_component(components.Transform)

    # Can't add more than 63 custom components
    for i in range(61):
        class Test:
            pass
        controller.register_component(Test)

    with pytest.raises(RuntimeError):
        class Test:
            pass
        controller.register_component(Test)

def test_add_component(controller):
    pass
