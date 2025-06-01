

###----------------------------------------------------------------------------


class SettingsGroup():
    """
    A simple utility class for applying, removing, fetching and testing a group
    of settings in a view when all settings must be applied together to take
    effect.
    """
    def __init__(self, *settings):
        """
        Construct a settings group from a list of settings.

        The order of the settings here is the order that the settings will be
        applied and returned later.
        """
        self.key_list = list(settings)

    def apply(self, view, *values):
        """
        Apply the list of settings values given to the provided view, in the
        order the setting names were given to the constructor.
        """
        if len(values) != len(self.key_list):
            raise IndexError("Expected %d settings" % len(self.key_list))

        for setting in zip(self.key_list, values):
            view.settings().set(*setting)

    def remove(self, view):
        """
        Remove all settings in this group from the provided view.
        """
        for setting in self.key_list:
            view.settings().erase(setting)

    def has(self, view):
        """
        Check if the settings in this group are all set on the provided view.
        """
        for key in self.key_list:
            if not view.settings().has(key):
                return False
        return True

    def get(self, view):
        """
        Get the list of settings values from the provided view, in the order
        the setting names were given to the constructor.
        """
        return tuple(view.settings().get(key) for key in self.key_list)


###----------------------------------------------------------------------------
