from site_generator import config


class BuildCommand:
    def __init__(self, cfg: config.SiteGeneratorConfig) -> None:
        self.cfg = cfg

    def run(self):
        print("build")
