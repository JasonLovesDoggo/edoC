# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  Copyright (c) 2021. Jason Cameron                                                               +
#  All rights reserved.                                                                            +
#  This file is part of the edoC discord bot project ,                                             +
#  and is released under the "MIT License Agreement". Please see the LICENSE                       +
#  file that should have been included as part of this package.                                    +
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class MojangObject:
    def to_dict(self) -> dict:
        """Returns a dictionary of all instance attributes"""
        return self.__dict__.copy()

    def __repr__(self):
        return "%s(%s)" % (
            self.__class__.__name__,
            self.__dict__
        )


class UserProfile(MojangObject):
    def __init__(self, data: dict):
        self.timestamp = data["timestamp"]
        self.id = data["profileId"]
        self.name = data["profileName"]

        self.is_legacy_profile = data.get("legacy")
        if self.is_legacy_profile is None:
            self.is_legacy_profile = False

        self.cape_url = None
        self.skin_url = None
        self.skin_model = "classic"

        if data["textures"].get("CAPE"):
            self.cape_url = data["textures"]["CAPE"]["url"]

        if data["textures"].get("SKIN"):
            self.skin_url = data["textures"]["SKIN"]["url"]
            if data["textures"]["SKIN"].get("metadata"):
                self.skin_model = "slim"