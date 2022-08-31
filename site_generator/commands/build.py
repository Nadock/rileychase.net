from site_generator import config, markdown


class BuildCommand:
    def __init__(self, cfg: config.SiteGeneratorConfig) -> None:
        self.cfg = cfg

    def run(self):
        print("build")

        for md_path in markdown.find_markdown(self.cfg.pages):
            markdown.load_markdown(md_path)
