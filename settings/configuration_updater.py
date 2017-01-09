from collections import OrderedDict
class BaseConfigurationUpdater(object):
    FROM_VERSION = None
    TO_VERSION = None
    UPDATERS = OrderedDict()
    NEXT_UPDATER = None

    def __init__(self):
         pass

    @classmethod
    def register(self, cls):
        to_version = cls.TO_VERSION
        previous_updater = None
        if len(self.UPDATERS) > 0:
            updaters = BaseConfigurationUpdater.UPDATERS.values()
            previous_updater = updaters[len(updaters) - 1]
            previous_updater.NEXT_UPDATER = cls

        #Add our new updater to the collection
        BaseConfigurationUpdater.UPDATERS[cls.FROM_VERSION] = cls

class ConfigUpdater13(BaseConfigurationUpdater):
    FROM_VERSION = 1.2
    TO_VERSION = 1.3

    def run(self):
        #Do updating until successful
        if not self.NEXT_UPDATER is None:
            next_updater = self.NEXT_UPDATER()
            next_updater.run()

ConfigUpdater13.register(ConfigUpdater13)

class ConfigUpdater14(BaseConfigurationUpdater):
    FROM_VERSION = 1.3
    TO_VERSION = 1.4

    def run(self):
        #Something
        pass

ConfigUpdater14.register(ConfigUpdater14)

#If current config version is 1.2
# v = 1.2
# updaters = BaseConfigurationUpdater.UPDATERS
# if v in self.UPDATERS:
#     updater_cls = updaters[v]
#     updater = updater_cls()
#     updater.run()
# #
        
