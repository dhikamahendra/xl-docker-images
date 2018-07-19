from . import ALL_TARGET_SYSTEMS
import json
import docker
from os import path
import re
import sys
from . import image_version, all_tags


class XLDockerImageBuilder(object):
    def __init__(self, commandline_args):
        self.target_systems = commandline_args.target_os or ALL_TARGET_SYSTEMS
        self.registry = commandline_args.registry,
        self.repository = commandline_args.repository
        self.image_version = image_version(commandline_args.version, commandline_args.suffix)
        self.use_cache = commandline_args.use_cache

    @staticmethod
    def convert_logs(generator):
        for line in generator:
            multilines = [l for l in line.split(b'\n') if l.strip()]
            for l in multilines:
                j = json.loads(l)
                if "stream" in j:
                    yield j['stream']
                elif "error" in j:
                    raise Exception(j["error"])

    def build_docker_image(self, target_os):
        client = docker.from_env()
        generator = client.api.build(
            nocache=not self.use_cache,
            pull=not self.use_cache,
            path=".",
            dockerfile=path.join(target_os, 'Dockerfile'),
            rm=True,
        )
        for line in self.convert_logs(generator):
            match = re.search(
                r'(^Successfully built |sha256:)([0-9a-f]+)$',
                line
            )
            if match:
                image_id = match.group(2)
            sys.stdout.write(line)

        print("Built image %s for %s" % (image_id, target_os))
        image = client.images.get(image_id)
        for tag, force in all_tags(target_os, self.image_version):
            image.tag("%s/%s" % (self.registry, self.repository), tag)
        image.reload()
        print("Image %s has been tagged with %s" % (image_id, ', '.join(image.tags)))
