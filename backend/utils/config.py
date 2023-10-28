from configparser import BasicInterpolation, ConfigParser
import os
import sys


class EnvInterpolation(BasicInterpolation):
    """Interpolation which expands environment variables in values."""

    def before_get(self, parser, section, option, value, defaults):
        value = super().before_get(parser, section, option, value, defaults)
        return os.path.expandvars(value)


class Config(object):
    def __init__(self, logger, filename="hallway-display.conf"):
        try:
            config = ConfigParser(interpolation=EnvInterpolation())
            config.read(filename)
            self.config = config
        except Exception as e:
            logger.error("🔥 Could not read configuration file %s: %s", filename, e)
            sys.exit(1)

    def get(self, option):
        return self.config.get("DEFAULT", option)

    def get_sites(self):
        return [section for section in self.config.sections() if section != "DEFAULT"]

    def get_section(self, section_name):
        return self.config[section_name]
