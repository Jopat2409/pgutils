import numpy as np

from pgutils.exceptions import InitialisationError, RegistrationError

class Controller:

    initialised = False
    components: list[np.ndarray] = []
    config = {
        "max-ents": 1000,
        "culling": "last-accessed",
    }
    next_entities: list[int] = [0]

    def init(max_entities: int = 1e3,
                register_defaults: bool = True):
        """Initialise the entity component system controller

        Sets the max entity limit, creates the component array for tracking component types and
        registers the default components if `register_defaults` is not changed to false

        To check if the controller has already been initialised, see the `is_init` function

        Parameters
        ----------
        max_entities: int, optional
            Max number of entites before they are culled. Defaults to 1000.
        register_defaults: bool, optional
            Whether to register the in-built components. Defaults to True.

        Examples
        --------
        >>> Controller.init()
        >>> Controller.init(max_entities=10'000)
        >>> Controller.init(register_defaults=False)
        """

        Controller.reset()

        Controller.config["max-ents"] = int(max_entities)
        Controller.components.append(
            np.ndarray([max_entities], dtype=int)
        )

        if register_defaults:
            from pgutils.ecs.components import Transform, Render
            Controller.register_components(Transform, Render)

        Controller.initialised = True

    def reset():
        """Reset the entity component system controller back to its default values, before a call to `Controller.init`

        Removes all components and registered components, resets `Controller.config` and sets `is_init` to False.
        """
        Controller.initialised = False
        Controller.components = []
        Controller.config = {"max-ents": 1000, "culling": "last-accessed"}

    def register_component(component: object) -> None:
        """Registers a new component type to the entity component system controller.

        This function creates a component array and assigns a unique `ECS_COMPONENT_INDEX` and `ECS_COMPONENT_MASK` which
        are used to fetch components later on. Each component that you wish to use must first be registered using this function.

        Parameters
        ----------
        component : object
            The component **class** to add. Note this must be the class and not an object of said class.

        Raises
        ------
        RegistrationError
            If the component given has already been registered.
        InitialisationError
            If the controller has not been initialised (see `Controller.init`)
        ValueError
            If the maximum number of unique components has been reached
        """

        # Ensure this component has not been registered
        if hasattr(component, "ECS_COMPONENT_INDEX"):
            raise RegistrationError("This component has already been registered.")

        # Ensure the controller has been initialised
        if not Controller.initialised:
            raise InitialisationError("You must initialise the ECS controller before adding any components or systems. See ecs.Controller.initialise for more info.")

        # Ensure the max components has not been reached
        next_index = len(Controller.components)
        if next_index >= 64:
            raise ValueError("Maximum unique components reached (>64). This will be changed in a later version")

        # Create the component index, mask and array
        component.ECS_COMPONENT_INDEX = next_index
        component.ECS_COMPONENT_MASK = 1<<next_index
        Controller.components.append(np.ndarray([Controller.config["max-ents"]], dtype=component))

    def register_components(*components) -> None:
        map(Controller.register_component, components)

    def get_component_mask(*components) -> int:
        """Generates a bitmask that will be present in all entities with the given components.

        Entity components are tracked using a 64-bit integer, where the presence of each bit represents the presence
        of the corresponding component in the entity. Hence masks can be used to efficiently get entites which have
        a combination of multiple components.

        Returns
        -------
        int
            The bitmask created
        """
        mask = 0
        for c in components:
            mask |= c.ECS_COMPONENT_MASK
        return mask

    def get_next_entity_index() -> int:
        """Gets the next entity index that is free to use.

        If there are no more entity indexes left then `next_ent + 1` is appended as the next entity index to be used

        Returns
        -------
        int
            The index of the last freed entity
        """
        next_ent = Controller.next_entities.pop(-1)
        if not Controller.next_entities:
            Controller.next_entities.append(next_ent + 1)
        return next_ent

    def free_entity_index(index: int) -> None:
        Controller.next_entities.append(index)
