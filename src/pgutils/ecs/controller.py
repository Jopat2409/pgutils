import numpy as np

class ECSException(Exception):
    pass

class Controller:

    initialised = False
    components: list[np.ndarray] = []
    config = {
        "max-ents": 1000,
        "culling": "last-accessed",
    }

    def init(max_entities: int = 1e3,
                register_defaults: bool = True):
        """_summary_

        Args:
            max_entities (int, optional): _description_. Defaults to 1e3.
            register_defaults (bool, optional): _description_. Defaults to True.
        """

        Controller.config["max-ents"] = int(max_entities)
        Controller.components.append(
            np.ndarray([max_entities], dtype=int)
        )

        if register_defaults:
            from pgutils.ecs.components import Transform, Render
            Controller.register_components(Transform, Render)

        Controller.initialised = True

    def reset():
        print("Resetting Controller")
        Controller.initialised = False
        Controller.components = []
        Controller.config = {"max-ents": 1000, "culling": "last-accessed"}

    def get_max_entities() -> int:
        return Controller.__max_entities

    def register_component(component: object) -> None:

        if hasattr(component, "ECS_COMPONENT_INDEX"):
            raise ECSException("This component has already been registered.")

        if not Controller.initialised:
            raise ECSException("You must initialise the ECS controller before adding any components or systems. See ecs.Controller.initialise for more info.")

        next_index = len(Controller.components)

        if next_index >= 64:
            raise ECSException("Maximum unique components reached (>64). This will be changed in a later version")

        component.ECS_COMPONENT_INDEX = next_index
        Controller.components.append(np.ndarray([Controller.config["max-ents"]], dtype=component))

    def register_components(*components) -> None:
        map(Controller.register_component, components)


